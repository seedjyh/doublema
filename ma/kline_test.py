# -*- coding: utf-8 -*-
import datetime
import math

from ma.kline import KLineChart
from ma.command import KLineRecord


class TestKLineChart:
    def test_add_price(self):
        ch = KLineChart(name="test.KLineChart.crypto")
        ch.clear(reason="test")
        ch.add_price(timestamp=datetime.datetime(2022, 3, 4), price=4.56)
        ch.add_price(timestamp=datetime.datetime(2022, 1, 2), price=1.23)
        records = ch.get_records()
        assert len(records) == 2
        assert records[0].__dict__ == KLineRecord(timestamp=datetime.datetime(2022, 1, 2), price=1.23).__dict__
        assert records[1].__dict__ == KLineRecord(timestamp=datetime.datetime(2022, 3, 4), price=4.56).__dict__

    def test_set_price(self):
        ch = KLineChart(name="test.KLineChart.crypto")
        ch.clear(reason="test")
        ch.add_price(timestamp=datetime.datetime(2022, 3, 4), price=4.56)
        ch.add_price(timestamp=datetime.datetime(2022, 5, 6), price=7.89)
        ch.set_price(timestamp=datetime.datetime(2022, 3, 4), price=1.23)
        records = ch.get_records()
        assert len(records) == 2
        assert records[0].__dict__ == KLineRecord(timestamp=datetime.datetime(2022, 3, 4), price=1.23).__dict__
        assert records[1].__dict__ == KLineRecord(timestamp=datetime.datetime(2022, 5, 6), price=7.89).__dict__

    def test_save(self):
        ch = KLineChart(name="test.KLineChart.save")
        ch.clear(reason="test")
        now = datetime.datetime(year=2022, month=1, day=2)
        ch.add_price(timestamp=now, price=3.1415)
        ch.save()
        ch2 = KLineChart(name="test.KLineChart.save")
        records = ch2.get_records(since=now, until=now)
        assert len(records) == 1
        assert records[0].timestamp == now
        assert records[0].price == 3.1415
