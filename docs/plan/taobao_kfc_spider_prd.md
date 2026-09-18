# 淘宝肯德基代下单爬虫 - 产品需求文档 (PRD)

**版本**: 1.0
**日期**: 2026-01-23
**状态**: 草案
**作者**: Claude Code

---

## 1. 执行摘要

### 产品概述

淘宝肯德基代下单爬虫是一个专门用于采集淘宝平台"肯德基代下单"商品信息的自动化数据采集系统。该系统通过Selenium自动化框架模拟真实用户行为,爬取商品的SKU信息和价格数据,并将数据持久化存储到MySQL数据库中,为后续的价格监控和数据分析提供基础。

本项目采用Python开发,运行在Windows环境下,使用显示窗口模式的Chrome浏览器进行数据采集。系统设计了完善的反爬虫对抗策略,包括随机延迟、User-Agent轮换、自动化特征隐藏等机制,以降低被检测和封禁的风险。

### 核心价值主张

- **精准数据采集**: 自动化采集商品SKU级别的详细信息,包括名称、价格、链接等
- **价格监控基础**: 为价格变动监控和趋势分析提供数据支撑
- **反爬虫对抗**: 多层次的反检测机制,提高爬取成功率和稳定性
- **数据持久化**: 结构化存储到MySQL数据库,支持后续查询和分析
- **可扩展架构**: 模块化设计,便于后续功能扩展和维护

### MVP 目标声明

**MVP目标**: 实现一个稳定可靠的Demo版本,能够成功爬取淘宝"肯德基代下单"关键词搜索结果前3页(约144个商品)的所有SKU信息,并将数据准确存储到MySQL数据库中。系统应具备基本的反爬虫能力和异常处理机制,能够在遇到验证码时暂停并等待人工处理。

---

## 2. 使命

### 产品使命声明

**为电商价格监控和数据分析提供可靠的自动化数据采集解决方案,通过智能化的反爬虫策略和稳定的数据采集能力,帮助用户高效获取商品价格信息,支持价格趋势分析和决策优化。**

### 核心原则

1. **稳定性优先**: 采用成熟的Selenium框架,显示窗口模式降低被检测风险,确保爬取过程稳定可靠

2. **合规性第一**: 严格遵守淘宝robots.txt协议和服务条款,控制爬取频率,避免对服务器造成压力,仅用于学习和研究目的

3. **数据准确性**: 确保采集的SKU信息和价格数据准确无误,通过完善的数据验证和日志记录机制保证数据质量

4. **可维护性**: 模块化设计,代码结构清晰,配置与代码分离,便于后续维护和功能扩展

5. **用户友好**: 提供清晰的控制台输出和进度显示,在遇到异常时给出明确的提示和处理建议,降低使用门槛

---

## 3. 目标用户

### 主要用户画像

**用户类型**: 技术开发者 / 数据分析师 / 电商从业者

**典型特征**:
- 具备基本的Python编程知识
- 了解Web爬虫的基本原理
- 需要采集电商平台的商品价格数据
- 有价格监控或数据分析的需求
- 熟悉MySQL数据库的基本操作

### 技术熟练度

**必需技能**:
- Python基础语法和环境配置
- MySQL数据库的安装和基本使用
- 命令行工具的基本操作
- 浏览器开发者工具的使用(获取Cookie)

**可选技能**:
- Selenium自动化测试经验
- Web前端基础知识(HTML/CSS选择器)
- 爬虫反爬虫对抗经验

### 关键用户需求和痛点

**核心需求**:
1. **批量数据采集**: 需要快速采集大量商品的SKU和价格信息
2. **价格监控**: 需要定期更新价格数据,监控价格变动趋势
3. **数据结构化**: 需要将采集的数据结构化存储,便于后续查询和分析
4. **稳定可靠**: 需要爬虫能够稳定运行,不频繁被封禁或触发验证码

**主要痛点**:
1. **反爬虫机制**: 淘宝有严格的反爬虫策略,容易被检测和封禁
2. **验证码干扰**: 频繁触发滑块验证码,影响爬取效率
3. **Cookie管理**: Cookie有效期有限,需要定期更新维护
4. **数据准确性**: SKU价格动态加载,需要准确捕获点击后的价格变化
5. **异常处理**: 页面加载超时、元素定位失败等异常情况需要妥善处理

---

## 4. MVP 范围

### 范围内: 核心功能

#### 数据采集功能
- ✅ 搜索关键词"肯德基代下单",爬取前3页搜索结果
- ✅ 每页采集48个商品(6行 × 8列)
- ✅ 进入商品详情页,提取商品标题和商品ID
- ✅ 依次点击每个SKU选项,提取SKU名称和价格
- ✅ 生成简化的SKU链接(仅保留id和skuId参数)

#### 数据存储功能
- ✅ 连接本地MySQL数据库
- ✅ 存储商品主表信息(products表)
- ✅ 存储SKU信息表(skus表)
- ✅ 记录价格历史(price_history表)
- ✅ 记录爬取日志(crawl_logs表)

#### 反爬虫对抗
- ✅ 随机延迟(2-5秒)模拟人工操作
- ✅ 随机User-Agent轮换
- ✅ 使用selenium-stealth隐藏自动化特征
- ✅ Cookie管理(手动导入Cookie字符串)
- ✅ 显示窗口模式(非无头模式)

