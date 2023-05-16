from threading import Thread

from parsers.eurobet import EurobetParser

if __name__ == '__main__':
    parser = EurobetParser()

    valid = False
    while not valid:
        valid = parser.get_all_events()

    parser.handle()
