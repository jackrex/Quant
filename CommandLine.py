# -*- coding: UTF-8 -*-
# 命令行版本
from futubull.futu_api import *
from strategy.FTCallbackUp import *

# Items: Index(['code', 'data_date', 'data_time', 'last_price', 'open_price',
#        'high_price', 'low_price', 'prev_close_price', 'volume', 'turnover',
#        'turnover_rate', 'amplitude', 'suspension', 'listing_date',
#        'price_spread', 'dark_status', 'sec_status', 'strike_price',
#        'contract_size', 'open_interest', 'implied_volatility', 'premium',
#        'delta', 'gamma', 'vega', 'theta', 'rho', 'net_open_interest',
#        'expiry_date_distance', 'contract_nominal_value',
#        'owner_lot_multiplier', 'option_area_type', 'contract_multiplier',
#        'last_settle_price', 'position', 'position_change', 'index_option_type',
#        'pre_price', 'pre_high_price', 'pre_low_price', 'pre_volume',
#        'pre_turnover', 'pre_change_val', 'pre_change_rate', 'pre_amplitude',
#        'after_price', 'after_high_price', 'after_low_price', 'after_volume',
#        'after_turnover', 'after_change_val', 'after_change_rate',
#        'after_amplitude']


def main():
    FutuApi.get_account_info()
    FutuApi.position_list()
    FutuApi.get_history_kl_quota()
    FutuApi.request_history_kline()

    # logSys.stock_code = "HK.00700"
    # logSys.add_file_log()
    #
    # quote_ctx = ft.OpenQuoteContext(host='127.0.0.1', port=11111)
    # print('current subscription status :', quote_ctx.query_subscription())  # 查询初始订阅状态
    # handler = StockQuote()
    # quote_ctx.set_handler(handler)  # 设置实时报价回调
    # ret_sub, err_message = quote_ctx.subscribe(['HK.00700'], [ft.SubType.QUOTE])  # 订阅实时报价类型，FutuOpenD开始持续收到服务器的推送
    # if ret_sub == ft.RET_OK:  # 订阅成功
    #     print('subscribe successfully！current subscription status :', quote_ctx.query_subscription())  # 订阅成功后查询订阅状态
    #     # time_interval = Config.TIME_SCHEDULE
    #     # schedule.every(time_interval).seconds.do(InstanceConfig.ftCallbackup.find_gold_buy_point).tag("daily_task")  # 没有后面的括号
    #     ft.time.sleep(600)  # 设置脚本接收FutuOpenD的推送持续时间为600秒
    #     quote_ctx.close()
    # else:
    #     print('subscription failed', err_message)


if __name__ == '__main__':
    main()
