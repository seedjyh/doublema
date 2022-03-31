# -*- coding: utf-8 -*-
"""
命令的入口。
"""
import abc
import datetime


class KLineRecord:
    def __init__(self, timestamp: datetime.datetime, price: float):
        """
        一条K线记录。
        :param timestamp: 时间戳，具体精确视情况而定。
        :param price: 该时间戳的收盘价。
        """
        self.timestamp = timestamp
        self.price = price


class KLineChart:
    @abc.abstractmethod
    def add_price(self, timestamp: datetime.datetime, price: float):
        """
        新增某timestamp收盘价。该timestamp必须不存在。
        :param timestamp: 时间戳
        :param price: 收盘价
        :return: 无
        """
        pass

    @abc.abstractmethod
    def set_price(self, timestamp: datetime.datetime, price: float):
        """
        修改某timestamp的收盘价。该timestamp必须存在。
        :param timestamp: 时间戳
        :param price: 收盘价
        :return: 无
        """
        pass

    @abc.abstractmethod
    def get_records(self, since: datetime, until: datetime) -> []:
        """
        获取某timestamp范围内的K线图。
        :param since: 开始timestamp。
        :param until: 结束timestamp。
        :return: 一个 KLineRecord 的列表，按照 timestamp 排序。
        """
        pass

    @abc.abstractmethod
    def save(self):
        """
        持久化。
        :return:
        """
        pass


class Position:
    """
    仓位状态。
    """

    def __init__(self, name: str, crypto: float, usdt: float):
        """
        :param name: 仓位名称，通常是加密货币名，如 ”btc“
        :param crypto: 加密货币的余额。
        :param usdt: 用于该加密火币交易的usdt余额。
        """
        self.name = name
        self.crypto = crypto
        self.usdt = usdt


class Trade:
    def __init__(self, name: str, price: float, crypto: float):
        """
        交易参数
        :param name: 仓位名称，通常是加密货币名，如 ”btc“
        :param price: 交易时加密货币相对于 usdt 的价格。
        :param crypto: 被交易的加密货币的数量。
        """
        self.name = name
        self.price = price
        self.crypto = crypto


class TradeViewRecord:
    def __init__(self, timestamp: datetime.datetime, ma: {}, score: float):
        """

        :param timestamp: 时间戳。
        :param ma: 均线数据 dict。其中key是均线范围，比如1表示timestamp所在K柱的收盘价，3表示三日均线。
        :param score: 从 0.0 ~ 1.0 表示建议仓位。其中 0.0 表示建议空仓， 1.0 表示建议满仓。
        """
        self.timestamp = timestamp
        self.ma = ma
        self.score = score


class Evaluator:
    @abc.abstractmethod
    def get_scores(self, k_line_chart: KLineChart, since=None, until=None) -> []:
        """
        根据K线图计算建议仓位。
        :param k_line_chart: K线图。
        :param since: 开始timestamp。
        :param until: 结束timestamp。
        :return: 一个TradeViewRecord的列表。
        """
        pass

    @abc.abstractmethod
    def get_advice(self, k_line_chart: KLineChart, timestamp: datetime.datetime, position: Position) -> []:
        """
        根据K线士计算交易建议。
        :param k_line_chart: K线图。
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


def add_price(k_line_chart: KLineChart, timestamp: datetime.datetime, price: float):
    if timestamp is None:
        raise InvalidParameter("timestamp", timestamp)
    if price is None:
        raise InvalidParameter("price", price)
    k_line_chart.add_price(timestamp, price)
    k_line_chart.save()


def set_price(k_line_chart: KLineChart, timestamp: datetime.datetime, price: float):
    if timestamp is None:
        raise InvalidParameter("timestamp", timestamp)
    if price is None:
        raise InvalidParameter("price", price)
    k_line_chart.set_price(timestamp, price)
    k_line_chart.save()


def show_k_line(k_line_chart: KLineChart, displayer: Displayer):
    fields = ["timestamp", "price"]  # 最终显示的列名列表，从左到右排序
    lines = []  # 最终显示的列内容
    for r in k_line_chart.get_records():
        lines.append({"timestamp": r.timestamp, "price": r.price})
    displayer.display(fields, lines)


def list_scores(k_line_chart: KLineChart, evaluator: Evaluator, displayer: Displayer):
    fields = None  # 最终显示的列名列表，从左到右排序
    lines = []  # 最终显示的列内容
    ma2fields = {}  # 均线参数对应的列名
    for r in evaluator.get_scores(k_line_chart=k_line_chart):
        ma_p_list = [x for x in r.ma.keys()]
        ma_p_list.sort()
        if fields is None:
            fields = ["timestamp", ]
            for x in ma_p_list:
                if x == 1:
                    field_name = "closing"
                else:
                    field_name = "ma{}" % x
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
    displayer.display(lines)


def playback(k_line_chart: KLineChart, evaluator: Evaluator, displayer: Displayer):
    """

    :param k_line_chart: K线图
    :param evaluator: 评估器
    :param displayer: 结果展示
    :return:
    """
    trade_view_records = evaluator.get_scores(k_line_chart=k_line_chart)
    raise "TODO"


def find_advice(k_line_chart: KLineChart, evaluator: Evaluator, position: Position, displayer: Displayer):
    """

    :param k_line_chart: K线图
    :param evaluator: 评估器
    :param position: 当前仓位
    :param displayer: 结论展示
    :return: 无
    """
    advised_trades = evaluator.get_advice(k_line_chart=k_line_chart, timestamp=datetime.datetime.today(),
                                          position=position)
    lines = []  # 最终显示的列内容
    fields = ["id", "operation", "name", "price", "amount"]  # 最终显示的列名列表，从左到右排序
    for trade in advised_trades:
        new_line = {
            "id": len(lines) + 1,
            "operation": trade.operation(),
            "name": trade.name,
            "price": "{} usdt/{}".format(trade.price, trade.name),
            "crypto": "{} {}".format(trade.crypto, trade.name)
        }
        lines.append(new_line)
    displayer.display(fields=fields, lines=lines)
