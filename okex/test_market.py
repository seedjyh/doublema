# -*- coding: utf-8 -*-
from datetime import datetime

from okex.market import Market
from smarter.market import CCY_BTC, Candlestick


class TestMarket:
    def test_query(self):
        res = Market().query(ccy=CCY_BTC, since=datetime(year=2022, month=4, day=1),
                             until=datetime(year=2022, month=4, day=9))
        assert len(res) == 9
        assert res[0].__dict__ == \
               Candlestick(t=datetime(year=2022, month=4, day=1), o=46453.4, h=46707.8, l=44219.6, c=46529.6).__dict__
        assert res[8].__dict__ == \
               Candlestick(t=datetime(year=2022, month=4, day=9), o=43649.3, h=43716.0, l=42112.0, c=42280.0).__dict__
