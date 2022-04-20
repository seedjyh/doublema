# -*- coding: utf-8 -*-
from datetime import datetime

import const
import okex
from rangebreak import _score


def test_get_score():
    _score.init(okex.market.Market())
    print("score={}".format(_score.get_score(ccy=const.CCY_BTC, bar=const.BAR_1D, t=datetime.now())))
