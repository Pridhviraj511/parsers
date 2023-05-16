from typing import Union

from models.update import Update


class InvalidEvent(Exception):
    pass


class Event(Update):
    date: int
    home_id: int
    home_name: str
    away_id: int
    away_name: str
    tournament_id: int
    tournament_name: str
    category_id: int
    category_name: str
    betradar_id: Union[int, None]
    aams: str
    status: bool
    live: bool
    no_odds: bool = True
    back: dict = {}
    lay: dict = {}

    def __init__(self, _id: int, bookmaker_id: int, bookmaker_name: str, date: int, sport_id: int, sport_name: str,
                 home_id: Union[int, None], home_name: str, away_id: Union[int, None], away_name: str,
                 tournament_id: int, tournament_name: str, category_id: int, category_name: str,
                 betradar_id: Union[int, None], status: bool, last_update: int, aams: str = None, live: bool = False,
                 back=None, lay=None):
        """
        This class contains all the common data we use for a single event.

        :param bookmaker_id: ID of the bookmaker.
        :param bookmaker_name: Bookmaker's name.
        :param sport_id: ID of the sport.
        :param lay: True if bookmaker has lay odds.
        """

        super().__init__(_id, bookmaker_id, bookmaker_name, sport_id, sport_name, back, last_update)
        self.date = date

        if not isinstance(home_name, str) or len(home_name) < 1:
            raise InvalidEvent(f"Invalid home Id or home Name | home_id={home_id}, home_name={home_name}")
        else:
            self.home_id: int = home_id
            self.home_name: str = home_name

        if not isinstance(away_name, str) or len(away_name) < 1:
            raise InvalidEvent(f"Invalid away Id or away Name | away_id={away_id}, away_name={away_name}")
        else:
            self.away_id: int = away_id
            self.away_name: str = away_name

        self.tournament_id: int = tournament_id
        self.tournament_name: str = tournament_name
        self.category_id: int = category_id
        self.category_name: str = category_name
        self.sport_id: int = sport_id
        self.sport_name: str = sport_name
        self.betradar_id: int = betradar_id
        self.aams: str = aams
        self.status: bool = status
        self.live: bool = live
        self.lay: dict = lay
        self.back: dict = back

    def set_odds(self, odds):
        self.no_odds = True
        if 'back' in odds:
            self.no_odds = False
            self.back = odds['back']
        if 'lay' in odds:
            self.no_odds = False
            self.lay = odds['lay']
        if 'live' in odds:
            self.no_odds = False
            self.live = odds['live']

    @classmethod
    def make_outcome(cls, removed: bool = False) -> dict:
        """
        Returns a dictionary with the required data for the outcome.

        :param removed: If True it adds 'removed' flag in outcome.
        :return: Returns outcome format depending on a 'removed' flag.
        """

        return dict(odd=0, removed=True, lastUpdate=0) if removed else dict(odd=0, lastUpdate=0)

    @classmethod
    def make_sbv(cls, market, sbv: str, removed: bool = False) -> dict:
        """
        Creates dictionary where sbv is key and value is dictionary with default outcomes for certain market.

        :param market: ID or name of the market.
        :param sbv: SBV that we create.
        :param removed: If we need this flag in the format, e.g. in Redis.
        :return: Returns dict with sbv and outcomes if market exists.
        """

        sbv = str(sbv)  # the key in MongoDB must not contain a dot "."

        if market in (10, '1X2'):  # 1X2
            return {
                sbv: {
                    '1': cls.make_outcome(removed=removed),
                    'X': cls.make_outcome(removed=removed),
                    '2': cls.make_outcome(removed=removed)},
            }
        elif market in (20, 'H/H'):  # Head to head (12)
            return {sbv: {
                '1': cls.make_outcome(removed=removed),
                '2': cls.make_outcome(removed=removed)},
            }
        elif market in (51, 'HND'):  # Handicap
            return {sbv: {
                '1': cls.make_outcome(removed=removed),
                '2': cls.make_outcome(removed=removed)},
            }
        elif market in (16, 'HND'):  # Handicap
            return {sbv: {
                '1': cls.make_outcome(removed=removed),
                '2': cls.make_outcome(removed=removed)},
            }
        elif market in (187, 'HND'):
            return {sbv: {
                '1': cls.make_outcome(removed=removed),
                '2': cls.make_outcome(removed=removed)},
            }
        elif market in (189, 'O/U'):
            return {sbv: {
                'Over': cls.make_outcome(removed=removed),
                'Under': cls.make_outcome(removed=removed)},
            }
        elif market in (223, 'HND'):  # Handicap basket
            return {sbv: {
                '1': cls.make_outcome(removed=removed),
                '2': cls.make_outcome(removed=removed)},
            }
        elif market in (225, 'O/U'):  # Under/Over Basket
            return {sbv: {
                'Over': cls.make_outcome(removed=removed),
                'Under': cls.make_outcome(removed=removed)},
            }
        elif market in (43, 'BTTS'):  # Both teams to score (goal/no goal)
            return {sbv: {
                'Yes': cls.make_outcome(removed=removed),
                'No': cls.make_outcome(removed=removed)},
            }
        elif market in (60, 'O/U'):  # Over/Under
            return {sbv: {
                'Over': cls.make_outcome(removed=removed),
                'Under': cls.make_outcome(removed=removed)},
            }
        elif market in (226, 'O/U'):  # Over/Under
            return {sbv: {
                'Over': cls.make_outcome(removed=removed),
                'Under': cls.make_outcome(removed=removed)},
            }
        elif market in (18, 'O/U'):  # Over/Under
            return {sbv: {
                'Over': cls.make_outcome(removed=removed),
                'Under': cls.make_outcome(removed=removed)},
            }
        elif market in (165, 'Corner HH'):
            return {
                sbv: {
                    '1': cls.make_outcome(removed=removed),
                    '2': cls.make_outcome(removed=removed),
                }
            }
        elif market in (166, 'Corner Totals'):
            return {
                sbv: {
                    'Over': cls.make_outcome(removed=removed),
                    'Under': cls.make_outcome(removed=removed),
                }
            }
        elif market in (186, 'H/H'):
            return {
                sbv: {
                    '1': cls.make_outcome(removed=removed),
                    '2': cls.make_outcome(removed=removed),
                }
            }
        elif market in (237, 'HND'):  # Handicap volleyball
            return {sbv: {
                '1': cls.make_outcome(removed=removed),
                '2': cls.make_outcome(removed=removed)},
            }
        elif market in (238, 'O/U'):  # Over/Under volleyball
            return {sbv: {
                'Over': cls.make_outcome(removed=removed),
                'Under': cls.make_outcome(removed=removed)},
            }
        elif market in (16, 'HND'):
            return {sbv: {
                '1': cls.make_outcome(removed=removed),
                '2': cls.make_outcome(removed=removed)},
            }
        else:
            print(f'{market} market does not exists')
            return {}

    @classmethod
    def from_dict(cls, cached_value):
        return cls(
            _id=cached_value['_id'],
            bookmaker_id=cached_value['bookmaker_id'],
            bookmaker_name=cached_value['bookmaker_name'],
            date=cached_value['date'],
            home_id=cached_value['home_id'],
            home_name=cached_value['home_name'],
            away_id=cached_value['away_id'],
            away_name=cached_value['away_name'],
            tournament_id=cached_value['tournament_id'],
            tournament_name=cached_value['tournament_name'],
            category_id=cached_value['category_id'],
            category_name=cached_value['category_name'],
            sport_id=cached_value['sport_id'],
            sport_name=cached_value['sport_name'],
            betradar_id=cached_value['betradar_id'],
            aams=cached_value['aams'],
            status=cached_value['status'],
            live=cached_value['live'],
            last_update=cached_value['last_update'],
            back=cached_value['back']
        )


