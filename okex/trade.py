# -*- coding: utf-8 -*-
from datetime import datetime

from okex import _api


def query(last_bill_id: str = None):
    """
    查询从 last_bill_id 之后开始的所有成交的币币交易。
    :param last_bill_id: 上次查询的最终账单号。本次查询从这之后开始。
    :return:
    """
    trades = _api.query_trade_fills(last_bill_id=last_bill_id)
    for t in trades:
        print(t.__dict__)
    return trades
