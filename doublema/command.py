# -*- coding: utf-8 -*-
"""
主函数要执行的命令都在这里。
"""
import abc

import database
import display
import strategy


class Command(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def execute(self):
        pass


class Add(Command):
    def __init__(self, db: database.Database, record: database.Record):
        self._db = db
        self._record = record

    def execute(self):
        self._db.add_record(self._record)


class Set(Command):
    def __init__(self, db: database.Database, record: database.Record):
        self._db = db
        self._record = record

    def execute(self):
        self._db.set_record(self._record)


class Show(Command):
    def __init__(self, db: database.Database):
        self._db = db

    def execute(self):
        records = self._db.records()
        self.show(records)
        print("Last score:", strategy.get_score(records))

    @staticmethod
    def show(records):
        display.display(
            [{**records[i].dict(), "score": strategy.get_score(records[:i + 1])} for i in range(len(records))])
