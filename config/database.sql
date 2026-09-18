-- 淘宝肯德基代下单爬虫数据库建表脚本
-- 数据库：taobao_spider
-- 字符集：utf8mb4

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS taobao_spider CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE taobao_spider;

-- 1. 商品主表
CREATE TABLE IF NOT EXISTS products (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    product_id VARCHAR(100) NOT NULL UNIQUE COMMENT '淘宝商品ID',
    title VARCHAR(500) NOT NULL COMMENT '商品标题',
    product_url VARCHAR(1000) NOT NULL COMMENT '商品链接',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_product_id (product_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品主表';

-- 2. SKU信息表
CREATE TABLE IF NOT EXISTS skus (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    product_db_id BIGINT NOT NULL COMMENT '关联商品ID',
    sku_name VARCHAR(500) NOT NULL COMMENT 'SKU名称',
    price DECIMAL(10,2) NOT NULL COMMENT 'SKU价格',
    sku_url VARCHAR(1000) COMMENT 'SKU链接',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    CONSTRAINT fk_sku_product FOREIGN KEY (product_db_id) REFERENCES products(id) ON DELETE CASCADE,
    INDEX idx_product_db_id (product_db_id),
    INDEX idx_price (price),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='SKU信息表';

-- 3. 价格历史表
CREATE TABLE IF NOT EXISTS price_history (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    sku_id BIGINT NOT NULL COMMENT '关联SKU ID',
    price DECIMAL(10,2) NOT NULL COMMENT '价格',
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录时间',
    CONSTRAINT fk_price_sku FOREIGN KEY (sku_id) REFERENCES skus(id) ON DELETE CASCADE,
    INDEX idx_sku_id (sku_id),
    INDEX idx_recorded_at (recorded_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='价格历史表';

-- 4. 爬取日志表
CREATE TABLE IF NOT EXISTS crawl_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    log_level VARCHAR(20) NOT NULL COMMENT '日志级别',
    message TEXT NOT NULL COMMENT '日志消息',
    product_url VARCHAR(1000) COMMENT '相关商品链接',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_log_level (log_level),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='爬取日志表';
