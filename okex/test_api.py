# -*- coding: utf-8 -*-
from datetime import datetime

from model import CCY_BTC, Candlestick, BAR_1D
from okex._api import query


def test_query():
    res = query(
        ccy=CCY_BTC, bar=BAR_1D,
        since=datetime(year=2022, month=4, day=1, hour=0, minute=0, second=0),
        until=datetime(year=2022, month=4, day=10, hour=0, minute=0, second=0),
    )
    assert len(res) == 9
    assert res[0].__dict__ == Candlestick(t=datetime(year=2022, month=4, day=1), o=46453.4,
                                          h=46707.8, l=44219.6, c=46529.6).__dict__
    assert res[8].__dict__ == Candlestick(t=datetime(year=2022, month=4, day=9), o=43649.3,
                                          h=43716.0, l=42112.0, c=42280.0).__dict__


def test_query_partial():
    res = query(
        ccy=CCY_BTC, bar=BAR_1D,
        since=datetime(year=2022, month=3, day=31, hour=12, minute=0, second=0),
        until=datetime(year=2022, month=4, day=9, hour=12, minute=0, second=0),
    )
    assert len(res) == 9
    assert res[0].__dict__ == Candlestick(t=datetime(year=2022, month=4, day=1), o=46453.4,
                                          h=46707.8, l=44219.6, c=46529.6).__dict__
    assert res[8].__dict__ == Candlestick(t=datetime(year=2022, month=4, day=9), o=43649.3,
                                          h=43716.0, l=42112.0, c=42280.0).__dict__
