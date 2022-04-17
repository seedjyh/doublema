# -*- coding: utf-8 -*-
import getopt
import sqlite3
import sys
from datetime import datetime, timedelta

import display
import model
import okex.market
import okex.trade
import triplema._position
from triplema import _position, _index, _score, _playback, _trade

_db = "triplema.sqlite_db"

_bar = model.BAR_1D
_ma_list = [1, 5, 13, 34]


def set_position(ccy: str, crypto: float, usdt: float):
    db_conn = sqlite3.connect(database=_db)
    try:
        triplema._position.Repository(db_conn=db_conn).set(p=model.Position(ccy=ccy, crypto=crypto, usdt=usdt))
    except Exception as e:
        print("ERR: exception {}".format(e))
        raise e
    finally:
        db_conn.close()


def _buy_position(db_conn, ccy: str, price: float, crypto: float):
    try:
        repo = triplema._position.Repository(db_conn=db_conn)
        raw_position = repo.query(ccy=ccy)
        cost = crypto * price
        if cost > raw_position.usdt:
            cost = raw_position.usdt
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


def _sell_position(db_conn, ccy: str, price: float, crypto: float):
    try:
        repo = triplema._position.Repository(db_conn=db_conn)
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
    db_conn = sqlite3.connect(database=_db)
    try:
        displayer = display.Displayer()
        fields = ["id", "operation", "ccy", "price", "amount", "usdt"]
        lines = []
        evaluator = _score.Evaluator(source=okex.market.Market(), bar=_bar, ma_list=_ma_list)
        now = datetime.now()
        if ccy == "all":
            for p in _position.Repository(db_conn=db_conn).query_all():
                trade = evaluator.get_advice_one(raw_position=_position.Repository(db_conn=db_conn).query(ccy=p.ccy),
                                                 now=now)
                lines.append({
                    "id": len(lines) + 1,
                    "operation": trade.operation(),
                    "ccy": trade.ccy,
                    "price": "{:.8f} usdt/{}".format(trade.price, trade.ccy),
                    "amount": "{:+.8f} {}".format(trade.crypto, trade.ccy),
                    "usdt": "{:+.8f} usdt".format(-trade.crypto * trade.price),
                })
        else:
            trade = evaluator.get_advice_one(raw_position=_position.Repository(db_conn=db_conn).query(ccy=ccy), now=now)
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
        raise e
    finally:
        db_conn.close()


def playback(ccy: str):
    displayer = display.Displayer()
    fields = ["ts", "begin crypto", "begin usdt", "closing price", "final total", "final score", "atr"]
    lines = []
    market = okex.market.Market()
    since = datetime(year=2022, month=1, day=1)
    until = datetime.today()
    for record in _playback.playback(ccy=ccy, market=market, bar=_bar, ma_list=_ma_list, since=since, until=until):
        lines.append({
            "ts": record.ts,
            "begin crypto": "{:.8f} {}".format(record.crypto, ccy),
            "begin usdt": "{:.8f} usdt".format(record.usdt),
            "closing price": "{:.8f} usdt/{}".format(record.closing, ccy),
            "final total": "{:.8f} usdt".format(record.total),
            "final score": "{:.3f}".format(record.score),
            "atr": "{:.8f}".format(record.atr),
        })
    displayer.display(fields=fields, lines=lines)


def sync_trade():
    # last_bill_id = "435230091285774338"
    db_conn = sqlite3.connect(database=_db)
    trade_repo = _trade.Repository(db_conn=db_conn)
    try:
        try:
            last_bill_id = trade_repo.get_last().bill_id
        except model.NoSuchRecord:
            last_bill_id = None
        for t in okex.trade.query(last_bill_id=last_bill_id):
            if t.crypto > 0:
                _buy_position(db_conn=db_conn, ccy=t.ccy, price=t.price, crypto=t.crypto)
            else:
                _buy_position(db_conn=db_conn, ccy=t.ccy, price=t.price, crypto=-t.crypto)
            trade_repo.append(t)
    finally:
        db_conn.close()


# api above...
# opt below...


class Options:
    def __init__(self):
        self.operation = None
        self.target = None
        self.price = None
        self.crypto = None
        self.usdt = None
        self.since = None


def get_options(argv) -> Options:
    # todo: 检查参数数量
    # todo: 检查参数值合法性
    options = Options()
    options.operation = argv[0]
    options.target = argv[1]
    opt_define = [
        ("p:", "price="),
        ("c:", "crypto="),
        ("u:", "usdt="),
        ("s:", "since="),
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
        elif k in ("-s", "--since"):
            options.since = datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        else:
            raise Exception("unknown:" + k)
    return options



opt = get_options(sys.argv[1:])
if opt.operation == "set":
    set_position(ccy=opt.target, crypto=opt.crypto, usdt=opt.usdt)
elif opt.operation == "show":
    show_position(ccy=opt.target)
elif opt.operation == "advice":
    get_advice(ccy=opt.target)
elif opt.operation == "playback":
    playback(ccy=opt.target)
elif opt.operation == "sync":
    if opt.target == "trade":
        sync_trade()
