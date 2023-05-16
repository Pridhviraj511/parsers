from datetime import datetime
from typing import Generator, Tuple, Union

from lxml import etree
from lxml.etree import _Element
from pytz import utc, AmbiguousTimeError


class Betradar:

    @staticmethod
    def parse_xml(obj, path: str) -> Union[list, Generator]:
        """
        Incremental parsing of huge xml files.

        :param obj: Object we parse.
        :param path: Path to the tag we need, eg. 'Sports/Sport/Category/Tournament/Match'
        :return: All match tags.
        """

        try:
            path_parts = path.split('/')
            doc = etree.iterparse(obj, ('start', 'end'))
            try:
                next(doc)
            except etree.XMLSyntaxError as e:
                print(f'Parse_and_remove error: No element found in message {e}')
                return []

            elem_stack = []
            tag_stack = []
            try:
                for event, elem in doc:
                    try:
                        if event == 'start':
                            elem_stack.append(elem)
                            tag_stack.append(etree.QName(elem.tag).localname)
                        elif event == 'end':
                            if path_parts == tag_stack:
                                yield elem
                                elem_stack[-2].remove(elem)
                            try:
                                elem_stack.pop()
                                tag_stack.pop()
                            except IndexError:
                                pass
                    except Exception as e:
                        print('Parse_and_remove error 3:', e, str(tag_stack))
            except Exception as e:
                print('Parse_and_remove error 2:', e, str(doc))
        except Exception as e:
            print('Parse_and_remove error:', e, str(obj), path)

    @staticmethod
    def get_translations(items, competitors: bool = False) -> Tuple[str, dict]:
        """
        Parse the tag "Texts/Text" and returns the "BET" name of the item, and a dictionary with all other translations.

        :param competitors: If True then go trough 'Text' tag, else 'Texts/Text'.
        :param items: The tag we are parsing.
        :return: Returns main name and all translations.
        """

        name, translations = '', {}

        for item in items.findall('Text') if competitors else items.findall('Texts/Text'):
            lang = item.attrib.get('Language', None)
            if lang:
                translation = item.find('Value').text
                if lang == 'BET':
                    name = translation
                translations.update({lang: translation})

        return name, translations

    @staticmethod
    def get_date(date: str, timezone) -> datetime:
        """
        This function converts the date from the feed to the date in UTC, so we can store it in a database.

          :param date: The date we are converting. # '2021-09-02T11:00:00'
          :param timezone: The time zone from which we convert to UTC. For example. Europe / Rome # (+2)
                           type: 'pytz.tzfile.Europe/Rome'
          :return: Returns the date in UTC. # '2021-09-02T09:00:00+0000'
        """

        start_date_feed = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')  # 2021-09-02 11:00:00
        try:
            start_date_utc = timezone.localize(start_date_feed, is_dst=None).astimezone(utc)  # 2021-09-02 09:00:00+00:00
        except AmbiguousTimeError:
            print("Ambiguous Time Error")
            start_date_utc = timezone.localize(start_date_feed, is_dst=True).astimezone(utc)

        return start_date_utc

    @staticmethod
    def get_markets_from_event(match_odds: _Element) -> dict:
        """
        This parses the element and get the markets we need.

        :param match_odds: The element we parse.
        :return: Dictionary of the markets.
        """

        markets_d = {}

        if match_odds is not None:
            for market in match_odds.findall('Bet'):
                try:
                    odds_type = int(market.attrib.get('OddsType', 0))
                    if odds_type in {10, 20, 43, 60, 51, 226}:
                        markets_d[odds_type] = {
                            'market_name': market.attrib.get('OddsName', ''),
                            'market_id': odds_type,
                            'flagged': market.attrib.get('Flagged', ''),
                            'outcomes': defaultdict(dict)
                        }
                        for outcome in market.findall('Odds'):
                            sbv = outcome.attrib.get('SpecialBetValue', '#')

                            if outcome.text:
                                outcome_name = outcome.attrib['OutCome']

                                if outcome_name == '-1' or outcome.text == 'OFF':
                                    continue

                                o = dict(odd=float(outcome.text),
                                         original_odd=float(outcome.attrib.get('OriginalValue', 0)))
                                markets_d[odds_type]['outcomes'][sbv].update({outcome_name: o})
                except Exception as e:
                    print(f'universal error (get_markets_from_event): {e}')

        return markets_d

    @staticmethod
    def get_markets_from_outcome(outright_odds: _Element) -> dict:
        """
        This parses the element and get the markets we need.

        :param outright_odds: The element we parse.
        :return: Dictionary of the markets.
        """

        markets_dict = {}

        if outright_odds is not None:
            odds = outright_odds.findall('Odds')
            odds_type = int(outright_odds.attrib.get('OddsType', 0))
            for item in odds:
                try:
                    # if odds_type not in {10, 20, 43, 60, 51, 226}:  # TODO check if we need all?
                    #     continue
                    if item.text:
                        # TODO check this, sometimes ID is missing, sometimes OutCome
                        outcome_id = item.attrib.get('ID')
                        outcome_name = item.attrib.get('OutCome')
                        odd = item.text
                        if outcome_name == '-1' or odd == 'OFF':  # check if this is needed
                            continue
                        markets_dict[odds_type] = {
                            outcome_name: odd,  # or outcome_id: odd,..or somehow
                        }
                except Exception as e:
                    print(f'universal error (get_markets_from_outcome): {e}')

        return markets_dict

    @staticmethod
    def get_competitors(comps: list) -> Tuple[_Element, _Element]:
        """
        This function gets competitors from the tag and rotates them if needed.

        :param comps: List of elements.
        :return: Returns home and away in the right order.
        """

        home, away = comps
        if home.attrib['Type'] == '2':
            print('rotating competitors')
            away, home = comps

        return home, away

    @staticmethod
    def get_bool_from_value(tag: _Element, value: str) -> bool:
        """
        Checking if an element exists and if exists it gets the value and compares to the expected value and
        returns True if they match.

        :param tag: The element we check.
        :param value: Value we expect to return True.
        :return: Returns True or False.
        """

        return bool(tag is not None and tag.text == value)

    def get_result(results: list) -> dict:
        """
        Gets the result when event is finished.

        :param results: The tag from where we get results.
        :return: Returns a dictionary of results we need. # {'C': 'Cancelled', 'Set1': '6:2', 'Set2': '4:0', 'WO': '403329'}
        """
        r = {}

        for item in results:
            t = item.attrib['Type']
            if t in ('HT', 'FT'):
                r.update({t: item.text})

        return r
