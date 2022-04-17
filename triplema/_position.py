# -*- coding: utf-8 -*-


_db_conn = None


def set_db_conn(db_conn):
    """
    设置一个sqlite3的连接，用于缓存行情数据。
    :param db_conn:
    :return:
    """
    global _db_conn
    _db_conn = db_conn


class Position:
    def __init__(self, ccy: str, crypto: float, usdt: float, last_bill_id: str = None):
        self.ccy = ccy
        self.crypto = crypto
        self.usdt = usdt
        self.last_bill_id = last_bill_id

    def total(self, price: float):
        return self.usdt + self.crypto * price

    def score(self, price: float):
        return 1.0 - self.usdt / self.total(price)


class Repository:
    def __init__(self, db_conn=None):
        self._conn = db_conn or _db_conn
        self._table_name = "position"
        if not self._table_exist():
            self._create_table()
            self._conn.commit()

    def set(self, p: Position):
        if not self._exist_row(p.ccy):
            self._insert_row(p)
        else:
            self._update_row(p)
        self._conn.commit()

    def query(self, ccy: str):
        cur = self._conn.cursor()
        sql = "SELECT ccy, crypto, usdt, last_bill_id FROM {} WHERE ccy={} LIMIT 1".format(
            self._table_name,
            '"' + ccy + '"',
        )
        for row in cur.execute(sql):
            return Position(ccy=row[0], crypto=float(row[1]), usdt=float(row[2]), last_bill_id=row[3])
        else:
            raise NoSuchRecord(sql=sql)

    def query_all(self):
        cur = self._conn.cursor()
        sql = "SELECT ccy, crypto, usdt, last_bill_id FROM {} ORDER BY ccy".format(self._table_name)
        return [Position(ccy=row[0], crypto=float(row[1]), usdt=float(row[2]), last_bill_id=row[3]) for row in
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
            'ccy' VARCHAR,
            'crypto' FLOAT,
            'usdt' FLOAT,
            'last_bill_id' VARCHAR
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

    def _insert_row(self, p: Position):
        cur = self._conn.cursor()
        sql = "INSERT INTO {} (ccy, crypto, usdt, last_bill_id) VALUES({}, {}, {}, NULL)".format(
            self._table_name,
            '"' + p.ccy + '"',
            p.crypto,
            p.usdt
        )
        return cur.execute(sql)

    def _update_row(self, p: Position):
        cur = self._conn.cursor()
        sql = "UPDATE {} SET crypto={}, usdt={}, last_bill_id={} WHERE ccy={}".format(
            self._table_name,
            p.crypto,
            p.usdt,
            self._python_to_sqlite(p.last_bill_id),
            '"' + p.ccy + '"',
        )
        return cur.execute(sql)

    def get_last_bill_id(self):
        cur = self._conn.cursor()
        sql = "SELECT max(last_bill_id) FROM {} WHERE last_bill_id IS NOT NULL".format(self._table_name)
        for row in cur.execute(sql):
            return row[0]
        else:
            raise NoSuchRecord(sql=sql)

    @staticmethod
    def _python_to_sqlite(raw):
        if raw is None:
            return "NULL"
        elif type(raw) is str:
            return '"' + raw + '"'
        else:
            return str(raw)

class NoSuchRecord(Exception):
    def __init__(self, sql):
        self.sql = sql
