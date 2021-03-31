# -*- coding: UTF-8 -*-
# 沪深回调做多策略

from strategy.Config import Config
from log.LogSystem import logSys
from tools.Utils import Utils
from tools.StockStatusManager import StockStatus
from strategy.InstanceConfig import *
import futu as ft
import schedule

stock_data = ""
SHOULD_SOLD = False

class StockQuote(ft.StockQuoteHandlerBase):
    def on_recv_rsp(self, rsp_str):
        ret_code, data = super(StockQuote,self).on_recv_rsp(rsp_str)
        if ret_code != ft.RET_OK:
            print("StockQuoteTest: error, msg: %s" % data)
            return ft.RET_ERROR, data
        print("StockQuoteTest ", data) # StockQuoteTest自己的处理逻辑
        result = data[['code', 'last_price', 'prev_close_price', 'open_price', 'data_time', 'volume']]
        self.call_method(result)

        # for item in data.keys():
        #     print("item: " + item)
        self.find_gold_buy_point(data)

        return ft.RET_OK, data

    def find_gold_buy_point(self, rd):

        # 涨停盘卖出
        if SHOULD_SOLD:
            if 'open' in rd:
                change_percent = (float(rd['last_price']) - float(rd['open'])) / float(rd['last_price']) * 100
                if change_percent > 9.5 & change_percent < 10.5:
                    Utils.write_to_file_sold_out(rd, Config.SOLD_STOCK_VOLUME, 2)
            else:
                print("TODO")
        # 超时停盘卖出
        if SHOULD_SOLD:
            if (Utils.get_sec(rd['time']) - Utils.get_sec_str("16:00:00")) > 0:
                # sold_ids=
                Utils.write_to_file_sold_out(rd, Config.SOLD_STOCK_VOLUME, 5)

        # 买入之后第一个跌势开始卖，涨势和横盘一直持有
        if SHOULD_SOLD:
            if Config.stockStatusManager.state == StockStatus.Down:
                # sold_ids=
                Utils.write_to_file_sold_out(rd, Config.SOLD_STOCK_VOLUME, 0)
                # 止损卖出
        if SHOULD_SOLD:
            if Config.previous_buy_point is not None and (
                    (float(Config.previous_buy_point['last_price']) - float(rd['last_price'])) > 0):
                gap = ((float(Config.previous_buy_point['last_price']) - float(rd['last_price'])) / float(
                    Config.previous_buy_point['last_price']))
                if gap > 0.005:
                    Utils.write_to_file_sold_out(rd, Config.SOLD_STOCK_VOLUME, 1)

        if Config.DEBUG and rd is None:
            return

        if Config.start_point is None:
            Config.start_point = rd

        Config.stockStatusManager.add_stock_point(rd)

        # 初始化慢慢上涨
        logSys.log(Config.stockStatusManager.state)
        if Config.stockStatusManager.state == StockStatus.Down and Config.STATUS == 0:
            Config.start_point = Config.stockStatusManager.stock_arr_min_point()  # 行情下跌, 重置为start 点
            Config.STATUS = 0

        price_float_gap = (float(rd['last_price']) - float(Config.start_point['last_price'])) / float(Config.start_point['last_price'])
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

            if (float(Config.top_point['last_price']) - float(Config.low_point['last_price'])) / (
                    float(Config.top_point['last_price']) - float(Config.start_point['last_price'])) < 0.333:
                logSys.log("Down percent is ok")
                if Config.DOWN_TIME_MIN_GAP < Utils.get_sec(rd['time']) - Utils.get_sec(
                        Config.top_point['time']) < Config.DOWN_TIME_MAX_GAP:

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
                        Utils.write_to_file_buy_in(rd, Config.BUY_STOCK_VOLUME)
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



    def call_method(self, *args):
        result = repr(args)
        global stock_data
        stock_data = stock_data + result + "\n"
        length = len(stock_data.split('\n'))
        if length > 15:
            stock_data = ""
        logSys.log(stock_data)

class FTCallbackUp:
    # init log system
    logSys.stock_code = ""
    logSys.add_file_log()

    def __init__(self):
        quote_ctx = ft.OpenQuoteContext(host='127.0.0.1', port=11111)
        print('current subscription status :', quote_ctx.query_subscription())  # 查询初始订阅状态

        handler = StockQuote()
        quote_ctx.set_handler(handler)  # 设置实时报价回调
        ret_sub, err_message = quote_ctx.subscribe(['HK.00700'], [ft.SubType.QUOTE])  # 订阅实时报价类型，FutuOpenD开始持续收到服务器的推送
        if ret_sub == ft.RET_OK:  # 订阅成功
            print('subscribe successfully！current subscription status :', quote_ctx.query_subscription())  # 订阅成功后查询订阅状态
            time_interval = Config.TIME_SCHEDULE
            schedule.every(time_interval).seconds.do(InstanceConfig.ftCallbackup.find_gold_buy_point).tag("daily_task")  # 没有后面的括号
            ft.time.sleep(600)  # 设置脚本接收FutuOpenD的推送持续时间为600秒
            quote_ctx.close()
        else:
            print('subscription failed', err_message)






