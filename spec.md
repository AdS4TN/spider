# 淘宝肯德基代下单爬虫项目需求规格说明书

## 1. 项目概述

### 1.1 项目目标
开发一个淘宝商品爬虫，用于爬取"肯德基代下单"关键词搜索结果中的商品SKU信息，实现价格监控功能。

### 1.2 使用场景
- Demo版本：一次性数据采集
- 后续扩展：定期更新，用于价格监控

---

## 2. 功能需求

### 2.1 搜索范围
- **搜索关键词**：肯德基代下单
- **爬取页数**：每次爬取3页搜索结果
- **每页商品数**：48个商品（6行 × 8列）
- **总计商品数**：约144个商品

### 2.2 数据采集流程
1. 访问淘宝搜索页面，输入关键词"肯德基代下单"
2. 遍历前3页搜索结果
3. 依次点击每个商品链接，进入商品详情页
4. 在商品详情页中，依次点击每个SKU选项
5. 提取每个SKU的以下信息：
   - SKU名称
   - SKU价格（点击SKU后更新的价格）
   - SKU链接（简化格式）
   - 商品标题

### 2.3 SKU链接格式
- **完整链接示例**：`https://item.taobao.com/item.htm?id=649758140938&skuId=5000253969559&...其他参数`
- **简化链接格式**：`https://item.taobao.com/item.htm?id=649758140938&skuId=5000253969559`
- **提取规则**：只保留`id`和`skuId`两个参数

### 2.4 数据存储字段
| 字段名 | 说明 | 示例 |
|--------|------|------|
| 商品ID | 淘宝商品唯一标识 | 649758140938 |
| 商品标题 | 商品主标题 | 肯德基代下单服务 |
| 商品链接 | 商品详情页链接 | https://item.taobao.com/item.htm?id=649758140938 |
| SKU名称 | SKU选项名称 | 香辣鸡腿堡套餐 |
| SKU价格 | SKU对应价格 | 35.50 |
| SKU链接 | SKU简化链接 | https://item.taobao.com/item.htm?id=649758140938&skuId=5000253969559 |

---

## 3. 技术方案

### 3.1 技术栈选型
| 技术组件 | 选型方案 | 说明 |
|----------|----------|------|
| 爬虫框架 | Selenium + Chrome | 稳定性高，能处理动态加载和反爬 |
| 浏览器模式 | 显示窗口（非无头模式） | 降低被检测风险 |
| 数据库 | MySQL | 本地MySQL数据库 |
| 编程语言 | Python 3.x | - |
| 运行环境 | Windows | - |

### 3.2 反爬虫对抗策略

| 策略类型 | 实现方案 | 说明 |
|----------|----------|------|
| 随机延迟 | 每次请求间隔2-5秒随机延迟 | 模拟人工操作节奏 |
| 随机User-Agent | 从预设列表中随机选择 | 模拟不同浏览器访问 |
| 隐藏自动化特征 | 使用selenium-stealth库 | 隐藏webdriver等自动化标识 |
| Cookie管理 | 手动导入Cookie字符串 | 维持登录状态 |
| 代理IP池 | 预留接口（后续扩展） | 避免IP被封禁 |

### 3.3 验证码处理策略

**滑块验证码处理方案**：
- 检测到滑块验证码时，程序自动暂停
- 在控制台输出提示信息，等待用户手动完成验证
- 用户完成验证后，按Enter键继续爬取
- 使用selenium-stealth降低验证码出现频率

---

## 4. 数据库设计

### 4.1 数据库连接配置
- **主机地址**：localhost
- **端口**：3306
- **用户名**：root
- **密码**：（配置文件中填写）
- **数据库名**：taobao_spider
- **字符集**：utf8mb4

### 4.2 数据表结构

#### 4.2.1 products（商品主表）
| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | BIGINT | 主键ID | AUTO_INCREMENT, PRIMARY KEY |
| product_id | VARCHAR(100) | 淘宝商品ID | NOT NULL, UNIQUE |
| title | VARCHAR(500) | 商品标题 | NOT NULL |
| product_url | VARCHAR(1000) | 商品链接 | NOT NULL |
| created_at | TIMESTAMP | 创建时间 | DEFAULT CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | 更新时间 | ON UPDATE CURRENT_TIMESTAMP |

#### 4.2.2 skus（SKU信息表）
| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | BIGINT | 主键ID | AUTO_INCREMENT, PRIMARY KEY |
| product_id | BIGINT | 关联商品ID | NOT NULL, FOREIGN KEY |
| sku_name | VARCHAR(500) | SKU名称 | NOT NULL |
| price | DECIMAL(10,2) | SKU价格 | NOT NULL |
| sku_url | VARCHAR(1000) | SKU链接 | NULL |
| created_at | TIMESTAMP | 创建时间 | DEFAULT CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | 更新时间 | ON UPDATE CURRENT_TIMESTAMP |

#### 4.2.3 price_history（价格历史表）
| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | BIGINT | 主键ID | AUTO_INCREMENT, PRIMARY KEY |
| sku_id | BIGINT | 关联SKU ID | NOT NULL, FOREIGN KEY |
| price | DECIMAL(10,2) | 价格 | NOT NULL |
| recorded_at | TIMESTAMP | 记录时间 | DEFAULT CURRENT_TIMESTAMP |

