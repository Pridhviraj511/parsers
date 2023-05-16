"""
This file contains additional info for markets, names, ids, outcomes, etc. for each feed we use.
"""


def get_position_universal(inverted=False):
    return {
        1: {
            10: {"1": 1 if not inverted else 3,
                 "2": 3 if not inverted else 1,
                 "X": 2,
                 "outcomes": 3,
                 "market_id": 1,
                 "market_name": "1X2"
                 },
            "1X2": {
                "market_id": 10
            },
            43: {
                "Yes": 2,
                "No": 3,
                "outcomes": 2,
                "market_id": 9,
                "market_name": "BTTS"
            },
            "BTTS": {
                "market_id": 43
            },
            60: {
                "Under": 3,
                "Over": 2,
                "outcomes": 2,
                "market_id": 2,
                "market_name": "O/U"
            },
            "O/U": {
                "market_id": 60
            }
        },
        2: {
            20: {"1": 1 if not inverted else 2,
                 "2": 2 if not inverted else 1,
                 "outcomes": 2,
                 "market_id": 3,
                 "market_name": "H/H"
                 },
            "H/H": {
                "market_id": 20
            },
            51: {"1": 1 if not inverted else 2,
                 "2": 2 if not inverted else 1,
                 "outcomes": 2,
                 "market_id": 6,
                 "market_name": "HND"
                 },
            "HND": {
                "market_id": 51
            },
            60: {
                "Under": 2,
                "Over": 1,
                "outcomes": 2,
                "market_id": 5,
                "market_name": "O/U"
            },
            "O/U": {
                "market_id": 60
            }
        },
        5: {
            20: {"1": 1 if not inverted else 2,
                 "2": 2 if not inverted else 1,
                 "outcomes": 2,
                 "market_id": 4,
                 "market_name": "H/H"
                 },
            "H/H": {
                "market_id": 20
            },
            51: {"1": 1 if not inverted else 2,
                 "2": 2 if not inverted else 1,
                 "outcomes": 2,
                 "market_id": 8,
                 "market_name": "HND"
                 },
            "HND": {
                "market_id": 51
            },
            226: {
                "Under": 2,
                "Over": 1,
                "outcomes": 2,
                "market_id": 7,
                "market_name": "O/U"
            },
            "O/U": {
                "market_id": 226
            }
        }}


def get_position_eurobet():
    return {
        1: {
            3: {1: "1",
                3: "2",
                2: "X",
                "outcomes": 3,
                "market_id": 1,
                "br_market_id": 10,
                "market_name": "1X2"
                },
            1128: {
                1: "UNDER",
                2: "OVER",
                "outcomes": 2,
                "market_id": 2,
                "br_market_id": 60,
                "market_name": "O/U"
            },
            18: {
                1: "YES",
                2: "NO",
                "outcomes": 2,
                "market_id": 9,
                "br_market_id": 43,
                "market_name": "BTTS"
            }
        },
        2: {
            110: {1: "1",
                  2: "2",
                  "outcomes": 2,
                  "market_id": 3,
                  "br_market_id": 20,
                  "market_name": "H/H"
                  },
            26: {1: "1",
                 2: "2",
                 "outcomes": 2,
                 "market_id": 6,
                 "br_market_id": 51,
                 "market_name": "HND"
                 },
            14863: {
                2: "UNDER",
                1: "OVER",
                "outcomes": 2,
                "market_id": 5,
                "br_market_id": 60,
                "market_name": "O/U"
            }
        },
        5: {
            2: {1: "1",
                2: "2",
                "outcomes": 2,
                "market_id": 4,
                "br_market_id": 20,
                "market_name": "H/H"
                },
            1127: {1: "1",
                   2: "2",
                   "outcomes": 2,
                   "market_id": 8,
                   "br_market_id": 51,
                   "market_name": "HND"
                   },
            983: {
                2: "UNDER",
                1: "OVER",
                "outcomes": 2,
                "market_id": 7,
                "br_market_id": 226,
                "market_name": "O/U"
            }
        },
        3: {  # za neke eb da ne konvertujem
            2: {1: "1",
                2: "2",
                "outcomes": 2,
                "market_id": 4,
                "br_market_id": 20,
                "market_name": "H/H"
                },
            1127: {1: "1",
                   2: "2",
                   "outcomes": 2,
                   "market_id": 8,
                   "br_market_id": 51,
                   "market_name": "HND"
                   },
            983: {
                2: "UNDER",
                1: "OVER",
                "outcomes": 2,
                "market_id": 7,
                "br_market_id": 226,
                "market_name": "O/U"
            }
        },
        "markets": {
            3: {1: "1",
                3: "2",
                2: "X",
                "outcomes": 3,
                "market_id": 1,
                "br_market_id": 10,
                "market_name": "1X2"
                },
            1128: {
                3: "UNDER",
                2: "OVER",
                "outcomes": 2,
                "market_id": 2,
                "br_market_id": 60,
                "market_name": "O/U"
            },
            18: {
                2: "GOAL",
                3: "NOGOAL",
                "outcomes": 2,
                "market_id": 9,
                "br_market_id": 43,
                "market_name": "BTTS"
            },
            110: {1: "1",
                  2: "2",
                  "outcomes": 2,
                  "market_id": 3,
                  "br_market_id": 20,
                  "market_name": "H/H"
                  },
            26: {1: "1",
                 2: "2",
                 "outcomes": 2,
                 "market_id": 6,
                 "br_market_id": 51,
                 "market_name": "HND"
                 },
            14863: {
                2: "UNDER",
                1: "OVER",
                "outcomes": 2,
                "market_id": 5,
                "br_market_id": 60,
                "market_name": "O/U"
            },
            2: {1: "1",
                2: "2",
                "outcomes": 2,
                "market_id": 4,
                "br_market_id": 20,
                "market_name": "H/H"
                },
            1127: {1: "1",
                   2: "2",
                   "outcomes": 2,
                   "market_id": 8,
                   "br_market_id": 51,
                   "market_name": "HND"
                   },
            983: {
                2: "UNDER",
                1: "OVER",
                "outcomes": 2,
                "market_id": 7,
                "br_market_id": 226,
                "market_name": "O/U"
            }
        }
    }


