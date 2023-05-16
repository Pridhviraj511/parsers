import logging
import os
import time
from datetime import datetime
from json import dumps, loads
from traceback import print_exception
from typing import List, Any, Union

from requests import get
from websocket import WebSocketApp

from models.event import Event, InvalidEvent
from models.variation import Variations, Variation
from parsers._parser import Parser

URL = os.getenv('URL', "wss://api-pr.oddsmarket.org/v4/odds_ws")
API_KEY = os.getenv("API_KEY", "")

BOOKMAKER_ID = os.getenv("BOOKMAKER_ID")

INVERTED_DIRECTION = int(os.getenv('INVERTED_DIRECTION', 1))
PERCENTAGE_LIMIT = float(os.getenv('PERCENTAGE_LIMIT', 0))

SLEEP = int(os.getenv('SLEEP', 100))
HUNDRED_YEARS = 60 * 60 * 24 * 365 * 100
THOUSAND_SECONDS = 1000
DEBUG = os.getenv("DEBUG", "0") == "1"
HEARTBEAT_INTERVAL = os.getenv("HEARTBEAT_INTERVAL", 2 * 60)  # 2 Min


MARKETS_IDS = 1, 7, 11,

SPORT_IDS = 1, 2, 5

OUTCOMES = {
    "TU": "Under",
    "TO": "Over",
    "Y": "Yes",
    "N": "No"
}

ANTEPOST = "Race"
MARKETS = {
    "BTS": "BTTS",
    "OU": "O/U"
}

SPORTS_MAPPING = {
    7: 1,
    2: 2,
    8: 5
}

logging.basicConfig(level=logging.INFO)


