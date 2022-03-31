# -*- coding: utf-8 -*-
"""
这里定义了K线图模型。

创建时从文件中读取初始数据。

所有读写操作都在内存中，但调用save可以刷到文件中。

"""
import abc
import datetime
from copy import copy

from ma import command, model
from ma.database import database, csvio


class KLineSpan(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def strip(self, t: datetime.datetime) -> datetime.datetime:
        pass

    @abc.abstractmethod
    def to_string(self, t: datetime.datetime) -> str:
        pass

    @abc.abstractmethod
    def from_string(self, s: str) -> datetime.datetime:
        pass


class DaySpan(KLineSpan):
    """
    按照「天」为单位裁剪。
    """

    def __init__(self):
        # self._format = "%Y-%m-%d %H:%M:%S.%f"
        self._format = "%Y-%m-%d"

    def strip(self, t: datetime.datetime) -> datetime.datetime:
        return datetime.datetime(year=t.year, month=t.month, day=t.day)

    def to_string(self, t: datetime.datetime) -> str:
        return t.strftime(self._format)

    def from_string(self, s: str) -> datetime.datetime:
        return datetime.datetime.strptime(s, self._format)


_span = DaySpan()


class Record:
    def __init__(self, timestamp: datetime.datetime, price: float):
        self.timestamp = timestamp
        self.price = price

    def dict(self):
        return {
            "timestamp": _span.to_string(self.timestamp),
            "price": str(self.price),
        }

    @staticmethod
    def from_dict(d: dict):
        return Record(
            timestamp=_span.from_string(d["timestamp"]),
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
        timestamp = _span.strip(timestamp)
        if self._exist(timestamp):
            raise Exception("try insert but already exist: timestamp={}".format(timestamp))
        self._records.append(Record(timestamp=timestamp, price=price))
        self._sort_records()

    def set_price(self, timestamp: datetime.datetime, price: float):
        timestamp = _span.strip(timestamp)
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
        if since is not None:
            since = _span.strip(since)
        if until is not None:
            until = _span.strip(until)
        # todo: 检查时间戳记录有缺失的情况
        res = []
        for r in self._records:
            if since is not None and r.timestamp < since:
                continue
            if until is not None and r.timestamp > until:
                break
            res.append(model.KLineRecord(timestamp=r.timestamp, price=r.price))
        return res

    def clear(self, reason: str):
        """
        清空内存里的数据。随后调用save将导致原有数据全部丢失。所以仅用于测试时。
        :param reason:
        :return:
        """
        self._records.clear()

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
