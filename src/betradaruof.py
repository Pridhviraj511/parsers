from parsers.betradar_uof import BetradarUOFParser



if __name__ == '__main__':

    betradar_uof = BetradarUOFParser()

    while True:
        betradar_uof.handle()
