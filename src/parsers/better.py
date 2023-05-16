import os
from datetime import datetime, timedelta
from json import loads
from typing import Generator, Union, Tuple

from models.event import Event
from models.market import Market
from models.variation import Variation, Variations
from parsers import ApiParser
from utils.calculations import str_to_date

translation_table = {'FBL': {'sport_id': 1, 'sport_name': 'Soccer'},
                     'BKB': {'sport_id': 2, 'sport_name': 'Basket'},
                     'TNS': {'sport_id': 5, 'sport_name': 'Tennis'}
                     }

market_translations = {'515894559': dict(market_id=1,
                                         market_name='1X2'),
                       '1097857087': dict(market_id=2,
                                          market_name='O/U'),
                       '2057603233': dict(market_id=9,
                                          market_name='BTTS'),
                       '-826827631': dict(market_id=3,
                                          market_name='H/H'),
                       '839811643': dict(market_id=5,
                                         market_name='O/U'),
                       '-1492771842': dict(market_id=6,
                                           market_name='HND'),
                       '323323928': dict(market_id=4,
                                         market_name='H/H'),
                       '1700601811': dict(market_id=7,
                                          market_name='O/U'),
                       '974581025': None
                       # Add a new market ID if they start sending it
                       # '': dict(market_id=8,
                       #                     market_name='HND')
                       }

INVERTED_DIRECTION = int(os.getenv('INVERTED_DIRECTION', 1))
PERCENTAGE_LIMIT = float(os.getenv('PERCENTAGE_LIMIT', 0))

URL = os.getenv('URL', 'https://wmnaz6ep53.execute-api.eu-south-1.amazonaws.com')
SLEEP = int(os.getenv('SLEEP', 100))

API_KEY = os.getenv('API_KEY')
PROVIDER = os.getenv('PROVIDER')


