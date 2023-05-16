import os

from parsers._betradar import BetradarParser

INVERTED_DIRECTION = int(os.getenv('INVERTED_DIRECTION', 0))
PERCENTAGE_LIMIT = float(os.getenv('PERCENTAGE_LIMIT', 0))

URL = os.getenv('URL', 'http://osrv20.oddsandmore.com')
SLEEP = int(os.getenv('SLEEP', 10))

MIN_TIME = int(os.getenv('min_time', 200))
ALERT_TIME = int(os.getenv('alert_time', 3600))
QSIZE = int(os.getenv('q_size', 15))


class BetiumParser(BetradarParser):

    def __init__(self):
        """ This is the Container class that extends the Bookmaker class and gives us some additional info we need. """

        super().__init__(
            bookmaker_id=7,
            bookmaker_name='betium',
            inverted_direction=INVERTED_DIRECTION,
            percentage_limit=PERCENTAGE_LIMIT,
            url=URL,
            sleep=SLEEP,
            sports={1: 1, 2: 2, 3: 5}
        )
