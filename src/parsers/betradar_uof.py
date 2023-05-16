import logging
import os
import ssl
import time
from copy import deepcopy
from datetime import datetime
from time import sleep
from typing import Union, Tuple, Dict, Any
from uuid import uuid4

import pika
from bson.json_util import dumps
from lxml.etree import XML, Element, XMLSyntaxError, tostring
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import BasicProperties, Basic
from pymongo import UpdateOne
from requests import get

from models.event import FeedMakerEvent as Event, OutRight
from models.variation import Variation, Variations
from parsers._parser import client
from ._betradar import BetradarParser

INVERTED_DIRECTION = int(os.getenv('INVERTED_DIRECTION', 1))
PERCENTAGE_LIMIT = float(os.getenv('PERCENTAGE_LIMIT', 0))
OUTRIGHT_COLLECTION = os.getenv("OUTRIGHT_COLLECION", "activeOutrights")

URL = os.getenv('URL', '')
SLEEP = int(os.getenv('SLEEP', 100))
HUNDRED_YEARS = 60 * 60 * 24 * 365 * 100
THOUSAND_SECONDS = 1000

MESSAGING_HOST = os.getenv('MESSAGING_HOST', 'global.stgmq.betradar.com')
API_URL = os.getenv("API_URL", "https://stgapi.betradar.com")

BETRADAR_USERNAME = os.getenv('BETRADAR_USERNAME', '')
BETRADAR_TOKEN = os.getenv('BETRADAR_TOKEN', '')
BETRADAR_EXCHANGE = "unifiedfeed"
BETRADAR_PORT = 5671

PRIORITY = os.getenv("PRIORITY", '-')
PRE_MATCH_INTEREST = os.getenv("PRE_MATCH_INTEREST", '-')
LIVE_INTEREST = os.getenv('LIVE_INTEREST', '-')
MESSAGE_TYPE = os.getenv('MESSAGE_TYPE', 'odds_change')
SPORT_ID = os.getenv('SPORT_ID', '-')
URN_SPORT_ID = os.getenv('URN_SPORT_ID', '-')
SPORT_ID_WITHOUT_URN = os.getenv('SPORT_ID_WIHTHOUT_URN', '-')
NODE_ID = os.getenv('NODE_ID', '-')

DEBUG = os.getenv("DEBUG", "0") == "1"
EVENT_EXPIRE_TIME = int(os.getenv("EVENT_EXPIRE_TIME", 60 * 60 * 12))  # 12 hours
MAPPING = bool(os.getenv("MAPPING", False))

LANGUAGES = (
    "it",  # Italian
    "de",  # German
    "es",  # Spanish
    "fr"  # French
)

SPORTS = {
    1: {"name": "Soccer", "markets": [1, 18, 29, 166, 165, 136, 139], "extras": ['period_length', 'overtime_length']},
    2: {"name": "BasketBall", "markets": [219, 223, 225, 68],
        'extras': ['period_length', 'overtime_length', 'regular_number_of_periods']},
    4: {"name": "Ice Hockey", "markets": [1, 18], 'extras': ['period_length', 'overtime_length']},
    5: {"name": "Tennis", "markets": [186, 189, 187], 'extras': ['surface', 'best_of']},
    6: {"name": "Handball", "markets": [1, 18, 16], 'extras': ['period_length', 'overtime_length']},
    12: {"name": "Rugby", "markets": [1, 18, 16], 'extras': ['period_length', 'overtime_length']},
    43: {"name": "Alpine Skiing", "markets": [539]},
    23: {"name": "Volleyball", "markets": [186, 238, 237], 'extras': ['best_of', 'set_limit']},
    13: {"name": "Aussie Rules", "markets": [186, 18, 16], 'extras': ['period_length']},
    31: {"name": "Badminton", "markets": [186, 238, 237]},
    15: {"name": "Bandy", "markets": [1, 18]},
    3: {"name": "Baseball", "markets": [251, 258, 256], 'extras': ['period_length', 'number_of_regular_innings']},
    155: {"name": "Basketball 3x3", "markets": [219]},
    60: {"name": "Beach Soccer", "markets": [1, 18]},
    34: {"name": "Beach Volley", "markets": [186, 238, 237]},
    44: {"name": "Biathlon", "markets": [539]},
    32: {"name": "Bowls", "markets": [186, 314, 188]},
    10: {"name": "Boxing", "markets": [186, 18]},
    33: {"name": "Chess", "markets": [1]},
    21: {"name": "Cricket", "markets": [340, 1, 605]},
    46: {"name": "Cross-Country", "markets": [539]},
    28: {"name": "Curling", "markets": [186]},
    17: {"name": "Cycling", "markets": [539]},
    22: {"name": "Darts", "markets": [186, 314, 188], 'extras': ['best_of_legs']},
    24: {"name": "Field Hockey", "markets": [1, 18]},
    7: {"name": "Floorball", "markets": [1, 18], 'extras': ['period_length']},
    16: {"name": "American Football", "markets": [219, 225, 1, 223], 'extras': ['period_length', 'overtime_length']},
    40: {"name": "Formula 1", "markets": [539]},
    29: {"name": "Futsal", "markets": [1, 18]},
    135: {"name": "Gaelic Football", "markets": [1]},
    9: {"name": "Golf", "markets": [539]},
    129: {"name": "Indy Racing", "markets": [539]},
    117: {"name": "MMA", "markets": [186, 18]},
    190: {"name": "Motorcycle Racing", "markets": [539]},
    61: {"name": "Pesapallo", "markets": [1]},
    48: {"name": "Ski Jumping", "markets": [539]},
    37: {"name": "Squash", "markets": [186, 238, 237]},
    191: {"name": "Stock Car Racing", "markets": [539]},
    20: {"name": "Table Tennis", "markets": [186, 238, 237], 'extras': ['best_of']},
    188: {"name": "Touring Car Racing", "markets": [539]},
    26: {"name": "Waterpolo", "markets": [1, 18]},
    75: {"name": "Waterpolo", "markets": [539]},
    36: {"name": "Athletics", "markets": [539]},
    45: {"name": "Bobsleigh", "markets": [539]},
    180: {"name": "Cycling BMX Racing", "markets": [539]},
    96: {"name": "Diving", "markets": [539]},
    76: {"name": "Equestrian", "markets": [539]},
    102: {"name": "Figure Skating", "markets": [539]},
    103: {"name": "Freestly", "markets": [539]},
    138: {"name": "Kabaddi", "markets": [1, 18, 16]},
    51: {"name": "Luge", "markets": [539]},
    182: {"name": "Marathon Swimming", "markets": [539]},
    47: {"name": "Nordic Combined", "markets": [539]},
    64: {"name": "Rowing", "markets": [539]},
    81: {"name": "Sailing", "markets": [539]},
    105: {"name": "Short Track Speed Skating", "markets": [539]},
    183: {"name": "Skateboarding", "markets": [539]},
    104: {"name": "Skeleton", "markets": [539]},
    19: {"name": "Snooker", "markets": [186, 1, 494]},
    106: {"name": "Soccer Mythical", "markets": [1, 18, 16]},
    50: {"name": "Speed Skating", "markets": [539]},
    90: {"name": "Surfing", "markets": [539]},
    84: {"name": "Triathlon", "markets": [539]},
    158: {"name": "ESport Arena of Valor", "markets": [186]},
    118: {"name": "ESport Call of Duty", "markets": [186]},
    109: {"name": "ESport Counter-Strike", "markets": [186, 327, 328]},
    111: {"name": "ESport Dota", "markets": [186, 327, 328]},
    134: {"name": "ESport King of Glory", "markets": [186]},
    110: {"name": "ESport League of Legends", "markets": [186, 327, 328]},
    121: {"name": "ESport Overwatch", "markets": [186]},
    125: {"name": "ESport Rainbow Six", "markets": [186]},
    128: {"name": "ESport Rocket League", "markets": [186]},
    112: {"name": "ESport StarCraft", "markets": [186, 327, 328]}
}
EXTRA_MAPPING = {
    "period_length": "periodLength",
    "overtime_length": "otLength",
    'best_of': 'bof',
    'set_limit': 'setLimit',
    'number_of_regular_innings': 'nof',
    'best_of_legs': 'bof',
    'regular_number_of_periods': 'nperiods'
}

