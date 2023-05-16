import datetime
import os

from bson.json_util import loads, dumps
from redis.client import Redis

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', None)
REDIS_DB = int(os.environ.get('REDIS_DB', 0))


class Cache:
    def __init__(self):
        self.client: Redis = Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True, db=REDIS_DB)

    def get(self, redis_key: str):
        """
        Getting previous odds from Redis if they exist, the key is for example "bookmaker_name@123456@"

        :param redis_key: rey to retrive
        :return: redis key that we will use later for storing the changes, markets dictionary.
        """

        # maybe add few more data to redis like last update that depends only on odds changes or date
        value = self.client.get(name=redis_key)
        if value is None:
            return None
        return loads(value)

    def set(self, redis_key: str, r: dict, expire: int = 300):
        """
        Putting the data to Redis, and setting the expiration date, so events will be automatically deleted from
        Redis 5min after they start.

        :param redis_key: Hash name ('betium@27885876@').
        :param r: Value that we store.
        :param expire: Key expiration time in sec from now
        """

        self.client.set(name=redis_key, value=dumps(r))  # Storing to Redis
        self.client.expire(redis_key, expire)

    def put(self, date: datetime, redis_key: str, r: dict):
        """
        Putting the data to Redis, and setting the expiration date, so events will be automatically deleted from
        Redis 5min after they start.

        :param odds_type: BACK or LAY.
        :param date: Start date of the event.
        :param redis_key: Hash name ('betium@27885876@').
        :param r: Value that we store.
        """

        exp = (date - datetime.datetime.now()).total_seconds()
        exp = int(exp) + 300
        # In "r" we can also add "lastUpdate" so we can change "lastUpdate" param only when we have odd change,
        # or to add "date" also and to change "lastUpdate" param on date and odd change.
        self.client.set(name=redis_key, value=dumps(r))  # Storing to Redis
        self.client.expire(redis_key, exp)
