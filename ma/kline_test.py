# -*- coding: utf-8 -*-
import datetime
import math

from ma.kline import KLineChart
from ma.command import KLineRecord


class TestKLineChart:
    def test_add_price(self):
        ch = KLineChart(name="test.KLineChart.crypto")
        ch.add_price(timestamp=datetime.datetime(2022, 3, 4), price=4.56)
        ch.add_price(timestamp=datetime.datetime(2022, 1, 2), price=1.23)

    def test_get_records(self):
        ch = KLineChart(name="test.KLineChart.crypto")
        ch.add_price(timestamp=datetime.datetime(2022, 3, 4), price=4.56)
        ch.add_price(timestamp=datetime.datetime(2022, 1, 2), price=1.23)
        records = ch.get_records()
        assert len(records) == 2
        assert records[0].__dict__ == KLineRecord(timestamp=datetime.datetime(2022, 1, 2), price=1.23).__dict__
        assert records[1].__dict__ == KLineRecord(timestamp=datetime.datetime(2022, 3, 4), price=4.56).__dict__
