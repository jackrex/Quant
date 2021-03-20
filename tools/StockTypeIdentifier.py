#!/usr/bin/python
# -*- coding: UTF-8 -*-

from enum import Enum


class StockType(Enum):
    INVALID = 0
    SHENZHEN = 1
    SHANGHAI = 2


class StockTypeIdentifier:

    def __init__(self):
        self.type = StockType.SHENZHEN

    def stock_type(self, code):
        if code.startswith("3") or code.startswith("0"):
            return StockType.SHENZHEN

        if code.startswith("6"):
            return StockType.SHANGHAI
        return StockType.INVALID



