# -*- coding: utf-8 -*-
import datetime

from ma import command


class MARecord:
    def __init__(self, timestamp: datetime.datetime, ma: dict):
        self.timestamp = timestamp
        self.ma = ma


class Evaluator(command.Evaluator):
    def __init__(self):
        self._ma_parameters = [1, 7, 13, 55]
        self._ma_parameters.sort()

    def get_scores(self, k_line_chart: command.KLineChart, since=None, until=None) -> []:
        ma_records = self._get_ma_records(k_line_chart, since, until)
        res = []
        for i in range(len(ma_records)):
            new_record = command.TradeViewRecord(
                timestamp=ma_records[i].timestamp,
                ma={**ma_records[i].ma},
                score=self._evaluate_last_record_score(ma_records[:i + 1])
            )
            res.append(new_record)
        return res

    def get_advice(self, k_line_chart: command.KLineChart, timestamp: datetime.datetime,
                   position: command.Position) -> []:
        pass

    def _get_ma_records(self, k_line_chart: command.KLineChart, since=None, until=None) -> []:
        """
        读取K线图，返回带有均线信息的记录。
        :param k_line_chart: K线图。
        :param since: 开始时间戳（含）
        :param until: 结束时间戳（含）
        :return: list of MARecord
        """
        res = []
        raw_records = k_line_chart.get_records(since=since, until=until)
        sums = {}
        for p in self._ma_parameters:
            sums[p] = 0.0
        for i in range(len(raw_records)):
            new_record = MARecord(timestamp=raw_records[i].timestamp, ma={})
            for p in self._ma_parameters:
                sums[p] += raw_records[i].price
                if i - p >= 0:
                    sums[p] -= raw_records[i - p].price
                new_record.ma[p] = sums[p] / min(i + 1, p)
            res.append(new_record)
        return res

    def _evaluate_last_record_score(self, ma_records: []) -> float:
        """
        获取最后一条 MARecord 的评分
        :param ma_records: list of MARecord
        :return: 评分 [0.0, 1.0]
        """
        last_record = ma_records[-1]
        total = 0.0
        hit = 0.0
        for shorter in self._ma_parameters:
            for longer in self._ma_parameters[self._ma_parameters.index(shorter) + 1:]:
                total += 1
                if last_record.ma[shorter] > last_record.ma[longer]:  # todo: 这里考虑引入 1e-3 的容错范围
                    hit += 1
        return float(hit) / float(total)
