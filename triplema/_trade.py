# -*- coding: utf-8 -*-
import sqlite3

import model


class Repository:
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

    def query_all(self):
        cur = self._conn.cursor()
        sql = "SELECT bill_id, ccy, price, crypto FROM {} ORDER BY bill_id".format(self._table_name)
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
