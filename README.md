# Spider｜淘宝指定商品采集工具

> 按关键词采集淘宝指定商品，提取商品信息、SKU 与价格，并保存到 MySQL。

## 项目能力

| 模块 | 代码中的实现 |
| --- | --- |
| 搜索页 | 按关键词访问结果、翻页并收集商品链接 |
| 详情页 | 解析商品与 SKU 信息，组织价格数据 |
| 存储 | MySQL 商品 / SKU 数据、价格历史与采集日志 |
| 登录态 | 读取本地 Cookie 并注入自己的浏览器会话 |
| 节流 | 页面与 SKU 操作间随机等待 |
| 人工介入 | 检测到验证码时暂停，由用户处理 |
| 排查 | 控制台与文件日志、失败现场辅助排查 |

## 技术与流程

- Python、Selenium、Chrome：交互式浏览器采集。
- PyMySQL、MySQL：结构化数据与历史记录。
- python-dotenv：加载本地 `.env`。
- tqdm、logging：进度与运行记录。
- 浏览器适配包含 fake-useragent / selenium-stealth，不代表可以绕过平台限制或获得访问授权。

```text
main.py → 初始化数据库与浏览器 → 读取本地登录态
                                      ↓
                              搜索页 → 商品链接
                                      ↓
                              详情页 → SKU / 价格
                                      ↓
                         MySQL 持久化 + 日志 + 历史记录
```

## 本地启动

建议 Python 3.11+、已安装的 Chrome，以及可连接的 MySQL。本次整理不承诺特定浏览器 / 网站版本兼容性。

```powershell
git clone https://github.com/AdS4TN/spider.git
cd spider
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

### 1. 初始化数据库

用自己的账号连接 MySQL，在 MySQL 客户端内执行：

```sql
SOURCE C:/your-path/spider/config/database.sql;
```

替换为实际路径。脚本创建 `taobao_spider` 数据库及表；部署时使用最小权限账号，不要把真实凭据写进源码。

### 2. 配置环境

编辑 `.env`：

```dotenv
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_NAME=taobao_spider
```

`main.py` 在导入配置前加载 `.env`。在 `config/config.py` 的 `SPIDER_CONFIG` 中，将 `search_keyword` 修改为目标商品关键词，即可指定采集对象，不限于某一商品类别。例如：

```python
SPIDER_CONFIG = {
    "search_keyword": "无线鼠标",
    "max_pages": 3,
}
```

上面仅展示需要关注的配置项，不要用它覆盖整个配置字典。修改 `search_keyword` 和 `max_pages` 后运行 `python main.py`；实际采集数量取决于搜索结果、访问权限与页面加载情况。

### 3. 准备授权登录态

在 `config/cookies.txt` 保存你自己的、获准用于该场景的会话 Cookie，第一行格式为 `name=value; name2=value2`。文件已被 Git 忽略，仓库不附真实 Cookie。不要使用他人账号或登录态。

### 4. 运行

```powershell
python main.py
```

程序会打开浏览器。遇到验证或权限限制时按提示人工处理，不要将其当作验证码绕过工具。登录态失效、页面变化或数据缺失时，应停止并排查，不要无上限重试。

## 数据模型

表定义见 [config/database.sql](config/database.sql)：

```sql
SELECT id, product_id, title FROM products LIMIT 20;
SELECT p.title, s.sku_name, s.price
FROM products AS p
JOIN skus AS s ON p.id = s.product_db_id
LIMIT 20;
SELECT * FROM price_history ORDER BY recorded_at DESC LIMIT 20;
```

历史记录用于观察变化，不代表平台实时价格承诺。

## 目录与阅读顺序

```text
main.py                  主流程与资源收尾
config/config.py         环境变量与参数
config/database.sql      表结构
crawler/search_page.py   搜索页遍历
crawler/product_page.py  商品与 SKU 解析
utils/db_manager.py      DTO 与数据库操作
utils/cookie_manager.py  本地会话加载
utils/captcha_handler.py 人工验证入口
utils/throttler.py       等待与节流
utils/logger.py          日志
```

建议阅读 `main.py` → `crawler/search_page.py` → `crawler/product_page.py` → `utils/db_manager.py`。

## 验证与限制

本地核验（2026-09-18，Python 3.12）：核心源码语法检查及配置 / 爬虫模块导入通过。未连接真实数据库、打开浏览器或执行线上采集。

不启动浏览器、不访问目标站点的语法检查：

```powershell
python -m compileall -q main.py config crawler utils
```

- `test_extract.py` 是会真实打开浏览器的调试脚本，含历史链接与本机输出路径，**不是自动化单元测试**。
- `analyze_json.py` 依赖本地调试产物，干净克隆不含这些数据。
- 当前没有完整的隔离测试套件；真实采集需准备数据库、浏览器与授权会话，本次不声称线上采集验收通过。
- 浏览器失败时检查 Chrome 与驱动；数据库失败时检查服务、权限和 `.env`。

## 安全与来源说明

GitHub 版本为本地项目的脱敏发布快照：不携带旧历史、Cookie、`.env`、日志截图、页面转储和虚拟环境。原目录与历史没有改写；不要将导入日期当作最初开发日期。

仅在获得授权、符合平台访问规则的场景使用，控制频率，不采集无关个人信息，不公开会话与页面转储。历史 README 的 MIT 字样没有对应独立 LICENSE 文件，本次不擅自增加授权声明。

背景见 [项目需求](docs/plan/taobao_kfc_spider_prd.md)；文档规划不等于已验收功能。
