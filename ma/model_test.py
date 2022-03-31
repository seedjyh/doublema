# -*- coding: utf-8 -*-

from ma.model import Position, Trade


class TestTrade:
    def test_do(self):
        before = Position(name="btc", crypto=0.0, usdt=1000.0)
        after = Trade(name="btc", price=500.0, crypto=1.0).do(before)
        assert after.__dict__ == Position(name="btc", crypto=1.0, usdt=500.0).__dict__

    def test_do_no_enough_usdt(self):
        before = Position(name="btc", crypto=0.0, usdt=1000.0)
        after = Trade(name="btc", price=2000.0, crypto=1.0).do(before)
        assert after.__dict__ == Position(name="btc", crypto=0.5, usdt=0.0).__dict__

    def test_operation(self):
        assert Trade(name="btc", price=2000.0, crypto=1.0).operation() == "BUY"