# -*- coding: UTF-8 -*-
# 主框架 App

import wx
from framework.AppUI import AppGUI


app = wx.App()
ex = AppGUI(None, title='Stock Platform - Apollo')


def main():
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