TOTAL_SPORTS = list(SPORTS.keys())

MARKETS = {
    1: {"name": "1X2", "outcomes": [1, 2, 3]},
    16: {"name": "HND", "outcomes": [1714, 1715]},
    18: {"name": "Totals", "outcomes": [12, 13]},
    29: {"name": "BTTS", "outcomes": [74, 76]},
    166: {"name": "Corner Totals", "outcomes": [12, 13]},
    165: {"name": "Corner HH", "outcomes": [1714, 1715]},
    136: {"name": "Cards 1X2", "outcomes": [1, 2, 3]},
    139: {"name": "Cards Totals", "outcomes": [12, 13]},
    219: {"name": "H/H", "outcomes": [4, 5]},
    223: {"name": "HND", "outcomes": [1714, 1715]},
    225: {"name": "O/U", "outcomes": [12, 13]},
    237: {"name": "Points HND", "outcomes": [1714, 1715]},
    238: {"name": "Points O/U", "outcomes": [12, 13]},
    68: {"name": "O/U 1HT", "outcomes": [12, 13]},
    186: {"name": "HH", "outcomes": [4, 5]},
    187: {"name": "Games HND", "outcomes": [1714, 1715]},
    189: {"name": "Games O/U", "outcomes": [12, 13]},
    539: {"name": "HH", "outcomes": []},
    251: {"name": "HH", "outcomes": [4, 5]},
    258: {"name": "Totals", "outcomes": [12, 13]},
    256: {"name": "HND", "outcomes": [1714, 1715]},
    314: {"name": "Sets O/U", "outcomes": [12, 13]},
    188: {"name": "Sets HND", "outcomes": [1714, 1715]},
    340: {"name": "HH", "outcomes": [4, 5]},
    605: {"name": "Innings Totals", "outcomes": [12, 13]},
    494: {"name": "Frames Totals", "outcomes": [12, 13]},
    327: {"name": "Map HND", "outcomes": [1714, 1715]},
    328: {"name": "Totals", "outcomes": [12, 13]}
}

OUTCOMES = {  # Mapping of OutCome ID - Outcome String
    1: "1", 2: "X", 3: "2", 4: "1", 5: "2",
    12: "Over", 13: "Under",
    74: "Yes", 76: "No",
    1714: "1", 1715: "2"
}
OUTCOME_STATUS = {
    0: True, "not_started": True, "delayed": True, "match_about_to_start": True,
    "live": False, "ended": False, "closed": False, "cancelled": False,
    "postponed": False, "suspended": False, "interrupted": False,
    1: False, 2: False, 3: False, 4: False,
}
MARKET_ACTIVE_STATUS = 1, -1, -2
MARKET_INACTIVE_STATUS = 0, -3, -4
MARKET_STATUS = {
    1: "active", -1: "suspended", 0: "disabled",
    -3: "settled", -4: "cancelled", -2: "suspended"
}
MATCH_STATUS_CODES = {1: "1P", 2: "2P", 3: "3P", 4: "4P", 5: "5P",
                      6: "HT", 7: "2HT",
                      8: "S1", 9: "S2", 10: "S3", 11: "S4", 12: "S5",
                      13: "1Q", 14: "2Q", 15: "3Q", 16: "4Q",
                      17: "GS", 40: "OT", 41: "1OT", 42: "2OT",
                      50: "Pen", 51: "Pen", 52: "Pen", 60: "P",
                      70: "C", 71: "G1", 72: "G2", 73: "G3", 74: "G4",
                      75: "G5", 76: "G6", 77: "G7", 80: "I", 81: "S", 90: "A",
                      91: "WO", 92: "R", 100: "FT", 110: "AOT", 111: "AOT", 120: "AP",
                      141: "M1", 142: "M2", 143: "M3", 144: "M4", 145: "M5", 146: "M6", 147: "M7",
                      151: "G1", 152: "G2", 153: "G3", 154: "G4", 155: "G5",
                      441: "S6", 442: "S7", 514: "S8", 515: "S9", 516: "S10", 517: "S11",
                      518: "S12", 519: "S13", 531: "I1", 532: "I2", 533: "I3", 534: "I4", 535: "I5",
                      536: "I6", 537: "I7", 538: "I8", 539: "I9"
                      }
