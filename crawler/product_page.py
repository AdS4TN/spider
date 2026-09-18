# -*- coding: utf-8 -*-
"""
商品详情页爬虫模块
负责爬取商品详情页的SKU信息
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from decimal import Decimal
from urllib.parse import urlparse, parse_qs, urlencode
import re
import time


class ProductPageCrawler:
    """商品详情页爬虫"""

    def __init__(self, driver, db_manager, logger, throttler, captcha_handler):
        """
        初始化商品详情页爬虫

        Args:
            driver: Selenium WebDriver实例
            db_manager: 数据库管理器
            logger: 日志记录器
            throttler: 节流控制器
            captcha_handler: 验证码处理器
        """
        self.driver = driver
        self.db_manager = db_manager
        self.logger = logger
        self.throttler = throttler
        self.captcha_handler = captcha_handler

    def _extract_product_id(self, url: str) -> str:
        """
        从URL中提取商品ID

        Args:
            url: 商品URL

        Returns:
            商品ID
        """
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        return params.get('id', [''])[0]

    def _extract_product_meta(self):
        """
        提取商品基本信息

        Returns:
            (product_id, title, product_url)
        """
        try:
            # 提取商品ID
            product_id = self._extract_product_id(self.driver.current_url)
            title = None

            # 统一等待页面核心内容加载完成
            try:
                self.logger.info("product_page", "等待SKU面板加载...")
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#SkuPanel_tbpcDetail_ssr2025"))
                )
                self.logger.info("product_page", "SKU面板加载完成。")
            except Exception as wait_e:
                self.logger.warning("product_page", f"等待SKU面板超时: {str(wait_e)}，将继续尝试提取。")

            # 方案1：尝试从页面内嵌JSON数据提取标题
            try:
                global_data = self.driver.execute_script("""
                    return window.__GLOBAL_DATA__ || window.g_config || null;
                """)
                if global_data and isinstance(global_data, dict):
                    title = (global_data.get('item', {}).get('title') or
                             global_data.get('data', {}).get('item', {}).get('title') or
                             global_data.get('trade', {}).get('item', {}).get('title'))
                    if title:
                        self.logger.info("product_page", "从JSON数据提取标题成功")
            except Exception as json_e:
                self.logger.warning("product_page", f"从JSON提取标题失败: {str(json_e)}")

            # 方案2：兜底CSS选择器（新版淘宝）
            if not title:
                self.logger.info("product_page", "JSON提取失败，尝试使用CSS选择器...")
                selectors = [
                    "#SkuPanel_tbpcDetail_ssr2025 span[class^='mainTitle--']",  # 2025新版淘宝 - SKU面板标题（最可靠）
                    "span[class^='mainTitle--']",  # 2025新版淘宝 - 前缀匹配
                    "div[class*='ItemTitle--'] span[class^='mainTitle--']",  # 2025新版淘宝备选
                    "h1[data-spm='1000983']",  # 旧版淘宝
                    "[class*='ItemHeader--title']",  # React组件
                    ".ItemTitle--mainTitle",  # 另一种可能的类名
                    "h1.tb-main-title",  # 旧版兜底
                ]

                for selector in selectors:
                    try:
                        title_element = WebDriverWait(self.driver, 2).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        title = title_element.text.strip()
                        if title:
                            self.logger.info("product_page", f"使用选择器 '{selector}' 提取标题成功")
                            break
                    except:
                        continue
            
            # 方案3：最终兜底，从<title>标签获取
            if not title:
                try:
                    self.logger.warning("product_page", "所有选择器均失败，启用<title>标签作为最终兜底方案。")
                    title_raw = self.driver.title
                    if title_raw:
                        title = title_raw.replace('-淘宝网', '').replace('-tmall.com天猫', '').strip()
                except Exception as title_e:
                    self.logger.error("product_page", f"获取 driver.title 失败: {str(title_e)}")


            if not title:
                raise ValueError("所有方案均失败，无法提取商品标题")

            product_url = self.driver.current_url

            return product_id, title, product_url

        except Exception as e:
            self.logger.error("product_page", f"提取商品信息失败: {str(e)}")

            # 保存调试信息
            try:
                screenshot_path = "logs/product_page_error.png"
                source_path = "logs/product_page_error.html"
                self.driver.save_screenshot(screenshot_path)
                with open(source_path, "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                self.logger.info("product_page", f"错误截图已保存至: {screenshot_path}")
                self.logger.info("product_page", f"错误页面源码已保存至: {source_path}")
            except Exception as save_e:
                self.logger.error("product_page", f"保存调试信息失败: {str(save_e)}")

            raise

    def _simplify_url(self, url: str, sku_id: str = None) -> str:
        """
        生成简化的URL（只保留id和skuId参数）

        Args:
            url: 原始URL
            sku_id: SKU ID（可选）

        Returns:
            简化的URL
        """
        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        # 只保留id和skuId参数
        new_params = {}
        if 'id' in params:
            new_params['id'] = params['id'][0]
        if sku_id:
            new_params['skuId'] = sku_id
        elif 'skuId' in params:
            new_params['skuId'] = params['skuId'][0]

        query_string = urlencode(new_params)
        return f"https://item.taobao.com/item.htm?{query_string}"

    def _is_sku_selected(self, sku_element) -> bool:
        """
        检查SKU元素是否处于选中状态

        Args:
            sku_element: SKU元素对象

        Returns:
            True表示已选中，False表示未选中
        """
        try:
            class_attr = sku_element.get_attribute("class") or ""
            # 淘宝常见的选中状态class
            selected_classes = ["selected", "active", "tb-selected", "checked"]
            return any(cls in class_attr.lower() for cls in selected_classes)
        except:
            return False

    def _is_sku_disabled(self, sku_element) -> bool:
        """
        检查SKU元素是否处于禁用状态

        Args:
            sku_element: SKU元素对象

        Returns:
            True表示已禁用，False表示可用
        """
        try:
            class_attr = sku_element.get_attribute("class") or ""
            aria_disabled = sku_element.get_attribute("aria-disabled") or ""
            # 淘宝常见的禁用状态class
            disabled_classes = ["disabled", "tb-disabled", "unavailable"]
            return any(cls in class_attr.lower() for cls in disabled_classes) or aria_disabled.lower() == "true"
        except:
            return False

    def _extract_sku_containers(self):
        """
        识别并提取所有SKU容器及其选项

        Returns:
            list: 容器列表，每个容器包含 {'name': 容器名称, 'options': [选项元素列表]}
                  如果没有找到容器结构，返回空列表
        """
        try:
            # 尝试多种容器选择器
            container_selectors = [
                "div[data-property]:not([aria-hidden='true'])",  # 2025新版淘宝
                "div[data-propertyname]:not([aria-hidden='true'])",  # 2025新版淘宝备选
                "dl.tb-prop",  # 旧版淘宝
                "div.sku-property",  # 通用SKU容器
                "[class*='skuBlock']",  # 另一种可能
            ]

            containers = []
            for selector in container_selectors:
                container_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if container_elements:
                    self.logger.info("product_page", f"使用选择器 {selector} 找到 {len(container_elements)} 个SKU容器")

                    for idx, container in enumerate(container_elements, 1):
                        # 提取容器名称
                        container_name = self._extract_container_name(container)

                        # 提取容器内的选项
                        options = self._extract_container_options(container)

                        if options:
                            containers.append({
                                'name': container_name or f"规格{idx}",
                                'element': container,
                                'options': options
                            })
                            self.logger.debug("product_page", f"  容器[{idx}] '{container_name}': {len(options)} 个选项")

                    if containers:
                        break

            return containers

        except Exception as e:
            self.logger.error("product_page", f"提取SKU容器失败: {str(e)}")
            return []

    def _extract_container_name(self, container_element) -> str:
        """
        从容器元素中提取容器名称

        Args:
            container_element: 容器元素对象

        Returns:
            容器名称字符串
        """
        try:
            # 尝试多种方式提取容器名称
            name_selectors = [
                "[class*='propertyName']",  # 2025新版淘宝
                ".tb-property-name",  # 旧版淘宝
                "dt",  # dl/dt/dd 结构
                "label",  # label 标签
                "[class*='title']",  # 通用标题
            ]

            for selector in name_selectors:
                try:
                    name_element = container_element.find_element(By.CSS_SELECTOR, selector)
                    name = name_element.text.strip()
                    if name:
                        return name
                except:
                    continue

            # 兜底：尝试从 aria-label 或 data-propertyname 属性获取
            aria_label = container_element.get_attribute("aria-label")
            if aria_label:
                return aria_label.strip()

            data_property = container_element.get_attribute("data-propertyname")
            if data_property:
                return data_property.strip()

            return ""

        except Exception as e:
            self.logger.debug("product_page", f"提取容器名称失败: {str(e)}")
            return ""

    def _extract_container_options(self, container_element):
        """
        从容器元素中提取所有选项元素

        Args:
            container_element: 容器元素对象

        Returns:
            选项元素列表
        """
        try:
            # 尝试多种选项选择器
            option_selectors = [
                "div[data-vid]:not([aria-hidden='true'])",  # 2025新版淘宝
                "[role='option']",  # ARIA 角色
                "li[data-value]",  # 旧版淘宝
                "[class*='valueItem']",  # 通用选项
            ]

            for selector in option_selectors:
                options = container_element.find_elements(By.CSS_SELECTOR, selector)
                if options:
                    # 过滤隐藏元素
                    visible_options = [opt for opt in options if opt.is_displayed()]
                    if visible_options:
                        return visible_options

            return []

        except Exception as e:
            self.logger.debug("product_page", f"提取容器选项失败: {str(e)}")
            return []

    def _get_price_element(self, selectors: list):
        """
        获取价格元素对象（用于检测DOM变化）

        Args:
            selectors: 价格选择器列表

        Returns:
            价格元素对象，找不到则返回None
        """
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if element.is_displayed():
                    return element
            except:
                continue
        return None

    def _get_current_price_text(self, selectors: list) -> str or None:
        """
        安全地获取当前价格元素的文本，找不到则返回None
        """
        for selector in selectors:
            try:
                price_element = self.driver.find_element(By.CSS_SELECTOR, selector)

                # 方法1：尝试从data-price属性获取
                data_price = price_element.get_attribute("data-price")
                if data_price and data_price.strip():
                    return data_price.strip()

                # 方法2：尝试从.text获取
                text = price_element.text.strip()
                if text:
                    return text

                # 方法3：尝试从innerText获取（包括子元素）
                inner_text = self.driver.execute_script("return arguments[0].innerText;", price_element)
                if inner_text and inner_text.strip():
                    return inner_text.strip()

            except:
                continue
        return None

    def _wait_and_extract_price(self, old_price_element=None, old_price_text: str or None = None, timeout: int = 5) -> Decimal:
        """
        等待价格更新并提取新价格（使用DOM元素陈旧检测）

        Args:
            old_price_element: 点击前的价格元素对象（用于检测DOM变化）
            old_price_text: 点击前记录的旧价格文本（兜底方案）
            timeout: 等待超时时间

        Returns:
            价格（Decimal类型）

        Raises:
            TimeoutException: 如果价格在指定时间内没有更新
        """
        price_selectors = [
            "[class*='priceWrap']",
            "[class*='Price--priceText']",
            ".Price--priceInt",
            "[class*='priceInt']",
            "span.tb-rmb-num",
        ]

        combined_selector = ", ".join(price_selectors)

        try:
            # 先尝试滚动到价格元素
            try:
                price_element = self.driver.find_element(By.CSS_SELECTOR, combined_selector)
                self.driver.execute_script("arguments[0].scrollIntoView(true);", price_element)
                time.sleep(0.5)
            except:
                pass

            # 方案一：等待DOM元素陈旧（最可靠）
            if old_price_element:
                try:
                    from selenium.webdriver.support import expected_conditions as EC
                    WebDriverWait(self.driver, timeout).until(
                        EC.staleness_of(old_price_element)
                    )
                    self.logger.info("product_page", "检测到价格DOM元素已更新")
                except:
                    # 超时说明DOM未变化，可能价格确实相同，继续提取当前价格
                    self.logger.warning("product_page", "价格DOM未变化，可能SKU价格与默认价格相同")
                    pass
            # 方案二：等待价格文本变化（兜底）
            elif old_price_text:
                try:
                    WebDriverWait(self.driver, timeout).until(
                        lambda driver: self._get_current_price_text(price_selectors) != old_price_text
                    )
                except:
                    self.logger.warning("product_page", "价格文本未变化，可能SKU价格与默认价格相同")
                    pass

            # 价格变化后，再次获取并解析
            price_element = self.driver.find_element(By.CSS_SELECTOR, combined_selector)

            # 使用改进的方法获取价格文本
            new_price_text = self._get_current_price_text(price_selectors)

            if not new_price_text:
                raise ValueError("无法获取价格文本")

            price_match = re.search(r'[\d.]+', new_price_text)

            if not price_match:
                raise ValueError(f"无法从新的价格文本中解析出数字: '{new_price_text}'")

            price = Decimal(price_match.group())
            self.logger.info("product_page", f"价格更新成功: ¥{price}")
            return price

        except Exception as e:
            self.logger.error("product_page", f"等待价格更新或提取新价格失败: {str(e)}")

            # 调试：保存价格元素的HTML结构
            try:
                for selector in price_selectors:
                    try:
                        elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        elem_html = elem.get_attribute('outerHTML')
                        self.logger.debug("product_page", f"选择器 {selector} 的HTML: {elem_html[:300]}")
                        break
                    except:
                        continue
            except:
                pass

            raise

    def _process_sku_combinations(self, containers, product_db_id, url):
        """
        遍历所有SKU组合并提取价格

        Args:
            containers: SKU容器列表
            product_db_id: 商品数据库ID
            url: 商品URL
        """
        from itertools import product as itertools_product
        from utils.db_manager import SkuDTO

        # 提取所有容器的选项列表
        option_groups = [container['options'] for container in containers]

        # 生成所有可能的组合（笛卡尔积）
        all_combinations = list(itertools_product(*option_groups))

        total_combinations = len(all_combinations)
        self.logger.info("product_page", f"共有 {total_combinations} 个SKU组合需要处理")

        # 定义价格选择器
        price_selectors = [
            "[class*='priceWrap']",
            "[class*='Price--priceText']",
            ".Price--priceInt",
            "[class*='priceInt']",
            "span.tb-rmb-num",
        ]

        # 遍历所有组合
        for idx, combination in enumerate(all_combinations, 1):
            try:
                # 构建SKU名称
                sku_name_parts = []
                for container, option in zip(containers, combination):
                    option_text = option.get_attribute("title") or option.text.strip()
                    if option_text:
                        sku_name_parts.append(f"{option_text}")

                sku_name = " + ".join(sku_name_parts)
                self.logger.info("product_page", f"处理组合 [{idx}/{total_combinations}]: {sku_name}")

                # 点击组合中的每个选项
                invalid_combination = False
                for option in combination:
                    # 检查选项是否被禁用
                    if self._is_sku_disabled(option):
                        self.logger.warning("product_page", f"组合包含禁用选项，跳过: {sku_name}")
                        invalid_combination = True
                        break

                    # 点击选项
                    try:
                        self.driver.execute_script("arguments[0].click();", option)
                        time.sleep(0.2)  # 短暂等待点击生效
                    except Exception as e:
                        self.logger.warning("product_page", f"点击选项失败: {str(e)}")
                        invalid_combination = True
                        break

                if invalid_combination:
                    continue

                # 等待价格更新并提取
                try:
                    old_price_element = self._get_price_element(price_selectors)
                    old_price_text = self._get_current_price_text(price_selectors)

                    price = self._wait_and_extract_price(
                        old_price_element=old_price_element,
                        old_price_text=old_price_text,
                        timeout=5
                    )

                    # 价格为0时跳过
                    if price <= Decimal('0.00'):
                        self.logger.warning("product_page", f"SKU价格为0或无效，跳过: {sku_name}")
                        continue

                    # 生成SKU URL
                    sku_url = self._simplify_url(url)

                    # 插入SKU信息
                    sku = SkuDTO(
                        product_db_id=product_db_id,
                        sku_name=sku_name,
                        price=price,
                        sku_url=sku_url
                    )
                    sku_id = self.db_manager.insert_sku(sku)
                    self.db_manager.insert_price_history(sku_id, price)

                    self.logger.info("product_page", f"SKU保存成功: {sku_name} - ¥{price}")

                except Exception as e:
                    self.logger.error("product_page", f"提取价格失败: {str(e)}")
                    continue

                # 节流延迟
                self.throttler.sleep()

            except Exception as e:
                self.logger.error("product_page", f"处理组合失败: {str(e)}")
                continue

    def process(self, url: str):
        """
        处理单个商品页面

        Args:
            url: 商品URL
        """
        try:
            # 访问商品页面
            self.driver.get(url)
            self.logger.info("product_page", f"访问商品页面: {url}")

            # 显式等待，确保页面已跳转到详情页
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.url_contains("item.htm")
                )
            except Exception as e:
                self.logger.error("product_page", "等待商品详情页URL超时", url)
                raise

            # 等待React渲染完成（等待页面主容器加载）
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.ID, "ice-container"))
                )
                self.logger.info("product_page", "页面React容器加载完成")
            except Exception as e:
                self.logger.warning("product_page", f"等待React容器超时: {str(e)}")

            # 检测验证码
            if self.captcha_handler.detect_slider(self.driver):
                self.logger.warning("product_page", "检测到验证码", url)
                self.captcha_handler.wait_for_manual()

            # 提取商品基本信息
            product_id, title, product_url = self._extract_product_meta()
            self.logger.info("product_page", f"商品: {title} (ID: {product_id})")

            # 导入DTO类
            from utils.db_manager import ProductDTO, SkuDTO

            # 插入商品信息
            product = ProductDTO(product_id=product_id, title=title, product_url=product_url)
            product_db_id = self.db_manager.upsert_product(product)

            # 尝试识别多SKU容器结构
            try:
                # 首先尝试提取SKU容器
                containers = self._extract_sku_containers()

                if containers:
                    # 找到多个SKU容器，使用组合遍历逻辑
                    self.logger.info("product_page", f"检测到 {len(containers)} 个SKU容器，使用组合遍历模式")
                    self._process_sku_combinations(containers, product_db_id, url)
                    return

                # 如果没有找到容器结构，回退到单一SKU列表模式
                self.logger.info("product_page", "未检测到SKU容器结构，使用单一列表模式")

                sku_selectors = [
                    "div[data-vid]:not([aria-hidden='true'])",  # 2025新版淘宝
                    "[role='option'][class*='valueItem']",  # 2025新版淘宝
                    "[class*='valueItem'][data-vid]",  # 2025新版淘宝
                    ".tb-sku li[data-value]",  # 旧版淘宝
                    "[class*='sku'] li[data-value]",  # 通配符匹配
                    "li[data-sku-id]",  # 另一种可能
                ]

                sku_elements = []
                for selector in sku_selectors:
                    sku_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if sku_elements:
                        self.logger.info("product_page", f"使用选择器 {selector} 找到 {len(sku_elements)} 个SKU")
                        for i, elem in enumerate(sku_elements[:3], 1):
                            sample_text = elem.text.strip()[:50]
                            self.logger.debug("product_page", f"  SKU样本[{i}]: {sample_text}")
                        break

                # SKU去重
                if sku_elements:
                    from collections import OrderedDict
                    unique_skus = OrderedDict()

                    for elem in sku_elements:
                        vid = elem.get_attribute("data-vid") or elem.get_attribute("data-value")
                        if not vid:
                            vid = elem.text.strip()
                        if vid and vid not in unique_skus:
                            unique_skus[vid] = elem

                    original_count = len(sku_elements)
                    sku_elements = list(unique_skus.values())

                    if original_count != len(sku_elements):
                        self.logger.info("product_page", f"SKU去重: {original_count} -> {len(sku_elements)}")

                # 定义价格选择器
                price_selectors = [
                    "[class*='priceWrap']",
                    "[class*='Price--priceText']",
                    ".Price--priceInt",
                    "[class*='priceInt']",
                    "span.tb-rmb-num",
                ]

                if not sku_elements:
                    self.logger.warning("product_page", "未找到SKU选项，使用默认价格", url)
                    # 没有SKU，尝试直接提取价格
                    try:
                        price = self._wait_and_extract_price(old_price_element=None, old_price_text=None)
                        sku = SkuDTO(
                            product_db_id=product_db_id,
                            sku_name="默认",
                            price=price,
                            sku_url=self._simplify_url(url)
                        )
                        sku_id = self.db_manager.insert_sku(sku)
                        self.db_manager.insert_price_history(sku_id, price)
                    except Exception as e:
                        self.logger.error("product_page", f"无SKU时提取默认价格失败: {e}")
                    return

                # 遍历SKU选项
                self.logger.info("product_page", f"找到 {len(sku_elements)} 个SKU选项")
                for idx, sku_element in enumerate(sku_elements, 1):
                    try:
                        # 获取SKU名称
                        sku_name = sku_element.get_attribute("title") or sku_element.text.strip()
                        if not sku_name:
                            self.logger.warning("product_page", "SKU名称为空，跳过")
                            continue
                            
                        self.logger.info("product_page", f"处理SKU [{idx}/{len(sku_elements)}]: {sku_name}")

                        # 点击前获取价格元素对象（用于DOM陈旧检测）
                        old_price_element = self._get_price_element(price_selectors)
                        old_price_text = self._get_current_price_text(price_selectors)

                        # 点击SKU
                        self.driver.execute_script("arguments[0].click();", sku_element)
                        time.sleep(0.3)  # 短暂等待点击生效

                        # 等待价格更新并提取（使用DOM陈旧检测）
                        price = self._wait_and_extract_price(
                            old_price_element=old_price_element,
                            old_price_text=old_price_text,
                            timeout=8
                        )

                        # 价格为0时跳过
                        if price <= Decimal('0.00'):
                            self.logger.warning("product_page", f"SKU价格为0或无效，跳过: {sku_name}")
                            continue

                        # 生成SKU URL
                        sku_url = self._simplify_url(url)

                        # 插入SKU信息
                        sku = SkuDTO(
                            product_db_id=product_db_id,
                            sku_name=sku_name,
                            price=price,
                            sku_url=sku_url
                        )
                        sku_id = self.db_manager.insert_sku(sku)
                        self.db_manager.insert_price_history(sku_id, price)

                        self.logger.info("product_page", f"SKU保存成功: {sku_name} - ¥{price}")

                        # 节流延迟
                        self.throttler.sleep()

                    except Exception as e:
                        self.logger.error("product_page", f"处理SKU '{sku_name}' 失败: {str(e)}", url)
                        continue

            except Exception as e:
                self.logger.error("product_page", f"提取SKU信息失败: {str(e)}", url)

        except Exception as e:
            self.logger.error("product_page", f"处理商品页面失败: {str(e)}", url)
            raise
