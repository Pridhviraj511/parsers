import os
from datetime import datetime
from io import BytesIO
from typing import Union, Generator, Tuple

from lxml.etree import Element
from pytz import timezone
from requests import get

from models.betradar import Betradar
from models.event import Event
from models.market import Market
from models.variation import Variations, Variation
from parsers import ApiParser
from utils.position import get_position_universal

MIN_TIME = int(os.getenv('min_time', 200))
ALERT_TIME = int(os.getenv('alert_time', 3600))
QSIZE = int(os.getenv('q_size', 15))


class BetradarParser(ApiParser):

    def __init__(self, bookmaker_id: int, bookmaker_name: str, inverted_direction: int, percentage_limit: float,
                 sports: dict, url: str, sleep: int):
        """ This is the Container class that extends the Bookmaker class and gives us some additional info we need. """

        super().__init__(
            bookmaker_id=bookmaker_id,
            bookmaker_name=bookmaker_name,
            inverted_direction=inverted_direction,
            percentage_limit=percentage_limit,
            url=url,
            sleep=sleep,
            sports=sports
        )

        self.position = get_position_universal()

    def _get_xml(self) -> BytesIO:
        """
        Get an XML data from API response. If no new data, it prints "/", otherwise, it prints timestamp from the file.

        :return: Returns XML data.
        """

        o = BytesIO()
        try:
            username = os.getenv('USERNAME')
            password = os.getenv('PASSWORD')
            delete_after_transfer = os.getenv('DELETE_AFTER_TRANSFER', 'yes')

            _cfg = dict(username=username, password=password, deleteAfterTransfer=delete_after_transfer)

            ddd = datetime.utcnow()
            r = get(url=f'{self.url}/getXmlFeed.php', params=_cfg, timeout=120).content
            o.write(r)
            self.type = self.get_type(r)
            print(f'---> time {datetime.utcnow() - ddd} for _get_xml')

            if r:
                self.date = str(r)[131:150] if self.name in ['testv500'] else str(r)[83:102]

                if "BetData" in self.date:
                    print("/")
                elif self.date:
                    print(self.date)
                    self.is_file = 1
                else:
                    print(r)
            else:
                print("/")

        except Exception as e:
            print(f'_get_xml error: {e}')

        o.seek(0)
        return o

    def get_all_events(self) -> Generator:
        """
        Parsing the events from the update.

        :return: Parsed events with fixtures and odds.
        """
        file_xml = self._get_xml()
        for match in Betradar.parse_xml(file_xml, 'Sports/Sport/Category/Tournament/Match'):
            yield match

    def get_event(self, event: any, last_update: datetime) -> Union[None, Event]:
        """
        This function parses the required data and creates a unique format for storage in MongoDB.
        We also use Redis to get previous odds, so that we can keep only the new ones, and also keep the historical
        odds without duplicates. If necessary - we can set the percentage below we will not accept the changes,
        as there will be a lot of calculations for the weighted average system unnecessarily.

        :param event: This is the event we parse.
        :param last_update: Date and time (UTC) when this event received last time.
        """
        event_id = int(event.attrib.get('BetradarMatchID', event.attrib.get('MatchID')))
        tournament = event.getparent()
        category = tournament.getparent()
        sport = category.getparent()
        sport_id = int(sport.attrib.get('BetradarSportID', sport.attrib.get('SportID')))
        if sport_id not in (1, 2, 5):
            return None

        comps = event.findall('Fixture/Competitors/Texts/Text')
        if len(comps) != 2:
            return None

        home, away = Betradar.get_competitors(comps)
        home_name, home_translations = Betradar.get_translations(home, True)
        away_name, away_translations = Betradar.get_translations(away, True)
        sport_name, sport_translations = Betradar.get_translations(sport, False)

        category_id = int(category.attrib.get('BetradarCategoryID', category.attrib.get('CategoryID')))
        category_name, category_translations = Betradar.get_translations(category, False)

        tournament_id = int(tournament.attrib.get('BetradarTournamentID', tournament.attrib.get('TournamentID')))
        tournament_name, tournament_translations = Betradar.get_translations(tournament, False)

        time_zone = timezone(sport.getparent().getparent().find('Timestamp').attrib['TimeZone'])
        start_date = Betradar.get_date(date=event.find('Fixture/DateInfo/MatchDate').text, timezone=time_zone)

        disable = Betradar.get_bool_from_value(tag=event.find('OfferType/Disable_event'), value='True')
        cancelled = Betradar.get_bool_from_value(tag=event.find('Result/ScoreInfo/Score'), value='Cancelled')

        # TODO: What is this id?
        # None if self.id in (5, 20) else (event.attrib['event_id'] if len(str(event['event_id'])) == 8 else None),

        return Event(
            _id=event_id,
            bookmaker_id=self.id,
            bookmaker_name=self.name,
            date=int(start_date.timestamp()),
            home_id=int(home.attrib['ID'] if self.name.lower() != 'testv500' else home.attrib['SUPERID']),
            home_name=home_name,
            away_id=int(away.attrib['ID'] if self.name.lower() != 'testv500' else away.attrib['SUPERID']),
            away_name=away_name,
            sport_id=sport_id,
            sport_name=sport_name,
            tournament_id=tournament_id,
            tournament_name=tournament_name,
            category_id=category_id,
            category_name=category_name,
            betradar_id=event_id,
            status=disable and cancelled,
            last_update=int(last_update.timestamp()),
        )

    def _get_market_data(self, event: Element):
        return event.find('MatchOdds')

    def get_market(self, event: Event, markets: dict, current_event: Event) -> Tuple[dict, int]:

        """
        This function parses the market received according to our standard format

        :param event: Event that we are parsing.
        :param markets: Market data that we received
        """
        if markets is None:
            return {}, 0

        if current_event is None or current_event.back is None or not len(current_event.back):
            current_odds = Market.get_market_by_sport(event.sport_id)
        else:
            current_odds = current_event.back

        odds = Market.get_market_by_sport(event.sport_id)
        variations = Variations(event)

        for market in markets.findall('Bet'):
            try:

                market_type = int(market.attrib.get('OddsType', 0))

                if (event.sport_id == 1 and market_type in (10, 43, 60)) or (
                        event.sport_id == 2 and market_type in (20, 60, 51)) \
                        or (event.sport_id == 5 and market_type in (20, 226, 51)):

                    market_id = self.position.get(event.sport_id, {}).get(market_type, []).get('market_id', None)
                    market_name = self.position.get(event.sport_id, {}).get(market_type, []).get('market_name', None)

                    odds[market_name]['flagged'] = market.attrib.get('Flagged', '') == 'true'
                    odds[market_name]['marketId'] = market_id
                    for outcome in market.findall('Odds'):

                        sbv = outcome.attrib.get('SpecialBetValue', '#')
                        sbv = self.check_sbv(sbv=sbv, market_id=market_id)

                        outcome_name = outcome.attrib['OutCome']

                        if outcome_name == '-1' or outcome.text == 'OFF':
                            continue

                        odd = float(outcome.text)
                        # odd = self.check_odd(float(outcome.attrib.get('OriginalValue', 0)))
                        if not odd:
                            continue

                        if not market_name or not outcome_name or not sbv:
                            print(f'Error! Market ({market_name}), outcome ({outcome_name}) or sbv ({sbv}) '
                                  f'is missing: {outcome}\n{event}')
                            continue

                        if sbv not in current_odds[market_name]:
                            # only the first odd can be 0, later odds will be just removed
                            current_odds[market_name].update(Event.make_sbv(market=market_name, sbv=sbv, removed=True))
                            prev_odd, prev_last_update, removed = 0, '', True
                        else:
                            prev = current_odds.get(market_name, {}).get(sbv, {}).get(outcome_name,
                                                                                      dict(odd=0, removed=True,
                                                                                           lastUpdate=''))
                            prev_odd, prev_last_update = prev.get('odd', 0), prev.get('lastUpdate', '')
                            removed = prev.get('removed', True)

                        po = 0 if removed else prev_odd

                        if sbv not in odds[market_name]:
                            odds[market_name].update(Event.make_sbv(market=market_name, sbv=sbv))

                        if odd == po:
                            odds[market_name][sbv][outcome_name].update(odd=odd, lastUpdate=prev_last_update)
                        else:
                            key = f'back.{market_name}.{sbv}.{outcome_name}'

                            if not self.percentage_checker(odd=odd, prev_odd=po, key=key):
                                continue

                            if odd != prev_odd:
                                d = dict(odd=odd, removed=False, lastUpdate=str(event.last_update))
                            else:
                                d = dict(odd=odd, removed=False, lastUpdate=prev_last_update)

                            odds[market_name][sbv][outcome_name].update(dict(odd=odd, lastUpdate=event.last_update))
                            current_odds[market_name][sbv][outcome_name].update(d)

                            variations.append(Variation(
                                _id=event.id,
                                bookmaker_name=self.name,
                                sport_id=event.sport_id,
                                market_name=market_name,
                                sbv=sbv,
                                outcome_name=outcome_name,
                                odd=odd,
                                last_update=event.last_update,
                                status=event.status
                            ))

            except Exception as e:
                print(f'get_market error: {e}\n{event}\n{event.__dict__}\n{market}')

        if variations.exists():
            variations.calculate_main_lines(odds)
            self.store_variations(variations=variations)

        return {'back': odds}, variations.exists()

    @staticmethod
    def get_type(text: bytes) -> str:
        """
        This checks the words in the feed and decides which type it is.

        :return: Returns the feed type.
        """

        if text.find(b'<Outright ') != -1:
            return 'outright'
        elif text.find(b'<Match ') != -1:
            return 'event'
        return ''
