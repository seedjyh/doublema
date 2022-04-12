# -*- coding: utf-8 -*-
import getopt
import sys
from datetime import datetime

import display
import model
import okex.market
import triplema._position
from triplema import _position, _index, _score, _playback

_db = "triplema.sqlite_db"
_market_db = "triplema_okex.sqlite_db"
_bar = model.BAR_1D
_ma_list = [1, 5, 13, 34]


def set_position(ccy: str, crypto: float, usdt: float):
    try:
        triplema._position.PositionRepository(db=_db).set(p=model.Position(ccy=ccy, crypto=crypto, usdt=usdt))
    except Exception as e:
        print("ERR: exception {}".format(e))
        raise e


def buy_position(ccy: str, price: float, crypto: float):
    try:
        repo = triplema._position.PositionRepository(db=_db)
        raw_position = repo.query(ccy=ccy)
        cost = crypto * price
        if cost > raw_position.usdt:
            raise Exception("no enough usdt")
        new_position = model.Position(
            ccy=raw_position.ccy,
            crypto=raw_position.crypto + crypto,
            usdt=raw_position.usdt - cost,
        )
        repo.set(p=new_position)
        print("OK.")
    except model.NoSuchRecord:
        print("ERR: No position record for ccy {}".format(ccy))
    except Exception as e:
        print("ERR: exception {}".format(e))


def sell_position(ccy: str, price: float, crypto: float):
    try:
        repo = triplema._position.PositionRepository(db=_db)
        raw_position = repo.query(ccy=ccy)
        receive = crypto * price
        if crypto > raw_position.crypto:
            raise Exception("no enough {}".format(ccy))
        new_position = model.Position(
            ccy=raw_position.ccy,
            crypto=raw_position.crypto - crypto,
            usdt=raw_position.usdt + receive,
        )
        repo.set(p=new_position)
        print("OK.")
    except model.NoSuchRecord:
        print("ERR: No position record for ccy {}".format(ccy))
    except Exception as e:
        print("ERR: exception {}".format(e))


def show_position(ccy: str):
    try:
        displayer = display.Displayer()
        fields = ["ccy", "crypto", "usdt"]
        lines = []
        repo = triplema._position.PositionRepository(db=_db)
        if ccy == "all":
            for p in repo.query_all():
                lines.append(p.__dict__)
        else:
            p = repo.query(ccy=ccy)
            lines.append(p.__dict__)
        displayer.display(fields=fields, lines=lines)
    except Exception as e:
        print("ERR: exception {}".format(e))


def get_advice(ccy: str):
    try:
        displayer = display.Displayer()
        fields = ["id", "operation", "ccy", "price", "amount", "usdt"]
        lines = []
        evaluator = _score.Evaluator(source=okex.market.Market(db=_market_db), bar=_bar, ma_list=_ma_list)
        now = datetime.now()
        if ccy == "all":
            for p in _position.PositionRepository(db=_db).query_all():
                trade = evaluator.get_advice_one(raw_position=_position.PositionRepository(db=_db).query(ccy=p.ccy),
                                                 t=now)
                lines.append({
                    "id": len(lines) + 1,
                    "operation": trade.operation(),
                    "ccy": trade.ccy,
                    "price": "{:.8f} usdt/{}".format(trade.price, trade.ccy),
                    "amount": "{:+.8f} {}".format(trade.crypto, trade.ccy),
                    "usdt": "{:+.8f} usdt".format(-trade.crypto * trade.price),
                })
        else:
            trade = evaluator.get_advice_one(raw_position=_position.PositionRepository(db=_db).query(ccy=ccy), t=now)
            lines.append({
                "id": len(lines) + 1,
                "operation": trade.operation(),
                "ccy": trade.ccy,
                "price": "{:.8f} usdt/{}".format(trade.price, trade.ccy),
                "amount": "{:+.8f} {}".format(trade.crypto, trade.ccy),
                "usdt": "{:+.8f} usdt".format(-trade.crypto * trade.price),
            })
        displayer.display(fields=fields, lines=lines)
    except Exception as e:
        print("ERR: exception {}".format(e))


def playback(ccy: str):
    displayer = display.Displayer()
    fields = ["ts", "begin crypto", "begin usdt", "closing price", "final total", "final score"]
    lines = []
    market = okex.market.Market(db=_market_db)
    since = datetime(year=2022, month=1, day=1)
    until = datetime.today()
    for record in _playback.playback(ccy=ccy, market=market, bar=_bar, ma_list=_ma_list, since=since, until=until):
        lines.append({
            "ts": record.ts,
            "begin crypto": record.crypto,
            "begin usdt": record.usdt,
            "closing price": record.closing,
            "final total": record.total,
            "final score": record.score,
        })
    displayer.display(fields=fields, lines=lines)


class Options:
    def __init__(self):
        self.operation = None
        self.ccy = None
        self.price = None
        self.crypto = None
        self.usdt = None


def get_options(argv) -> Options:
    # todo: 检查参数数量
    # todo: 检查参数值合法性
    options = Options()
    options.operation = argv[0]
    options.ccy = argv[1]
    opt_define = [
        ("p:", "price="),
        ("c:", "crypto="),
        ("u:", "usdt="),
    ]
    short_opts = "".join([s for s, l in opt_define])
    long_opts = [l for s, l in opt_define]
    opts, args = getopt.getopt(argv[2:], short_opts, long_opts)
    for k, v in opts:
        if k in ("-p", "--price"):
            options.price = float(v)
        elif k in ("-c", "--crypto"):
            options.crypto = float(v)
        elif k in ("-u", "--usdt"):
            options.usdt = float(v)
        else:
            raise Exception("unknown:" + k)
    return options


opt = get_options(sys.argv[1:])
if opt.operation == "set":
    set_position(ccy=opt.ccy, crypto=opt.crypto, usdt=opt.usdt)
elif opt.operation == "buy":
    buy_position(ccy=opt.ccy, price=opt.price, crypto=opt.crypto)
elif opt.operation == "sell":
    sell_position(ccy=opt.ccy, price=opt.price, crypto=opt.crypto)
elif opt.operation == "show":
    show_position(ccy=opt.ccy)
elif opt.operation == "advice":
    get_advice(ccy=opt.ccy)
elif opt.operation == "playback":
    playback(ccy=opt.ccy)
