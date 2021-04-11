#!/usr/bin/python
# -*- coding: UTF-8 -*-
from abc import abstractmethod, ABC
from enum import Enum


class StockStatus(Enum):
    Down = -1
    Stable = 0
    Up = 1


class IStockStatusManager(ABC):
    def __init__(self):
        self.turning_min_price = 0
        self.turning_max_price = 0
        pass

    @abstractmethod
    def add_stock_point(self, rd):
        """

        :param rd:
        :return:
        """

    @abstractmethod
    def last_stock_point(self):
        """

        :return:
        """

    @abstractmethod
    def volume_sum_stock_point(self):
        """

        :return:
        """

    @abstractmethod
    def stock_arr_min_point(self):
        """

        :return:
        """

    @abstractmethod
    def stock_arr_max_point(self):
        """

        :return:
        """