"""
Flask 主应用 - 用户登录与会话管理系统
"""
import os
from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
from config import Config
from routes.auth import auth_bp


def create_app():
    """
    创建Flask应用实例
    
    Returns:
        Flask: Flask应用实例
    """
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # 加载配置
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    app.config['DEBUG'] = Config.DEBUG
    
    # 启用CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # 注册蓝图
    app.register_blueprint(auth_bp)
    
    # 主页路由 - 前端演示页面
    @app.route('/')
    def index():
        return render_template('index.html')
    
    # 静态文件路由
    @app.route('/static/<path:filename>')
    def static_files(filename):
        return send_from_directory('static', filename)
    
    # 全局错误处理
    @app.errorhandler(404)
    def not_found(error):
        return {
            'success': False,
            'message': '资源不存在',
            'data': None
        }, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {
            'success': False,
            'message': '服务器内部错误',
            'data': None
        }, 500
    
    return app


# 创建应用实例
app = create_app()


if __name__ == '__main__':
    print("=" * 60)
    print("用户登录与会话管理系统")
    print("=" * 60)
    print(f"MySQL Host: {Config.MYSQL_HOST}:{Config.MYSQL_PORT}")
    print(f"MySQL Database: {Config.MYSQL_DATABASE}")
    print(f"Redis Host: {Config.REDIS_HOST}:{Config.REDIS_PORT}")
    print(f"Max Login Attempts: {Config.MAX_LOGIN_ATTEMPTS}")
    print(f"Lock Time: {Config.LOCK_TIME_SECONDS} seconds")
    print(f"Session Expire: {Config.SESSION_EXPIRE_SECONDS} seconds")
    print("=" * 60)
    print("API Endpoints:")
    print("  POST /api/register - 用户注册")
    print("  POST /api/login    - 用户登录")
    print("  GET  /api/verify   - 会话验证")
    print("  POST /api/logout   - 用户登出")
    print("  GET  /api/user/info - 获取用户信息")
    print("  GET  /api/health   - 健康检查")
    print("=" * 60)
    print("前端演示页面: http://localhost:5000/")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
