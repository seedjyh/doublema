# -*- coding: utf-8 -*-
import csv
import shutil


class Price:
    def __init__(self, field: str):
        self._value = float(field)


class Record:
    def __init__(self, date, k_price=None, ma13_price=None, ma55_price=None, crypto_balance=None, usdt_balance=None):
        self.date = self.__parse_date(date)
        self.k_price = self.__parse_price(k_price)
        self.ma13_price = self.__parse_price(ma13_price)
        self.ma55_price = self.__parse_price(ma55_price)
        self.crypto_balance = self.__parse_balance(crypto_balance)
        self.usdt_balance = self.__parse_balance(usdt_balance)

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

    @staticmethod
    def __parse_price(field: str):
        if field is None:
            return None
        else:
            return float(field)

    @staticmethod
    def __parse_balance(field: str):
        if field is None:
            return None
        else:
            return float(field)

    @staticmethod
    def __parse_date(d: str):
        return d


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
        for r in self._records:
            print("record in database:", r.__dict__)

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
        date=fields[0],
        k_price=fields[1],
        ma13_price=fields[2],
        ma55_price=fields[3],
        crypto_balance=fields[4],
        usdt_balance=fields[5],
    )
    return r


def record_to_line(r: Record):
    return [
        str(r.date),
        str(r.k_price),
        str(r.ma13_price),
        str(r.ma55_price),
        str(r.crypto_balance),
        str(r.usdt_balance),
    ]


def save(db: Database):
    file_name = get_file_name(crypto_name=db.crypto_name())
    tmp_file_name = file_name + ".tmp"
    bak_file_name = file_name + ".bak"
    with open(tmp_file_name, "w") as f:
        csv_writer = csv.writer(f)
        for r in db.records():
            csv_writer.writerow(record_to_line(r))
    shutil.move(file_name, bak_file_name)
    shutil.move(tmp_file_name, file_name)
