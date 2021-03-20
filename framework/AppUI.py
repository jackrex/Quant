# -*- coding: UTF-8 -*-

import wx
from tools.StockHelper import logSys
from threading import Thread
import schedule
from strategy.Config import Config
import time

from tools.StockHelper import StockHelper
from strategy.InstanceConfig import InstanceConfig

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
        Config.csvManager.stock_code = STOCK_NUM
        Config.csvManager.setUp()
        global stockHelper
        stockHelper = StockHelper(STOCK_NUM)
        self.thread = Thread(target=self.threadMethod)
        self.thread.start()

    def threadMethod(self):
        schedule.clear()
        time_interval = Config.TIME_SCHEDULE
        if Config.DEBUG:
            while True:
                InstanceConfig.callBackUp.find_gold_buy_point()
        schedule.every(time_interval).seconds.do(InstanceConfig.ftCallbackup.find_gold_buy_point).tag("daily_task")  # 没有后面的括号
        while True:
            schedule.run_pending()
            time.sleep(1)
