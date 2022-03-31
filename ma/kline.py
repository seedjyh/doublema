# -*- coding: utf-8 -*-
"""
这里定义了K线图模型。

创建时从文件中读取初始数据。

所有读写操作都在内存中，但调用save可以刷到文件中。

"""
import datetime
from copy import copy

from ma import command
from ma.database import database, csvio


class Record:
    datetime_format = "%Y-%m-%d %H:%M:%S"

    def __init__(self, timestamp: datetime.datetime, price: float):
        self.timestamp = timestamp
        self.price = price

    def dict(self):
        return {
            "timestamp": datetime.datetime.strftime(self.timestamp, self.datetime_format),
            "price": str(self.price),
        }

    @staticmethod
    def from_dict(d: dict):
        return Record(
            timestamp=datetime.datetime.strptime(d["timestamp"], Record.datetime_format),
            price=float(d["price"]),
        )


class KLineChart(command.KLineChart):
    """
    创建时从文件中读取初始数据。
    所有读写操作都在内存中，但调用save可以刷到文件中。
    """

    def __init__(self, name):
        self._name = name
        self._records = self._load_records_from_db(name=name)

    def add_price(self, timestamp: datetime.datetime, price: float):
        if self._exist(timestamp):
            raise Exception("try insert but already exist: timestamp={}".format(timestamp))
        self._records.append(Record(timestamp=timestamp, price=price))
        self._sort_records()

    def set_price(self, timestamp: datetime.datetime, price: float):
        if not self._exist(timestamp):
            raise Exception("try update but not exist: timestamp={}".format(timestamp))
        for i in range(len(self._records)):
            if self._records[i].timestamp == timestamp:
                self._records[i].price = price

    def get_records(self, since=None, until=None) -> []:
        """
        返回command.Record列表。
        :return:
        """
        return [command.KLineRecord(timestamp=r.timestamp, price=r.price) for r in self._records]

    def _sort_records(self):
        self._records.sort(key=lambda r: r.timestamp.timestamp())

    def _exist(self, timestamp: datetime.datetime) -> bool:
        for r in self._records:
            if r.timestamp == timestamp:
                return True
        else:
            return False

    def save(self):
        """
        保存到文件里
        :return:
        """
        self._save_records_to_db(name=self._name, records=self._records)

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
    def _save_records_to_db(name, records: []):
        db = database.Database(
            name=name,
            primary_key="timestamp",
            fields=["timestamp", "price"]
        )
        for r in records:
            db.insert(r.dict())
        csvio.save(db)

    @staticmethod
    def _check_db_format(db: database.Database):
        if db.primary_key() != "timestamp":
            raise Exception("database mismatch!")
