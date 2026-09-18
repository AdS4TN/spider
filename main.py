# -*- coding: utf-8 -*-
"""
淘宝肯德基代下单爬虫 - 主程序入口
"""
import sys
from datetime import datetime
from pathlib import Path
from tqdm import tqdm
from dotenv import load_dotenv

# 加载 .env 环境变量（必须在导入 config 之前）
# 使用项目根目录下的 .env 文件
_project_root = Path(__file__).parent
load_dotenv(_project_root / ".env")

# 导入配置
from config.config import DB_CONFIG, SPIDER_CONFIG, LOG_CONFIG, COOKIE_FILE

# 导入工具模块
from utils.logger import Logger
from utils.db_manager import MySQLManager
from utils.browser import BrowserManager
from utils.cookie_manager import CookieManager
from utils.captcha_handler import CaptchaHandler
from utils.throttler import Throttler

# 导入爬虫模块
from crawler.search_page import SearchPageCrawler
from crawler.product_page import ProductPageCrawler


def main():
    """主函数"""
    print("="*60)
    print("淘宝肯德基代下单爬虫")
    print("="*60)

    # 初始化日志
    log_file = LOG_CONFIG['log_dir'] / f"spider_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logger = Logger(log_file, db_manager=None)
    logger.info("main", "爬虫启动")

    # 初始化数据库
    try:
        db_manager = MySQLManager(DB_CONFIG, logger)
        db_manager.connect()
        logger.db_manager = db_manager  # 将数据库管理器注入到日志器
    except Exception as e:
        logger.error("main", f"数据库连接失败，程序退出: {str(e)}")
        sys.exit(1)

    # 初始化浏览器
    try:
        browser_manager = BrowserManager(SPIDER_CONFIG, logger)
        driver = browser_manager.start()
    except Exception as e:
        logger.error("main", f"浏览器启动失败，程序退出: {str(e)}")
        db_manager.close()
        sys.exit(1)

    # 注入Cookie
    try:
        cookie_manager = CookieManager(COOKIE_FILE)
        cookie_manager.inject(driver, "taobao.com")
        logger.info("main", "Cookie注入成功")
    except Exception as e:
        logger.warning("main", f"Cookie注入失败: {str(e)}")

    # 初始化工具组件
    captcha_handler = CaptchaHandler()
    page_throttler = Throttler(SPIDER_CONFIG['page_delay'][0], SPIDER_CONFIG['page_delay'][1])
    sku_throttler = Throttler(SPIDER_CONFIG['sku_delay'][0], SPIDER_CONFIG['sku_delay'][1])

    # 初始化爬虫
    search_crawler = SearchPageCrawler(driver, logger, page_throttler, captcha_handler)
    product_crawler = ProductPageCrawler(driver, db_manager, logger, sku_throttler, captcha_handler)

    try:
        # 打开搜索页面
        keyword = SPIDER_CONFIG['search_keyword']
        max_pages = SPIDER_CONFIG['max_pages']
        search_crawler.open_search(keyword)

        # 收集所有商品链接
        all_links = []
        for page_links in search_crawler.iter_pages(max_pages):
            all_links.extend(page_links)

        logger.info("main", f"共收集到 {len(all_links)} 个商品链接")

        # 遍历商品链接，使用进度条
        for idx, link in enumerate(tqdm(all_links, desc="爬取商品"), 1):
            try:
                logger.info("main", f"[{idx}/{len(all_links)}] 处理商品: {link}")
                product_crawler.process(link)
                page_throttler.sleep()  # 商品间延迟
            except Exception as e:
                logger.error("main", f"商品爬取失败: {str(e)}", link)
                # 询问用户是否继续
                user_input = input("\n商品爬取失败，是否继续？(y/n): ")
                if user_input.lower() != 'y':
                    break

        logger.info("main", "爬取任务完成")

    except KeyboardInterrupt:
        logger.warning("main", "用户中断程序")
    except Exception as e:
        logger.error("main", f"程序异常: {str(e)}")
    finally:
        # 清理资源
        logger.info("main", "正在清理资源...")
        browser_manager.quit()
        db_manager.close()
        logger.info("main", "爬虫结束")
        print("\n" + "="*60)
        print("爬虫已结束")
        print("="*60)


if __name__ == "__main__":
    main()
