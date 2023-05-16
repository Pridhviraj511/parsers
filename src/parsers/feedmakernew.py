import logging
import os
import time
from datetime import datetime
from io import BytesIO
from traceback import print_exception
from typing import Union, Tuple

from lxml.etree import XML
from pymongo import UpdateOne
from pytz import timezone

from models.betradar import Betradar
from models.event import FeedMakerEvent as Event
from models.variation import Variations, Variation
from parsers._betradar import BetradarParser
from parsers._parser import client

INVERTED_DIRECTION = int(os.getenv('INVERTED_DIRECTION', 0))
PERCENTAGE_LIMIT = float(os.getenv('PERCENTAGE_LIMIT', 0))

URL = os.getenv('URL', 'http://62.138.8.207:90/testfeed/')
PARTENER_ID = os.getenv('PARTNER_ID', '17')
SLEEP = int(os.getenv('SLEEP', 10))

MIN_TIME = int(os.getenv('min_time', 200))
ALERT_TIME = int(os.getenv('alert_time', 3600))
QSIZE = int(os.getenv('q_size', 15))

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
logging.basicConfig(level=logging.INFO)
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
MATCH_STATUS_CODES = {'Set1': 'S1', 'Set2': 'S2', 'Set3': 'S3',
                      'Set4': 'S4', 'Set5': 'S5', 'Set6': 'S6',
                      'Set7': 'S7', 'Set8': 'S8', 'Set9': 'S9',
                      'Set10': 'S10', 'Set11': 'S11', 'Set12': 'S12',
                      'Set13': 'S13', 'Map1': 'M1', 'Map2': 'M2',
                      'Map3': 'M3', 'Map4': 'M4', 'Map5': 'M5',
                      'Map6': 'M6', 'Map7': 'M7', 'OT': 'AOT'}
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