#### 异常处理
- ✅ 滑块验证码检测和人工处理流程
- ✅ 页面加载超时重试机制(3次重试)
- ✅ 商品爬取失败暂停处理
- ✅ SKU信息缺失警告和跳过
- ✅ 数据库连接失败检测

#### 日志系统
- ✅ 控制台实时输出
- ✅ 文件日志详细记录
- ✅ 进度条显示(tqdm)
- ✅ 关键日志写入数据库

### 范围外: 未来功能

#### 高级功能
- ❌ 定时任务和自动化调度
- ❌ 增量更新(仅爬取价格变化的SKU)
- ❌ 价格变动通知(邮件/微信)
- ❌ 数据分析和可视化
- ❌ 价格趋势预测

#### 技术优化
- ❌ 代理IP池集成
- ❌ 多线程/多进程并行爬取
- ❌ 断点续爬功能
- ❌ 自动化验证码识别
- ❌ 分布式爬虫架构

#### 集成扩展
- ❌ Web管理界面
- ❌ RESTful API接口
- ❌ 数据导出功能(Excel/CSV)
- ❌ 其他电商平台支持
- ❌ 云端部署支持

#### 部署运维
- ❌ Docker容器化
- ❌ 自动化测试
- ❌ 性能监控和告警
- ❌ 日志分析和可视化

---

## 5. 用户故事

### 主要用户故事

**US-1: 批量采集商品信息**
> 作为一名电商数据分析师,我想要自动采集淘宝"肯德基代下单"关键词下的所有商品信息,以便我能够快速获取市场上的商品数据,而不需要手动逐个查看和记录。

**具体场景**: 用户运行程序后,系统自动访问淘宝搜索页面,输入关键词,遍历前3页搜索结果,采集约144个商品的基本信息,包括商品ID、标题、链接等。

---

**US-2: 获取SKU级别的价格信息**
> 作为一名价格监控人员,我想要获取每个商品所有SKU选项的详细价格,以便我能够了解不同规格商品的价格差异,为价格策略制定提供数据支持。

**具体场景**: 系统进入商品详情页后,自动点击每个SKU选项(如"香辣鸡腿堡套餐"、"黄金鸡块套餐"等),等待价格更新,提取并记录每个SKU的名称和对应价格。

---

**US-3: 数据持久化存储**
> 作为一名数据工程师,我想要将采集的数据结构化存储到MySQL数据库中,以便我能够方便地进行数据查询、分析和后续处理。

**具体场景**: 系统将商品信息存储到products表,SKU信息存储到skus表,价格历史存储到price_history表,并建立表之间的外键关联,确保数据完整性。

---

**US-4: 应对反爬虫机制**
> 作为一名爬虫开发者,我想要系统能够有效应对淘宝的反爬虫机制,以便我能够稳定地采集数据,而不会频繁被封禁或触发验证码。

**具体场景**: 系统使用随机延迟模拟人工操作节奏,使用selenium-stealth隐藏自动化特征,轮换User-Agent,使用显示窗口模式,降低被检测的风险。

---

**US-5: 处理验证码干扰**
> 作为一名系统操作员,我想要在遇到滑块验证码时系统能够暂停并提示我手动处理,以便我能够完成验证后继续爬取,而不会导致整个任务失败。

**具体场景**: 系统检测到滑块验证码时,自动暂停爬取,在控制台输出提示信息,等待用户手动拖动滑块完成验证,用户按Enter键后程序继续执行。

---

**US-6: 监控爬取进度**
> 作为一名系统用户,我想要实时看到爬取进度和状态信息,以便我能够了解任务执行情况,及时发现和处理异常。

**具体场景**: 系统在控制台显示进度条(使用tqdm),实时输出当前正在爬取的商品链接、SKU信息、遇到的错误等,同时将详细日志记录到文件中。

---

**US-7: 异常情况处理**
> 作为一名系统管理员,我想要系统在遇到异常时能够智能处理,以便我能够根据提示采取相应措施,而不会导致数据丢失或程序崩溃。

**具体场景**: 系统在页面加载超时时自动重试3次,在商品爬取失败时暂停并输出失败链接,在数据库连接失败时立即停止并输出详细错误信息。

---

**US-8: Cookie管理**
> 作为一名技术用户,我想要能够方便地管理和更新Cookie,以便我能够维持登录状态,避免因Cookie失效导致爬取失败。

**具体场景**: 用户从浏览器开发者工具复制Cookie字符串,粘贴到config/cookies.txt文件中,程序启动时自动读取并加载Cookie,每次请求时携带Cookie维持登录状态。

---

## 6. 核心架构与模式

### 高层架构方法

本项目采用**分层模块化架构**,将系统划分为配置层、工具层、业务层和数据层,各层职责清晰,低耦合高内聚。

```
┌─────────────────────────────────────────┐
│           主程序入口 (main.py)           │
│         - 初始化系统                     │
│         - 协调各模块                     │
└─────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│ 配置层   │ │ 工具层   │ │ 业务层   │
│ config/  │ │ utils/   │ │ crawler/ │
└──────────┘ └──────────┘ └──────────┘
                    │
                    ▼
            ┌──────────────┐
            │   数据层     │
            │   MySQL DB   │
            └──────────────┘
```

### 目录结构

