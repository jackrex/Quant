#!/usr/bin/python
# -*- coding: UTF-8 -*-
from .DataFrameCSVManager import *
import pandas as pd


class ReplayManager:

    def __init__(self):
        self.__currentDebugIndex = -1
        self.dfs = None

    def setup(self, fileName):
        self.dfs = read_csv_to_df(fileName)
        self.__currentDebugIndex = -1

    def get_realtime_data(self):
        self.__currentDebugIndex = self.__currentDebugIndex + 1
        return self.dfs.iloc[self.__currentDebugIndex:self.__currentDebugIndex + 1]
