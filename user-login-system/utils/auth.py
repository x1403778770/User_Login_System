"""
认证工具模块 - 密码加密、Token生成等
"""
import bcrypt
import uuid
import re
from typing import Tuple


def hash_password(password: str) -> str:
    """
    使用bcrypt对密码进行哈希加密
    
    Args:
        password: 明文密码
    
    Returns:
        str: 哈希后的密码字符串
    """
    # 生成盐并哈希密码
    salt = bcrypt.gensalt(rounds=12)  # rounds=12 提供4096次迭代
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """
    验证密码是否匹配哈希值
    
    Args:
        password: 明文密码
        password_hash: 存储的哈希密码
    
    Returns:
        bool: 密码是否匹配
    """
    try:
        return bcrypt.checkpw(
            password.encode('utf-8'), 
            password_hash.encode('utf-8')
        )
    except Exception:
        return False


def generate_token() -> str:
    """
    生成唯一的会话Token
    
    使用UUID4生成随机Token，具有较高的唯一性保证
    
    Returns:
        str: 36字符的UUID字符串
    """
    return str(uuid.uuid4())


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    验证密码强度
    
    要求：
    - 至少8个字符
    - 至少包含一个小写字母
    - 至少包含一个大写字母
    - 至少包含一个数字
    
    Args:
        password: 待验证的密码
    
    Returns:
        Tuple[bool, str]: (是否有效, 错误消息)
    """
    if len(password) < 8:
        return False, "密码长度至少8个字符"
    
    if not re.search(r'[a-z]', password):
        return False, "密码必须包含至少一个小写字母"
    
    if not re.search(r'[A-Z]', password):
        return False, "密码必须包含至少一个大写字母"
    
    if not re.search(r'\d', password):
        return False, "密码必须包含至少一个数字"
    
    return True, ""


def validate_username(username: str) -> Tuple[bool, str]:
    """
    验证用户名格式
    
    要求：
    - 3-20个字符
    - 只能包含字母、数字、下划线
    
    Args:
        username: 待验证的用户名
    
    Returns:
        Tuple[bool, str]: (是否有效, 错误消息)
    """
    if not username:
        return False, "用户名不能为空"
    
    if len(username) < 3 or len(username) > 20:
        return False, "用户名长度必须在3-20个字符之间"
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "用户名只能包含字母、数字和下划线"
    
    return True, ""


def validate_email(email: str) -> Tuple[bool, str]:
    """
    验证邮箱格式
    
    Args:
        email: 待验证的邮箱
    
    Returns:
        Tuple[bool, str]: (是否有效, 错误消息)
    """
    if not email:
        return True, ""  # 邮箱可选，空值有效
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "邮箱格式不正确"
    
    return True, ""


def extract_token_from_header(auth_header: str) -> Tuple[bool, str]:
    """
    从Authorization头中提取Token
    
    Args:
        auth_header: Authorization头的值
    
    Returns:
        Tuple[bool, str]: (是否成功, Token或错误消息)
    """
    if not auth_header:
        return False, "缺少Authorization头"
    
    parts = auth_header.split()
    
    if len(parts) != 2:
        return False, "Authorization头格式错误"
    
    if parts[0].lower() != 'bearer':
        return False, "Authorization类型必须是Bearer"
    
    return True, parts[1]
