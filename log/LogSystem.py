#!/usr/bin/python
# -*- coding: UTF-8 -*-
import logging
from enum import Enum
from datetime import datetime
import sys


class LogSystemType(Enum):
    ALL = 0
    Debug = 1


def get_log_formatter():
    return logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")


class LogSystem:

    def __init__(self):
        logging.getLogger().setLevel(logging.DEBUG)
        self.type = LogSystemType.ALL
        self.log_file_name = "log.txt"
        self.fh = None
        self.ch = None
        self.logger = None
        self.stock_code = None
        self.init_logger()
        self.add_console_log()

    def init_logger(self):
        self.logger = logging.getLogger()

    def add_file_log(self):
        logfile = "./doc/" + self.file_name() + self.log_file_name
        self.fh = logging.FileHandler(logfile, mode='a')  # open的打开模式这里可以进行参考
        self.fh.setLevel(logging.DEBUG)
        self.fh.setFormatter(get_log_formatter())
        self.logger.addHandler(self.fh)

    def file_name(self):
        dt = datetime.now()
        file_name = self.stock_code + "_" + dt.strftime('%Y%m%d%H%M%S') + "_"
        return file_name

    def add_console_log(self):
        self.ch = logging.StreamHandler(sys.stdout)
        self.ch.setLevel(logging.DEBUG)
        self.logger.addHandler(self.ch)

    def log(self, message):
        self.logger.debug(message)


logSys = LogSystem()