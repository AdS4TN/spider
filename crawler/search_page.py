# -*- coding: utf-8 -*-
"""
搜索页爬虫模块
负责爬取淘宝搜索结果页
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Iterator, List


class SearchPageCrawler:
    """搜索页爬虫"""

    def __init__(self, driver, logger, throttler, captcha_handler):
        """
        初始化搜索页爬虫

        Args:
            driver: Selenium WebDriver实例
            logger: 日志记录器
            throttler: 节流控制器
            captcha_handler: 验证码处理器
        """
        self.driver = driver
        self.logger = logger
        self.throttler = throttler
        self.captcha_handler = captcha_handler

    def open_search(self, keyword: str):
        """
        打开淘宝搜索页面并输入关键词

        Args:
            keyword: 搜索关键词
        """
        try:
            # 访问淘宝搜索页面
            search_url = f"https://s.taobao.com/search?q={keyword}"
            self.driver.get(search_url)
            self.logger.info("search_page", f"打开搜索页面: {keyword}")

            # 等待页面加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".item"))
            )

            # 检测验证码
            if self.captcha_handler.detect_slider(self.driver):
                self.logger.warning("search_page", "检测到验证码")
                self.captcha_handler.wait_for_manual()

        except Exception as e:
            self.logger.error("search_page", f"打开搜索页面失败: {str(e)}")
            raise

    def get_product_links(self) -> List[str]:
        """
        获取当前页所有商品链接

        Returns:
            商品链接列表
        """
        try:
            # 等待页面加载完成（等待任意商品链接出现）
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'item.taobao.com/item.htm')]"))
            )

            # 提取所有包含item.taobao.com的链接
            links = []
            all_links = self.driver.find_elements(By.TAG_NAME, "a")

            for link in all_links:
                href = link.get_attribute("href")
                if href and "item.taobao.com/item.htm" in href:
                    # 确保使用https
                    if href.startswith("//"):
                        href = "https:" + href
                    # 去重
                    if href not in links:
                        links.append(href)

            self.logger.info("search_page", f"提取到 {len(links)} 个商品链接")
            return links

        except Exception as e:
            self.logger.error("search_page", f"提取商品链接失败: {str(e)}")
            return []

    def go_to_next_page(self) -> bool:
        """
        翻页到下一页

        Returns:
            是否成功翻页
        """
        try:
            # 等待下一页按钮出现并可点击（新版淘宝使用next-next类名）
            next_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".next-next"))
            )

            # 检查按钮是否被禁用
            if "disabled" in next_button.get_attribute("class"):
                self.logger.info("search_page", "已到达最后一页")
                return False

            # 滚动到按钮位置，避免被遮挡
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
            self.throttler.sleep()  # 等待滚动完成

            # 使用JavaScript点击，避免被遮挡
            self.driver.execute_script("arguments[0].click();", next_button)
            self.logger.info("search_page", "翻页成功")

            # 等待新页面加载（等待商品链接出现）
            self.throttler.sleep()
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'item.taobao.com/item.htm')]"))
            )

            return True

        except Exception as e:
            self.logger.error("search_page", f"翻页失败: {str(e)}")

            # 增加调试信息：保存截图和页面源码
            try:
                screenshot_path = "logs/screenshot_on_error.png"
                source_path = "logs/page_source_on_error.html"
                self.driver.save_screenshot(screenshot_path)
                with open(source_path, "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                self.logger.info("search_page", f"错误截图已保存至: {screenshot_path}")
                self.logger.info("search_page", f"错误页面源码已保存至: {source_path}")
            except Exception as save_e:
                self.logger.error("search_page", f"保存调试信息失败: {str(save_e)}")

            return False

    def iter_pages(self, max_pages: int) -> Iterator[List[str]]:
        """
        遍历多页搜索结果

        Args:
            max_pages: 最大页数

        Yields:
            每页的商品链接列表
        """
        for page_num in range(1, max_pages + 1):
            self.logger.info("search_page", f"正在爬取第 {page_num} 页")

            # 获取当前页商品链接
            links = self.get_product_links()
            if links:
                yield links

            # 如果不是最后一页，翻页
            if page_num < max_pages:
                if not self.go_to_next_page():
                    break
