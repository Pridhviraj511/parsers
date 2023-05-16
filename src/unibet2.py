from parsers.unibet2 import UnibetParser

if __name__ == "__main__":
    unibet_parser = UnibetParser()

    while True:
        unibet_parser.handle()