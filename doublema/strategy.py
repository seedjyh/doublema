# -*- coding: utf-8 -*-
import statistics

from doublema import trend, database, display


class Account:
    def __init__(self, crypto_name, crypto_balance, usdt_balance):
        self.crypto_name = crypto_name
        self.crypto_balance = crypto_balance
        self.usdt_balance = usdt_balance

    def show(self):
        record = {self.crypto_name: self.crypto_balance, "USDT": self.usdt_balance}
        display.display([record, ])


class Trade:
    def __init__(self, crypto_name, price, crypto_diff, usdt_diff):
        self._crypto_name = crypto_name
        self._price = price
        self._crypto_diff = crypto_diff
        self._usdt_diff = usdt_diff
        if abs(crypto_diff * price + usdt_diff) > 0.001:
            raise Exception(
                "Invalid trade parameter: price={}, crypto_diff={}, usdt_diff={}".format(price, crypto_diff, usdt_diff))

    def __dict__(self):
        return {
            "name": self._crypto_name,
            "op": self.get_operation(),
            "crypto": self.diff_to_str(self._crypto_diff),
            "usdt": self.diff_to_str(self._usdt_diff),
        }

    def get_operation(self):
        if abs(self._usdt_diff) < 0.001:
            return "---"
        if self._usdt_diff > 0:
            return "SELL"
        else:
            return "BUY"

    @staticmethod
    def diff_to_str(diff: float):
        if diff < 0:
            return str(diff)
        elif diff > 0:
            return "+" + str(diff)
        else:
            return "0"

    def __eq__(self, other):
        return self.__dict__() == other.__dict__()


class Strategy:
    def __init__(self):
        pass

    def get_score(self, records):
        """
        获取 records 最后一个 Record 的分数
        :param records: LIST<Record>
        :return:
        """
        try:
            scores = [
                self._get_k_ma13_score(records[-1]),
                self._get_ma13_score(records),
                self._get_ma13_ma55_score(records[-1]),
                self._get_ma55_score(records),
            ]
            return statistics.mean(scores)
        except trend.NoEnoughDataError:
            return None

    @staticmethod
    def _get_k_ma13_score(r: database.Record) -> float:
        if trend.larger(r.k_price, r.ma13_price):
            return 1.0
        elif trend.less(r.k_price, r.ma13_price):
            return 0.0
        else:
            return 0.5

    @staticmethod
    def _get_ma13_score(records) -> float:
        if trend.is_increasing([r.ma13_price for r in records]):
            return 1.0
        elif trend.is_decreasing([r.ma13_price for r in records]):
            return 0.0
        else:
            return 0.5

    @staticmethod
    def _get_ma13_ma55_score(r: database.Record) -> float:
        if trend.larger(r.ma13_price, r.ma55_price):
            return 1.0
        elif trend.less(r.ma13_price, r.ma55_price):
            return 0.0
        else:
            return 0.5

    @staticmethod
    def _get_ma55_score(records) -> float:
        if trend.is_increasing([r.ma55_price for r in records]):
            return 1.0
        elif trend.is_decreasing([r.ma55_price for r in records]):
            return 0.0
        else:
            return 0.5

    @staticmethod
    def get_advice_trade(account: Account, score: float, price: float) -> Trade:
        total_usdt = account.crypto_balance * price + account.usdt_balance
        new_account = Account(
            crypto_name=account.crypto_name,
            crypto_balance=total_usdt * score / price,
            usdt_balance=total_usdt * (1.0 - score),
        )
        return Trade(
            crypto_name=account.crypto_name,
            price=price,
            crypto_diff=new_account.crypto_balance - account.crypto_balance,
            usdt_diff=new_account.usdt_balance - account.usdt_balance,
        )
