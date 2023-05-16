from parsers.vincitu import VincituParser

if __name__ == '__main__':
    vincitu = VincituParser()

    while True:
        vincitu.handle()
