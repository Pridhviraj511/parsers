from parsers.pinnacle import PinnacleParser

if __name__ == '__main__':

    pinnacle = PinnacleParser()

    while True:
        pinnacle.handle()
