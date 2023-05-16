import datetime
import io
import os
import socket
import time
from typing import Union, Tuple

import lxml.etree
import pytz
import requests
from lxml import etree
from lxml.etree import Element

from models.event import Event
from models.market import Market
from models.update import Update, BASKET_ID, SOCCER_ID, TENNIS_ID, SPORTS
from models.variation import Variation, Variations
from parsers import Parser
from utils.position import get_position_eurobet

utc = pytz.timezone('UTC')
cet = pytz.timezone('CET')

URL = os.getenv('URL', 'http://comparatore.eurobet.it/quotext.xml')

INVERTED_DIRECTION = int(os.getenv('INVERTED_DIRECTION', 0))
PERCENTAGE_LIMIT = int(os.getenv('PERCENTAGE_LIMIT', 0))

ALLOWED_MARKETS = [3, 18, 1128, 110, 26, 14863, 2, 983, 1127]


class EurobetParser(Parser):

    def __init__(self):
        super().__init__(1, 'eurobet-direct', INVERTED_DIRECTION, PERCENTAGE_LIMIT)
        self.positions = get_position_eurobet()
        self.sport_id = {'CALCIO': 1, 'BASKET': 2, 'TENNIS': 5}

    def last_update_time(self):
        return self._last_update

    def update_time(self):
        self._last_update = datetime.datetime.utcnow()
        print('updated', self._last_update)

    def _is_sport_allowed(self, event: Element) -> bool:
        sport_id = int(event.attrib['spc']) if 'spc' in event.attrib else 0
        if sport_id and sport_id in [1, 2, 3]:
            return True
        sport_name = event.attrib['sp'] if 'sp' in event.attrib else ''
        if sport_name and sport_name in ['CALCIO', 'BASKET', 'TENNIS']:
            return True
        return False

    def _get_sport_by_market(self, market_key) -> [int, str]:
        for sport_id, sport in self.positions.items():
            if market_key in sport:
                return [sport_id, sport[market_key]]
        return [0, '']

    def get_all_events(self):

        try:

            print('Start call to snapshot')
            content = io.BytesIO()

            r = requests.get(URL, headers={'User-Agent': 'om-agent'}, timeout=60)

            content.write(r.content)

            print('Snapshot ready')
            start = int(time.time())

            # ?? We have to parse all file to read the creation time ??

            content.seek(0)
            root = lxml.etree.parse(content)

            timestamp_tags = root.findall('CreationTime')
            if len(timestamp_tags) != 1:
                raise Exception('Invalid Creation Time')

            # Millisecond time so truncate to seconds
            timestamp = int(timestamp_tags[0].attrib['timestamp'][:-3])
            print('MAIN TIMESTAMP', timestamp)

            events = 0
            for programs in root.findall('Pr'):
                for item in programs.findall('Ev'):
                    try:
                        last_update = datetime.datetime.fromtimestamp(timestamp)
                        event = self.prepare_event(item, last_update, program_id=programs.attrib['cd'])
                        self.handle_event(event, last_update)
                    except Exception as e:
                        print('Error on parse event ', int(programs.attrib['cd'] + item.attrib['cd']))
                    finally:
                        events += 1

            stop = int(time.time())
            print(events, 'processed in ', stop - start, 'ms')

            return True

        except Exception as e:
            print('get_all_events_1:', e)
            time.sleep(30)
            return False

    def get_event(self, event: dict, last_update: datetime) -> Union[None, Event]:
        return Event(
            _id=event['_id'],
            bookmaker_id=event['bookmaker_id'],
            bookmaker_name=event['bookmaker_name'],
            home_id=event['home_id'],
            home_name=event['home_name'],
            away_id=event['away_id'],
            away_name=event['away_name'],
            category_id=event['category_id'],
            category_name=event['category_name'],
            date=event['date'],
            sport_id=event['sport_id'],
            sport_name=event['sport_name'],
            tournament_id=event['tournament_id'],
            tournament_name=event['tournament_name'],
            status=event['status'],
            betradar_id=event['betradar_id'],
            last_update=event['last_update']
        )

    def prepare_event(self, event: any, last_update: datetime, program_id) -> dict:
        """
        This function parses the required data and creates a unique format for storage in MongoDB.
        We also use Redis to get previous odds, so that we can keep only the new ones, and also keep the historical
        odds without duplicates. If necessary - we can set the percentage below we will not accept the changes,
        as there will be a lot of calculations for the weighted average system unnecessarily.

        :param event: This is the event we parse.
        :param last_update: Last arrival date of the event.
        :param program_id: Last arrival date of the event.
        """
        try:
            cet_start_date = cet.localize(datetime.datetime.strptime(event.attrib['dt'], '%Y/%m/%d %H:%M'))

            if not self._is_sport_allowed(event):
                raise Exception('Sport not allowed')

            event_name = event.attrib['ds'].split(' - ')
            if len(event_name) != 2:
                raise Exception('Event name ' + event.attrib['ds'] + ' no valid')

            event_id = int(program_id + event.attrib['cd'])

            # Store the betradar id {opmid} if provider is betradar {opid == 1}
            betradar_id = int(event.attrib['opmid']) if int(event.attrib['opid']) in (1, 7) else None

            return {
                '_id': event_id,
                'bookmaker_id': self.id,
                'bookmaker_name': self.name,
                'home_id': None,
                'home_name': event_name[0],
                'away_id': None,
                'away_name': event_name[1],
                'category_id': int(event.attrib['scc']),
                'category_name': event.attrib['sc'],
                'date': int(datetime.datetime.timestamp(cet_start_date)),
                'sport_id': self.sport_id[event.attrib['sp']],
                'sport_name': event.attrib['sp'].lower(),
                'tournament_id': int(event.attrib['spc']),
                'tournament_name': event.attrib['sp'],
                'status': event.attrib['st'] == 'Op',
                'betradar_id': betradar_id,
                'last_update': int(datetime.datetime.timestamp(last_update)),
                'markets': event
            }
        except Exception as e:
            print('parse_event main error', e, str(event))
            raise

    def get_market(self, event: Update, doc: Element, current_event) -> Tuple[dict, int]:

        if current_event is None or current_event.back is None or not len(current_event.back):
            odds = Market.get_market_by_sport(event.sport_id)
        else:
            odds = current_event.back

        variations = Variations(event)

        for m in doc.findall('Bf'):

            market_key = int(m.attrib['cd'])
            hn = float(m.attrib['hn'].replace(',', '')) / 100 if 'hn' in m.attrib else ''

            if (event.sport_id == SOCCER_ID and market_key in [3, 18, 1128]) or (
                    event.sport_name == BASKET_ID and market_key in [110, 26, 14863]) or (
                    event.sport_name == TENNIS_ID and market_key in [2, 983, 1127]):

                market = self.positions.get(event.sport_id).get(market_key)
                market_id = market.get('market_id', '')
                market_name = market.get('market_name', '')

                sbv = self.check_sbv(sbv=hn, market_id=market_id)
                if sbv == '':
                    continue

                for b in m.findall('Rs'):
                    try:

                        odd = 0 if b.attrib['odd'] == '-1' else float(b.attrib['odd']) / 100
                        outcome_name = market.get(int(b.attrib['cd'])).capitalize()

                        if not market_name or not outcome_name or not sbv:
                            print(f'Error! Market ({market_name}), outcome ({outcome_name}) or sbv ({sbv}) '
                                  f'is missing: {b.attrib}\n{event}')
                            continue
                        elif not market_name in odds:
                            raise f'Error! Market ({market_name}) is missing: {b.attrib}\n{event}'

                        if sbv not in odds[market_name]:
                            odds[market_name].update(Event.make_sbv(market=market_name, sbv=sbv))
                            prev_odd, prev_last_update = 0, 0
                        else:
                            prev = odds.get(market_name, {}).get(sbv, {}) \
                                .get(outcome_name, dict(odd=0, lastUpdate=0))
                            prev_odd, prev_last_update = prev.get('odd', 0), prev.get('lastUpdate', 0)

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
                            ))
                    except Exception as e:
                        print(f'get_market error: {e}\n{event.__dict__}\n{b.attrib}')

        if variations.exists():
            variations.calculate_main_lines(odds)
            self.store_variations(variations=variations)

        return {'back': odds}, variations.exists()

    def parse_new_event(self, doc: Element, timestamp: int):
        try:
            last_update = datetime.datetime.fromtimestamp(timestamp)
            event_elem = doc.find('Ev')
            event = self.prepare_event(event_elem, last_update, program_id=doc.attrib['pc'])
            self.handle_event(event, last_update)
        except Exception as e:
            print('parse_new_event error', e, str(doc))

    def parse_update_event(self, doc, timestamp):
        try:

            program_id = doc.attrib['pc']

            event_elem = doc.find('Ev')

            event_name = event_elem.attrib['ds'].split('-')
            if event_name and len(event_name) != 2:
                raise Exception('Event name not valid')

            event = self.load_event('{}:{}{}'.format(self.name, program_id, event_elem.attrib['cd']))
            if event is None:
                event = Update(
                    _id=int(program_id + event_elem.attrib['cd']),
                    bookmaker_id=self.id,
                    bookmaker_name=self.name,
                    sport_id=self.sport_id[event_elem.attrib['sp']],
                    sport_name=event_elem.attrib['sp'],
                    last_update=int(timestamp)
                )

            if 'dt' in event_elem.attrib:
                cet_start_date = cet.localize(datetime.datetime.strptime(event_elem.attrib['dt'], '%Y/%m/%d %H:%M'))
                event.date = int(datetime.datetime.timestamp(cet_start_date.astimezone(utc)))

            event.home_name = event_name[0]
            event.away_name = event_name[1]

            if 'scc' in event_elem.attrib:
                event.category_id = int(event_elem.attrib['scc'])
            if 'sc' in event_elem.attrib:
                event.category_name = event_elem.attrib['sc']

            if 'spc' in event_elem.attrib:
                event.tournament_id = int(event_elem.attrib['spc'])
            if 'sp' in event_elem.attrib:
                event.tournament_name = event_elem.attrib['sp']

            if 'st' in event_elem.attrib:
                event.status = event_elem.attrib['st'] == 'Op'

            if 'opid' in event_elem.attrib and int(event_elem.attrib['opid']) == 1:
                event.betradar_id = int(event_elem.attrib['opmid'])

            self.store(event)

        except Exception as e:
            print('parse_update_event error', e, str(doc))

    def parse_change_bet(self, doc: Element, timestamp: int) -> Union[None, dict]:
        try:

            odds_state = doc.attrib['oddsState']
            market_key = int(doc.attrib['bc']) if odds_state == 'updated' else int(doc.find('Bf').attrib['cd'])

            if market_key not in ALLOWED_MARKETS:
                return

            sport_id, market = self._get_sport_by_market(market_key)
            if sport_id == 0:
                return

            event = self.load_event('{}:{}{}'.format(self.name, doc.attrib['pc'], doc.attrib['ec']))

            if event is None:
                event = Update(
                    _id=int(doc.attrib['pc'] + doc.attrib['ec']),
                    bookmaker_id=self.id,
                    bookmaker_name=self.name,
                    sport_id=sport_id,
                    sport_name=SPORTS.get(sport_id),
                    last_update=int(timestamp)
                )

            if odds_state == 'new':
                markets = doc
            else:
                element = Element('Bf')
                element.set('cd', doc.attrib['bc'])
                element.set('hn', doc.attrib['hn'])
                for i in doc.iter('Rs'):
                    element.append(i)
                markets = Element('VAR_DATA')
                markets.append(element)

            odds = self.get_market(event, markets, event)
            event.set_odds(odds)

            self.store(event)

        except Exception as e:
            print('parse_change_bet error:', e, str(doc))

    def parse_event_state(self, doc, timestamp):
        try:
            event = self.load_event('{}:{}{}'.format(self.name, doc.attrib['pc'], doc.attrib['ec']))
            event.status = doc.attrib['st'] if 'st' in doc.attrib else False
            self.store(event)
        except Exception as e:
            print('parse_event_state error:', e, str(doc))

    def handle_variation(self, msg):

        try:
            msg = msg.decode('utf-8')
            msg = msg.strip()
        except Exception as e:
            print('handle_variation error (can\'t decode): ' + str(msg) + str(e))
            return

        try:
            doc = etree.fromstring(msg)
            if doc is None:
                return

            var_id = doc.attrib['cd']
            service_id = doc.attrib['vs']
            timestamp = int(doc.attrib['vp'][:-3])

            if service_id == '261':
                return

            vdata = doc.find('VAR_DATA')
            if vdata is None:
                print('NO VDATA:', str(msg))
                return

            if var_id == '10001':
                print('heartbeat', dict(time=doc.attrib['vp'], timestamp=timestamp))
            elif var_id == '11051':
                print('Received parse_new_event variation:', msg)
                self.parse_new_event(doc=vdata, timestamp=timestamp)
            elif var_id == '11105':
                print('Received parse_update_event variation:', msg)
                self.parse_update_event(doc=vdata, timestamp=timestamp)
            elif var_id == '10304':
                print('Received parse_change_bet variation:', msg)
                self.parse_change_bet(doc=vdata, timestamp=timestamp)
            elif var_id == '11041':
                self.parse_event_state(doc=vdata, timestamp=timestamp)
            else:
                return None

        except Exception as e:
            print("COME ON (handle_variation): " + str(e))

    def handle(self):

        print('Socket handle')

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('0.0.0.0', 4321))
            print('Port listen on 0.0.0.0:4321 ')
            s.listen(5)
        except socket.error as msg:
            print('Socket error:. Msg: ' + str(msg))
            s.shutdown(socket.SHUT_RDWR)
            s.close()

        print('Socket ready to accept')
        msg_buffer = b''

        while True:

            try:
                conn, addr = s.accept()
            except Exception as e:
                print('Socket conn error:', e)
                s.shutdown(socket.SHUT_RDWR)
                s.close()
                continue

            try:

                print('*' * 15, 'address', addr, '*' * 15, str(datetime.datetime.utcnow()).split('.')[0],
                      int(round(time.time())))

                with conn:

                    while True:

                        try:
                            msg = conn.recv(32768)
                            if not msg:
                                continue

                            msg_buffer = b''.join([msg_buffer, msg])
                            *complete_msg_list, tail = msg_buffer.split(b'\n')
                            msg_buffer = tail

                            for item in complete_msg_list:
                                self.handle_variation(item)

                        except Exception as e:
                            print('EXC: ' + str(e))

            except Exception as e:
                print('eurobet_socket_feed error 2:', e)
