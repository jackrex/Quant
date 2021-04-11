#!/usr/bin/python
# -*- coding: UTF-8 -*-

from enum import Enum
from log.LogSystem import logSys
from tools.IStockStatusManager import IStockStatusManager, StockStatus


class StockStatusManager(IStockStatusManager):
    def __init__(self):
        # 五点集
        super().__init__()
        self.__stock_point_arr = []
        self.state = StockStatus.Stable
        self.previous_ave = 0

    def add_stock_point(self, rd):
        if len(self.__stock_point_arr) >= 5:
            self.__stock_point_arr.pop(0)
        self.__stock_point_arr.append(rd)
        self.state = self.__stock_arr_status()

    def last_stock_point(self):
        if len(self.__stock_point_arr) <= 0:
            return None
        return self.__stock_point_arr[-1]

    def volume_sum_stock_point(self):
        return (float(self.__stock_point_arr[-1]['volume']) - float(self.__stock_point_arr[0]['volume'])) / 100
        # volume_sum = 0
        # for point in self.__stock_point_arr:
        #     volume_sum = volume_sum + float(point['volume'])
        # return volume_sum

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

    def ave(self):
        total = 0
        for num, rd in enumerate(self.__stock_point_arr, start=0):
            total = total + rd['last_price']
        return total / len(self.__stock_point_arr)

    def reset(self):
        self.__stock_point_arr = []
        self.state = StockStatus.Stable

    # 股票状态上涨 1，平稳 0， 下跌 -1
    def __stock_arr_status(self):
        if len(self.__stock_point_arr) < 5:
            return StockStatus.Stable

        max_price = float(self.__stock_point_arr[0]['last_price'])
        min_price = max_price
        arr_price_up_count = 0
        arr_price_down_count = 0

        # 图形修正 如果队列中后边的连续 3 个点是单调递增或者递减序列  则认为就是上升或者下降状态
        first_price = float(self.__stock_point_arr[0]['last_price'])
        second_price = float(self.__stock_point_arr[1]['last_price'])
        third_price = float(self.__stock_point_arr[2]['last_price'])
        fourth_price = float(self.__stock_point_arr[3]['last_price'])
        fifth_price = float(self.__stock_point_arr[4]['last_price'])

        print(str(first_price) + "-" + str(second_price) + "-" + str(third_price) + "-" + str(fourth_price) + "-" + str(fifth_price))

        if fifth_price > fourth_price >= third_price or \
                fifth_price >= fourth_price > third_price:
                # or \
                # fourth_price >= third_price > second_price or \
                # fourth_price > third_price >= second_price:
            logSys.log("连续递增")
            self.turning_min_price = third_price
            self.turning_max_price = fifth_price
            return StockStatus.Up
        elif fifth_price < fourth_price <= third_price or \
                fifth_price <= fourth_price < third_price:
            # or \
            #     fourth_price < third_price <= second_price or \
            #     fourth_price <= third_price < second_price:
            logSys.log("连续递减")
            self.turning_min_price = fifth_price
            self.turning_max_price = third_price
            return StockStatus.Down
        elif fifth_price == fourth_price == third_price and first_price > second_price >= third_price:
            logSys.log("----")
            self.turning_min_price = fifth_price
            self.turning_max_price = first_price
            return StockStatus.Down
        elif fifth_price == fourth_price == third_price and first_price < second_price <= third_price:
            self.turning_min_price = first_price
            self.turning_max_price = fifth_price
            return StockStatus.Up
        else:
            self.turning_min_price = self.stock_arr_min_point()['last_price']
            self.turning_max_price = self.stock_arr_max_point()['last_price']

        for num, rd in enumerate(self.__stock_point_arr, start=0):
            if num == 0:
                continue

            if float(rd['last_price']) > max_price:
                max_price = float(rd['last_price'])
                arr_price_up_count = arr_price_up_count + 1

            if float(rd['last_price']) < min_price:
                min_price = float(rd['last_price'])
                arr_price_down_count = arr_price_down_count + 1

        print("arr_price_up_count=" + str(arr_price_up_count) + ", arr_price_down_count=" + str(arr_price_down_count))
        if arr_price_up_count >= 2:
            return StockStatus.Up

        if arr_price_down_count >= 2:
            return StockStatus.Down

        return StockStatus.Stable
