# -*- coding: UTF-8 -*-
from strategy.Config import Config
from tools.StockStatusManager import StockStatus
from tools.Utils import Utils
from futubull.futu_api import *


class Breakthrough:
    maximumForStage1 = None
    minimumForStage2 = None
    maximumForStage3 = None

    # 买入的价格
    buyin = 0

    def find_gold_buy_point(self, rd):
        if Config.start_point is None:
            Config.start_point = rd

        Config.stockStatusManager.add_stock_point(rd)

        if Config.stockStatusManager.state == StockStatus.Up:
            if Config.STATUS == -1:
                print("-1 ====> 0")
                Config.STATUS = 0
            elif Config.STATUS == 0:
                print("一阶段，持续上升")
            elif Config.STATUS == 1:
                print("三阶段，再次上升，此时要判断是否买入")
                if self.minimumForStage2 is None:
                    self.minimumForStage2 = Config.stockStatusManager.stock_arr_min_point()
                if (float(rd['last_price'])-float(self.minimumForStage2['last_price']))/(
                        float(self.maximumForStage1['last_price'])-float(self.minimumForStage2['last_price'])) > 0.3:
                    print("三阶段，已经足够反弹")
                    if Utils.get_sec(rd['time']) - Utils.get_sec(Config.top_point['time']) < Config.UP_TIME_GAP:
                        print("1 ====> 2")
                        Config.STATUS = 2
                        FutuApi.place_order("", "", "", "")
                        self.buyin = rd["last_price"] + Config.BUY_PRICE_GAP
            elif Config.STATUS == 2:
                print("三阶段，持续上升")

        elif Config.stockStatusManager.state == StockStatus.Down:
            if Config.STATUS == -1:
                Config.STATUS = 0
            elif Config.STATUS == 0:
                print("二阶段，开始下降, 0 ====> 1")
                self.maximumForStage1 = Config.stockStatusManager.stock_arr_max_point()
                Config.STATUS = 1
            elif Config.STATUS == 1:
                print("二阶段，持续下降")
            elif Config.STATUS == 2:
                print("四阶段，再次下降，此时要决定是否卖票")
                self.maximumForStage3 = Config.stockStatusManager.stock_arr_max_point()
                drop_percent = \
                    (float(rd['last_price']) - float(self.maximumForStage3['last_price'])) / \
                    float(self.maximumForStage3['last_price']) * 100
                print("drop_percent: " + drop_percent)
                if drop_percent > 2 or \
                        (self.buyin > rd['last_price'] and (self.buyin - float(rd['last_price'])) / self.buyin > 0.02):
                    print("卖出, 2 ====> 1")
                    FutuApi.place_order("", "", "", "")
                    Config.STATUS = 1
                    self.maximumForStage1 = self.maximumForStage3
        elif Config.stockStatusManager.state == StockStatus.Stable:
            pass