```
spider/
├── config/                    # 配置模块
│   ├── __init__.py
│   ├── config.py             # 配置管理(数据库、爬虫参数)
│   ├── cookies.txt           # Cookie字符串存储
│   └── database.sql          # 数据库建表SQL脚本
│
├── utils/                     # 工具模块
│   ├── __init__.py
│   ├── browser.py            # Selenium浏览器管理
│   ├── cookie_manager.py     # Cookie加载和管理
│   ├── captcha_handler.py    # 验证码检测和处理
│   ├── proxy_manager.py      # 代理IP管理(预留接口)
│   ├── db_manager.py         # 数据库连接和操作
│   └── logger.py             # 日志系统管理
│
├── crawler/                   # 爬虫核心模块
│   ├── __init__.py
│   ├── search_page.py        # 搜索结果页爬取逻辑
│   └── product_page.py       # 商品详情页爬取逻辑
│
├── logs/                      # 日志文件目录
│   └── spider_YYYYMMDD_HHMMSS.log
│
├── docs/                      # 文档目录
│   └── plan/                 # 计划文档
│
├── main.py                    # 主程序入口
├── requirements.txt           # Python依赖包
├── spec.md                    # 需求规格说明书
└── README.md                  # 使用说明文档
```

### 关键设计模式和原则

#### 1. 单一职责原则 (SRP)
每个模块只负责一个功能领域:
- `browser.py`: 仅负责浏览器的初始化和管理
- `db_manager.py`: 仅负责数据库操作
- `search_page.py`: 仅负责搜索页面的爬取逻辑

#### 2. 配置与代码分离
所有配置参数集中在`config/config.py`中,包括:
- 数据库连接配置
- 爬虫参数(延迟时间、重试次数等)
- 日志配置

#### 3. 依赖注入模式
工具类通过参数传递给业务类,便于测试和替换:
```python
# 示例
crawler = SearchPageCrawler(browser, db_manager, logger)
```

#### 4. 策略模式
反爬虫策略可灵活配置和扩展:
- 随机延迟策略
- User-Agent轮换策略
- 代理IP切换策略(预留)

#### 5. 异常处理链
分层异常处理机制:
- 底层: 捕获并记录异常
- 中层: 重试机制
- 顶层: 用户提示和暂停

### 特定于技术的模式

#### Selenium最佳实践
- **显式等待**: 使用`WebDriverWait`等待元素加载
- **异常捕获**: 捕获`NoSuchElementException`、`TimeoutException`等
- **资源清理**: 使用`try-finally`确保浏览器正确关闭

#### 数据库操作模式
- **连接池**: 复用数据库连接
- **事务管理**: 批量操作使用事务
- **参数化查询**: 防止SQL注入

---

## 7. 工具/功能

### 7.1 浏览器管理工具 (browser.py)

**用途**: 初始化和管理Selenium WebDriver,应用反爬虫策略

**核心功能**:
- 初始化Chrome浏览器(显示窗口模式)
- 应用selenium-stealth隐藏自动化特征
- 设置随机User-Agent
- 配置浏览器选项(禁用图片加载、设置超时等)
- 提供页面导航和元素查找方法

**关键方法**:
```python
class BrowserManager:
    def __init__(self, headless=False):
        """初始化浏览器管理器"""

    def get_driver(self):
        """获取配置好的WebDriver实例"""

    def navigate_to(self, url):
        """导航到指定URL"""

    def find_element_safe(self, by, value, timeout=10):
        """安全查找元素,带超时和异常处理"""

    def close(self):
        """关闭浏览器并清理资源"""
```

### 7.2 Cookie管理工具 (cookie_manager.py)

**用途**: 加载和管理Cookie,维持登录状态

**核心功能**:
- 从`config/cookies.txt`读取Cookie字符串
- 解析Cookie字符串为字典格式
- 将Cookie注入到浏览器会话
- 验证Cookie有效性

**关键方法**:
```python
class CookieManager:
    def load_cookies_from_file(self, file_path):
        """从文件加载Cookie字符串"""

    def parse_cookie_string(self, cookie_str):
        """解析Cookie字符串为字典"""

    def inject_cookies(self, driver):
        """将Cookie注入到浏览器"""

    def validate_cookies(self, driver):
        """验证Cookie是否有效"""
```

### 7.3 验证码处理工具 (captcha_handler.py)

**用途**: 检测验证码并协调人工处理

**核心功能**:
- 检测页面是否出现滑块验证码
- 暂停程序并输出提示信息
- 等待用户手动完成验证
- 验证完成后继续执行

**关键方法**:
```python
class CaptchaHandler:
    def detect_captcha(self, driver):
        """检测是否出现验证码"""

    def wait_for_manual_solve(self):
        """等待用户手动解决验证码"""

    def verify_captcha_solved(self, driver):
        """验证验证码是否已解决"""
```

### 7.4 数据库管理工具 (db_manager.py)

**用途**: 管理MySQL数据库连接和数据操作

**核心功能**:
- 建立和管理数据库连接
- 插入商品信息到products表
- 插入SKU信息到skus表
- 记录价格历史到price_history表
- 记录日志到crawl_logs表
- 查询和更新数据

