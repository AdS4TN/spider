# -*- coding: utf-8 -*-
"""
验证码处理模块
负责检测验证码并协调人工处理
"""
from selenium.webdriver.common.by import By


class CaptchaHandler:
    """验证码处理器"""

    def detect_slider(self, driver) -> bool:
        """
        检测是否出现滑块验证码

        Args:
            driver: Selenium WebDriver实例

        Returns:
            是否检测到验证码
        """
        try:
            # 检测淘宝常见的滑块验证码元素
            captcha_selectors = [
                "#nc_1_n1z",  # 淘宝滑块验证码
                "iframe[src*='geetest']",  # 极验验证码
                ".nc-container",  # 滑块容器
            ]

            for selector in captcha_selectors:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements and elements[0].is_displayed():
                    return True

            return False

        except Exception:
            return False

    def wait_for_manual(self, prompt: str = "检测到验证码，请手动完成验证后按Enter键继续..."):
        """
        等待用户手动解决验证码

        Args:
            prompt: 提示信息
        """
        print(f"\n{'='*60}")
        print(f"⚠️  {prompt}")
        print(f"{'='*60}\n")
        input("按Enter键继续...")
