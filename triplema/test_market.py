# -*- coding: utf-8 -*-
from datetime import datetime

import triplema.market
import okex.market
from smarter.market import CCY_BTC, BAR_1D
from triplema import _arg


# class TestMarket:
#     def test_query(self):
#         m = triplema.market.Market(source=okex.market.Market(ccy=CCY_BTC, bar=BAR_1D))
#
#         for index in m.query(since=datetime(year=2022, month=4, day=1), until=datetime.today(), ma_list=_arg.ma_list):
#             print(index.__dict__)
