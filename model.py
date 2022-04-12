# -*- coding: utf-8 -*-
import abc
from datetime import datetime, timedelta


class Candlestick:
    def __init__(self, t: datetime, o: float, h: float, l: float, c: float):
        self._t = t
        self._o = o
        self._h = h
        self._l = l
        self._c = c

    def t(self):
        return self._t

    def o(self):
        return self._o

    def h(self):
        return self._h

    def l(self):
        return self._l

    def c(self):
        return self._c

    def timestamp(self):
        return self._t.timestamp()


# 常用的柱形图单位
BAR_1D = "1D"

# 常用的加密货币名称
CCY_BTC = "btc"


class Market(metaclass=abc.ABCMeta):
    def __init__(self, ccy: str, bar: str):
        self._ccy = ccy
        self._bar = bar

    @abc.abstractmethod
    def query(self, since: datetime, until: datetime):
        """
        获取一段时间的市场行情。
        :param since: 查询的开始时刻。
        :param until: 查询的结束时刻。
        :return: Candlestick 列表。
        """
        pass


class Position:
    def __init__(self, ccy: str, crypto: float, usdt: float):
        self.ccy = ccy
        self.crypto = crypto
        self.usdt = usdt

    def total(self, price: float):
        return self.usdt + self.crypto * price

    def score(self, price: float):
        return 1.0 - self.usdt / self.total(price)


class PositionRepository(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def set(self, p: Position):
        pass

    @abc.abstractmethod
    def query(self, ccy: str):
        pass

    @abc.abstractmethod
    def query_all(self):
        pass


class NoSuchRecord(Exception):
    def __init__(self, sql):
        self.sql = sql