def get_position_pinnacle(inverted=False):
    return {1: {
        "1X2": {"1": 1 if not inverted else 3,
                "2": 3 if not inverted else 1,
                "X": 2,
                "outcomes": 3,
                "market_id": 1,
                "br_market_id": 10,
                "market_name": "1X2"
                },
        "Over/Under 2.5": {
            "Under": 3,
            "Over": 2,
            "outcomes": 2,
            "market_id": 2,
            "br_market_id": 60,
            "market_name": "O/U"
        }
    },
        2: {
            "12": {"1": 1 if not inverted else 2,
                   "2": 2 if not inverted else 1,
                   "outcomes": 2,
                   "market_id": 3,
                   "br_market_id": 20,
                   "market_name": "H/H"
                   },
            "PointsSpreads": {"Home": 1 if not inverted else 2,
                              "Away": 2 if not inverted else 1,
                              "outcomes": 2,
                              "market_id": 6,
                              "br_market_id": 51,
                              "market_name": "HND"
                              },
            "Total": {
                "Under": 2,
                "Over": 1,
                "outcomes": 2,
                "market_id": 5,
                "br_market_id": 60,
                "market_name": "O/U"
            }
        },
        5: { # What is this 5
            "12": {"1": 1 if not inverted else 2,
                   "2": 2 if not inverted else 1,
                   "outcomes": 2,
                   "market_id": 4,
                   "br_market_id": 20,
                   "market_name": "H/H"
                   },
            "PointsSpreads": {"Home": 1 if not inverted else 2,
                              "Away": 2 if not inverted else 1,
                              "outcomes": 2,
                              "market_id": 8,
                              "br_market_id": 51,
                              "market_name": "HND"
                              },
            "Total": {
                "Under": 2,
                "Over": 1,
                "outcomes": 2,
                "market_id": 7,
                "br_market_id": 226,
                "market_name": "O/U"
            }
        }}


