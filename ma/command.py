# -*- coding: utf-8 -*-
"""
命令的入口。
"""
import abc
import datetime
import math

from ma.candle import CandleChart, Candle
from ma.model import Position



class Evaluator:
    @abc.abstractmethod
    def get_scores(self, candle_chart: CandleChart, since=None, until=None) -> []:
        """
        根据K线图计算建议仓位。
        :param candle_chart: K线图。
        :param since: 开始timestamp。
        :param until: 结束timestamp。
        :return: 一个 TradeViewRecord 的列表。
        """
        pass

    @abc.abstractmethod
    def get_advice(self, candle_chart: CandleChart, timestamp: datetime.datetime, position: Position) -> []:
        """
        根据K线士计算交易建议。
        :param candle_chart: K线图。
        :param timestamp: 要获取建议的当前时间戳。
        :param position: 当前仓位。
        :return: 一个 Trade 列表，表示建议的交易参数。如果是空列表，表示建议持仓不动。
        """
        pass


class Displayer:
    @abc.abstractmethod
    def display(self, fields: [], lines: []):
        """
        模仿mysql命令行，将内容显示在控制台。
        :param fields: 列的列表
        :param lines: 每一项是一个dict，key是fields的元素，否则该key不会被显示。
        :return: 无
        """
        pass


class InvalidParameter(Exception):
    def __init__(self, name: str, value):
        super(InvalidParameter, self).__init__("Invalid Parameter, name={}, value={}".format(name, value))
        self.name = name
        self.value = value


def add_price(candle_chart: CandleChart, timestamp: datetime.datetime, price: float):
    if timestamp is None:
        raise InvalidParameter("timestamp", timestamp)
    if price is None:
        raise InvalidParameter("price", price)
    candle_chart.insert_one(c=Candle(timestamp=timestamp, opening=0, highest=0, lowest=0, closing=price))


def show_k_line(candle_chart: CandleChart, displayer: Displayer):
    fields = ["timestamp", "price"]  # 最终显示的列名列表，从左到右排序
    lines = []  # 最终显示的列内容
    for r in candle_chart.query():
        lines.append({"timestamp": r.timestamp, "price": r.closing})
    displayer.display(fields, lines)


def list_scores(candle_chart: CandleChart, evaluator: Evaluator, displayer: Displayer):
    fields = None  # 最终显示的列名列表，从左到右排序
    lines = []  # 最终显示的列内容
    ma2fields = {}  # 均线参数对应的列名
    for r in evaluator.get_scores(candle_chart=candle_chart):
        ma_p_list = [x for x in r.ma.keys()]
        ma_p_list.sort()
        if fields is None:
            fields = ["timestamp", ]
            for x in ma_p_list:
                field_name = "ma{}".format(x)
                ma2fields[x] = field_name
                fields.append(field_name)
            fields.append("score")
        new_line = {
            "timestamp": r.timestamp,
            "score": r.score,
        }
        for k, v in r.ma.items():
            new_line[ma2fields[k]] = v
        lines.append(new_line)
    displayer.display(fields, lines)


def playback(candle_chart: CandleChart, evaluator: Evaluator, displayer: Displayer):
    """

    :param candle_chart: K线图
    :param evaluator: 评估器
    :param displayer: 结果展示
    :return:
    """
    trade_view_records = evaluator.get_scores(candle_chart=candle_chart)
    position = Position(name="theCRYPTO", crypto=0.0, usdt=1000.0)
    trades = []
    fields = ["timestamp", "price", "score", "crypto", "usdt", "total"]
    lines = []
    for i in range(len(trade_view_records)):
        now_price = trade_view_records[i].ma[1]
        for trade in trades:
            if trade.ok(now_price):
                position = trade.do(position, now_price)

        trades.clear()
        for trade in evaluator.get_advice(candle_chart=candle_chart, timestamp=trade_view_records[i].timestamp,
                                          position=position):
            if math.isclose(trade.price, now_price, rel_tol=1e-5):
                position = trade.do(position)
            else:
                trades.append(trade)
        lines.append({
            "timestamp": trade_view_records[i].timestamp,
            "price": now_price,
            "score": trade_view_records[i].score,
            "crypto": position.crypto,
            "usdt": position.usdt,
            "total": position.total(now_price)
        })
    displayer.display(fields, lines)


def find_advice(candle_chart: CandleChart, evaluator: Evaluator, position: Position, displayer: Displayer):
    """

    :param candle_chart: K线图
    :param evaluator: 评估器
    :param position: 当前仓位
    :param displayer: 结论展示
    :return: 无
    """
    advised_trades = evaluator.get_advice(candle_chart=candle_chart, timestamp=datetime.datetime.today(),
                                          position=position)
    lines = []  # 最终显示的列内容
    fields = ["id", "operation", "name", "price", "amount", "usdt"]  # 最终显示的列名列表，从左到右排序
    for trade in advised_trades:
        new_line = {
            "id": len(lines) + 1,
            "operation": trade.operation(),
            "name": trade.name,
            "price": "{:.8f} usdt/{}".format(trade.price, trade.name),
            "amount": "{:+.8f} {}".format(trade.crypto, trade.name),
            "usdt": "{:+.8f} usdt".format(-trade.crypto * trade.price),
        }
        lines.append(new_line)
    displayer.display(fields=fields, lines=lines)
