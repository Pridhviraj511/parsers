from parsers.betium import BetiumParser

if __name__ == '__main__':
    betium = BetiumParser()

    while True:
        betium.handle()
