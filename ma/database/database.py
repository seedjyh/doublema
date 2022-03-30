# -*- coding: utf-8 -*-
"""
database 是一个模拟的数据库。每一行都是一个dict，key是列名，value是列值。key和value都是str类型。

database 预先规定了一个key作为主键。不允许有重复主键出现；新增记录时，主键原先必须不存在；修改记录时，主键必须已经存在。

本模块不包含文件读写。

"""


class DuplicatePrimaryKey(Exception):
    """
    重复主键
    """
    pass


class NoSuchPrimaryKey(Exception):
    """
    目标主键没找到
    """
    pass


class NoPrimaryKeyInValues(Exception):
    """
    参数里没有目标主键
    """
    pass


class Database:
    def __init__(self, name: str, primary_key: str, fields: []):
        """
        新增一个database对象。其中name是
        :param name: database的名称，会在读写文件系统时用到。
        :param primary_key: 主键列名。
        :param fields: 所有列名（必须包含主键）
        """
        self._name = name
        self._primary_key = primary_key
        self._fields = fields
        self._data = {}  # key是主键，value是一个dict，其中主键也包含在内。

    def name(self):
        return self._name

    def primary_key(self):
        return self._primary_key

    def fields(self):
        return self._fields

    def values(self) -> []:
        """
        返回 list of dict 按照主键排序
        :return:
        """
        res = [d for d in self._data.values()]
        res.sort(key=lambda r: r[self._primary_key])
        return res

    def insert(self, value: dict):
        primary_key_value = value.get(self._primary_key)
        if primary_key_value is None:
            raise NoPrimaryKeyInValues
        if self._data.get(primary_key_value) is not None:
            raise DuplicatePrimaryKey
        r = {}
        for k in self._fields:
            r[k] = ""
        for k, v in value.items():
            if k in self._fields:
                r[k] = v
        self._data[primary_key_value] = r

    def update(self, values: dict):
        primary_key_value = values.get(self._primary_key)
        if primary_key_value is None:
            raise NoPrimaryKeyInValues
        if self._data.get(primary_key_value) is None:
            raise NoSuchPrimaryKey
        for k, v in values.items():
            if k in self._fields:
                self._data[primary_key_value][k] = v
