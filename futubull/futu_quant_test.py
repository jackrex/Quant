# -*- coding: UTF-8 -*-
# 回调做多策略
# Futu python: https://github.com/FutunnOpen/py-futu-api
# Futu SDK: https://www.futunn.com/download/OpenAPI

import futu as ft

# 实例化行情上下文对象
quote_ctx = ft.OpenQuoteContext(host="127.0.0.1", port=11111)

# 上下文控制
quote_ctx.start()              # 开启异步数据接收
quote_ctx.set_handler(ft.TickerHandlerBase())  # 设置用于异步处理数据的回调对象(可派生支持自定义)

# US.AAPL, HK.00700, SZ.000001  / US not enough level
print(quote_ctx.get_market_snapshot('US.AAPL'))  # 获取港股 HK.00700 的快照数据
quote_ctx.close() # 关闭对象，防止连接条数用尽


# # 下单
# trd_ctx = ft.OpenHKTradeContext(host='127.0.0.1', port=11111)  # 创建交易对象
# print(trd_ctx.unlock_trade(000000))  # 解锁
# print(trd_ctx.place_order(price=500.0, qty=100, code="HK.00700", trd_side=ft.TrdSide.BUY))  # 下单
# trd_ctx.close()  # 关闭对象，防止连接条数用尽


# ret_sub, err_message = quote_ctx.subscribe(['HK.00700'], [ft.SubType.QUOTE], subscribe_push=False)
# # 先订阅K 线类型。订阅成功后FutuOpenD将持续收到服务器的推送，False代表暂时不需要推送给脚本
# if ret_sub == ft.RET_OK:  # 订阅成功
#     ret, data = quote_ctx.get_stock_quote(['HK.00700'])  # 获取订阅股票报价的实时数据
#     if ret == ft.RET_OK:
#         print(data)
#         print(data['code'][0])   # 取第一条的股票代码
#         print(data['code'].values.tolist())   # 转为list
#     else:
#         print('error:', data)
# else:
#     print('subscription failed', err_message)
# quote_ctx.close()  # 关闭当条连接，FutuOpenD会在1分钟后自动取消相应股票相应类型的订阅


# class StockQuoteTest(ft.StockQuoteHandlerBase):
#     def on_recv_rsp(self, rsp_str):
#         ret_code, data = super(StockQuoteTest,self).on_recv_rsp(rsp_str)
#         if ret_code != ft.RET_OK:
#             print("StockQuoteTest: error, msg: %s" % data)
#             return ft.RET_ERROR, data
#         print("StockQuoteTest ", data) # StockQuoteTest自己的处理逻辑
#         return ft.RET_OK, data
#
# quote_ctx = ft.OpenQuoteContext(host='127.0.0.1', port=11111)
# handler = StockQuoteTest()
# quote_ctx.set_handler(handler)  # 设置实时报价回调
# quote_ctx.subscribe(['HK.00700'], [ft.SubType.QUOTE])  # 订阅实时报价类型，FutuOpenD开始持续收到服务器的推送
# ft.time.sleep(3)  #  设置脚本接收FutuOpenD的推送持续时间为15秒
# quote_ctx.close()   # 关闭当条连接，FutuOpenD会在1分钟后自动取消相应股票相应类型的订阅