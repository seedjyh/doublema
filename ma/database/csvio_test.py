# -*- coding: utf-8 -*-
from ma.database import database, csvio


def test_save_empty_database():
    db = database.Database(
        name="btc",
        primary_key="date",
        fields=["usdt", "date", "crypto"]
    )
    csvio.save(db)
    db2 = csvio.load("btc")
    assert db2.name() == "btc"
    assert db2.primary_key() == "date"
    assert db2.fields() == ["date", "usdt", "crypto"]


def test_save_partial_fields():
    db = database.Database(
        name="btc",
        primary_key="date",
        fields=["usdt", "date", "crypto"]
    )
    db.insert({"date": "2022-03-30", "usdt": "1.0", })
    csvio.save(db)
    db2 = csvio.load("btc")
    assert db2.name() == "btc"
    assert db2.primary_key() == "date"
    assert db2.fields() == ["date", "usdt", "crypto"]
    values = db2.values()
    assert len(values) == 1
    assert values[0]["date"] == "2022-03-30"
    assert values[0]["usdt"] == "1.0"
    assert values[0]["crypto"] == ""
