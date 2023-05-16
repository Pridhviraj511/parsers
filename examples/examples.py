import datetime

historicals = {'back': {
    "2021-02-13 15:48:00": 2.40,
    "2021-02-13 22:18:00": 2.30,
    "2021-02-14 07:05:00": 2.25,
    "2021-02-14 07:06:00": 2.20,
    "2021-02-14 22:50:00": 2.15,
    "2021-02-15 08:04:00": 2.10,
    "2021-02-15 08:28:00": 2.05,
    "2021-02-15 14:19:00": 2.00,
    "2021-02-16 09:10:00": 2.05,
    "2021-02-16 14:27:00": 2.10,
    "2021-02-17 12:34:00": 2.05,
    "2021-02-17 19:48:00": 2.10,
    "2021-02-18 10:07:00": 2.15,
    "2021-02-18 15:34:00": 2.18,
    "2021-02-18 18:17:00": 2.20,
    "2021-02-19 09:26:00": 2.25,
    "2021-02-19 16:12:00": 2.27,
    "2021-02-20 08:20:00": 2.23,
    "2021-02-20 16:40:00": 2.22,
    "2021-02-21 09:45:00": 2.20,
    "2021-02-21 10:12:00": 2.15,
    "2021-02-21 10:46:00": 2.12,
    "2021-02-21 11:18:00": 2.15,
    "2021-02-21 11:34:00": 2.10,
    "2021-02-21 12:25:00": 2.08,
    "2021-02-21 12:52:00": 2.10,
    "2021-02-21 13:04:00": 2.05,
    "2021-02-21 13:28:00": 2.03,
    "2021-02-21 13:42:00": 2.05,
    "2021-02-21 14:09:00": 2.02,
    "2021-02-21 14:22:00": 2.00,
    "2021-02-21 14:36:00": 2.05,
    "2021-02-21 14:42:00": 2.10,
    "2021-02-21 14:58:00": 2.15
}}

betfair_soccer = {
    "event_id": 30652114,
    "event_name": "Ppj - Finnkurd",
    "start_date": "2022-06-28T17:20:00",
    "sport_id": "1",
    "tournament_id": "5281887",
    "home_id": 10143889,
    "home_name": "PPJ",
    "away_id": 13400300,
    "away_name": "Finnkurd",
    "markets": {
        "1.184849531": {
            "name": "BothteamstoScore",
            "status": "OPEN",
            "back_odds": {
                "30246": {
                    "odd": 1.29,
                    "status": "ACTIVE"
                },
                "110503": {
                    "odd": 1.01,
                    "status": "ACTIVE"
                }
            },
            "lay_odds": {
                "30246": {
                    "odd": 1000.0,
                    "status": "ACTIVE"
                },
                "110503": {
                    "odd": 1000.0,
                    "status": "ACTIVE"
                }
            },
            "back_margin": 1.7652928083506026,
            "lay_margin": 0.002
        },
        "1.184849532": {
            "name": "MatchOdds",
            "status": "OPEN",
            "back_odds": {
                "10143889": {
                    "odd": 2.94,
                    "status": "ACTIVE"
                },
                "13400300": {
                    "odd": 1.65,
                    "status": "ACTIVE"
                },
                "58805": {
                    "odd": 3.95,
                    "status": "ACTIVE"
                }
            },
            "lay_odds": {
                "10143889": {
                    "odd": 7.0,
                    "status": "ACTIVE"
                },
                "13400300": {
                    "odd": 2.34,
                    "status": "ACTIVE"
                },
                "58805": {
                    "odd": 20.0,
                    "status": "ACTIVE"
                }
            },
            "back_margin": 1.1993612174444002,
            "lay_margin": 0.6202075702075702
        },
        "1.184849536": {
            "name": "OverUnder25Goals",
            "status": "OPEN",
            "back_odds": {
                "47972": {
                    "odd": 3.35,
                    "status": "ACTIVE"
                },
                "47973": {
                    "odd": 1.3,
                    "status": "ACTIVE"
                }
            },
            "lay_odds": {
                "47972": {
                    "odd": 4.5,
                    "status": "ACTIVE"
                },
                "47973": {
                    "odd": 1.43,
                    "status": "ACTIVE"
                }
            },
            "back_margin": 1.0677382319173364,
            "lay_margin": 0.9215229215229216
        }
    },
    "tournament_name": "Finnish Kolmonen",
    "category_name": "FIN"
}