**关键方法**:
```python
class DBManager:
    def __init__(self, config):
        """初始化数据库连接"""

    def insert_product(self, product_id, title, product_url):
        """插入商品信息"""

    def insert_sku(self, product_id, sku_name, price, sku_url):
        """插入SKU信息"""

    def insert_price_history(self, sku_id, price):
        """记录价格历史"""

    def insert_log(self, log_level, message, product_url=None):
        """插入日志记录"""

    def close(self):
        """关闭数据库连接"""
```

### 7.5 日志管理工具 (logger.py)

**用途**: 统一管理日志输出

**核心功能**:
- 配置多级日志(DEBUG/INFO/WARNING/ERROR/CRITICAL)
- 控制台输出(INFO及以上)
- 文件日志(所有级别)
- 数据库日志(WARNING及以上)
- 格式化日志输出

**关键方法**:
```python
class LoggerManager:
    def __init__(self, log_file_path):
        """初始化日志管理器"""

    def debug(self, message):
        """输出DEBUG级别日志"""

    def info(self, message):
        """输出INFO级别日志"""

    def warning(self, message, product_url=None):
        """输出WARNING级别日志"""

    def error(self, message, product_url=None):
        """输出ERROR级别日志"""
```

### 7.6 搜索页爬取工具 (search_page.py)

**用途**: 爬取淘宝搜索结果页

**核心功能**:
- 访问淘宝搜索页面
- 输入搜索关键词
- 提取当前页所有商品链接(48个)
- 翻页到下一页
- 处理页面加载异常

**关键方法**:
```python
class SearchPageCrawler:
    def search_keyword(self, keyword):
        """搜索关键词"""

    def get_product_links(self):
        """获取当前页所有商品链接"""

    def go_to_next_page(self):
        """翻页到下一页"""

    def crawl_pages(self, keyword, max_pages=3):
        """爬取多页搜索结果"""
```

### 7.7 商品详情页爬取工具 (product_page.py)

**用途**: 爬取商品详情页的SKU信息

**核心功能**:
- 访问商品详情页
- 提取商品标题和商品ID
- 获取所有SKU选项
- 依次点击SKU并提取价格
- 生成简化的SKU链接
- 处理SKU信息缺失

**关键方法**:
```python
class ProductPageCrawler:
    def extract_product_info(self):
        """提取商品基本信息"""

    def get_sku_options(self):
        """获取所有SKU选项"""

    def click_sku_and_get_price(self, sku_element):
        """点击SKU并获取价格"""

    def generate_sku_url(self, product_id, sku_id):
        """生成简化的SKU链接"""

    def crawl_product(self, product_url):
        """爬取单个商品的所有SKU信息"""
```

---

## 8. 技术栈

### 编程语言
| 技术 | 版本 | 说明 |
|------|------|------|
| Python | 3.8+ | 主要编程语言 |

### 核心依赖库
| 库名 | 版本 | 用途 |
|------|------|------|
| selenium | ≥4.15.0 | Web自动化框架,模拟浏览器操作 |
| selenium-stealth | ≥1.0.6 | 隐藏Selenium自动化特征,降低被检测风险 |
| pymysql | ≥1.1.0 | MySQL数据库连接驱动 |
| tqdm | ≥4.66.0 | 进度条显示库 |
| fake-useragent | ≥1.4.0 | 随机User-Agent生成 |

### 系统依赖
| 组件 | 版本 | 说明 |
|------|------|------|
| Chrome浏览器 | 最新稳定版 | Selenium驱动的浏览器 |
| ChromeDriver | 与Chrome版本匹配 | Selenium WebDriver |
| MySQL | 5.7+ / 8.0+ | 数据存储数据库 |

### 可选依赖
| 库名 | 用途 | 阶段 |
|------|------|------|
| requests | 代理IP池管理 | 未来扩展 |
| pandas | 数据分析和导出 | 未来扩展 |
| matplotlib | 价格趋势可视化 | 未来扩展 |
| schedule | 定时任务调度 | 未来扩展 |

### 第三方集成
- **淘宝网**: 数据源(需遵守robots.txt和服务条款)
- **Chrome DevTools**: Cookie获取工具

---

## 9. 安全与配置

### 认证/授权方法

**Cookie认证**:
- 用户手动从浏览器获取Cookie字符串
- Cookie存储在本地文件`config/cookies.txt`
- 程序启动时加载Cookie到浏览器会话
- 每次请求携带Cookie维持登录状态

**安全注意事项**:
- Cookie包含敏感信息,不应提交到版本控制系统
- 建议在`.gitignore`中添加`config/cookies.txt`
- Cookie有效期有限,需定期更新

### 配置管理

**配置文件**: `config/config.py`

**数据库配置**:
```python
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '您的MySQL密码',  # 敏感信息
    'database': 'taobao_spider',
    'charset': 'utf8mb4'
}
```

**爬虫参数配置**:
```python
SPIDER_CONFIG = {
    'search_keyword': '肯德基代下单',
    'max_pages': 3,
    'page_delay_min': 3,      # 页面间延迟最小值(秒)
    'page_delay_max': 6,      # 页面间延迟最大值(秒)
    'sku_delay_min': 2,       # SKU间延迟最小值(秒)
    'sku_delay_max': 5,       # SKU间延迟最大值(秒)
    'page_load_timeout': 30,  # 页面加载超时(秒)
    'retry_times': 3,         # 重试次数
    'retry_delay': 5          # 重试间隔(秒)
}
```

