# -*- coding: utf-8 -*-

"""
保存关注的币的情况。
"""

from peewee import *


class Position(Model):
    ccy = CharField()
    unit = FloatField()

    class Meta:
        database = None


_db = None


def init(db_name):
    global _db
    _db = SqliteDatabase(db_name)
    _db.connect()
    Position._meta.database = _db
    if not Position.table_exists():
        Position.create_table()


def query_one(ccy: str):
    query = Position.select().where(Position.ccy == ccy)
    if not query.exists():
        raise Exception("position {} not exist".format(ccy))
    return query.get()


# query_all 返回 Position 的列表。
def query_all():
    return [p for p in Position.select().order_by(Position.ccy)]


def add_one(ccy: str):
    if Position.select().where(Position.ccy == ccy).exists():
        raise Exception("position {} exists".format(ccy))
    incr = Position(ccy=ccy, unit=0.0).save()
    if incr != 1:
        raise Exception("add {} row(s)".format(incr))


def update_one(ccy: str, delta_unit):
    query = Position.select().where(Position.ccy == ccy)
    if not query.exists():
        raise Exception("position {} not exist".format(ccy))
    current = query.get()
    current.unit += delta_unit
    current.save()
