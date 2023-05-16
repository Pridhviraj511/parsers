import os
from datetime import timedelta
from functools import reduce
from json import dumps
from time import time

from requests import post, get


def update_dict(a: dict, b: dict) -> dict:
    """ This function updates dictionary "b" in the dictionary "a" """

    a.update(b)
    return a


class Parameter:

    def __init__(self, *args, **kwargs):

        if len(args) > 0:
            self._items = args
        for k, v in kwargs.items():
            setattr(self, k, v)


class Filter(Parameter):

    def value(self):
        return {'filter': self.__dict__}


class MarketProjection(Parameter):

    def value(self):
        return {'marketProjection': list(self._items)}


class MaxResult(Parameter):

    def value(self):
        return {'maxResults': self._items[0]}


class MarketId(Parameter):

    def value(self):
        return {'marketIds': list(self._items)}


class PriceProjection(Parameter):

    def value(self):
        return {'priceProjection': self.__dict__}


class BetfairApi:
    IDENTIFY_URL = os.getenv('IDENTIFY_URL', 'https://identitysso.betfair.com/api/')
    API_URL = os.getenv('URL', 'https://api.betfair.com/exchange/betting/json-rpc/v1/')

    def __init__(self, app_key, username, password):
        self.app_key: str = app_key
        self.username: str = username
        self.password: str = password
        self._token: str = ''
        self._expiry_date: float = 0

    def token(self) -> str:

        payload = {
            'username': self.username,
            'password': self.password
        }

        headers = {
            'X-Application': self.app_key,
            'Content-Type': 'application/x-www-form-urlencoded',
            'accept': 'application/json'
        }

        if not self._token:
            res = post(url=f'{self.IDENTIFY_URL}login', data=payload, headers=headers, timeout=120)
            if res.status_code == 200:
                doc = res.json()
                if doc['status'] == 'SUCCESS':
                    self._set_token(doc)
            else:
                print(f'Betfair error (token) status code: {res.status_code} {res}')

        elif self._about_to_expire_in(20) == True:  # About to expire in 20 minutes
            headers.update({"X-Authentication": self._token})
            res = get(url=f'{self.IDENTIFY_URL}keepAlive', headers=headers, timeout=120)
            if res.status_code == 200 or res.json()['status'] == 'SUCCESS':
                self._set_token(res.json())  # It will update _expiry_date to next {8} hours
            else:
                print(f"Betfair error (keepAlive) status code: {res.status_code} {res}")

        return self._token

    def _set_token(self, doc: dict):
        print('set token', doc['token'])
        self._token = doc['token']
        self._expiry_date = time() + timedelta(hours=8).total_seconds()

    def _about_to_expire_in(self, minutes: int) -> float:
        return time() > self._expiry_date - timedelta(minutes=minutes).total_seconds()

    def _headers(self) -> dict:

        return {
            'X-Application': self.app_key,
            'X-Authentication': self.token(),
            'Connection': 'keep-alive',
            'accept': 'application/json'
        }

    def _aping(self, payload: bytes) -> dict:
        try:

            r = post(self.API_URL, payload, headers=self._headers(), timeout=120)

            if r.status_code != 200:
                print(f'Status code for API_URL: {r.status_code}, {r}')

            return r.json()
        except Exception as e:
            print(f'Betfair error (_aping): {e}')

        return {}

    @staticmethod
    def _payload(name: str, params, **kwargs) -> bytes:
        params = reduce(update_dict, [p.value() for p in params], {})  # tuple into dict
        doc = dict(jsonrpc='2.0', method='SportsAPING/v1.0/' + name, params=params)
        doc.update(kwargs)
        return dumps(doc).encode('utf-8')

    @staticmethod
    def _result(doc: dict) -> list:
        try:
            return doc['result']
        except KeyError as e:
            print('Betfair key result missing', doc['error'])
        except Exception as e:
            print(f'Betfair error (_result) {e}')
        return []

    # def event_types(self, *params):
    #     payload = self._payload('listEventTypes', params)
    #     doc = self._aping(payload)
    #     for item in self._result(doc):
    #         yield item

    def competitions(self, *params):
        """
        :Example:

        b'{
        "jsonrpc": "2.0",
        "method": "SportsAPING/v1.0/listCompetitions",
        "params": {
            "filter": {
                "eventTypeIds": [
                    1
                ],
                "marketTypeCodes": [
                    "MATCH_ODDS",
                    "OVER_UNDER_25",
                    "BOTH_TEAMS_TO_SCORE"
                ]
            }
        }
        }'

        :param params:
        :return:
        """
        payload = self._payload('listCompetitions', params)
        doc = self._aping(payload)
        return self._result(doc)

    def market_catalogue(self, *params):
        """
        :Example:

        b'{
        "jsonrpc": "2.0",
        "method": "SportsAPING/v1.0/listMarketCatalogue",
        "params": {
            "filter": {
                "competitionIds": [
                    55,
                    67387,
                    10932509,
                    59
                ],
                "marketTypeCodes": [
                    "MATCH_ODDS",
                    "OVER_UNDER_25",
                    "BOTH_TEAMS_TO_SCORE"
                ]
            },
            "marketProjection": [
                "EVENT",
                "EVENT_TYPE",
                "RUNNER_DESCRIPTION",
                "COMPETITION"
            ],
            "maxResults": 1000
        }
        }'

        """

        payload = self._payload('listMarketCatalogue', params)
        doc = self._aping(payload)
        return self._result(doc)

    def market_book(self, *params):
        """
        :Example:

        b'{
        "jsonrpc": "2.0",
        "method": "SportsAPING/v1.0/listMarketBook",
        "params": {
            "marketIds": [
                "1.187029746",
                "1.187029576",
                "1.187029741",
                "1.187029571",
                "1.187029742",
                "1.187029572",
                "1.187029831",
                "1.187029661",
                "1.187029491",
                "1.187029826",
                "1.187029656"
            ],
            "priceProjection": {
                "priceData": [
                    "EX_BEST_OFFERS",
                    "EX_ALL_OFFERS"
                ]
            }
        }
        }'

        """
        payload = self._payload('listMarketBook', params)
        doc = self._aping(payload)
        return self._result(doc)
