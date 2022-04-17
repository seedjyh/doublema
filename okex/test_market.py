# -*- coding: utf-8 -*-
import os
import sqlite3
from datetime import datetime, timedelta

import pytest

from okex import _sqlite
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