**日志配置**:
```python
LOG_CONFIG = {
    'log_dir': 'logs/',
    'log_level': 'INFO',
    'console_output': True,
    'file_output': True,
    'db_output': True
}
```

### 安全范围

#### 范围内 ✅
- Cookie本地存储和加载
- 数据库连接密码配置
- 参数化SQL查询(防止SQL注入)
- 异常捕获和日志记录
- 资源清理(浏览器、数据库连接)

#### 范围外 ❌
- Cookie加密存储
- 数据库密码加密
- HTTPS证书验证
- 数据传输加密
- 用户权限管理
- API认证和授权

### 部署注意事项

**环境要求**:
- Windows操作系统
- Python 3.8+已安装
- MySQL数据库已安装并运行
- Chrome浏览器已安装
- ChromeDriver版本与Chrome匹配

**安全建议**:
1. 不要在公共网络环境运行
2. 控制爬取频率,避免被封禁
3. 定期更新Cookie
4. 监控日志,及时发现异常
5. 遵守淘宝服务条款和robots.txt

**合规性**:
- 仅用于学习和研究目的
- 不得用于商业用途
- 不得大规模采集数据
- 尊重网站服务条款

---

## 10. API 规范

本项目为数据采集系统,不对外提供API接口。数据通过MySQL数据库存储和访问。

### 数据库表结构

#### 10.1 products表 (商品主表)

**表名**: `products`

**字段定义**:
```sql
CREATE TABLE products (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    product_id VARCHAR(100) NOT NULL UNIQUE COMMENT '淘宝商品ID',
    title VARCHAR(500) NOT NULL COMMENT '商品标题',
    product_url VARCHAR(1000) NOT NULL COMMENT '商品链接',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_product_id (product_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品主表';
```

**示例数据**:
```json
{
    "id": 1,
    "product_id": "649758140938",
    "title": "肯德基代下单服务 全国通用",
    "product_url": "https://item.taobao.com/item.htm?id=649758140938",
    "created_at": "2026-01-23 10:30:45",
    "updated_at": "2026-01-23 10:30:45"
}
```

#### 10.2 skus表 (SKU信息表)

**表名**: `skus`

**字段定义**:
```sql
CREATE TABLE skus (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    product_id BIGINT NOT NULL COMMENT '关联商品ID',
    sku_name VARCHAR(500) NOT NULL COMMENT 'SKU名称',
    price DECIMAL(10,2) NOT NULL COMMENT 'SKU价格',
    sku_url VARCHAR(1000) NULL COMMENT 'SKU链接',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    INDEX idx_product_id (product_id),
    INDEX idx_price (price),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='SKU信息表';
```

**示例数据**:
```json
{
    "id": 1,
    "product_id": 1,
    "sku_name": "香辣鸡腿堡套餐",
    "price": 35.50,
    "sku_url": "https://item.taobao.com/item.htm?id=649758140938&skuId=5000253969559",
    "created_at": "2026-01-23 10:31:20",
    "updated_at": "2026-01-23 10:31:20"
}
```

#### 10.3 price_history表 (价格历史表)

**表名**: `price_history`

**字段定义**:
```sql
CREATE TABLE price_history (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    sku_id BIGINT NOT NULL COMMENT '关联SKU ID',
    price DECIMAL(10,2) NOT NULL COMMENT '价格',
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录时间',
    FOREIGN KEY (sku_id) REFERENCES skus(id) ON DELETE CASCADE,
    INDEX idx_sku_id (sku_id),
    INDEX idx_recorded_at (recorded_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='价格历史表';
```

**示例数据**:
```json
{
    "id": 1,
    "sku_id": 1,
    "price": 35.50,
    "recorded_at": "2026-01-23 10:31:20"
}
```

#### 10.4 crawl_logs表 (爬取日志表)

**表名**: `crawl_logs`

**字段定义**:
```sql
CREATE TABLE crawl_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    log_level VARCHAR(20) NOT NULL COMMENT '日志级别',
    message TEXT NOT NULL COMMENT '日志消息',
    product_url VARCHAR(1000) NULL COMMENT '相关商品链接',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_log_level (log_level),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='爬取日志表';
```

**示例数据**:
```json
{
    "id": 1,
    "log_level": "WARNING",
    "message": "检测到滑块验证码,等待人工处理",
    "product_url": "https://item.taobao.com/item.htm?id=649758140938",
    "created_at": "2026-01-23 10:32:15"
}
```

### 数据查询示例

**查询商品及其所有SKU**:
```sql
SELECT
    p.product_id,
    p.title,
    s.sku_name,
    s.price,
    s.sku_url
FROM products p
LEFT JOIN skus s ON p.id = s.product_id
WHERE p.product_id = '649758140938';
```

**查询SKU价格历史**:
```sql
SELECT
    s.sku_name,
    ph.price,
    ph.recorded_at
FROM skus s
JOIN price_history ph ON s.id = ph.sku_id
WHERE s.id = 1
ORDER BY ph.recorded_at DESC;
```

---

## 11. 成功标准

### MVP 成功定义

MVP被认为成功需要满足以下所有条件:

1. **功能完整性**: 所有核心功能正常工作,无阻塞性缺陷
2. **数据准确性**: 采集的SKU信息和价格数据准确率≥95%
3. **稳定性**: 能够连续运行完成3页搜索结果的爬取,无崩溃
4. **可用性**: 用户能够按照文档独立完成环境配置和程序运行

