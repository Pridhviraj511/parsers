from datetime import datetime
from time import sleep as time_sleep, sleep
from typing import Union, Generator

from requests import get, post, Response

from parsers import Parser


class ApiParser(Parser):

    def __init__(self, bookmaker_id: int, bookmaker_name: str, inverted_direction: int, percentage_limit: float,
                 sports: dict, url: str, sleep: int):
        """
        This class contains common data for all bookmakers.

        :param bookmaker_id: ID of the bookmaker.
        :param bookmaker_name: Bookmaker's name.
        :param url: URL from where we get the feed.
        :param inverted_direction: Is the direction of the SBV in the right order.
        :param sleep: Seconds to sleep between getting feed.
        :param percentage_limit: The upper limit of the percentage for the acceptance of new odds.
        """
        super().__init__(bookmaker_id, bookmaker_name, inverted_direction, percentage_limit)
        self.url = url
        self.sleep = sleep
        self.sports = sports

    def call_api(self, url: str, headers: dict, data: dict, func_name: str, timeout: int = 120,
                 get_method: bool = True, to_print: bool = True) -> Union[Response, str]:
        """
        Function with all the data we may need for an API call.

        :param url: URL from which we get the feed.
        :param headers: Dictionary of HTTP Headers if they are required.
        :param data: The data to send in the body if needed.
        :param func_name: Name of the function from which we are calling the API.
        :param timeout: How many seconds to wait for the server to send data before giving up.
        :param get_method: If True then method is GET, else POST.
        :param to_print: If True it will print the duration of the API call.
        :return: Returns an API response.
        """

        # TODO maybe add json, params, auth...
        for _ in range(3):
            try:
                ddd = datetime.utcnow()
                if get_method:
                    resp = get(url=url, headers=headers, data=data, timeout=timeout)
                else:
                    resp = post(url=url, headers=headers, data=data, timeout=timeout)

                if to_print:
                    print(f'---> time {datetime.utcnow() - ddd} for {func_name}')

                if resp.status_code != 200:
                    print(f'{func_name} for status code is: {resp.status_code}')

                return resp

            except Exception as e:
                print(f'call_api: {url}, {func_name}, error{e}')

            time_sleep(3)

        print(f'{url}, {func_name} is not available..')
        return ''

    def get_all_events(self) -> Generator:
        """
        Calling the API to collect data of event changes
        """
        pass

    def handle(self):
        """
        This function goes through events, calls functions to process them and later stores.
        :return: void
        """

        received = 0
        processed = 0

        last_update = datetime.utcnow()
        print(f'Control date: {last_update}')
        print(f'Start loading updates')

        for update in self.get_all_events():
            received += 1
            if self.handle_event(update, last_update):
                processed += 1

        print(f'{processed} updates processed on {received} received')
        print(f'---> time for processing {received} events', datetime.utcnow() - last_update)
        self.heartbeat()

        sleep(self.sleep)
