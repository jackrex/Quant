# -*- coding: UTF-8 -*-
# 富图API

from futu import *


class futuApi:
    @staticmethod
    def get_account_info():
        print("get_account_info.")
        pwd_unlock = '419312'
        trd_ctx = OpenHKTradeContext(host='127.0.0.1', port=11111)
        trd_ctx.unlock_trade(pwd_unlock)
        print(trd_ctx.accinfo_query())
        trd_ctx.close()

    @staticmethod
    def place_order(price, qty, code, trd_side):
        pwd_unlock = '419312'
        trd_ctx = OpenHKTradeContext(host='127.0.0.1', port=11111)
        print(trd_ctx.unlock_trade(pwd_unlock))
        print(trd_ctx.place_order(price=price, qty=qty, code=code, trd_side=trd_side, trd_env=TrdEnv.SIMULATE))
        trd_ctx.close()
