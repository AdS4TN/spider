# -*- coding: utf-8 -*-
"""
测试从JavaScript变量中提取商品信息
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
import time
import json

# 配置浏览器
options = Options()
options.add_argument('--window-size=1920,1080')
options.add_experimental_option('excludeSwitches', ['enable-automation'])
options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(options=options)
stealth(driver,
        languages=["zh-CN", "zh"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True)

try:
    # 访问商品页面
    url = "https://item.taobao.com/item.htm?id=860166683529"
    driver.get(url)
    print(f"访问页面: {url}")

    # 等待页面加载
    time.sleep(5)

    # 尝试从JavaScript变量中提取数据
    print("\n尝试提取JavaScript变量...")

    # 方法1：提取 window.__GLOBAL_DATA__
    try:
        global_data = driver.execute_script("return window.__GLOBAL_DATA__;")
        if global_data:
            print(f"\n✅ 找到 window.__GLOBAL_DATA__")
            print(f"数据类型: {type(global_data)}")
            print(f"数据键: {list(global_data.keys()) if isinstance(global_data, dict) else 'Not a dict'}")

            # 保存到文件
            with open("D:/spider/logs/global_data.json", "w", encoding="utf-8") as f:
                json.dump(global_data, f, ensure_ascii=False, indent=2)
            print("已保存到 logs/global_data.json")
    except Exception as e:
        print(f"❌ window.__GLOBAL_DATA__ 不存在: {e}")

    # 方法2：提取 window.g_config
    try:
        g_config = driver.execute_script("return window.g_config;")
        if g_config:
            print(f"\n✅ 找到 window.g_config")
            print(f"数据类型: {type(g_config)}")
            with open("D:/spider/logs/g_config.json", "w", encoding="utf-8") as f:
                json.dump(g_config, f, ensure_ascii=False, indent=2)
            print("已保存到 logs/g_config.json")
    except Exception as e:
        print(f"❌ window.g_config 不存在: {e}")

    # 方法3：列出所有window对象的属性（更全面）
    try:
        window_keys = driver.execute_script("""
            var keys = [];
            for (var key in window) {
                if (typeof window[key] === 'object' && window[key] !== null &&
                    (key.toLowerCase().includes('item') ||
                     key.toLowerCase().includes('product') ||
                     key.toLowerCase().includes('data') ||
                     key.toLowerCase().includes('config'))) {
                    keys.push(key);
                }
            }
            return keys;
        """)
        print(f"\n✅ Window对象中可能包含商品数据的属性:")
        for key in window_keys[:30]:
            print(f"  - {key}")

        # 尝试提取每个可能的对象
        for key in window_keys[:10]:
            try:
                data = driver.execute_script(f"return window.{key};")
                if data and isinstance(data, dict):
                    print(f"\n✅ 成功提取 window.{key}")
                    with open(f"D:/spider/logs/{key}.json", "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    print(f"已保存到 logs/{key}.json")
            except Exception as e:
                print(f"❌ 无法提取 window.{key}: {e}")
    except Exception as e:
        print(f"❌ 无法列出window属性: {e}")

    # 方法4：直接从页面源码中搜索商品标题
    try:
        page_source = driver.page_source
        # 搜索可能包含商品标题的script标签
        import re

        # 搜索包含"title"的JSON数据
        title_patterns = [
            r'"title"\s*:\s*"([^"]+)"',
            r"'title'\s*:\s*'([^']+)'",
            r'title:\s*"([^"]+)"',
        ]

        print(f"\n✅ 从页面源码中搜索标题:")
        for pattern in title_patterns:
            matches = re.findall(pattern, page_source)
            if matches:
                print(f"  找到 {len(matches)} 个匹配:")
                for match in matches[:5]:  # 只显示前5个
                    if len(match) > 10:  # 过滤掉太短的
                        print(f"    - {match[:100]}")
                break
    except Exception as e:
        print(f"❌ 无法搜索页面源码: {e}")

    print("\n测试完成，3秒后自动关闭浏览器...")
    time.sleep(3)

finally:
    driver.quit()
