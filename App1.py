# -*- coding: UTF-8 -*-
# 回调做多策略

import wx
import tushare as ts
import schedule
import time
from threading import Thread
from tools.StockStatusManager import StockStatusManager
from tools.StockStatusManager import StockStatus
from tools.StockHelper import StockHelper
from tools.DataFrameCSVManager import *
from tools.ReplayManager import ReplayManager
from log.LogSystem import logSys
from tools.CPlusBridge import CPlusBridge

################# GLOBE CONFIG

SHOULD_SOLD = False
BUY=False
SOLD=False

TIME_SCHEDULE = 2

STOCK_NUM = "600100"
UP_GAP = 0.01
UP_TIME_GAP = 5 * 60
DOWN_GAP = 0.5
DOWN_TIME_MIN_GAP = 9
DOWN_TIME_MAX_GAP = 90

BUY_PRICE_GAP = 0.05
BUY_STOCK_TIMES = 3
BUY_STOCK_VOLUME = 100

SOLD_PRICE_GAP = 0.05
SOLD_STOCK_TIMES = 3
SOLD_STOCK_VOLUME = 100


CURRENT_BUY_STOCK_NUM = 0

#######################

stock_point_arr = []

DOWN_UP_MAX_COUNT = 1
STATUS = 0  # 0,1,2 0 Up  1 Down  2 Up Again
down_count = 0  # Up Trends down count 4 for 3 is ok
up_count = 0  # Down Trends up count 4 for 3 is ok

start_point = None
remainder=0
top_point = None
low_point = None
previous_buy_point = None
previous_sell_point =None
stockStatusManager = StockStatusManager()
stockHelper = None
CPlusBridge=CPlusBridge()
csvManager = DataFrameCSVManager()

##########################

D_FLAG = False

if D_FLAG:
    # debug
    replayManager = ReplayManager()
    replayManager.setup("300737_20200820092756_csv.csv")
    DEBUG = True
else:
    replayManager = ReplayManager()
    DEBUG = False