betfair_basket = {'event_id': 30893644, 'event_name': 'HydroTruck Radom - Enea Zastal BC Zielona Gora',
                  'start_date': '2021-09-14T15:30:00', 'sport_id': '7522', 'tournament_id': '10537346',
                  'home_id': 25907883, 'home_name': 'HydroTruck Radom', 'away_id': 40695326,
                  'away_name': 'Enea Zastal BC Zielona Gora',
                  'markets': {
                      '1.187543221': {'name': 'Moneyline', 'status': 'OPEN',
                                      'back_odds': {'25907883': {'odd': 4.0, 'status': 'ACTIVE'},
                                                    '40695326': {'odd': 1.21, 'status': 'ACTIVE'}},
                                      'lay_odds': {'25907883': {'odd': 5.8, 'status': 'ACTIVE'},
                                                   '40695326': {'odd': 1.34, 'status': 'ACTIVE'}},
                                      'back_margin': 1.0764462809917354,
                                      'lay_margin': 0.9186824498198661}}, 'tournament_name': 'Polish PLK',
                  'category_name': 'International'}

betfair_tennis = {'event_id': 30894478, 'event_name': 'Castelnuovo - Minda', 'start_date': '2021-09-13T16:57:00',
                  'sport_id': '2', 'tournament_id': '12384546', 'home_id': 9629318, 'home_name': 'Luca Castelnuovo',
                  'away_id': 12023072, 'away_name': 'Hugo Minda',
                  'markets': {
                      '1.187545720': {'name': 'MatchOdds', 'status': 'OPEN',
                                      'back_odds': {'9629318': {'odd': 1.05, 'status': 'ACTIVE'},
                                                    '12023072': {'odd': 8.6, 'status': 'ACTIVE'}},
                                      'lay_odds': {'9629318': {'odd': 1.14, 'status': 'ACTIVE'},
                                                   '12023072': {'odd': 21.0, 'status': 'ACTIVE'}},
                                      'back_margin': 1.0686600221483942,
                                      'lay_margin': 0.9248120300751881}},
                  'tournament_name': 'Quito Challenger 2021',
                  'category_name': 'ECU'}

