# -*- coding: UTF-8 -*-

from strategy.Config import Config
import schedule
import time
from datetime import datetime
import pandas as pd


class Utils:

    staticmethod
    def get_sec(self, time_str):
        """Get Seconds from time."""
        words = time_str.str.split()
        h, m, s = words.values[0][0].split(':')
        return int(h) * 3600 + int(m) * 60 + int(s)

    def get_sec_str(self, time_str):
        """Get Seconds from time."""
        h, m, s = time_str.split(':')
        return int(h) * 3600 + int(m) * 60 + int(s)

    def write_to_file_buy_in(self, rd, volume):

        # print(str(CURRENT_BUY_Config.STOCK_NUM) + " xxxx" + str(Config.BUY_STOCK_TIMES))

        if (float(rd['volume']) != 0) and (float(rd['volume']) < volume):
            volume = rd['volume']
        volume_total = 0
        Config.SHOULD_SOLD = True

        Config.previous_buy_point = rd

        for i in range(0, Config.BUY_STOCK_TIMES):
            # 查询额度，有多少买多少，一点没有了就退出循环
            real_num = Config.stockHelper.buy_stock(volume)
            if real_num == 0:
                logSys.log('没票了')
                break
            dt = datetime.now()
            csv_name = dt.strftime('appbuy_' + Config.STOCK_NUM + '_' + '%Y%m%d%H%M%S') + '_0' + str(
                i) + '_order_strategy.csv'
            # dataframe = pd.DataFrame(
            #     {'证券代码': [Config.STOCK_NUM], '委托方向买入': [1], 'time': [rd['time']], 'price': [rd['price']], '委托数量': [volume]})
            # logSys.log("buy_stock_time" + str(Config.BUY_STOCK_TIMES))
            # dataframe.to_csv(csv_name, index=False, sep=',', encoding='utf-8')

            #######

            # 开仓

            #######

            # 累计买入总和
            volume_total = real_num + volume_total
        # 如果多次总和为0，即没有真正买入,已经没有票
        if volume_total == 0:
            Config.SHOULD_SOLD = False
            # 暂停程序
            input('余额不足，程序已停止')
        else:
            # 如果有买入,应卖数量为买入总和/应卖次数，当仓位足够时，Config.SOLD_STOCK_VOLUME和默认值一致

            # 剔除单次买入为小数的情况
            # 1.当买入数量小于卖出次数时
            # 如：共买入5手，应卖出6次，此时应卖出改为5次，每次卖出1手
            if volume_total <= Config.BUY_STOCK_TIMES:
                Config.BUY_STOCK_TIMES = volume_total

                # 2.当买入数量大于卖出次数时
            else:
                # 如果买入数量能被卖出次数整除
                # 如买入10手，应卖出5次，正常情况，单次为总买入除以卖出次数
                if volume_total % Config.BUY_STOCK_TIMES == 0:
                    Config.SOLD_STOCK_VOLUME = volume_total / Config.BUY_STOCK_TIMES
                # 如果买入数量不能被整除
                # 如计划买入10手，实际买入8手，计划卖出5次，此时余数为3
                else:
                    # 余数为3
                    remainder = volume_total % Config.BUY_STOCK_TIMES
                    # 卖出改为5手
                    volume_total = volume_total - remainder
            # 单次卖出为1手，保留余数的3手到最后一次卖出（卖出函数中设置）
            Config.SOLD_STOCK_VOLUME = volume_total / Config.BUY_STOCK_TIMES

    # 跌破 0.5% 就出场严格止损
    def write_to_file_sold_out(self, rd, volume, status):

        global SHOULD_SOLD
        SHOULD_SOLD = False

        if (float(rd['volume']) != 0) and (float(rd['volume']) < volume):
            volume = rd['volume']

        Config.previous_sell_point = rd

        for i in range(0, Config.BUY_STOCK_TIMES):
            if i == Config.BUY_STOCK_TIMES - 1:
                volume = volume + Config.remainder
            dt = datetime.now()
            csv_name = dt.strftime('appsold_' + Config.STOCK_NUM + '_' + '%Y%m%d%H%M%S') + '_0' + str(
                i) + '_order_strategy.csv'
            dataframe = pd.DataFrame(
                {'外部委托序号': ['1'], '证券代码': [Config.STOCK_NUM], '委托方向卖出': [0], '卖出': [status], 'time': [rd['time']],
                 'buy_time': [Config.previous_buy_point['time']],
                 'price': [rd['price']],
                 '委托数量': [volume]})
            dataframe.to_csv(csv_name, index=False, sep=',', encoding='utf-8')

        Config.remainder = 0

