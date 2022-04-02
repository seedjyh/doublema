# -*- coding: utf-8 -*-

"""
仓位历史表
"""
import datetime

from ma import model
from ma.database import database, csvio
from ma.span import SecondSpan

_span = SecondSpan()


class Record:
    def __init__(self, timestamp: datetime.datetime, crypto: float, usdt: float):
        self.timestamp = _span.strip(timestamp)
        self.crypto = crypto
        self.usdt = usdt

    def dict(self):
        return {
            "timestamp": _span.to_string(self.timestamp),
            "crypto": str(self.crypto),
            "usdt": str(self.usdt),
        }

    @staticmethod
    def from_dict(d: dict):
        return Record(
            timestamp=_span.from_string(d["timestamp"]),
            crypto=float(d["crypto"]),
            usdt=float(d["usdt"]),
        )


class PositionHistory:
    def __init__(self, name: str):
        self._name = name
        self._db_name = name + ".position"
        self._records = self._load_records_from_db(name=self._db_name)

    def add_record(self, record: model.PositionRecord):
        self._records.append(
            Record(timestamp=record.timestamp, crypto=record.position.crypto, usdt=record.position.usdt))
        self._sort_records()

    def get_records(self, since=None, until=None) -> []:
        """
        返回 model.PositionRecord 列表。
        :return:
        """
        if since is not None:
            since = _span.strip(since)
        if until is not None:
            until = _span.strip(until)
        res = []
        for r in self._records:
            if since is not None and r.timestamp < since:
                continue
            if until is not None and r.timestamp > until:
                break
            res.append(
                model.PositionRecord(
                    timestamp=r.timestamp,
                    position=model.Position(
                        name=self._name,
                        crypto=r.crypto,
                        usdt=r.usdt,
                    )
                )
            )
        return res

    def save(self):
        """
        保存到文件里
        :return:
        """
        self._save_records_to_db(name=self._db_name, records=self._records)

    @staticmethod
    def _load_records_from_db(name) -> []:
        records = []
        try:
            db = csvio.load(name)
            PositionHistory._check_db_format(db)
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
            fields=["timestamp", "crypto", "usdt"]
        )
        for r in records:
            db.insert(r.dict())
        csvio.save(db)

    @staticmethod
    def _check_db_format(db: database.Database):
        if db.primary_key() != "timestamp":
            raise Exception("database mismatch!")

    def _sort_records(self):
        self._records.sort(key=lambda r: r.timestamp.timestamp())

    def clear(self, reason: str):
        """
        清空内存里的数据。随后调用save将导致原有数据全部丢失。所以仅用于测试时。
        :param reason:
        :return:
        """
        self._records.clear()
