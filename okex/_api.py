# -*- coding: utf-8 -*-
import base64
import hashlib
import hmac
import logging

from datetime import datetime, timedelta
from urllib.parse import urljoin

import requests

import const
from okex import _secret, _proxy, _host
import model

logger = logging.getLogger(__name__)

def query_market_candles(ccy: str, bar: str, since: datetime, until: datetime):
    """
    查询指定 ccy ，指定 bar ，开始时间位于 [since, until) （半闭半开区间）的K线数据。
    注意，since和until只限制了K柱开始时刻。K柱结束时刻不限。
    :param ccy: 货币名称。
    :param bar: k柱宽度
    :param since: K柱开始时刻 >= since
    :param until: K柱开始时刻 < until
    :return:
    """
    default_max_bar = 100  # 默认情况下，一次只能查询到从until前的最后一个bar开始的最后100条记录。
    if until.timestamp() < since.timestamp():
        raise Exception("until is earlier than since")
    if until.timestamp() - since.timestamp() > default_max_bar * const.bar_to_timedelta(bar).total_seconds():
        raise Exception("too large range")
    request_path = "/api/v5/market/candles"
    logger.debug("querying market candles, request_path={}".format(request_path))
    url = _make_url(request_path=request_path)
    headers = _make_headers(request_path=request_path)
    proxies = _make_proxies()
    params = {
        "instId": _get_inst_id(ccy=ccy),
        "bar": bar,
        "before": _make_unix_millisecond(since + timedelta(milliseconds=-1)),
        "after": _make_unix_millisecond(until),
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


def query_trade_fills(last_bill_id: str = None) -> []:
    """
    查询last_bill_id之后的、所有成交了的币币交易。
    :param last_bill_id: 上一次的最后的账单ID。（注意，区别于订单ID ordId ）如果参数是None，会返回三天内的所有账单。
    :return: a list of model.Trade 按照账单ID顺序从小到大排列。
    """
    request_path = "/api/v5/trade/fills"
    # 这个接口要求将查询参数写入签名的加密串
    request_path += "?instType=SPOT"
    if last_bill_id is not None:
        request_path += "&before=" + last_bill_id
    logger.debug("querying trade fills, request_path={}".format(request_path))
    url = _make_url(request_path=request_path)
    headers = _make_headers(request_path=request_path)
    proxies = _make_proxies()
    rsp = requests.get(url=url, headers=headers, proxies=proxies)
    if rsp.status_code != 200:
        raise Exception("http status code {} body {}".format(rsp.status_code, rsp.json()))
    body = rsp.json()
    if body.get("code") != "0":
        raise Exception("response code {}".format(body))
    trades = []
    for t in body.get("data"):
        trades.append(model.Trade(
            ccy=t["instId"].split("-")[0].lower(),
            price=float(t["fillPx"]),
            crypto=float(t["fillSz"]) * (1.0 if t["side"] == "buy" else -1.0),
            bill_id=t["billId"],
        ))
    trades.reverse()
    return trades


def _get_inst_id(ccy: str):
    return "{}-USDT".format(ccy).upper()


def _make_signature(raw: str, secret_key: str) -> str:
    """
    Use b64encode, but NOT encodebytes, to avoid "\n"
    :param raw:
    :param secret_key:
    :return:
    """
    return str(base64.b64encode(
        hmac.new(bytes(secret_key, "utf-8"), msg=bytes(raw, 'utf-8'), digestmod=hashlib.sha256).digest()),
        encoding="utf8")


def _get_timestamp() -> str:
    """
    获取当前的时间戳，YYYY-MM-DDThh:mm:ss.pppZ
    :return:
    """
    return str(datetime.utcnow().isoformat()[:-3]) + "Z"


def _make_unix_millisecond(timestamp: datetime) -> str:
    """
    将 timestamp 转换成 unix 的毫秒数。str类型。
    :param timestamp:
    :return:
    """
    return str(round(timestamp.timestamp() * 1000.0))


def _make_url(request_path: str):
    return urljoin(_host.url, request_path)


def _make_headers(request_path: str):
    req_timestamp = _get_timestamp()
    signature = _make_signature(
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
    return {
        **ok_headers,
        **std_headers,
    }


def _make_proxies():
    return {
        "http": _proxy.url,
        "https": _proxy.url,
    }
