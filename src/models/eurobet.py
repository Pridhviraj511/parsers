from lxml.etree import _Element


class EurobetMarket:
    market_id: int
    market_name: str
    market_state: str
    market_csmf_state: str
    live_state: int
    hn: str
    ht: str
    outcomes: list

    def __init__(self, market_id: int, market_name: str, market_state: str, market_csmf_state: str, live_state: int, hn: str, ht: str):
        self.market_id = market_id
        self.market_name = market_name
        self.market_state = market_state
        self.market_csmf_state = market_csmf_state
        self.live_state = live_state
        self.hn = hn
        self.ht = ht
        self.outcomes = []

    @staticmethod
    def get_from_element(element: _Element):
        result = []
        for m in element.findall('Bf'):
            market = EurobetMarket(
                market_name=m.attrib['ds'],
                market_id=int(m.attrib['cd']),
                hn=m.attrib['hn'] if 'hn' in m.attrib else "",
                ht=m.attrib['ht'] if 'ht' in m.attrib else "",
                market_state=m.attrib['st'],
                market_csmf_state=m.attrib['csmfst'],
                live_state=m.attrib['lv']
            )
            for b in m.findall('Rs'):
                market.outcomes.append(
                    dict(
                        outcome_id=b.attrib['cd'],
                        outcome_name=b.attrib['ds'],
                        outcome_state=b.attrib['st'],
                        outcome_odd=-1.0 if b.attrib['odd'] == '-1' else float(b.attrib['odd']) / 100
                    )
                )
            result.append(market)
        return result
