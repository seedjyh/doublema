# -*- coding: utf-8 -*-
import datetime

from ma.position import Position


class KLineRecord:
    def __init__(self, timestamp: datetime.datetime, price: float):
        """
        一条K线记录。
        :param timestamp: 时间戳，具体精确视情况而定。
        :param price: 该时间戳的收盘价。
        """
        self.timestamp = timestamp
        self.price = price


class Trade:
    def __init__(self, name: str, price: float, crypto: float):
        """
        交易参数
        :param name: 仓位名称，通常是加密货币名，如 ”btc“
        :param price: 交易时加密货币相对于 usdt 的价格。
        :param crypto: 被交易的加密货币的数量。
        """
        self.name = name
        self.price = float(price)
        self.crypto = float(crypto)
        if abs(price * crypto) < 1e-3:
            self.crypto = 0

    def ok(self, price):
        if self.crypto < 0.0:  # sell
            return self.price < price - 1e-5
        else:
            return self.price > price + 1e-5

    def do(self, raw: Position, price=None) -> Position:
        if price is None:
            price = self.price
        amount = self.crypto
        if amount > 0 and amount * price > raw.usdt:  # BUY
            amount = raw.usdt / price
        res = Position(
            name=raw.name,
            crypto=raw.crypto + amount,
            usdt=raw.usdt - price * amount,
        )
        res.assert_valid()
        return res

    def operation(self) -> str:
        if abs(self.price * self.crypto) < 1e-2:
            return "--"
        elif self.crypto > 0:
            return "buy"
        else:
            return "sell"


class TradeViewRecord:
    def __init__(self, timestamp: datetime.datetime, ma: {}, score: float):
        """

        :param timestamp: 时间戳。
        :param ma: 均线数据 dict。其中key是均线范围，比如1表示timestamp所在K柱的收盘价，3表示三日均线。
        :param score: 从 0.0 ~ 1.0 表示建议仓位。其中 0.0 表示建议空仓， 1.0 表示建议满仓。
        """
        self.timestamp = timestamp
        self.ma = ma
        self.score = score
