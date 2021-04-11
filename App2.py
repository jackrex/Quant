# -*- coding: UTF-8 -*-
# 突破做多策略
# https://github.com/waditu/tushare
# http://tushare.org/trading.html#id4
# volume 成交量 换作手 /100
# amount 成交额 成交总额度

import wx
import tushare as ts
import schedule
import time
import pandas as pd
from datetime import datetime
from threading import Thread
from tools.StockStatusManager import StockStatusManager
from tools.StockStatusManager import StockStatus
from tools.StockHelper import StockHelper
from tools.DataFrameCSVManager import *
from tools.ReplayManager import ReplayManager
from log.LogSystem import logSys
import os
from tools.CPlusBridge import CPlusBridge
import math

################# GLOBE CONFIG

SHOULD_SOLD = False
BUY=False
SOLD=False


TIME_SCHEDULE = 2
STOCK_NUM = "600100"
UP_GAP = 0.01
UP_TIME_GAP = 5 * 60

PLATFORM_MEAN_VOLUME_MULTIPLE = 2
PLATFORM_BIG_MULTIPLE = 4

BUY_PRICE_GAP = 0.05
BUY_STOCK_TIMES = 1
BUY_STOCK_VOLUME = 100

SOLD_PRICE_GAP = 0.05
SOLD_STOCK_TIMES = 1
SOLD_STOCK_VOLUME = 100

CURRENT_BUY_STOCK_NUM = 0

#######################

stock_point_arr = []

DOWN_UP_MAX_COUNT = 1
STATUS = 0  # 0,1,2 0 Up  1 Down  2 Up Again
down_count = 0  # Up Trends down count 4 for 3 is ok
up_count = 0  # Down Trends up count 4 for 3 is ok

PLATFORM_MAX_POINT = None
PLATFORM_MAX_PRICE = -1  # 进入平台后的最高价
PLATFORM_MEAN_VOLUME = 0
PLATFORM_CAL_MEAN = False
PLATFORM_WAIT_COUNT = 0
PLATFORM_MAX_VOLUME_A = False
platform_point_arr = []
buy_ids=[]
sold_ids=[]
remainder=0
volume_total=0

start_point = None
top_point = None
low_point = None
previous_point = None
previous_buy_point = None
previous_sell_point=None
stockStatusManager = StockStatusManager()
stockHelper = StockHelper(STOCK_NUM)
csvManager = DataFrameCSVManager()
CPlusBridge=CPlusBridge()
##########################

D_FLAG = False

if D_FLAG:
    # debug
    replayManager = ReplayManager()
    replayManager.setup("300807_20200917134038_csv.csv")
    DEBUG = True
else:
    replayManager = ReplayManager()
    DEBUG = False

########################## UI Logic


