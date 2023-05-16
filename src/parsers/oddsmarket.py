import os
from datetime import datetime
from json import dumps, loads
from typing import List, Any, Union
from urllib.parse import urljoin, urlparse

from websocket import WebSocketApp
from requests import get, head
from lxml.etree import XML

from utils.cache import Cache
import logging

logging.basicConfig(level=logging.INFO)  # for websocket

URL = os.getenv('URL', "wss://api-pr.oddsmarket.org/v4/odds_ws")
BETRADAR_ID_URL = os.getenv("BETRADAR_ID_URL", 'https://fr.unibet.be/kambi-rest-api/sportradar/widget/event/fr/')
API_KEY = os.getenv("API_KEY", "")
BOOKMAKER_ID = os.getenv("BOOKMAKER_ID", 164)
DEBUG = os.getenv("DEBUG", "0") == "1"

SPORT_IDS = 2, 7, 8,


class OddsMarket:

    def __init__(self):

        self.cache = Cache()

        self.outcomes_data = None
        self.events_data = None

    def on_open(self, ws):
        """

        :param ws:
        :return:
        """
        self.socket.send(dumps({"msg": API_KEY, "cmd": "authorization"}))
        self.socket.send(dumps({"msg": {"bookmakerIds": [BOOKMAKER_ID]}, "cmd": "subscribe"}))

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
            elif command == "bookmaker_events_removed":
                pass
            else:
                logging.error("Unknown command is received " + str(command) + str(message))

        except Exception as e:
            logging.exception(e)

    def on_close(self, status_code, close_msg, *_, **args):
        """

        :param status_code:
        :param close_msg:
        :return:
        """
        logging.error(f'Closing connection : {status_code}, {close_msg}')

    def on_odd_change(self, message: List[List[Any]]):
        """

        :param message:
        :return:
        """
        if DEBUG:
            logging.info("New odd change" + str(message))

    def on_event_change(self, message: List[List[Any]]):
        """
        Called with new event data
        :param message:
        :return: None
        """

        events = [
            {key: value for key, value in zip(self.events_data, event)}
            for event in message
        ]

        for event in events:

            if event['sportId'] not in SPORT_IDS:
                continue

            key = f"oddsmarket:{event['eventId'] if event['eventId'] != 0 else event['rawId']}"
            old_value = self.cache.get(key)

            if not old_value:
                new_value = self.betradar_id(event['rawId'])

                if not new_value:
                    logging.warning("BetradarId not found for event :- " + str(event))
                    continue

                logging.info(f"updating betradarId for id={event['id']}|eventId={event['eventId']} to {new_value}")

                exp = int(event['startedAt'] - datetime.utcnow().timestamp())
                self.cache.set(key, new_value, expire=exp + 21600 if exp > 0 else 300)

    def betradar_id(self, id: int) -> Union[int, None]:
        """
        gets betradar id from api
        :param id: event_id
        :return: betradarId
        """

        response = get(urljoin(BETRADAR_ID_URL, str(id))).json()

        if response['statusCode'] == 200:
            url = urlparse(response['content'][0]['Resource'])
            betradar_id = int(url.fragment.split('=')[-1])

        else:
            betradar_id = None

            headers = head(f'https://s5.sir.sportradar.com/unibet/it/match/m{id}').headers

            if 'Location' in headers:
                betradar_id = headers['Location'].split('/')[-1]
                if betradar_id.isdigit():
                    betradar_id = int(betradar_id)
                else:
                    betradar_id = None
                    logging.info("betradarId not found in header's location " + str(headers['Location']))

            else:
                logging.warning(f"BetradarId not found for raw_id :- {id}")

        return betradar_id

    def handle(self):
        logging.info("OddsMarket Parser is started")

        while True:
            self.socket = WebSocketApp(url=URL, on_close=self.on_close,
                                       on_message=self.on_message,
                                       on_open=self.on_open)
            self.socket.run_forever()
