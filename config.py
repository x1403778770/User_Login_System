"""
配置文件 - MySQL/Redis 连接配置
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """应用配置类"""
    
    # Flask 配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # MySQL 配置
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'root123')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'user_login_db')
    
    # Redis 配置
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    
    # 安全配置
    MAX_LOGIN_ATTEMPTS = int(os.getenv('MAX_LOGIN_ATTEMPTS', 5))  # 最大登录尝试次数
    LOCK_TIME_SECONDS = int(os.getenv('LOCK_TIME_SECONDS', 900))  # 锁定时间（秒），默认15分钟
    SESSION_EXPIRE_SECONDS = int(os.getenv('SESSION_EXPIRE_SECONDS', 86400))  # 会话过期时间（秒），默认24小时
    
    # Redis Key 前缀
    REDIS_KEY_PREFIX = 'user_login:'
    
    @classmethod
    def get_mysql_config(cls):
        """获取MySQL连接配置"""
        return {
            'host': cls.MYSQL_HOST,
            'port': cls.MYSQL_PORT,
            'user': cls.MYSQL_USER,
            'password': cls.MYSQL_PASSWORD,
            'database': cls.MYSQL_DATABASE
        }
    
    @classmethod
    def get_redis_config(cls):
        """获取Redis连接配置"""
        return {
            'host': cls.REDIS_HOST,
            'port': cls.REDIS_PORT,
            'password': cls.REDIS_PASSWORD,
            'db': cls.REDIS_DB,
            'decode_responses': True  # 自动解码为字符串
        }
