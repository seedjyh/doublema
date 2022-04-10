# -*- coding: utf-8 -*-

"""
market 实现了 smarter.market.Market 接口访问Okex交易所并下载行情数据的功能。

依赖repo.Repo做缓存或存储，但自己不实现。
"""
import abc
from datetime import datetime
from smarter import market
from smarter.market import Candlestick
from okex import _api


class Market(market.Market):
    def __init__(self):
        pass

    def query(self, ccy: str = None, since: datetime = None, until: datetime = None, bar: str = None):
        return _api.query(ccy, since, until, bar)


class Repo(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def save(self, candle: Candlestick):
        """
        将candle保存到数据库。
        :param candle: 要保存的行情数据，Candlestick类型。
        :return: 无
        """
        pass

    def save_all(self, candles: []):
        """
        将所有candles保存到数据库。
        :param candles: Candlestick列表
        :return: 无
        """
        pass

    def query(self, ccy: str, since: datetime, until: datetime, bar: str) -> []:
        """
        查询指定范围数据。
        :param ccy:
        :param since:
        :param until:
        :param bar:
        :return: Candlestick 列表
        """
