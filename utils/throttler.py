# -*- coding: utf-8 -*-
"""
节流控制模块
负责随机延迟，模拟人工操作节奏
"""
import time
import random


class Throttler:
    """节流控制器"""

    def __init__(self, min_delay: float, max_delay: float):
        """
        初始化节流控制器

        Args:
            min_delay: 最小延迟时间（秒）
            max_delay: 最大延迟时间（秒）
        """
        self.min_delay = min_delay
        self.max_delay = max_delay

    def sleep(self):
        """执行随机延迟"""
        delay = random.uniform(self.min_delay, self.max_delay)
        time.sleep(delay)