def get_position_goldbet(inverted=False):
    return {
        1: {
            "1x2": {"one": 1 if not inverted else 3,
                    "two": 3 if not inverted else 1,
                    "x": 2,
                    "outcomes": 3,
                    "market_id": 1,
                    "br_market_id": 10,
                    "market_name": "1X2"
                    },
            "ou": {"under": 3,
                   "over": 2,
                   "outcomes": 2,
                   "market_id": 2,
                   "br_market_id": 60,
                   "market_name": "O/U"
                   },
            "gg_ng": {"gg": 2,
                      "ng": 3,
                      "outcomes": 2,
                      "market_id": 9,
                      "br_market_id": 43,
                      "market_name": "BTTS"
                      },
            1: {"one": 1 if not inverted else 3,
                "two": 3 if not inverted else 1,
                "x": 2,
                "outcomes": 3,
                "market_id": 1,
                "br_market_id": 10,
                "market_name": "1X2"
                },
            2: {"under": 3,
                "over": 2,
                "outcomes": 2,
                "market_id": 2,
                "br_market_id": 60,
                "market_name": "O/U"
                },
            9: {"gg": 2,
                "ng": 3,
                "outcomes": 2,
                "market_id": 9,
                "br_market_id": 43,
                "market_name": "BTTS"
                }
        },
        2: {
            "12": {"one": 1 if not inverted else 2,
                   "two": 2 if not inverted else 1,
                   "outcomes": 2,
                   "market_id": 3,
                   "br_market_id": 20,
                   "market_name": "H/H"
                   },
            "hcp": {"one": 1 if not inverted else 2,
                    "two": 2 if not inverted else 1,
                    "market_id": 6,
                    "outcomes": 2,
                    "br_market_id": 51,
                    "market_name": "HND"
                    },
            "ou": {"under": 2,
                   "over": 1,
                   "outcomes": 2,
                   "market_id": 5,
                   "br_market_id": 60,
                   "market_name": "O/U"
                   },
            3: {"one": 1 if not inverted else 2,
                "two": 2 if not inverted else 1,
                "outcomes": 2,
                "market_id": 3,
                "br_market_id": 20,
                "market_name": "H/H"
                },
            6: {"one": 1 if not inverted else 2,
                "two": 2 if not inverted else 1,
                "outcomes": 2,
                "market_id": 6,
                "br_market_id": 51,
                "market_name": "HND"
                },
            5: {"under": 2,
                "over": 1,
                "outcomes": 2,
                "market_id": 5,
                "br_market_id": 60,
                "market_name": "O/U"
                }
        },
        5: {
            "12": {"one": 1 if not inverted else 2,
                   "two": 2 if not inverted else 1,
                   "outcomes": 2,
                   "market_id": 4,
                   "br_market_id": 20,
                   "market_name": "H/H"
                   },
            "games_hcp": {"one": 1 if not inverted else 2,
                          "two": 2 if not inverted else 1,
                          "outcomes": 2,
                          "market_id": 8,
                          "br_market_id": 51,
                          "market_name": "HND"
                          },
            "games_ou": {"under": 2,
                         "over": 1,
                         "market_id": 7,
                         "outcomes": 2,
                         "br_market_id": 226,
                         "market_name": "O/U"
                         },
            4: {"one": 1 if not inverted else 2,
                "two": 2 if not inverted else 1,
                "outcomes": 2,
                "market_id": 4,
                "br_market_id": 20,
                "market_name": "H/H"
                },
            8: {"one": 1 if not inverted else 2,
                "two": 2 if not inverted else 1,
                "outcomes": 2,
                "market_id": 8,
                "br_market_id": 51,
                "market_name": "HND"
                },
            7: {"under": 2,
                "over": 1,
                "outcomes": 2,
                "market_id": 7,
                "br_market_id": 226,
                "market_name": "O/U"
                }
        }}


