# -*- coding: UTF-8 -*-
# 沪深回调做多策略

from strategy.Config import Config
import wx
import schedule
import time
from datetime import datetime
from log.LogSystem import logSys
import tushare as ts
from tools.Utils import Utils
from tools.StockStatusManager import StockStatus
import pandas as pd


stock_data = ""
SHOULD_SOLD = False


class HSCallbackUp:
    # init log system
    logSys.stock_code = ""
    logSys.add_file_log()

    def get_realtime_data(self,STOCK_NUM):
        logSys.log("get_realtime")
        logSys.log("get_realtime_data" + str(Config.STOCK_NUM))
        if Config.DEBUG:
            df = Config.replayManager.get_realtime_data()
            if df.empty:
                print("回放结束,没有最新的点了")
                schedule.clear("daily_task")
                return None
            # 成交量、成交金额
            result = df[['code', 'name', 'price', 'bid', 'ask', 'volume', 'amount', 'time']]
            logSys.log("实时价格:\n")
            logSys.log(result)
            wx.CallAfter(self.call_method, result, result)
            return result
        else:
            try:
                logSys.log("实时价格:\n")
                df = ts.get_realtime_quotes(Config.STOCK_NUM)  # Single stock symbol

            except:
                logSys.log("Socket Connect Error")
                time.sleep(10)
                return None

            result = df[['code', 'name', 'price', 'bid', 'ask', 'volume', 'amount', 'time']]
            logSys.log("实时价格:\n")
            logSys.log(result)
            Config.csvManager.write_df_to_csv(df)
            wx.CallAfter(self.call_method, result, result)
            return result

    def call_method(self, *args):
        result = repr(args)
        global stock_data
        stock_data = stock_data + result + "\n"
        length = len(stock_data.split('\n'))
        if length > 15:
            stock_data = ""

        # ex.st_big.SetLabel(stock_data)

    def write_to_file_buy_in(self, rd, volume):

        # print(str(CURRENT_BUY_Config.STOCK_NUM) + " xxxx" + str(Config.BUY_STOCK_TIMES))

        if (float(rd['volume']) != 0) and (float(rd['volume']) < volume):
            volume = rd['volume']
        volume_total = 0
        SHOULD_SOLD = True

        Config.previous_buy_point = rd

        for i in range(0, Config.BUY_STOCK_TIMES):
            # 查询额度，有多少买多少，一点没有了就退出循环
            real_num = Config.stockHelper.buy_stock(volume)
            if real_num == 0:
                logSys.log('没票了')
                break
            dt = datetime.now()
            csv_name = dt.strftime('appbuy_' + Config.STOCK_NUM + '_' + '%Y%m%d%H%M%S') + '_0' + str(i) + '_order_strategy.csv'
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



    def find_gold_buy_point(self):
     
        try:
            rd = self.get_realtime_data(Config.STOCK_NUM)
            if rd is None:
                return
        except:
            logSys.log("RealTime Connect Error")
            return

        ###########

        # 撤单判定

        ###########

        # 涨停盘卖出
        if SHOULD_SOLD:
            if 'open' in rd:
                change_percent = (float(rd['price']) - float(rd['open'])) / float(rd['price']) * 100
                if change_percent > 9.5 & change_percent < 10.5:
                    self.write_to_file_sold_out(rd, Config.SOLD_STOCK_VOLUME, 2)
            else:
                print("TODO")
        # 超时停盘卖出
        if SHOULD_SOLD:
            if (Utils.get_sec(rd['time']) - Utils.get_sec_str("14:57:00")) > 0:
                # sold_ids=
                self.write_to_file_sold_out(rd, Config.SOLD_STOCK_VOLUME, 5)

        # 买入之后第一个跌势开始卖，涨势和横盘一直持有
        if SHOULD_SOLD:
            if Config.stockStatusManager.state == StockStatus.Down:
                # sold_ids=
                self.write_to_file_sold_out(rd, Config.SOLD_STOCK_VOLUME, 0)
                # 止损卖出
        if SHOULD_SOLD:
            if Config.previous_buy_point is not None and ((float(Config.previous_buy_point['price']) - float(rd['price'])) > 0):
                gap = ((float(Config.previous_buy_point['price']) - float(rd['price'])) / float(Config.previous_buy_point['price']))
                if gap > 0.005:
                    self.write_to_file_sold_out(rd, Config.SOLD_STOCK_VOLUME, 1)

        if Config.DEBUG and rd is None:
            return
      
        if Config.start_point is None:
            Config.start_point = rd

        Config.stockStatusManager.add_stock_point(rd)

        # 初始化慢慢上涨
        logSys.log(Config.stockStatusManager.state)
        if Config.stockStatusManager.state == StockStatus.Down and Config.STATUS == 0:
            Config.Config.start_point = Config.stockStatusManager.stock_arr_min_point()  # 行情下跌, 重置为start 点
            Config.STATUS = 0

        price_float_gap = (float(rd['price']) - float(Config.start_point['price'])) / float(Config.start_point['price'])
        logSys.log("\n" + "目前价格和Start 点价格涨幅 ---  price: GAP = " + str(price_float_gap))
        if price_float_gap > Config.UP_GAP and Config.STATUS == 0:  # 价格提升到2%以上
            logSys.log(">>>>>>>>> 价格超出增长阈值 >>>>>>>>")
            # 进入顶点位置
            Config.STATUS = 2

        # 进入上涨到Top 点状态，开始下跌

        if Config.STATUS == 2:
            if Utils.get_sec(rd['time']) - Utils.get_sec(Config.start_point['time']) < Config.UP_TIME_GAP:
                # 进入下跌状态
                if Config.stockStatusManager.state == StockStatus.Down:
                    Config.top_point = Config.stockStatusManager.stock_arr_max_point()
                    logSys.log("real down")
                    logSys.log(">>>>>>>>>>>>>>>>>>>>> Top Point 上涨区间价格最高点 >>>>>>>>>>>>>>>>")
                    logSys.log(Config.top_point)
                    logSys.log(">>>>>>>>>>>>>>>>>>>>>")

                    Config.STATUS = 1

                if Config.stockStatusManager.state == StockStatus.Up:
                    # 上涨还没结束
                    Config.STATUS = 2

        #  再次上涨
        if Config.STATUS == 1 and Config.stockStatusManager.state == StockStatus.Up:
            logSys.log("进入第二次上涨区间")
            logSys.log('Start Point: \n\n')
            logSys.log(Config.start_point)

            if Config.low_point is None:
                low_point = Config.stockStatusManager.stock_arr_min_point()
                logSys.log('Low Point: \n\n')
                logSys.log(low_point)

            if (float(Config.top_point['price']) - float(Config.low_point['price'])) / (
                    float(Config.top_point['price']) - float(Config.start_point['price'])) < 0.333:
                logSys.log("Down percent is ok")
                if Config.DOWN_TIME_MIN_GAP < Utils.get_sec(rd['time']) - Utils.get_sec(Config.top_point['time']) < Config.DOWN_TIME_MAX_GAP:

                    logSys.log(">>>>>>>>>>>>>>>>>>>>>>=========================>>>>>>>>>>>>>>>>>>>>>>")
                    logSys.log("=========================")
                    logSys.log('Start Point: \n\n')
                    logSys.log(Config.start_point)
                    logSys.log("=========================")

                    logSys.log("=========================")
                    logSys.log('Top Point: \n\n')
                    logSys.log(Config.top_point)
                    logSys.log("=========================")

                    logSys.log("=========================")
                    logSys.log('Low Point: \n\n')
                    logSys.log(Config.low_point)
                    logSys.log("=========================")

                    # buy in
                    logSys.log("=========================")
                    logSys.log('Buy in: \n\n')
                    logSys.log(rd)
                    logSys.log("=========================")
                    logSys.log(">>>>>>>>>>>>>>>>>>>>>>=========================>>>>>>>>>>>>>>>>>>>>>>")
                    if Utils.get_sec(rd['time']) - 9 * 3600 - 32 * 60 < 0:
                        logSys.log("开盘前 2 分钟不买入")
                    else:
                        self.write_to_file_buy_in(rd, Config.BUY_STOCK_VOLUME)
                    Config.STATUS = 0
                    Config.start_point = Config.low_point
                    Config.low_point = None
                    Config.top_point = None
                else:
                    Config.STATUS = 0
                    Config.start_point = Config.low_point
                    Config.low_point = None
                    Config.top_point = None

            else:
                Config.STATUS = 0
                Config.start_point = Config.low_point
                Config.low_point = None
                Config.top_point = None
        else:
            logSys.log("=========================")


