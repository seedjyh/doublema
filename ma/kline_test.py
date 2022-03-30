# -*- coding: utf-8 -*-
import datetime
import math

from ma.kline import KLineChart, Record


class TestKLineChart:
    def test_add_closing(self):
        ch = KLineChart(name="test.KLineChart.crypto")
        ch.add_closing(timestamp=datetime.datetime(2022, 3, 4), closing=4.56)
        ch.add_closing(timestamp=datetime.datetime(2022, 1, 2), closing=1.23)

    def test_get_records(self):
        ch = KLineChart(name="test.KLineChart.crypto")
        ch.add_closing(timestamp=datetime.datetime(2022, 3, 4), closing=4.56)
        ch.add_closing(timestamp=datetime.datetime(2022, 1, 2), closing=1.23)
        records = ch.get_records(ma_parameter=[1, 2, 3])
        assert len(records) == 2
        assert records[0].timestamp == datetime.datetime(2022, 1, 2)
        assert records[0].closing == 1.23
        assert math.isclose(records[0].ma[1], 1.23, rel_tol=1e-5)
        assert math.isclose(records[0].ma[2], 1.23, rel_tol=1e-5)
        assert math.isclose(records[0].ma[3], 1.23, rel_tol=1e-5)
        assert records[1].timestamp == datetime.datetime(2022, 3, 4)
        assert records[1].closing == 4.56
        assert math.isclose(records[1].ma[1], 4.56, rel_tol=1e-5)
        assert math.isclose(records[1].ma[2], 2.895, rel_tol=1e-5)
        assert math.isclose(records[1].ma[3], 2.895, rel_tol=1e-5)
