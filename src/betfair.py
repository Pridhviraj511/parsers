from parsers.betfair import BetfairParser

if __name__ == '__main__':

    betfair = BetfairParser()

    while True:
        betfair.handle()
