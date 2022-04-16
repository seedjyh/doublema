# -*- coding: utf-8 -*-
from datetime import datetime

from okex import _api


def query(last_bill_id: str):
    trades = _api.query_trade(last_bill_id=last_bill_id)
    for t in trades:
        print(t.__dict__)
    return trades
