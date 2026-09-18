# -*- coding: utf-8 -*-
"""
Cookie管理模块
负责加载和注入Cookie
"""
from pathlib import Path
from typing import List, Dict


class CookieManager:
    """Cookie管理器"""

    def __init__(self, cookie_file: Path):
        """
        初始化Cookie管理器

        Args:
            cookie_file: Cookie文件路径
        """
        self.cookie_file = cookie_file

    def load(self) -> List[Dict]:
        """
        从文件加载Cookie字符串并解析

        Returns:
            Cookie字典列表
        """
        if not self.cookie_file.exists():
            raise FileNotFoundError(f"Cookie文件不存在: {self.cookie_file}")

        with open(self.cookie_file, 'r', encoding='utf-8') as f:
            cookie_str = f.read().strip()

        # 跳过注释行
        lines = [line.strip() for line in cookie_str.split('\n') if line.strip() and not line.startswith('#')]
        if not lines:
            raise ValueError("Cookie文件为空或只包含注释")

        cookie_str = lines[0]
        return self.parse_cookie_string(cookie_str)

    def parse_cookie_string(self, cookie_str: str) -> List[Dict]:
        """
        解析Cookie字符串为字典列表

        Args:
            cookie_str: Cookie字符串（格式：key1=value1; key2=value2）

        Returns:
            Cookie字典列表
        """
        cookies = []
        for item in cookie_str.split(';'):
            item = item.strip()
            if '=' in item:
                key, value = item.split('=', 1)
                cookies.append({
                    'name': key.strip(),
                    'value': value.strip()
                })
        return cookies

    def inject(self, driver, domain: str):
        """
        将Cookie注入到浏览器

        Args:
            driver: Selenium WebDriver实例
            domain: Cookie的域名
        """
        cookies = self.load()

        # 先访问目标域名，否则无法添加Cookie
        driver.get(f"https://{domain}")

        # 清除现有Cookie
        driver.delete_all_cookies()

        # 添加Cookie
        for cookie in cookies:
            cookie['domain'] = domain
            try:
                driver.add_cookie(cookie)
            except Exception as e:
                # 某些Cookie可能添加失败，忽略
                pass

        # 刷新页面使Cookie生效
        driver.refresh()
