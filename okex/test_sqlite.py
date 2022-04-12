# -*- coding: utf-8 -*-
from datetime import datetime

import pytest

from okex._sqlite import Repo
from model import Candlestick, BAR_1D, CCY_BTC


class TestRepo:
    @pytest.fixture
    def setup(self):
        repo = Repo(ccy=CCY_BTC, bar=BAR_1D)
        candlestick1 = Candlestick(t=datetime(year=2022, month=4, day=1), o=41001, h=41003, l=41000, c=41002)
        candlestick2 = Candlestick(t=datetime(year=2022, month=4, day=3), o=43001, h=43003, l=43000, c=43002)
        repo.save(candles=[candlestick1, candlestick2])
        return repo, [candlestick1, candlestick2]

    def test_save(self, setup):
        repo, candlesticks = setup
        res = repo.query()
        assert len(res) == 2
        assert res[0].__dict__ == candlesticks[0].__dict__
        assert res[1].__dict__ == candlesticks[1].__dict__

    def test_save_no_data(self, setup):
        repo = Repo(ccy=CCY_BTC, bar=BAR_1D)
        res = repo.query(until=datetime(year=2000, month=1, day=1))
        assert len(res) == 0

    def test_save_partial(self, setup):
        repo, candlesticks = setup
        res = repo.query(until=datetime(year=2022, month=4, day=1))
        assert len(res) == 1
        assert res[0].__dict__ == candlesticks[0].__dict__

    def test_save_partial_2(self, setup):
        repo, candlesticks = setup
        res = repo.query(since=datetime(year=2022, month=4, day=3))
        assert len(res) == 1
        assert res[0].__dict__ == candlesticks[1].__dict__
