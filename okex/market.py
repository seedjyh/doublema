# -*- coding: utf-8 -*-

"""
market 实现了 model.Market 接口访问Okex交易所并下载行情数据的功能。

依赖repo.Repo做缓存或存储，但自己不实现。
"""
import abc
from datetime import datetime, timedelta
import model
from okex import _api
from okex import _sqlite


def _bar_to_timedelta(bar) -> timedelta:
    if bar == model.BAR_1D:
        return timedelta(days=1)
    else:
        raise Exception("invalid bar {}".format(bar))


class Market(model.Market):
    def __init__(self, db_conn=None):
        self._db_conn = db_conn

    def query(self, ccy: str, bar: str, since: datetime, until: datetime):
        now = datetime.now()
        bar_timedelta = _bar_to_timedelta(bar)
        repo = _sqlite.MarketRepo(ccy=ccy, bar=bar, db_conn=self._db_conn)
        res = repo.query(since=since, until=until)
        api_res = []
        if len(res) == 0:
            api_res += _api.query(ccy=ccy, bar=bar, since=since, until=until)
        else:
            if res[0].t() > since:
                api_res += _api.query(ccy=ccy, bar=bar, since=since, until=res[0].t())
            if res[-1].t() + _bar_to_timedelta(bar) < until:
                api_res += _api.query(ccy=ccy, bar=bar, since=res[-1].t() + timedelta(milliseconds=1), until=until)
        saving_res = [c for c in api_res if c.t() + bar_timedelta <= now]
        repo.save(candles=saving_res)
        res += api_res
        res.sort(key=lambda candle: candle.t())
        return res
