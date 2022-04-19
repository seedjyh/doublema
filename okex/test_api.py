# -*- coding: utf-8 -*-
import logging
from datetime import datetime

from model import Candlestick, Trade
from const import BAR_1D, CCY_BTC
from okex._api import query_market_candles, query_trade_fills

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def test_query_market_candles():
    res = query_market_candles(
        ccy=CCY_BTC, bar=BAR_1D,
        since=datetime(year=2022, month=4, day=1, hour=0, minute=0, second=0),
        until=datetime(year=2022, month=4, day=10, hour=0, minute=0, second=0),
    )
    assert len(res) == 9
    assert res[0].__dict__ == Candlestick(t=datetime(year=2022, month=4, day=1), o=46453.4,
                                          h=46707.8, l=44219.6, c=46529.6).__dict__
    assert res[8].__dict__ == Candlestick(t=datetime(year=2022, month=4, day=9), o=43649.3,
                                          h=43716.0, l=42112.0, c=42280.0).__dict__


def test_query_market_candles_partial():
    res = query_market_candles(
        ccy=CCY_BTC, bar=BAR_1D,
        since=datetime(year=2022, month=3, day=31, hour=12, minute=0, second=0),
        until=datetime(year=2022, month=4, day=9, hour=12, minute=0, second=0),
    )
    assert len(res) == 9
    assert res[0].__dict__ == Candlestick(t=datetime(year=2022, month=4, day=1), o=46453.4,
                                          h=46707.8, l=44219.6, c=46529.6).__dict__
    assert res[8].__dict__ == Candlestick(t=datetime(year=2022, month=4, day=9), o=43649.3,
                                          h=43716.0, l=42112.0, c=42280.0).__dict__

#
# def test_query_trade_fills():
#     # 注意，这个测试只有 2022-04-17 20:58:39 开始没有新交易时才有效。
#     res = query_trade_fills(last_bill_id="435607391688867841")
#     assert len(res) == 3
#     assert res[0].__dict__ == Trade(ccy="xmr", price=233.79, crypto=-0.123668, bill_id='435607463918977025').__dict__
#     assert res[1].__dict__ == Trade(ccy="xrp", price=0.77057, crypto=-1.039431, bill_id='435607531526963204').__dict__
#     assert res[2].__dict__ == Trade(ccy="xrp", price=0.77054, crypto=-3.260116, bill_id='435607531526963208').__dict__
