# -*- coding: utf-8 -*-
import abc
import datetime


class Span(metaclass=abc.ABCMeta):
    """
    根据K线图的粒度，在datetime和str之间转换。
    """

    @abc.abstractmethod
    def strip(self, t: datetime.datetime) -> datetime.datetime:
        pass

    @abc.abstractmethod
    def to_string(self, t: datetime.datetime) -> str:
        pass

    @abc.abstractmethod
    def from_string(self, s: str) -> datetime.datetime:
        pass


class DaySpan(Span):
    """
    按照「天」为单位裁剪。
    """

    def __init__(self):
        # self._format = "%Y-%m-%d %H:%M:%S.%f"
        self._format = "%Y-%m-%d"

    def strip(self, t: datetime.datetime) -> datetime.datetime:
        return datetime.datetime(year=t.year, month=t.month, day=t.day)

    def to_string(self, t: datetime.datetime) -> str:
        return t.strftime(self._format)

    def from_string(self, s: str) -> datetime.datetime:
        return datetime.datetime.strptime(s, self._format)


class SecondSpan(Span):
    """
    按照「秒」为单位裁剪。
    """

    def __init__(self):
        # self._format = "%Y-%m-%d %H:%M:%S.%f"
        self._format = "%Y-%m-%d %H:%M:%S"

    def strip(self, t: datetime.datetime) -> datetime.datetime:
        return datetime.datetime(year=t.year, month=t.month, day=t.day, hour=t.hour, minute=t.minute, second=t.second)

    def to_string(self, t: datetime.datetime) -> str:
        return t.strftime(self._format)

    def from_string(self, s: str) -> datetime.datetime:
        return datetime.datetime.strptime(s, self._format)
