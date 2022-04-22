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


def get_atr(ccy: str, bar: str, t: datetime):
    logger.info("get_atr, ccy={}, bar={}, t={}".format(ccy, bar, t))
    td = const.bar_to_timedelta(bar=bar)
    until = t - td
    since = until - td * _interval
    tr = [c.h() - c.l() for c in _market.query(ccy=ccy, bar=bar, since=since, until=until)]
    return sum(tr) / len(tr)
