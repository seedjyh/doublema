# -*- coding: utf-8 -*-
import logging
import sqlite3

from model import Trade
from okex.trade import set_db_conn, query

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

#
# def test_query():
#     # 注意，这个测试只有 2022-04-17 20:58:39 开始没有新交易时才有效。
#     db_conn = sqlite3.connect(database=":memory:")
#     set_db_conn(db_conn)
#     trades = query(last_bill_id="435607391688867841")
#     assert len(trades) == 3
#     assert trades[0].__dict__ == Trade(ccy="xmr", price=233.79, crypto=-0.123668, bill_id='435607463918977025').__dict__
#     assert trades[1].__dict__ == Trade(ccy="xrp", price=0.77057, crypto=-1.039431, bill_id='435607531526963204').__dict__
#     assert trades[2].__dict__ == Trade(ccy="xrp", price=0.77054, crypto=-3.260116, bill_id='435607531526963208').__dict__
