import os
from time import sleep

from parsers.crawler_socket import CrawlerSocket

BOOKMAKER_ID = int(os.getenv('BOOKMAKER_ID'))
BOOKMAKER = os.getenv('BOOKMAKER')
INVERTED_DIRECTION = int(os.getenv('INVERTED_DIRECTION', 0))
PERCENTAGE_LIMIT = float(os.getenv('PERCENTAGE_LIMIT', 0))

if __name__ == '__main__':

    c = CrawlerSocket(
        bookmaker_id=BOOKMAKER_ID,
        bookmaker_name=BOOKMAKER,
        inverted_direction=INVERTED_DIRECTION,
        percentage_limit=PERCENTAGE_LIMIT
    )

    c.handle()

    while True:
        sleep(1000)
