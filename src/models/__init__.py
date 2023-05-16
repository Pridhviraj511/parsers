import time
from json import dumps

TYPE_FIXTURE_VARIATION = 'fx'
TYPE_ODD_VARIATION = 'ov'
TYPE_NEW_EVENT = 'ne'
#
BOOKMAKER_MAP = {
    1: "eurobet",
    101: 'eurobet-direct',
    2: "betfair",
    3: "pinnacle",
    12: "goldbet",
    22: "vincitu",
    26: "snai",
    30: "feedmaker",
    31: "sisal",
    33: "bet365",
    34: "eplay24",
    39: "better",
    42: 'ladbrokes',
    43: 'bwin',
    44: 'unibet',
    45: 'betfirst',
    46: 'betradarUOF',
    47: 'unibet2',
    48: 'pinnacle2',
    49: 'feedmakernew',
    50: 'betfair-lay',
    51: 'scomesseitalia',
    52: 'vincitu'

}
BOOKMAKERS = list(BOOKMAKER_MAP.values())


class Heartbeat:
    bookmaker: str
    timestamp: int

    def __init__(self, bookmaker: str):
        self.bookmaker = bookmaker
        self.timestamp = int(time.time())

    def serialize(self):
        return dumps({"bookmaker": self.bookmaker, "timestamp": self.timestamp})