class AppGUI(wx.Frame):

    def __init__(self, parent, title):
        super(AppGUI, self).__init__(parent, title=title,
                                     size=(1000, 800))
        self.Centre()
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.init_user_interface()

    def init_user_interface(self):
        panel = wx.Panel(self, wx.ID_ANY)

        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(14)

        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(panel, label='Stock Code / 股票代码')
        st1.SetFont(font)
        hbox1.Add(st1, flag=wx.RIGHT, border=8)
        self.tc = wx.TextCtrl(panel)
        self.tc.AppendText("603686")
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
        st4 = wx.StaticText(panel, label='PLATFORM_MEAN_VOLUME_MULTIPLE / 平台价成交量均值倍数')
        st4.SetFont(font)
        hbox4.Add(st4, flag=wx.RIGHT, border=8)
        self.tc4 = wx.TextCtrl(panel)
        self.tc4.AppendText("2")
        hbox4.Add(self.tc4, proportion=1)
        vbox.Add(hbox4, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        vbox.Add((-1, 10))

        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        st5 = wx.StaticText(panel, label='PLATFORM_BIG_MULTIPLE / 大成交5点位同向成交总量')
        st5.SetFont(font)
        hbox5.Add(st5, flag=wx.RIGHT, border=8)
        self.tc5 = wx.TextCtrl(panel)
        self.tc5.AppendText("4")
        hbox5.Add(self.tc5, proportion=1)
        vbox.Add(hbox5, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        vbox.Add((-1, 10))

        hbox6 = wx.BoxSizer(wx.HORIZONTAL)
        st6 = wx.StaticText(panel, label='PLATFORM_Price_Gap / 平台价差')
        st6.SetFont(font)
        hbox6.Add(st6, flag=wx.RIGHT, border=8)
        self.tc6 = wx.TextCtrl(panel)
        self.tc6.AppendText("0")
        hbox6.Add(self.tc6, proportion=1)
        vbox.Add(hbox6, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        vbox.Add((-1, 10))

        hbox7 = wx.BoxSizer(wx.HORIZONTAL)
        st7 = wx.StaticText(panel, label='Buy Stocks / 每次买入多少 手(百股)')
        st7.SetFont(font)
        hbox7.Add(st7, flag=wx.RIGHT, border=8)
        self.tc7 = wx.TextCtrl(panel)
        self.tc7.AppendText("1")
        hbox7.Add(self.tc7, proportion=1)
        vbox.Add(hbox7, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        vbox.Add((-1, 10))

        hbox8 = wx.BoxSizer(wx.HORIZONTAL)
        st8 = wx.StaticText(panel, label='Buy Times / 买入多少 次')
        st8.SetFont(font)
        hbox8.Add(st8, flag=wx.RIGHT, border=8)
        self.tc8 = wx.TextCtrl(panel)
        self.tc8.AppendText("1")
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
        self.tc11.AppendText("1")
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

        global PLATFORM_MEAN_VOLUME_MULTIPLE
        PLATFORM_MEAN_VOLUME_MULTIPLE = float(self.tc4.GetValue())

        global PLATFORM_BIG_MULTIPLE
        PLATFORM_BIG_MULTIPLE = int(self.tc5.GetValue())

        global PLATFORM_Price_Gap
        PLATFORM_Price_Gap = int(self.tc6.GetValue())

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


stock_data = ""


def call_method(self, *args):
    result = repr(args)
    global stock_data
    stock_data = stock_data + result + "\n"
    length = len(stock_data.split('\n'))
    if length > 15:
        stock_data = ""

    ex.st_big.SetLabel(stock_data)


def get_history_data(stock_num):
    ts.get_hist_data(stock_num)  # get all data


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

        global previous_point
        result = df[['open','code', 'name', 'price', 'bid', 'ask', 'volume', 'amount', 'time']]
        if previous_point is not None:
            logSys.log("实时价格:\n")
            logSys.log(result)
            logSys.log("========================")
            volume_gap = (float(result['volume']) - float(previous_point['volume']))/100
            logSys.log("real volume is : " + str(volume_gap) + "手")

        csvManager.write_df_to_csv(df)
        wx.CallAfter(call_method, result, result)
        return result


def write_to_file_buy_in(rd, volume):
    global STOCK_NUM
    global BUY_STOCK_TIMES
    global previous_buy_point
    global top_point
    global SHOULD_SOLD
    global start_point
    global PLATFORM_MEAN_VOLUME
    global PLATFORM_MAX_POINT
    global BUY_PRICE_GAP
    global SOLD_STOCK_VOLUME
    global SOLD_STOCK_TIMES
    global remainder
    global buy_ids
    global BUY
    global volume_total


    # print(str(CURRENT_BUY_STOCK_NUM) + " xxxx" + str(BUY_STOCK_TIMES))

    if (float(rd['volume']) != 0) and (float(rd['volume']) < volume):
        volume = rd['volume']
    volume_total=0

    previous_buy_point = rd

    for i in range(0, BUY_STOCK_TIMES):
        #查询额度，有多少买多少，一点没有了就退出
        real_num= stockHelper.buy_stock(volume)
        if real_num ==0:
            logSys.log('没票了')
            break

        #######

        #开仓

        #######
        buy_price=float(rd['price'])+BUY_PRICE_GAP
        buy_id=CPlusBridge.SendOrder(0,0,STOCK_NUM,buy_price,real_num)
        buy_ids.append(buy_id)

        dt = datetime.now()
        csv_name = dt.strftime('app2buy_' + STOCK_NUM + '_' + '%Y%m%d%H%M%S') + '_0' + str(i) + '_order_strategy.csv'
        dataframe = pd.DataFrame(
            {'证券代码': [STOCK_NUM], 'start_point': [start_point['price']], 'plat_max_point': [PLATFORM_MAX_POINT['price']],
           'top_point': [top_point['price']], 'plat_mean_volume': [PLATFORM_MEAN_VOLUME], '委托方向买入': [1],
           'time': [rd['time']], 'price': [rd['price']], '委托数量': [real_num],'委托编号':[buy_id]})

        logSys.log("buy_stock_time" + str(BUY_STOCK_TIMES))
 #       dataframe.to_csv(csv_name, index=False, sep=',', encoding='utf-8')
        


        #累计买入总和
        volume_total = real_num +volume_total


     #如果多次总和为0，即没有真正买入,已经没有票
    if volume_total == 0:
        #暂停程序
        input('余额不足，程序已停止')
    else:
        BUY=True



    '''else:
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
        SOLD_STOCK_VOLUME = volume_total/ SOLD_STOCK_TIMES'''

        
        #<param name="Category">表示委托的种类，0买入 1卖出  2融资买入  3融券卖出   4买券还券   5卖券还款  6现券还券</param>
        #<param name="PriceType">表示报价方式 0上海限价委托 深圳限价委托 1(市价委托)深圳对方最优价格  2(市价委托)深圳本方最优价格  3(市价委托)深圳即时成交剩余撤销  4(市价委托)上海五档即成剩撤 深圳五档即成剩撤 5(市价委托)深圳全额成交或撤销 6(市价委托)上海五档即成转限价
        #<param name="Gddm">股东代码, 交易上海股票填上海的股东代码；交易深圳的股票填入深圳的股东代码</param>
        #上海："E042977471"
        #深圳："0680013816"
        #code: argv[4]
        #price: argv[5]
        #quantity: argv[6]
        #####Category = '0'
        #PriceType ='0' #上海限价委托 深圳限价委托 初期先用涨停价和跌停价进行买卖，保证不出现需要撤单的情况
        #Gddm = "E042977471"
        #code= STOCK_NUM
        #price=float(rd['price'])+BUY_PRICE_GAP#涨停
        #quantity=volume/100   #(int([volume])/100)



# 跌破 0.5% 就出场严格止损
def write_to_file_sold_out(rd, volume, status):
    global STOCK_NUM
    global SOLD_STOCK_TIMES
    global SOLD_STOCK_VOLUME
    global SOLD_PRICE_GAP
    global remainder
    global previous_buy_point
    global previous_sell_point
    global sold_ids


    if (float(rd['volume']) != 0) and (float(rd['volume']) < volume):
        volume = rd['volume']

    #0   1  2
    SHOULD_SOLD=False
    previous_sell_point=rd

    for i in range(0, SOLD_STOCK_TIMES):
        #接上述例子，如果当前为最后一次，真实卖出为原定卖出+余数
        #通常情况下，remainder为0，无影响
        if i==SOLD_STOCK_TIMES-1:
           volume=volume+remainder

        ######
        #平仓
        ######
        sold_price=float(rd['price'])-SOLD_PRICE_GAP
        sold_id=CPlusBridge.SendOrder(1,0,STOCK_NUM,sold_price,volume)
        sold_ids.append(sold_id)

        dt = datetime.now()
        csv_name = dt.strftime('app2sold_' + STOCK_NUM + '_' + '%Y%m%d%H%M%S') + '_0' + str(i) + '_order_strategy.csv'
        dataframe = pd.DataFrame(
            {'外部委托序号': ['1'], '证券代码': [STOCK_NUM], '委托方向卖出': [0], '卖出': [status], 'time': [rd['time']],
             'buy_time': [previous_buy_point['time']],
             'price': [rd['price']],
             '委托数量': [volume],'委托编号':[sold_id]})
        dataframe.to_csv(csv_name, index=False, sep=',', encoding='utf-8')


    SOLD=True
    #实际卖出为i=0:1 i=1:1, i=2:1, i=3:1, i=4:4,共8手
    #计划卖出次数越多，卖出差异可能就越大
    #卖出完成后，重置余数
    remainder=0
        ##Category='1'#卖出
        #PriceType='0' #上海限价委托 深圳限价委托 
        #Gddm="E042977471" #先统一市场
        #code=STOCK_NUM
        #price=float(rd['price'])-SOLD_PRICE_GAP#委托价差
        #quantity=volume/100             #(int([volume])/100)报错
        #t='.\sendorder.exe '+Category+' '+PriceType+' '+Gddm+' '+code+' '+str(price)+' '+str(quantity)
        #os.system(t)


def get_sec(time_str):
    """Get Seconds from time."""
    words = time_str.str.split()
    h, m, s = words.values[0][0].split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)


def get_sec_str(time_str):
    """Get Seconds from time."""
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)




def buy_cancel():
    global SOLD_STOCK_VOLUME
    global buy_ids
    global STOCK_NUM
    global BUY
    global SHOULD_SOLD
    global SOLD_STOCK_TIMES
    global remainder
    global volume_total

    com_total=0
    #撤掉未成单
    for buy_id in buy_ids:
        test=CPlusBridge.Test_Cancel(buy_id)
        #如果可撤
        if test:
            #撤单
            cancel_result=CPlusBridge.CancelOrder(STOCK_NUM,buy_id)

        #查询每单成交
        com=CPlusBridge.Query_Completed(buy_id)/100
        #求和
        com_total=com+com_total

    #写入实际买入
    remain_stock = stockHelper.read_sync_stocks()
    #剩余额度=剩余额度减去实际成交（一定大于，在买入时已经判定了） 向上取整 实际买入2.3，写入3
    #在下单时，已经修改了剩余仓位，如果有未成交，此时需要将未成交加回到remain中
    stockHelper.write_sync_stocks(remain_stock+(volume_total-com_total))

    #如果已买入少于100股（多买，碎股long）
    if com_total<1:
        #算了
        SHOULD_SOLD = False
        BUY = False
        buy_ids=[]
    else:
    #如果已买入多于1手,应卖
        #向下取整，多买的少于1都不算
        com_total=math.floor(com_total)
        #如果有买入,应卖数量为买入总和/应卖次数，当仓位足够时，SOLD_STOCK_VOLUME和默认值一致
        
        #剔除单次买入为小数的情况
        #1.当买入数量小于卖出次数时
        #如：共买入5手，应卖出6次，此时应卖出改为5次，每次卖出1手
        if com_total <= SOLD_STOCK_TIMES:
            SOLD_STOCK_TIMES =com_total
            
            #2.当买入数量大于卖出次数时
        else:
            #如果买入数量不能被整除
            #如计划买入10手，实际买入8手，计划卖出5次，此时余数为3
            #余数为3
            remainder=com_total % SOLD_STOCK_TIMES
            #卖出改为5手
            com_total=com_total-remainder

        #单次卖出为1手，保留余数的3手到最后一次卖出（卖出函数中设置）
        SOLD_STOCK_VOLUME = com_total/ SOLD_STOCK_TIMES

        #防止在确认未成交的时候，已经卖出
        SHOULD_SOLD=True
        BUY = False
        buy_ids=[]

def sold_cancel():
    global sold_ids
    global STOCK_NUM
    global SHOULD_SOLD
    global SOLD

    uncom_total=0
        #撤掉未成单
    for sold_id in sold_ids:
        test=CPlusBridge.Test_Cancel(sold_id)

        if test:
            #撤单
            cancel_result=CPlusBridge.CancelOrder(STOCK_NUM,sold_id)

    for sold_id in sold_ids:
        #查询每单未成交
        uncom=CPlusBridge.Query_unCompleted(sold_id)/100
        #求和
        uncom_total=uncom+uncom_total
    #重新下单出
    #如果未卖出少于1手（碎股long）
    uncom_total=math.floor(uncom_total)
    if uncom_total>=1:
        #如果未卖出多于100股
        #向下取整，例如530股未卖，卖出500，剩30不卖（碎股long）
        #低10个点卖
        sold_id=CPlusBridge.SendOrder('1','0',STOCK_NUM,rd['price']-0.1,uncom_total)

    SOLD = False
    sold_ids=[]

# Core Logic - 策略

def find_gold_buy_point():

    # 全局变量声明
    global SHOULD_SOLD
    global previous_buy_point
    global previous_sell_point
    global SOLD_STOCK_VOLUME
    global BUY_STOCK_VOLUME
    global BUY
    global SOLD
    global buy_ids
    global sold_ids
    global STOCK_NUM

    global PLATFORM_MAX_POINT
    global PLATFORM_MEAN_VOLUME
    global PLATFORM_CAL_MEAN

    global start_point
    global low_point
    global top_point
    global STATUS
    global previous_point
    global down_count
    global up_count
    global stockStatusManager

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
    #买入之后，成交测试
    if BUY:
        #买入后5秒开始测试
        if get_sec(rd['time']) - get_sec(previous_buy_point['time']) > 5:

            buy_cancel()

     #卖出后，成交测试
    if SOLD:
        #卖出后5秒开始测试
        if get_sec(rd['time']) - get_sec(previous_sell_point['time']) > 5:
            
            sold_cancel()




    # 卖出逻辑 ------------------ #
    # ############################

    # real_buy = stockHelper.buy_stock(5)
    # print(real_buy)

    # 涨停盘卖出
    if SHOULD_SOLD:
        if 'open' in rd:
            change_percent = (float(rd['price']) - float(rd['open'])) / float(rd['price']) * 100
            if (change_percent > 9.5) and (change_percent < 10.5):
                write_to_file_sold_out(rd, SOLD_STOCK_VOLUME, 2)
        else:
            print("TODO")

    # 超时停盘卖出
    if SHOULD_SOLD:
        if (get_sec(rd['time']) - get_sec_str("14:57:00")) > 0:
            write_to_file_sold_out(rd, SOLD_STOCK_VOLUME, 5)

    # 买入之后第一个跌势开始卖，涨势和横盘一直持有
    if SHOULD_SOLD:
        if stockStatusManager.state == StockStatus.Down:
            write_to_file_sold_out(rd, SOLD_STOCK_VOLUME, 0)

    # 止损卖出
    if SHOULD_SOLD:
        if previous_buy_point is not None and ((float(previous_buy_point['price']) - float(rd['price'])) > 0):
            gap = ((float(previous_buy_point['price']) - float(rd['price'])) / float(previous_buy_point['price']))
            if gap > 0.005:
                write_to_file_sold_out(rd, SOLD_STOCK_VOLUME, 1)

    if DEBUG and rd is None:
        return

    if start_point is None:
        start_point = rd

    stockStatusManager.add_stock_point(rd)
    logSys.log(stockStatusManager.state)

    # 初始化慢慢上涨，如果下跌则从头取最小的点作为起始点，重新计算上涨逻辑
    # Status == 0 这个逻辑只在初始化上涨有用
    if stockStatusManager.state == StockStatus.Down and STATUS == 0:
        start_point = stockStatusManager.stock_arr_min_point()  # 行情下跌, 重置为start 点

    if rd is None or start_point is None:
        return

    if float(start_point['price']) == 0:
        return

    price_float_gap = (float(rd['price']) - float(start_point['price'])) / float(start_point['price'])
    logSys.log("\n" + "目前价格和Start 点价格涨幅 ---  price: GAP = " + str(price_float_gap))
    if price_float_gap > UP_GAP and STATUS == 0:  # 价格提升到2%以上
        logSys.log(">>>>>>>>> 价格超出增长阈值 >>>>>>>>")
        # 一直上涨超过阈值，进入找 Top 点阶段
        STATUS = 2

    # 进入上涨到 Top 点状态，开始下跌
    if STATUS == 2:
        if get_sec(rd['time']) - get_sec(start_point['time']) < UP_TIME_GAP:
            # 进入下跌状态
            if stockStatusManager.state == StockStatus.Down:
                top_point = stockStatusManager.stock_arr_max_point()

                logSys.log("real down")
                logSys.log(">>>>>>>>>>>>>>>>>>>>> Top Point 上涨区间价格最高点 >>>>>>>>>>>>>>>>")
                logSys.log(top_point)
                logSys.log(">>>>>>>>>>>>>>>>>>>>>")

                # 第一次成交之后继续等待, 高点卖出
                if SHOULD_SOLD:
                    if (float(rd['price']) - float(previous_buy_point['price'])) > 0.5 * (
                            float(top_point['price']) - float(start_point['price'])):
                        if stockStatusManager.state == StockStatus.Up:
                            write_to_file_sold_out(rd, SOLD_STOCK_VOLUME, 3)
                            start_point = previous_buy_point
                            top_point = rd

                # 只有拉伸结束后的首次触发Mean计算，top_point为第一个平台
                PLATFORM_CAL_MEAN = True
                PLATFORM_MEAN_VOLUME = 0
                PLATFORM_MAX_POINT = top_point
                
                # 涨到最高点卖出
                # if SOLDING:
                #     write_to_file_sold_out(rd, SOLD_STOCK_VOLUME, 0)

                STATUS = 1

            if stockStatusManager.state == StockStatus.Up:
                # 上涨还没结束
                STATUS = 2

        else:
            # 涨到最高点卖出,超时卖出
            # if SOLDING:
            #     write_to_file_sold_out(rd, SOLD_STOCK_VOLUME, 0)

            start_point = rd
            STATUS = 0

    if STATUS == 1:
        # 动态找到最高成交价格 平台价格S
        
        global PLATFORM_MAX_VOLUME_A
        global PLATFORM_WAIT_COUNT
        global PLATFORM_Price_Gap
        global PLATFORM_MEAN_VOLUME_MULTIPLE
        global PLATFORM_BIG_MULTIPLE

        if PLATFORM_MAX_POINT is None:
            logSys.log("platform_max_point is none error")
            return

        if top_point is None:
            logSys.log("top_point is none error")
            return

        if start_point is None:
            logSys.log("start_point is none error")
            return

        # PLATFORM_MAX_POINT 平台价格 S
        max_gap = (float(PLATFORM_MAX_POINT['price']) - float(rd['price']))
        top_gap = (float(top_point['price']) - float(start_point['price']))
        if top_gap == 0:
            logSys.log("========== Top Gap is 0 ===============")
            logSys.log("==========Status Reset ===============")
            reset()
            return

        price_gap = max_gap / top_gap
        logSys.log("==========Price Gap ===============")
        logSys.log(price_gap)

        # 价格在平台价波动，并未跌落起始幅度 1/2
        if (float(PLATFORM_MAX_POINT['price']) - float(top_point['price']))/top_gap >0.5:
            logSys.log("平台偏离过大")
            logSys.log("==========Status Reset ===============")
            reset()
            return

        if price_gap > 0.5:
            # Todo: 除非B点在的拉伸幅度超过其实的1/2
            logSys.log("==========Status Reset ===============")
            reset()
            return

        if PLATFORM_CAL_MEAN:
            global platform_point_arr
            platform_point_arr.append(rd)

            # 进入平台期后需要等待 60s 来算平均值，PLATFORM_MEAN_VOLUME
            if get_sec(rd['time']) - get_sec(platform_point_arr[0]['time']) > 60:
                arr_count = (get_sec(rd['time']) - get_sec(platform_point_arr[0]['time'])) / 3
                vol_sum = float(platform_point_arr[-1]['volume']) - float(platform_point_arr[0]['volume'])
                PLATFORM_MEAN_VOLUME = vol_sum / arr_count / 100

                # log info
                logSys.log("==========Mean Volume ===============")
                logSys.log(PLATFORM_MEAN_VOLUME)
                logSys.log("==========Mean Volume ===============")

                logSys.log(platform_point_arr[-1]['time'])
                logSys.log(platform_point_arr[0]['time'])
                logSys.log(float(platform_point_arr[-1]['volume']))
                logSys.log(float(platform_point_arr[0]['volume']))

        if PLATFORM_MEAN_VOLUME > 0:
            current_volume_gap = float(rd['volume']) - float(previous_point['volume'])
            logSys.log("current_volume_gap" + str(current_volume_gap))
            
            # 找到Mean值之后停止再次计算，只算一次
            PLATFORM_CAL_MEAN = False

            if current_volume_gap / 100 > PLATFORM_MEAN_VOLUME_MULTIPLE * PLATFORM_MEAN_VOLUME:
                # wait 5 point 出现同向大成交量 A
                logSys.log("==========A " + str(PLATFORM_MEAN_VOLUME_MULTIPLE) + "倍成交量 ===============" + str(current_volume_gap))
                PLATFORM_MAX_VOLUME_A = True

        # 出现同向大成交量 A 条件满足
        if PLATFORM_MAX_VOLUME_A:
            PLATFORM_WAIT_COUNT = PLATFORM_WAIT_COUNT + 1
            # 等待出现后个，五点法
            if PLATFORM_WAIT_COUNT >= 5:

                if stockStatusManager.state == StockStatus.Up:
                    t_max_point = stockStatusManager.stock_arr_max_point()
                    # 成交价格变动突破平台价的正负 x
                    if float(t_max_point['price']) >= (float(PLATFORM_MAX_POINT['price']) + PLATFORM_Price_Gap):
                        # 同向成交总量大于设定的倍数 x 平台价60s内的成交价均值
                        if stockStatusManager.volume_sum_stock_point() > (PLATFORM_BIG_MULTIPLE * PLATFORM_MEAN_VOLUME):
                            logSys.log("==========成交量总和具体值 " + str(stockStatusManager.volume_sum_stock_point()))
                            logSys.log("==========PLATFORM_BIG_MULTIPLE " + str(PLATFORM_BIG_MULTIPLE))
                            logSys.log("==========PLATFORM_MEAN_VOLUME " + str(PLATFORM_MEAN_VOLUME))
                            
                            # 限制条件: 最小时间约束，进场时间距离拉伸不少于90s
                            # 10s太敏感，配合reset(),进场混乱
                            #70s
                            if get_sec(rd['time']) - get_sec(top_point['time']) > 80:

                                if get_sec(rd['time']) - 9 * 3600 - 32 * 60 < 0:
                                    logSys.log("开盘前 2 分钟不买入")
                                    return

                                if 'open' in rd:
                                    change_percent = (float(rd['price']) - float(rd['open'])) / float(rd['open']) * 100

                                    if (change_percent > 8.5) or (change_percent < -8.5):
                                        logSys.log("涨跌幅超过8.5% 不开仓")
                                        return
                                else:
                                    print("TODO")

                                # 卖出前不再买入
                                if BUY is True:
                                    logSys.log("买入未测试前不再买入")
                                    return
                                    
                                if SHOULD_SOLD is True:
                                    logSys.log("卖出前不再买入")
                                    return  

                                #最大累计交易数量限制

                                write_to_file_buy_in(rd, BUY_STOCK_VOLUME)
                                reset()
                            else:
                                logSys.log("90s内不买入")
                         
                             
        # 平台价最大值动态调整
        if PLATFORM_MAX_POINT is None:
            # PLATFORM_CAL_MEAN = True
            if (previous_point is not None) and (float(rd['price']) > float(previous_point['price'])):
                PLATFORM_MAX_POINT = rd
            else:
                PLATFORM_MAX_POINT = previous_point
        else:
            if float(rd['price']) > float(PLATFORM_MAX_POINT['price']):
                PLATFORM_MAX_POINT = rd
                
                #防止每次出平台就触发计算Mean
                #PLATFORM_CAL_MEAN = True
                #PLATFORM_MEAN_VOLUME = 0
                
                logSys.log("==========Platform Price ===============")
                result = rd[['code', 'name', 'price', 'bid', 'ask', 'volume', 'amount', 'time']]
                logSys.log("最高价格:\n")
                logSys.log(result)
                logSys.log("==========Platform Price ===============")

                platform_point_arr.clear()




    previous_point = rd
    
def reset():
    # Reset
    global PLATFORM_MAX_POINT
    global PLATFORM_MEAN_VOLUME
    global STATUS
    global low_point
    global top_point
    global stockStatusManager
    global start_point
    global PLATFORM_CAL_MEAN
    global platform_point_arr
    global PLATFORM_MAX_VOLUME_A
    global PLATFORM_WAIT_COUNT

    STATUS = 0
    start_point = None
    PLATFORM_MAX_VOLUME_A = False
    low_point = None
    PLATFORM_MAX_POINT = None
    PLATFORM_CAL_MEAN = False


app = wx.App()
ex = AppGUI(None, title='Stock Platform - Apollo')


def main():
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
