# -*- coding: utf-8 -*-
import pytest as pytest

from doublema.database import Database, Record, RecordExistsError, NoSuchRecordError


class TestDatabase:
    def test_add_existed_date(self):
        db = Database(crypto_name="btc")
        r = Record(date="2022-03-28")
        db.add_record(record=r)
        with pytest.raises(RecordExistsError) as e:
            db.add_record(record=r)

    def test_set_not_exist_date(self):
        db = Database(crypto_name="btc")
        r = Record(date="2022-03-28")
        with pytest.raises(NoSuchRecordError) as e:
            db.set_record(record=r)

    def test_add_order_by_date(self):
        db = Database(crypto_name="btc")
        r1 = Record(date="2022-03-28")
        r2 = Record(date="2022-03-27")
        db.add_record(r1)
        db.add_record(r2)
        res = db.records()
        assert res[0].date == "2022-03-27"
        assert res[1].date == "2022-03-28"

    def test_set_partial_fields(self):
        db = Database(crypto_name="btc")
        r = Record(date="2022-03-28")
        db.add_record(r)
        db.set_record(record=Record(date="2022-03-28", k_price=3.14))
        rec = db.records()
        assert rec[0].date == "2022-03-28"
        assert rec[0].k_price == 3.14
        assert rec[0].ma13_price is None