### 功能需求

#### 核心功能
- ✅ 成功访问淘宝搜索页面并输入关键词
- ✅ 爬取前3页搜索结果,每页48个商品链接
- ✅ 进入商品详情页,提取商品标题和ID
- ✅ 识别并点击所有SKU选项
- ✅ 准确提取每个SKU的名称和价格
- ✅ 生成简化的SKU链接(仅保留id和skuId参数)
- ✅ 数据成功存储到MySQL数据库的对应表中

#### 反爬虫功能
- ✅ 随机延迟功能正常工作(2-5秒范围)
- ✅ User-Agent随机轮换生效
- ✅ selenium-stealth成功隐藏自动化特征
- ✅ Cookie正确加载并维持登录状态
- ✅ 显示窗口模式运行

#### 异常处理
- ✅ 检测到滑块验证码时正确暂停并提示
- ✅ 页面加载超时时自动重试(最多3次)
- ✅ 商品爬取失败时暂停并输出失败信息
- ✅ SKU信息缺失时记录警告并跳过
- ✅ 数据库连接失败时立即停止并输出错误

#### 日志系统
- ✅ 控制台实时输出爬取进度
- ✅ 文件日志详细记录所有操作
- ✅ 进度条正确显示当前进度
- ✅ 关键日志写入数据库

### 质量指标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 数据准确率 | ≥95% | SKU信息和价格数据的准确性 |
| 爬取成功率 | ≥90% | 成功爬取的商品占总商品数的比例 |
| 系统稳定性 | 无崩溃 | 完成3页爬取过程中不出现程序崩溃 |
| 响应时间 | ≤5秒 | 单个SKU的爬取时间(不含延迟) |
| 日志完整性 | 100% | 所有关键操作都有日志记录 |

### 用户体验目标

- ✅ 用户能够在30分钟内完成环境配置
- ✅ 用户能够理解控制台输出的信息
- ✅ 遇到验证码时用户知道如何处理
- ✅ 遇到错误时用户能够根据提示采取措施
- ✅ 用户能够通过日志文件排查问题

---

## 12. 实施阶段

### 阶段1: 基础设施搭建

**目标**: 建立项目基础架构和开发环境

**交付物**:
- ✅ 创建项目目录结构(config/, utils/, crawler/, logs/)
- ✅ 配置管理模块(config.py)
- ✅ 数据库建表SQL脚本(database.sql)
- ✅ 依赖包安装和环境验证
- ✅ 日志系统实现(logger.py)

**验证标准**:
- 项目目录结构完整
- 配置文件可正常读取
- 数据库表创建成功
- 日志系统能够正常输出到控制台和文件

**预估工作量**: 2-3小时

---

### 阶段2: 核心工具模块开发

**目标**: 实现浏览器管理、Cookie管理、数据库操作等核心工具

**交付物**:
- ✅ 浏览器管理工具(browser.py)
  - 初始化Chrome浏览器
  - 应用selenium-stealth
  - 设置随机User-Agent
- ✅ Cookie管理工具(cookie_manager.py)
  - 读取和解析Cookie文件
  - 注入Cookie到浏览器
- ✅ 数据库管理工具(db_manager.py)
  - 数据库连接管理
  - 数据插入和查询方法
- ✅ 验证码处理工具(captcha_handler.py)
  - 验证码检测
  - 人工处理流程

**验证标准**:
- 浏览器能够正常启动并隐藏自动化特征
- Cookie能够成功加载并维持登录状态
- 数据库连接正常,数据能够正确插入
- 验证码检测和暂停机制工作正常

**预估工作量**: 4-6小时

---

### 阶段3: 爬虫核心逻辑实现

**目标**: 实现搜索页和商品详情页的爬取逻辑

**交付物**:
- ✅ 搜索页爬取模块(search_page.py)
  - 搜索关键词
  - 提取商品链接
  - 翻页功能
- ✅ 商品详情页爬取模块(product_page.py)
  - 提取商品信息
  - 点击SKU并获取价格
  - 生成简化链接
- ✅ 主程序入口(main.py)
  - 初始化各模块
  - 协调爬取流程
  - 异常处理和重试机制

**验证标准**:
- 能够成功爬取3页搜索结果
- 能够进入商品详情页并提取信息
- SKU信息和价格准确提取
- 数据正确存储到数据库
- 异常情况能够正确处理

**预估工作量**: 6-8小时

---

### 阶段4: 测试、优化和文档完善

**目标**: 全面测试系统功能,优化性能,完善文档

**交付物**:
- ✅ 功能测试
  - 完整流程测试
  - 异常场景测试
  - 数据准确性验证
- ✅ 性能优化
  - 调整延迟参数
  - 优化数据库查询
  - 减少不必要的等待
- ✅ 文档完善
  - README.md使用说明
  - 代码注释补充
  - 常见问题FAQ
- ✅ 代码审查和重构
  - 代码规范检查
  - 重复代码提取
  - 错误处理完善

**验证标准**:
- 所有功能测试通过
- 数据准确率≥95%
- 爬取成功率≥90%
- 文档清晰完整,用户能够独立使用
- 代码符合规范,可维护性良好

**预估工作量**: 3-4小时

---

## 13. 未来考虑

