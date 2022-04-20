# -*- coding: utf-8 -*-

"""
基本操作
show btc 显示单个币的情况。包括单个币的波动率、单位头寸、当前头寸数、评分。
show all 显示所有币的情况。包括所有币的波动率、单位头寸、当前头寸数、评分。
当前头寸用整数表示，+1表示一个做多头寸单位，-1表示一个做空头寸单位。
分数+1.0 表示平空开多或加仓开多，-1.0 表示平多开空或加仓开空。
init btc 表示增加一个关注的币，并将仓位置0。如果已经存在则失败。
long btc 表示btc减少一个空仓头寸单位，或增加一个多仓头寸单位。
short btc 表示btc减少一个多仓头寸单位，或增加一个空仓头寸单位。
playback btc 回放
"""
import getopt
import sys

import const
import display
import okex.market
from rangebreak import _position, _playback, _score, _atr

_db_name = "rangebreak.sqlite_db"
_market = okex.market.Market()
_position.init(db_name=_db_name)
_score.init(market=_market)
_atr.init(market=_market)
_playback.init(market=_market)


def show_ccy(ccy: str):
    displayer = display.Displayer()
    fields = ["ccy", "volatility", "each", "unit", "score"]
    lines = []
    if ccy == "all":
        for p in _position.query_all():
            lines.append({
                'ccy': p.ccy,
                "volatility": 12.3,
                "each": "{} usdt/unit".format(45.6),
                "unit": p.unit,
                "score": 78.9,
            })
    else:
        p = _position.query_one(ccy=ccy)
        lines.append({
            'ccy': p.ccy,
            "volatility": 12.3,
            "each": "{} usdt/unit".format(45.6),
            "unit": p.unit,
            "score": 78.9,
        })
    displayer.display(fields=fields, lines=lines)


def add_ccy(ccy: str):
    _position.add_one(ccy=ccy)


def long_ccy(ccy: str, unit: int):
    _position.update_one(ccy=ccy, delta_unit=unit)


def short_ccy(ccy: str, unit: int):
    _position.update_one(ccy=ccy, delta_unit=-unit)


def playback(ccy: str):
    displayer = display.Displayer()
    fields = ["ts", "open crypto", "open usdt", "open unit", "closing price", "closing total", "closing score"]
    lines = [{
        "ts": r.ts,
        "open crypto": r.open_crypto,
        "open usdt": r.open_usdt,
        "open unit": r.open_unit,
        "closing price": r.closing_price,
        "closing total": r.closing_total,
        "closing score": r.closing_score,
    } for r in _playback.playback(ccy=ccy, bar=const.BAR_1D)]
    displayer.display(fields=fields, lines=lines)


class Options:
    def __init__(self):
        self.operation = None
        self.target = None
        self.unit = None


def get_options(argv) -> Options:
    if len(argv) < 2:
        raise Exception("invalid arguments")
    # todo: 检查参数值合法性
    options = Options()
    options.operation = argv[0]
    options.target = argv[1]
    opt_define = [
        ("u:", "unit="),
    ]
    short_opts = "".join([s for s, l in opt_define])
    long_opts = [l for s, l in opt_define]
    opts, args = getopt.getopt(argv[2:], short_opts, long_opts)
    for k, v in opts:
        if k in ("-u", "--unit"):
            options.unit = float(v)
        else:
            raise Exception("unknown:" + k)
    return options


opt = get_options(sys.argv[1:])
if opt.operation == "show":
    show_ccy(ccy=opt.target)
elif opt.operation == "add":
    add_ccy(ccy=opt.target)
elif opt.operation == "long":
    long_ccy(ccy=opt.target, unit=opt.unit)
elif opt.operation == "short":
    short_ccy(ccy=opt.target, unit=opt.unit)
elif opt.operation == "playback":
    playback(ccy=opt.target)
else:
    raise Exception("unknown operation: {}".format(opt.operation))
