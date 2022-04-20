# -*- coding: utf-8 -*-
from datetime import datetime

import const
from model import Market

_market: Market = None


def init(market: Market):
    global _market
    _market = market


def get_score(ccy: str, bar: str, t: datetime) -> float:
    td = const.bar_to_timedelta(bar=bar)
    until = t - td
    since = until - 3 * td
    candles = _market.query(ccy=ccy, bar=bar, since=since, until=until)
    if candles[0].l() < candles[1].l() < candles[2].l() and candles[0].h() < candles[1].h() < candles[2].h():
        return 1.0
    if candles[0].l() > candles[1].l() > candles[2].l() and candles[0].h() > candles[1].h() > candles[2].h():
        return -1.0
    return 0.0
