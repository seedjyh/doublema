# -*- coding: utf-8 -*-
from datetime import datetime

import model
from triplema import _score


class Record:
    def __init__(self, ts: datetime, crypto: float, usdt: float, total: float, closing: float, score: float, atr: float):
        """

        :param ts: 日期
        :param crypto: 当天开始时的币数
        :param usdt: 当天开始时的U数
        :param total: 当天开始时的总价值
        :param closing: 当天收盘价
        :param score: 当天最终分数
        :param atr: 真实波动均值
        """
        self.ts = ts
        self.crypto = crypto
        self.usdt = usdt
        self.total = total
        self.closing = closing
        self.score = score
        self.atr = atr


def playback(ccy: str, market: model.Market, bar: str, ma_list: [], since: datetime, until: datetime) -> []:
    p = model.Position(ccy=ccy, crypto=0, usdt=1000)
    evaluator = _score.Evaluator(source=market, bar=bar, ma_list=ma_list)
    for candle in market.query(ccy=ccy, bar=bar, since=since, until=until):
        price = candle.c()
        t = candle.t()
        score = evaluator.get_score(ccy=ccy, t=t)
        trade = score.get_trade(raw_position=p)
        yield Record(
            ts=t,
            crypto=p.crypto,
            usdt=p.usdt,
            total=p.total(price=price),
            closing=price,
            score=score.v,
            atr=score.atr,
        )
        p.crypto += trade.crypto
        p.usdt -= trade.price * trade.crypto
