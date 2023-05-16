from parsers.pinnacle2 import PinnacleParser

if __name__ == "__main__":
    pinnacle_parser = PinnacleParser()

    while True:
        pinnacle_parser.handle()