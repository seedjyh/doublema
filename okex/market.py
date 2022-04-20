# -*- coding: utf-8 -*-

"""
market 实现了 model.Market 接口访问Okex交易所并下载行情数据的功能。

依赖repo.Repo做缓存或存储，但自己不实现。
"""
import logging
from datetime import datetime, timedelta

import const
import model
from okex import _api

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

_db_conn = None


def set_db_conn(db_conn):
    """
    设置一个sqlite3的连接，用于缓存行情数据。
    :param db_conn:
    :return:
    """
    global _db_conn
    _db_conn = db_conn


def query(ccy: str, bar: str, since: datetime, until: datetime):
    print("method query", ccy, bar, since, until)
    """
    查询指定标的、指定K线粒度，K柱起点从since（含）到until（不含）的所有K柱，按照K柱时间顺序排列。
    :param ccy: 标的。
    :param bar: K线粒度。
    :param since: 起点时间（含）
    :param until: 终点时间（不含）
    :return:
    """
    now = datetime.now()
    bar_timedelta = const.bar_to_timedelta(bar)
    if now.timestamp() - until.timestamp() < bar_timedelta.total_seconds():
        until -= bar_timedelta
    repo = Repo(ccy=ccy, bar=bar, db_conn=_db_conn)
    res = repo.query(since=since, until=until)
    if len(res) > 0 and res[0].t().timestamp() < since.timestamp() + bar_timedelta.total_seconds() and \
            res[-1].t().timestamp() >= until.timestamp() - bar_timedelta.total_seconds():
        return res
    res = []
    max_api_bar_range = 100  # api限制，最多100条
    now_since = since
    while now_since < until:
        api_since = now_since
        api_until = min(api_since + max_api_bar_range * bar_timedelta, until)
        api_res = _api.query_market_candles(ccy=ccy, bar=bar, since=api_since, until=api_until)
        res += api_res
        now_since = api_until
    saving_res = [c for c in api_res if c.t() + bar_timedelta <= now]
    repo.save(candles=saving_res)
    res.sort(key=lambda candle: candle.t())
    return res


class Market(model.Market):
    """
    为了兼容而保留的一个包装类。
    """

    def __init__(self):
        self.cache = []

    def query(self, ccy: str, bar: str, since: datetime, until: datetime):
        _offset = timedelta(days=90)  # 每次故意多查一点，备用
        if len(self.cache) == 0 or since < self.cache[0].t() or until > self.cache[-1].t():
            self.cache = query(ccy, bar, since - _offset, until)
        return [c for c in self.cache if since <= c.t() < until]


class Repo:
    def __init__(self, ccy: str, bar: str, db_conn=None):
        self._ccy = ccy
        self._bar = bar
        self._db_conn = db_conn or _db_conn
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

    def _save_one(self, candle: model.Candlestick):
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
            res.append(model.Candlestick(
                t=self._str_to_timestamp(row[0]),
                o=row[1],
                h=row[2],
                l=row[3],
                c=row[4],
            ))
        return res

    def _query_one(self, t: datetime) -> model.Candlestick:
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
            return model.Candlestick(
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

    def _insert_one(self, c: model.Candlestick):
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
