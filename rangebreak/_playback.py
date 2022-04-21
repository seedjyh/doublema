# -*- coding: utf-8 -*-
from datetime import datetime

from model import Market
from rangebreak import _score, _atr

_market: Market = None


def init(market: Market):
    global _market
    _market = market


class Record:
    def __init__(self, ts: datetime, open_crypto: float, open_usdt: float, open_unit: float, closing_atr: float,
                 closing_price: float,
                 closing_total: float, closing_score: float):
        self.ts = ts
        self.open_crypto = open_crypto
        self.open_usdt = open_usdt
        self.open_unit = open_unit
        self.closing_atr = closing_atr
        self.closing_price = closing_price
        self.closing_total = closing_total
        self.closing_score = closing_score


def playback(ccy: str, bar: str):
    crypto = 0.0
    usdt = 1000.0
    unit = 0
    since = datetime(year=2022, month=1, day=1)
    until = datetime.now()
    _score.init(market=_market)
    candles = _market.query(ccy=ccy, bar=bar, since=since, until=until)
    for c in candles:
        closing_atr = _atr.get_atr(ccy=ccy, bar=bar, t=c.t())
        closing_price = c.c()
        closing_score = _score.get_score(ccy=ccy, bar=bar, t=c.t())
        closing_total = crypto * closing_price + usdt
        # 返回 bar 结束时的情况
        yield Record(ts=c.t(), open_crypto=crypto, open_usdt=usdt, open_unit=unit, closing_atr=closing_atr,
                     closing_price=closing_price,
                     closing_total=closing_total, closing_score=closing_score)
        # bar 结束后，立刻进行交易
        closing_atr = _atr.get_atr(ccy=ccy, bar=bar, t=c.t())
        closing_each = _get_each(total=closing_total, atr=closing_atr)
        if closing_score > 0.7:
            # 平空，开多
            if unit < 0:
                usdt += crypto * closing_price
                crypto = 0
                unit = 0
            if unit < 4:
                usdt -= closing_each * closing_price
                crypto += closing_each
                unit += 1
        elif closing_score < 0.3:
            # 平多，开空
            if unit > 0:
                usdt += crypto * closing_price
                crypto = 0
                unit = 0
            if unit > -4:
                usdt += closing_each * closing_price
                crypto -= closing_each
                unit -= 1
        else:
            # 全平
            usdt += crypto * closing_price
            crypto = 0
            unit = 0


def _get_each(total: float, atr: float):
    """
    计算每个头寸单位对应的ccy数量。（注意，不是usdt数量）
    :param total: 目前总资产
    :param atr: 当前ATR
    :param price: 当前价格
    :return: 头寸单位对应的币数量
    """
    if total < 0:
        # raise Exception("no money any more")
        return 0.0
    return total * 0.01 / atr  # 0.01 表示每个单位的ATR波动应该损失1%的总资产