### Post-MVP 增强功能

#### 定时任务和自动化
- **定时调度**: 使用schedule库或Windows任务计划程序实现定时爬取
- **增量更新**: 只爬取价格变化的SKU,提高效率
- **自动重启**: 程序异常退出后自动重启
- **健康检查**: 定期检查Cookie有效性和数据库连接状态

#### 价格监控和通知
- **价格变动检测**: 对比历史价格,识别价格变化
- **阈值告警**: 价格变动超过设定阈值时触发通知
- **通知渠道**: 邮件通知、微信通知、钉钉通知
- **报表生成**: 定期生成价格变动报表

#### 数据分析和可视化
- **价格趋势分析**: 绘制价格变化曲线图
- **商品热度排名**: 统计商品浏览量和销量
- **价格区间分布**: 分析不同价格区间的商品数量
- **数据导出**: 导出Excel/CSV格式报表

### 集成机会

#### 代理IP池集成
- **代理服务商**: 集成第三方代理IP服务(如阿布云、快代理)
- **IP轮换策略**: 每次请求或每N次请求切换IP
- **IP质量检测**: 自动检测和剔除失效IP
- **成本优化**: 根据爬取频率选择合适的代理套餐

#### 验证码识别服务
- **打码平台**: 集成打码平台API(如超级鹰、若快)
- **自动识别**: 检测到验证码时自动调用识别服务
- **成功率监控**: 统计验证码识别成功率
- **降级策略**: 识别失败时回退到人工处理

#### 消息队列集成
- **任务队列**: 使用Redis或RabbitMQ管理爬取任务
- **分布式爬取**: 多个爬虫实例并行处理任务
- **任务优先级**: 根据商品重要性设置任务优先级
- **失败重试**: 失败任务自动重新入队

### 后期阶段的高级功能

#### 性能优化
- **多线程爬取**: 使用线程池并行爬取多个商品
- **异步IO**: 使用asyncio提高IO密集型操作效率
- **数据库优化**: 批量插入、索引优化、查询缓存
- **断点续爬**: 记录爬取进度,支持中断后继续

#### 平台扩展
- **京东平台**: 扩展支持京东商品爬取
- **拼多多平台**: 扩展支持拼多多商品爬取
- **美团平台**: 扩展支持美团商品爬取
- **统一接口**: 抽象爬虫接口,支持多平台切换

#### Web管理界面
- **任务管理**: 创建、启动、停止、删除爬取任务
- **数据查看**: 查看商品信息、SKU信息、价格历史
- **日志查看**: 实时查看爬取日志和系统状态
- **配置管理**: 在线修改爬虫参数和数据库配置
- **数据可视化**: 图表展示价格趋势和统计数据

---

## 14. 风险与缓解措施

### 风险1: 反爬虫机制升级

**风险描述**: 淘宝可能随时升级反爬虫策略,导致现有爬虫失效

**影响程度**: 高

**缓解策略**:
1. **多层防护**: 实施多种反爬虫对抗策略(延迟、User-Agent、stealth等)
2. **监控告警**: 实时监控爬取成功率,异常时及时告警
3. **快速响应**: 建立问题响应机制,发现问题后快速调整策略
4. **备用方案**: 预留代理IP池接口,必要时启用代理
5. **降低频率**: 控制爬取频率,避免触发风控

---

### 风险2: Cookie频繁失效

**风险描述**: Cookie有效期有限,频繁失效影响爬取连续性

**影响程度**: 中

**缓解策略**:
1. **有效期监控**: 记录Cookie获取时间,定期提醒更新
2. **自动检测**: 爬取前检测Cookie有效性,失效时及时提示
3. **多账号轮换**: 准备多个淘宝账号,轮换使用Cookie
4. **降级处理**: Cookie失效时暂停爬取,等待人工更新
5. **文档说明**: 在文档中明确说明Cookie更新流程

---

### 风险3: 页面结构变化

**风险描述**: 淘宝页面结构调整导致元素定位失败

**影响程度**: 中

**缓解策略**:
1. **多选择器策略**: 为关键元素准备多个备用选择器
2. **异常捕获**: 完善异常处理,元素定位失败时记录详细日志
3. **版本控制**: 记录页面结构版本,便于快速定位问题
4. **定期检查**: 定期运行爬虫,及时发现页面变化
5. **快速修复**: 建立快速修复流程,发现问题后尽快更新选择器

---

### 风险4: 数据准确性问题

**风险描述**: SKU价格动态加载,可能捕获到错误的价格数据

**影响程度**: 高

**缓解策略**:
1. **显式等待**: 使用WebDriverWait等待价格元素更新
2. **二次验证**: 点击SKU后等待足够时间,确保价格已更新
3. **数据校验**: 对采集的价格数据进行合理性校验(如价格范围检查)
4. **日志记录**: 详细记录每次价格提取过程,便于问题排查
5. **人工抽检**: 定期人工抽检数据准确性,发现问题及时调整

---

### 风险5: 法律合规风险

**风险描述**: 爬虫行为可能违反淘宝服务条款或相关法律法规

**影响程度**: 高

**缓解策略**:
1. **明确用途**: 在文档中明确说明仅用于学习和研究目的
2. **遵守协议**: 严格遵守robots.txt协议和服务条款
3. **控制频率**: 严格控制爬取频率,避免对服务器造成压力
4. **数据保护**: 不公开传播采集的数据,仅个人使用
5. **免责声明**: 在文档中添加免责声明,提醒用户注意法律风险

