# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

import triplema.market
import okex.market
from smarter.market import BAR_1D, CCY_BTC
from triplema import _arg


class Score:
    def __init__(self, ccy: str, t: datetime, v: float):
        """

        :param ccy: 货币名称。
        :param t: 所属K柱
        :param v: 浮点数，0.0~1.0，0表示空仓，1表示满仓。
        """
        self.ccy = ccy
        self.t = t
        self.v = v


def calc_score(ccy: str, t: datetime) -> Score:
    """
    计算指定货币在指定时刻的建议仓位分数。
    :param ccy: 货币名称。
    :param t: 将要计算的是 t 之前已经完整结束的一个k柱。
    :return: Score
    """
    market = triplema.market.Market(source=okex.market.Market(ccy=ccy, bar=BAR_1D, db="triplema_okex.sqlite_db"))
    index = market.query(since=t, until=t, ma_list=_arg.ma_list)[-1]
    count = 0
    total = len(index.ma) - 1
    ma_list = [v for v in index.ma.keys()]
    for i in range(len(ma_list)):
        if i == 0:
            continue
        now_ma = ma_list[i]
        last_ma = ma_list[i - 1]
        if index.ma[now_ma] < index.ma[last_ma]:
            count += 1
        else:
            break
    return Score(ccy=ccy, t=index.t, v=float(count) / float(total))