class FeedmakerParserNew(BetradarParser):

    def __init__(self):
        """ This is the Container class that extends the Bookmaker class and gives us some additional info we need. """

        super().__init__(
            bookmaker_id=49,
            bookmaker_name='feedmakernew',
            inverted_direction=INVERTED_DIRECTION,
            percentage_limit=PERCENTAGE_LIMIT,
            url=URL,
            sleep=SLEEP,
            sports={1: 1, 2: 2, 3: 5, 4: 6, 5: 12, 6: 23}
        )
        self.last_update = 0

        # data = b''
        # event = XML(data)
        # event = self.get_event(event)
        # print(event.__dict__)

    def get_event(self, event: any, last_update: datetime) -> Union[None, Event]:
        """
        This function parses the required data and creates a unique format for storage in MongoDB.
        We also use Redis to get previous odds, so that we can keep only the new ones, and also keep the historical
        odds without duplicates. If necessary - we can set the percentage below we will not accept the changes,
        as there will be a lot of calculations for the weighted average system unnecessarily.

        :param event: This is the event we parse.
        :param last_update: Date and time (UTC) when this event received last time.
        """
        try:

            event_id = int(event.attrib.get('BetradarMatchID', event.attrib.get('MatchID')))

            if event_id in (34152061, 34152045):
                print(event_id)
            else:
                return

            tournament = event.getparent()
            category = tournament.getparent()
            sport = category.getparent()

            sport_id = int(sport.attrib.get('BetradarSportID', sport.attrib.get('SportID')))
            comps = event.findall('Fixture/Competitors/Texts/Text')

            if sport_id not in TOTAL_SPORTS:
                return None
            if len(comps) != 2:
                return None

            home, away = Betradar.get_competitors(comps)
            home_name, home_translations = Betradar.get_translations(home, True)
            away_name, away_translations = Betradar.get_translations(away, True)
            sport_name, sport_translations = Betradar.get_translations(sport, False)

            category_id = int(category.attrib.get('BetradarCategoryID', category.attrib.get('CategoryID')))
            category_name, category_translations = Betradar.get_translations(category, False)

            tournament_id = int(tournament.attrib.get('BetradarTournamentID', tournament.attrib.get('TournamentID')))
            tournament_name, tournament_translations = Betradar.get_translations(tournament, False)

            time_zone = timezone(sport.getparent().getparent().find('Timestamp').attrib['TimeZone'])
            start_date = Betradar.get_date(date=event.find('Fixture/DateInfo/MatchDate').text, timezone=time_zone)

            # Goals
            goals = {}
            for goal in event.findall('Goals/Goal'):
                time_ = goal.attrib.get('Time')
                type = self.get_extra_type(time_)

                if type not in goals:
                    goals[type] = []
                goals[type].append(
                    {
                        'id': goal.attrib.get('Id'),
                        'score': f"{goal.attrib.get('Team1')}:{goal.attrib.get('Team2')}",
                        'time': time_,
                        'clock': goal.attrib.get('Clock'),
                        'scorerPlayerId': goal.find('./Player').attrib.get('Id'),
                        'scorerPlayerName': goal.find('./Player').attrib.get('Name'),
                        'assistPlayerID': None,
                        'assistPlayerName': None
                    }
                )
            corners = {}
            for corner_count in event.findall('Corners/CornerCount'):
                time_ = corner_count.attrib.get('Time')
                type = self.get_extra_type(time_)

                if type not in corners:
                    corners[type] = []

                corners[type].append(
                    {
                        'type': corner_count.attrib.get('Type'),
                        'cornerID': corner_count.attrib.get('CornerID'),
                        'team': corner_count.attrib.get('Team'),
                        'time': time_,
                        'clock': corner_count.attrib.get('Time'),
                        'playerID': corner_count.attrib.get('PlayerId'),
                        'playerName': corner_count.attrib.get('PlayerName')
                    }
                )

            cards = {}
            for card in event.findall('Cards/Card'):
                time_ = card.attrib.get('Time')
                type = self.get_extra_type(time_)

                if type not in cards:
                    cards[type] = []

                cards[type].append(
                    {
                        'type': card.attrib.get('Type'),
                        'cardId': card.attrib.get('Id'),
                        'teamId': card.find('./Player').attrib.get('TeamId'),
                        'homeScore': card.attrib.get('HomeScore'),
                        'awayScore': card.attrib.get('AwayScore'),
                        'time': card.attrib.get('Time'),
                        'clock': card.attrib.get('Clock'),
                        'playerId': card.find('./Player').attrib.get('Id'),
                        'playerName': card.find('./Player').attrib.get('Name'),

                    }
                )

            event = Event(
                _id=event_id,
                bookmaker_id=self.id,
                bookmaker_name=self.name,
                date=int(start_date.timestamp()),

                home_id=int(home.attrib['ID'] if self.name.lower() != 'testv500' else home.attrib['SUPERID']),
                home_info={},
                home_name=home_name,

                away_id=int(away.attrib['ID'] if self.name.lower() != 'testv500' else away.attrib['SUPERID']),
                away_name=away_name,
                away_info={},

                sport_id=sport_id,
                sport_name=sport_name,

                tournament_id=tournament_id,
                tournament_name=tournament_name,
                tournament_round=dict(id=int(tournament.attrib['uof_id'])),

                season={},
                extra={},
                extra_result={"goals": goals, 'corners': corners, 'cards': cards},
                result={
                    MATCH_STATUS_CODES.get(item.attrib.get('Type'), item.attrib.get('Type')): item.text
                    for item in event.findall('Result/ScoreInfo/Score')
                },
                category_id=category_id,
                category_name=category_name,
                betradar_id=event_id,
                status=event.find('Fixture/StatusInfo/Off').text == '0',
                last_update=int(last_update.timestamp()),
            )

            event.translations = {
                key: {
                    'id': id,
                    'type': type,
                    'data': {
                        lang: {"0": [value]}
                        for lang, value in translations.items()
                        if lang != "BET"
                    }
                }

                for key, type, id, translations in (('home', 'competitor', event.home_id, home_translations),
                                                    ('away', 'competitor', event.away_id, away_translations),
                                                    ('sport', 'sport', event.sport_id, sport_translations),
                                                    ('category', 'category', event.category_id, category_translations),
                                                    ('tournament', 'tournament', event.tournament_id,
                                                     tournament_translations))
            }

            return event
        except Exception as e:
            print_exception(e)
            raise e

    def _get_xml(self) -> BytesIO:
        """
        Get an XML data from API response. If no new data, it prints "/", otherwise, it prints timestamp from the file.

        :return: Returns XML data.
        """

        o = BytesIO()
        url = URL + PARTENER_ID + '/' + str(self.last_update)
        logging.info(f"URL:- {url}")
        try:
            ddd = datetime.utcnow()
            # r = bytes("""""", encoding='utf-8')
            # with open('feed.xml', 'rb') as file:
            #     r = file.read()
            r = get(url).content  # Metodo per leggere il feed
            # with open("feed.xml", 'wb') as file:
            #     file.write(r)
            o.write(r)
            self.type = self.get_type(r)  # check teams messages

            logging.info(f'---> time {datetime.utcnow() - ddd} for _get_xml')

            if r:
                self.last_update = int(XML(r).attrib.get("timestamp"))
                logging.info(self.last_update)
                # logging.info(r)
        except Exception as e:
            logging.exception(e)

        o.seek(0)
        return o

    def get_market(self, event: Event, markets: dict, current_event: Event) -> Tuple[dict, int]:

        if markets is None:
            return {}

        if current_event is None or current_event.back is None or not len(current_event.back):
            current_odds = {}  # empty dict is fine here
        else:
            current_odds = current_event.back
        if event.sport_id in (12, 4, 23):
            pass
        interested_markets = SPORTS[event.sport_id]['markets']
        variations = Variations(event)

        try:
            for market in markets.findall('Bet'):

                market_id = int(market.attrib.get('OddsType', 0))

                if market_id not in interested_markets:
                    continue

                market_data: dict = MARKETS[market_id]
                market_name = market_data['name']

                if market_name not in current_odds:
                    current_odds[market_name] = {"status": "active"}

                outcomes = market_data['outcomes']

                for outcome in market.findall('Odds'):

                    outcome_id = int(outcome.attrib['OutCome'])

                    if outcome_id not in outcomes:
                        if outcome_id == -1 and outcome.text == 'OFF':
                            current_odds[market_name].update({
                                "status": "disabled",
                                "lastUpdate": int(time.time())
                            })
                        continue

                    sbv = outcome.attrib.get('SpecialBetValue', '#')

                    if event.sport_id == 1 and market_id == 18 and sbv == "2.5":
                        market_name = "O/U"
                        if market_name not in current_odds:
                            current_odds[market_name] = {"status": "active"}

                    if current_odds[market_name]['status'] != 'active':
                        current_odds[market_name]['status'] = 'active'

                    if sbv not in current_odds[market_name]:
                        current_odds[market_name][sbv] = {}

                    if market_id == 539:  # Special Case
                        competitor_id = int(outcome.attrib.get('id').split(":")[-1])
                        outcome_name = "1" if event.home_id == competitor_id else "2"
                    else:
                        outcome_name = OUTCOMES[outcome_id]

                    active = outcome.attrib.get("active") or '1' == '1'

                    odd_value = float(outcome.text)

                    if outcome_name in current_odds[market_name][sbv]:
                        prev_value = current_odds[market_name][sbv][outcome_name]['odd']

                        if odd_value != prev_value:
                            key = f'back.{market_name}.{sbv}.{outcome_name}'
                            if not self.percentage_checker(odd=odd_value, prev_odd=prev_value, key=key):
                                continue
                        else:
                            continue

                    current_odds[market_name][sbv][outcome_name] = {"odd": odd_value,
                                                                    "lastUpdate": int(time.time()),
                                                                    "status": "active" if active else "disabled"}

                    variations.append(
                        Variation(
                            _id=event.id,
                            bookmaker_name=self.name,
                            sport_id=event.sport_id,
                            market_name=market_name,
                            sbv=sbv,
                            outcome_name=outcome_name,
                            odd=odd_value,
                            last_update=event.last_update,
                            back=True
                        )
                    )
        except Exception as e:
            logging.exception(e)
        if variations.exists():
            logging.info(variations.serialize())
            variations.calculate_main_lines(current_odds)
            self.store_variations(variations=variations)

        return {'back': current_odds}, variations.exists()

    def store(self, event: Event):
        # logging.info("storing event " + dumps(event.serialize()))

        if hasattr(event, 'translations') and event.translations:
            if event.is_new:
                self.store_translations(event.translations)

            del event.translations

        return super().store(event)

    def send_fixture_variations(self, event: Event, origin: Event):
        self.store_translations(event.translations)
        return super().send_fixture_variations(event, origin)

    def store_translations(self, translations: dict) -> None:

        operations = [
            UpdateOne(
                filter={
                    "id": item['id'],
                    "type": item['type']
                },
                update={
                    "$set": {
                        f"data.{language}": value
                        for language, value in item['data'].items()
                        if language and value
                    }
                },
                upsert=True

            ) for key, item in translations.items()
        ]

        if operations:
            client.get_database(self.name).get_collection("translations").bulk_write(operations)

    @staticmethod
    def get_extra_type(time: str) -> str:
        try:
            t, *_ = time.split(":")
            t = int(t)

            if 0 < t <= 45:
                type = 'HT'
            elif 46 <= t <= 90:
                type = '2HT'
            elif 91 <= t <= 105:
                type = '1OT'
            elif 106 <= t <= 120:
                type = '2OT'
            else:
                type = ""

            return type
        except:
            return time
