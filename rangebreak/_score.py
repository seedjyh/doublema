# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta
from deprecated import deprecated
import const
from model import Market, Candlestick

_market: Market = None

logger = logging.getLogger(__name__)

_need_bar = 3  # 计算分数所需的candle 的数量。


def need_bar() -> int:
    return _need_bar


def init(market: Market):
    global _market
    _market = market


class ClosingScore:
    """
    某一天结束后，这一天的分数。
    """

    def __init__(self, t: datetime, score: float):
        self.t = t
        self.score = score


def get_scores(ccy: str, bar: str, since: datetime, until: datetime):
    """
    查询一个区间的所有score
    :param ccy:
    :param bar:
    :param since:
    :param until:
    :return: list of ClosingScore order by t increasing （since <= t < until)
    """
    td = const.bar_to_timedelta(bar=bar)
    market_since = since - _need_bar * td
    market_until = until
    candles = _market.query(ccy=ccy, bar=bar, since=market_since, until=market_until)
    for i in range(len(candles)):
        if candles[i].t() >= since:
            yield _get_score_by_candles(candles=candles[:i + 1])


def _get_score_by_candles(candles: []) -> ClosingScore:
    """
    计算candles列表的最后一个candle的时间的closing score
    :param candles:
    :return:
    """
    if len(candles) < _need_bar:
        raise Exception("no enough candles")
    candles = candles[-_need_bar:]
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
    return ClosingScore(t=candles[2].t(), score=(hit + 4) / 8)
