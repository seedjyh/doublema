# -*- coding: utf-8 -*-
"""
程序入口。
处理命令行参数，构建各模块的对象，组装后传入 command.py 的函数中。
"""
import getopt
import sys

from ma import command
from ma.kline import KLineChart
from ma import command
from ma import database
from ma.displayer import Displayer
from ma.evaluator import Evaluator


class Options:
    def __init__(self):
        self.crypto_name = None
        self.operation = None
        self.datetime = None
        self.price = None
        self.crypto_balance = None
        self.usdt_balance = None


def get_options(argv) -> Options:
    # todo: 检查参数数量
    # todo: 检查参数值合法性
    options = Options()
    options.crypto_name = argv[0]
    options.operation = argv[1]
    opt_define = [
        ("d:", "datetime="),
        ("p:", "price="),
        ("c:", "crypto="),
        ("u:", "usdt="),
    ]
    short_opts = "".join([s for s, l in opt_define])
    long_opts = [l for s, l in opt_define]
    opts, args = getopt.getopt(argv[2:], short_opts, long_opts)
    for k, v in opts:
        if k in ("-d", "--datetime"):
            options.datetime = v
        elif k in ("-p", "--price"):
            options.price = v
        elif k in ("-c", "--crypto"):
            options.crypto_balance = v
        elif k in ("-u", "--usdt"):
            options.usdt_balance = v
        else:
            raise Exception("unknown:" + k)
    return options


if __name__ == "__main__":
    opt = get_options(sys.argv[1:])
    k_line_chart = KLineChart()
    evaluator = Evaluator()
    displayer = Displayer()
    try:
        if opt.operation == "add":
            command.add_price(k_line_chart=k_line_chart, timestamp=opt.datetime, price=opt.price)
        elif opt.operation == "set":
            command.set_price(k_line_chart=k_line_chart, timestamp=opt.datetime, price=opt.price)
        elif opt.operation == "score":
            command.list_scores(k_line_chart=k_line_chart, evaluator=evaluator, displayer=displayer)
        elif opt.operation == "playback":
            command.playback(k_line_chart=k_line_chart, evaluator=evaluator, displayer=displayer)
        elif opt.operation == "advice":
            command.find_advice(k_line_chart=k_line_chart, evaluator=evaluator,
                                position=command.Position(name=opt.crypto_name, crypto=opt.crypto_balance,
                                                          usdt=opt.usdt_balance), displayer=displayer)
        else:
            raise Exception("unknown operation:" + opt.operation)
    except Exception as e:
        print("ERR:", e)
        raise e
