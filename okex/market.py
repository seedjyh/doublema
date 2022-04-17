# -*- coding: utf-8 -*-

"""
market 实现了 model.Market 接口访问Okex交易所并下载行情数据的功能。

依赖repo.Repo做缓存或存储，但自己不实现。
"""

from datetime import datetime, timedelta
import model
from okex import _api
from okex import _sqlite

_db_conn = None


def set_db_conn(db_conn):
    """
    设置一个sqlite3的连接，用于缓存行情数据。
    :param db_conn:
    :return:
    """
    global _db_conn
    _db_conn = db_conn


def query(ccy: str, bar: str, since: datetime, until: datetime):
    """
    查询指定标的、指定K线粒度，K柱起点从since（含）到until（不含）的所有K柱，按照K柱时间顺序排列。
    :param ccy: 标的。
    :param bar: K线粒度。
    :param since: 起点时间（含）
    :param until: 终点时间（不含）
    :return:
    """
    now = datetime.now()
    bar_timedelta = _bar_to_timedelta(bar)
    repo = _sqlite.MarketRepo(ccy=ccy, bar=bar, db_conn=_db_conn)
    res = repo.query(since=since, until=until)
    api_res = []
    if len(res) == 0:
        api_res += _api.query_market_candles(ccy=ccy, bar=bar, since=since, until=until)
    else:
        if res[0].t() > since:
            api_res += _api.query_market_candles(ccy=ccy, bar=bar, since=since, until=res[0].t())
        if res[-1].t() + _bar_to_timedelta(bar) < until:
            api_res += _api.query_market_candles(ccy=ccy, bar=bar, since=res[-1].t() + timedelta(milliseconds=1), until=until)
    saving_res = [c for c in api_res if c.t() + bar_timedelta <= now]
    repo.save(candles=saving_res)
    res += api_res
    res.sort(key=lambda candle: candle.t())
    return res


class Market(model.Market):
    """
    为了兼容而保留的一个包装类。
    """
    def query(self, ccy: str, bar: str, since: datetime, until: datetime):
        return query(ccy, bar, since, until)


def _bar_to_timedelta(bar) -> timedelta:
    if bar == model.BAR_1D:
        return timedelta(days=1)
    else:
        raise Exception("invalid bar {}".format(bar))
