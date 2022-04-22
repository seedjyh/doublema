# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta

import const
from model import Market

_market: Market = None

logger = logging.getLogger(__name__)

def init(market: Market):
    global _market
    _market = market


def get_score(ccy: str, bar: str, t: datetime) -> float:
    logger.info("get_score, ccy={}, bar={}, t={}".format(ccy, bar, t))
    td = const.bar_to_timedelta(bar=bar)
    until = t + timedelta(milliseconds=1)
    since = until - 3 * td
    candles = _market.query(ccy=ccy, bar=bar, since=since, until=until)
    assert len(candles) == 3
    hit = 0
    if candles[0].l() < candles[1].l() and candles[0].h() < candles[1].h():
        hit += 1
    elif candles[0].l() > candles[1].l() and candles[0].h() > candles[1].h():
        hit -= 1
    if candles[1].l() < candles[2].l() and candles[1].h() < candles[2].h():
        hit += 1
    elif candles[1].l() > candles[2].l() and candles[1].h() > candles[2].h():
        hit -= 1
    if candles[1].c() > candles[1].o():
        hit += 1
    elif candles[1].c() < candles[1].o():
        hit -= 1
    if candles[2].c() > candles[2].o():
        hit += 1
    elif candles[2].c() < candles[2].o():
        hit -= 1
    return (hit + 4) / 8
