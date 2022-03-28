# -*- coding: utf-8 -*-
import statistics

import trend
import database


def get_score(records):
    """
    获取 records 最后一个 Record 的分数
    :param records: LIST<Record>
    :return:
    """
    try:
        return statistics.mean([
            _get_k_ma13_score(records[-1]),
            _get_k_self_score(records),
            _get_ma13_ma55_score(records[-1]),
            _get_ma13_self_score(records),
        ])
    except trend.NoEnoughDataError:
        return None


def _get_k_ma13_score(r: database.Record) -> float:
    if trend.larger(r.k_price, r.ma13_price):
        return 1.0
    elif trend.less(r.k_price, r.ma13_price):
        return 0.0
    else:
        return 0.5


def _get_k_self_score(records) -> float:
    if trend.is_increasing([r.k_price for r in records]):
        return 1.0
    elif trend.is_decreasing([r.k_price for r in records]):
        return 0.0
    else:
        return 0.5


def _get_ma13_ma55_score(r: database.Record) -> float:
    if trend.larger(r.ma13_price, r.ma55_price):
        return 1.0
    elif trend.less(r.ma13_price, r.ma55_price):
        return 0.0
    else:
        return 0.5


def _get_ma13_self_score(records) -> float:
    if trend.is_increasing([r.ma13_price for r in records]):
        return 1.0
    elif trend.is_decreasing([r.ma13_price for r in records]):
        return 0.0
    else:
        return 0.5
