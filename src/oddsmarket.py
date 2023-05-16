from parsers.oddsmarket import OddsMarket

if __name__ == "__main__":
    odds_market = OddsMarket()
    
    while True:
        odds_market.handle()