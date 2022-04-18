# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

import model

ATR_RANGE = 20


class Index:
    def __init__(self, t: datetime, ma: dict, atr: float):
        self.t = t
        self.ma = ma
        self.atr = atr


class IndexChart:
    def __init__(self, source: model.Market):
        self._source = source

    def query(self, ccy: str, bar: str, since: datetime, until: datetime, ma_list: list):
        max_ma = max(*ma_list, ATR_RANGE)
        source_since = since + timedelta(days=-max_ma)
        source_until = until
        source_res = self._source.query(ccy=ccy, bar=bar, since=source_since, until=source_until)
        res = []
        for i in range(len(source_res)):
            if source_res[i].t() < since:
                continue
            new_index = Index(
                t=source_res[i].t(),
                ma={},
                atr=self.calc_average([abs(r.h() - r.l()) for r in source_res[max(0, i + 1 - ATR_RANGE): i + 1]]),
            )
            for interval in ma_list:
                new_index.ma[interval] = self.calc_average([r.c() for r in source_res[max(0, i + 1 - interval): i + 1]])
            res.append(new_index)
        return res

    def query_latest(self, ccy: str, bar: str) -> Index:
        until = datetime.now()
        since = until - self._bar_to_timedelta(bar) * 2
        return self.query(ccy=ccy, bar=bar, since=since, until=until, ma_list=[1, ])[-1]

    @staticmethod
    def calc_average(arr: list):
        return sum([float(v) for v in arr]) / len(arr)

    @staticmethod
    def _bar_to_timedelta(bar) -> timedelta:
        if bar == model.BAR_1D:
            return timedelta(days=1)
        else:
            raise Exception("invalid bar {}".format(bar))
