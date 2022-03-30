# -*- coding: utf-8 -*-

from ma import types


class TestClosing:
    def test_str(self):
        assert str(types.Closing(value=3.14)) == "3.14"
        assert str(types.Closing(value=3.140)) == "3.14"
