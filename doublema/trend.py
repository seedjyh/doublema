# -*- coding: utf-8 -*-

class NoEnoughDataError(Exception):
    pass


def larger(a: float, b: float) -> bool:
    return a * 0.999 > b


def less(a: float, b: float) -> bool:
    return a * 1.001 < b


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
