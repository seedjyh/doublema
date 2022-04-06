# -*- coding: utf-8 -*-
import datetime

from ma import command, model
from ma.candle import CandleChart, Candle
from ma.evaluator import Evaluator


class MockCandleChart(CandleChart):
    def __init__(self, records: []):
        self._records = records

    def __del__(self):
        pass

    def insert_one(self, c: Candle):
        pass

    def insert_multi(self, cs: []):
        pass

    def query(self, since: datetime = None, until: datetime = None) -> []:
        return self._records


class TestEvaluator:
    def test_get_scores(self):
        eval = Evaluator()
        raw_records = [
            model.KLineRecord(timestamp=datetime.datetime(year=2022, month=1, day=1), price=1.0),
            model.KLineRecord(timestamp=datetime.datetime(year=2022, month=1, day=2), price=2.0),
        ]
        candle_chart = MockCandleChart(records=raw_records)
        scored_records = eval.get_scores(candle_chart=candle_chart)
        assert len(scored_records) == 2
        assert scored_records[0].timestamp == raw_records[0].timestamp
        assert scored_records[0].ma[1] == raw_records[0].price
        assert scored_records[1].timestamp == raw_records[1].timestamp
        assert scored_records[1].ma[1] == raw_records[1].price
