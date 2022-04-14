# -*- coding: utf-8 -*-
import base64
import hashlib
import hmac
from datetime import datetime, timedelta
from urllib.parse import urljoin

import requests

from okex import _secret, _proxy, _host
import model


def query(ccy: str, bar: str, since: datetime, until: datetime):
    """
    查询指定 ccy ，指定 bar ，开始时间位于 [since, until) （半闭半开区间）的K线数据。
    注意，since和until只限制了K柱开始时刻。K柱结束时刻不限。
    :param ccy: 货币名称。
    :param bar: k柱宽度
    :param since: K柱开始时刻 >= since
    :param until: K柱开始时刻 < until
    :return:
    """
    host = _host.url
    since += timedelta(milliseconds=-1)
    request_path = "/api/v5/market/candles"
    url = urljoin(host, request_path)
    req_timestamp = get_timestamp()
    signature = make_signature(
        raw=req_timestamp + "GET" + request_path,
        secret_key=_secret.secret_key,
    )
    ok_headers = {
        "OK-ACCESS-KEY": _secret.api_key,
        "OK-ACCESS-SIGN": signature,
        "OK-ACCESS-TIMESTAMP": req_timestamp,
        "OK-ACCESS-PASSPHRASE": _secret.passphrase,
    }
    std_headers = {
        "Content-Type": "application/json"
    }
    headers = {
        **ok_headers,
        **std_headers,
    }
    params = {
        "instId": get_inst_id(ccy=ccy),
        "bar": bar,
        "before": make_unix_millisecond(since),
        "after": make_unix_millisecond(until),
    }
    proxies = {
        "http": _proxy.url,
        "https": _proxy.url,
    }
    rsp = requests.get(url=url, headers=headers, params=params, proxies=proxies)
    if rsp.status_code != 200:
        raise Exception("http status code {}".format(rsp.status_code))
    body = rsp.json()
    if body.get("code") != "0":
        raise Exception("response code {}".format(body))
    candles = []
    for (ts, o, h, l, c, vol, vol_ccy) in body.get("data"):
        candles.append(model.Candlestick(
            t=datetime.fromtimestamp(int(ts) / 1000),
            o=float(o),
            h=float(h),
            l=float(l),
            c=float(c),
        ))
    candles.sort(key=lambda candle: candle.timestamp())
    return candles


def get_inst_id(ccy: str):
    return "{}-USDT".format(ccy).upper()


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


def get_timestamp() -> str:
    """
    获取当前的时间戳，YYYY-MM-DDThh:mm:ss.pppZ
    :return:
    """
    return str(datetime.utcnow().isoformat()[:-3]) + "Z"


def make_unix_millisecond(timestamp: datetime) -> str:
    """
    将 timestamp 转换成 unix 的毫秒数。str类型。
    :param timestamp:
    :return:
    """
    return str(round(timestamp.timestamp() * 1000.0))
