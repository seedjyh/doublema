# -*- coding: utf-8 -*-

"""
market 实现了 smarter.market.Market 接口访问Okex交易所并下载行情数据的功能。

依赖repo.Repo做缓存或存储，但自己不实现。
"""
import abc
from datetime import datetime
from smarter import market
from okex import _api
from okex import _sqlite


class Market(market.Market):
    def __init__(self, ccy: str, bar: str, db: str = None):
        super(Market, self).__init__(ccy=ccy, bar=bar)
        db = db or ":memory:"
        self._repo = _sqlite.Repo(ccy=ccy, bar=bar, db=db)

    def query(self, since: datetime = None, until: datetime = None):
        res = self._repo.query(since, until)
        if len(res) == 0:
            self._repo.save(candles=_api.query(self._ccy, since, until, self._bar))
        else:
            if since and res[0].t() > since:
                self._repo.save(candles=_api.query(self._ccy, since, res[0].t(), self._bar))
            if until and res[-1].t() < until:
                self._repo.save(candles=_api.query(self._ccy, res[-1].t(), until, self._bar))
        return self._repo.query(since, until)


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
