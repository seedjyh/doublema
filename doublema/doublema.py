# -*- coding: utf-8 -*-
import getopt
import sys

import database


class Options:
    def __init__(self):
        self.operation = None
        self.crypto_name = None
        self.date = None
        self.k_price = None
        self.ma13_price = None
        self.ma55_price = None
        self.crypto_balance = None
        self.usdt_balance = None


def get_options(argv) -> Options:
    # todo: 检查参数数量
    # todo: 检查参数值合法性
    options = Options()
    options.operation = argv[0]
    options.crypto_name = argv[1]
    opt_define = [
        ("d:", "date="),
        ("k:", "k-price="),
        ("", "ma13-price="),
        ("", "ma55-price="),
        ("c:", "crypto-balance="),
        ("u:", "usdt-balance="),
    ]
    short_opts = "".join([s for s, l in opt_define])
    long_opts = [l for s, l in opt_define]
    opts, args = getopt.getopt(argv[2:], short_opts, long_opts)
    for k, v in opts:
        if k in ("-d", "--date"):
            options.date = v
        elif k in ("-k", "--k-price"):
            options.k_price = v
        elif k in ("--ma13-price",):
            options.ma13_price = v
        elif k in ("--ma55-price",):
            options.ma55_price = v
        elif k in ("-c", "--crypto-balance"):
            options.crypto_balance = v
        elif k in ("-u", "--usdt-balance"):
            options.usdt_balance = v
        else:
            raise Exception("unknown k:" + k)
    return options


def opt_to_record(opt) -> database.Record:
    r = database.Record(
        date=opt.date,
        k_price=opt.k_price,
        ma13_price=opt.ma13_price,
        ma55_price=opt.ma55_price,
        crypto_balance=opt.crypto_balance,
        usdt_balance=opt.usdt_balance,
    )
    return r


if __name__ == "__main__":
    opt = get_options(sys.argv[1:])
    db = database.load(crypto_name=opt.crypto_name)
    try:
        if opt.operation == "add":
            db.add_record(opt_to_record(opt))
        elif opt.operation == "set":
            db.set_record(opt_to_record(opt))
        elif opt.operation == "show":
            db.dump()
        else:
            raise Exception("unknown operation:" + opt.operation)
    except database.RecordExistsError as e:
        print("ERR: RecordExistsError", e)
    except Exception as e:
        print("ERR:", e)
    finally:
        database.save(db)
