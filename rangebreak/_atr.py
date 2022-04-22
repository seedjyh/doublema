# -*- coding: utf-8 -*-
import logging
from datetime import datetime

import const
from model import Market

_interval = 20
_market: Market = None

logger = logging.getLogger(__name__)


def init(market: Market):
    global _market
    _market = market


def need_bar() -> int:
    return _interval


class ClosingATR:
    def __init__(self, t: datetime, atr: float):
        self.t = t
        self.atr = atr


def get_atrs(ccy: str, bar: str, since: datetime, until: datetime):
    td = const.bar_to_timedelta(bar=bar)
    market_since = since - td * _interval
    market_until = until
    candles = _market.query(ccy=ccy, bar=bar, since=market_since, until=market_until)
    for i in range(len(candles)):
        if i >= _interval:
            yield _get_atr_by_candles(candles[:i + 1])


def _get_atr_by_candles(candles: []) -> ClosingATR:
    if len(candles) < _interval:
        raise Exception("no enough candles")
    tr = [c.h() - c.l() for c in candles[-_interval:]]
    return ClosingATR(t=candles[-1], atr=sum(tr) / len(tr))
