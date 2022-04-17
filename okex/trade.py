# -*- coding: utf-8 -*-
from datetime import datetime

import model
from okex import _api

_db_conn = None


def set_db_conn(db_conn):
    """
    设置一个sqlite3的连接，用于缓存数据。
    :param db_conn:
    :return:
    """
    global _db_conn
    _db_conn = db_conn


def query(last_bill_id: str = None):
    """
    查询从 last_bill_id 之后开始的所有成交的币币交易。
    :param last_bill_id: 上次查询的最终账单号。本次查询从这之后开始。
    :return:
    """
    _sync()
    repo = Repo(db_conn=_db_conn)
    return repo.query(last_bill_id=last_bill_id)


def _sync():
    """
    查询本地缓存的交易，并获取从此之后的所有交易。
    :return:
    """
    repo = Repo(db_conn=_db_conn)
    try:
        last_bill_id = repo.get_last().bill_id
    except model.NoSuchRecord:
        last_bill_id = None
    for t in _api.query_trade_fills(last_bill_id=last_bill_id):
        repo.append(t)


class Repo:
    def __init__(self, db_conn):
        self._conn = db_conn
        self._table_name = "trade"
        if not self._table_exist():
            self._create_table()
            self._conn.commit()

    def append(self, t: model.Trade):
        if not self._exist_row(t.bill_id):
            self._insert_row(t)
        else:
            self._update_row(t)
        self._conn.commit()

    def get_last(self) -> model.Trade:
        cur = self._conn.cursor()
        sql = "SELECT bill_id, ccy, price, crypto FROM {} ORDER BY bill_id DESC LIMIT 1".format(
            self._table_name,
        )
        for row in cur.execute(sql):
            return model.Trade(bill_id=row[0], ccy=row[1], price=float(row[2]), crypto=float(row[3]))
        else:
            raise model.NoSuchRecord(sql=sql)

    def query(self, last_bill_id: str):
        cur = self._conn.cursor()
        if last_bill_id is not None:
            where_part = "WHERE bill_id > \"{}\"".format(last_bill_id)
        else:
            where_part = ""
        sql = "SELECT bill_id, ccy, price, crypto FROM {} {} ORDER BY bill_id".format(self._table_name, where_part)
        return [model.Trade(bill_id=row[0], ccy=row[1], price=float(row[2]), crypto=float(row[3])) for row in
                cur.execute(sql)]

    def _table_exist(self):
        cur = self._conn.cursor()
        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name='{}'".format(self._table_name)
        for row in cur.execute(sql):
            return True
        else:
            return False

    def _create_table(self):
        cur = self._conn.cursor()
        sql = """
        CREATE TABLE {} (
            'bill_id' VARCHAR,
            'ccy' VARCHAR,
            'price' FLOAT,
            'crypto' FLOAT
        )
        """.format(self._table_name)
        print("create table sql=", sql)
        for row in cur.execute(sql):
            print("create table row>", row)

    def _exist_row(self, bill_id: str) -> bool:
        cur = self._conn.cursor()
        sql = "SELECT bill_id FROM {} WHERE bill_id={} LIMIT 1".format(
            self._table_name,
            '"' + bill_id + '"'
        )
        for _ in cur.execute(sql):
            return True
        else:
            return False

    def _insert_row(self, t: model.Trade):
        cur = self._conn.cursor()
        sql = "INSERT INTO {} (bill_id, ccy, price, crypto) VALUES({}, {}, {}, {})".format(
            self._table_name,
            '"' + t.bill_id + '"',
            '"' + t.ccy + '"',
            t.price,
            t.crypto,
        )
        return cur.execute(sql)

    def _update_row(self, t: model.Trade):
        cur = self._conn.cursor()
        sql = "UPDATE {} SET ccy={}, price={}, crypto={}} WHERE bill_id={}".format(
            self._table_name,
            '"' + t.ccy + '"',
            t.price,
            t.crypto,
            '"' + t.bill_id + '"',
        )
        return cur.execute(sql)
