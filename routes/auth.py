"""
认证路由模块 - 处理用户认证相关的API请求
"""
from flask import Blueprint, request, jsonify
from services.user_service import UserService
from utils.auth import extract_token_from_header

# 创建认证蓝图
auth_bp = Blueprint('auth', __name__, url_prefix='/api')


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    用户注册 API
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请求体不能为空',
                'data': None
            }), 400
        
        # 使用 or '' 确保处理 None 值（前端可能发送 null）
        username = (data.get('username') or '').strip()
        password = data.get('password') or ''
        email = (data.get('email') or '').strip() or None
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': '用户名和密码不能为空',
                'data': None
            }), 400
        
        result = UserService.register(username, password, email)
        
        status_code = 201 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}',
            'data': None
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    用户登录 API（带失败次数限制）
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请求体不能为空',
                'data': None
            }), 400
        
        # 使用 or '' 确保处理 None 值
        username = (data.get('username') or '').strip()
        password = data.get('password') or ''
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': '用户名和密码不能为空',
                'data': None
            }), 400
        
        # 获取客户端信息
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')
        
        result = UserService.login(username, password, ip_address, user_agent)
        
        status_code = 200 if result['success'] else 401
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}',
            'data': None
        }), 500


@auth_bp.route('/verify', methods=['GET'])
def verify():
    """
    会话验证 API
    """
    try:
        auth_header = request.headers.get('Authorization', '')
        success, token_or_msg = extract_token_from_header(auth_header)
        
        if not success:
            return jsonify({
                'success': False,
                'message': token_or_msg,
                'data': None
            }), 401
        
        result = UserService.verify_session(token_or_msg)
        
        status_code = 200 if result['success'] else 401
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}',
            'data': None
        }), 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    用户登出 API
    """
    try:
        auth_header = request.headers.get('Authorization', '')
        success, token_or_msg = extract_token_from_header(auth_header)
        
        if not success:
            return jsonify({
                'success': False,
                'message': token_or_msg,
                'data': None
            }), 401
        
        result = UserService.logout(token_or_msg)
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}',
            'data': None
        }), 500


@auth_bp.route('/user/info', methods=['GET'])
def user_info():
    """
    获取用户信息 API
    """
    try:
        auth_header = request.headers.get('Authorization', '')
        success, token_or_msg = extract_token_from_header(auth_header)
        
        if not success:
            return jsonify({
                'success': False,
                'message': token_or_msg,
                'data': None
            }), 401
        
        # 验证会话
        session_result = UserService.verify_session(token_or_msg)
        
        if not session_result['success']:
            return jsonify(session_result), 401
        
        # 获取用户信息
        user_id = session_result['data']['user_id']
        result = UserService.get_user_info(user_id)
        
        status_code = 200 if result['success'] else 404
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}',
            'data': None
        }), 500


@auth_bp.route('/health', methods=['GET'])
def health_check():
    """
    健康检查 API
    """
    return jsonify({
        'success': True,
        'message': '服务正常',
        'data': {
            'status': 'healthy'
        }
    }), 200
