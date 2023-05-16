import os
import time
from base64 import b64encode
from datetime import datetime
from typing import Generator, Union, List, Tuple
from urllib.parse import urlencode

from pytz import timezone

from models.event import Event
from models.market import Market
from models.update import SPORTS
from models.variation import Variations, Variation
from parsers import ApiParser
from utils.calculations import str_to_date

utc = timezone('utc')

INVERTED_DIRECTION = int(os.getenv('INVERTED_DIRECTION', 0))
PERCENTAGE_LIMIT = float(os.getenv('PERCENTAGE_LIMIT', 0))

URL = os.getenv('URL', 'https://api.pinnacle.com/v1')
SLEEP = int(os.getenv('SLEEP', 15))

LIVE = int(os.getenv('LIVE', 0)) == 1


class PinnacleParser(ApiParser):

    def __init__(self):
        """ This is the Pinnacle class that extends the Bookmaker class and gives us some additional info we need. """

        super().__init__(
            bookmaker_id=3,
            bookmaker_name='pinnacle',
            inverted_direction=INVERTED_DIRECTION,
            percentage_limit=PERCENTAGE_LIMIT,
            url=URL,
            sleep=SLEEP,
            sports={29: 1, 4: 2, 33: 5, 34: 23}
        )

        self.LAST_UPDATE = 0
        self.LAST_EVENTS = {29: 0, 4: 0, 33: 0, 34: 0}
        self.LAST_ODDS = {29: 0, 4: 0, 33: 0, 34: 0}
        self.live: bool = LIVE

    @property
    def _get_headers(self) -> dict:

        USERNAME = os.getenv('USERNAME')
        PASSWORD = os.getenv('PASSWORD')
        return dict(
            Authorization="Basic " + b64encode((USERNAME + ":" + PASSWORD).encode("utf-8")).decode('utf-8')
        )

    def _moneyline(self, doc: dict, sport_id: int, status: bool, tmp: dict):
        """
        This is the market 1X2 for soccer or HH for basketball or tennis.

        :param doc: Document from which we obtain data.
        :param sport_id: Sport ID so we can decide on the market name.
        :param status: Status from event and markets so we can remove odds if needed.
        :param tmp: A dictionary in which we return the available markets.
        """

        outcome = {}

        if len(doc.keys()) == 2 and sport_id in {4, 33, 34}:
            outcome.update({'1': dict(odd=self.round_number(doc['home']) if status else 0,
                                      lastUpdate=self.LAST_UPDATE),
                            '2': dict(odd=self.round_number(doc['away']) if status else 0,
                                      lastUpdate=self.LAST_UPDATE)})
            if outcome['1']['odd'] != 0 or outcome['2']['odd'] != 0:
                # TODO OR or AND..check if they want to show only one odd.
                tmp['H/H'].update({"#": outcome})

        elif len(doc.keys()) == 3 and sport_id == 29:
            outcome.update({'1': dict(odd=self.round_number(doc['home']) if status else 0,
                                      lastUpdate=self.LAST_UPDATE),
                            'X': dict(odd=self.round_number(doc['draw']) if status else 0,
                                      lastUpdate=self.LAST_UPDATE),
                            '2': dict(odd=self.round_number(doc['away']) if status else 0,
                                      lastUpdate=self.LAST_UPDATE)})
            if outcome['1']['odd'] != 0 or outcome['2']['odd'] != 0 or outcome['X']['odd'] != 0:
                tmp['1X2'].update({"#": outcome})

    def _totals(self, doc: dict, sport_id: int, status: bool, tmp: dict):
        """
        This is the market OVER/UNDER 2.5 for soccer or OVER/UNDER for basketball or tennis.

        :param doc: Document from which we obtain data.
        :param sport_id: Sport ID so we can decide on the market name.
        :param status: Status from event and markets so we can remove odds if needed.
        :param tmp: A dictionary in which we return the available markets.
        """

        outcomes, averages = {}, {}

        for item in doc:
            sbv = '#' if sport_id == 29 and item['points'] == 2.5 else str(item['points']).replace('.', ',')

            if sport_id == 29 and sbv != '#':
                continue

            outcome = {
                'Over': dict(odd=self.round_number(item['over']) if status else 0,
                             lastUpdate=self.LAST_UPDATE),
                'Under': dict(odd=self.round_number(item['under']) if status else 0,
                              lastUpdate=self.LAST_UPDATE),
            }

            if outcome['Over']['odd'] != 0 and outcome['Under']['odd'] != 0:
                avg = abs(outcome['Over']['odd'] - outcome['Under']['odd'])
                outcomes.update({sbv: outcome})
                averages.update({sbv: avg})

        if self.live:
            for n, item in enumerate(sorted(averages.items(), key=lambda data: data[1])):
                if self.live and n > 1:
                    break
                tmp['O/U'].update({item[0]: outcomes[item[0]]})
        else:
            tmp['O/U'].update(outcomes)

    def _spreads(self, doc: dict, status: bool, tmp: dict):
        """
        This is the market HANDICAP for basketball or tennis.

        :param doc: Document from which we obtain data.
        :param status: Status from event and markets so we can remove odds if needed.
        :param tmp: A dictionary in which we return the available markets.
        """

        outcomes, averages = {}, {}

        for item in doc:
            sbv = str(item['hdp']).replace('.', ',')

            outcome = {
                '1': dict(odd=self.round_number(item['home']) if status else 0,
                          lastUpdate=self.LAST_UPDATE),
                '2': dict(odd=self.round_number(item['away']) if status else 0,
                          lastUpdate=self.LAST_UPDATE),
            }

            if outcome['1']['odd'] != 0 and outcome['2']['odd'] != 0:
                avg = abs(outcome['1']['odd'] - outcome['2']['odd'])
                outcomes.update({sbv: outcome})
                averages.update({sbv: avg})

        if self.live:
            for n, item in enumerate(sorted(averages.items(), key=lambda data: data[1])):
                if self.live and n > 1:
                    break
                tmp['HND'].update({item[0]: outcomes[item[0]]})
        else:
            tmp['HND'].update(outcomes)

    def _period(self, doc: dict, sport_id: int) -> dict:
        """
        Searching the period to find markets we use.
        Status:
            1 - online, period is open for betting
            2 - offline, period is not open for betting

        :param doc: Document from which we obtain data.
        :param sport_id: Sport ID so we can decide on the market name.

        :return: A dictionary with available markets.
        """

        tmp = Market.get_market_by_sport(sport_id=self.sports.get(sport_id))
        status = doc['status'] == 1

        try:

            if 'moneyline' in doc:
                self._moneyline(doc=doc['moneyline'], sport_id=sport_id, status=status, tmp=tmp)

            if 'totals' in doc:
                self._totals(doc=doc['totals'], sport_id=sport_id, status=status, tmp=tmp)

            if 'spreads' in doc and sport_id in {4, 33, 34}:
                self._spreads(doc=doc['spreads'], status=status, tmp=tmp)

        except Exception as e:
            print(self.name, 'error (_period)', e)

        return tmp

    def _load_events(self, sport_id: int, event_ids: List[str]):
        """
        Calling an API for the attached sport and getting fixtures for events that match the filter.

        API params:
        If param isLive=1 we receive live events only, otherwise if the value is missing or any other value will result
        in retrieval of events regardless of their Live status.

        Param "since" is used to receive incremental updates. Use the value of last from previous fixtures response.
        When since the parameter is not provided, the fixtures are delayed up to 1 minute to encourage the use of
        the parameter.

        Fixture data:
        status:
        (This is deprecated parameter, please check period's `status` in the `/odds` endpoint to see if it's open
        for betting.)
            O = This is the starting status of a game.
            H = This status indicates that the lines are temporarily unavailable for betting,
            I = This status indicates that one or more lines have a red circle (lower maximum bet amount).

        liveStatus:
            0 = No live betting will be offered on this event,
            1 = Live betting event,
            2 = Live betting will be offered on this match, but on a different event (it will send live event later,
            with the new id, but parentId will be id of this match).

        resultingUnit:
          Specifies based on what the event will be resulted, e.g.
            Corners,
            Bookings,
            Regular..

        :param sport_id: The sport we take events for.
        """

        query_dict = {
            'sportId': sport_id,
            'isLive': 1 if self.live else 0
        }

        if len(event_ids) > 150:
            query_dict['since'] = 0
        else:
            query_dict['eventIds'] = ','.join(event_ids)

        response = self.call_api(f'{self.url}/fixtures?{urlencode(query_dict)}', headers=self._get_headers, data={},
                                 func_name='_load_events')
        if len(response.text) == 0:
            return {}

        return response.json()

    def _load_odds(self, sport_id):
        """
        Calling an API for the attached sport and getting odds for events that match the filter.

        API params:
        To retrieve only live odds set the value to 1 (isLive=1). Otherwise, response will get all odds.

        Param "since" is used to receive incremental updates. Use the value of last from the previous odds response.
        When since the parameter is not provided, the odds are delayed up to 1 min to encourage the use of the
        parameter. Please note that when using the since parameter you will get in the response ONLY changed periods.
        If a period did not have any changes it will not be in the response.

        The format in which we get the odds can be one of these:
        [American, Decimal, HongKong, Indonesian, Malay]. Default is American.

        :param sport_id: The sport we take odds for.
        """

        try:
            query_dict = {
                'sportId': sport_id,
                'oddsFormat': "Decimal",
                'isLive': 1 if self.live else 0
            }

            if self.LAST_ODDS[sport_id] > 0:
                query_dict['since'] = self.LAST_ODDS[sport_id]

            response = self.call_api(f'{self.url}/odds?{urlencode(query_dict)}', headers=self._get_headers, data={},
                                     func_name='_load_odds')
            if len(response.text) == 0:
                return []

            data = response.json()
            if not data:
                return []

            self.LAST_ODDS[sport_id] = data['last']

            _markets = dict()

            for league in data['leagues']:
                for event in league['events']:
                    # home_score = event.get('homeScore', 0.0)
                    # away_score = event.get('awayScore', 0.0)
                    for period in event['periods']:
                        if period['number'] == 0:  # Period of the match that is being bet on.
                            # if event['id'] in self._events[sport_id].keys():  # if we get events first, and then odds
                            # event_list.append(event['id'])
                            _markets[event['id']] = self._period(period, sport_id)
                            # if self.live:
                            #     self._events \
                            #         .get(sport_id, {}) \
                            #         .get(event['id'], {}) \
                            #         .update({'home_score': home_score, 'away_score': away_score})
                            break
            return _markets
        except Exception as e:
            print(f'{self.name} error (_load_odds) {e}')

    def get_all_events(self) -> Generator:
        """
        This function takes the odds for the sport specified in the sport_id parameter.
        Documentation: https://pinnacleapi.github.io/#operation/Odds_Straight_V1_Get

        :param sport_id: The sport id to retrieve the fixtures for. *Required parameter*.
        :param kwargs: Dictionary that can contain additional parameters we need:
                       leagueIds=[], isLive=1, since=123456789, eventIds=[], oddsFormat="Decimal", toCurrencyCode="AED"
        :return: Returns a dictionary of event fixtures.
        """

        print('loading events since', self.LAST_EVENTS)
        print('loading odds since', self.LAST_ODDS)

        for sport_id in self.sports:
            odds = self._load_odds(sport_id)

            events = self._load_events(sport_id, [str(k) for k in odds])

            for league in events.get('league', {}):
                for event in league.get('events', {}):
                    try:

                        if event['resultingUnit'] != 'Regular':
                            continue

                        if not self.live and (event['liveStatus'] == 1 or 'parentId' in event.keys()):
                            continue  # if prematch data, we skip live events.

                        if event['id'] in odds:
                            yield dict(
                                sport_id=int(sport_id),
                                league_id=league['id'],
                                league_name=league['name'],
                                event_id=event['id'],
                                parent_id=event.get('parentId', None),
                                start_date=event['starts'],
                                home_name=event['home'],
                                away_name=event['away'],
                                live_status=event['liveStatus'],
                                status=True,
                                # event['status'] it's deprecated so we always put True, and use odds status
                                markets=odds[event['id']]
                            )
                    except Exception as e:
                        print(f'{self.name} error (_load_events 2) {e}')

        self.LAST_UPDATE = int(time.time())

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
        sport_id = self.sports.get(event['sport_id'], 0)
        event_status = event['status']
        date = int(str_to_date(event['start_date'].replace('Z', '')).timestamp())

        # if not self.live and date < curr_time(False):
        #     print(f'Skipping event {event_id} because it started {date}')
        #     return

        # if is_main:
        #     self.active_events.append(event_id)

        category_name = event['league_name'].split(' - ')[0]

        return Event(
            _id=event_id,
            bookmaker_id=self.id,
            bookmaker_name=self.name,
            date=date,
            sport_id=sport_id,
            sport_name=SPORTS[sport_id],
            home_id=None,
            home_name=str(event['home_name']),
            away_id=None,
            away_name=str(event['away_name']),
            category_id=sport_id,
            category_name=category_name,
            tournament_id=int(event['league_id']),
            tournament_name=str(event['league_name']),
            betradar_id=0,
            status=event_status,
            live=bool(event['live_status'] == 1),
            last_update=int(last_update.timestamp())
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

        odds = Market.get_market_by_sport(sport_id=event.sport_id)
        variations = Variations(event)

        for market_name, item in markets.items():
            try:
                for sbv, other in item.items():
                    for outcome_name, outcome in other.items():
                        odd = outcome['odd']

                        if not market_name or not outcome_name or not sbv:
                            print(f'Error! Market ({market_name}), outcome ({outcome_name}) or sbv ({sbv}) '
                                  f'is missing: {outcome}\n{event}')
                            continue

                        if sbv not in odds[market_name]:
                            odds[market_name].update(event.make_sbv(market=market_name, sbv=sbv))

                        if sbv not in current_odds[market_name]:
                            current_odds[market_name].update(event.make_sbv(market=market_name, sbv=sbv))
                            prev_odd, prev_last_update = 0, ''
                        else:
                            prev = current_odds.get(market_name, {}).get(sbv, {}) \
                                .get(outcome_name, dict(odd=0, lastUpdate=0))
                            prev_odd, prev_last_update = prev.get('odd', 0), prev.get('lastUpdate', 0)

                        if odd == prev_odd and odd != 0:
                            odds[market_name][sbv][outcome_name] \
                                .update(odd=odd, lastUpdate=prev_last_update)

                        if odd != prev_odd:
                            key = f'back.{market_name}.{sbv}.{outcome_name}'
                            if not self.percentage_checker(odd=odd, prev_odd=prev_odd, key=key):
                                continue

                            odds[market_name][sbv][outcome_name].update(outcome)

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
                print(f'get_market error: {e}\n{event}\n{markets}\n{item}')

        if variations.exists():
            variations.calculate_main_lines(odds)
            self.store_variations(variations=variations)

        return {'back': odds}, variations.exists()
