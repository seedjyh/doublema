# -*- coding: utf-8 -*-
import os
import sqlite3
from datetime import datetime, timedelta

import pytest

from okex import _sqlite
from okex.market import Market
from model import CCY_BTC, BAR_1D, Candlestick


@pytest.fixture(scope="function")
def db_name():
    db_name = "test.sqlite_db"
    if os.path.exists(path=db_name):
        os.remove(path=db_name)
    yield db_name
    if os.path.exists(path=db_name):
        os.remove(path=db_name)


class TestMarket:
    def test_query(self, db_name):
        m = Market(db_conn=sqlite3.connect(database=":memory:"))
        assert len(m.query(ccy=CCY_BTC, bar=BAR_1D,
                           since=datetime(year=2022, month=4, day=3),
                           until=datetime(year=2022, month=4, day=4))) == 1
        assert len(m.query(ccy=CCY_BTC, bar=BAR_1D,
                           since=datetime(year=2022, month=4, day=2),
                           until=datetime(year=2022, month=4, day=5))) == 3
        res = m.query(ccy=CCY_BTC, bar=BAR_1D,
                      since=datetime(year=2022, month=4, day=1),
                      until=datetime(year=2022, month=4, day=7))
        assert len(res) == 6
        assert res[0].__dict__ == Candlestick(t=datetime(year=2022, month=4, day=1),
                                              o=46453.4, h=46707.8, l=44219.6, c=46529.6).__dict__
        assert res[-1].__dict__ == Candlestick(t=datetime(year=2022, month=4, day=6),
                                               o=45762.2, h=46190.0, l=43716.8, c=44166.0).__dict__

    def test_query_partial(self, db_name):
        """
        测试不完整的k线情况。
        since=2022-04-03 12:00:00, until=2022-04-06 12:00:00, ccy=btc, bar=1D.
        预期返回的是数据长度是2，时间戳
        2022-04-04 00:00:00
        2022-04-05 00:00:00
        每一条数据里的时间戳都表示bar的开始时刻。即，如果一个candle的结束时间晚于until，那么这个candle不会返回。
        为了确保candle也不会被写入数据库，我加了一个检查。
        :return:
        """
        db_conn = sqlite3.connect(database=":memory:")
        since = datetime(year=2022, month=4, day=3, hour=12, minute=0, second=0)
        until = datetime(year=2022, month=4, day=5, hour=12, minute=0, second=0)
        market_res = Market(db_conn=db_conn).query(ccy=CCY_BTC, bar=BAR_1D, since=since, until=until)
        assert len(market_res) == 2
        assert market_res[0].t() == datetime(year=2022, month=4, day=4, hour=0, minute=0, second=0)
        assert market_res[1].t() == datetime(year=2022, month=4, day=5, hour=0, minute=0, second=0)
        repo = _sqlite.MarketRepo(ccy=CCY_BTC, bar=BAR_1D, db_conn=db_conn)
        db_res = repo.query(since=since, until=until + timedelta(days=2))
        assert len(db_res) == 2
        assert db_res[0].t() == datetime(year=2022, month=4, day=4, hour=0, minute=0, second=0)
        assert db_res[1].t() == datetime(year=2022, month=4, day=5, hour=0, minute=0, second=0)

    def test_query_partial_2(self, db_name):
        """
        测试不完整的k线情况。
        since=2022-04-04 00:00:00, until=2022-04-06 00:00:00, ccy=btc, bar=1D.
        预期返回的是数据长度是2，时间戳
        2022-04-04 00:00:00
        2022-04-05 00:00:00
        每一条数据里的时间戳都表示bar的开始时刻。即，如果一个candle的结束时间晚于until，那么这个candle不会返回。
        为了确保candle也不会被写入数据库，我加了一个检查。
        :return:
        """
        db_conn = sqlite3.connect(database=":memory:")
        since = datetime(year=2022, month=4, day=4, hour=0, minute=0, second=0)
        until = datetime(year=2022, month=4, day=6, hour=0, minute=0, second=0)
        market_res = Market(db_conn=db_conn).query(ccy=CCY_BTC, bar=BAR_1D, since=since, until=until)
        assert len(market_res) == 2
        assert market_res[0].t() == datetime(year=2022, month=4, day=4, hour=0, minute=0, second=0)
        assert market_res[1].t() == datetime(year=2022, month=4, day=5, hour=0, minute=0, second=0)
        repo = _sqlite.MarketRepo(ccy=CCY_BTC, bar=BAR_1D, db_conn=db_conn)
        db_res = repo.query(since=since, until=until + timedelta(days=2))
        assert len(db_res) == 2
        assert db_res[0].t() == datetime(year=2022, month=4, day=4, hour=0, minute=0, second=0)
        assert db_res[1].t() == datetime(year=2022, month=4, day=5, hour=0, minute=0, second=0)
