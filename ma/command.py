# -*- coding: utf-8 -*-
"""
命令的入口。
"""
import abc
import datetime

from ma import display


class KLineRecord:
    def __init__(self, timestamp: datetime.datetime, ma: dict):
        self.timestamp = timestamp
        self.ma = ma


class KLineChart:
    @abc.abstractmethod
    def add_closing(self, timestamp: datetime.datetime, closing: float):
        pass

    @abc.abstractmethod
    def set_closing(self, timestamp: datetime.datetime, closing: float):
        pass

    @abc.abstractmethod
    def get_records(self, ma_parameters: [], since=None, until=None) -> []:
        pass


class Evaluator:
    @abc.abstractmethod
    def get_score(self, ma_dict: {}) -> float:
        """
        根据均线计算建议仓位。
        :param ma_dict: 是一个dict，key是int，表示均线参数；value是float，表示均线值。key=1表示收盘价(closing)
        :return: 一个分数值，从 0.0 ~ 1.0 表示建议仓位。其中 0.0 表示建议空仓， 1.0 表示建议满仓。
        """
        pass


class Displayer:
    @abc.abstractmethod
    def display(self, fields: [], lines: []):
        pass


class Position:
    """
    仓位状态。
    """

    def __init__(self, name: str, crypto: float, usdt: float):
        self.name = name
        self.crypto = crypto
        self.usdt = usdt


class Trade:
    def __init__(self, name: str, price: float, crypto: float):
        self.name = name
        self.price = price
        self.crypto = crypto


def add_closing(k_line_chart: KLineChart, timestamp: datetime.datetime, closing: float):
    k_line_chart.add_closing(timestamp, closing)


def set_closing(k_line_chart: KLineChart, timestamp: datetime.datetime, closing: float):
    k_line_chart.set_closing(timestamp, closing)


def list_scores(k_line_chat: KLineChart, evaluator: Evaluator, displayer: Displayer):
    lines = []
    ma_parameters = [1, 7, 13, 55]
    for r in k_line_chat.get_records(ma_parameters):
        new_line = {"timestamp": r.timestamp, "score": evaluator.get_score(r.ma)}
        for k, v in r.ma.items():
            if k == 1:
                new_line["closing"] = v
            else:
                new_line["ma{}" % k] = v
        lines.append(new_line)
    displayer.display(lines)


def playback(k_line_chat: KLineChart, evaluator: Evaluator, displayer: Displayer):
    """

    :param k_line_chat: K线图
    :param evaluator: 评估器
    :param displayer: 结果展示
    :return:
    """
    pass


def find_advice(k_line_chat: KLineChart, evaluator: Evaluator, position: Position, displayer: Displayer):
    """

    :param k_line_chat: K线图
    :param evaluator: 评估器
    :param position: 当前仓位
    :param displayer: 结论展示
    :return: 无
    """
    pass