pinnacle_soccer = {'sport_id': 33,
                   'league_id': 9781,
                   'league_name': 'ATP Challenger Quito - R1',
                   'event_id': 1396395985,
                   'parent_id': None,
                   'start_date': '2021-09-13T19:00:00Z',
                   'home_name': 'Mathieu Perchicot',
                   'away_name': 'Antonio Cayetano March',
                   'live_status': 0,
                   'status': True,
                   'markets': {
                       'H/H': {
                           '#': {'1': {'odd': 1.66, 'lastUpdate': datetime.datetime(2021, 9, 13, 15, 18, 18)},
                                 '2': {'odd': 2.22, 'lastUpdate': datetime.datetime(2021, 9, 13, 15, 18, 18)}}},

                       'O/U': {
                           '21,5': {'Over': {'odd': 1.86, 'lastUpdate': datetime.datetime(2021, 9, 13, 15, 18, 18)},
                                    'Under': {'odd': 1.93, 'lastUpdate': datetime.datetime(2021, 9, 13, 15, 18, 18)}},
                           '20,5': {'Over': {'odd': 1.69, 'lastUpdate': datetime.datetime(2021, 9, 13, 15, 18, 18)},
                                    'Under': {'odd': 2.1, 'lastUpdate': datetime.datetime(2021, 9, 13, 15, 18, 18)}},
                           '21,0': {'Over': {'odd': 1.76, 'lastUpdate': datetime.datetime(2021, 9, 13, 15, 18, 18)},
                                    'Under': {'odd': 2.02, 'lastUpdate': datetime.datetime(2021, 9, 13, 15, 18, 18)}},
                           '22,0': {'Over': {'odd': 2.01, 'lastUpdate': datetime.datetime(2021, 9, 13, 15, 18, 18)},
                                    'Under': {'odd': 1.77, 'lastUpdate': datetime.datetime(2021, 9, 13, 15, 18, 18)}},
                           '22,5': {'Over': {'odd': 2.16, 'lastUpdate': datetime.datetime(2021, 9, 13, 15, 18, 18)},
                                    'Under': {'odd': 1.64, 'lastUpdate': datetime.datetime(2021, 9, 13, 15, 18, 18)}}},

                       'HND': {
                           '-3,0': {'1': {'odd': 2.04, 'lastUpdate': datetime.datetime(2021, 9, 13, 15, 18, 18)},
                                    '2': {'odd': 1.74, 'lastUpdate': datetime.datetime(2021, 9, 13, 15, 18, 18)}},
                           '-2,0': {'1': {'odd': 1.83, 'lastUpdate': datetime.datetime(2021, 9, 13, 15, 18, 18)},
                                    '2': {'odd': 1.95, 'lastUpdate': datetime.datetime(2021, 9, 13, 15, 18, 18)}},
                           '-2,5': {'1': {'odd': 1.91, 'lastUpdate': datetime.datetime(2021, 9, 13, 15, 18, 18)},
                                    '2': {'odd': 1.88, 'lastUpdate': datetime.datetime(2021, 9, 13, 15, 18, 18)}},
                           '-3,5': {'1': {'odd': 2.23, 'lastUpdate': datetime.datetime(2021, 9, 13, 15, 18, 18)},
                                    '2': {'odd': 1.6, 'lastUpdate': datetime.datetime(2021, 9, 13, 15, 18, 18)}},
                           '-4,0': {'1': {'odd': 2.6, 'lastUpdate': datetime.datetime(2021, 9, 13, 15, 18, 18)},
                                    '2': {'odd': 1.4, 'lastUpdate': datetime.datetime(2021, 9, 13, 15, 18, 18)}}}}}

