"""
用户服务模块 - 处理用户相关的业务逻辑
"""
from typing import Dict, Any, Tuple
from models.user import User
from services.session_service import SessionService
from utils.auth import (
    hash_password, 
    verify_password, 
    validate_username, 
    validate_password_strength,
    validate_email
)
from config import Config


class UserService:
    """用户服务类 - 处理用户注册、登录等业务逻辑"""
    
    @staticmethod
    def register(username: str, password: str, email: str = None) -> Dict[str, Any]:
        """
        用户注册
        
        Args:
            username: 用户名
            password: 密码
            email: 邮箱（可选）
        
        Returns:
            Dict: 注册结果
        """
        # 验证用户名格式
        valid, msg = validate_username(username)
        if not valid:
            return {
                'success': False,
                'message': msg,
                'data': None
            }
        
        # 验证密码强度
        valid, msg = validate_password_strength(password)
        if not valid:
            return {
                'success': False,
                'message': msg,
                'data': None
            }
        
        # 验证邮箱格式
        if email:
            valid, msg = validate_email(email)
            if not valid:
                return {
                    'success': False,
                    'message': msg,
                    'data': None
                }
        
        try:
            # 哈希密码
            password_hash = hash_password(password)
            
            # 创建用户
            user = User.create(username, password_hash, email)
            
            return {
                'success': True,
                'message': '注册成功',
                'data': {
                    'user_id': user.id,
                    'username': user.username
                }
            }
            
        except ValueError as e:
            return {
                'success': False,
                'message': str(e),
                'data': None
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'注册失败: {str(e)}',
                'data': None
            }
    
    @staticmethod
    def login(username: str, password: str, ip_address: str = None, 
              user_agent: str = None) -> Dict[str, Any]:
        """
        用户登录（带失败次数限制）
        
        Args:
            username: 用户名
            password: 密码
            ip_address: IP地址
            user_agent: 浏览器标识
        
        Returns:
            Dict: 登录结果
        """
        # 检查账户是否被锁定
        lock_status = SessionService.is_locked(username)
        if lock_status['locked']:
            remaining_minutes = lock_status['remaining_seconds'] // 60
            remaining_seconds = lock_status['remaining_seconds'] % 60
            
            return {
                'success': False,
                'message': f'账户已锁定，请 {remaining_minutes} 分 {remaining_seconds} 秒后重试',
                'data': {
                    'locked': True,
                    'remaining_seconds': lock_status['remaining_seconds']
                }
            }
        
        # 查找用户
        user = User.find_by_username(username)
        
        if not user:
            # 用户不存在，记录失败（不透露用户是否存在）
            SessionService.increment_failed_attempts(username)
            remaining = SessionService.get_remaining_attempts(username)
            
            # 记录登录日志
            User.log_login(
                user_id=None,
                username=username,
                ip_address=ip_address,
                user_agent=user_agent,
                status='failed',
                message='用户不存在'
            )
            
            return {
                'success': False,
                'message': f'用户名或密码错误，剩余尝试次数: {remaining}',
                'data': {
                    'remaining_attempts': remaining
                }
            }
        
        # 验证密码
        if not verify_password(password, user.password_hash):
            # 密码错误，增加失败计数
            failed_attempts = SessionService.increment_failed_attempts(username)
            remaining = SessionService.get_remaining_attempts(username)
            
            # 记录登录日志
            User.log_login(
                user_id=user.id,
                username=username,
                ip_address=ip_address,
                user_agent=user_agent,
                status='failed',
                message=f'密码错误，第{failed_attempts}次失败'
            )
            
            # 检查是否需要锁定
            if failed_attempts >= Config.MAX_LOGIN_ATTEMPTS:
                SessionService.lock_account(username)
                return {
                    'success': False,
                    'message': f'登录失败次数过多，账户已锁定 {Config.LOCK_TIME_SECONDS // 60} 分钟',
                    'data': {
                        'locked': True,
                        'remaining_seconds': Config.LOCK_TIME_SECONDS
                    }
                }
            
            return {
                'success': False,
                'message': f'用户名或密码错误，剩余尝试次数: {remaining}',
                'data': {
                    'remaining_attempts': remaining
                }
            }
        
        # 登录成功
        # 清除失败计数
        SessionService.clear_failed_attempts(username)
        
        # 创建会话
        session = SessionService.create_session(user.id, user.username)
        
        # 记录登录日志
        User.log_login(
            user_id=user.id,
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            status='success',
            message='登录成功'
        )
        
        return {
            'success': True,
            'message': '登录成功',
            'data': {
                'token': session['token'],
                'expires_in': session['expires_in'],
                'user_id': user.id,
                'username': user.username
            }
        }
    
    @staticmethod
    def verify_session(token: str) -> Dict[str, Any]:
        """
        验证会话
        
        Args:
            token: 会话Token
        
        Returns:
            Dict: 验证结果
        """
        session = SessionService.get_session(token)
        
        if not session:
            return {
                'success': False,
                'message': '会话无效或已过期',
                'data': None
            }
        
        return {
            'success': True,
            'message': '会话有效',
            'data': {
                'user_id': session['user_id'],
                'username': session['username']
            }
        }
    
    @staticmethod
    def logout(token: str) -> Dict[str, Any]:
        """
        用户登出
        
        Args:
            token: 会话Token
        
        Returns:
            Dict: 登出结果
        """
        deleted = SessionService.delete_session(token)
        
        if deleted:
            return {
                'success': True,
                'message': '登出成功',
                'data': None
            }
        else:
            return {
                'success': False,
                'message': '会话不存在或已过期',
                'data': None
            }
    
    @staticmethod
    def get_user_info(user_id: int) -> Dict[str, Any]:
        """
        获取用户信息
        
        Args:
            user_id: 用户ID
        
        Returns:
            Dict: 用户信息
        """
        user = User.find_by_id(user_id)
        
        if not user:
            return {
                'success': False,
                'message': '用户不存在',
                'data': None
            }
        
        return {
            'success': True,
            'message': '获取成功',
            'data': user.to_dict()
        }
