# -*- coding: utf-8 -*-
from datetime import timedelta

# 常用的柱形图单位
BAR_1D = "1D"
BAR_1H = "1H"

# 常用的加密货币名称
CCY_BTC = "btc"


def bar_to_timedelta(bar) -> timedelta:
    bar2delta = {
        BAR_1H: timedelta(hours=1),
        BAR_1D: timedelta(days=1),
    }
    t = bar2delta.get(bar)
    if t is None:
        raise Exception("invalid bar {}".format(bar))
    else:
        return t
