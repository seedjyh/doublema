# -*- coding: utf-8 -*-
import sqlite3

from ma.sqlite.exception import NoSuchRecord


class Position:
    def __init__(self, name, crypto: float, usdt: float):
        self.name = name
        self.crypto = crypto
        self.usdt = usdt


class PositionRepository:
    def __init__(self, db_name: str):
        self._conn = sqlite3.connect(db_name)
        self._table_name = "position"
        if not self._table_exist():
            self._create_table()

    def __del__(self):
        self._conn.close()

    def set(self, p: Position):
        if not self._exist_row(p.name):
            self._insert_row(p)
        else:
            self._update_row(p)

    def query(self, name: str):
        cur = self._conn.cursor()
        sql = "SELECT name, crypto, usdt FROM {} WHERE name={} LIMIT 1".format(
            self._table_name,
            '"' + name + '"',
        )
        for row in cur.execute(sql):
            return Position(name=row[0], crypto=float(row[1]), usdt=float(row[2]))
        else:
            raise NoSuchRecord(sql=sql)

    def query_all(self):
        cur = self._conn.cursor()
        sql = "SELECT name, crypto, usdt FROM {} ORDER BY name".format(self._table_name)
        return [Position(name=row[0], crypto=float(row[1]), usdt=float(row[2])) for row in cur.execute(sql)]

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
            'name' VARCHAR,
            'crypto' FLOAT,
            'usdt' FLOAT
        )
        """.format(self._table_name)
        print("create table sql=", sql)
        for row in cur.execute(sql):
            print("create table row>", row)

    def _exist_row(self, name: str) -> bool:
        cur = self._conn.cursor()
        sql = "SELECT name FROM {} WHERE name={} LIMIT 1".format(
            self._table_name,
            '"' + name + '"'
        )
        for _ in cur.execute(sql):
            return True
        else:
            return False

    def _insert_row(self, p: Position):
        cur = self._conn.cursor()
        sql = "INSERT INTO {} (name, crypto, usdt) VALUES({}, {}, {})".format(
            self._table_name,
            '"' + p.name + '"',
            p.crypto,
            p.usdt
        )
        return cur.execute(sql)

    def _update_row(self, p: Position):
        cur = self._conn.cursor()
        sql = "UPDATE {} SET crypto={}, usdt={} WHERE name={}".format(
            self._table_name,
            p.crypto,
            p.usdt,
            '"' + p.name + '"',
        )
        return cur.execute(sql)
