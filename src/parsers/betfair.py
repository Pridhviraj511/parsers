import os
from collections import defaultdict
from copy import deepcopy
from datetime import datetime
from re import sub
from typing import Generator, Union, Tuple

from pytz import utc

from models.event import Event
from models.market import Market
from models.update import SPORTS
from models.variation import Variations, Variation
from parsers import ApiParser
from utils.betfair import Filter, MarketProjection, MaxResult, PriceProjection, MarketId, BetfairApi
from utils.calculations import str_to_date

URL = os.getenv('URL', 'https://api.betfair.com/exchange/betting/json-rpc/v1/')
SLEEP = os.getenv('SLEEP', 60)
INVERTED_DIRECTION = int(os.getenv('INVERTED_DIRECTION', 0))
PERCENTAGE_LIMIT = float(os.getenv('PERCENTAGE_LIMIT', 0))

USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
APP_KEY = os.getenv('APP_KEY')


class BetfairParser(ApiParser):
    PARTITION = 11

    def __init__(self):
        self._events_list: dict = dict()
        self._market_to_event: dict = dict()
        self._tournaments: dict = dict()
        self.market_translations = dict(
            BothteamstoScore='BTTS',
            OverUnder25Goals='O/U',
            MatchOdds='H/H',
            Moneyline='H/H'
        )
        sport_ids = {1: 1, 7522: 2, 2: 5}

        self.betfair = BetfairApi(username=USERNAME, password=PASSWORD, app_key=APP_KEY)

        super(BetfairParser, self).__init__(2, 'betfair', INVERTED_DIRECTION, PERCENTAGE_LIMIT, sport_ids, URL, SLEEP)

    def get_competition_ids(self, sport_id) -> dict:
        cur_market_count, tot_market_count, tot = 0, 0, 0
        competition_ids = defaultdict(list)

        for c in self.betfair.competitions(Filter(eventTypeIds=[sport_id],
                                                  marketTypeCodes=['MATCH_ODDS', 'OVER_UNDER_25',
                                                                   'BOTH_TEAMS_TO_SCORE'])):  # 'MONEYLINE'
            self._tournaments.update({int(c['competition']['id']): dict(tournament_name=c['competition']['name'],
                                                                        category_name=c['competitionRegion'])})
            market_count = int(c['marketCount'])
            tot += market_count
            if cur_market_count + market_count < 100:
                cur_market_count += market_count
            else:
                tot_market_count += cur_market_count
                cur_market_count = market_count
            competition_ids[tot_market_count].append(int(c['competition']['id']))

        return competition_ids

    def _make_event_list(self, sport_id: int) -> None:

        for v in self.get_competition_ids(sport_id=sport_id).values():
            for i in self.betfair.market_catalogue(
                    Filter(competitionIds=v,
                           marketTypeCodes=['MATCH_ODDS', 'OVER_UNDER_25', 'BOTH_TEAMS_TO_SCORE']),
                    MarketProjection('EVENT', 'EVENT_TYPE', 'RUNNER_DESCRIPTION', 'COMPETITION'),
                    MaxResult(1000)):
                try:
                    event_id = i['event']['id']
                    market_id = i['marketId']
                    market_name = sub('\\W', '', i['marketName'])
                    tournament_id = i['competition']['id']

                    if event_id not in self._events_list.keys():
                        utc_start_date = utc.localize(datetime.strptime(i['event']['openDate'],
                                                                        '%Y-%m-%dT%H:%M:%S.%fZ'))

                        e = dict(
                            event_id=int(event_id),
                            event_name=i['event']['name'].replace(' v ', ' - ').replace(' @ ', ' - '),
                            start_date=datetime.strftime(utc_start_date, '%Y-%m-%dT%H:%M:%S'),
                            sport_id=sport_id,  # i['eventType']['id'],
                            tournament_id=tournament_id,
                            home_id=None,
                            home_name=None,
                            away_id=None,
                            away_name=None,
                            markets={market_id: {'name': market_name}}
                        )
                        e.update(self._tournaments.get(tournament_id, dict(tournament_name='', category_name='')))

                        if i['marketName'] in ('Match Odds', 'Moneyline'):
                            e['home_id'] = i['runners'][0]['selectionId'] if i['runners'][0]['sortPriority'] == 1 \
                                else i['runners'][1]['selectionId']
                            e['home_name'] = i['runners'][0]['runnerName'] if i['runners'][0]['sortPriority'] == 1 \
                                else i['runners'][1]['runnerName']
                            e['away_id'] = i['runners'][1]['selectionId'] if i['runners'][1]['sortPriority'] == 2 \
                                else i['runners'][0]['selectionId']
                            e['away_name'] = i['runners'][1]['runnerName'] if i['runners'][1]['sortPriority'] == 2 \
                                else i['runners'][0]['runnerName']

                        self._events_list[event_id] = e

                    else:
                        if i['marketName'] in ('Match Odds', 'Moneyline'):
                            self._events_list[event_id]['home_id'] = i['runners'][0]['selectionId'] \
                                if i['runners'][0]['sortPriority'] == 1 else i['runners'][1]['selectionId']
                            self._events_list[event_id]['home_name'] = i['runners'][0]['runnerName'] \
                                if i['runners'][0]['sortPriority'] == 1 else i['runners'][1]['runnerName']
                            self._events_list[event_id]['away_id'] = i['runners'][1]['selectionId'] \
                                if i['runners'][1]['sortPriority'] == 2 else i['runners'][0]['selectionId']
                            self._events_list[event_id]['away_name'] = i['runners'][1]['runnerName'] \
                                if i['runners'][1]['sortPriority'] == 2 else i['runners'][0]['runnerName']

                        self._events_list[event_id]['markets'][market_id] = {'name': market_name}

                    self._market_to_event[market_id] = event_id

                except Exception as e:
                    print(f'betfair container error (_make_event_list), error: {e}, '
                          f'tournament id {v}, market id {i}')

    def _make_odds(self) -> None:
        prev = 0
        market_ids = list(self._market_to_event.keys())

        for j in range(self.PARTITION, len(market_ids) + self.PARTITION, self.PARTITION):
            for i in self.betfair.market_book(
                    MarketId(*[i for i in market_ids[prev:j]]),
                    PriceProjection(priceData=['EX_BEST_OFFERS', 'EX_ALL_OFFERS'])):

                best_back_odds, best_lay_odds = {}, {}
                back_margin, lay_margin = 0, 0
                closed = False
                market_id = i['marketId']
                market_status = i['status'] or ""

                for runner in i['runners']:
                    status = runner['status']  # ACTIVE/REMOVED/WINNER/LOSER
                    selection_id = runner['selectionId']
                    if market_status != 'OPEN' or status != 'ACTIVE':
                        closed = True

                    best_back_odd = runner['ex']['availableToBack'][0] \
                        if len(runner['ex']['availableToBack']) > 0 else {'price': 1.01, 'size': 0}
                    best_lay_odd = runner['ex']['availableToLay'][0] \
                        if len(runner['ex']['availableToLay']) > 0 else {'price': 1000, 'size': 0}
                    back_odd = 0 if closed else best_back_odd['price']
                    lay_odd = 0 if closed else best_lay_odd['price']
                    best_back_odds[selection_id] = {'odd': back_odd if back_odd > 1 else 0, 'status': status}
                    best_lay_odds[selection_id] = {'odd': lay_odd if lay_odd > 1 else 0, 'status': status}
                    back_margin += 1 / back_odd if back_odd > 1 else 0
                    lay_margin += 1 / lay_odd if lay_odd > 1 else 0

                event_id = self._market_to_event[market_id]
                self._events_list[event_id]['markets'][market_id]['status'] = market_status
                self._events_list[event_id]['markets'][market_id]['back_odds'] = best_back_odds
                self._events_list[event_id]['markets'][market_id]['lay_odds'] = best_lay_odds
                self._events_list[event_id]['markets'][market_id]['back_margin'] = back_margin
                self._events_list[event_id]['markets'][market_id]['lay_margin'] = lay_margin

            prev = j

    def get_all_events(self) -> Generator:

        print('Getting event list')
        for sport_id in (1, 2, 7522):
            self._make_event_list(sport_id=sport_id)

        print('Getting Odds')
        self._make_odds()

        for event in self._events_list.values():
            yield event

    def get_event(self, event: any, last_update: datetime) -> Union[None, Event]:
        """
        This function parses the required data and creates a unique format for storage in MongoDB.
        We also use Redis to get previous odds, so that we can keep only the new ones, and also keep the historical
        odds without duplicates. If necessary - we can set the percentage below we will not accept the changes,
        as there will be a lot of calculations for the weighted average system unnecessarily.

        :param event: This is the event we parse.
        :param last_update: Last arrival date of the event.
        """
        event_id = int(event['event_id'])
        sport_id = self.sports.get(int(event['sport_id']), 0)
        date = str_to_date(event['start_date'])

        home, away = None, None
        try:
            home, away = event['event_name'].split(' - ', 1)
        except Exception as e:
            print(f"event_name ({event['event_name']}) error {e}")

        return Event(
            _id=event_id,
            date=int(date.timestamp()),
            bookmaker_id=self.id,
            bookmaker_name=self.name,
            sport_id=sport_id,
            sport_name=SPORTS.get(sport_id),
            home_id=event['home_id'] or None,
            home_name=str(event['home_name']) if event['home_name'] else home,
            away_id=event['away_id'] or None,
            away_name=str(event['away_name']) if event['away_name'] else away,
            category_id=0,  # TODO
            category_name=str(event['category_name']),  # FRA, WTA... better to stay
            tournament_id=int(event['tournament_id']),
            tournament_name=str(event['tournament_name']),
            betradar_id=None,
            status=True,  # it is always true, because they send statuses only for markets and odds
            last_update=int(last_update.timestamp())
        )

    def get_market(self, event: Event, markets: dict, current_event: Event) -> Tuple[dict, int]:
        """
        This function parses the market received according to our standard format

        :param event: Event that we are parsing.
        :param markets: Market data that we received
        :param current_event: Event that we received
        """

        odd_names = {
            event.home_id: '1',
            event.away_id: '2',
            58805: 'X',
            47972: 'Under',
            47973: 'Over',
            30246: 'Yes',
            110503: 'No'
        }

        current_odds = {}
        if current_event is None or current_event.back is None or not len(current_event.back):
            current_odds['back'] = Market.get_market_by_sport(sport_id=event.sport_id)
        else:
            current_odds['back'] = current_event.back

        if current_event is None or current_event.lay is None or not len(current_event.lay):
            current_odds['lay'] = Market.get_market_by_sport(sport_id=event.sport_id)
        else:
            current_odds['lay'] = current_event.lay

        variations = Variations(event)

        for market in markets:
            try:
                if 'back_odds' in markets[market] or 'lay_odds' in markets[market]:
                    if 'Unmanaged' in markets[market]['name']:
                        continue
                    market_name = self.market_translations.get(markets[market]['name'], '')
                    market_name = '1X2' if event.sport_id == 1 and market_name == 'H/H' else market_name
                    sbv = '#'

                    for odd_type in ('back', 'lay'):  # Betfair has both back and lay odds

                        margin = (markets[market][odd_type + '_margin'] * 100).__round__(2)

                        for selection_id in markets[market][odd_type + '_odds'].keys():
                            odd = self.check_odd(markets[market][odd_type + '_odds'][selection_id]['odd'])
                            outcome_name = odd_names.get(int(selection_id))

                            if not market_name or not outcome_name or not sbv:
                                print(f'Error! Market ({market_name}), outcome ({outcome_name}) or sbv ({sbv}) '
                                      f'is missing: {market}\n{event}')
                                continue

                            if sbv not in current_odds[odd_type][market_name]:
                                current_odds[odd_type][market_name].update(Event.make_sbv(market=market_name, sbv=sbv))
                                prev_odd, prev_last_update = 0, 0
                            else:
                                prev = current_odds[odd_type].get(market_name, {}).get(sbv, {}) \
                                    .get(outcome_name, dict(odd=0, lastUpdate=''))
                                prev_odd, prev_last_update = prev.get('odd', 0), prev.get('lastUpdate', 0)

                            if odd == prev_odd and odd != 0:
                                current_odds[odd_type][market_name][sbv][outcome_name] \
                                    .update(odd=odd, lastUpdate=prev_last_update)

                            if odd != prev_odd:
                                key = f'{odd_type}.{market_name}.{sbv}.{outcome_name}'

                                if not self.percentage_checker(odd=odd, prev_odd=prev_odd, key=key):
                                    continue

                                # For storage in historical odds, only odds that are within the margins are
                                # important to us. At this point we call their API-es for it.
                                if odd and (
                                        (
                                                odd_type == 'back'
                                                and 100 <= margin < 105
                                        )
                                        or (
                                                odd_type == 'lay'
                                                and 95 < margin <= 100
                                        )
                                ):
                                    change = {key: dict(date=event.last_update, change=odd)}
                                    print(event.id, change)

                                current_odds[odd_type][market_name][sbv][outcome_name].update(
                                    dict(odd=odd, lastUpdate=event.last_update))

                                variations.append(Variation(
                                    _id=event.id,
                                    bookmaker_name=self.name,
                                    sport_id=event.sport_id,
                                    market_name=market_name,
                                    sbv=sbv,
                                    outcome_name=outcome_name,
                                    odd=odd,
                                    last_update=event.last_update,
                                    status=event.status
                                ))

            except Exception as e:
                print(f'error on get_market: {e}\n{event}\n{event.__dict__}\n{market}')

        if variations.exists():
            variations.calculate_main_lines(current_odds)
            # self.store_variations(variations=variations)
        return current_odds, variations.exists()

    def store(self, event: Event):

        if event.lay:
            event_lay = deepcopy(event)
            event_lay.bookmaker_name = "betfair-lay"

            event.lay, event_lay.back, event_lay.lay = {}, event.lay, {}

            super().store(event_lay)

        super().store(event)