def get_position_crawler(inverted=False):
    return {
        1: {
            "1X2 FINALE": {
                "1": 1 if not inverted else 3,
                "2": 3 if not inverted else 1,
                "X": 2,
                "outcomes": 3,
                "market_id": 1,
                "br_market_id": 10,
                "market_name": "1X2"
            },
            "UNDER/OVER": {
                "UNDER": 3,
                "OVER": 2,
                "outcomes": 2,
                "market_id": 2,
                "br_market_id": 60,
                "market_name": "O/U"
            },
            "GOAL/NOGOAL": {
                "GOAL": 2,
                "NOGOAL": 3,
                "outcomes": 2,
                "market_id": 9,
                "br_market_id": 43,
                "market_name": "BTTS"
            },
            1: {
                "1": 1 if not inverted else 3,
                "2": 3 if not inverted else 1,
                "X": 2,
                "outcomes": 3,
                "market_id": 1,
                "br_market_id": 10,
                "market_name": "1X2"
            },
            2: {
                "UNDER": 3,
                "OVER": 2,
                "outcomes": 2,
                "market_id": 2,
                "br_market_id": 60,
                "market_name": "O/U"
            },
            9: {
                "GOAL": 2,
                "NOGOAL": 3,
                "outcomes": 2,
                "market_id": 9,
                "br_market_id": 43,
                "market_name": "BTTS"
            }
        },
        2: {
            "TESTA A TESTA": {
                "1": 1 if not inverted else 2,
                "2": 2 if not inverted else 11,
                "outcomes": 2,
                "market_id": 3,
                "br_market_id": 20,
                "market_name": "H/H"
            },
            "T/T HANDICAP": {
                "1": 1 if not inverted else 2,
                "2": 2 if not inverted else 1,
                "market_id": 6,
                "outcomes": 2,
                "br_market_id": 51,
                "market_name": "HND"
            },
            "UNDER/OVER": {
                "UNDER": 2,
                "OVER": 1,
                "market_id": 5,
                "br_market_id": 60,
                "market_name": "O/U"
            },
            3: {
                "1": 1 if not inverted else 2,
                "2": 2 if not inverted else 1,
                "outcomes": 2,
                "market_id": 3,
                "br_market_id": 20,
                "market_name": "H/H"
            },
            6: {
                "1": 1 if not inverted else 2,
                "2": 2 if not inverted else 1,
                "market_id": 6,
                "outcomes": 2,
                "br_market_id": 51,
                "market_name": "HND"
            },
            5: {
                "UNDER": 2,
                "OVER": 1,
                "market_id": 5,
                "br_market_id": 60,
                "market_name": "O/U"
            }
        },
        3: {
            "TESTA A TESTA": {
                "1": 1 if not inverted else 2,
                "2": 2 if not inverted else 1,
                "outcomes": 2,
                "market_id": 4,
                "br_market_id": 20,
                "market_name": "H/H"
            },
            "T/T HANDICAP": {
                "1": 1 if not inverted else 2,
                "2": 2 if not inverted else 1,
                "outcomes": 2,
                "market_id": 8,
                "br_market_id": 51,
                "market_name": "HND"
            },
            "UNDER/OVER": {
                "UNDER": 2,
                "OVER": 1,
                "market_id": 7,
                "outcomes": 2,
                "br_market_id": 226,
                "market_name": "O/U"
            },
            4: {
                "1": 1 if not inverted else 2,
                "2": 2 if not inverted else 1,
                "outcomes": 2,
                "market_id": 4,
                "br_market_id": 20,
                "market_name": "H/H"
            },
            8: {
                "1": 1 if not inverted else 2,
                "2": 2 if not inverted else 1,
                "outcomes": 2,
                "market_id": 8,
                "br_market_id": 51,
                "market_name": "HND"
            },
            7: {
                "UNDER": 2,
                "OVER": 1,
                "market_id": 7,
                "outcomes": 2,
                "br_market_id": 226,
                "market_name": "O/U"
            }
        },
        5: {
            "TESTA A TESTA": {
                "1": 1 if not inverted else 2,
                "2": 2 if not inverted else 1,
                "outcomes": 2,
                "market_id": 4,
                "br_market_id": 20,
                "market_name": "H/H"
            },
            "T/T HANDICAP": {
                "1": 1 if not inverted else 2,
                "2": 2 if not inverted else 1,
                "outcomes": 2,
                "market_id": 8,
                "br_market_id": 51,
                "market_name": "HND"
            },
            "UNDER/OVER": {
                "UNDER": 2,
                "OVER": 1,
                "market_id": 7,
                "outcomes": 2,
                "br_market_id": 226,
                "market_name": "O/U"
            },
            4: {
                "1": 1 if not inverted else 2,
                "2": 2 if not inverted else 1,
                "outcomes": 2,
                "market_id": 4,
                "br_market_id": 20,
                "market_name": "H/H"
            },
            8: {
                "1": 1 if not inverted else 2,
                "2": 2 if not inverted else 1,
                "outcomes": 2,
                "market_id": 8,
                "br_market_id": 51,
                "market_name": "HND"
            },
            7: {
                "UNDER": 2,
                "OVER": 1,
                "market_id": 7,
                "outcomes": 2,
                "br_market_id": 226,
                "market_name": "O/U"
            }
        }}

