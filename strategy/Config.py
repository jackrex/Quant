################# GLOBE CONFIG
from tools.StockStatusManager import StockStatusManager
from tools.DataFrameCSVManager import DataFrameCSVManager

class Config:

    SHOULD_SOLD = False
    BUY = False
    SOLD = False

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
    remainder = 0
    top_point = None
    low_point = None
    previous_buy_point = None
    previous_sell_point = None
    stockStatusManager = StockStatusManager()
    stockHelper = None
    csvManager = DataFrameCSVManager()

    ##########################

    D_FLAG = False
    DEBUG = False





