from parsers.goldbet import GoldbetParser

if __name__ == '__main__':

    gb = GoldbetParser()

    while True:
        gb.handle()