def get_position_feedmakernew(inverted=False):

    return {
        1: {
            1: { "1": 1 if not inverted else 3,
                 "2": 3 if not inverted else 1,
                 "X": 2,
                 "outcomes": 3,
                 "market_id": 1,
                 "market_name": "1X2"
                 },
            "1X2": {
                "market_id": 1
            },
            18: {

                "Over": 12,
                "Under": 13,
                "outcomes": 2,
                "market_id": 18,
                "market_name": "O/U"
            },
            "Totals": {
                "market_id": 18
            },

            29 : {
                "Yes": 74,
                "No": 76,
                "outcomes": 2,
                "market_id": 29,
                "market_name": "BTTS"
            },
            "BTTS": {
                "market_id": 29
            },

        166 : {
                "Over": 12,
                "Under": 13,
                "outcomes": 2,
                "market_id": 166,
                "market_name": "Corner Totals"
             },
            "Corner Totals": {
                "market_id": 166
            },

        165 : {
                "1": 1714,
                "2": 1715,
                "outcomes": 2,
                "market_id": 165,
                "market_name": "Corner HH"
            },
            "Corner HH": {
                "market_id": 165
            }
        },
        2: {
            219: {"1": 4 if not inverted else 5,
                  "2": 5 if not inverted else 4,
                  "outcomes": 2,
                  "market_id": 219,
                  "market_name": "H/H"
                 },
             "H/H": {
                 "market_id": 219
            },
            223: {"1": 1714 if not inverted else 1715,
                  "2": 1715 if not inverted else 1714,
                  "outcomes": 2,
                  "market_id": 223,
                  "market_name": "HND"
                 },
             "HND": {
                 "market_id": 223
            },
            225: {
                "Under": 13,
                "Over": 12,
                "outcomes": 2,
                "market_id": 225,
                "market_name": "O/U"
            },
            "O/U": {
                "market_id": 225
            }
        },
        5: {
            186: {"1": 4 if not inverted else 5,
                  "2": 5 if not inverted else 4,
                  "outcomes": 2,
                  "market_id": 186,
                  "market_name": "H/H"
                 },
             "H/H": {
                 "market_id": 186
            },
            187: {"1": 1714 if not inverted else 1715,
                  "2": 1715 if not inverted else 1714,
                  "outcomes": 2,
                  "market_id": 187,
                  "market_name": "HND"
                 },
             "HND": {
                "market_id": 187
            },
            189: {
                 "Under": 13,
                 "Over": 12,
                 "outcomes": 2,
                 "market_id": 189,
                 "market_name": "O/U"
            },
             "O/U": {
                 "market_id": 189
            }
        },
        4: {
            1: {"1": 1 if not inverted else 3,
                "2": 3 if not inverted else 1,
                "X": 2,
                "outcomes": 3,
                "market_id": 1,
                "market_name": "1X2"
                },
            "1X2": {
                "market_id": 4
            },
            18: {

                "Over": 12,
                "Under": 13,
                "outcomes": 2,
                "market_id": 18,
                "market_name": "O/U"
            },
            "Totals": {
                "market_id": 18
            }
            },
        6: {
            1: {"1": 1 if not inverted else 3,
                "2": 3 if not inverted else 1,
                "X": 2,
                "outcomes": 3,
                "market_id": 1,
                "market_name": "1X2"
                },
            "1X2": {
                "market_id": 4
            },
            18: {

                "Over": 12,
                "Under": 13,
                "outcomes": 2,
                "market_id": 18,
                "market_name": "O/U"
            },
            "Totals": {
                "market_id": 18
            },
            16: {

                "1": 1714 if not inverted else 1715,
                "2": 1715 if not inverted else 1714,
                "outcomes": 2,
                "market_id": 16,
                "market_name": "HND"
            },
            "HND": {
                "market_id": 16
            }
        },
        23: {
            186: {
                 "1": 4 if not inverted else 5,
                 "2": 5 if not inverted else 4,
                 "outcomes": 2,
                 "market_id": 186,
                 "market_name": "H/H"
                 },
            "H/H": {
                "market_id": 186
            },
            238: {
                 "Under": 13,
                 "Over": 12,
                 "outcomes": 2,
                 "market_id": 238,
                 "market_name": "O/U"
            },
             "O/U": {
                 "market_id": 238
            },
            237: {
                "1": 1714 if not inverted else 1715,
                "2": 1715 if not inverted else 1714,
                "outcomes": 2,
                "market_id": 237,
                "market_name": "HND"
            },
            "HND": {
                "market_id": 237
            },

            12: {
                1: {"1": 1 if not inverted else 3,
                    "2": 3 if not inverted else 1,
                    "X": 2,
                    "outcomes": 3,
                    "market_id": 1,
                    "market_name": "1X2"
                    },
                "1X2": {
                    "market_id": 1
                },
                18: {

                    "Over": 12,
                    "Under": 13,
                    "outcomes": 2,
                    "market_id": 18,
                    "market_name": "O/U"
                },
                "Totals": {
                    "market_id": 18
                },

                16:{
                "1": 1714 if not inverted else 1715,
                "2": 1715 if not inverted else 1714,
                "outcomes": 2,
                "market_id": 16,
                "market_name": "HND"
            },
            "HND": {
                "market_id": 16
            }
    } }
    }



if __name__ == '__main__':
    pos = get_position_universal()
    print(pos.get(5, {}).get(20, {}).get('2', None))
