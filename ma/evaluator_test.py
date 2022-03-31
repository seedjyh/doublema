# -*- coding: utf-8 -*-
import datetime

from ma import command
from ma.evaluator import Evaluator


class MockKLineChart(command.KLineChart):
    def __init__(self, records: []):
        self._records = records

    def add_price(self, timestamp: datetime.datetime, price: float):
        pass

    def set_price(self, timestamp: datetime.datetime, price: float):
        pass

    def get_records(self, since: datetime, until: datetime) -> []:
        return self._records

    def save(self):
        pass


class TestEvaluator:
    def test_get_scores(self):
        eval = Evaluator()
        raw_records = [
            command.KLineRecord(timestamp=datetime.datetime(year=2022, month=1, day=1), price=1.0),
            command.KLineRecord(timestamp=datetime.datetime(year=2022, month=1, day=2), price=2.0),
        ]
        k_line_chart = MockKLineChart(records=raw_records)
        scored_records = eval.get_scores(k_line_chart=k_line_chart)
        assert len(scored_records) == 2
        assert scored_records[0].timestamp == raw_records[0].timestamp
        assert scored_records[0].ma[1] == raw_records[0].price
        assert scored_records[1].timestamp == raw_records[1].timestamp
        assert scored_records[1].ma[1] == raw_records[1].price
