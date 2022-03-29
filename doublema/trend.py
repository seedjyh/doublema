# -*- coding: utf-8 -*-

class NoEnoughDataError(Exception):
    pass


def larger(a: float, b: float) -> bool:
    return a * 0.9 > b


def less(a: float, b: float) -> bool:
    return a < b * 0.9


def is_increasing(values):
    if len(values) < 2:
        raise NoEnoughDataError
    last = values[-2]
    now = values[-1]
    return larger(now, last)


def is_decreasing(values):
    if len(values) < 2:
        raise NoEnoughDataError
    last = values[-2]
    now = values[-1]
    return larger(last, now)
