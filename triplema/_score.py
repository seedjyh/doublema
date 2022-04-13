# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

import model
from triplema import _index


class Score:
    def __init__(self, ccy: str, t: datetime, v: float, p: float, atr: float):
        """

        :param ccy: 货币名称。
        :param t: 所属K柱
        :param v: 浮点数，0.0~1.0，0表示空仓，1表示满仓。
        :param p: 价格。
        :param atr: 真实波动均值。
        """
        self.ccy = ccy
        self.t = t
        self.v = v
        self.p = p
        self.atr = atr

    def get_trade(self, raw_position: model.Position) -> model.Trade:
        total = raw_position.total(price=self.p)
        expect_crypto = total * self.v / self.p
        if self._need_trade(trade_usdt=(raw_position.crypto - expect_crypto) * self.p, total_usdt=total):
            trade = model.Trade(ccy=raw_position.ccy, price=self.p, crypto=expect_crypto - raw_position.crypto)
            return trade
        else:
            return model.Trade(ccy=raw_position.ccy, price=self.p, crypto=0)

    @staticmethod
    def _need_trade(trade_usdt: float, total_usdt: float):
        return abs(trade_usdt) / total_usdt > 0.1


class Evaluator:
    def __init__(self, source: model.Market, bar: str, ma_list: []):
        self._index_chart = _index.IndexChart(source=source)
        self._bar = bar
        self._ma_list = ma_list
        self._ma_list.sort()
        # 为了比较不同均线，必须有至少两条均线。
        assert (len(self._ma_list) > 1)
        # 必须包含宽度1的均线，即当前K柱
        assert (self._ma_list[0] == 1)

    @staticmethod
    def _calc_score(index: _index.Index) -> float:
        count = 0
        total = len(index.ma) - 1
        ma_list = [v for v in index.ma.keys()]
        for i in range(len(ma_list)):
            if i == 0:
                continue
            now_ma = ma_list[i]
            last_ma = ma_list[i - 1]
            if index.ma[now_ma] < index.ma[last_ma]:
                count += 1
            else:
                break
        return float(count) / float(total)

    def get_score(self, ccy: str, t: datetime) -> Score:
        """
        计算指定货币在指定时刻的建议仓位分数。
        :param ccy: 货币名称。
        :param t: 将要计算的是 t 之前已经完整结束的一个k柱。
        :return: Score
        """
        index_list = self._index_chart.query(ccy=ccy, bar=self._bar, since=t, until=t, ma_list=self._ma_list)
        index = index_list[-1]
        return Score(ccy=ccy, t=index.t, v=self._calc_score(index), p=index.ma[1], atr=index.atr)

    def get_advice_one(self, raw_position: model.Position, now: datetime) -> model.Trade:
        """

        :param raw_position:
        :param now: 过了一半的时间（不是午夜0点）
        :return:
        """
        yesterday = datetime.combine(now + timedelta(days=-1), datetime.min.time())
        now_score = self.get_score(ccy=raw_position.ccy, t=yesterday)
        return now_score.get_trade(raw_position=raw_position)
