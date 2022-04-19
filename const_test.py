# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, timezone

from const import trim_timestamp


def test_time_trim():
    raw_time = datetime(year=1970, month=1, day=3, hour=22, minute=27, second=24, microsecond=123456,
                        tzinfo=timezone.utc).timestamp()
    assert trim_timestamp(raw_time, timedelta(days=1)) == \
           datetime(year=1970, month=1, day=3, tzinfo=timezone.utc).timestamp()
    assert trim_timestamp(raw_time, timedelta(hours=1)) == \
           datetime(year=1970, month=1, day=3, hour=22, tzinfo=timezone.utc).timestamp()
    assert trim_timestamp(raw_time, timedelta(minutes=15)) == \
           datetime(year=1970, month=1, day=3, hour=22, minute=15, tzinfo=timezone.utc).timestamp()
    assert trim_timestamp(raw_time, timedelta(minutes=1)) == \
           datetime(year=1970, month=1, day=3, hour=22, minute=27, tzinfo=timezone.utc).timestamp()