---

## 15. 附录

### 15.1 相关文档

- **需求规格说明书**: `spec.md` - 详细的技术需求和实现方案
- **项目README**: `README.md` - 项目使用说明和快速开始指南
- **数据库建表脚本**: `config/database.sql` - MySQL数据库表结构定义
- **配置文件**: `config/config.py` - 系统配置参数

### 15.2 关键依赖项

#### Python库
- [Selenium](https://pypi.org/project/selenium/) - Web自动化测试框架
- [selenium-stealth](https://pypi.org/project/selenium-stealth/) - 隐藏Selenium自动化特征
- [PyMySQL](https://pypi.org/project/PyMySQL/) - Python MySQL客户端
- [tqdm](https://pypi.org/project/tqdm/) - 进度条显示库
- [fake-useragent](https://pypi.org/project/fake-useragent/) - 随机User-Agent生成

#### 系统组件
- [Chrome浏览器](https://www.google.com/chrome/) - Google Chrome浏览器
- [ChromeDriver](https://chromedriver.chromium.org/) - Chrome WebDriver
- [MySQL](https://www.mysql.com/) - 关系型数据库

### 15.3 代码库结构

```
spider/
├── config/                    # 配置模块
│   ├── __init__.py           # 模块初始化
│   ├── config.py             # 配置管理
│   ├── cookies.txt           # Cookie存储(不提交到Git)
│   └── database.sql          # 数据库建表脚本
│
├── utils/                     # 工具模块
│   ├── __init__.py           # 模块初始化
│   ├── browser.py            # 浏览器管理
│   ├── cookie_manager.py     # Cookie管理
│   ├── captcha_handler.py    # 验证码处理
│   ├── proxy_manager.py      # 代理管理(预留)
│   ├── db_manager.py         # 数据库操作
│   └── logger.py             # 日志管理
│
├── crawler/                   # 爬虫核心模块
│   ├── __init__.py           # 模块初始化
│   ├── search_page.py        # 搜索页爬取
│   └── product_page.py       # 商品详情页爬取
│
├── logs/                      # 日志目录
│   └── spider_*.log          # 日志文件(不提交到Git)
│
├── docs/                      # 文档目录
│   └── plan/                 # 计划文档
│       └── taobao_kfc_spider_prd.md  # 产品需求文档
│
├── .gitignore                # Git忽略文件
├── main.py                   # 主程序入口
├── requirements.txt          # Python依赖包
├── spec.md                   # 需求规格说明书
└── README.md                 # 项目说明文档
```

### 15.4 环境配置清单

#### Python环境
```bash
# 检查Python版本
python --version  # 应为3.8+

# 安装依赖包
pip install -r requirements.txt
```

#### MySQL数据库
```bash
# 创建数据库
mysql -u root -p
CREATE DATABASE taobao_spider CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 导入表结构
mysql -u root -p taobao_spider < config/database.sql
```

#### ChromeDriver配置
```bash
# 检查Chrome版本
chrome --version

# 下载对应版本的ChromeDriver
# 将ChromeDriver添加到系统PATH
```

### 15.5 常见问题FAQ

**Q1: ChromeDriver版本不匹配怎么办?**
A: 访问 https://chromedriver.chromium.org/ 下载与Chrome浏览器版本匹配的ChromeDriver。

**Q2: 如何获取Cookie?**
A: 打开Chrome浏览器,登录淘宝,按F12打开开发者工具,切换到Network标签,刷新页面,选择任意请求,在Headers中找到Cookie字段并复制。

**Q3: 数据库连接失败怎么办?**
A: 检查MySQL服务是否启动,确认配置文件中的用户名和密码正确,确认数据库taobao_spider已创建。

**Q4: 频繁触发验证码怎么办?**
A: 降低爬取频率,增加延迟时间,使用selenium-stealth隐藏自动化特征,或考虑使用代理IP。

**Q5: 页面元素定位失败怎么办?**
A: 淘宝页面结构可能已更新,需要重新分析页面并更新选择器。

### 15.6 免责声明

**重要提示**:

1. 本项目仅用于技术学习和研究目的,不得用于任何商业用途
2. 使用本项目进行数据采集时,请严格遵守淘宝网站的robots.txt协议和服务条款
3. 请控制爬取频率,避免对淘宝服务器造成过大压力
4. 采集的数据仅供个人学习使用,不得公开传播或用于商业目的
5. 使用本项目产生的任何法律责任由使用者自行承担,项目作者不承担任何责任
6. 如果淘宝网站明确禁止爬虫行为,请立即停止使用本项目

**法律风险提示**:

根据《中华人民共和国网络安全法》和相关法律法规,未经授权的数据采集行为可能涉及以下法律风险:
- 侵犯网站运营者的合法权益
- 违反网站服务条款和用户协议
- 可能构成不正当竞争行为
- 大规模采集可能影响网站正常运营

请使用者充分了解相关法律法规,合法合规使用本项目。

---

## 文档变更历史

| 版本 | 日期 | 作者 | 变更说明 |
|------|------|------|----------|
| 1.0 | 2026-01-23 | Claude Code | 初始版本,完成PRD全部章节 |

---

**文档结束**