#### 4.2.4 crawl_logs（爬取日志表）
| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | BIGINT | 主键ID | AUTO_INCREMENT, PRIMARY KEY |
| log_level | VARCHAR(20) | 日志级别 | NOT NULL |
| message | TEXT | 日志消息 | NOT NULL |
| product_url | VARCHAR(1000) | 相关商品链接 | NULL |
| created_at | TIMESTAMP | 创建时间 | DEFAULT CURRENT_TIMESTAMP |

---

## 5. Cookie管理

### 5.1 Cookie格式
- **输入格式**：Cookie字符串
- **示例**：`cookie1=value1; cookie2=value2; cookie3=value3`
- **获取方式**：从浏览器开发者工具中复制

### 5.2 Cookie存储位置
- **文件路径**：`config/cookies.txt`
- **文件格式**：纯文本，单行Cookie字符串

### 5.3 Cookie使用流程
1. 用户手动从浏览器复制Cookie字符串
2. 将Cookie字符串粘贴到`config/cookies.txt`文件中
3. 程序启动时自动读取并加载Cookie
4. 每次请求时携带Cookie维持登录状态

---

## 6. 日志系统

### 6.1 日志输出方式
| 输出方式 | 说明 | 用途 |
|----------|------|------|
| 控制台输出 | 实时显示爬取进度和状态 | 实时监控 |
| 文件日志 | 详细日志保存到文件 | 问题排查 |
| 进度条显示 | 使用tqdm显示爬取进度 | 可视化进度 |
| 数据库记录 | 关键日志写入数据库 | 持久化存储 |

### 6.2 日志级别
- **DEBUG**：调试信息（仅文件日志）
- **INFO**：一般信息（控制台+文件）
- **WARNING**：警告信息（控制台+文件+数据库）
- **ERROR**：错误信息（控制台+文件+数据库）
- **CRITICAL**：严重错误（控制台+文件+数据库）

### 6.3 日志文件
- **文件路径**：`logs/spider_YYYYMMDD_HHMMSS.log`
- **文件格式**：`[时间] [级别] [模块] 消息内容`
- **示例**：`[2026-01-23 10:30:45] [INFO] [search_page] 开始爬取第1页搜索结果`

---

## 7. 异常处理策略

### 7.1 商品爬取失败
- **处理方式**：程序暂停，等待用户处理
- **暂停提示**：在控制台输出错误信息和失败的商品链接
- **继续方式**：用户按Enter键后继续爬取下一个商品
- **日志记录**：将失败信息记录到日志文件和数据库

### 7.2 页面加载超时
- **超时时间**：30秒
- **重试次数**：3次
- **重试间隔**：5秒
- **失败处理**：3次重试后仍失败，则暂停程序

### 7.3 SKU信息缺失
- **处理方式**：记录警告日志，保存已获取的部分数据
- **继续执行**：跳过该SKU，继续处理下一个SKU

### 7.4 数据库连接失败
- **处理方式**：程序立即停止
- **错误提示**：输出详细的数据库连接错误信息
- **建议操作**：检查MySQL服务状态和配置信息

---

## 8. 项目结构

```
spider/
├── config/
│   ├── __init__.py
│   ├── config.py          # 配置文件
│   ├── cookies.txt        # Cookie字符串存储
│   └── database.sql       # 数据库建表SQL
├── utils/
│   ├── __init__.py
│   ├── browser.py         # Selenium浏览器管理
│   ├── cookie_manager.py  # Cookie管理
│   ├── captcha_handler.py # 验证码处理
│   ├── proxy_manager.py   # 代理IP管理（预留）
│   ├── db_manager.py      # 数据库操作
│   └── logger.py          # 日志管理
├── crawler/
│   ├── __init__.py
│   ├── search_page.py     # 搜索结果页爬取
│   └── product_page.py    # 商品详情页爬取
├── logs/                  # 日志文件目录
├── main.py                # 主程序入口
├── requirements.txt       # 依赖包
├── spec.md                # 需求规格说明书
└── README.md              # 使用说明
```

---

## 9. 依赖包清单

```
selenium>=4.15.0
selenium-stealth>=1.0.6
pymysql>=1.1.0
tqdm>=4.66.0
fake-useragent>=1.4.0
```

---

## 10. 运行流程

### 10.1 启动流程
1. 程序启动，初始化日志系统
2. 读取配置文件（数据库配置、爬虫参数）
3. 加载Cookie字符串
4. 连接MySQL数据库
5. 初始化Selenium浏览器（应用反爬策略）
6. 开始爬取流程

