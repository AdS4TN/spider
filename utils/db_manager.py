# -*- coding: utf-8 -*-
"""
数据库管理模块
负责MySQL数据库连接和数据操作
"""
import pymysql
from decimal import Decimal
from typing import Optional
from dataclasses import dataclass


@dataclass
class ProductDTO:
    """商品数据传输对象"""
    product_id: str
    title: str
    product_url: str


@dataclass
class SkuDTO:
    """SKU数据传输对象"""
    product_db_id: int
    sku_name: str
    price: Decimal
    sku_url: Optional[str] = None


class MySQLManager:
    """MySQL数据库管理器"""

    def __init__(self, config: dict, logger=None):
        """
        初始化数据库管理器

        Args:
            config: 数据库配置字典
            logger: 日志记录器（可选）
        """
        self.config = config
        self.logger = logger
        self.connection = None
        self.cursor = None

    def connect(self):
        """建立数据库连接"""
        try:
            self.connection = pymysql.connect(
                host=self.config['host'],
                port=self.config['port'],
                user=self.config['user'],
                password=self.config['password'],
                database=self.config['database'],
                charset=self.config['charset'],
                autocommit=False
            )
            self.cursor = self.connection.cursor()
            if self.logger:
                self.logger.info("db_manager", "数据库连接成功")
            return True
        except Exception as e:
            if self.logger:
                self.logger.error("db_manager", f"数据库连接失败: {str(e)}")
            raise

    def close(self):
        """关闭数据库连接"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
            if self.logger:
                self.logger.info("db_manager", "数据库连接已关闭")
        except Exception as e:
            if self.logger:
                self.logger.error("db_manager", f"关闭数据库连接失败: {str(e)}")

    def _reconnect(self):
        """重新连接数据库"""
        if self.logger:
            self.logger.warning("db_manager", "尝试重新连接数据库")
        self.close()
        self.connect()

    def upsert_product(self, product: ProductDTO) -> int:
        """
        插入或更新商品信息

        Args:
            product: 商品DTO对象

        Returns:
            商品数据库ID
        """
        try:
            # 先查询是否存在
            sql_select = "SELECT id FROM products WHERE product_id = %s"
            self.cursor.execute(sql_select, (product.product_id,))
            result = self.cursor.fetchone()

            if result:
                # 更新现有记录
                product_db_id = result[0]
                sql_update = """
                    UPDATE products
                    SET title = %s, product_url = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """
                self.cursor.execute(sql_update, (product.title, product.product_url, product_db_id))
            else:
                # 插入新记录
                sql_insert = """
                    INSERT INTO products (product_id, title, product_url)
                    VALUES (%s, %s, %s)
                """
                self.cursor.execute(sql_insert, (product.product_id, product.title, product.product_url))
                product_db_id = self.cursor.lastrowid

            self.connection.commit()
            return product_db_id

        except Exception as e:
            self.connection.rollback()
            if self.logger:
                self.logger.error("db_manager", f"插入商品失败: {str(e)}", product.product_url)
            raise

    def insert_sku(self, sku: SkuDTO) -> int:
        """
        插入SKU信息

        Args:
            sku: SKU DTO对象

        Returns:
            SKU数据库ID
        """
        try:
            sql = """
                INSERT INTO skus (product_db_id, sku_name, price, sku_url)
                VALUES (%s, %s, %s, %s)
            """
            self.cursor.execute(sql, (sku.product_db_id, sku.sku_name, sku.price, sku.sku_url))
            self.connection.commit()
            return self.cursor.lastrowid

        except Exception as e:
            self.connection.rollback()
            if self.logger:
                self.logger.error("db_manager", f"插入SKU失败: {str(e)}")
            raise

    def insert_price_history(self, sku_id: int, price: Decimal):
        """
        记录价格历史

        Args:
            sku_id: SKU数据库ID
            price: 价格
        """
        try:
            sql = """
                INSERT INTO price_history (sku_id, price)
                VALUES (%s, %s)
            """
            self.cursor.execute(sql, (sku_id, price))
            self.connection.commit()

        except Exception as e:
            self.connection.rollback()
            if self.logger:
                self.logger.error("db_manager", f"插入价格历史失败: {str(e)}")
            raise

    def insert_log(self, log_level: str, message: str, product_url: Optional[str] = None):
        """
        插入日志记录

        Args:
            log_level: 日志级别
            message: 日志消息
            product_url: 相关商品链接（可选）
        """
        try:
            sql = """
                INSERT INTO crawl_logs (log_level, message, product_url)
                VALUES (%s, %s, %s)
            """
            self.cursor.execute(sql, (log_level, message, product_url))
            self.connection.commit()

        except Exception as e:
            self.connection.rollback()
            # 日志插入失败不抛出异常，避免影响主流程
            pass
