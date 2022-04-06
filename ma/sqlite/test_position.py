# -*- coding: utf-8 -*-
import pytest

from ma.sqlite.exception import NoSuchRecord
from ma.sqlite.position import PositionRepository, Position


class TestPositionRepository:
    def test_set(self):
        pr = PositionRepository(db_name=":memory:")
        ps = [
            Position(name="btc", crypto=1.0, usdt=10.0),
            Position(name="eth", crypto=2.0, usdt=20.0),
            Position(name="doge", crypto=3.0, usdt=30.0),
        ]
        for p in ps:
            pr.set(p=p)
        for p in ps:
            assert pr.query(p.name).__dict__ == p.__dict__

    def test_set_again(self):
        pr = PositionRepository(db_name=":memory:")
        ps = [
            Position(name="btc", crypto=1.0, usdt=10.0),
            Position(name="btc", crypto=2.0, usdt=20.0),
            Position(name="btc", crypto=3.0, usdt=30.0),
        ]
        for p in ps:
            pr.set(p=p)
        assert pr.query("btc").__dict__ == ps[-1].__dict__

    def test_query_all(self):
        pr = PositionRepository(db_name=":memory:")
        ps = [
            Position(name="btc", crypto=1.0, usdt=10.0),
            Position(name="eth", crypto=2.0, usdt=20.0),
            Position(name="doge", crypto=3.0, usdt=30.0),
        ]
        for p in ps:
            pr.set(p=p)
        res = pr.query_all()
        assert len(res) == 3
        assert res[0].__dict__ == ps[0].__dict__
        assert res[1].__dict__ == ps[2].__dict__
        assert res[2].__dict__ == ps[1].__dict__

    def test_query_not_exist(self):
        pr = PositionRepository(db_name=":memory:")
        with pytest.raises(NoSuchRecord) as e:
            pr.query(name="no-such-ccy")
