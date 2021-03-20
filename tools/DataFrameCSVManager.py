#!/usr/bin/python
# -*- coding: UTF-8 -*-
from datetime import datetime
import pandas as pd


def read_csv_to_df(file_name):
    df = pd.read_csv(file_name)
    return df


class DataFrameCSVManager:

    def __init__(self):
        self.csv_file_name = "csv.csv"
        self.stock_code = None
        self.first_set_csv = False

    # 初始化
    def setUp(self):
        self.csv_file_name = "./" + self.__file_name() + self.csv_file_name

    def write_df_to_csv(self, df):
        if not self.first_set_csv:
            self.first_set_csv = True
            df.to_csv(self.csv_file_name, mode='w', index=False, encoding='utf-8')
        else:
            df.to_csv(self.csv_file_name, mode='a', header=False, index=False, encoding='utf-8')

    def __file_name(self):
        dt = datetime.now()
        file_name = self.stock_code + "_" + dt.strftime('%Y%m%d%H%M%S') + "_"
        return file_name
