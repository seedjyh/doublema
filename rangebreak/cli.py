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
import logging
import sys
from datetime import datetime

import const
import display
import model
import okex.market
from rangebreak import _position, _playback, _score, _atr

logger = logging.getLogger(__name__)

_db_name = "rangebreak.sqlite_db"
_market = okex.market.Market()
_position.init(db_name=_db_name)
_score.init(market=_market)
_atr.init(market=_market)
_playback.init(market=_market)
_bar = const.BAR_1D
_total_asset = 1500.0
_each_max_lost_rage = 0.01

def show_ccy(ccy: str):
    logger.debug("show ccy, ccy={}".format(ccy))
    bar = _bar
    displayer = display.Displayer()
    fields = ["ccy", "unit", "each", "atr", "score", "operation"]
    lines = []
    td = const.bar_to_timedelta(bar=bar)
    until = datetime.now() - td
    since = until - td

    def calc_line(p: _position.Position):
        last_candle = _get_last_complete_candle(ccy=p.ccy, bar=bar)
        price = last_candle.c()
        __atr = [a for a in _atr.get_atrs(ccy=p.ccy, bar=bar, since=since, until=until)][-1]
        __volatility = __atr.atr / price
        max_lost = _total_asset * _each_max_lost_rage
        __each = max_lost / __atr.atr
        __score = [s for s in _score.get_scores(ccy=p.ccy, bar=bar, since=since, until=until)][-1]
        return __atr, __volatility, __each, __score

    def p2line(p: _position.Position) -> dict:
        atr, volatility, each, score = calc_line(p)
        last_price = _get_latest_candle(ccy=p.ccy, bar=_bar)
        return {
            'ccy': p.ccy,
            "unit": p.unit,
            "atr": display.Value(v=atr.atr, sign=False, unit="usdt"),
            # "volatility": volatility,
            "each": display.Value(v=each, sign=False, unit="crypto/unit"),
            "score": score.score,
            "operation": make_operation(ccy=p.ccy, score=score.score, now_unit=p.unit, each=each, atr=atr.atr,
                                        price=last_price.c())
        }

    if ccy == "all":
        for p in _position.query_all():
            lines.append(p2line(p))
    else:
        p = _position.query_one(ccy=ccy)
        lines.append(p2line(p))
    displayer.display(fields=fields, lines=lines)


def make_operation(ccy: str, score: float, now_unit: float, each: float, atr: float, price: float) -> str:
    """
    显示操作建议
    :param ccy: 当前标的名
    :param score: 当前分数
    :param now_unit: 当前持仓单位
    :param each: 每个持仓单位需要的币数
    :param atr: 平均波动范围
    :param price: 最近价格
    :return: 字符串描述的操作
    """
    stop_for_long = "{:.8f} usdt/{}".format(price - atr * 2, ccy)
    stop_for_short = "{:.8f} usdt/{}".format(price + atr * 2, ccy)
    if 0.9 < score:  # 0.1
        if now_unit < 0:
            return "close all short, open {:+.3f} {} (stop {})".format(each, ccy, stop_for_long)
        else:
            return "open {:+.3f} {} (stop {})".format(each, ccy, stop_for_long)
    elif 0.8 < score < 0.9:  # 0.875
        if now_unit < 0:
            return "close all short, open {:+.3f} {} (stop {})".format(each, ccy, stop_for_long)
        else:
            return "open {:+.3f} {} (stop {})".format(each, ccy, stop_for_long)
    elif 0.7 < score < 0.8:  # 0.75
        if now_unit < 0:
            return "close all short"
        else:
            return "----"
    elif 0.6 < score < 0.7:  # 0.625
        if now_unit < 0:
            return "close all short"
        elif now_unit > 0:
            return "close HALF long {:.3f} {}".format(now_unit / 2 * each, ccy)
        else:
            return "----"
    elif 0.4 < score < 0.6:  # 0.5
        if now_unit < 0:
            return "close all short"
        elif now_unit > 0:
            return "close all long"
        else:
            return "----"
    elif 0.3 < score < 0.4:  # 0.375
        if now_unit < 0:
            return "close HALF short {:.3f} {}".format(now_unit / 2 * each, ccy)
        elif now_unit > 0:
            return "close all long"
        else:
            return "----"
    elif 0.2 < score < 0.3:  # 0.25
        if now_unit <= 0:
            return "----"
        else:
            return "close all long"
    elif 0.1 < score < 0.2:  # 0.125
        if now_unit <= 0:
            return "open {:+.3f} {} (stop {})".format(-each, ccy, stop_for_short)
        else:
            return "close all long, open {:+.3f} {} (stop {})".format(-each, ccy, stop_for_short)
    elif score < 0.1:  # 0.0
        if now_unit <= 0:
            return "open {:+.3f} {} (stop {})".format(-each, ccy, stop_for_short)
        else:
            return "close all long, open {:+.3f} {} (stop {})".format(-each, ccy, stop_for_short)
    else:
        return "invalid score {}".format(score)


def add_ccy(ccy: str):
    _position.add_one(ccy=ccy)


def long_ccy(ccy: str, unit: int):
    _position.update_one(ccy=ccy, delta_unit=unit)


def short_ccy(ccy: str, unit: int):
    _position.update_one(ccy=ccy, delta_unit=-unit)


def playback(ccy: str):
    displayer = display.Displayer()
    fields = ["ts", "open crypto", "open usdt", "open unit", "closing atr", "closing price", "closing total",
              "closing score"]
    lines = [{
        "ts": r.ts,
        "open crypto": r.open_crypto,
        "open usdt": r.open_usdt,
        "open unit": r.open_unit,
        "closing atr": r.closing_atr,
        "closing price": r.closing_price,
        "closing total": r.closing_total,
        "closing score": r.closing_score,
    } for r in _playback.playback(ccy=ccy, bar=_bar)]
    displayer.display(fields=fields, lines=lines)


def _get_last_complete_candle(ccy: str, bar: str) -> model.Candlestick:
    td = const.bar_to_timedelta(bar=bar)
    until = datetime.now() - td
    since = until - td
    return _market.query(ccy=ccy, bar=bar, since=since, until=until)[-1]


def _get_latest_candle(ccy: str, bar: str) -> model.Candlestick:
    td = const.bar_to_timedelta(bar=bar)
    until = datetime.now()
    since = datetime.now() - td * 2
    return _market.query(ccy=ccy, bar=bar, since=since, until=until)[-1]


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
