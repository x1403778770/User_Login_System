"""
会话服务模块 - 处理Redis会话管理和登录限制
"""
import redis
import json
from typing import Optional, Dict, Any
from config import Config
from utils.auth import generate_token


class SessionService:
    """
    会话服务类 - 管理用户会话和登录限制
    
    Redis 数据结构:
    - session:{token} -> {user_id, username} (TTL: 24小时)
    - login_failed:{username} -> 失败次数 (TTL: 15分钟)
    - login_locked:{username} -> 锁定时间戳 (TTL: 15分钟)
    """
    
    _redis_client = None
    
    @classmethod
    def get_redis(cls):
        """
        获取Redis连接（单例模式）
        
        Returns:
            redis.Redis: Redis客户端实例
        """
        if cls._redis_client is None:
            cls._redis_client = redis.Redis(**Config.get_redis_config())
        return cls._redis_client
    
    @classmethod
    def create_session(cls, user_id: int, username: str) -> Dict[str, Any]:
        """
        创建新会话
        
        Args:
            user_id: 用户ID
            username: 用户名
        
        Returns:
            Dict: 包含token和过期时间的字典
        """
        redis_client = cls.get_redis()
        token = generate_token()
        session_key = f"{Config.REDIS_KEY_PREFIX}session:{token}"
        
        # 存储会话数据
        session_data = json.dumps({
            'user_id': user_id,
            'username': username
        })
        
        redis_client.setex(
            session_key,
            Config.SESSION_EXPIRE_SECONDS,
            session_data
        )
        
        return {
            'token': token,
            'expires_in': Config.SESSION_EXPIRE_SECONDS
        }
    
    @classmethod
    def get_session(cls, token: str) -> Optional[Dict[str, Any]]:
        """
        获取会话信息
        
        Args:
            token: 会话Token
        
        Returns:
            Dict: 会话数据（user_id, username），无效则返回None
        """
        redis_client = cls.get_redis()
        session_key = f"{Config.REDIS_KEY_PREFIX}session:{token}"
        
        session_data = redis_client.get(session_key)
        
        if session_data:
            return json.loads(session_data)
        return None
    
    @classmethod
    def delete_session(cls, token: str) -> bool:
        """
        删除会话（登出）
        
        Args:
            token: 会话Token
        
        Returns:
            bool: 是否成功删除
        """
        redis_client = cls.get_redis()
        session_key = f"{Config.REDIS_KEY_PREFIX}session:{token}"
        
        result = redis_client.delete(session_key)
        return result > 0
    
    @classmethod
    def refresh_session(cls, token: str) -> bool:
        """
        刷新会话过期时间
        
        Args:
            token: 会话Token
        
        Returns:
            bool: 是否成功刷新
        """
        redis_client = cls.get_redis()
        session_key = f"{Config.REDIS_KEY_PREFIX}session:{token}"
        
        if redis_client.exists(session_key):
            redis_client.expire(session_key, Config.SESSION_EXPIRE_SECONDS)
            return True
        return False
    
    # ==================== 登录限制相关方法 ====================
    
    @classmethod
    def is_locked(cls, username: str) -> Dict[str, Any]:
        """
        检查账户是否被锁定
        
        Args:
            username: 用户名
        
        Returns:
            Dict: {'locked': bool, 'remaining_seconds': int}
        """
        redis_client = cls.get_redis()
        lock_key = f"{Config.REDIS_KEY_PREFIX}login_locked:{username}"
        
        remaining_seconds = redis_client.ttl(lock_key)
        
        if remaining_seconds > 0:
            return {
                'locked': True,
                'remaining_seconds': remaining_seconds
            }
        
        return {
            'locked': False,
            'remaining_seconds': 0
        }
    
    @classmethod
    def lock_account(cls, username: str):
        """
        锁定账户
        
        Args:
            username: 用户名
        """
        redis_client = cls.get_redis()
        lock_key = f"{Config.REDIS_KEY_PREFIX}login_locked:{username}"
        
        redis_client.setex(
            lock_key,
            Config.LOCK_TIME_SECONDS,
            str(Config.MAX_LOGIN_ATTEMPTS)
        )
    
    @classmethod
    def get_failed_attempts(cls, username: str) -> int:
        """
        获取登录失败次数
        
        Args:
            username: 用户名
        
        Returns:
            int: 失败次数
        """
        redis_client = cls.get_redis()
        failed_key = f"{Config.REDIS_KEY_PREFIX}login_failed:{username}"
        
        attempts = redis_client.get(failed_key)
        return int(attempts) if attempts else 0
    
    @classmethod
    def increment_failed_attempts(cls, username: str) -> int:
        """
        增加登录失败次数
        
        Args:
            username: 用户名
        
        Returns:
            int: 当前的失败次数
        """
        redis_client = cls.get_redis()
        failed_key = f"{Config.REDIS_KEY_PREFIX}login_failed:{username}"
        
        # 使用管道确保原子性
        pipe = redis_client.pipeline()
        pipe.incr(failed_key)
        pipe.expire(failed_key, Config.LOCK_TIME_SECONDS)
        results = pipe.execute()
        
        return results[0]
    
    @classmethod
    def clear_failed_attempts(cls, username: str):
        """
        清除登录失败计数
        
        Args:
            username: 用户名
        """
        redis_client = cls.get_redis()
        failed_key = f"{Config.REDIS_KEY_PREFIX}login_failed:{username}"
        lock_key = f"{Config.REDIS_KEY_PREFIX}login_locked:{username}"
        
        redis_client.delete(failed_key, lock_key)
    
    @classmethod
    def get_remaining_attempts(cls, username: str) -> int:
        """
        获取剩余尝试次数
        
        Args:
            username: 用户名
        
        Returns:
            int: 剩余尝试次数
        """
        failed = cls.get_failed_attempts(username)
        return max(0, Config.MAX_LOGIN_ATTEMPTS - failed)
