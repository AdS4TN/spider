# -*- coding: utf-8 -*-
"""
日志管理模块
负责控制台、文件和数据库的日志输出
"""
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional


class Logger:
    """日志管理器"""

    def __init__(self, log_file: Path, db_manager=None):
        """
        初始化日志管理器

        Args:
            log_file: 日志文件路径
            db_manager: 数据库管理器（可选）
        """
        self.db_manager = db_manager
        self.logger = logging.getLogger("spider")
        self.logger.setLevel(logging.DEBUG)

        # 确保日志目录存在
        log_file.parent.mkdir(parents=True, exist_ok=True)

        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '[%(asctime)s][%(levelname)s][%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)

        # 文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '[%(asctime)s][%(levelname)s][%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)

        # 添加处理器
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def debug(self, module: str, msg: str):
        """输出DEBUG级别日志"""
        self.logger.debug(f"[{module}] {msg}")

    def info(self, module: str, msg: str):
        """输出INFO级别日志"""
        self.logger.info(f"[{module}] {msg}")

    def warning(self, module: str, msg: str, product_url: Optional[str] = None):
        """输出WARNING级别日志"""
        self.logger.warning(f"[{module}] {msg}")
        # WARNING及以上级别写入数据库
        if self.db_manager:
            try:
                self.db_manager.insert_log("WARNING", f"[{module}] {msg}", product_url)
            except:
                pass

    def error(self, module: str, msg: str, product_url: Optional[str] = None):
        """输出ERROR级别日志"""
        self.logger.error(f"[{module}] {msg}")
        # ERROR级别写入数据库
        if self.db_manager:
            try:
                self.db_manager.insert_log("ERROR", f"[{module}] {msg}", product_url)
            except:
                pass
