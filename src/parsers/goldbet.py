import os
from datetime import datetime
from json import loads
from typing import Union, Generator, List, Tuple

from models.event import Event
from models.market import Market
from models.variation import Variations, Variation
from parsers import ApiParser
from utils.position import get_position_goldbet

URL = os.getenv('URL', 'http://oes.goldbet.it/')
SLEEP = os.getenv('SLEEP', 60)
INVERTED_DIRECTION = int(os.getenv('INVERTED_DIRECTION', 0))
PERCENTAGE_LIMIT = float(os.getenv('PERCENTAGE_LIMIT', 0))


class GoldbetParser(ApiParser):

    def __init__(self):
        """ This is the Goldbet class that extends the Bookmaker class and gives us some additional info we need. """

        self.sport_ids = {1: 1, 2: 2, 3: 5}
        self.position = get_position_goldbet()
        self.markets: dict = {1: {"1x2": 1, "ou": 2, "gg_ng": 9},
                              2: {"12": 3, "ou": 5, "hcp": 6, "other_ou_lines": 5, "other_hcp_lines": 6},
                              5: {"12": 4, "games_ou": 7, "games_hcp": 8}}
        self.translation_table = {'one': '1', 'x': 'X', 'two': '2', 'over': 'Over', 'under': 'Under',
                                  'gg': 'Yes', 'ng': 'No'}
        super().__init__(12, 'goldbet', INVERTED_DIRECTION, PERCENTAGE_LIMIT,
                         sports={1: 'Soccer', 2: 'Basket', 5: 'Tennis'}, url=URL, sleep=SLEEP)

    def _get_json(self, sport: str) -> List[dict]:
        """
        Calling the API for each sport we use.
        If there is an some error in the API, after third attempt it sends a message informing us that
        something is wrong, otherwise, it returns an json object that we will parse later or an empty list.

        :param sport: The sport for which we are calling the API.
        """
        r = self.call_api(url=f"{self.url}{sport}OddsService.svc/GetOdds{'/Extended' if sport == 'Basket' else '/'}",
                          headers={}, data={}, func_name=f'{self.name}_get_json_{sport}', timeout=120, get_method=True,
                          to_print=True)

        return loads(r.content.decode('utf-8')) if r else []

    def _get_market_data(self, update):
        """
        Get market data from update

        :param update
        :return object
        """
        return update

    def get_all_events(self) -> Generator:
        """
        This function goes through events, calls functions to process them and later stores them in a database.
        Also, if we have at least one event, we put a heartbeat, which means that the feed is alive.

        :param last_update: Date and time (UTC) when this event received last time.
        :param control_date: Current timestamp, so we can search through logs.
        :return:
        """
        for sport_id, sport_name in self.sports.items():
            for event in self._get_json(sport_name):
                event.update({'sportid': sport_id, 'sportname': sport_name})
                yield event

    def get_event(self, event: any, last_update: datetime) -> Union[None, Event]:
        # (self, event: dict, sport_id: int, last_update: datetime, control_date: int):
        """
        This function parses the required data and creates a unique format for storage in MongoDB.
        We also use Redis to get previous odds, so that we can keep only the new ones, and also keep the historical
        odds without duplicates. If necessary - we can set the percentage below we will not accept the changes,
        as there will be a lot of calculations for the weighted average system unnecessarily.

        :param event: This is the event we parse.
        :param last_update: Date and time (UTC) when this event received last time.
        """
        if event['countryid'] == '29187':  # skips Calcio Fantasy
            return

        event_id = int(event['matchid'])
        event_status = event['status'] == 1
        date = datetime.utcfromtimestamp(int(event['starttime']))

        if date < datetime.utcnow():
            print(f'Skipping event {event_id} because it started {date}')
            return

        # Collecting the necessary data and converting them into expected types.
        return Event(
            _id=event_id,
            date=int(datetime.timestamp(date)),
            bookmaker_id=self.id,
            bookmaker_name=self.name,
            sport_id=int(event['sportid']),  # TODO
            sport_name=event['sportname'],
            home_id=int(event['e1id']),
            home_name=event['e1'],
            away_id=int(event['e2id']),
            away_name=event['e2'],
            category_id=int(event['countryid']),
            category_name=str(event['country']),
            tournament_id=int(event['lid']),
            tournament_name=str(event['liga']),
            betradar_id=int(event['betradar']) if event['betradar'] else None,
            status=event_status,
            live=False,
            last_update=int(datetime.timestamp(last_update)),
            aams=str(event['aams'])
        )

    def get_market(self, event: Event, markets: dict, current_event: Event) -> Tuple[dict, int]:
        """
        This function parses the market received according to our standard format

        :param event: Event that we are parsing.
        :param markets: Market data that we received
        :param current_event: Event that we received
        """
        if current_event is None or current_event.back is None or not len(current_event.back):
            current_odds = Market.get_market_by_sport(event.sport_id)
        else:
            current_odds = current_event.back

        odds = Market.get_market_by_sport(event.sport_id)
        variations = Variations(event)

        for m_name, m_id in self.markets.get(event.sport_id, {}).items():  # Iterating through our markets

            try:
                if m_name in markets:  # Checking if they have sent the market we need
                    lst = [markets[m_name]] if type(markets[m_name]) is dict else markets[m_name]
                    market_name = self.position.get(event.sport_id).get(m_id).get('market_name', '')

                    for item in lst:  # Iterating through outcomes
                        sbv = item['ps'] if 'ps' in item else '#'

                        for outcome, odd in item.items():
                            try:
                                if outcome == 'ps':  # Skipping the SBV
                                    continue

                                odd = self.check_odd(odd)
                                outcome_name = self.translation_table.get(outcome, '')
                                sbv = self.check_sbv(sbv=sbv, market_id=m_id)

                                if not market_name or not outcome_name or not sbv:
                                    print(
                                        f'Error! Market ({market_name}), outcome ({outcome_name}) or sbv ({sbv}) '
                                        f'is missing: {item}\n{event}')
                                    continue

                                if sbv not in odds[market_name]:
                                    odds[market_name].update(event.make_sbv(market=market_name, sbv=sbv))

                                if sbv not in current_odds[market_name]:
                                    current_odds[market_name].update(event.make_sbv(market=market_name, sbv=sbv))
                                    prev_odd, prev_last_update = 0, ''
                                else:
                                    prev = current_odds.get(market_name, {}).get(sbv, {}) \
                                        .get(outcome_name, dict(odd=0, lastUpdate=''))
                                    prev_odd, prev_last_update = prev.get('odd', 0), prev.get('lastUpdate', '')

                                if odd == prev_odd and odd != 0:
                                    odds[market_name][sbv][outcome_name] \
                                        .update(odd=odd, lastUpdate=prev_last_update)

                                if odd != prev_odd:
                                    key = f'back.{market_name}.{sbv}.{outcome_name}'

                                    if not self.percentage_checker(odd=odd, prev_odd=prev_odd, key=key):
                                        continue

                                    odds[market_name][sbv][outcome_name].update(
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
                                print(f'{self.name} error (process_event 4): {e}\n{event}\n{event.__dict__}')

            except Exception as e:
                print(f'get_market error: {e}\n{event}\n{event.__dict__}')

        if variations.exists():
            variations.calculate_main_lines(odds)
            self.store_variations(variations=variations)

        return {'back': odds}, variations.exists()
