from parsers.feedmakernew import FeedmakerParserNew

if __name__ == '__main__':
    feedmakernew = FeedmakerParserNew()

    while True:
        feedmakernew.handle()
