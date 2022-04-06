# -*- coding: utf-8 -*-
"""
程序入口。
处理命令行参数，构建各模块的对象，组装后传入 command.py 的函数中。
"""
import datetime
import getopt
import sys

from ma import command
from ma import model
from ma.displayer import Displayer
from ma.evaluator import Evaluator
from ma.position import Position
from ma.sqlite import candle
from ma.sqlite.position import PositionRepository


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
    options.operation = argv[0]
    options.crypto_name = argv[1]
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
            options.datetime = datetime.datetime.strptime(v, "%Y-%m-%d")  # 暂时精确到天
        elif k in ("-p", "--price"):
            options.price = float(v)
        elif k in ("-c", "--crypto"):
            options.crypto_balance = float(v)
        elif k in ("-u", "--usdt"):
            options.usdt_balance = float(v)
        else:
            raise Exception("unknown:" + k)
    return options


if __name__ == "__main__":
    opt = get_options(sys.argv[1:])
    db_name = "ma.sqlite.db"
    evaluator = Evaluator()
    displayer = Displayer()
    position_repository = PositionRepository(db_name=db_name)
    try:
        if opt.operation == "add":
            command.add_price(
                candle_chart=candle.CandleChart(db_name=db_name, ccy=opt.crypto_name), timestamp=opt.datetime,
                price=opt.price)
        elif opt.operation == "show":
            command.show_k_line(
                candle_chart=candle.CandleChart(db_name=db_name, ccy=opt.crypto_name), displayer=displayer)
        elif opt.operation == "score":
            command.list_scores(
                candle_chart=candle.CandleChart(db_name=db_name, ccy=opt.crypto_name), evaluator=evaluator,
                displayer=displayer)
        elif opt.operation == "playback":
            command.playback(
                candle_chart=candle.CandleChart(db_name=db_name, ccy=opt.crypto_name), evaluator=evaluator,
                displayer=displayer)
        elif opt.operation == "advice":
            command.find_advice(
                candle_chart=candle.CandleChart(db_name=db_name, ccy=opt.crypto_name), evaluator=evaluator,
                position=position_repository.query(name=opt.crypto_name), displayer=displayer)
        elif opt.operation == "position":
            command.set_position(
                position_repository=position_repository,
                position=Position(
                    name=opt.crypto_name,
                    crypto=opt.crypto_balance,
                    usdt=opt.usdt_balance,
                ),
            )
        else:
            raise Exception("unknown operation:" + opt.operation)
    except Exception as e:
        print("ERR:", e)
        raise