pinnacle_basket = {'sport_id': 4, 'league_id': 460, 'league_name': 'Israel - Cup', 'event_id': 1395965691,
                   'parent_id': None, 'start_date': '2021-09-14T17:00:00Z', 'home_name': 'Hapoel Jerusalem',
                   'away_name': 'Bnei Herzliya', 'live_status': 0, 'status': True,
                   'markets':
                       {'H/H': {
                           '#': {'1': {'odd': 1.3, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)},
                                 '2': {'odd': 3.35, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)}}},

                           'O/U': {
                               '169,5': {'Over': {'odd': 1.9, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)},
                                         'Under': {'odd': 1.84,
                                                   'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)}},
                               '167,0': {'Over': {'odd': 1.67, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)},
                                         'Under': {'odd': 2.12,
                                                   'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)}},
                               '167,5': {'Over': {'odd': 1.71, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)},
                                         'Under': {'odd': 2.06,
                                                   'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)}},
                               '168,0': {'Over': {'odd': 1.75, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)},
                                         'Under': {'odd': 2.01,
                                                   'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)}},
                               '168,5': {'Over': {'odd': 1.79, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)},
                                         'Under': {'odd': 1.95,
                                                   'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)}},
                               '169,0': {'Over': {'odd': 1.85, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)},
                                         'Under': {'odd': 1.89,
                                                   'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)}},
                               '170,0': {'Over': {'odd': 1.96, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)},
                                         'Under': {'odd': 1.79,
                                                   'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)}},
                               '170,5': {'Over': {'odd': 2.02, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)},
                                         'Under': {'odd': 1.74,
                                                   'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)}},
                               '171,0': {'Over': {'odd': 2.08, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)},
                                         'Under': {'odd': 1.7,
                                                   'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)}},
                               '171,5': {'Over': {'odd': 2.13, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)},
                                         'Under': {'odd': 1.67,
                                                   'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)}},
                               '172,0': {'Over': {'odd': 2.19, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)},
                                         'Under': {'odd': 1.63,
                                                   'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)}}},

                           'HND': {
                               '-6,5': {'1': {'odd': 1.82, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)},
                                        '2': {'odd': 1.93, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)}},
                               '-9,0': {'1': {'odd': 2.24, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)},
                                        '2': {'odd': 1.59, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)}},
                               '-8,5': {'1': {'odd': 2.16, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)},
                                        '2': {'odd': 1.63, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)}},
                               '-8,0': {'1': {'odd': 2.07, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)},
                                        '2': {'odd': 1.68, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)}},
                               '-7,5': {'1': {'odd': 1.99, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)},
                                        '2': {'odd': 1.75, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)}},
                               '-7,0': {'1': {'odd': 1.9, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)},
                                        '2': {'odd': 1.83, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)}},
                               '-6,0': {'1': {'odd': 1.74, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)},
                                        '2': {'odd': 2.02, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)}},
                               '-5,5': {'1': {'odd': 1.67, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)},
                                        '2': {'odd': 2.11, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)}},
                               '-5,0': {'1': {'odd': 1.61, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)},
                                        '2': {'odd': 2.2, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)}},
                               '-4,5': {'1': {'odd': 1.56, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)},
                                        '2': {'odd': 2.3, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)}},
                               '-4,0': {'1': {'odd': 1.52, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)},
                                        '2': {'odd': 2.39, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)}}}}}

pinnacle_tennis = {'sport_id': 33, 'league_id': 3240, 'league_name': 'WTA Luxembourg - R1', 'event_id': 1396849692,
                   'parent_id': None, 'start_date': '2021-09-14T08:00:00Z', 'home_name': 'Marketa Vondrousova',
                   'away_name': 'Alison Van Uytvanck', 'live_status': 0, 'status': True,
                   'markets':
                       {'H/H': {
                           '#': {'1': {'odd': 1.43, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)},
                                 '2': {'odd': 3.01, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)}}},

                           'O/U': {
                               '20,5': {'Over': {'odd': 1.92, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)},
                                        'Under': {'odd': 1.9, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)}},
                               '21,5': {'Over': {'odd': 2.14, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)},
                                        'Under': {'odd': 1.72,
                                                  'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)}},
                               '21,0': {'Over': {'odd': 2.04, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)},
                                        'Under': {'odd': 1.8, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)}},
                               '20,0': {'Over': {'odd': 1.8, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)},
                                        'Under': {'odd': 2.03,
                                                  'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)}},
                               '19,5': {'Over': {'odd': 1.7, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)},
                                        'Under': {'odd': 2.18,
                                                  'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)}}},

                           'HND': {
                               '-4,0': {'1': {'odd': 1.92, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)},
                                        '2': {'odd': 1.9, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)}},
                               '-5,0': {'1': {'odd': 2.4, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)},
                                        '2': {'odd': 1.58, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)}},
                               '-4,5': {'1': {'odd': 2.11, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)},
                                        '2': {'odd': 1.74, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)}},
                               '-3,5': {'1': {'odd': 1.76, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)},
                                        '2': {'odd': 2.08, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)}},
                               '-3,0': {'1': {'odd': 1.66, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)},
                                        '2': {'odd': 2.24, 'lastUpdate': datetime.datetime(2021, 9, 13, 16, 11, 2)}}}}}

