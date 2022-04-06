# -*- coding: utf-8 -*-
from datetime import datetime

from ma.candle import Candle
from ma.sqlite.candle import CandleChart


class TestCandleChat:
    def test_insert_one(self):
        chart = CandleChart(db_name=":memory:", ccy="BTC")
        candles = [
            Candle(timestamp=datetime(year=2022, month=4, day=1), opening=1.1, highest=3.1, lowest=0.1, closing=2.1),
            Candle(timestamp=datetime(year=2022, month=4, day=3), opening=1.3, highest=3.3, lowest=0.3, closing=2.3),
            Candle(timestamp=datetime(year=2022, month=4, day=4), opening=1.4, highest=3.4, lowest=0.4, closing=2.4),
        ]
        for c in candles:
            chart.insert_one(c=c)
        res = chart.query()
        assert len(res) == 3
        assert res[0].__dict__ == candles[0].__dict__
        assert res[1].__dict__ == candles[1].__dict__
        assert res[2].__dict__ == candles[2].__dict__

    def test_insert_multi(self):
        chart = CandleChart(db_name=":memory:", ccy="BTC")
        candles = [
            Candle(timestamp=datetime(year=2022, month=4, day=1), opening=1.1, highest=3.1, lowest=0.1, closing=2.1),
            Candle(timestamp=datetime(year=2022, month=4, day=3), opening=1.3, highest=3.3, lowest=0.3, closing=2.3),
            Candle(timestamp=datetime(year=2022, month=4, day=4), opening=1.4, highest=3.4, lowest=0.4, closing=2.4),
        ]
        chart.insert_multi(cs=candles)
        res = chart.query()
        assert len(res) == 3
        assert res[0].__dict__ == candles[0].__dict__
        assert res[1].__dict__ == candles[1].__dict__
        assert res[2].__dict__ == candles[2].__dict__

    def test_query_with_until(self):
        chart = CandleChart(db_name=":memory:", ccy="BTC")
        candles = [
            Candle(timestamp=datetime(year=2022, month=4, day=1), opening=1.1, highest=3.1, lowest=0.1, closing=2.1),
            Candle(timestamp=datetime(year=2022, month=4, day=3), opening=1.3, highest=3.3, lowest=0.3, closing=2.3),
            Candle(timestamp=datetime(year=2022, month=4, day=4), opening=1.4, highest=3.4, lowest=0.4, closing=2.4),
        ]
        chart.insert_multi(cs=candles)
        res = chart.query(until=datetime(year=2022, month=4, day=3))
        assert len(res) == 2
        assert res[0].__dict__ == candles[0].__dict__
        assert res[1].__dict__ == candles[1].__dict__

    def test_query_with_since(self):
        chart = CandleChart(db_name=":memory:", ccy="BTC")
        candles = [
            Candle(timestamp=datetime(year=2022, month=4, day=1), opening=1.1, highest=3.1, lowest=0.1, closing=2.1),
            Candle(timestamp=datetime(year=2022, month=4, day=3), opening=1.3, highest=3.3, lowest=0.3, closing=2.3),
            Candle(timestamp=datetime(year=2022, month=4, day=4), opening=1.4, highest=3.4, lowest=0.4, closing=2.4),
        ]
        chart.insert_multi(cs=candles)
        res = chart.query(since=datetime(year=2022, month=4, day=3))
        assert len(res) == 2
        assert res[0].__dict__ == candles[1].__dict__
        assert res[1].__dict__ == candles[2].__dict__

    def test_query_with_since_until(self):
        chart = CandleChart(db_name=":memory:", ccy="BTC")
        candles = [
            Candle(timestamp=datetime(year=2022, month=4, day=1), opening=1.1, highest=3.1, lowest=0.1, closing=2.1),
            Candle(timestamp=datetime(year=2022, month=4, day=3), opening=1.3, highest=3.3, lowest=0.3, closing=2.3),
            Candle(timestamp=datetime(year=2022, month=4, day=4), opening=1.4, highest=3.4, lowest=0.4, closing=2.4),
        ]
        chart.insert_multi(cs=candles)
        res = chart.query(since=datetime(year=2022, month=4, day=3), until=datetime(year=2022, month=4, day=3))
        assert len(res) == 1
        assert res[0].__dict__ == candles[1].__dict__