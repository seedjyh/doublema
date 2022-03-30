# -*- coding: utf-8 -*-
"""
这里定义了K线图模型。

创建时从文件中读取初始数据。

所有读写操作都在内存中，但调用save可以刷到文件中。

"""
import datetime
from copy import copy

from ma.database import database, csvio


class Record:
    def __init__(self, timestamp: datetime.datetime, closing: float):
        self.timestamp = timestamp
        self.closing = closing
        self.ma = {}

    def dict(self):
        return {
            "timestamp": str(self.timestamp),
            "closing": str(self.closing),
        }

    @staticmethod
    def from_dict(d: dict):
        return Record(
            timestamp=d["timestamp"],
            closing=d["closing"],
        )


class FullData:
    """
    包含0个或多个 MA 的数据。
    """

    def __init__(self, timestamp: datetime.datetime, closing: float, ma: {}):
        self.timestamp = timestamp
        self.closing = closing
        self.ma = ma


class KLineChart:
    """
    创建时从文件中读取初始数据。
    所有读写操作都在内存中，但调用save可以刷到文件中。
    """

    def __init__(self, name):
        self._name = name
        self._records = self._load_records_from_db(name=name)

    def save(self):
        """
        保存到文件里
        :return:
        """
        self._save_records_to_db(self._name, self._records)

    def add_closing(self, timestamp: datetime.datetime, closing: float):
        if self._exist(timestamp):
            raise Exception("try insert but already exist: timestamp={}".format(timestamp))
        self._records.append(Record(timestamp=timestamp, closing=closing))
        self._sort_records()

    def set_closing(self, timestamp: datetime.datetime, closing: float):
        if not self._exist(timestamp):
            raise Exception("try update but not exist: timestamp={}".format(timestamp))
        for i in range(len(self._records)):
            if self._records[i].timestamp == timestamp:
                self._records[i].closing = closing

    def get_records(self, ma_parameter: []) -> []:
        """
        返回带有ma值的Record列表。
        统计ma的时候不考虑timestamp是否连续。
        :return:
        """
        records = [copy(r) for r in self._records]
        for p in ma_parameter:
            closing_sum = 0.0
            for i in range(len(records)):
                closing_sum += records[i].closing
                if i - p >= 0:
                    closing_sum -= records[i - p].closing
                records[i].ma[p] = closing_sum / min(i + 1, p)
        return records

    def _sort_records(self):
        self._records.sort(key=lambda r: r.timestamp)

    def _exist(self, timestamp: datetime.datetime) -> bool:
        for r in self._records:
            if r.timestamp == timestamp:
                return True
        else:
            return False

    @staticmethod
    def _load_records_from_db(name) -> []:
        records = []
        try:
            db = csvio.load(name)
            KLineChart._check_db_format(db)
            for db_value in db.values():
                records.append(Record.from_dict(db_value))
        except FileNotFoundError:
            pass
        return records

    @staticmethod
    def _save_records_to_db(self, name, records: []):
        db = database.Database(
            name=name,
            primary_key="timestamp",
            fields=["timestamp", "closing"]
        )
        for r in records:
            db.insert(r.dict())
        csvio.save(db)

    @staticmethod
    def _check_db_format(db: database.Database):
        if db.primary_key() != "timestamp":
            raise Exception("database mismatch!")
