from parsers.scomesseitalia import ScomesseitaliaParser

if __name__ == '__main__':
    scomesseitalia = ScomesseitaliaParser()

    while True:
        scomesseitalia.handle()
