# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

import model
from triplema import _index


class Score:
    def __init__(self, ccy: str, t: datetime, v: float, p: float):
        """

        :param ccy: 货币名称。
        :param t: 所属K柱
        :param v: 浮点数，0.0~1.0，0表示空仓，1表示满仓。
        :param p: 价格。
        """
        self.ccy = ccy
        self.t = t
        self.v = v
        self.p = p


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

    def calc_score(self, ccy: str, t: datetime) -> Score:
        """
        计算指定货币在指定时刻的建议仓位分数。
        :param ccy: 货币名称。
        :param t: 将要计算的是 t 之前已经完整结束的一个k柱。
        :return: Score
        """
        index_list = self._index_chart.query(ccy=ccy, bar=self._bar, since=t, until=t, ma_list=self._ma_list)
        index = index_list[-1]
        return Score(ccy=ccy, t=index.t, v=self._calc_score(index), p=index.ma[1])

    def get_advice_one(self, raw_position: model.Position, t: datetime):
        try:
            t = datetime.combine(t + timedelta(days=-1), datetime.min.time())
            now_score = self.calc_score(ccy=raw_position.ccy, t=t)
            total = raw_position.total(price=now_score.p)
            expect_crypto = total * now_score.v / now_score.p
            if now_score.p * abs(expect_crypto - raw_position.crypto) < 1.0:
                print("--")
            elif expect_crypto > raw_position.crypto:
                buy_crypto = expect_crypto - raw_position.crypto
                cost = buy_crypto * now_score.p
                print("Buy, ccy={}, crypto=+{}, usdt=-{}".format(raw_position.ccy, buy_crypto, cost))
            elif expect_crypto < raw_position.crypto:
                sell_crypto = raw_position.crypto - expect_crypto
                receive = sell_crypto * now_score.p
                print("Sell, ccy={}, crypto=-{}, usdt=+{}".format(raw_position.ccy, sell_crypto, receive))
        except Exception as e:
            print("ERR: exception {}".format(e))
            raise