class BetterParser(ApiParser):

    def __init__(self):
        """ This is the Collection class that extends the Bookmaker class and gives us some additional info we need. """

        super().__init__(
            bookmaker_id=41,
            bookmaker_name='better',
            inverted_direction=INVERTED_DIRECTION,
            percentage_limit=PERCENTAGE_LIMIT,
            url=URL,
            sleep=SLEEP,
            sports={'fbl': 0, 'others': 1}
        )

    def get_event(self, event: any, last_update: datetime) -> Union[None, Event]:
        """
        This function parses the required data and creates a unique format for storage in MongoDB.
        We also use Redis to get previous odds, so that we can keep only the new ones, and also keep the historical
        odds without duplicates. If necessary - we can set the percentage below we will not accept the changes,
        as there will be a lot of calculations for the weighted average system unnecessarily.

        :param event: This is the event we parse.
        :param last_update: Last arrival date of the event.
        """

        event_id = int(event['id'])
        date = str_to_date(event['startDate'].split('.')[0])
        betradar_id = int(event.get('betradarId')) if 'betradarId' in event else None

        try:
            home, away = event['name'].replace('"', '\'').split(' - ', 1)
        except Exception as e:
            print('splitting error for name', event['name'], e)
            home, away = event['name'].replace('"', '\'').split('-', 1)

        if date < datetime.utcnow() - timedelta(minutes=10):
            print(f'Skipping event {event_id} because it started {date}')
            return

        return Event(
            _id=event_id,
            bookmaker_id=self.id,
            bookmaker_name=self.name,
            sport_id=event['sport_id'],
            sport_name=event['sport'],
            date=int(datetime.timestamp(date)),
            home_id=None,
            home_name=home,
            away_id=None,
            away_name=away,
            category_id=event['category_id'],
            category_name=event['category_name'],
            tournament_id=event['tournament_id'],
            tournament_name=event['tournament_name'],
            betradar_id=int(betradar_id) if betradar_id else None,
            status=True,  # Always
            last_update=int(datetime.timestamp(last_update))
        )

    def get_market(self, event: Event, markets: dict, current_event: Event) -> Tuple[dict, int]:

        """
        This function parses the market received according to our standard format

        :param event: Event that we are parsing.
        :param markets: Market data that we received
        """
        if current_event is None or current_event.back is None or not len(current_event.back):
            current_odds = Market.get_market_by_sport(event.sport_id)
        else:
            current_odds = current_event.back

        odds = Market.get_market_by_sport(event.sport_id)
        variations = Variations(event)

        for mark in markets:

            try:
                market = market_translations[mark['id']] or {}
                market_id = market.get('market_id')
                if not market_id:
                    print(mark)
                    continue

                market_name = market.get('market_name')
                sbv = mark.get('hv', '')
                if market_id == 2 and sbv != 2.5:
                    continue

                sbv = self.check_sbv(sbv=sbv, market_id=market_id)

                for sel in mark['selections']:
                    # outcome_id = sel['id']  # we don't need atm
                    outcome_name = str(sel['name']).capitalize()
                    price = sel['price'] or 0
                    odd = self.check_odd(float(price))
                    outcome_name = outcome_name.replace('Goal', 'Yes').replace('Nogoal', 'No')

                    if not market_name or not outcome_name or not sbv:
                        print(
                            f'Error! Market ({market_name}), outcome ({outcome_name}) or sbv ({sbv}) '
                            f'is missing: {sel}\n{mark}')
                        continue

                    if sbv not in odds[market_name]:
                        odds[market_name].update(Event.make_sbv(market=market_name, sbv=sbv))

                    if sbv not in current_odds[market_name]:
                        current_odds[market_name].update(Event.make_sbv(market=market_name, sbv=sbv))
                        prev_odd, prev_last_update = 0, ''
                    else:
                        prev = current_odds.get(market_name, {}).get(sbv, {}) \
                            .get(outcome_name, dict(odd=0, lastUpdate=0))
                        prev_odd, prev_last_update = prev.get('odd', 0), prev.get('lastUpdate', 0)

                    if odd == prev_odd and odd != 0:
                        odds[market_name][sbv][outcome_name].update(odd=odd, lastUpdate=prev_last_update)

                    if odd != prev_odd:
                        key = f'back.{market_name}.{sbv}.{outcome_name}'
                        if not self.percentage_checker(odd=odd, prev_odd=prev_odd, key=key):
                            continue

                        odds[market_name][sbv][outcome_name].update(dict(odd=odd, lastUpdate=event.last_update))
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
                print(f'get_market error: {e}\n{odds}{markets}')

        if variations.exists():
            variations.calculate_main_lines(odds)
            self.store_variations(variations=variations)

        return {'back': odds}, variations.exists()

    def get_all_events(self) -> Generator:
        """
        This function goes through events, process them and later stores them in a database.
        It creates a unique format for storage in MongoDB.
        Also, if we have at least one event, we put a heartbeat, which means that the feed is alive.
        """
        for sport in self.sports:

            headers = {
                "X-Api-Key": API_KEY,
                "Content-Type": "application/json"
            }
            resp = self.call_api(url=self.url + '/prod/feed/' + PROVIDER + '/prematch/' + sport,
                                 data={},
                                 headers=headers,
                                 func_name=f"{self.name} get_snapshot {sport}")

            data = resp.content.decode("utf-8")
            result = loads(data)

            for sport in result:
                try:
                    _sport = translation_table.get(sport['id'], {})
                    print(translation_table.get(sport['id'], {}).get('sport_name'))
                    for competition in sport['competitions']:
                        for event in competition['events']:
                            event.update({
                                'sport_id': _sport.get('sport_id'),
                                'sport': _sport.get('sport_name'),
                                'category_id': int(competition['countryId']),
                                'category_name': str(competition['countryName']).replace('"', '\''),
                                'tournament_id': int(competition['id']),
                                'tournament_name': str(competition['name']).replace('"', '\'')
                            })
                            yield event

                except Exception as e:
                    print(f'get_all_events error: {e}\n{sport}')