EXTRA_RESULT_MAPPING = {
    1: ['score_change', 'corner_kick', 'yellow_card', 'red_card', 'yellow_red_card'],
    2: ['score_change'],
    4: ['score_change'],
    6: ['score_change', 'yellow_card', 'red_card', 'yellow_red_card'],
    12: ['score_change', 'yellow_card', 'red_card', 'yellow_red_card'],
    16: ['score_change'],
    3: ['score_change'],
    29: ['score_change', 'corner_kick', 'yellow_card', 'red_card', 'yellow_red_card'],

}

EXTRA_RESULT_MAPPING_SPORTS = list(EXTRA_RESULT_MAPPING.keys())

TYPE_MAPPING = {
    'score_change': "Goals",
    'corner_kick': 'Corners',
    'yellow_card': 'Bookings',
    'red_card': 'Bookings',
    'yellow_red_card': 'Bookings'
}

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)


class CustomLogger(logging.Logger):
    def process(self):
        pass


class BetradarUOFParser(BetradarParser):
    logger: logging.Logger

    def __init__(self):
        super().__init__(bookmaker_id=46, bookmaker_name='betradarUOF',
                         inverted_direction=INVERTED_DIRECTION,
                         percentage_limit=PERCENTAGE_LIMIT, sports={},
                         url=URL, sleep=SLEEP)

        self.betradar_connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=MESSAGING_HOST, port=BETRADAR_PORT,
                                      virtual_host=f"/{BETRADAR_EXCHANGE}/{BETRADAR_USERNAME}",
                                      credentials=pika.PlainCredentials(BETRADAR_TOKEN, ""),
                                      ssl_options=pika.SSLOptions(ssl.create_default_context(), MESSAGING_HOST))
        )

        self.betradar_channel = self.betradar_connection.channel()
        self.betradar_queue = self.betradar_channel.queue_declare(queue="")
        self.betradar_channel.queue_bind(
            exchange=BETRADAR_EXCHANGE,
            queue=self.betradar_queue.method.queue,
            routing_key="#.*.#"
        )
        self.betradar_channel.basic_consume(self.betradar_queue.method.queue, on_message_callback=self.on_message)

        response = get(f"{API_URL}/v1/descriptions/en/match_status.xml", headers={"x-access-token": BETRADAR_TOKEN})

        self.match_status = {
            int(match_status.attrib.get('id')): [int(sport.attrib.get('id').split(':')[-1])
                                                 for sport in match_status.find(".//sports").findall('.//sport')]
            for match_status in XML(response.content).findall(".//match_status")
        }

        self.root_logger = self.logger = logging.getLogger()
        # self.get_event_from_db("")

    def on_message(self, channel: BlockingChannel,
                   method_frame: Basic.Deliver,
                   header_frame: BasicProperties,
                   body: bytes):

        xml = XML(body)
        event_id: str = xml.get('event_id') or ''

        self.logger = logging.getLogger(str(uuid4()))

        self.logger.info(f"Processing {xml.tag} for event = {event_id} with message %s",
                         body)

        is_outright = not event_id.startswith('sr:match')
        try:
            if xml.tag == 'odds_change':
                if is_outright:
                    self.on_odd_change_outright(xml)
                else:
                    self.on_odd_change(xml)

            elif xml.tag == 'bet_settlement':
                if is_outright:
                    self.on_bet_settlement_outright(xml)
                else:
                    self.on_bet_settlement(event_id)

            elif xml.tag == 'bet_stop':
                self.on_event_change(event_id)

            elif xml.tag == 'cancelbet':
                pass

            elif xml.tag == 'rollback_bet_settlement':
                if is_outright:
                    self.on_bet_settlement_outright(xml)
                else:
                    self.on_bet_settlement(event_id)

            elif xml.tag == 'rollback_cancelbet':
                pass

            elif xml.tag == 'fixture_change':
                self.on_event_change(event_id)

            elif xml.tag == 'alive':
                # alive from betradar to send alive to our system
                self.heartbeat()
            else:
                logging.warning("unknown data received with tag :- " + xml.tag)

        except Exception as e:
            self.logger.exception(e)

        self.logger = self.root_logger

    def on_bet_settlement(self, event_id):

        event = self.get_event(event_id)

        response = get(f"{API_URL}/v1/sports/en/sport_events/{event_id}/timeline.xml", headers={
            "x-access-token": BETRADAR_TOKEN
        })

        bet_settle = XML(response.content)
        self.logger.info("Timeline.xml --> %s", tostring(bet_settle, pretty_print=True))

        # Result
        event.result = dict()
        sport_event_status = bet_settle.find(".//sport_event_status", namespaces=bet_settle.nsmap)

        total_results = []
        results = sport_event_status.find(".//results", namespaces=bet_settle.nsmap)
        if results is not None:
            total_results += results.findall(".//result", namespaces=bet_settle.nsmap)

        period_scores = sport_event_status.find(".//period_scores", namespaces=bet_settle.nsmap)
        if period_scores is not None:
            total_results += period_scores.findall(".//period_score", namespaces=bet_settle.nsmap)

        self.logger.info("Before Updating -->  results = %s  and extra_results = %s ",
                         dumps(event.result), dumps(event.extra_result))

        for result in total_results:

            match_status_code = int(result.attrib.get("match_status_code"))

            sports = self.match_status[match_status_code]

            if event.sport_id not in sports:
                continue

            if match_status_code not in MATCH_STATUS_CODES:
                logging.info(f"{match_status_code} is not found #matchStatusNotFound")
            else:
                match_status_code = MATCH_STATUS_CODES.get(match_status_code)

                if match_status_code in ('WO', 'R'):  # 91 & 92
                    event.result[match_status_code] = int(sport_event_status.attrib.get("winner_id").split(':')[-1])
                else:
                    event.result[
                        match_status_code] = f"{result.attrib.get('home_score')}:{result.attrib.get('away_score')}"

        sport_event_status_code = int(sport_event_status.attrib.get('match_status_code'))
        match_status_code = MATCH_STATUS_CODES.get(sport_event_status_code)

        if match_status_code not in event.result:
            if match_status_code in ('WO', 'R'):  # 91 & 92
                event.result[match_status_code] = int(sport_event_status.attrib.get("winner_id").split(':')[-1])
            else:
                event.result[match_status_code] = f"{sport_event_status.attrib.get('home_score')}:" \
                                                  f"{sport_event_status.attrib.get('away_score')}"
        # Extra Result

        if event.sport_id in EXTRA_RESULT_MAPPING_SPORTS:
            event.extra_result = {}
            event_types = EXTRA_RESULT_MAPPING[event.sport_id]

            timeline = bet_settle.find('.//timeline', namespaces=bet_settle.nsmap)
            if timeline is None:
                self.logger.info("Time line is valid")
                return
            events = timeline.findall('.//event', namespaces=bet_settle.nsmap)

            for e in events:
                attrib = e.attrib
                type = attrib['type']

                if type == 'period_start' and 'match_status_code' in attrib:
                    sport_event_status_code = int(attrib.get('match_status_code'))
                    match_status_code = MATCH_STATUS_CODES.get(sport_event_status_code)

                if attrib['type'] not in event_types:
                    continue

                result = {
                    'id': int(attrib.get('id')),
                    'team': attrib.get('team'),
                    'time': int(attrib.get('match_time') or 0),
                }

                if 'match_clock' in attrib:
                    result['clock'] = attrib['match_clock']
                if 'stoppage_time' in attrib:
                    result['stoppageTime'] = attrib['stoppage_time']

                if type == 'score_change':
                    result.update({
                        'score': f'{attrib["home_score"]}:{attrib["away_score"]}',

                    })

                    goal_scorer = e.find('.//goal_scorer', namespaces=bet_settle.nsmap)
                    if goal_scorer is not None:
                        result['scorerPlayerId'] = int(goal_scorer.attrib.get('id').split(':')[-1])
                        result['scorerPlayerName'] = goal_scorer.attrib.get('name')

                    assist = e.find('.//assist', namespaces=bet_settle.nsmap)
                    if assist is not None:
                        result['assistPlayerId'] = int(assist.attrib.get('id').split(':')[-1])
                        result['assistPlayerName'] = assist.attrib.get('name')

                elif type in ('corner_kick', 'yellow_card', 'red_card', 'yellow_red_card'):

                    if type != 'corner_kick':
                        *t, card = type.split('_')
                        result['type'] = '_'.join(t)

                    player = e.find('.//player', namespaces=bet_settle.nsmap)
                    if player is not None:
                        result['playerId'] = int(player.attrib['id'].split(':')[-1])
                        result['playerName'] = player.attrib['name']

                mapped_type = TYPE_MAPPING[type]

                if mapped_type == 'Goals':  # Special Case
                    if event.sport_id == 2:
                        mapped_type = "Points"
                    elif event.sport_id == 3:
                        mapped_type = 'Runs'

                if mapped_type not in event.extra_result:
                    event.extra_result[mapped_type] = {}
                if match_status_code not in event.extra_result[mapped_type]:
                    event.extra_result[mapped_type][match_status_code] = []

                event.extra_result[mapped_type][match_status_code].append(result)

        if len(event.result) or len(event.extra_result):
            self.logger.info("Updating\n result = %s \n extra_result = %s",
                             dumps(event.result), dumps(event.extra_result))
            self.store(event)

    def get_event_from_api(self, event_id: str, lang: str = 'en') -> Union[None, Event]:

        r = get(f"{API_URL}/v1/sports/{lang}/sport_events/{event_id}/fixture.xml",
                headers={
                    "x-access-token": BETRADAR_TOKEN
                })
        try:
            event: Element = XML(r.content)
        except XMLSyntaxError:
            logging.error(f"{event_id} is can't be parsed")
            return

        fixture = event[0]

        tournament = fixture.find(".//tournament", namespaces=fixture.nsmap)

        if tournament is None:
            return

        sport = tournament.find(".//sport", namespaces=fixture.nsmap)
        sport_id = int(sport.attrib['id'].split(':')[-1])

        if sport_id not in TOTAL_SPORTS:
            return

        season = fixture.find(".//season", namespaces=fixture.nsmap)

        competitors = fixture.find(".//competitors", namespaces=fixture.nsmap)

        if competitors is None or len(competitors) > 2:
            return

        home, away = self.get_competitors(competitors)

        tournament_round = fixture.find(".//tournament_round", namespaces=fixture.nsmap)
        sport = tournament.find(".//sport", namespaces=fixture.nsmap)

        category = tournament.find(".//category", namespaces=fixture.nsmap)
        extra_info = fixture.find('.//extra_info', namespaces=fixture.nsmap)

        reference_ids = next((child for child in fixture if child.tag.endswith("reference_ids")), None)

        if reference_ids is not None:
            aams = [ref.attrib['value'] for ref in reference_ids if ref.attrib['name'] == 'aams']
            aams = int(aams[0]) if aams else None
        else:
            aams = None

        *_, id = event_id.split(':')

        return Event(
            _id=int(id),
            bookmaker_id=self.id,
            bookmaker_name=self.name,
            date=int(datetime.fromisoformat(fixture.attrib['start_time']).timestamp()),

            sport_id=int(sport.attrib['id'].split(':')[-1]),
            sport_name=sport.attrib['name'],

            home_id=int(home.attrib['id'].split(":")[-1]),
            home_name=home.attrib['name'],
            home_info=dict(gender=home.attrib.get('gender'),
                           abbreviation=home.attrib.get('abbreviation'),
                           shortName=home.attrib.get('short_name'),
                           country=home.attrib.get('country'),
                           countryCode=home.attrib.get('country_code'),
                           betradarId=int(next((ref.attrib['value']
                                                for ref in home.find(".//reference_ids", namespaces=fixture.nsmap)
                                                if ref.attrib['name'] == 'betradar')))),

            away_id=int(away.attrib['id'].split(":")[-1]),
            away_name=away.attrib['name'],
            away_info=dict(gender=away.attrib.get('gender'),
                           abbreviation=away.attrib.get('abbreviation'),
                           shortName=away.attrib.get('short_name'),
                           country=away.attrib.get('country'),
                           countryCode=away.attrib.get('country_code'),
                           betradarId=int(next((ref.attrib['value']
                                                for ref in away.find(".//reference_ids", namespaces=fixture.nsmap)
                                                if ref.attrib['name'] == 'betradar'))),

                           ),

            tournament_id=int(tournament.attrib['id'].split(':')[-1]),
            tournament_name=tournament.attrib['name'],
            tournament_round=dict(id=int(tournament_round.attrib['betradar_id']),
                                  number=tournament_round.attrib.get('number'),
                                  type=tournament_round.attrib.get('type'),
                                  longName=tournament_round.attrib.get('group_long_name'),
                                  roundName=tournament_round.attrib.get('betradar_name'),
                                  phase=tournament_round.attrib.get('phase')
                                  ),

            season=dict(id=int(season.attrib["id"].split(':')[-1]),
                        name=season.attrib.get('name'),
                        startDate=int(datetime.strptime(season.attrib.get('start_date'), "%Y-%m-%d").timestamp()),
                        endDate=int(datetime.strptime(season.attrib.get('end_date'), "%Y-%m-%d").timestamp()),
                        year=int(season.attrib.get('year'))
                        if season.attrib.get('year').isdigit() else season.attrib.get('year'),
                        ) if season is not None and season.attrib else None,

            category_id=int(category.attrib['id'].split(':')[-1]),
            category_name=category.attrib['name'],

            betradar_id=int(id),
            status=OUTCOME_STATUS.get(fixture.attrib['status'], False),
            last_update=int(datetime.now().timestamp()),
            aams=aams,
            extra={EXTRA_MAPPING.get(info.attrib['key'], info.attrib['key']): self.process_value(info.attrib['value'])
                   for info in extra_info if info.attrib['key'] in SPORTS[sport_id]['extras']
                   } if extra_info is not None and 'extras' in SPORTS[sport_id] else {}
        )

    def on_odd_change(self, odd_change) -> None:

        event_id: str = odd_change.get('event_id')

        event: Event = self.get_event(event_id)

        if event.sport_id not in TOTAL_SPORTS:
            return

        # Updates fixture Status
        sport_event_status = odd_change.find(".//sport_event_status", namespaces=odd_change.nsmap)
        status = int(sport_event_status.attrib.get('status'))
        event.status = OUTCOME_STATUS.get(status, True)

        markets = SPORTS[event.sport_id]['markets']

        variations = Variations(event)

        updates = event.back or {}

        old_updates = deepcopy(updates)
        self.logger.info("Odds Before Updating = %s", dumps(old_updates))

        odds = odd_change.find(".//odds", namespaces=odd_change.nsmap)

        for market in odds:

            market_id = int(market.get('id'))

            if market_id not in markets:
                continue

            market_data: dict = MARKETS[market_id]
            market_name = market_data['name']
            outcomes = market_data['outcomes']

            specifiers = market.get("specifiers", "#")
            specifier, *specifiers = specifiers.split("|")
            *_, specifier = specifier.split("=")
            market_status = int(market.get('status'))

            # Special cases
            if event.sport_id == 1 and market_id == 18 and specifier == "2.5":
                market_name = "O/U"

            if market_name not in updates:
                updates[market_name] = {}

            if specifier not in updates[market_name]:
                updates[market_name][specifier] = {}

            updates[market_name][specifier].update({"status": MARKET_STATUS.get(market_status)})

            if market_status in MARKET_INACTIVE_STATUS:
                updates[market_name][specifier].update({"lastUpdate": int(time.time())})

            for outcome in market:
                outcome_id = int(outcome.attrib.get('id'))

                if outcome_id not in outcomes:
                    continue

                if market_id == 539:  # Special Case
                    competitor_id = int(outcome.attrib.get('id').split(":")[-1])
                    outcome_name = "1" if event.home_id == competitor_id else "2"
                else:
                    outcome_name = OUTCOMES[outcome_id]

                active = outcome.attrib.get("active") == '1'

                if market_status in MARKET_INACTIVE_STATUS:
                    active = False

                odd_value = float(outcome.attrib.get('odds'))

                if outcome_name in updates[market_name][specifier]:
                    prev_value = updates[market_name][specifier][outcome_name]['odd']

                    if odd_value != prev_value:
                        key = f'back.{market_name}.{specifier}.{outcome_name}'
                        if not self.percentage_checker(odd=odd_value, prev_odd=prev_value, key=key):
                            continue
                    else:
                        continue

                updates[market_name][specifier][outcome_name] = {"odd": odd_value,
                                                                 "lastUpdate": int(time.time()),
                                                                 "status": "active" if active else "disabled"}

                variations.append(
                    Variation(
                        _id=event.id,
                        bookmaker_name=self.name,
                        sport_id=event.sport_id,
                        market_name=market_name,
                        sbv=specifier,
                        outcome_name=outcome_name,
                        odd=odd_value,
                        last_update=event.last_update,
                        status=event.status
                    )
                )

        if variations.exists() or old_updates != updates:
            event.back = updates
            self.logger.info("Updated Odds = %s", dumps(updates))
            self.logger.info("Variations = %s", variations.serialize())
            variations.calculate_main_lines(updates)
            self.store_variations(variations=variations)
            self.store(event)

    def on_odd_change_outright(self, xml, lang: str = 'en'):

        event_id = xml.get('event_id')

        self.logger.info(f"processing odd change for event {event_id}")

        for market, event in zip(xml.xpath('//market'), self.get_outrights(xml)):

            variations = Variations(event)

            specifiers = market.get("specifiers")
            specifiers, *_ = specifiers.split('|')
            outright_id = specifiers
            market_name = market.get('name')
            market_id = str(self.extract_id(market.get('id')))
            sbv = str(self.extract_id(market.get('specifiers')))

            for outcome in market.findall(".//outcome", namespaces=market.nsmap):
                outcome_id = outcome.attrib.get('id').split(':')[-1]
                odd_value = float(outcome.attrib.get('odds') or 0)

                if outcome_id not in event.back[market_id]:
                    event.back[market_id][outcome_id] = {}

                if "odd" in event.back[market_id][outcome_id]:
                    prev_value = event.back[market_id][outcome_id]['odd']

                    if prev_value != odd_value:
                        key = f'back.{market_name}.{sbv}{outcome_id}'
                        if not self.percentage_checker(odd=odd_value, prev_odd=prev_value, key=key):
                            continue
                    else:
                        continue

                event.back[market_id][outcome_id].update(
                    {
                        "odd": odd_value,
                        "lastUpdate": int(time.time()),
                        "status": 'active' if outcome.attrib.get("active") == '1' else 'disabled'

                    }
                )
                variations.append(
                    Variation(
                        _id=event.id,
                        bookmaker_name=self.name,
                        sport_id=event.sport_id,
                        market_name=market_name,
                        sbv=sbv,
                        outcome_name=outcome_id,
                        odd=odd_value,
                        last_update=int(time.time())
                    )
                )

            if variations.exists():
                self.logger.info("variations => " + variations.serialize())
                # variations.calculate_main_lines(event)
                # self.store_variations(variations=variations)
                # variations.calculate_main_lines(event)
                # self.store_variations(variations)
                self.store(event)

    def get_outright(self, fixture, market, lang='en') -> Union[OutRight, None]:

        metadata = market.find('.//market_metadata')

        event = {
            '_id': self.extract_id(market.get("specifiers")),
            'aams': None,
            'outright_name': "",
            'back': {},
            'betradar_id': self.extract_id(market.get('specifiers')),
            'bookmaker_id': self.id,
            'bookmaker_name': self.name,
            'category_id': 0,
            'category_name': " ",
            'status': 'active',
            'start_date': None,
            'date': 0,
            'end_date': None,
            'expiry_date': None,
            'last_update': int(time.time()),
            'season': {},
            'sport_id': 0,
            'sport_name': "",
            'tournament_id': 0,
            'tournament_name': " ",
            'tournament_round': {}
        }
        if metadata is not None:
            event.update({
                'start_date': self.process_date(metadata.get('start_time')),
                'date': self.process_date(metadata.get('start_time')),
                'end_date': self.process_date(metadata.get('end_time', 0)),
                'expiry_date': self.process_date(metadata.get('next_betstop')),
                'aams': metadata.get('aams_id')
            })
        sport = fixture.find('.//sport', namespaces=fixture.nsmap)

        if sport is not None:
            event.update({
                'sport_id': self.extract_id(sport.get('id')),
                'sport_name': sport.get('name')
            })

        category = fixture.find('.//category', namespaces=fixture.nsmap)
        if category is not None:
            event.update(
                {
                    "category_id": self.extract_id(category.get('id')),
                    "category_name": category.get('name')
                }
            )

        tournament = fixture.find('.//tournament', namespaces=fixture.nsmap)

        if tournament is not None:
            event.update({
                'tournament_id': self.extract_id(tournament.get('id')),
                'tournament_name': tournament.get('name')
            })

            if 'scheduled' in tournament.attrib and event['date'] is None:
                event['date'] = tournament.get('scheduled')

        season = fixture.find('.//season', namespaces=fixture.nsmap)
        if season is not None:
            event.update({
                "season": dict(id=int(season.attrib["id"].split(':')[-1]),
                               name=season.attrib.get('name'),
                               startDate=int(
                                   datetime.strptime(season.attrib.get('start_date'), "%Y-%m-%d").timestamp()),
                               endDate=int(datetime.strptime(season.attrib.get('end_date'), "%Y-%m-%d").timestamp()),
                               year=int(season.attrib.get('year'))
                               if season.attrib.get('year').isdigit() else season.attrib.get('year')
                               )
            })

        tournament_round = fixture.find(".//tournament_round", namespaces=fixture.nsmap)
        if tournament_round is not None:
            event.update({
                "tournament_round": dict(id=int(tournament_round.attrib['betradar_id']),
                                         number=tournament_round.attrib.get('number'),
                                         type=tournament_round.attrib.get('type'),
                                         longName=tournament_round.attrib.get('group_long_name'),
                                         roundName=tournament_round.attrib.get('betradar_name'),
                                         phase=tournament_round.attrib.get('phase')
                                         )
            })

        market_id = market.get('id')
        specifier, *_ = market.get('specifiers').split("|")
        *_, specifier = specifier.split("=")
        sbv = specifier.split(':')[-1]

        r = get(f"{API_URL}/v1/descriptions/{lang}/markets/{market_id}/variants/{specifier}",
                headers={
                    "x-access-token": BETRADAR_TOKEN
                })
        self.logger.info(f"market info => {r.content}")
        back = {}
        market_data: Element = XML(r.content)

        if market_id not in back:
            back[market_id] = {}

        back[market_id] = {
            outcome.attrib.get("id").split(":")[-1]: {
                "name": outcome.attrib.get('name')
            } for outcome in market_data.xpath("//market_descriptions/market/outcomes/outcome",
                                               namespaces=market_data.nsmap)
        }

        event['back'] = back

        market = market_data.find('.//market', namespaces=market_data.nsmap)
        if market is not None and 'name' in market.attrib:
            event['outright_name'] = market.get('name')

        return OutRight(**event)

    def on_bet_settlement_outright(self, xml: Any):

        for market, event in zip(xml.xpath('//market'), self.get_outrights(xml)):
            event.result = {}
            specifiers = market.get("specifiers")
            specifiers, *_ = specifiers.split('|')
            market_id = str(self.extract_id(market.get('id')))

            if market_id not in event.result:
                event.result[market_id] = {}

            event.result[market_id] = {
                str(self.extract_id(outcome.get('id'))): {
                    'name': event.back[market_id][str(self.extract_id(outcome.get('id')))]['name'],
                    'result': int(outcome.get('result')),
                    'lastUpdate': int(time.time())

                } for outcome in market.findall(".//outcome", namespaces=market.nsmap)
            }

            if event.result and len(event.result):
                self.store(event)

    def get_outrights(self, xml: Any, lang='en'):
        event_id = xml.get('event_id')
        fixture = None
        for market in xml.xpath('//market'):
            specifiers = market.get("specifiers")
            specifiers, *_ = specifiers.split('|')
            outright_id = specifiers

            event = self.load_event(outright_id)

            if not event:
                self.logger.info(f"Event not found in cache with id {outright_id}")
                if fixture is None:
                    r = get(f"{API_URL}/v1/sports/{lang}/sport_events/{event_id}/fixture.xml", headers={
                        "x-access-token": BETRADAR_TOKEN
                    })

                    fixture = XML(r.content)
                    self.logger.info(f"Fixture.xml --> {r.content}")

                event = self.get_outright(fixture, market)

                if not event:
                    self.logger.info("Unable to get Outright from Api")
                    continue

                self.store_translations_outrights(event)
                event.set_is_new(True)
                self.logger.info("Event from api " + dumps(event.serialize()))

            else:
                event.set_is_new(False)
                self.logger.info("Event before update " + dumps(event.serialize()))

            yield event

    def on_event_change(self, event_id: str):

        event = self.get_event_from_api(event_id)

        if not event:
            return

        self.logger.debug("Event from API %s", dumps(event.serialize()))

        current_event = self.get_event(event.key) or self.get_event_from_db(str(event.id))

        if not current_event:
            self.logger.warning("Event not found in cache")
            event.set_is_new(True)
            self.store_translations(event)
        else:
            self.logger.debug("Event from Cache %s", dumps(current_event.serialize()))

            event.set_is_new(False), current_event.set_is_new(False)

            old_odds, current_event.back = current_event.back, None
            event.result, event.extra_result = current_event.result, current_event.extra_result
            last_update, event.last_update = event.last_update, current_event.last_update

            if event.__dict__ == current_event.__dict__:
                self.logger.warning("Event up-to date with cached event --> skipping Event Update ")
                return
            else:
                current_event.back = event.back = old_odds
                event.last_update = last_update

            self.logger.debug("Performing Event update from \n %s \nTo\n %s",
                              dumps(current_event.serialize()), dumps(event.serialize()))

            self.send_fixture_variations(event, current_event)

        self.store(event)

        return event

    def store_translations(self, event: Event) -> None:

        if not event:
            return

        events: Dict[str, Event] = {}

        for lang in LANGUAGES:
            event_ = self.get_event_from_api(f"sr:match:{event.id}", lang)
            if event_:
                events[lang] = event_

        sports = {"bookmaker": self.name, "id": event.sport_id, "type": "sport", "data": {"en": [event.sport_name]}}
        away = {"bookmaker": self.name, "id": event.away_id, "type": "competitor", "data": {"en": [event.away_name]}}
        home = {"bookmaker": self.name, "id": event.home_id, "type": "competitor", "data": {"en": [event.home_name]}}
        category = {"bookmaker": self.name, "id": event.category_id, "type": "category",
                    "data": {"en": [event.category_name]}}
        season = {"bookmaker": self.name, "id": event.season['id'], "type": "season",
                  "data": {"en": [event.season['name']]}} if event.season else {}
        tournament = {"bookmaker": self.name, "id": event.tournament_id, "type": "tournament",
                      "data": {"en": [event.tournament_name]}}
        tournament_round = {"bookmaker": self.name, "id": event.tournament_round['id'], "type": "tournament_round",
                            "data": {"en": [event.tournament_name]}}

        for language, event in events.items():
            sports['data'].update(
                {
                    language: [event.sport_name]
                }
            )
            away['data'].update({language: [event.away_name]})
            home['data'].update({language: [event.home_name]})
            category['data'].update({language: [event.category_name]})
            if event.season:
                season['data'].update({language: [event.season['name']]})
            tournament['data'].update({language: [event.tournament_name]})
            tournament_round['data'].update({language: [event.tournament_round['longName']]})

        operations = [
            UpdateOne(
                filter={
                    "id": item['id'],
                    "type": item['type']
                },
                update={
                    "$set": {
                        f"data.{language}.0": value
                        for language, value in item['data'].items()
                        if language and value
                    }
                },
                upsert=True

            ) for item in (sports, away, home, category, season,
                           tournament, tournament_round) if item != {} and len(item['data']) > 1
        ]

        if operations:
            client.get_database(self.name).get_collection("translations").bulk_write(operations)

    def store_translations_outrights(self, event: OutRight) -> None:

        outcomes = {outcome_id: {"bookmaker": self.name,
                                 "id": outcome_id,
                                 "type": "outcome",
                                 "data": {"en": [outcome.get('name')]}}
                    for market_id, market in event.back.items() for outcome_id, outcome in market.items()
                    }

        outright = {
            "bookmaker": self.name,
            "id": event.id,
            "type": "outright",
            "data": {
                "en": [event.outright_name]
            }
        }
        market_id = list(event.back.keys())[0]

        for lang in LANGUAGES:
            r = get(f"{API_URL}/v1/descriptions/{lang}/markets/{market_id}/variants/pre:markettext:{event.id}",
                    headers={
                        "x-access-token": BETRADAR_TOKEN
                    })
            market_data = XML(r.content)
            for outcome in market_data.xpath("//market_descriptions/market/outcomes/outcome",
                                             namespaces=market_data.nsmap):
                outcome_id = outcome.attrib.get("id").split(":")[-1]
                outcomes.get(outcome_id)['data'].update(
                    {
                        lang: [outcome.get('name')]
                    }
                )

            market = market_data.find('.//market', namespaces=market_data.nsmap)
            if 'name' in market.attrib:
                outright['data'].update({
                    lang: [market.get('name')]
                }),

        operations = [
            UpdateOne(
                filter={
                    "id": item['id'],
                    "type": item['type']
                },
                update={
                    "$set": {
                        f"data.{language}.0": value
                        for language, value in item['data'].items()
                        if language and value
                    }
                },
                upsert=True

            ) for item in [v for k, v in outcomes.items()] + [outright] if item != {} and len(item['data']) > 1
        ]

        if operations:
            self.logger.info("storing translation of outcomes & outrights" + dumps(outright) + dumps(outcomes))
            client.get_database(self.name).get_collection("translations").bulk_write(operations)

    @staticmethod
    def get_competitors(comps: list) -> Tuple[Element, Element]:
        """
        This function gets competitors from the tag and rotates them if needed.

        :param comps: List of elements.
        :return: Returns home and away in the right order.
        """

        home, away = comps
        if home.attrib['qualifier'] == 'away':
            logging.info('rotating competitors')
            away, home = comps

        return home, away

    def get_event(self, event_id: str, last_update: datetime = None) -> Union[None, Event]:

        id = self.extract_id(event_id)
        event: Event = self.load_event(f"{self.name}:{id}") or self.get_event_from_db(str(id))

        if not event:
            event = self.get_event_from_api(event_id)
            self.logger.debug("Event from API %s", dumps(event.serialize()))
            if not event:
                return
            event.set_is_new(True)
        else:
            self.logger.debug("Event from Cache %s", dumps(event.serialize()))
            event.set_is_new(False)

        return event

    def get_event_from_db(self, event_id: str):

        event = client.get_database(self.name).get_collection("passiveEvents").find_one({"_id": event_id})
        if event:
            event = Event.from_dict(**{
                "".join(["_" + char.lower() if char.isupper() else char for char in key]): value
                for key, value in event.items()
                # camelCase to snake_case
            })

        return event

    def load_event(self, event_id: str) -> Event:
        """
        
        """
        id = int(event_id.split(":")[-1])
        event = self.cache.get(f'{self.name}:{id}')

        if event:
            if 'outright_name' in event:
                return OutRight.from_dict(**event)

            return Event.from_dict(**event)

    def store_event(self, event: Event):
        """
        Putting the data to Redis, and setting the expiration date, so events will be automatically deleted from
        Redis 12 hours after they start.

        :param event: Value that we store.
        """

        exp = int(event.date - datetime.utcnow().timestamp())
        exp = exp + EVENT_EXPIRE_TIME if exp > 0 else 300
        # keep this 12h because results can arrive later, and we need last odds

        self.cache.set(event.key, event.__dict__, exp)

    def store(self, event: Event):
        self.logger.info("Storing Event = %s", dumps(event.serialize()))

        if isinstance(event, OutRight):
            self.store_event(event)

            event = event.serialize()

            if 'isNew' in event and event['isNew']:
                event['_insertOn'] = datetime.utcnow()

            event['_modifyOn'] = datetime.utcnow()
            event['endDate'] = datetime.fromtimestamp(float(event['endDate'] or 0))
            event['expiryDate'] = datetime.fromtimestamp(float(event['expiryDate'] or 0))
            event['startDate'] = datetime.fromtimestamp(float(event['startDate'] or 0))

            client.get_database(self.name).get_collection(OUTRIGHT_COLLECTION) \
                .update_one({'_id': event['_id']}, {'$set': event}, upsert=True)

        elif isinstance(event, Event):

            if not MAPPING:
                event.is_new = False

            return super().store(event)
        else:
            pass

    @staticmethod
    def process_value(value: str) -> Any:
        """

        :param value:
        :return:
        """
        if value.isdigit():
            return int(value)
        elif value == 'true':
            return True
        elif value == 'false':
            return False
        return value

    @staticmethod
    def process_date(value: Any) -> int:

        if not isinstance(value, int):
            value = int(value)
        after_100_years = time.time() + HUNDRED_YEARS

        if value > after_100_years:  # timestamp in milliseconds
            value //= THOUSAND_SECONDS

        return value

    @staticmethod
    def extract_id(id: str) -> int:
        id, *_ = id.split("|")
        return int(id.split(":")[-1])

    def handle(self):
        logging.info("Started consuming Odds & fixture changes")
        while True:
            try:
                self.betradar_channel.start_consuming()
            except Exception as e:
                logging.error("Recovering from error")
                logging.exception(e)
                self.__init__()
                sleep(2)
