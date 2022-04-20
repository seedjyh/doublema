# -*- coding: utf-8 -*-
import pytest

from rangebreak import _position


def test_add_one():
    _position.init(db_name=":memory:")
    _position.add_one(ccy="btc")
    _position.add_one(ccy="eth")
    _position.add_one(ccy="doge")
    res = _position.query_all()
    assert len(res) == 3
    assert res[0].ccy == "btc"
    assert res[0].unit == 0.0
    assert res[1].ccy == "doge"
    assert res[1].unit == 0.0
    assert res[2].ccy == "eth"
    assert res[2].unit == 0.0


def test_add_one_exists():
    with pytest.raises(Exception):
        _position.init(db_name=":memory:")
        _position.add_one(ccy="btc")
        _position.add_one(ccy="btc")


def test_update_one():
    _position.init(db_name=":memory:")
    _position.add_one(ccy="btc")
    _position.update_one(ccy="btc", delta_unit=2.5)
    assert _position.query_one(ccy="btc").unit == 2.5
    _position.update_one(ccy="btc", delta_unit=-3.6)
    assert _position.query_one(ccy="btc").unit == -1.1


def test_update_one_not_exists():
    with pytest.raises(Exception):
        _position.init(db_name=":memory:")
        _position.update_one(ccy="btc", delta_unit=2.5)
