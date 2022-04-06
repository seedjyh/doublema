# -*- coding: utf-8 -*-
import abc
from datetime import datetime


class Candle:
    def __init__(self, timestamp, opening, highest, lowest, closing):
        self.timestamp = timestamp
        self.opening = opening
        self.highest = highest
        self.lowest = lowest
        self.closing = closing


class CandleChart(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __del__(self):
        pass

    @abc.abstractmethod
    def insert_one(self, c: Candle):
        pass

    @abc.abstractmethod
    def insert_multi(self, cs: []):
        pass

    @abc.abstractmethod
    def query(self, since: datetime = None, until: datetime = None) -> []:
        pass