class SocketParser(Parser):

    def __init__(self, bookmaker_id: int, bookmaker_name: str, ):
        super().__init__(bookmaker_id, bookmaker_name, INVERTED_DIRECTION, PERCENTAGE_LIMIT)

        self.outcomes_data = None
        self.events_data = None

        self.outcomes = {int(outcome['id']): outcome for outcome in
                         get(url="https://api-mst.oddsmarket.org/v1/market_and_bet_types").json()}
        self.markets = {int(market['id']): market for market in
                        get(url="https://api-mst.oddsmarket.org/v1/markets").json()['response']}
        self.last_heartbeat = None

    def on_open(self, ws):
        """

        :param ws:
        :return:
        """
        self.socket.send(dumps({"msg": API_KEY, "cmd": "authorization"}))
        self.socket.send(dumps({"msg": {"bookmakerIds": [BOOKMAKER_ID], "sportIds": [2, 7, 8]}, "cmd": "subscribe"}))

    @staticmethod
    def on_close(ws, close_status_code, close_msg):
        logging.error(f"Connection Closed {close_msg}, {close_status_code}")

    def heartbeat(self):

        if not self.last_heartbeat or time.time() - self.last_heartbeat > HEARTBEAT_INTERVAL:
            super().heartbeat()
            self.last_heartbeat = time.time()

    def on_message(self, ws, message: str):
        """

        :param ws:
        :param message:
        :return:
        """
        try:

            data = loads(message)
            command, message = data['cmd'], data['msg']

            if command == 'authorized':
                logging.info("Authorized")
            elif command == 'subscribed':
                logging.info(str(data['msg']) + 'Subscribed')
            elif command == "fields":
                self.outcomes_data, self.events_data = message['Outcome'], message['BookmakerEvent']
            elif command == "outcomes":
                self.on_odd_change(message)
            elif command == "bookmaker_events":
                self.on_event_change(message)
            elif command == 'error':
                logging.error("Error received :- " + str(message))
            elif command == "bookmaker_events_removed":
                pass
            else:
                logging.critical("Unknown command is received ", command, message)

            self.heartbeat()
        except Exception as e:
            logging.exception(e)

    def on_odd_change(self, message: List[List[Any]]):
        """

        :param message:
        :return:
        """
        changes = [
            {key: value for key, value in zip(self.outcomes_data, change)}
            for change in message
        ]

        if not len(changes):
            return

        event_id = changes[0]['bookmakerEventId']
        event = self.load_event(f"{self.name}:{event_id}")

        if not event:
            return

        variations = Variations(event)
        updates = event.back or {}

        for change in changes:
            outcome_id = change['marketAndBetTypeId']
            outcome = self.outcomes[outcome_id]
            market = self.markets[outcome['marketId']]
            sbv = change.get('marketAndBetTypeParameterValue', '#')

            if market['id'] not in MARKETS_IDS:
                continue

            if event.sport_id == 1:  # Soccer
                if change['periodName'] != 'match':
                    continue
                if market['id'] == 7:
                    if sbv != 2.5:
                        continue
                    else:
                        sbv = '#'

            if sbv in (0, "0.0"):
                sbv = "#"

            market_name = MARKETS.get(market['shortTitle'], market['shortTitle'])
            outcome_name = outcome['title'].split('-')[-1]
            outcome_name = OUTCOMES.get(outcome_name, outcome_name)
            odd_value = float(change['odds'])

            if market_name not in updates:
                updates[market_name] = {}
            if sbv not in updates[market_name]:
                updates[market_name][sbv] = {}

            if outcome_name in updates[market_name][sbv]:
                prev_value = updates[market_name][sbv][outcome_name]['odd']

                if odd_value != prev_value:
                    key = f'back.{market_name}.{sbv}.{outcome_name}'
                    if not self.percentage_checker(odd=odd_value, prev_odd=prev_value, key=key):
                        continue

                else:
                    continue

            updates[market_name][sbv][outcome_name] = {"odd": odd_value, "lastUpdate": int(time.time())}

            variations.append(
                Variation(
                    _id=event.id,
                    bookmaker_name=self.name,
                    sport_id=event.sport_id,
                    market_name=market_name,
                    sbv=sbv,
                    outcome_name=outcome_name,
                    odd=odd_value,
                    last_update=int(datetime.now().timestamp()),
                    status=event.status
                )
            )

        if variations.exists():
            event.back = updates
            event.set_is_new(False)
            if DEBUG:
                logging.info("event is updating with odd change " + str(event.__dict__))
            variations.calculate_main_lines(updates)
            self.store_variations(variations=variations)
            self.store(event)

    def on_event_change(self, message: List[List[Any]]):
        """
        Called with new event data
        :param message:
        :return: None
        """

        events = [
            self.get_event({key: value for key, value in zip(self.events_data, event)}, datetime.now())
            for event in message
        ]
        events = [event for event in events if event]

        for event in events:
            if event.sport_id not in SPORT_IDS:
                continue

            current_event = self.load_event(event.key)

            if not current_event:
                event.set_is_new(True)
            else:
                old_odds = current_event.back
                last_update = event.last_update

                current_event.back = None
                event.last_update = current_event.last_update

                if event.__dict__ == current_event.__dict__:
                    continue  # check if it updated or not
                else:
                    current_event.back = old_odds
                    event.last_update = last_update

                event.set_is_new(False)
                event.back = current_event.back
                self.send_fixture_variations(event, current_event)

                if DEBUG:
                    logging.info("updating" + str(current_event.__dict__) + str(message) + str(
                        [
                            {key: value for key, value in zip(self.events_data, event)}
                            for event in message
                        ]))

            self.store(event)

    def get_event(self, event: any, last_update: datetime) -> Union[None, Event]:
        """

        :param event:
        :param last_update:
        :return:
        """

        if event['away'] == ANTEPOST:
            if DEBUG:
                logging.info("ANTEPOST event found --> Skipping" + str(event))
            return

        key = f"oddsmarket:{event['eventId'] if event['eventId'] != 0 else event['rawId']}"
        betradar_id = self.cache.get(key)

        if betradar_id:
            betradar_id = int(betradar_id)
        else:
            logging.warning("betradar Id not found in cache for " + str(event))

        sport_id = int(event['sportId'])

        after_100_years = time.time() + HUNDRED_YEARS
        if event['startedAt'] > after_100_years:  # timestamp in milliseconds
            event['startedAt'] //= THOUSAND_SECONDS

        if event['updatedAt'] > after_100_years:
            event['updatedAt'] //= THOUSAND_SECONDS

        try:
            return Event(_id=event['id'], bookmaker_id=self.id, bookmaker_name=self.name, date=event['startedAt'],
                         sport_id=SPORTS_MAPPING.get(sport_id, sport_id), sport_name=event['sportName'],
                         home_id=event['homeId'],
                         home_name=event['home'], away_id=event['awayId'], away_name=event['away'],
                         category_id=None, category_name=None, tournament_id=event['leagueId'],
                         tournament_name=event['leagueName'], betradar_id=betradar_id,
                         status=event['active'], last_update=event['updatedAt'])
        except InvalidEvent as e:
            logging.exception(e)

    def handle(self):

        while True:
            try:
                self.socket = WebSocketApp(url=URL, on_close=self.on_close,
                                           on_message=self.on_message,
                                           on_open=self.on_open)
                self.socket.run_forever()

            except Exception as e:
                print_exception(e)
