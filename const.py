# -*- coding: utf-8 -*-
from datetime import timedelta, datetime

# 常用的柱形图单位
BAR_1D = "1D"
BAR_1H = "1H"

# 常用的加密货币名称
CCY_BTC = "btc"


def bar_to_timedelta(bar: str) -> timedelta:
    """
    将bar名称转化成timedelta
    :param bar:
    :return:
    """
    assert type(bar) == str
    bar2delta = {
        BAR_1H: timedelta(hours=1),
        BAR_1D: timedelta(days=1),
    }
    t = bar2delta.get(bar)
    if t is None:
        raise Exception("invalid bar {}".format(bar))
    else:
        return t


def trim_timestamp(raw, bar) -> float:
    """
    将一个时间转修剪成整delta数。
    :param raw: 时间戳(float)或时间(datetime)
    :param bar: bar(str)或时间间隔(timedelta)
    :return: 时间戳(float)
    """
    if type(raw) == datetime:
        raw = raw.timestamp()
    if type(bar) == str:
        bar = bar_to_timedelta(bar)
    raw_second = int(raw)
    delta_second = int(bar.total_seconds())
    return float(raw_second // delta_second * delta_second)
