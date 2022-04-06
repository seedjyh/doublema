# -*- coding: utf-8 -*-
import sqlite3
from datetime import datetime

from ma import candle


class CandleChart(candle.CandleChart):
    def __init__(self, db_name: str, ccy: str):
        ccy = ccy.lower()
        self._conn = sqlite3.connect(db_name)
        self._ccy = ccy
        self._table_name = "{}_candle".format(ccy)
        if not self._table_exist():
            self._create_table()

    def __del__(self):
        self._conn.commit()
        self._conn.close()

    def insert_one(self, c: candle.Candle):
        cur = self._conn.cursor()
        sql = "INSERT INTO {}(timestamp, opening, highest, lowest, closing) VALUES({},{},{},{},{});".format(
            self._table_name,
            '"' + self._timestamp_to_str(c.timestamp) + '"',
            c.opening,
            c.highest,
            c.lowest,
            c.closing,
        )
        print("insert one sql=", sql)
        print("insert one res=", cur.execute(sql))

    def insert_multi(self, cs: []):
        for c in cs:
            self.insert_one(c)

    def query(self, since: datetime = None, until: datetime = None) -> []:
        cur = self._conn.cursor()
        since = since or datetime(year=2000, month=1, day=1)
        until = until or datetime(year=2099, month=1, day=1)
        sql = """
            SELECT timestamp, opening, highest, lowest, closing FROM {}
            WHERE timestamp >= {} AND timestamp <= {}
        """.format(
            self._table_name,
            '"' + self._timestamp_to_str(since) + '"',
            '"' + self._timestamp_to_str(until) + '"',
        )
        sql += "order by timestamp"
        res = []
        # print("query sql=", sql)
        for row in cur.execute(sql):
            # print("query row>", row)
            res.append(candle.Candle(
                timestamp=self._str_to_timestamp(row[0]),
                opening=row[1],
                highest=row[2],
                lowest=row[3],
                closing=row[4],
            ))
        return res

    def _table_exist(self):
        cur = self._conn.cursor()
        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name='{}'".format(self._table_name)
        # print("table exist sql=", sql)
        for row in cur.execute(sql):
            # print("table exist row>", row)
            return True
        else:
            return False  # todo: check

    def _create_table(self):
        cur = self._conn.cursor()
        sql = """
        CREATE TABLE {} (
            'timestamp' DATETIME PRIMARY KEY,
            'opening' FLOAT,
            'highest' FLOAT,
            'lowest' FLOAT,
            'closing' FLOAT
        )
        """.format(self._table_name)
        print("create table sql=", sql)
        for row in cur.execute(sql):
            print("create table row>", row)

    @staticmethod
    def _timestamp_to_str(t: datetime) -> str:
        return t.strftime(format="%Y-%m-%d %H:%M:%S")

    @staticmethod
    def _str_to_timestamp(s: str) -> datetime:
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
