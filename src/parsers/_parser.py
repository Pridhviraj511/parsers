import json
import os
from datetime import datetime
from typing import Union, Tuple
from traceback import print_exc
import pika

from database.mongodb import get_db
from models import TYPE_FIXTURE_VARIATION
from models.event import Event
from models.variation import Variations
from utils.cache import Cache

RMQ_HOSTNAME = os.getenv('RMQ_HOSTNAME', 'localhost')
RMQ_VHOST = os.getenv('RMQ_VHOST', '/')
RMQ_USERNAME = os.getenv('RMQ_USERNAME')
RMQ_PASSWORD = os.getenv('RMQ_PASSWORD')
RMQ_TOPIC_NEW_EVENT = os.getenv('RMQ_TOPIC_NEW_EVENT', 'new-event')
RMQ_TOPIC_HEARTBEAT = os.getenv('RMQ_TOPIC_HEARTBEAT', 'heartbeat')
RMQ_TOPIC_ODD_VARIATION = os.getenv('RMQ_TOPIC_ODD_VARIATION', 'odd-variation')
RMQ_TOPIC_FIXTURE_VARIATION = os.getenv('RMQ_TOPIC_FIXTURE_VARIATION', 'fixture-variation')

DEBUG = int(os.getenv('DEBUG', 0)) == 1

client = get_db()


