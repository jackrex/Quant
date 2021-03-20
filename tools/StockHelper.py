#!/usr/bin/python
# -*- coding: UTF-8 -*-

from enum import Enum
from log.LogSystem import logSys
import json
import math


class StockHelper:

    def __init__(self, STOCK_NUM):
        self.config = "./buy_config" + STOCK_NUM + ".json"

    def write_sync_stocks(self, num):
        with open(self.config, "w") as outfile:
            dicts = {"stock_num": num}
            json.dump(dicts, outfile)

    def read_sync_stocks(self):
        f = open(self.config)
        data = json.load(f)
        print(data)
        print(data['stock_num'])
        f.close()
        return data['stock_num']

    def buy_stock(self, num):
        remain_stock = self.read_sync_stocks()
        
        if remain_stock < 1:
            return 0
        if (remain_stock - num) <= 0:
            # 不够了只买入这么多
            remain_stock_int=math.floor(remain_stock)
            self.write_sync_stocks(remain_stock-remain_stock_int)
            return remain_stock_int

        if remain_stock - num > 0:
            self.write_sync_stocks(remain_stock-num)
            return num


