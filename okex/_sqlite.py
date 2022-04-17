# -*- coding: utf-8 -*-
import sqlite3
from datetime import datetime

from model import Candlestick

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

_db_name = "okex.sqlite_db"
_module_db_conn = sqlite3.connect(database=_db_name)


class MarketRepo:
    def __init__(self, ccy: str, bar: str, db_conn=None):
        self._ccy = ccy
        self._bar = bar
        self._db_conn = db_conn or _module_db_conn
        table_name = self.table_name(ccy, bar)
        self._table_name = table_name
        if not self._table_exist(table_name=table_name):
            self._create_table(table_name=table_name)
        self._db_conn.commit()

    def save(self, candles: []):
        """
        将所有candles保存到数据库。
        :param candles: Candlestick列表
        :return: 无
        """
        for c in candles:
            self._save_one(c)
        self._db_conn.commit()

    def _save_one(self, candle: Candlestick):
        try:
            _ = self._query_one(t=candle.t())
            pass  # 如果数据已存在，不覆盖，直接返回
        except NoSuchRecord:
            self._insert_one(candle)

    def query(self, since: datetime = None, until: datetime = None) -> []:
        """
        查询指定范围数据。
        :param since:
        :param until:
        :return: Candlestick 列表
        """
        cur = self._db_conn.cursor()
        since = since or datetime(year=2000, month=1, day=1)
        until = until or datetime(year=2099, month=1, day=1)
        sql = """
            SELECT timestamp, opening, highest, lowest, closing FROM {}
            WHERE timestamp >= {} AND timestamp < {}
        """.format(
            self._table_name,
            '"' + self._timestamp_to_str(since) + '"',
            '"' + self._timestamp_to_str(until) + '"',
        )
        sql += "order by timestamp"
        res = []
        logger.debug("query sql={}".format(sql))
        for row in cur.execute(sql):
            logger.debug("query row={}".format(row))
            res.append(Candlestick(
                t=self._str_to_timestamp(row[0]),
                o=row[1],
                h=row[2],
                l=row[3],
                c=row[4],
            ))
        return res

    def _query_one(self, t: datetime) -> Candlestick:
        cur = self._db_conn.cursor()
        sql = """
            SELECT timestamp, opening, highest, lowest, closing FROM {}
            WHERE timestamp = {}
        """.format(
            self._table_name,
            '"' + self._timestamp_to_str(t) + '"',
        )
        logger.debug("query sql={}".format(sql))
        for row in cur.execute(sql):
            logger.debug("query row: {}".format(row))
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
        cur = self._db_conn.cursor()
        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name='{}'".format(table_name)
        logger.debug("table exist sql={}".format(sql))
        for row in cur.execute(sql):
            logger.debug("table exist row: {}".format(row))
            return True
        else:
            return False  # todo: check

    def _create_table(self, table_name: str):
        cur = self._db_conn.cursor()
        sql = """
            CREATE TABLE {} (
                'timestamp' DATETIME PRIMARY KEY,
                'opening' FLOAT,
                'highest' FLOAT,
                'lowest' FLOAT,
                'closing' FLOAT
            )
            """.format(table_name)
        logger.debug("create table sql={}".format(sql))
        for row in cur.execute(sql):
            logger.debug("create table row={}".format(row))

    @staticmethod
    def table_name(ccy: str, bar: str) -> str:
        return "{}_market_{}".format(ccy, bar).lower()

    @staticmethod
    def _timestamp_to_str(t: datetime) -> str:
        return t.strftime(format="%Y-%m-%d %H:%M:%S.%f")

    @staticmethod
    def _str_to_timestamp(s: str) -> datetime:
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S.%f")

    def _insert_one(self, c: Candlestick):
        cur = self._db_conn.cursor()
        sql = "INSERT INTO {}(timestamp, opening, highest, lowest, closing) VALUES({},{},{},{},{});".format(
            self._table_name,
            '"' + self._timestamp_to_str(c.t()) + '"',
            c.o(),
            c.h(),
            c.l(),
            c.c(),
        )
        res = cur.execute(sql)
        logger.debug("insert one, sql={}, res={}".format(sql, res))


class NoSuchRecord(Exception):
    def __init__(self, sql):
        self.sql = sql
