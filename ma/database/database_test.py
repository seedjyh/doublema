# -*- coding: utf-8 -*-
import datetime

import pytest as pytest

from ma.database import database


class TestDatabase:
    def test_insert_existed_key(self):
        db = database.Database(
            name="btc",
            primary_key="date",
            fields=["date", "usdt_balance"],
        )
        r1 = {"date": "2022-03-28"}
        r2 = {"date": "2022-03-28", "usdt_balance": "3.14"}
        db.insert(r1)
        with pytest.raises(database.DuplicatePrimaryKey) as e:
            db.insert(r2)

    def test_update_not_exists_key(self):
        db = database.Database(
            name="btc",
            primary_key="date",
            fields=["date", "usdt_balance"],
        )
        with pytest.raises(database.NoSuchPrimaryKey) as e:
            db.update(values={"date": "2022-03-28", "usdt_balance": "3.14"})

    def test_insert(self):
        db = database.Database(
            name="btc",
            primary_key="date",
            fields=["date", "usdt_balance"],
        )
        r1 = {"date": "2022-03-28"}
        r2 = {"date": "2022-03-27"}
        db.insert(r1)
        db.insert(r2)
        res = db.values()
        assert res[0]["date"] == "2022-03-27"
        assert res[1]["date"] == "2022-03-28"

    def test_insert_invalid_fields(self):
        db = database.Database(
            name="btc",
            primary_key="date",
            fields=["date", "usdt_balance"],
        )
        db.insert({"date": "2022-03-27", "price": "1.23"})
        res = db.values()
        assert res[0]["date"] == "2022-03-27"
        assert res[0].get("price") is None

    def test_insert_with_invalid_value_type(self):
        db = database.Database(
            name="btc",
            primary_key="date",
            fields=["date", "usdt_balance"],
        )
        with pytest.raises(database.InvalidValueType) as e:
            db.insert({"date": "2022-03-27", "usdt_balance": 1.23})

    def test_update_partial_fields(self):
        db = database.Database(
            name="btc",
            primary_key="date",
            fields=["date", "usdt_balance", "k_price"],
        )
        db.insert({"date": "2022-03-28"})
        db.update({"date": "2022-03-28", "k_price": "3.14"})
        rec = db.values()[0]
        assert rec["date"] == "2022-03-28"
        assert rec["k_price"] == "3.14"
        assert rec["usdt_balance"] == ""
