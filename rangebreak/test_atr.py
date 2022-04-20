# -*- coding: utf-8 -*-
from datetime import datetime

import const
import okex.market
from rangebreak import _atr


# 此测试可能依赖外网，不一定能用。
# def test_get_atr():
#     _atr.init(okex.market.Market())
#     print("atr={}".format(_atr.get_atr(ccy=const.CCY_BTC, bar=const.BAR_1D, t=datetime.now())))
