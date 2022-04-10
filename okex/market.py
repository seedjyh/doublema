# -*- coding: utf-8 -*-

"""
market 实现了 smarter.market.Market 接口访问Okex交易所并下载行情数据的功能。
"""

import base64
import hashlib
import hmac
from datetime import datetime, timedelta
from urllib.parse import urljoin

import requests as requests

from smarter import market
from okex import proxy, secret

_host = "https://www.okx.com/"


class Market(market.Market):
    def __init__(self):
        pass

    def query(self, ccy: str = None, since: datetime = None, until: datetime = None, bar: str = None):
        # 故意偏移1毫秒，以确保这个时间也被包含在内
        ccy = (ccy or market.CCY_BTC)
        since = (since or datetime(year=2022, month=1, day=1)) + timedelta(milliseconds=-1)
        until = (until or datetime.utcnow()) + + timedelta(milliseconds=1)
        bar = (bar or market.BAR_1D)
        host = _host
        request_path = "/api/v5/market/candles"
        url = urljoin(host, request_path)
        req_timestamp = self.get_timestamp()
        signature = self.make_signature(
            raw=req_timestamp + "GET" + request_path,
            secret_key=secret.secret_key,
        )
        ok_headers = {
            "OK-ACCESS-KEY": secret.api_key,
            "OK-ACCESS-SIGN": signature,
            "OK-ACCESS-TIMESTAMP": req_timestamp,
            "OK-ACCESS-PASSPHRASE": secret.passphrase,
        }
        std_headers = {
            "Content-Type": "application/json"
        }
        headers = {
            **ok_headers,
            **std_headers,
        }
        params = {
            "instId": self.get_inst_id(ccy=ccy),
            "bar": bar,
            "before": self.make_unix_millisecond(since),
            "after": self.make_unix_millisecond(until),
        }
        proxies = {
            "http": proxy.url,
            "https": proxy.url,
        }
        rsp = requests.get(url=url, headers=headers, params=params, proxies=proxies)
        if rsp.status_code != 200:
            raise Exception("http status code {}".format(rsp.status_code))
        body = rsp.json()
        if body.get("code") != "0":
            raise Exception("response code {}".format(body.code))
        candles = []
        for (ts, o, h, l, c, vol, vol_ccy) in body.get("data"):
            candles.append(market.Candlestick(
                t=datetime.fromtimestamp(int(ts) / 1000),
                o=float(o),
                h=float(h),
                l=float(l),
                c=float(c),
            ))
        candles.sort(key=lambda candle: candle.timestamp())
        return candles

    @staticmethod
    def get_inst_id(ccy: str):
        return "{}-USDT".format(ccy).upper()

    @staticmethod
    def make_signature(raw: str, secret_key: str) -> str:
        """
        Use b64encode, but NOT encodebytes, to avoid "\n"
        :param raw:
        :param secret_key:
        :return:
        """
        return str(base64.b64encode(
            hmac.new(bytes(secret_key, "utf-8"), msg=bytes(raw, 'utf-8'), digestmod=hashlib.sha256).digest()),
            encoding="utf8")

    @staticmethod
    def get_timestamp() -> str:
        """
        获取当前的时间戳，YYYY-MM-DDThh:mm:ss.pppZ
        :return:
        """
        return str(datetime.utcnow().isoformat()[:-3]) + "Z"

    @staticmethod
    def make_unix_millisecond(timestamp: datetime) -> str:
        """
        将 timestamp 转换成 unix 的毫秒数。str类型。
        :param timestamp:
        :return:
        """
        return str(round(timestamp.timestamp() * 1000.0))
