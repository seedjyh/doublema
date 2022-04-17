# -*- coding: utf-8 -*-
from datetime import datetime

import triplema._index
import okex.market
from model import CCY_BTC, BAR_1D


# class TestMarket:
#     def test_query(self):
#         m = triplema.market.Market(source=okex.market.Market(ccy=CCY_BTC, bar=BAR_1D))
#         ma_list = [1,5,13,34]
#         for index in m.query_market_candles(since=datetime(year=2022, month=4, day=1), until=datetime.today(), ma_list=ma_list):
#             print(index.__dict__)
