# -*- coding: utf-8 -*-

class Price:
    """
    表示价格，附有单位
    """

    def __init__(self, name, value, unit="usdt"):
        self._name = name
        self._value = value
        self._unit = unit

    def __str__(self):
        return str(self._value)


class Closing(Price):
    def __init__(self, value: float, unit='usdt'):
        super(Closing, self).__init__(name='closing', value=value, unit=unit)


class MA7(Price):
    def __init__(self, value: float, unit='usdt'):
        super(MA7, self).__init__(name='ma7', value=value, unit=unit)


class MA13(Price):
    def __init__(self, value: float, unit='usdt'):
        super(MA13, self).__init__(name='ma13', value=value, unit=unit)


class MA55(Price):
    def __init__(self, value: float, unit='usdt'):
        super(MA55, self).__init__(name='ma55', value=value, unit=unit)


class Balance:
    """
    表示资产数。可以用于保存加密货币、usdt等。
    """

    def __init__(self, name, balance):
        self._name = name
        self._balance = balance

    def __str__(self):
        return str(self._balance)


class Crypto(Balance):
    pass


class USDT(Balance):
    def __init__(self, balance):
        super(USDT, self).__init__(name='usdt', balance=balance)


class Score:
    """
    表示仓位的分数，从0.0空仓~1.0满仓
    """

    def __init__(self, value):
        self._value = value

    def __str__(self):
        return str(self._value)