crawler_soccer = {'date': '2021-09-13T20:30:00.000Z', 'category_name': 'Soccer Category', 'away_name': 'CA San Telmo',
                  'markets': {'1X2 FINALE': {'market_name': '1X2 FINALE', 'market_status': 1,
                                             'outcomes': [{'name': '1', 'sbv': None, 'odd': 2.38},
                                                          {'name': 'X', 'sbv': None, 'odd': 3.1},
                                                          {'name': '2', 'sbv': None, 'odd': 2.8}]},
                              'UNDER/OVER': {'market_name': 'UNDER/OVER', 'market_status': 1,
                                             'outcomes': [{'name': 'OVER', 'sbv': 2.5, 'odd': 2.38},
                                                          {'name': 'UNDER', 'sbv': 2.5, 'odd': 1.55}]},
                              'GOAL/NOGOAL': {'market_name': 'GOAL/NOGOAL', 'market_status': 1,
                                              'outcomes': [{'name': 'GOAL', 'sbv': None, 'odd': 2.1},
                                                           {'name': 'NOGOAL', 'sbv': None, 'odd': 1.73}]}},
                  'category_id': 1,
                  'tournament_id': 57893381, 'refreshDate': '2021-09-13T15:41:27.760Z', 'betradar_id': '29121504',
                  'tournament_name': 'Argentina - Nacional B', 'event_id': 631480576, 'event_status': 1,
                  'home_name': 'All Boys', 'sport_id': 1, 'sport_name': 'SOCCER'}

