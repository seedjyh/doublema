# -*- coding: utf-8 -*-
import os
import sqlite3
from datetime import datetime, timedelta

import pytest

from okex import market
from model import CCY_BTC, BAR_1D, Candlestick


@pytest.fixture(scope="function")
def db_name():
    db_name = "test.sqlite_db"
    if os.path.exists(path=db_name):
        os.remove(path=db_name)
    db_conn = sqlite3.connect(database=db_name)
    market.set_db_conn(db_conn)
    yield db_name
    db_conn.close()
    if os.path.exists(path=db_name):
        os.remove(path=db_name)


def test_query(db_name):
    assert len(market.query(ccy=CCY_BTC, bar=BAR_1D,
                            since=datetime(year=2022, month=4, day=3),
                            until=datetime(year=2022, month=4, day=4))) == 1
    assert len(market.query(ccy=CCY_BTC, bar=BAR_1D,
                            since=datetime(year=2022, month=4, day=2),
                            until=datetime(year=2022, month=4, day=5))) == 3
    res = market.query(ccy=CCY_BTC, bar=BAR_1D,
                       since=datetime(year=2022, month=4, day=1),
                       until=datetime(year=2022, month=4, day=7))
    assert len(res) == 6
    assert res[0].__dict__ == Candlestick(t=datetime(year=2022, month=4, day=1),
                                          o=46453.4, h=46707.8, l=44219.6, c=46529.6).__dict__
    assert res[-1].__dict__ == Candlestick(t=datetime(year=2022, month=4, day=6),
                                           o=45762.2, h=46190.0, l=43716.8, c=44166.0).__dict__


class TestRepo:
    @pytest.fixture
    def setup(self):
        db_conn = sqlite3.connect(":memory:")
        repo = market.Repo(ccy=CCY_BTC, bar=BAR_1D, db_conn=db_conn)
        candlestick1 = Candlestick(t=datetime(year=2022, month=4, day=1), o=41001, h=41003, l=41000, c=41002)
        candlestick2 = Candlestick(t=datetime(year=2022, month=4, day=3), o=43001, h=43003, l=43000, c=43002)
        repo.save(candles=[candlestick1, candlestick2])
        return repo, [candlestick1, candlestick2]

    def test_query(self, setup):
        repo, candlesticks = setup
        res = repo.query()
        assert len(res) == 2
        assert res[0].__dict__ == candlesticks[0].__dict__
        assert res[1].__dict__ == candlesticks[1].__dict__

    def test_query_no_data(self, setup):
        repo, candlesticks = setup
        assert len(repo.query(until=min([c.t() for c in candlesticks]))) == 0
        assert len(repo.query(since=max([c.t() for c in candlesticks]) + timedelta(milliseconds=1))) == 0

    def test_query_partial(self, setup):
        repo, candlesticks = setup
        # 比较小的那个bar < until 则该bar会被选中
        min_candlestick_t = min([c.t() for c in candlesticks])
        until = min_candlestick_t + timedelta(milliseconds=1)
        res = repo.query(until=until)
        assert len(res) == 1
        assert res[0].t() == min_candlestick_t

    def test_query_partial_2(self, setup):
        repo, candlesticks = setup
        max_candlestick_t = max([c.t() for c in candlesticks])
        since = max_candlestick_t
        res = repo.query(since=since)
        assert len(res) == 1
        assert res[0].t() == max_candlestick_t
