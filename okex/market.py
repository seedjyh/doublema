# -*- coding: utf-8 -*-

"""
market 实现了 model.Market 接口访问Okex交易所并下载行情数据的功能。

依赖repo.Repo做缓存或存储，但自己不实现。
"""
import abc
from datetime import datetime
import model
from okex import _api
from okex import _sqlite


class Market(model.Market):
    def __init__(self, db: str = ":memory:"):
        self._db = db

    def query(self, ccy: str, bar: str, since: datetime = None, until: datetime = None):
        repo = _sqlite.Repo(db=self._db, ccy=ccy, bar=bar)
        res = repo.query(since, until)
        if len(res) == 0:
            repo.save(candles=_api.query(ccy, since, until, bar))
        else:
            if since and res[0].t() > since:
                repo.save(candles=_api.query(ccy, since, res[0].t(), bar))
            if until and res[-1].t() < until:
                repo.save(candles=_api.query(ccy, res[-1].t(), until, bar))
        return repo.query(since, until)


class Repo(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def save(self, candles: []):
        """
        将所有candles保存到数据库。
        :param candles: Candlestick列表
        :return: 无
        """
        pass

    @abc.abstractmethod
    def query(self, since: datetime, until: datetime) -> []:
        """
        查询指定范围数据。
        :param since:
        :param until:
        :return: Candlestick 列表
        """
