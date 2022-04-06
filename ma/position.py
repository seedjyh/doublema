# -*- coding: utf-8 -*-
import abc


class Position:
    def __init__(self, name, crypto: float, usdt: float):
        self.name = name
        self.crypto = crypto
        self.usdt = usdt

    def assert_valid(self):
        if self.crypto < -1e-5:
            raise Exception("invalid position, crypto={}".format(self.crypto))
        if self.usdt < -1e-5:
            raise Exception("invalid position, usdt={}".format(self.usdt))

    def total(self, price: float):
        return self.usdt + self.crypto * price

    def score(self, price: float):
        return 1.0 - self.usdt / self.total(price)


class PositionRepository(abc.ABCMeta):
    @abc.abstractmethod
    def __del__(self):
        pass

    @abc.abstractmethod
    def set(self, p: Position):
        pass

    @abc.abstractmethod
    def query(self, name: str):
        pass

    @abc.abstractmethod
    def query_all(self):
        pass
