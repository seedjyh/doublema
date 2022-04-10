# -*- coding: utf-8 -*-
import abc
from datetime import datetime, timedelta


class Candlestick:
    def __init__(self, ccy: str, bar: str, t: datetime, o: float, h: float, l: float, c: float):
        self._ccy = ccy
        self._bar = bar
        self._t = t
        self._o = o
        self._h = h
        self._l = l
        self._c = c

    def timestamp(self):
        return self._t.timestamp()


# 常用的柱形图单位
BAR_1D = "1D"

# 常用的加密货币名称
CCY_BTC = "btc"


class Market(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def query(self, ccy: str, since: datetime, until: datetime, bar: str):
        """
        获取一段时间的市场行情。
        :param ccy: 加密货币的名称，如 BTC, btc 等。
        :param since: 查询的开始时刻。
        :param until: 查询的结束时刻。
        :param bar: 柱形图的单位。
        :return: Candlestick 列表。
        """
        pass
