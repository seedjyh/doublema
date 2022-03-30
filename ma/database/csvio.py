# -*- coding: utf-8 -*-
"""
csvio 用于 Database 的文件读写。

用save(db: Database) 将一个数据库持久化到文件系统；
用load(): Database 从文件系统加载一个数据库。

"""
import csv
import os
import shutil

from ma.database import database


def save(db: database.Database):
    """
    1. 写入临时文件"<PATH>.tmp"
    2. 重命名"<PATH>"为备份文件"<PATH>.bak"
    3. 重命名"<PATH>.tmp"到最终文件"<PATH>"
    :param db: 要写入的数据库。
    :return:
    """
    _assure_directory(_db_root_path())
    path = _get_file_path(db.name())
    tmp_file_path = path + ".tmp"
    bak_file_path = path + ".bak"
    plain_save(tmp_file_path, db.primary_key(), db.fields(), db.values())
    if os.path.exists(path):
        shutil.move(path, bak_file_path)
    if os.path.exists(tmp_file_path):
        shutil.move(tmp_file_path, path)


def plain_save(path: str, primary_key: str, fields: [], values: []):
    """
    将数据写入csv文件系统。主键放在最左边一列。
    :param path: 文件路径
    :param primary_key: 主键
    :param fields: 列名列表 list of str
    :param values: list of dict
    :return:
    """
    write_fields = [primary_key, ]
    for k in fields:
        if k != primary_key:
            write_fields.append(k)
    with open(path, "w") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(write_fields)
        for d in values:
            csv_writer.writerow([d.get(k) for k in write_fields])


def load(name: str) -> database.Database:
    """
    从csv文件系统读取。第一行是列名，之后每行是一条记录。
    注意处理  FileNotFoundError 异常
    :return: database.Database
    """
    db = None
    fields = None
    path = _get_file_path(name)
    with open(path, newline="\r\n") as f:
        csv_reader = csv.reader(f)
        for line in csv_reader:
            if len(line) == 0:
                raise -1  # todo: 莫名其妙的空行
            if db is None:  # 第一行是列名
                fields = line
                db = database.Database(name=name, primary_key=fields[0], fields=fields)
            else:
                db.insert(dict(zip(fields, line)))
    return db


def _db_root_path() -> str:
    return os.path.join(os.path.abspath("."), ".db")


def _assure_directory(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def _get_file_name(name: str):
    return name + ".dma.csv"


def _get_file_path(name: str):
    return os.path.join(_db_root_path(), _get_file_name(name))

#
# def load(name: str) -> Database:
#     """
#     从csv文件读取数据库。其中第一列作为主键。
#     :param name:
#     :return:
#     """
#     db = None
#     for line in csvio.load(_get_file_path(name)):
#         if db is None:
#             fields = [k for k in line.keys()]
#             db = Database(name=name, primary_key=fields[0])
#         db.insert(line)
#     return db