class AppGUI(wx.Frame):

    def __init__(self, parent, title):
        super(AppGUI, self).__init__(parent, title=title,
                                     size=(1000, 800))
        self.Centre()
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.init_UI()

    def init_UI(self):
        panel = wx.Panel(self, wx.ID_ANY)

        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(14)

        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(panel, label='Stock Code / 股票代码')
        st1.SetFont(font)
        hbox1.Add(st1, flag=wx.RIGHT, border=8)
        self.tc = wx.TextCtrl(panel)
        self.tc.AppendText("600100")
        hbox1.Add(self.tc, proportion=1)
        vbox.Add(hbox1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        vbox.Add((-1, 10))

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        st2 = wx.StaticText(panel, label='Up Gap / 股票拉升幅度')
        st2.SetFont(font)
        hbox2.Add(st2, flag=wx.RIGHT, border=8)
        self.tc2 = wx.TextCtrl(panel)
        self.tc2.AppendText("0.01")
        hbox2.Add(self.tc2, proportion=1)
        vbox.Add(hbox2, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        vbox.Add((-1, 10))

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        st3 = wx.StaticText(panel, label='Up Time Gap Max / 股票拉升时间最大值 秒')
        st3.SetFont(font)
        hbox3.Add(st3, flag=wx.RIGHT, border=8)
        self.tc3 = wx.TextCtrl(panel)
        self.tc3.AppendText("300")
        hbox3.Add(self.tc3, proportion=1)
        vbox.Add(hbox3, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        vbox.Add((-1, 10))

        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        st4 = wx.StaticText(panel, label='Down Gap / 股票回调下探最大幅度')
        st4.SetFont(font)
        hbox4.Add(st4, flag=wx.RIGHT, border=8)
        self.tc4 = wx.TextCtrl(panel)
        self.tc4.AppendText("0.5")
        hbox4.Add(self.tc4, proportion=1)
        vbox.Add(hbox4, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        vbox.Add((-1, 10))

        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        st5 = wx.StaticText(panel, label='Down Gap Min Time / 股票下探最小要求时间 秒')
        st5.SetFont(font)
        hbox5.Add(st5, flag=wx.RIGHT, border=8)
        self.tc5 = wx.TextCtrl(panel)
        self.tc5.AppendText("9")
        hbox5.Add(self.tc5, proportion=1)
        vbox.Add(hbox5, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        vbox.Add((-1, 10))

        hbox6 = wx.BoxSizer(wx.HORIZONTAL)
        st6 = wx.StaticText(panel, label='Down Gap Max Time / 股票下探最大要求时间 秒')
        st6.SetFont(font)
        hbox6.Add(st6, flag=wx.RIGHT, border=8)
        self.tc6 = wx.TextCtrl(panel)
        self.tc6.AppendText("90")
        hbox6.Add(self.tc6, proportion=1)
        vbox.Add(hbox6, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        vbox.Add((-1, 10))

        hbox7 = wx.BoxSizer(wx.HORIZONTAL)
        st7 = wx.StaticText(panel, label='Buy Stocks / 每次买入多少 手')
        st7.SetFont(font)
        hbox7.Add(st7, flag=wx.RIGHT, border=8)
        self.tc7 = wx.TextCtrl(panel)
        self.tc7.AppendText("100")
        hbox7.Add(self.tc7, proportion=1)
        vbox.Add(hbox7, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        vbox.Add((-1, 10))

        hbox8 = wx.BoxSizer(wx.HORIZONTAL)
        st8 = wx.StaticText(panel, label='Buy Times / 买入多少 次')
        st8.SetFont(font)
        hbox8.Add(st8, flag=wx.RIGHT, border=8)
        self.tc8 = wx.TextCtrl(panel)
        self.tc8.AppendText("2")
        hbox8.Add(self.tc8, proportion=1)
        vbox.Add(hbox8, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        vbox.Add((-1, 10))

        hbox9 = wx.BoxSizer(wx.HORIZONTAL)
        st9 = wx.StaticText(panel, label='Price Gap / 买入价格浮动值')
        st9.SetFont(font)
        hbox9.Add(st9, flag=wx.RIGHT, border=8)
        self.tc9 = wx.TextCtrl(panel)
        self.tc9.AppendText("0.05")
        hbox9.Add(self.tc9, proportion=1)
        vbox.Add(hbox9, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        vbox.Add((-1, 10))


        # # 卖出选项
        #
        # hbox10 = wx.BoxSizer(wx.HORIZONTAL)
        # st10 = wx.StaticText(panel, label='Sold Stocks / 每次卖出多少 手')
        # st10.SetFont(font)
        # hbox10.Add(st10, flag=wx.RIGHT, border=8)
        # self.tc10 = wx.TextCtrl(panel)
        # self.tc10.AppendText("100")
        # hbox10.Add(self.tc10, proportion=1)
        # vbox.Add(hbox10, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        #
        # vbox.Add((-1, 10))

        hbox11 = wx.BoxSizer(wx.HORIZONTAL)
        st11 = wx.StaticText(panel, label='Sold Times / 卖出多少 次')
        st11.SetFont(font)
        hbox11.Add(st11, flag=wx.RIGHT, border=8)
        self.tc11 = wx.TextCtrl(panel)
        self.tc11.AppendText("2")
        hbox11.Add(self.tc11, proportion=1)
        vbox.Add(hbox11, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        vbox.Add((-1, 10))

        hbox12 = wx.BoxSizer(wx.HORIZONTAL)
        st12 = wx.StaticText(panel, label='Sold Price Gap / 卖出格浮动值')
        st12.SetFont(font)
        hbox12.Add(st12, flag=wx.RIGHT, border=8)
        self.tc12 = wx.TextCtrl(panel)
        self.tc12.AppendText("0.05")
        hbox12.Add(self.tc12, proportion=1)
        vbox.Add(hbox12, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        vbox.Add((-1, 10))


        # Button
        hbox7 = wx.BoxSizer(wx.HORIZONTAL)
        exec_btn = wx.Button(panel, label='Execution / 执行', pos=(120, 20))
        exec_btn.Bind(wx.EVT_BUTTON, self.on_exec)
        hbox7.Add(exec_btn)
        close_btn = wx.Button(panel, label='Close / 关闭', pos=(120, 20))
        close_btn.Bind(wx.EVT_BUTTON, self.on_close)
        hbox7.Add(close_btn)
        vbox.Add(hbox7, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        vbox.Add((-1, 10))

        # 显示的东西
        self.st_big = wx.StaticText(panel, label='Will Show')
        self.st_big.SetFont(font)
        vbox.Add(self.st_big, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        panel.SetSizer(vbox)

    def on_close(self, e):
        self.Close()

    def OnCloseWindow(self, e):

        dial = wx.MessageDialog(None, 'Are you sure to quit?', 'Question',
                                wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

        ret = dial.ShowModal()

        if ret == wx.ID_YES:
            schedule.clear("daily_task")
            self.Destroy()
        else:
            e.Veto()

    def on_exec(self, e):
        # self.Close(True)
        global STOCK_NUM
        STOCK_NUM = self.tc.GetValue()
        global UP_GAP
        UP_GAP = float(self.tc2.GetValue())

        global UP_TIME_GAP
        UP_TIME_GAP = int(self.tc3.GetValue())

        global DOWN_GAP
        DOWN_GAP = float(self.tc4.GetValue())

        global DOWN_TIME_MIN_GAP
        DOWN_TIME_MIN_GAP = int(self.tc5.GetValue())

        global DOWN_TIME_MAX_GAP
        DOWN_TIME_MAX_GAP = int(self.tc6.GetValue())

        global BUY_PRICE_GAP
        BUY_PRICE_GAP = float(self.tc9.GetValue())

        global BUY_STOCK_VOLUME
        BUY_STOCK_VOLUME = int(self.tc7.GetValue())

        global BUY_STOCK_TIMES
        BUY_STOCK_TIMES = int(self.tc8.GetValue())

        global SOLD_PRICE_GAP
        SOLD_PRICE_GAP = float(self.tc12.GetValue())

        global SOLD_STOCK_TIMES
        SOLD_STOCK_TIMES = int(self.tc11.GetValue())

        global SOLD_STOCK_VOLUME
        SOLD_STOCK_VOLUME = BUY_STOCK_VOLUME * BUY_STOCK_TIMES / SOLD_STOCK_TIMES

        # init log system
        logSys.stock_code = STOCK_NUM
        logSys.add_file_log()

        # init csv
        global csvManager
        csvManager.stock_code = STOCK_NUM
        csvManager.setUp()
        global stockHelper
        stockHelper = StockHelper(STOCK_NUM)
        self.thread = Thread(target=self.threadMethod)
        self.thread.start()

    def threadMethod(self):
        schedule.clear()
        time_interval = TIME_SCHEDULE
        if DEBUG:
            while True:
                find_gold_buy_point()
        schedule.every(time_interval).seconds.do(find_gold_buy_point).tag("daily_task")  # 没有后面的括号
        while True:
            schedule.run_pending()
            time.sleep(1)


def get_history_data(stock_num):
    ts.get_hist_data(stock_num)  # get all data


stock_data = ""


def get_realtime_data(stock_num):
    if DEBUG:
        df = replayManager.get_realtime_data()
        if df.empty:
            print("回放结束,没有最新的点了")
            schedule.clear("daily_task")
            return None
        # 成交量、成交金额
        result = df[['code', 'name', 'price', 'bid', 'ask', 'volume', 'amount', 'time']]
        logSys.log("实时价格:\n")
        logSys.log(result)
        wx.CallAfter(call_method, result, result)
        return result
    else:
        try:
            df = ts.get_realtime_quotes(stock_num)  # Single stock symbol
        except:
            logSys.log("Socket Connect Error")
            time.sleep(10)
            return None


        result = df[['code' ,'name', 'price', 'bid', 'ask', 'volume', 'amount', 'time']]
        logSys.log("实时价格:\n")
        logSys.log(result)
        csvManager.write_df_to_csv(df)
        wx.CallAfter(call_method, result, result)
        return result


def call_method(self, *args):
    result = repr(args)
    global stock_data
    stock_data = stock_data + result + "\n"
    length = len(stock_data.split('\n'))
    if length > 15:
        stock_data = ""

    ex.st_big.SetLabel(stock_data)


def write_to_file_buy_in(rd, volume):
    global STOCK_NUM
    global BUY_STOCK_TIMES
    global previous_buy_point
    global SOLD_STOCK_VOLUME
    global SOLD_STOCK_TIMES
    global SHOULD_SOLD
    global remainder
    

    # print(str(CURRENT_BUY_STOCK_NUM) + " xxxx" + str(BUY_STOCK_TIMES))

    if (float(rd['volume']) != 0) and (float(rd['volume']) < volume):
        volume = rd['volume']
    volume_total=0
    SHOULD_SOLD = True

    previous_buy_point = rd

    for i in range(0, BUY_STOCK_TIMES):
        #查询额度，有多少买多少，一点没有了就退出循环
        real_num= stockHelper.buy_stock(volume)
        if real_num ==0:
            logSys.log('没票了')
            break
        dt = datetime.now()
        csv_name = dt.strftime('appbuy_' + STOCK_NUM + '_' + '%Y%m%d%H%M%S') + '_0' + str(i) + '_order_strategy.csv'
        dataframe = pd.DataFrame(
            {'证券代码': [STOCK_NUM], '委托方向买入': [1], 'time': [rd['time']], 'price': [rd['price']], '委托数量': [volume]})
        logSys.log("buy_stock_time" + str(BUY_STOCK_TIMES))
        dataframe.to_csv(csv_name, index=False, sep=',', encoding='utf-8')

        #######

        #开仓

        #######

        



        #累计买入总和
        volume_total = real_num +volume_total
     #如果多次总和为0，即没有真正买入,已经没有票
    if volume_total == 0:
        SHOULD_SOLD = False
        #暂停程序
        input('余额不足，程序已停止')
    else:
        #如果有买入,应卖数量为买入总和/应卖次数，当仓位足够时，SOLD_STOCK_VOLUME和默认值一致
        
        #剔除单次买入为小数的情况
        #1.当买入数量小于卖出次数时
        #如：共买入5手，应卖出6次，此时应卖出改为5次，每次卖出1手
        if volume_total <= SOLD_STOCK_TIMES:
            SOLD_STOCK_TIMES =volume_total
            
            #2.当买入数量大于卖出次数时
        else:
            #如果买入数量能被卖出次数整除
            #如买入10手，应卖出5次，正常情况，单次为总买入除以卖出次数
            if volume_total % SOLD_STOCK_TIMES ==0:
                SOLD_STOCK_VOLUME = volume_total/ SOLD_STOCK_TIMES
            #如果买入数量不能被整除
            #如计划买入10手，实际买入8手，计划卖出5次，此时余数为3
            else:
                #余数为3
                remainder=volume_total % SOLD_STOCK_TIMES
                #卖出改为5手
                volume_total=volume_total-remainder
        #单次卖出为1手，保留余数的3手到最后一次卖出（卖出函数中设置）
        SOLD_STOCK_VOLUME = volume_total/ SOLD_STOCK_TIMES
        
        

# 跌破 0.5% 就出场严格止损
def write_to_file_sold_out(rd, volume, status):
    global STOCK_NUM
    global SOLD_STOCK_TIMES
    global SOLD_STOCK_VOLUME
    global SHOULD_SOLD
    global remainder
    global previous_buy_point
    global previous_sell_point

    SHOULD_SOLD = False

    if (float(rd['volume']) != 0) and (float(rd['volume']) < volume):
        volume = rd['volume']

    previous_sell_point= rd

    for i in range(0, SOLD_STOCK_TIMES):
        if i== SOLD_STOCK_TIMES-1:
            volume = volume +remainder
        dt = datetime.now()
        csv_name = dt.strftime('appsold_' + STOCK_NUM + '_' + '%Y%m%d%H%M%S') + '_0' + str(i) + '_order_strategy.csv'
        dataframe = pd.DataFrame(
            {'外部委托序号': ['1'], '证券代码': [STOCK_NUM], '委托方向卖出': [0], '卖出': [status], 'time': [rd['time']], 'buy_time': [previous_buy_point['time']],
             'price': [rd['price']],
             '委托数量': [volume]})
        dataframe.to_csv(csv_name, index=False, sep=',', encoding='utf-8')
        
    remainder=0



def get_sec(time_str):
    """Get Seconds from time."""
    words = time_str.str.split()
    h, m, s = words.values[0][0].split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)


def find_gold_buy_point():

    global BUY
    global SOLD
    global SHOULD_SOLD
    global previous_buy_point
    global SOLD_STOCK_VOLUME
    global BUY_STOCK_VOLUME
    global previous_sell_point


    try:
        rd = get_realtime_data(STOCK_NUM)
        if rd is None:
            return
    except:
        logSys.log("RealTime Connect Error")
        return

    ###########

    #撤单判定

    ###########


    # 涨停盘卖出
    if SHOULD_SOLD:
        if 'open' in rd:
            change_percent = (float(rd['price']) - float(rd['open'])) / float(rd['price']) * 100
            if change_percent > 9.5 & change_percent < 10.5:
                write_to_file_sold_out(rd, SOLD_STOCK_VOLUME, 2)
        else:
            print("TODO")
    # 超时停盘卖出
    if SHOULD_SOLD:
        if (get_sec(rd['time']) - get_sec_str("14:57:00")) > 0:
            #sold_ids=
            write_to_file_sold_out(rd, SOLD_STOCK_VOLUME, 5)
            
    # 买入之后第一个跌势开始卖，涨势和横盘一直持有
    if SHOULD_SOLD:
        if stockStatusManager.state == StockStatus.Down:
            #sold_ids=
            write_to_file_sold_out(rd, SOLD_STOCK_VOLUME, 0) 
    # 止损卖出
    if SHOULD_SOLD:
        if previous_buy_point is not None and ((float(previous_buy_point['price']) - float(rd['price'])) > 0):
            gap = ((float(previous_buy_point['price']) - float(rd['price'])) / float(previous_buy_point['price']))
            if gap > 0.005:
                write_to_file_sold_out(rd, SOLD_STOCK_VOLUME, 1)

    if DEBUG and rd is None:
        return
    global start_point
    global low_point
    global top_point
    global STATUS
    global down_count
    global up_count
    global stockStatusManager

    if start_point is None:
        start_point = rd

    stockStatusManager.add_stock_point(rd)

    # 初始化慢慢上涨
    logSys.log(stockStatusManager.state)
    if stockStatusManager.state == StockStatus.Down and STATUS == 0:
        start_point = stockStatusManager.stock_arr_min_point()  # 行情下跌, 重置为start 点
        STATUS = 0

    price_float_gap = (float(rd['price']) - float(start_point['price'])) / float(start_point['price'])
    logSys.log("\n" + "目前价格和Start 点价格涨幅 ---  price: GAP = " + str(price_float_gap))
    if price_float_gap > UP_GAP and STATUS == 0:  # 价格提升到2%以上
        logSys.log(">>>>>>>>> 价格超出增长阈值 >>>>>>>>")
        # 进入顶点位置
        STATUS = 2

    # 进入上涨到Top 点状态，开始下跌

    if STATUS == 2:
        if get_sec(rd['time']) - get_sec(start_point['time']) < UP_TIME_GAP:
            # 进入下跌状态
            if stockStatusManager.state == StockStatus.Down:
                top_point = stockStatusManager.stock_arr_max_point()
                logSys.log("real down")
                logSys.log(">>>>>>>>>>>>>>>>>>>>> Top Point 上涨区间价格最高点 >>>>>>>>>>>>>>>>")
                logSys.log(top_point)
                logSys.log(">>>>>>>>>>>>>>>>>>>>>")

                STATUS = 1

            if stockStatusManager.state == StockStatus.Up:
                # 上涨还没结束
                STATUS = 2

    #  再次上涨
    if STATUS == 1 and stockStatusManager.state == StockStatus.Up:
        logSys.log("进入第二次上涨区间")
        logSys.log('Start Point: \n\n')
        logSys.log(start_point)

        if low_point is None:
            low_point = stockStatusManager.stock_arr_min_point()
            logSys.log('Low Point: \n\n')
            logSys.log(low_point)

        if (float(top_point['price']) - float(low_point['price'])) / (
                float(top_point['price']) - float(start_point['price'])) < 0.333:
            logSys.log("Down percent is ok")
            if DOWN_TIME_MIN_GAP < get_sec(rd['time']) - get_sec(top_point['time']) < DOWN_TIME_MAX_GAP:

                logSys.log(">>>>>>>>>>>>>>>>>>>>>>=========================>>>>>>>>>>>>>>>>>>>>>>")
                logSys.log("=========================")
                logSys.log('Start Point: \n\n')
                logSys.log(start_point)
                logSys.log("=========================")

                logSys.log("=========================")
                logSys.log('Top Point: \n\n')
                logSys.log(top_point)
                logSys.log("=========================")

                logSys.log("=========================")
                logSys.log('Low Point: \n\n')
                logSys.log(low_point)
                logSys.log("=========================")

                # buy in
                logSys.log("=========================")
                logSys.log('Buy in: \n\n')
                logSys.log(rd)
                logSys.log("=========================")
                logSys.log(">>>>>>>>>>>>>>>>>>>>>>=========================>>>>>>>>>>>>>>>>>>>>>>")
                if get_sec(rd['time']) - 9 * 3600 - 32 * 60 < 0:
                    logSys.log("开盘前 2 分钟不买入")
                else:
                    write_to_file_buy_in(rd, BUY_STOCK_VOLUME)
                STATUS = 0
                start_point = low_point
                low_point = None
                top_point = None
            else:
                STATUS = 0
                start_point = low_point
                low_point = None
                top_point = None

        else:
            STATUS = 0
            start_point = low_point
            low_point = None
            top_point = None
    else:
        logSys.log("=========================")


app = wx.App()
ex = AppGUI(None, title='Stock Platform - Apollo')


def main():
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()

