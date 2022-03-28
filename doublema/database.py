# -*- coding: utf-8 -*-
import csv
import os
import shutil

import display


class Price:
    def __init__(self, field: str):
        self._value = float(field)


class Record:
    def __init__(self, date, k_price=None, ma13_price=None, ma55_price=None, crypto_balance=None, usdt_balance=None):
        self.date = date
        self.k_price = k_price
        self.ma13_price = ma13_price
        self.ma55_price = ma55_price
        self.crypto_balance = crypto_balance
        self.usdt_balance = usdt_balance

    def dict(self) -> dict:
        return {
            "date": self.date,
            "k_price": self.k_price,
            "ma13_price": self.ma13_price,
            "ma55_price": self.ma55_price,
            "crypto_balance": self.crypto_balance,
            "usdt_balance": self.usdt_balance,
        }

    def update(self, other):
        # won't modify date
        if other.k_price is not None:
            self.k_price = other.k_price
        if other.ma13_price is not None:
            self.ma13_price = other.ma13_price
        if other.ma55_price is not None:
            self.ma55_price = other.ma55_price
        if other.crypto_balance is not None:
            self.crypto_balance = other.crypto_balance
        if other.usdt_balance is not None:
            self.usdt_balance = other.usdt_balance


class RecordExistsError(Exception):
    pass


class NoSuchRecordError(Exception):
    pass


class Database:
    def __init__(self, crypto_name):
        self._crypto_name = crypto_name
        self._records = []

    def crypto_name(self):
        return self._crypto_name

    def add_record(self, record):
        if self._find_by_date(record.date) is not None:
            raise RecordExistsError
        self._records.append(record)
        self._sort_by_date()

    def set_record(self, record):
        r = self._find_by_date(record.date)
        if r is None:
            raise NoSuchRecordError
        r.update(record)

    def dump(self):
        display.display([r.dict() for r in self._records])

    def records(self):
        return self._records

    def _find_by_date(self, date):
        for r in self._records:
            if r.date == date:
                return r
        else:
            return None

    def _sort_by_date(self):
        self._records.sort(key=lambda r: r.date)


def get_file_name(crypto_name):
    return crypto_name + ".dma.csv"


def load(crypto_name) -> Database:
    """
    读取指定加密货币的dma.csv文件。
    :param crypto_name:
    :return:
    """
    db = Database(crypto_name=crypto_name)
    file_name = get_file_name(crypto_name=crypto_name)
    try:
        with open(file_name, newline='\r\n') as f:
            csv_reader = csv.reader(f)
            for line in csv_reader:
                if len(line) == 0:
                    continue
                db.add_record(line_to_record(line))
    except FileNotFoundError:
        print("No such file {}, data is empty.".format(file_name))
    return db


def line_to_record(fields) -> Record:
    """
    将文件里的一行转换成Record
    :param fields:
    :return:
    """
    if len(fields) != 6:
        raise Exception("invalid fields {}, length should be 6".format(fields))
    r = Record(
        date=parse_date(fields[0]),
        k_price=parse_price(fields[1]),
        ma13_price=parse_price(fields[2]),
        ma55_price=parse_price(fields[3]),
        crypto_balance=parse_balance(fields[4]),
        usdt_balance=parse_balance(fields[5]),
    )
    return r


def parse_price(field: str):
    if field is None or len(field) == 0:
        return None
    else:
        return float(field)


def put_price(value: float):
    if value is None:
        return ''
    else:
        return str(value)


def parse_balance(field: str):
    if field is None or len(field) == 0:
        return None
    else:
        return float(field)


def put_balance(value: float):
    if value is None:
        return ''
    else:
        return str(value)


def parse_date(d: str):
    return d


def put_date(value: str):
    return str(value)


def record_to_line(r: Record):
    return [
        put_date(r.date),
        put_price(r.k_price),
        put_price(r.ma13_price),
        put_price(r.ma55_price),
        put_balance(r.crypto_balance),
        put_balance(r.usdt_balance),
    ]


def save(db: Database):
    file_name = get_file_name(crypto_name=db.crypto_name())
    tmp_file_name = file_name + ".tmp"
    bak_file_name = file_name + ".bak"
    with open(tmp_file_name, "w") as f:
        csv_writer = csv.writer(f)
        for r in db.records():
            csv_writer.writerow(record_to_line(r))
    if os.path.exists(file_name):
        shutil.move(file_name, bak_file_name)
    if os.path.exists(tmp_file_name):
        shutil.move(tmp_file_name, file_name)

#
# def display(db: Database):
#     field2len = {}
#     for r in db.records():
#         for k, v in r.dict().items():
#             if field2len.get(k) is None:
#                 field2len[k] = len(k)
#             field2len[k] = max(field2len[k], len(str(v)))
#     # display column name
#     print("+-" + "-+-".join(['-' * v for k, v in field2len.items()]) + "-+")
#     print("| " + " | ".join([k.ljust(v) for k, v in field2len.items()]) + " |")
#     print("+-" + "-+-".join(['-' * v for k, v in field2len.items()]) + "-+")
#     # display record fields
#     for r in db.records():
#         print("| " + " | ".join([beautiful_column(r.dict()[k], v) for k, v in field2len.items()]) + " |")
#     # display end line
#     print("+-" + "-+-".join(['-' * v for k, v in field2len.items()]) + "-+")
#
#
# def str_field(value):
#     if value is None:
#         return "(null)"
#     else:
#         return str(value)
#
#
# def beautiful_column(value, width):
#     if type(value) is str:
#         return str_field(value).ljust(width)
#     elif value is None:
#         return str_field(value).ljust(width)
#     else:
#         return str_field(value).rjust(width)
