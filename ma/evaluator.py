# -*- coding: utf-8 -*-
import datetime

from ma import command, model


class MARecord:
    def __init__(self, timestamp: datetime.datetime, ma: dict):
        self.timestamp = timestamp
        self.ma = ma


class Evaluator(command.Evaluator):
    def __init__(self):
        # 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144
        self._ma_parameters = [1, 5, 13, 34]
        # self._ma_parameters = [1, 3, 8, 21, 55]
        self._ma_parameters.sort()

    def get_scores(self, k_line_chart: command.KLineChart, since=None, until=None) -> []:
        ma_records = self._get_ma_records(k_line_chart, since, until)
        res = []
        for i in range(len(ma_records)):
            new_record = model.TradeViewRecord(
                timestamp=ma_records[i].timestamp,
                ma={**ma_records[i].ma},
                score=self._evaluate_last_record_score(ma_records[:i + 1])
            )
            res.append(new_record)
        return res

    def get_advice(self, k_line_chart: command.KLineChart, timestamp: datetime.datetime,
                   position: command.Position) -> []:
        res = []
        trade_view_records = self.get_scores(k_line_chart=k_line_chart, until=timestamp)
        if len(trade_view_records) == 0:
            return []
        last_record = trade_view_records[-1]
        now_price = last_record.ma[1]
        now_score = last_record.score
        total_balance = position.total(price=now_price)
        if now_score > position.score(price=now_price):  # BUY
            buy_amount = total_balance * now_score / now_price - position.crypto
            res.append(model.Trade(name=position.name, price=now_price, crypto=buy_amount))  # todo: 暂时直接成交，不挂单
        else:  # SELL
            sell_amount = position.crypto - total_balance * now_score / now_price
            res.append(model.Trade(name=position.name, price=now_price, crypto=-sell_amount))  # todo: 暂时直接成交，不挂单
        return res

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
        assert len(self._ma_parameters) >= 2  # 包括收盘（ma1）在内，一共至少要有两条均线
        total = len(self._ma_parameters) - 1
        hit = 0
        for i in range(len(self._ma_parameters)):
            if i > 0:
                if last_record.ma[self._ma_parameters[i - 1]] > last_record.ma[self._ma_parameters[i]]:
                    hit += 1
                else:
                    break
        return float(hit) / float(total)
