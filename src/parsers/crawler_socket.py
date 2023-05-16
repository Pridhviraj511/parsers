import json
import os
from datetime import datetime
from json import loads, dumps
from threading import Event as ThreadEvent
from time import time
from traceback import print_exc
from typing import List, Union, Tuple

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.watch import DocumentChange

from models.event import Event
from models.market import Market
from models.variation import Variation, Variations
from parsers import ApiParser
from utils.calculations import str_to_date
from utils.position import get_position_crawler

URL = os.getenv('URL', 'https://us-central1-crawler-api-b7221.cloudfunctions.net/')
CRAWLER_API_KEY = os.getenv('CRAWLER_API_KEY')
CRAWLER_CHANNEL = os.getenv('CRAWLER_CHANNEL', None)




class CrawlerSocket(ApiParser):

    def __init__(self, bookmaker_id: int, bookmaker_name: str, inverted_direction: int, percentage_limit: float):
        """ This is the Crawler class that extends the Bookmaker class and gives us some additional info we need. """

        self.token_url = URL + 'getAuthToken'
        self.snapshot_url = URL + 'get' + bookmaker_name.capitalize() + 'Snapshot'
        self.changes_url = URL + 'get' + bookmaker_name.capitalize() + 'Changes?uid='
        self.health_url = URL + 'healthCheck' + bookmaker_name.capitalize()
        self.position = get_position_crawler()
        self.token = ''
        self.timestamp = None
        self.restart = False
        self.callback_done = ThreadEvent()

        cred = credentials.Certificate({"type": "service_account", "project_id": "crawler-api-b7221",
                                         "private_key_id": "d22e3c378a8193fa9fa5095147ed7f06fe3c52d3",
                                         "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCWhDwiDg88Cv16\n47Q0NyBSoiXvO7tdn5ShWurSQTdPYY7KbLs0MZDnIsBj+fZx+9m628PPkrj1g2d0\n2Cag9H8aYEVZA83qT2Lbx/3SmK3/cYcm9u3cMppKfydJvNXtYMNvm+O8L7ot2tju\nPM1s9PjNQL33vQg8sFiw4Ukjd120U37zvEEXZgI40LPof0/gnLXeHvRRyJLhG7Zl\nwJUB8xRXNSU0LNfSdQbKiUPzP+/o+vidSEjG8Je0lDJvUCm0xhpxO1d2m7mEKGEu\ntGhSLS9MNCW94ukM4JUsVeo9bwQ5jd14ruvwRduZBbSokYSqULYM2bqRUx02dvzJ\n79+P4m3HAgMBAAECggEACWzudxN6UMA/b1qjBkINfB87UOfkq9A6doBDBDehRw9M\n6dA1SOdxs4exlJEqpain0dPBR1Zgzr8T03VVte6ZpwUwUoqycmHWRv0XIAD/pGdv\nlzkPXCKvFssvoqZ4nwzYMD0K3dX/Sq/RtdmI47HTgsbzHnhv85z3cNwqwFXRQGGB\nk5oucvhn2E2/LlWR4ehslbibpEUtvxoltF/VQyuFjQpxMxxTpMB0dQu+NX/qrkOm\nTDF6xan9EOI+A772sug5Akt/lTpKd0y9OvoBTXQmIBFv3GZPVDChbjqFOaGulLcf\nh4ImSZQJvVAkVUoWgGfSSYKwAM3NdWSNs9Dg4RB5wQKBgQDGWr8kynkshwhjjeer\nN2KjwlmMAH8/VI+x/u/iaPzdIGMAFbpaEVsZOCIERaGI8g3PEuCO0LOUC7ae9gKz\nSxxacJ8HeSuTK3LyYE04yp0k7wig3dsqY3BAYQr17+cG4TMJcHrB7TkgBkDIBilC\nijdAodUbP76WvxXHJ9s8NKWWPQKBgQDCQmxD5rJF7lCUdz1OXLtpjblYix9ITa0m\n7TTmTw6febDR7zGyFa4QKRiy4CMhtqgDICBuKdcK90FzKaWjNVUrooM+epOZhaur\nNMA+iLg9AGDrT21QOKleWMUABT2fIRsv8CVUshAE2IPyyG6CWBhK6vUO4e90zRYp\noitM52EYUwKBgEFHHCC/gaFlzxz0VonCcHP0QgQRJc9xxNiPTeL1KkKbpfkhLXL2\nw0RJdOhzAfZPsruzOrPFe1P9htxJmhnnXi1lYvDSr8R/SBT8HG3UQGMnR2+pk7cf\ngpGtXi4SBbX95w30NnIb3/DqHee2H14Gnqhmmfudvttdh41DUKM/sD8BAoGBAKYV\n5DqpowHnHz3QNLoqzpEQescZK0XGI6SEahX+waHXiTX0K6j2oDtw540H1QGeCUei\n0Bdf7luRyoOLt/IyRv9nko54fnljr8JQ94x/mAWPrU2COxO7XhMsEkJSOL00sOnr\nh/9BvjBmbWnFs7X9W8ex2pM+2FwkfC5cWGkH6hvBAoGAKKzDi0J9pTaQ9m4vBnMQ\nZXXTIlQ3yjBwZLN38prgxrBjKwsNAywMT3nsuIo8rvJhhF6i3TJ5d5UAeoBFdGOl\nWQbfKgC86N9cZQsxdknWKADXenU4DDaeBJnIh4i1kSaZ6Pn5rf4JRazKVYDOsoA/\nAX2zbm3zNpFDLKS0JKeFS7I=\n-----END PRIVATE KEY-----\n",
        "client_email": "oddsandmore@crawler-api-b7221.iam.gserviceaccount.com",  "client_id": "111475949532761494129",
                                         "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                                         "token_uri": "https://oauth2.googleapis.com/token",
                                         "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                                         "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/oddsandmore%40crawler-api-b7221.iam.gserviceaccount.com" })
        firebase_admin.initialize_app(cred)

        self.db = firestore.client()

        super().__init__(
            bookmaker_id=bookmaker_id,
            bookmaker_name=bookmaker_name,
            inverted_direction=inverted_direction,
            percentage_limit=percentage_limit,
            sports={1: 1, 2: 2, 3: 5},
            url=URL,
            sleep=0
        )

    def get_snapshot(self):
        """
        It gets a snapshot of all the data, stores it in logs, and calls functions that handle the events we receive.
        """

        print('GETTING SNAPSHOT')

        try:

            resp = self.call_api(url=self.token_url, headers={}, data={}, func_name='get_token',
                                 timeout=120, get_method=False, to_print=False)
            data = resp.json()
            headers = {
                'Authorization': 'Bearer ' + data['token'],
                'Content-Type': 'application/json'
            }

            resp = self.call_api(url=self.snapshot_url, headers=headers, data={},
                                 func_name='get_snapshot', timeout=120, get_method=True, to_print=True)

            if resp.status_code != 200:
                self.restart = True
                return

            data = resp.content.decode('utf-8')
            with open('feed.json', 'w') as file:
                file.write(data)
            data = loads(data)
            self.timestamp = data['uid']
            print(f'\t\t\tSTART\n{dumps(data)}')
            self.handle_events(data['data'], self.timestamp)

            ddd = datetime.utcnow()
            print(f'---> time {datetime.utcnow() - ddd} for bulk_write')

            self.restart = False

        except Exception as e:
            # print(f'get_snapshot error: {e}')
            self.restart = True

    def get_event(self, event: dict, last_update: datetime) -> Union[None, Event]:
        """
        This function parses the required data and creates a unique format for storage in MongoDB.
        We also use Redis to get previous odds, so that we can keep only the new ones, and also keep the historical
        odds without duplicates. If necessary - we can set the percentage below we will not accept the changes,
        as there will be a lot of calculations for the weighted average system unnecessarily.

        :param event: This is the event we parse.
        :param last_update: Date and time (UTC) when this process started.
        """
        event_id = int(event['event_id'])
        event_status = event['event_status'] == 1
        date = str_to_date(event['date'])

        if date < datetime.utcnow():
            print(f'Skipping event {event_id} because it started {date}')
            return

        spot_id = self.sports.get(event['sport_id'], 0)

        return Event(
            _id=event_id,
            bookmaker_id=self.id,
            bookmaker_name=self.name,
            date=int(datetime.timestamp(date)),
            home_id=None,
            home_name=str(event['home_name']),
            away_id=None,
            away_name=str(event['away_name']),
            sport_id=spot_id,
            sport_name='',
            category_id=int(event['category_id']) if event['category_id'] else None,
            category_name=event['category_name'],
            tournament_id=int(event['tournament_id']) if event['tournament_id'] else None,
            tournament_name=str(event['tournament_name']),
            betradar_id=int(event['betradar_id']) if event.get('betradar_id') else None,
            status=event_status,
            last_update=int(datetime.timestamp(last_update)),
            aams=str(event_id)[1:6] + '.' + str(event_id)[6:] if self.id in {1} else ''
        )

    def get_market(self, event: Event, markets: dict, current_event: Event) -> Tuple[dict, int]:
        """
        This function parses the market received according to our standard format

        :param event: Event that we are parsing.
        :param markets: Market data that we received
        :param current_event: Last received event
        """

        if current_event is None or current_event.back is None or not len(current_event.back):
            odds = Market.get_market_by_sport(event.sport_id)
        else:
            odds = current_event.back

        variations = Variations(event)

        for m_name, item in markets.items():  # Iterating through markets
            try:
                m_id = self.position.get(event.sport_id, {}).get(m_name, {}).get('market_id', None)
                market_name = self.position.get(event.sport_id, {}).get(m_name, {}).get('market_name', '')

                if not m_id:
                    # print(f'{self.name} error: No market id for this item {item} and sport {event.sport_id}')
                    continue

                for outcome in item['outcomes']:  # Iterating through outcomes
                    odd = self.check_odd(outcome['odd']) if item['market_status'] == 1 and event.status else 0
                    sbv = self.check_sbv(sbv=outcome['sbv'], market_id=m_id)
                    outcome_name = str(outcome['name']).capitalize().replace('Goal', 'Yes').replace('Nogoal', 'No')

                    if not market_name or not outcome_name or not sbv:
                        continue
                    elif market_name not in odds:
                        raise f'Error! Market ({market_name}) is missing: {odds}\n{event}'

                    if sbv not in odds[market_name]:
                        odds[market_name].update(Event.make_sbv(market=market_name, sbv=sbv))
                        prev_odd, prev_last_update = 0, ''
                    else:
                        prev = odds.get(market_name, {}).get(sbv, {}).get(outcome_name, dict(odd=0, lastUpdate=''))
                        prev_odd, prev_last_update = prev.get('odd', 0), prev.get('lastUpdate', '')

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
                print(f'{self.name} error (process_event 3): {e}\nevent:{event.__dict__}\nmarket:{markets}')
                print_exc()
                raise e

        if variations.exists():
            variations.calculate_main_lines(odds)
            self.store_variations(variations=variations)

        return {'back': odds}, variations.exists()

    def handle(self):
        """
        Callback on_change function to capture document changes
        """

        print('Start to get snapshot')
        # self.get_snapshot()

        now = time()

        channel = os.getenv('CRAWLER_CHANNEL', self.name)

        print(f'Start to listen on {channel}/logs/list')
        doc_ref = self.db.collection(channel + u'/logs/list').where(u'uid', u'>=', now)

        # Watch the document changes
        doc_ref.on_snapshot(self.on_change_handler)

    def on_change_handler(self, doc_snapshot, changes: List[DocumentChange], read_time):
        for change in changes:
            timestamp = change.document.to_dict()['uid']
            events = json.loads(change.document.to_dict()['avvenimenti'])
            self.handle_events(events, timestamp)
        self.callback_done.set()

    def handle_events(self, events: List[dict], control_date: int):
        """
        This function goes through events, calls functions to process them and later stores them in a database.
        Also, if we have at least one event, we put a heartbeat, which means that the feed is alive.

        :param events: Events we need to process and store.
        :param control_date: Timestamp from feed.
        """

        last_update = datetime.utcnow()
        print(f'Control date: {control_date}')

        ddd = datetime.utcnow()
        for event in events:
            self.handle_event(event, last_update)

        print(f'---> time {datetime.utcnow() - ddd} for processing {len(events)} events')
        self.heartbeat()
