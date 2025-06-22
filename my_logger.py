#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
"""
@File    : my_logger.py
@Software: PyCharm
"""
import logging
import os
from logging.handlers import RotatingFileHandler

import colorlog


class Logger:
    def __init__(self, log_name: str = __name__, log_file: str = 'logs/app.log'):
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(logging.INFO)

        # 创建日志格式
        self.formatter = colorlog.ColoredFormatter(
            "%(asctime)s - %(log_color)s%(levelname)-8s%(reset)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            }
        )

        # 创建控制台处理器
        self.console_handler = logging.StreamHandler()
        self.console_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.console_handler)

        # 确保日志文件目录存在
        log_dir = os.path.dirname(log_file)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 创建文件处理器 (基于大小滚动)
        self.file_handler = RotatingFileHandler(
            log_file, maxBytes=1000 * 1024 * 1024, backupCount=6, encoding='utf-8', delay=True
        )
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)

    def get_logger(self):
        return self.logger
