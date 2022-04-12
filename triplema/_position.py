# -*- coding: utf-8 -*-
import sqlite3

import model


class PositionRepository(model.PositionRepository):
    def __init__(self, db: str = ":memory:"):
        self._conn = sqlite3.connect(database=db)
        self._table_name = "position"
        if not self._table_exist():
            self._create_table()

    def __del__(self):
        self._conn.commit()
        self._conn.close()

    def set(self, p: model.Position):
        if not self._exist_row(p.ccy):
            self._insert_row(p)
        else:
            self._update_row(p)

    def query(self, ccy: str):
        cur = self._conn.cursor()
        sql = "SELECT ccy, crypto, usdt FROM {} WHERE ccy={} LIMIT 1".format(
            self._table_name,
            '"' + ccy + '"',
        )
        for row in cur.execute(sql):
            return model.Position(ccy=row[0], crypto=float(row[1]), usdt=float(row[2]))
        else:
            raise model.NoSuchRecord(sql=sql)

    def query_all(self):
        cur = self._conn.cursor()
        sql = "SELECT ccy, crypto, usdt FROM {} ORDER BY ccy".format(self._table_name)
        return [model.Position(ccy=row[0], crypto=float(row[1]), usdt=float(row[2])) for row in cur.execute(sql)]

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
            'ccy' VARCHAR,
            'crypto' FLOAT,
            'usdt' FLOAT
        )
        """.format(self._table_name)
        print("create table sql=", sql)
        for row in cur.execute(sql):
            print("create table row>", row)

    def _exist_row(self, ccy: str) -> bool:
        cur = self._conn.cursor()
        sql = "SELECT ccy FROM {} WHERE ccy={} LIMIT 1".format(
            self._table_name,
            '"' + ccy + '"'
        )
        for _ in cur.execute(sql):
            return True
        else:
            return False

    def _insert_row(self, p: model.Position):
        cur = self._conn.cursor()
        sql = "INSERT INTO {} (ccy, crypto, usdt) VALUES({}, {}, {})".format(
            self._table_name,
            '"' + p.ccy + '"',
            p.crypto,
            p.usdt
        )
        return cur.execute(sql)

    def _update_row(self, p: model.Position):
        cur = self._conn.cursor()
        sql = "UPDATE {} SET crypto={}, usdt={} WHERE ccy={}".format(
            self._table_name,
            p.crypto,
            p.usdt,
            '"' + p.ccy + '"',
        )
        return cur.execute(sql)