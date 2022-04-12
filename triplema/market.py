# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

import model


class Index:
    def __init__(self, t: datetime, ma: dict):
        self.t = t
        self.ma = ma


class Market:
    def __init__(self, source=model.Market):
        self._source = source

    def query(self, since: datetime, until: datetime, ma_list: dict):
        max_ma = max(ma_list)
        source_since = since + timedelta(days=-max_ma)
        source_until = until
        tmp_res = [Index(t=c.t(), ma={1: c.c()}) for c in self._source.query(source_since, source_until)]
        for i in range(len(tmp_res)):
            for interval in ma_list:
                if interval == 1:
                    continue
                tmp_res[i].ma[interval] = self.calc_average([r.ma[1] for r in tmp_res[max(0, i + 1 - interval): i + 1]])

        res = []
        for r in tmp_res:
            if r.t >= since:
                res.append(r)
        return res

    @staticmethod
    def calc_average(arr: list):
        return sum([float(v) for v in arr]) / len(arr)
