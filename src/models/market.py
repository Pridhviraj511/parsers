class Market:

    @staticmethod
    def get_market_by_sport(sport_id: int) -> dict:
        """
        Return markets dict according the sport id in input

        :param sport_id: A sport for which we create markets.
        :return: Dictionary with all the markets we use for certain sport.

        """

        if sport_id == 1:  # soccer
            return {
                '1X2': {},
                'O/U': {},
                'BTTS': {},
                'Corner Totals': {},
                'Corner HH': {}
            }

        elif sport_id in {2, 5, 23}:  # basketball, tennis and volleyball
            return {
                'H/H': {},
                'O/U': {},
                'HND': {},
                'O/U 1HT': {}

            }
        elif sport_id == 4:
            return {
                '1X2': {},
                'O/U': {}
            }
        elif sport_id == 6:
            return {
                '1X2': {},
                'O/U': {},
                'HND': {},
            }


        else:
            return {}
