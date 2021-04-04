# -*- coding: UTF-8 -*-
from strategy.Config import Config
from tools.StockStatusManager import StockStatus
from tools.Utils import Utils
from futubull.futu_api import *


class Breakthrough():
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
                print("一阶段，持续上升 ")
            elif Config.STATUS == 1:
                print("三阶段，再次上升，此时要判断是否买入")
                if self.minimumForStage2 is None:
                    self.minimumForStage2 = Config.stockStatusManager.stock_arr_min_point()

                print("一阶段最大值: " + str(self.maximumForStage1['last_price']))
                print("反弹幅度:" + str(float(rd['last_price'])-float(self.minimumForStage2['last_price'])))
                print("累计下降幅度:" + str(float(self.maximumForStage1['last_price'])-float(self.minimumForStage2['last_price'])))

                if (float(rd['last_price'])-float(self.minimumForStage2['last_price']))/(
                        float(self.maximumForStage1['last_price'])-float(self.minimumForStage2['last_price'])) > 0.3:
                    self.buyin = rd["last_price"] + Config.BUY_PRICE_GAP
                    print("三阶段，已经足够反弹。买入100股，共" + str(100 * self.buyin))
                    print("period: " + str(Utils.get_sec(rd['time']) - Utils.get_sec(self.minimumForStage2['time'])))
                    # if Utils.get_sec(rd['time']) - Utils.get_sec(self.minimumForStage2['time']) < Config.UP_TIME_GAP:
                    print("1 ====> 2")
                    Config.STATUS = 2
                    # FutuApi.place_order("", "", "", "")
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
                print(str(self.maximumForStage3['last_price']) + "-" + str(rd['last_price']))
                drop_percent = \
                    (float(self.maximumForStage3['last_price']) - float(rd['last_price'])) / \
                    float(self.maximumForStage3['last_price'])
                print("drop_percent: " + str(drop_percent))
                if drop_percent*100 > 3 or \
                        (self.buyin > rd['last_price'] and (self.buyin - float(rd['last_price'])) / self.buyin > 0.02):
                    print("卖出, 2 ====> 1")
                    print("==========================================")
                    print(str(rd['last_price'] - Config.SOLD_PRICE_GAP - self.buyin) + " " + str(self.buyin) + "  " + str(rd['last_price']))
                    print("==========================================")
                    # FutuApi.place_order("", "", "", "")
                    Config.STATUS = 1
                    self.maximumForStage1 = self.maximumForStage3
        elif Config.stockStatusManager.state == StockStatus.Stable:
            pass
