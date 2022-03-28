# -*- coding: utf-8 -*-
import pytest

from doublema.strategy import Strategy, Account, Trade


class TestStrategy:
    @pytest.mark.parametrize('account, score, price, trade', [
        (Account('btc', 0.0, 1000.0), 1.0, 20.0, Trade('btc', 20.0, 50.0, -1000.0)),
        (Account('btc', 0.0, 1000.0), 0.0, 20.0, Trade('btc', 20.0, 0.0, 0.0)),
        (Account('btc', 0.0, 1000.0), 0.5, 20.0, Trade('btc', 20.0, 25.0, -500.0)),
        (Account('btc', 25.0, 500.0), 0.5, 20.0, Trade('btc', 20.0, 0.0, 0.0)),
        (Account('btc', 50.0, 0.0), 1.0, 20.0, Trade('btc', 20.0, 0.0, 0.0)),
        (Account('btc', 50.0, 0.0), 0.0, 20.0, Trade('btc', 20.0, -50.0, 1000.0)),
    ])
    def test_advice_trade(self, account, score, price, trade):
        assert Strategy().advice_trade(
            account=account,
            score=score,
            price=price,
        ) == trade
