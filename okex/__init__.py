# -*- coding: utf-8 -*-
import sqlite3

from okex import trade, market

_db_name = "okex.sqlite_db"
_db_conn = sqlite3.connect(database=_db_name)
trade.set_db_conn(db_conn=_db_conn)
market.set_db_conn(db_conn=_db_conn)
