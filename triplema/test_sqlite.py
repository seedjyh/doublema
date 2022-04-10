# -*- coding: utf-8 -*-
import pytest

from triplema._sqlite import Repo
from triplema.position import Position, NoSuchRecord


class TestRepo:
    def test_set(self):
        pr = Repo()
        ps = [
            Position(ccy="btc", crypto=1.0, usdt=10.0),
            Position(ccy="eth", crypto=2.0, usdt=20.0),
            Position(ccy="doge", crypto=3.0, usdt=30.0),
        ]
        for p in ps:
            pr.set(p=p)
        for p in ps:
            assert pr.query(p.ccy).__dict__ == p.__dict__

    def test_set_again(self):
        pr = Repo()
        ps = [
            Position(ccy="btc", crypto=1.0, usdt=10.0),
            Position(ccy="btc", crypto=2.0, usdt=20.0),
            Position(ccy="btc", crypto=3.0, usdt=30.0),
        ]
        for p in ps:
            pr.set(p=p)
        assert pr.query("btc").__dict__ == ps[-1].__dict__

    def test_query_all(self):
        pr = Repo()
        ps = [
            Position(ccy="btc", crypto=1.0, usdt=10.0),
            Position(ccy="eth", crypto=2.0, usdt=20.0),
            Position(ccy="doge", crypto=3.0, usdt=30.0),
        ]
        for p in ps:
            pr.set(p=p)
        res = pr.query_all()
        assert len(res) == 3
        assert res[0].__dict__ == ps[0].__dict__
        assert res[1].__dict__ == ps[2].__dict__
        assert res[2].__dict__ == ps[1].__dict__

    def test_query_not_exist(self):
        pr = Repo()
        with pytest.raises(NoSuchRecord) as e:
            pr.query(ccy="no-such-ccy")