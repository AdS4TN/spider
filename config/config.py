# -*- coding: utf-8 -*-
"""
配置管理模块
负责管理数据库配置、爬虫参数配置和日志配置
"""
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent.parent

# 数据库配置
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),  # 从环境变量读取，避免硬编码
    "database": os.getenv("DB_NAME", "taobao_spider"),
    "charset": "utf8mb4"
}

# 爬虫配置
SPIDER_CONFIG = {
    "search_keyword": "肯德基代下单",
    "max_pages": 3,
    "page_delay": [3, 6],  # 页面间延迟范围（秒）
    "sku_delay": [2, 5],   # SKU间延迟范围（秒）
    "page_load_timeout": 30,  # 页面加载超时（秒）
    "retry_times": 3,      # 重试次数
    "retry_delay": 5,      # 重试间隔（秒）
}

# 日志配置
LOG_CONFIG = {
    "log_dir": BASE_DIR / "logs",
    "log_level": "INFO"
}

# Cookie文件路径
COOKIE_FILE = BASE_DIR / "config" / "cookies.txt"

# 数据库SQL文件路径
DATABASE_SQL_FILE = BASE_DIR / "config" / "database.sql"