crawler_basket = {'refreshDate': '2021-09-13T15:31:22.571Z', 'betradar_id': '28807902', 'event_status': 1,
                  'category_id': 2, 'date': '2021-10-21T02:10:00.000Z', 'sport_name': 'BASKET',
                  'markets': {
                      'T/T HANDICAP': {'market_name': 'T/T HANDICAP', 'market_status': 1,
                                       'outcomes': [{'name': '1', 'sbv': 4.5, 'odd': 1.91},
                                                    {'name': '2', 'sbv': 4.5, 'odd': 1.91}]},
                      'UNDER/OVER': {'market_name': 'UNDER/OVER', 'market_status': 1,
                                     'outcomes': [{'name': 'OVER', 'sbv': 220.5, 'odd': 1.42},
                                                  {'name': 'OVER', 'sbv': 221, 'odd': 1.45},
                                                  {'name': 'OVER', 'sbv': 221.5, 'odd': 1.47},
                                                  {'name': 'OVER', 'sbv': 222, 'odd': 1.48},
                                                  {'name': 'OVER', 'sbv': 222.5, 'odd': 1.5},
                                                  {'name': 'OVER', 'sbv': 223, 'odd': 1.53},
                                                  {'name': 'OVER', 'sbv': 223.5, 'odd': 1.56},
                                                  {'name': 'OVER', 'sbv': 224, 'odd': 1.57},
                                                  {'name': 'OVER', 'sbv': 224.5, 'odd': 1.63},
                                                  {'name': 'OVER', 'sbv': 225, 'odd': 1.65},
                                                  {'name': 'OVER', 'sbv': 225.5, 'odd': 1.67},
                                                  {'name': 'OVER', 'sbv': 226, 'odd': 1.69},
                                                  {'name': 'OVER', 'sbv': 226.5, 'odd': 1.71},
                                                  {'name': 'OVER', 'sbv': 227, 'odd': 1.77},
                                                  {'name': 'OVER', 'sbv': 227.5, 'odd': 1.8},
                                                  {'name': 'OVER', 'sbv': 228, 'odd': 1.83},
                                                  {'name': 'OVER', 'sbv': 228.5, 'odd': 1.91},
                                                  {'name': 'UNDER', 'sbv': 220.5, 'odd': 2.7},
                                                  {'name': 'UNDER', 'sbv': 221, 'odd': 2.65},
                                                  {'name': 'UNDER', 'sbv': 221.5, 'odd': 2.6},
                                                  {'name': 'UNDER', 'sbv': 222, 'odd': 2.55},
                                                  {'name': 'UNDER', 'sbv': 222.5, 'odd': 2.5},
                                                  {'name': 'UNDER', 'sbv': 223, 'odd': 2.45},
                                                  {'name': 'UNDER', 'sbv': 223.5, 'odd': 2.4},
                                                  {'name': 'UNDER', 'sbv': 224, 'odd': 2.35},
                                                  {'name': 'UNDER', 'sbv': 224.5, 'odd': 2.3},
                                                  {'name': 'UNDER', 'sbv': 225, 'odd': 2.25},
                                                  {'name': 'UNDER', 'sbv': 225.5, 'odd': 2.2},
                                                  {'name': 'UNDER', 'sbv': 226, 'odd': 2.15},
                                                  {'name': 'UNDER', 'sbv': 226.5, 'odd': 2.1},
                                                  {'name': 'UNDER', 'sbv': 227, 'odd': 2.05},
                                                  {'name': 'UNDER', 'sbv': 227.5, 'odd': 2},
                                                  {'name': 'UNDER', 'sbv': 228, 'odd': 1.95},
                                                  {'name': 'UNDER', 'sbv': 228.5, 'odd': 1.91},
                                                  {'name': 'OVER', 'sbv': 229, 'odd': 1.95},
                                                  {'name': 'OVER', 'sbv': 229.5, 'odd': 2},
                                                  {'name': 'OVER', 'sbv': 230, 'odd': 2.05},
                                                  {'name': 'OVER', 'sbv': 230.5, 'odd': 2.1},
                                                  {'name': 'OVER', 'sbv': 231, 'odd': 2.15},
                                                  {'name': 'OVER', 'sbv': 231.5, 'odd': 2.2},
                                                  {'name': 'OVER', 'sbv': 232, 'odd': 2.25},
                                                  {'name': 'OVER', 'sbv': 232.5, 'odd': 2.3},
                                                  {'name': 'OVER', 'sbv': 233, 'odd': 2.35},
                                                  {'name': 'OVER', 'sbv': 233.5, 'odd': 2.4},
                                                  {'name': 'OVER', 'sbv': 234, 'odd': 2.45},
                                                  {'name': 'OVER', 'sbv': 234.5, 'odd': 2.5},
                                                  {'name': 'OVER', 'sbv': 235, 'odd': 2.55},
                                                  {'name': 'OVER', 'sbv': 235.5, 'odd': 2.6},
                                                  {'name': 'OVER', 'sbv': 236, 'odd': 2.65},
                                                  {'name': 'OVER', 'sbv': 236.5, 'odd': 2.7},
                                                  {'name': 'UNDER', 'sbv': 229, 'odd': 1.83},
                                                  {'name': 'UNDER', 'sbv': 229.5, 'odd': 1.8},
                                                  {'name': 'UNDER', 'sbv': 230, 'odd': 1.77},
                                                  {'name': 'UNDER', 'sbv': 230.5, 'odd': 1.74},
                                                  {'name': 'UNDER', 'sbv': 231, 'odd': 1.71},
                                                  {'name': 'UNDER', 'sbv': 231.5, 'odd': 1.67},
                                                  {'name': 'UNDER', 'sbv': 232, 'odd': 1.65},
                                                  {'name': 'UNDER', 'sbv': 232.5, 'odd': 1.63},
                                                  {'name': 'UNDER', 'sbv': 233, 'odd': 1.57},
                                                  {'name': 'UNDER', 'sbv': 233.5, 'odd': 1.56},
                                                  {'name': 'UNDER', 'sbv': 234, 'odd': 1.53},
                                                  {'name': 'UNDER', 'sbv': 234.5, 'odd': 1.51},
                                                  {'name': 'UNDER', 'sbv': 235, 'odd': 1.5},
                                                  {'name': 'UNDER', 'sbv': 235.5, 'odd': 1.48},
                                                  {'name': 'UNDER', 'sbv': 236, 'odd': 1.45},
                                                  {'name': 'UNDER', 'sbv': 236.5, 'odd': 1.43}]},
                      'TESTA A TESTA': {'market_name': 'TESTA A TESTA', 'market_status': 1,
                                        'outcomes': [{'name': '1', 'sbv': None, 'odd': 2.65},
                                                     {'name': '2', 'sbv': None, 'odd': 1.54}]}},
                  'home_name': 'HOU Rockets',
                  'category_name': 'Basket Category', 'away_name': 'MIN Timberwolves', 'tournament_id': 20604387,
                  'sport_id': 2, 'tournament_name': 'NBA', 'event_id': -397016223}

