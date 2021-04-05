# -*- coding: UTF-8 -*-
from strategy.Config import Config
from tools.StockStatusManager import StockStatus
from tools.Utils import Utils
from futubull.futu_api import *

# 一阶段上升阈值
UP_THRESHOLD_STAGE1 = 0.01
# 二阶段下降幅度（相对一阶段）
DOWN_RATIO_THRESHOLD_STAGE2 = 0.3
# 四阶段下降阈值
DOWN_THRESHOLD_STAGE4 = 0.01
# 止损线，
STOP_LOSS_THRESHOLD = 0.002


class Breakthrough:
    startPoint = 0
    maximumForStage1 = 0
    minimumForStage2 = 0
    maximumForStage3 = 0

    # 买入的价格
    buyin = 0

    def find_gold_buy_point(self, index, rd):
        if Config.start_point is None:
            Config.start_point = rd

        Config.stockStatusManager.add_stock_point(rd)

        if Config.stockStatusManager.state == StockStatus.Up:
            if Config.STATUS == -1:
                print("-1 ====> 0")
                Config.STATUS = 0
                self.startPoint = Config.stockStatusManager.turning_min_price
            elif Config.STATUS == 0:
                print("一阶段，持续上升 ")
            elif Config.STATUS == 1:
                print("三阶段，再次上升，此时要判断是否买入")
                self.minimumForStage2 = Config.stockStatusManager.turning_min_price

                increaseValueStage1 = float(self.maximumForStage1) - float(self.startPoint)
                decreaseValueStage2 = float(self.maximumForStage1) - float(self.minimumForStage2)

                print("一阶段最大值=" + str(self.maximumForStage1) + ", 二阶段最小值=" + str(self.minimumForStage2) +
                      ",startPoint=" + str(self.startPoint))
                print("一阶段增长幅度=" + str(increaseValueStage1))
                print("二阶段下降幅度=" + str(decreaseValueStage2))
                ratio = decreaseValueStage2 / increaseValueStage1
                print("ratio=" + str(decreaseValueStage2 / increaseValueStage1))

                if increaseValueStage1 > 0 and 0.1 < ratio < DOWN_RATIO_THRESHOLD_STAGE2:
                    self.buyin = rd["last_price"] + Config.BUY_PRICE_GAP
                    print("三阶段，已下跌幅度(0~50%)。买入100股，共" + str(100 * self.buyin))
                    # print("period: " + str(Utils.get_sec(rd['time']) - Utils.get_sec(self.minimumForStage2['time'])))
                    # if Utils.get_sec(rd['time']) - Utils.get_sec(self.minimumForStage2['time']) < Config.UP_TIME_GAP:
                    print("1 ====> 2")
                    Config.STATUS = 2
                    # FutuApi.place_order("", "", "", "")
                    return {'direction': 0, 'price': self.buyin - Config.BUY_PRICE_GAP, "index": index}
                elif ratio < 0.1:
                    # 上升途中一次小回调，则认为仍是一阶段上升途中
                    print("下降途中的一次小拉升，仍是二阶段下降中.")
                    pass
                else:
                    print("二阶段下降太多，忽略")
                    self.reset()
                    pass
            elif Config.STATUS == 2:
                print("三阶段，持续上升")
        elif Config.stockStatusManager.state == StockStatus.Down:
            if Config.STATUS == -1:
                pass
            elif Config.STATUS == 0:
                print("二阶段，开始下降, 0 ====> 1")
                self.maximumForStage1 = Config.stockStatusManager.turning_max_price
                print("maximumForStage1=" + str(self.maximumForStage1))
                print("startPoint=" + str(self.startPoint))
                increaseValueStage1 = float(self.maximumForStage1) - float(self.startPoint)
                print("一阶段上涨幅度为: " + str(increaseValueStage1 / float(self.startPoint)))
                if increaseValueStage1 / float(self.startPoint) > 0.01:
                    print("上涨幅度超过1%")
                    Config.STATUS = 1
                else:
                    print("一阶段上升幅度偏低，重新寻找")
                    self.reset()
            elif Config.STATUS == 1:
                print("二阶段，持续下降")
            elif Config.STATUS == 2:
                print("四阶段，再次下降，此时要决定是否卖票")
                self.maximumForStage3 = Config.stockStatusManager.turning_max_price
                print(str(rd['last_price']) + "-" + str(self.maximumForStage3))
                drop_percent = (float(self.maximumForStage3) - float(rd['last_price'])) * 100 / float(self.maximumForStage3)
                stop_loss = (self.buyin - float(rd['last_price'])) / self.buyin

                print("drop_percent=" + str(drop_percent))
                print("stop_loss=" + str(stop_loss))

                if drop_percent > DOWN_THRESHOLD_STAGE4 or stop_loss > STOP_LOSS_THRESHOLD:
                    print("卖出, 2 ====> 1")
                    print("==========================================")
                    print(
                        str(rd['last_price'] - Config.SOLD_PRICE_GAP - self.buyin) + " " + str(self.buyin) + "  " + str(
                            rd['last_price']))
                    print("==========================================")
                    # FutuApi.place_order("", "", "", "")
                    # Config.STATUS = 1
                    # self.maximumForStage1 = self.maximumForStage3
                    self.startPoint = self.minimumForStage2
                    self.maximumForStage1 = self.maximumForStage3
                    self.minimumForStage2 = None
                    self.maximumForStage3 = None

                    print("maximumForStage1=" + str(self.maximumForStage1))
                    print("startPoint=" + str(self.startPoint))
                    _increaseValueStage1 = float(self.maximumForStage1) - float(self.startPoint)
                    print("一阶段上涨幅度为: " + str(_increaseValueStage1 / float(self.startPoint)))
                    if _increaseValueStage1 / float(self.startPoint) > 0.005:
                        print("上涨幅度超过1%")
                        Config.STATUS = 1
                    else:
                        print("一阶段上升幅度偏低，重新寻找")
                        self.reset()
                    return {'direction': 1, 'price': rd['last_price'], "index": index}
        elif Config.stockStatusManager.state == StockStatus.Stable:
            pass

    # 不符合条件，重新寻找
    def reset(self):
        print("reset.")
        Config.STATUS = -1

        self.startPoint = 0
        self.maximumForStage1 = 0
        self.minimumForStage2 = 0
        self.maximumForStage3 = 0
        self.buyin = 0
        pass
