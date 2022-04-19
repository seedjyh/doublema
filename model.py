# -*- coding: utf-8 -*-
import abc
from datetime import datetime


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



class Market(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def query(self, ccy: str, bar: str, since: datetime, until: datetime):
        """
        获取一段时间的市场行情。
        :param ccy: 标的，如"btc"
        :param bar: K柱宽度
        :param since: 查询的开始时刻。
        :param until: 查询的结束时刻。
        :return: Candlestick 列表。
        """
        pass

#
# class Position:
#     def __init__(self, ccy: str, crypto: float, usdt: float):
#         self.ccy = ccy
#         self.crypto = crypto
#         self.usdt = usdt
#
#     def total(self, price: float):
#         return self.usdt + self.crypto * price
#
#     def score(self, price: float):
#         return 1.0 - self.usdt / self.total(price)
#
#
# class PositionRepository(metaclass=abc.ABCMeta):
#     @abc.abstractmethod
#     def set(self, p: Position):
#         pass
#
#     @abc.abstractmethod
#     def query(self, ccy: str):
#         pass
#
#     @abc.abstractmethod
#     def query_all(self):
#         pass


class NoSuchRecord(Exception):
    def __init__(self, sql):
        self.sql = sql


class Trade:
    def __init__(self, ccy: str, price: float, crypto: float, bill_id: str = ""):
        """
        交易参数
        :param ccy: 仓位名称，通常是加密货币名，如 ”btc“
        :param price: 交易时加密货币相对于 usdt 的价格。
        :param crypto: 被交易的加密货币的数量。
        """
        self.ccy = ccy
        self.price = float(price)
        self.crypto = float(crypto)
        self.bill_id = bill_id
        if abs(price * crypto) < 1e-3:
            self.crypto = 0.0

    def operation(self) -> str:
        if self.no_op():
            return "--"
        elif self.crypto > 0:
            return "buy"
        else:
            return "sell"

    def price_desc(self, fmt: str):
        return (fmt + " usdt/{}").format(self.price, self.ccy)

    def amount_desc(self, fmt: str):
        if self.no_op():
            return "--"
        return (fmt + " {}").format(self.crypto, self.ccy)

    def usdt_desc(self, fmt: str):
        if self.no_op():
            return "--"
        return (fmt + " usdt").format(-self.crypto * self.price)

    def no_op(self) -> bool:
        return abs(self.price * self.crypto) < 1e-2
