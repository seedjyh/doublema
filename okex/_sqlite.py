# -*- coding: utf-8 -*-
import sqlite3
from datetime import datetime

from model import Candlestick


class Repo:
    def __init__(self, ccy: str, bar: str, db: str = ":memory:"):
        self._ccy = ccy
        self._bar = bar
        self._conn = sqlite3.connect(database=db)
        table_name = self.table_name(ccy, bar)
        self._table_name = table_name
        if not self._table_exist(table_name=table_name):
            self._create_table(table_name=table_name)

    def __del__(self):
        self._conn.commit()
        self._conn.close()

    def save(self, candles: []):
        for c in candles:
            self._save_one(c)

    def _save_one(self, candle: Candlestick):
        try:
            _ = self._query_one(t=candle.t())
            pass  # 如果数据已存在，不覆盖，直接返回
        except NoSuchRecord:
            self._insert_one(candle)

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
            res.append(Candlestick(
                t=self._str_to_timestamp(row[0]),
                o=row[1],
                h=row[2],
                l=row[3],
                c=row[4],
            ))
        return res

    def _query_one(self, t: datetime) -> Candlestick:
        cur = self._conn.cursor()
        sql = """
            SELECT timestamp, opening, highest, lowest, closing FROM {}
            WHERE timestamp = {}
        """.format(
            self._table_name,
            '"' + self._timestamp_to_str(t) + '"',
        )
        # print("query sql=", sql)
        for row in cur.execute(sql):
            # print("query row>", row)
            return Candlestick(
                t=self._str_to_timestamp(row[0]),
                o=row[1],
                h=row[2],
                l=row[3],
                c=row[4],
            )
        else:
            raise NoSuchRecord(sql=sql)

    def _table_exist(self, table_name: str):
        cur = self._conn.cursor()
        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name='{}'".format(table_name)
        # print("table exist sql=", sql)
        for row in cur.execute(sql):
            # print("table exist row>", row)
            return True
        else:
            return False  # todo: check

    def _create_table(self, table_name: str):
        cur = self._conn.cursor()
        sql = """
            CREATE TABLE {} (
                'timestamp' DATETIME PRIMARY KEY,
                'opening' FLOAT,
                'highest' FLOAT,
                'lowest' FLOAT,
                'closing' FLOAT
            )
            """.format(table_name)
        print("create table sql=", sql)
        for row in cur.execute(sql):
            print("create table row>", row)

    @staticmethod
    def table_name(ccy: str, bar: str) -> str:
        return "{}_market_{}".format(ccy, bar).lower()

    @staticmethod
    def _timestamp_to_str(t: datetime) -> str:
        return t.strftime(format="%Y-%m-%d %H:%M:%S")

    @staticmethod
    def _str_to_timestamp(s: str) -> datetime:
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")

    def _insert_one(self, c: Candlestick):
        cur = self._conn.cursor()
        sql = "INSERT INTO {}(timestamp, opening, highest, lowest, closing) VALUES({},{},{},{},{});".format(
            self._table_name,
            '"' + self._timestamp_to_str(c.t()) + '"',
            c.o(),
            c.h(),
            c.l(),
            c.c(),
        )
        print("insert one sql=", sql)
        print("insert one res=", cur.execute(sql))


class NoSuchRecord(Exception):
    def __init__(self, sql):
        self.sql = sql
