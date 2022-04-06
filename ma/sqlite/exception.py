# -*- coding: utf-8 -*-

class NoSuchRecord(Exception):
    def __init__(self, sql):
        self.sql = sql