class FeedMakerEvent(Event):
    season: dict
    tournament_round: dict
    home_info: dict
    away_info: dict
    extra: dict
    result: dict
    extra_result: dict

    def __init__(self, _id: int, bookmaker_id: int, bookmaker_name: str, date: int, sport_id: int, sport_name: str,
                 home_id: Union[int, None], home_name: str, home_info: dict, away_id: Union[int, None], away_name: str,
                 away_info: dict, tournament_id: int, tournament_name: str, tournament_round: dict, season: dict,
                 category_id: int, category_name: str, betradar_id: int, status: bool, last_update: int,
                 aams: str = None, live: bool = False, back=None, lay=None, extra: dict = {}, result: dict = {},
                 extra_result: dict = {}, *_, **kwargs):
        super().__init__(_id, bookmaker_id, bookmaker_name, date, sport_id, sport_name, home_id, home_name, away_id,
                         away_name, tournament_id, tournament_name, category_id, category_name, betradar_id, status,
                         last_update, aams, live, back, lay)

        self.home_info = home_info
        self.away_info = away_info
        self.season = season
        self.tournament_round = tournament_round
        self.extra = extra
        self.result = result
        self.extra_result = extra_result

    @classmethod
    def from_dict(cls, **kwargs):
        return cls(**kwargs)


