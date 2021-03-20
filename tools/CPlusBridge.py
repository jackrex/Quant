#!/usr/bin/python
# -*- coding: UTF-8 -*-

import ctypes 
from tools.StockTypeIdentifier import StockType
from tools.StockTypeIdentifier import StockTypeIdentifier

SI = StockTypeIdentifier()


Gddm =b"0135420570"
Sign='0'


class CPlusBridge:

    def __init__(self):
        self.c_name = "./demo_trade.dll"
        self.cpp = ctypes.CDLL(self.c_name)

        #self.cpp.Send_Order.argtypes = ctypes.c_int,ctypes.c_int,ctypes.c_char_p,ctypes.c_char_p,ctypes.c_float,ctypes.c_int
        #self.cpp.Cancel_Order.argtypes = ctypes.c_char_p,ctypes.c_char_p,ctypes.c_char_p,ctypes.c_char_p
        #self.cpp.query_histdata.argtypes = ctypes.c_int,ctypes.c_int,ctypes.c_int
        
        self.cpp.Send_Order.restype = ctypes.c_char_p
        self.cpp.query_data.restype = ctypes.c_char_p
        self.cpp.Cancel_Order.restype = ctypes.c_char_p
        self.cpp.query_histdata.restype = ctypes.c_char_p

    def SendOrder(self,Category, PriceType, Zqdm, Price, Quantity):
        global Gddm

        if SI.stock_type(Zqdm) == StockType.SHENZHEN:
            #深市
            Gddm = b"0135420570"
        elif SI.stock_type(Zqdm) == StockType.SHANGHAI:
            #沪市
            Gddm = b"A226170650"
        Zqdm_Bytes=Zqdm.encode()
        #手到股
        result=self.cpp.Send_Order(Category, PriceType, Gddm, Zqdm_Bytes,ctypes.c_float(Price),Quantity*100).decode("gb2312")
        order_id=result.split('\n')[1].split("\t")[0]
        return order_id

    def Test_Cancel(self,order_id):
        cancel_able=self.cpp.query_data(4).decode("gb2312")
        test='\t'+order_id+'\t'
        if test in cancel_able:
            return True
        else:
            return False

    def CancelOrder(self,Zqdm,order_id):
        global Gddm
        global Sign        

        if Zqdm.startswith("3") or Zqdm.startswith("0"):
            #深市
            Gddm = b"0135420570"
            sign='0'
        elif Zqdm.startswith("6"):
            #沪市
            Gddm = b"A226170650"
            sign='1'
        #转为字节
        Zqdm_Bytes=Zqdm.encode()
        order_id_Bytes=order_id.encode()

        result=self.cpp.Cancel_Order(sign,Gddm,Zqdm_Bytes,order_id_Bytes).decode("gb2312")
        if '\t撤单申报成功'  in result:
            return True
        else:
            return False

    def Query_Completed(self,order_id):
        completed =0
        records=self.cpp.query_data(2).decode("gb2312")
        test='\t'+order_id+'\t'
        lis=records.split('\n')
        for i in range(len(lis)):
            if test in lis[i]:
                l=lis[i]
                completed=l.split('\t')[10]
        completed=int(completed)
        return completed

    def Query_unCompleted(self,order_id):
        uncompleted=0
        records=self.cpp.query_data(2).decode("gb2312")
        test='\t'+order_id+'\t'
        lis=records.split('\n')
        for i in range(len(lis)):
            if test in lis[i]:
                l=lis[i]
                uncompleted=l.split('\t')[12]
        uncompleted=int(uncompleted)
        return uncompleted