crawler_tennis = {'home_name': 'L-Montagud/Sureshkumar', 'category_id': 3, 'away_name': 'Ruiz/Mardones',
                  'sport_name': 'TENNIS', 'date': '2021-09-15T13:00:00.000Z', 'category_name': 'Tennis Category',
                  'tournament_id': 20768124, 'refreshDate': '2021-09-13T15:21:32.958Z', 'event_id': -1999144022,
                  'betradar_id': None, 'sport_id': 3,
                  'markets': {
                      'TESTA A TESTA': {'market_name': 'TESTA A TESTA', 'market_status': 1,
                                        'outcomes': [{'name': '1', 'sbv': None, 'odd': 2.25},
                                                     {'name': '2', 'sbv': None, 'odd': 1.57}]}},
                  'event_status': 1,
                  'tournament_name': 'ITF M25 Madrid DM'}

goldbet_soccer = {
    "matchid": "5738305",
    "status": 1,
    "aams": "31371.3243",
    "betradar": "28176304",
    "starttime": "1631645100",
    "country": "Inghilterra",
    "countryid": "3010",
    "liga": "Northern League",
    "lid": "26703",
    "e1": "Matlock Town",
    "e1id": "9707",
    "e2": "Witton Albion",
    "e2id": "61047",
    "1x2": {
        "one": 1.58,
        "x": 3.75,
        "two": 4.75
    },
    "ou": {
        "over": 1.75,
        "under": 1.91
    },
    "dc": {
        "1x": 1.1,
        "12": 1.17,
        "x2": 2.05
    },
    "gg_ng": {
        "gg": 1.71,
        "ng": 1.94
    }
}

goldbet_basket = {
    "matchid": "5742559",
    "status": 1,
    "aams": "31372.31287",
    "betradar": "29172426",
    "starttime": "1631579400",
    "country": "Uruguay",
    "countryid": "20633",
    "liga": "El Metro",
    "lid": "2586187",
    "e1": "CA Cordon",
    "e1id": "642564",
    "e2": "Miramar BBC",
    "e2id": "643019",
    "12": {
        "one": 1.54,
        "two": 2.22
    },
    "hcp": {
        "ps": -3.5,
        "one": 1.82,
        "two": 1.82
    },
    "ou": {
        "ps": 152.5,
        "over": 1.82,
        "under": 1.81
    },
    "other_hcp_lines": [
        {
            "ps": -4.5,
            "one": 1.95,
            "two": 1.7
        },
        {
            "ps": -2.5,
            "one": 1.71,
            "two": 1.94
        }
    ],
    "other_ou_lines": [
        {
            "ps": 151.5,
            "over": 1.74,
            "under": 1.9
        },
        {
            "ps": 153.5,
            "over": 1.91,
            "under": 1.73
        }
    ]
}

goldbet_tennis = {
    "matchid": "5736479",
    "status": 1,
    "aams": "31371.43254",
    "betradar": "29170092",
    "starttime": "1631628000",
    "country": "Challenger",
    "countryid": "8358",
    "liga": "USA",
    "lid": "22312",
    "e1": "Sandgren, Tennys",
    "e1id": "52344",
    "e2": "Eubanks, Christopher",
    "e2id": "54440",
    "12": {
        "one": 1.71,
        "two": 1.98
    },
    "games_hcp": {
        "ps": -1.5,
        "one": 1.86,
        "two": 1.78
    },
    "games_ou": {
        "ps": 22.5,
        "over": 1.87,
        "under": 1.8
    }
}