class OutRight(FeedMakerEvent):
    outright_name: str
    start_date: int
    expiry_date: int
    end_date: int

    def __init__(self, *args, **kwargs):
        super(OutRight, self).__init__(*args, **kwargs)
        self.outright_name = kwargs.get('outright_name')
        self.start_date = kwargs.get('start_date')
        self.expiry_date = kwargs.get('expiry_date')
        self.end_date = kwargs.get('end_date')


class FeedMakerEvent(Event):
    season: dict
    tournament_round: dict
    home_info: dict
    away_info: dict
    extra: dict
    result: dict
    extra_result: dict
    translations: dict

    def __init__(self, _id: int, bookmaker_id: int, bookmaker_name: str, date: int, sport_id: int, sport_name: str,
                 home_id: Union[int, None], home_name: str, home_info: dict, away_id: Union[int, None], away_name: str,
                 away_info: dict, tournament_id: int, tournament_name: str, tournament_round: dict, season: dict,
                 category_id: int, category_name: str, betradar_id: int, status: bool, last_update: int,
                 aams: str = None, live: bool = False, back=None, lay=None, extra: dict = {}, result: dict = {},
                 extra_result: dict = {}, *_, **kwargs):
        super().__init__(_id, bookmaker_id, bookmaker_name, date, sport_id, sport_name, home_id, home_name, away_id,
                         away_name, tournament_id, tournament_name, category_id, category_name, betradar_id, status,
                         last_update, aams, live, back, lay)

        self.home_info = home_info
        self.away_info = away_info
        self.season = season
        self.tournament_round = tournament_round
        self.extra = extra
        self.result = result
        self.extra_result = extra_result

    @classmethod
    def from_dict(cls, **kwargs):
        return cls(**kwargs)


class OutRight(Update):
    date: int
    tournament_id: int
    tournament_name: str
    category_id: int
    category_name: str
    betradar_id: Union[int, None]
    aams: str
    status: bool
    live: bool
    back: dict = {}
    lay: dict = {}

    season: dict
    tournament_round: dict
    extra: dict
    result: dict
    extra_result: dict

    outright_name: str
    start_date: int
    expiry_date: int
    end_date: int

    def __init__(self, _id: int, bookmaker_id: int, bookmaker_name: str, date: int, sport_id: int, sport_name: str,
                 tournament_id: int, tournament_name: str, category_id: int, category_name: str,
                 betradar_id: Union[int, None], status: bool, last_update: int,
                 outright_name, start_date, expiry_date, end_date, aams: str = None, live: bool = False,
                 back=None, lay=None, season={}, tournament_round={}, extra: dict = {}, result: dict = {},
                 extra_result: dict = {}, *_, **kwargs):
        super().__init__(_id, bookmaker_id, bookmaker_name, sport_id, sport_name, back, last_update)

        self.date = date
        self.tournament_id = tournament_id
        self.tournament_name = tournament_name
        self.category_id = category_id
        self.category_name = category_name
        self.betradar_id = betradar_id
        self.aams = aams
        self.status = status
        self.live = live
        self.back = back
        self.lay = lay

        self.season = season
        self.tournament_round = tournament_round
        self.extra = extra
        self.result = result
        self.extra_result = extra_result

        self.outright_name = outright_name
        self.start_date = start_date
        self.expiry_date = expiry_date
        self.end_date = end_date

    @classmethod
    def from_dict(cls, **kwargs):
        return cls(**kwargs)
