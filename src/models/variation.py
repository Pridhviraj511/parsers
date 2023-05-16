from json import dumps

from models import TYPE_ODD_VARIATION
from models.event import Event
from utils import calculate_mainline


class Variations(object):
    id: int
    sport_id: int
    bookmaker_name: str
    status: bool
    mainLines: str = None
    variations = []

    def __init__(self, event: Event):
        self.id = event.id
        self.sport_id = event.sport_id
        self.bookmaker_name = event.bookmaker_name
        self.status = event.status
        self.variations = []

    def append(self, item):
        self.variations.append(item)

    def exists(self):
        return len(self.variations)

    def calculate_main_lines(self, odds):
        self.mainLines = calculate_mainline(odds)

    def serialize(self) -> str:
        return dumps({
            'type': TYPE_ODD_VARIATION,
            'id': self.id,
            'sportId': self.sport_id,
            'bookmakerName': self.bookmaker_name,
            'status': self.status,
            'mainLines': self.mainLines,
            'updates': [x.serialize() for x in self.variations]
        })


class Variation:
    _id: int
    bookmaker_name: str
    sport_id: int
    market_name: str
    sbv: str
    outcome_name: str
    odd: float
    last_update: int
    back: bool = True
    status: bool = True

    def __init__(self,
                 _id: int,
                 bookmaker_name: str,
                 sport_id: int,
                 market_name: str,
                 sbv: str,
                 outcome_name: str,
                 odd: float,
                 last_update,
                 status: bool = True
                 ):
        """
        This class contains all the common data we use for a single variation.
        """
        self._id = _id
        self.bookmaker_name = bookmaker_name
        self.sport_id = sport_id
        self.market_name = market_name
        self.sbv = sbv
        self.outcome_name = outcome_name
        self.odd = odd
        self.last_update = last_update
        self.status = status

    def serialize(self):
        return self.__dict__
