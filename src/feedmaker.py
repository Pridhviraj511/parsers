from parsers.feedmaker import FeedmakerParser

if __name__ == '__main__':
    feedmaker = FeedmakerParser()

    while True:
        feedmaker.handle()
