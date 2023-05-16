import time
from typing import Dict

from utils import to_camel_case

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

SOCCER_ID = 1
BASKET_ID = 2
TENNIS_ID = 5
VOLLEY_ID = 23

SPORTS: Dict[int, str] = {
    SOCCER_ID: 'Soccer',
    BASKET_ID: 'Basketball',
    TENNIS_ID: 'Tennis',
    VOLLEY_ID: 'Volleyball'
}


class Update:
    _id: int
    bookmaker_id: int
    bookmaker_name: str
    sport_id: int
    sport_name: str
    is_new: bool = False

    def __init__(self, _id: int,
                 bookmaker_id: int,
                 bookmaker_name: str,
                 sport_id: int = None,
                 sport_name: str = '',
                 back: dict = None,
                 last_update: int = None
                 ):
        """
        This class contains all the common data we use for a single event.

        :param bookmaker_id: ID of the bookmaker.
        :param bookmaker_name: Bookmaker's name.
        :param sport_id: ID of the sport.
        :param lay: True if bookmaker has lay odds.
        """

        self._id = _id
        self.bookmaker_id: int = bookmaker_id
        self.bookmaker_name: str = bookmaker_name
        self.sport_id: int = sport_id
        self.sport_name: str = sport_name
        self.last_update: int = last_update if last_update is not None else int(time.time())
        self.back: dict = back

    @property
    def id(self):
        return self._id

    @property
    def key(self):
        return f'{self.bookmaker_name}:{self._id}'

    def serialize(self, no_odds=False) -> dict:
        stream = {}
        for key in self.__dict__:
            if no_odds and key in ['back', 'lay']: continue
            _k = to_camel_case(key) if not key.startswith('_') else key
            stream[_k] = self.__dict__[key]
        return stream

    def set_is_new(self, is_new: bool):
        self.is_new = is_new
