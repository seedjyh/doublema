# -*- coding: utf-8 -*-
from datetime import datetime

from okex.market import Market
from model import CCY_BTC, BAR_1D, Candlestick


class TestMarket:
    def test_query(self):
        m = Market()
        m.query(ccy=CCY_BTC, bar=BAR_1D, since=datetime(year=2022, month=4, day=3),
                until=datetime(year=2022, month=4, day=4))
        m.query(ccy=CCY_BTC, bar=BAR_1D, since=datetime(year=2022, month=4, day=2),
                until=datetime(year=2022, month=4, day=5))
        res = m.query(ccy=CCY_BTC, bar=BAR_1D, since=datetime(year=2022, month=4, day=1),
                      until=datetime(year=2022, month=4, day=6))
        assert len(res) == 6
        assert res[0].__dict__ == Candlestick(t=datetime(year=2022, month=4, day=1), o=46453.4, h=46707.8, l=44219.6,
                                              c=46529.6).__dict__
        assert res[5].__dict__ == Candlestick(t=datetime(year=2022, month=4, day=6), o=45762.2, h=46190.0, l=43716.8,
                                              c=44166.0).__dict__
