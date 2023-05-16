def to_camel_case(snake_str):
    components = snake_str.split('_')
    # We capitalize the first letter of each component except the first one
    # with the 'title' method and join them together.
    return components[0] + ''.join(x.title() for x in components[1:])


def calculate_mainline(odds):
    main_lines = {}
    for market_id, market in odds.items():
        for spread, sbv in market.items():
            if not isinstance(sbv, dict):
                continue
            if "status" in sbv:
                sbv.pop("status")
            markets = list(sbv.values())
            if len(markets) not in [2, 3]:
                continue

            val = 0
            if len(markets) == 2:
                val = abs(markets[0]['odd'] - markets[1]['odd'])
            elif len(markets) == 3:
                val = min(abs(markets[0]['odd'] - markets[1]['odd']),
                          abs(markets[1]['odd'] - markets[2]['odd']),
                          abs(markets[2]['odd'] - markets[0]['odd']))

            if market_id not in main_lines or val < main_lines[market_id]['val']:
                main_lines[market_id] = {'val': val, 'sbv': spread.replace(',', '.')}

    result = {}
    for k in main_lines:
        result[k] = main_lines[k]['sbv']

    return result