### 10.2 爬取流程
```
开始
  ↓
访问淘宝搜索页面
  ↓
输入关键词"肯德基代下单"
  ↓
循环：遍历3页搜索结果
  ├─ 获取当前页所有商品链接（48个）
  ├─ 循环：遍历每个商品链接
  │   ├─ 打开商品详情页
  │   ├─ 提取商品标题和商品ID
  │   ├─ 保存商品信息到数据库
  │   ├─ 循环：遍历所有SKU选项
  │   │   ├─ 点击SKU选项
  │   │   ├─ 等待价格更新
  │   │   ├─ 提取SKU名称、价格
  │   │   ├─ 从URL提取简化链接
  │   │   ├─ 保存SKU信息到数据库
  │   │   └─ 随机延迟2-5秒
  │   └─ 返回搜索结果页
  ├─ 点击"下一页"按钮
  └─ 随机延迟3-6秒
  ↓
爬取完成，关闭浏览器
  ↓
结束
```

### 10.3 验证码处理流程
```
检测到滑块验证码
  ↓
程序暂停
  ↓
控制台输出提示：
"检测到滑块验证码，请手动完成验证后按Enter键继续..."
  ↓
等待用户手动完成验证
  ↓
用户按Enter键
  ↓
程序继续执行
```

---

## 11. 配置说明

### 11.1 数据库配置
在`config/config.py`中配置以下参数：

```python
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '您的MySQL密码',
    'database': 'taobao_spider',
    'charset': 'utf8mb4'
}
```

### 11.2 爬虫参数配置
```python
SPIDER_CONFIG = {
    'search_keyword': '肯德基代下单',
    'max_pages': 3,
    'page_delay_min': 3,
    'page_delay_max': 6,
    'sku_delay_min': 2,
    'sku_delay_max': 5,
    'page_load_timeout': 30,
    'retry_times': 3,
    'retry_delay': 5
}
```

### 11.3 Cookie配置
在`config/cookies.txt`中粘贴从浏览器复制的Cookie字符串：

```
cookie1=value1; cookie2=value2; cookie3=value3; ...
```

**获取Cookie的步骤**：
1. 打开Chrome浏览器，访问淘宝并登录
2. 按F12打开开发者工具
3. 切换到"Network"标签
4. 刷新页面，选择任意请求
5. 在"Headers"中找到"Cookie"字段
6. 复制完整的Cookie字符串到`config/cookies.txt`

---

## 12. 使用指南

### 12.1 环境准备
1. 安装Python 3.8+
2. 安装MySQL数据库
3. 安装Chrome浏览器
4. 下载对应版本的ChromeDriver

### 12.2 安装步骤
```bash
# 1. 克隆或下载项目到本地
cd D:\spider

# 2. 安装依赖包
pip install -r requirements.txt

# 3. 创建数据库
mysql -u root -p < config/database.sql

# 4. 配置数据库密码
# 编辑 config/config.py，填写MySQL密码

# 5. 配置Cookie
# 编辑 config/cookies.txt，粘贴Cookie字符串
```

### 12.3 运行程序
```bash
python main.py
```

### 12.4 运行过程
1. 程序启动后会自动打开Chrome浏览器
2. 浏览器会访问淘宝搜索页面
3. 控制台会显示实时爬取进度
4. 如遇到验证码，按提示手动完成后按Enter继续
5. 爬取完成后浏览器自动关闭

---

## 13. 注意事项

### 13.1 法律合规
- 本项目仅用于学习和研究目的
- 请遵守淘宝网站的robots.txt协议
- 不得用于商业用途或大规模数据采集
- 请控制爬取频率，避免对服务器造成压力

### 13.2 技术限制
- Cookie有效期有限，失效后需重新获取
- 淘宝反爬策略可能随时更新，需要相应调整代码
- 页面结构变化可能导致选择器失效
- 建议在非高峰时段运行，降低被封禁风险

### 13.3 数据准确性
- SKU价格可能存在促销活动等动态变化
- 部分商品可能存在地区限制或库存限制
- 建议定期更新数据以保持准确性

---

## 14. 后续扩展

### 14.1 定时任务
- 使用Windows任务计划程序或cron定时执行
- 实现增量更新，只爬取价格变化的SKU
- 添加价格变动通知功能（邮件/微信）

### 14.2 数据分析
- 价格趋势分析
- 商品热度排名
- 价格区间分布统计
- 导出Excel报表

### 14.3 性能优化
- 集成代理IP池，提高并发能力
- 使用多线程/多进程并行爬取
- 实现断点续爬功能
- 优化数据库查询性能

---

## 15. 常见问题

### 15.1 ChromeDriver版本不匹配
**问题**：启动时报错"ChromeDriver version mismatch"
**解决**：下载与Chrome浏览器版本匹配的ChromeDriver

### 15.2 数据库连接失败
**问题**：程序启动时提示数据库连接失败
**解决**：
1. 检查MySQL服务是否启动
2. 确认配置文件中的用户名和密码正确
3. 确认数据库taobao_spider已创建

### 15.3 Cookie失效
**问题**：爬取时提示需要登录
**解决**：重新从浏览器获取Cookie字符串并更新配置文件

### 15.4 页面元素定位失败
**问题**：程序运行时报错"Element not found"
**解决**：淘宝页面结构可能已更新，需要重新分析页面并更新选择器

---

**文档版本**：v1.0
**最后更新**：2026-01-23
**作者**：Claude Code