class Parser:

    def __init__(self, bookmaker_id: int, bookmaker_name: str, inverted_direction: int, percentage_limit: float):
        """
        This class contains common data for all bookmakers.

        :param bookmaker_id: ID of the bookmaker.
        :param bookmaker_name: Bookmaker's name.
        :param inverted_direction: Is the direction of the SBV in the right order.
        :param percentage_limit: The upper limit of the percentage for the acceptance of new odds.
        """

        self.id = bookmaker_id
        self.name = bookmaker_name
        self.inverted_direction = inverted_direction
        self.percentage_limit = percentage_limit
        self.cache: Cache = Cache()
        self.connect_to_rmq()
        self.channel.exchange_declare(exchange=self.name, exchange_type='fanout', durable=True)
        self.channel.exchange_declare(exchange=RMQ_TOPIC_NEW_EVENT, exchange_type='topic', durable=True)
        self.channel.exchange_declare(exchange=RMQ_TOPIC_ODD_VARIATION, exchange_type='fanout', durable=True)
        self.channel.exchange_declare(exchange=RMQ_TOPIC_FIXTURE_VARIATION, exchange_type='fanout', durable=True)

    def connect_to_rmq(self):
        if RMQ_USERNAME is not None and RMQ_PASSWORD is not None:
            credentials = pika.PlainCredentials(RMQ_USERNAME, RMQ_PASSWORD)
        else:
            credentials = pika.ConnectionParameters.DEFAULT_CREDENTIALS

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(RMQ_HOSTNAME, virtual_host=RMQ_VHOST, credentials=credentials, heartbeat=300,
                                      client_properties={
                                          'connection_name': str(self.name),
                                      }
                                      ))
        self.channel = self.connection.channel()

    @staticmethod
    def round_number(num: float) -> float:
        """
        Rounds the odds to two decimal places. (2,565 -> 2.57)

        :param num: Odd we round.
        :return: Rounded odd.
        """

        return 0 if num <= 1.0 else int((num * 100) + 0.5) / 100.0

    def check_odd(self, odd: float) -> float:
        """
        This function checks the odd value to keep a consistent format in the database and returns 0 if the odd value is
        like None, 0, -1, 1, etc.

        :param odd: This is the odd that needs to be checked.
        :return: This returns 0 or odd if exists.
        """

        return self.round_number(odd) if odd else 0

    def check_sbv(self, sbv: str, market_id: int) -> str:
        """
        Preparation of SBV to the appropriate value that we store in the database.

        :param sbv: SBV we check.
        :param market_id: The format of SBV depends on the market.
        :return: Returns SBV format we need, otherwise it returns an empty string.
        """

        if market_id == 2 and sbv not in (2.5, '2.5', '#'):  # Accepting only sbv=2.5 for soccer Over/Under
            return ''

        sbv = '#' if market_id in {1, 2, 3, 4, 9} else (sbv if sbv is None else str(sbv))
        if not sbv:
            return ''

        if self.inverted_direction == 1 and market_id in {6, 8} and sbv not in ("0", "0.0", "#"):
            sbv = str(float(sbv) * -1)

        return sbv

    def percentage_checker(self, odd: float, prev_odd: float, key: str) -> bool:
        """
        Calculates the percentage between the new and the previous odd, and compares it with the allowed
        percentage from the settings.

        :param odd: New odd that arrived.
        :param prev_odd: Previous odd.
        :param key: Historical path to that odd so we can find it faster.
        :return: Returns False if we have to skip inserting new odd value, because the odd change from previous one
        is not significant.
        """

        if self.percentage_limit != 0 and odd != 0 and prev_odd != 0:
            percent = round((odd / prev_odd - 1) * 100, 2)
            percent = abs(percent)
            if percent < self.percentage_limit:
                # print(f'Skipping odd {key}, old: {prev_odd}, new: {odd}, percent: {percent}')
                return False
        return True

    def load_event(self, key: str) -> Union[None, Event]:
        """
        Getting previous event from Redis if they exist, the key is for example "bookmaker_name:123456"
        :param key: ID of event we want.
        :return: redis key that we will use later for storing the changes, markets dictionary.
        """
        event = self.cache.get(key)
        if event:  # If event is already in Redis
            return Event.from_dict(event)
        else:
            return None

    def store_event(self, event: Event):
        """
        Putting the data to Redis, and setting the expiration date, so events will be automatically deleted from
        Redis 5min after they start.

        :param event: Value that we store.
        """

        exp = int(event.date - datetime.utcnow().timestamp())
        exp = exp + 21600 if exp > 0 else 300  # keep this 6h because results can arrive later and we need last odds

        self.cache.set(event.key, event.__dict__, exp)

    def get_event(self, event: any, last_update: datetime) -> Union[None, Event]:
        """
        This function parses the required data and creates a unique format for storage in MongoDB.
        We also use Redis to get previous odds, so that we can keep only the new ones, and also keep the historical
        odds without duplicates. If necessary - we can set the percentage below we will not accept the changes,
        as there will be a lot of calculations for the weighted average system unnecessarily.

        :param event: This is the event we parse.
        :param last_update: Date and time (UTC) when this event received last time.
        """
        pass

    def _get_market_data(self, update):
        """
        Get market data from update

        :param update
        :return object
        """
        return update['markets']

    def get_market(self, event: Event, markets: dict, current_event: Event) -> Tuple[dict, int]:
        """
        This function parses the market received according to our standard format and if it is the first time that we receive odds for this event

        :param event: Event that we are parsing.
        :param markets: Market data that we received
        :param current_event: Last received event
        """
        pass

    def handle(self):
        """
        This function will be implemented in specific parser
        """

    def handle_event(self, event: dict, last_update: datetime) -> bool:
        """
        This function will hande event and odds
        """
        try:

            ev = self.get_event(event=event, last_update=last_update)
            if ev is None:
                # if DEBUG: print("Invalid event", event)
                return False

            # load event from cache and set if it is new
            current_event = self.load_event(key=ev.key)
            if current_event is None:
                ev.set_is_new(True)
                fixture_vars = True
            else:
                ev.set_is_new(False)
                fixture_vars = self.send_fixture_variations(ev, current_event)

            # load event odds and variation
            odds, odd_vars = self.get_market(ev, self._get_market_data(event), current_event)
            # if DEBUG: print("No variation" if not len(odds) else "", event)
            ev.set_odds(odds)

            if fixture_vars or odd_vars:
                self.store(ev)
            else:
                print("no updates found for event", ev.id)

            return True
        except Exception as e:
            print_exc()
            return False

    def store(self, event: Event):
        """
        This function will store single event on kafka

        :param event: This is the event parsed ready to be stored.
        """

        self.store_event(event)

        if self.connection.is_closed:
            self.connect_to_rmq()

        instance = event.serialize()
        self.channel.basic_publish(
            exchange=self.name,
            routing_key='',
            body=json.dumps(instance).encode('utf-8'))

        if event.is_new:
            instance = event.serialize(True)
            self.channel.basic_publish(
                exchange=RMQ_TOPIC_NEW_EVENT,
                routing_key=RMQ_TOPIC_NEW_EVENT,
                body=json.dumps(instance).encode('utf-8'))

    def heartbeat(self):
        """
        This function will send a heartbeat message on kafka
        """
        """
        This function will check the status of the parser
        """
        if self.connection.is_closed or self.channel.is_closed:
            self.connect_to_rmq()

        try:
            self.channel.basic_publish(
                exchange='',
                routing_key=RMQ_TOPIC_HEARTBEAT,
                body=self.name.encode('utf-8'))
        except Exception as e:
            # print_exception(e)
            self.connect_to_rmq()

    def store_variations(self, variations: Variations, mainline: str = '#'):
        """
        This function will store only odd changed on kafka

        :param variations: This is the list of variation that need to be stored
        """
        if self.connection.is_closed:
            self.connect_to_rmq()

        if len(variations.variations) > 10:
            print("number is ", len(variations.variations))
            # print(variations.serialize())


        if variations.exists():
            self.channel.basic_publish(
                exchange=RMQ_TOPIC_ODD_VARIATION,
                routing_key=RMQ_TOPIC_ODD_VARIATION,
                body=variations.serialize().encode('utf-8'))

    def send_fixture_variations(self, event: Event, origin: Event):
        """
        cambio fixture
        cambio data
        cambio stato evento (attivo/disattivo, dovrebbe rimuovere o aggiungere evento)
        aggiunta nuovo evento

        rimozione mercato
        aggiunta nuova mappatura
        """
        comparation = [
            'date', 'home_id', 'home_name', 'away_id', 'away_name', 'tournament_id',
            'tournament_name', 'category_id', 'category_name', 'betradar_id', 'status',
            'live'
        ]

        variations = {
            'type': TYPE_FIXTURE_VARIATION,
            '_id': event.id,
            'bookmaker_name': event.bookmaker_name,
            'sport_id': event.sport_id
        }

        i = 0
        for key in comparation:
            if getattr(event, key) != getattr(origin, key):
                variations[key] = getattr(event, key)
                i += 1

        if i == 0:
            return i

        if self.connection.is_closed:
            self.connect_to_rmq()

        if ('betradar_id' in variations or 'date' in variations) and not event.is_new:
            instance = event.serialize(True)
            self.channel.basic_publish(
                exchange=RMQ_TOPIC_NEW_EVENT,
                routing_key=RMQ_TOPIC_NEW_EVENT,
                body=json.dumps(instance).encode('utf-8'))

        self.channel.basic_publish(
            exchange=RMQ_TOPIC_FIXTURE_VARIATION,
            routing_key='',
            body=json.dumps(variations).encode('utf-8'))

        return i
