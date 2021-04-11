#!/usr/bin/python
# -*- coding: UTF-8 -*-
from log.LogSystem import logSys
from tools.IStockStatusManager import IStockStatusManager, StockStatus


class SimpleStockStatusManager(IStockStatusManager):

    def __init__(self):
        # 三点集
        super().__init__()
        self.__stock_point_arr = []
        self.state = StockStatus.Stable
        self.previous_ave = 0

    def add_stock_point(self, rd):
        if len(self.__stock_point_arr) >= 3:
            self.__stock_point_arr.pop(0)
        self.__stock_point_arr.append(rd)
        self.state = self.__stock_arr_status()

    def last_stock_point(self):
        if len(self.__stock_point_arr) <= 0:
            return None
        return self.__stock_point_arr[-1]

    def volume_sum_stock_point(self):
        pass

    def stock_arr_min_point(self):
        min_price = float(self.__stock_point_arr[0]['last_price'])
        min_point = self.__stock_point_arr[0]
        for num, rd in enumerate(self.__stock_point_arr, start=0):
            if num == 0:
                continue

            if float(rd['last_price']) < min_price:
                min_price = float(rd['last_price'])
                min_point = rd

        return min_point

    def stock_arr_max_point(self):
        max_price = float(self.__stock_point_arr[0]['last_price'])
        max_point = self.__stock_point_arr[0]
        for num, rd in enumerate(self.__stock_point_arr, start=0):
            if num == 0:
                continue

            if float(rd['last_price']) > max_price:
                max_price = float(rd['last_price'])
                max_point = rd

        return max_point

        # 股票状态上涨 1，平稳 0， 下跌 -1

    def __stock_arr_status(self):
        if len(self.__stock_point_arr) < 3:
            return StockStatus.Stable

        # 图形修正 如果队列中后边的连续 3 个点是单调递增或者递减序列  则认为就是上升或者下降状态
        first_price = float(self.__stock_point_arr[0]['last_price'])
        second_price = float(self.__stock_point_arr[1]['last_price'])
        third_price = float(self.__stock_point_arr[2]['last_price'])

        print(str(first_price) + "-" + str(second_price) + "-" + str(third_price) + "-")

        if third_price == second_price == first_price:
            self.turning_min_price = first_price
            self.turning_max_price = first_price
            return StockStatus.Stable
        elif third_price >= second_price > first_price:
            self.turning_min_price = first_price
            self.turning_max_price = third_price
            logSys.log("3值连续递增")
            return StockStatus.Up
        elif first_price >= second_price > third_price:
            self.turning_min_price = third_price
            self.turning_max_price = first_price
            logSys.log("3值连续递减")
            return StockStatus.Down
        elif third_price > second_price and first_price > second_price:
            self.turning_min_price = second_price
            self.turning_max_price = max(first_price, third_price)
            logSys.log("2值递增")
            return StockStatus.Up
        elif third_price < second_price and first_price < second_price:
            self.turning_min_price = min(third_price, first_price)
            self.turning_max_price = second_price
            logSys.log("2值递减")
            return StockStatus.Down

        return StockStatus.Stable
