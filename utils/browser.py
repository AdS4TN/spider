# -*- coding: utf-8 -*-
"""
浏览器管理模块
负责Selenium WebDriver的初始化和管理
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
from fake_useragent import UserAgent


class BrowserManager:
    """浏览器管理器"""

    def __init__(self, config: dict, logger):
        """
        初始化浏览器管理器

        Args:
            config: 爬虫配置字典
            logger: 日志记录器
        """
        self.config = config
        self.logger = logger
        self.driver = None

    def _build_options(self) -> Options:
        """
        构建Chrome选项

        Returns:
            Chrome选项对象
        """
        options = Options()

        # 随机User-Agent, 限制为桌面浏览器
        ua = UserAgent(browsers=['chrome', 'edge', 'firefox'])
        user_agent = ua.random
        options.add_argument(f'user-agent={user_agent}')

        # 窗口大小
        options.add_argument('--window-size=1920,1080')

        # 禁用自动化提示
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)

        self.logger.info("browser", f"使用User-Agent: {user_agent}")
        return options

    def _apply_stealth(self, driver):
        """
        应用selenium-stealth隐藏自动化特征

        Args:
            driver: WebDriver实例
        """
        stealth(driver,
                languages=["zh-CN", "zh"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True)
        self.logger.info("browser", "已应用selenium-stealth")

    def start(self):
        """
        启动浏览器

        Returns:
            WebDriver实例
        """
        try:
            options = self._build_options()
            self.driver = webdriver.Chrome(options=options)
            self._apply_stealth(self.driver)

            # 设置页面加载超时
            timeout = self.config.get('page_load_timeout', 30)
            self.driver.set_page_load_timeout(timeout)

            self.logger.info("browser", "浏览器启动成功")
            return self.driver

        except Exception as e:
            self.logger.error("browser", f"浏览器启动失败: {str(e)}")
            raise

    def quit(self):
        """关闭浏览器"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("browser", "浏览器已关闭")
            except Exception as e:
                self.logger.error("browser", f"关闭浏览器失败: {str(e)}")
