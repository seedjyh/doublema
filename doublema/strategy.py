# -*- coding: utf-8 -*-
import statistics

import trend
import database


class Strategy:
    def __init__(self):
        pass

    def get_score(self, records):
        """
        获取 records 最后一个 Record 的分数
        :param records: LIST<Record>
        :return:
        """
        try:
            scores = [
                self._get_k_ma13_score(records[-1]),
                self._get_ma13_score(records),
                self._get_ma13_ma55_score(records[-1]),
                self._get_ma55_score(records),
            ]
            return statistics.mean(scores)
        except trend.NoEnoughDataError:
            return None

    @staticmethod
    def _get_k_ma13_score(r: database.Record) -> float:
        if trend.larger(r.k_price, r.ma13_price):
            return 1.0
        elif trend.less(r.k_price, r.ma13_price):
            return 0.0
        else:
            return 0.5

    @staticmethod
    def _get_ma13_score(records) -> float:
        if trend.is_increasing([r.ma13_price for r in records]):
            return 1.0
        elif trend.is_decreasing([r.ma13_price for r in records]):
            return 0.0
        else:
            return 0.5

    @staticmethod
    def _get_ma13_ma55_score(r: database.Record) -> float:
        if trend.larger(r.ma13_price, r.ma55_price):
            return 1.0
        elif trend.less(r.ma13_price, r.ma55_price):
            return 0.0
        else:
            return 0.5

    @staticmethod
    def _get_ma55_score(records) -> float:
        if trend.is_increasing([r.ma55_price for r in records]):
            return 1.0
        elif trend.is_decreasing([r.ma55_price for r in records]):
            return 0.0
        else:
            return 0.5
