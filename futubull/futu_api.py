# -*- coding: UTF-8 -*-
# 富图API

from futu import *


class SingletonMeta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class FutuApi(metaclass=SingletonMeta):
    def __init__(self):
        self.pwd_unlock = "419312"
        self.trd_ctx = OpenHKTradeContext(host='127.0.0.1', port=11111)

    def unlock_trade(self):
        self.trd_ctx.unlock_trade(self.pwd_unlock)

    @staticmethod
    def get_account_info():
        FutuApi().unlock_trade()
        print(FutuApi().trd_ctx.accinfo_query())
        # FutuApi().trd_ctx.close()

    @staticmethod
    def place_order(price, qty, code, trd_side):
        pwd_unlock = '419312'
        trd_ctx = OpenHKTradeContext(host='127.0.0.1', port=11111)
        print(trd_ctx.unlock_trade(pwd_unlock))
        print(trd_ctx.place_order(price=price, qty=qty, code=code, trd_side=trd_side, trd_env=TrdEnv.SIMULATE))
        # trd_ctx.close()

    @staticmethod
    def position_list():
        print(FutuApi().trd_ctx.position_list_query())
        # FutuApi().trd_ctx.close()

    @staticmethod
    def get_history_kl_quota():
        FutuApi().quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
        ret, data = FutuApi().quote_ctx.get_history_kl_quota(get_detail=True)  # 设置 true 代表需要返回详细的拉取历史 K 线的记录
        if ret == RET_OK:
            print(data)
        else:
            print('error:', data)
        FutuApi().quote_ctx.close()  # 结束后记得关闭当条连接，防止连接条数用尽