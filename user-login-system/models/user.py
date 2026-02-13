"""
用户模型 - 定义用户数据结构和数据库操作
"""
import mysql.connector
from mysql.connector import Error
from typing import Optional, Dict, Any
from datetime import datetime
from config import Config


class User:
    """用户模型类"""
    
    def __init__(self, id: int = None, username: str = None, 
                 password_hash: str = None, email: str = None,
                 created_at: datetime = None, updated_at: datetime = None):
        """
        初始化用户对象
        
        Args:
            id: 用户ID
            username: 用户名
            password_hash: 密码哈希值
            email: 邮箱地址
            created_at: 创建时间
            updated_at: 更新时间
        """
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.email = email
        self.created_at = created_at
        self.updated_at = updated_at
    
    @staticmethod
    def get_connection():
        """
        获取数据库连接
        
        Returns:
            mysql.connector.connection.MySQLConnection: 数据库连接对象
        
        Raises:
            Error: 数据库连接错误
        """
        try:
            connection = mysql.connector.connect(**Config.get_mysql_config())
            return connection
        except Error as e:
            raise Error(f"数据库连接失败: {str(e)}")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将用户对象转换为字典
        
        Returns:
            Dict: 用户信息字典
        """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def create(cls, username: str, password_hash: str, email: str = None) -> 'User':
        """
        创建新用户
        
        Args:
            username: 用户名
            password_hash: 密码哈希值
            email: 邮箱地址（可选）
        
        Returns:
            User: 新创建的用户对象
        
        Raises:
            ValueError: 用户名已存在
            Error: 数据库操作错误
        """
        connection = None
        cursor = None
        try:
            connection = cls.get_connection()
            cursor = connection.cursor()
            
            # 检查用户名是否已存在
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                raise ValueError("用户名已存在")
            
            # 插入新用户
            sql = "INSERT INTO users (username, password_hash, email) VALUES (%s, %s, %s)"
            cursor.execute(sql, (username, password_hash, email))
            connection.commit()
            
            user_id = cursor.lastrowid
            return cls(id=user_id, username=username, email=email)
            
        except ValueError:
            raise
        except Error as e:
            if connection:
                connection.rollback()
            raise Error(f"创建用户失败: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    @classmethod
    def find_by_username(cls, username: str) -> Optional['User']:
        """
        根据用户名查找用户
        
        Args:
            username: 用户名
        
        Returns:
            User: 用户对象，如果不存在则返回None
        """
        connection = None
        cursor = None
        try:
            connection = cls.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute(
                "SELECT id, username, password_hash, email, created_at, updated_at "
                "FROM users WHERE username = %s", 
                (username,)
            )
            row = cursor.fetchone()
            
            if row:
                return cls(**row)
            return None
            
        except Error as e:
            raise Error(f"查询用户失败: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    @classmethod
    def find_by_id(cls, user_id: int) -> Optional['User']:
        """
        根据用户ID查找用户
        
        Args:
            user_id: 用户ID
        
        Returns:
            User: 用户对象，如果不存在则返回None
        """
        connection = None
        cursor = None
        try:
            connection = cls.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute(
                "SELECT id, username, password_hash, email, created_at, updated_at "
                "FROM users WHERE id = %s", 
                (user_id,)
            )
            row = cursor.fetchone()
            
            if row:
                return cls(**row)
            return None
            
        except Error as e:
            raise Error(f"查询用户失败: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    @classmethod
    def log_login(cls, user_id: int, username: str, ip_address: str, 
                  user_agent: str, status: str, message: str = None):
        """
        记录登录日志
        
        Args:
            user_id: 用户ID（失败时可为None）
            username: 用户名
            ip_address: IP地址
            user_agent: 浏览器标识
            status: 登录状态（success/failed）
            message: 消息
        """
        connection = None
        cursor = None
        try:
            connection = cls.get_connection()
            cursor = connection.cursor()
            
            sql = """INSERT INTO login_logs 
                     (user_id, username, ip_address, user_agent, status, message) 
                     VALUES (%s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (user_id, username, ip_address, user_agent, status, message))
            connection.commit()
            
        except Error:
            # 日志记录失败不影响主流程
            pass
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
