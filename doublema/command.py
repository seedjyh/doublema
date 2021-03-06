# -*- coding: utf-8 -*-
"""
主函数要执行的命令都在这里。
"""
import abc

from doublema import database, display, strategy


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
        self._strategy = strategy.Strategy()

    def execute(self):
        records = self._db.records()
        display.display(
            [{**records[i].dict(), "score": self._strategy.get_score(records[:i + 1])} for i in range(len(records))])


class Playback(Command):
    def __init__(self, db: database.Database, crypto=0.0, usdt=1000.0):
        self._db = db
        self._crypto = crypto
        self._usdt = usdt
        self._strategy = strategy.Strategy()

    def execute(self):
        crypto = self._crypto
        usdt = self._usdt
        records = []
        for i in range(len(self._db.records())):
            new_record = {**self._db.records()[i].dict()}
            score = self._strategy.get_score(self._db.records()[:i + 1])
            new_record["score"] = score
            if score is not None:
                crypto, usdt = self._trade(crypto, usdt, self._db.records()[i].k_price, score)
            new_record["playback_crypto"] = crypto
            new_record["playback_usdt"] = usdt
            new_record["playback_total"] = crypto * self._db.records()[i].k_price + usdt
            records.append(new_record)
        display.display(records)

    @staticmethod
    def _trade(crypto: float, usdt: float, price: float, score: float):
        total = crypto * price + usdt
        crypto = total * score / price
        usdt = total * (1.0 - score)
        return crypto, usdt


class Advice(Command):
    def __init__(self, db: database.Database):
        self._db = db
        self._strategy = strategy.Strategy()

    def execute(self):
        baseline_date = None
        baseline_crypto = None
        baseline_usdt = None
        for r in self._db.records():
            if r.crypto_balance is not None and r.usdt_balance is not None:
                baseline_date = r.date
                baseline_crypto = r.crypto_balance
                baseline_usdt = r.usdt_balance
        print("[ {} ] crypto: {}, usdt: {}".format(baseline_date, baseline_crypto, baseline_usdt))
        baseline_account = strategy.Account(
            crypto_name=self._db.crypto_name(),
            crypto_balance=baseline_crypto,
            usdt_balance=baseline_usdt,
        )
        today_record = self._db.records()[-1]
        today_score = self._strategy.get_score(self._db.records())
        print("[ {} ] score: {}".format(today_record.date, today_score))
        trade = self._strategy.get_advice_trade(
            account=baseline_account,
            score=today_score,
            price=today_record.k_price,
        )
        print(" ---ADVICE--- ")
        display.display([trade.__dict__(), ])
