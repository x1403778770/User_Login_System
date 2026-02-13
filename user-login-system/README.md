# 用户登录系统 + 会话管理系统

基于 **Python Flask** 的用户登录与会话管理系统，使用 **MySQL** 存储用户数据，使用 **Redis** 管理会话和登录限制。

## 功能特性

- ✅ **用户注册** - 支持用户名、密码、邮箱注册，密码使用 bcrypt 加密
- ✅ **用户登录** - 支持登录失败次数限制（5次失败后锁定15分钟）
- ✅ **会话管理** - 基于 Redis 的会话管理，支持会话验证
- ✅ **用户登出** - 会话销毁，Token 失效
- ✅ **前端演示** - 提供完整的 Web 界面演示
- ✅ **API 测试** - 提供自动化测试脚本

## 技术栈

| 组件 | 技术 |
|------|------|
| 后端框架 | Python Flask 3.0 |
| 数据库 | MySQL 8.0 |
| 缓存 | Redis 7 |
| 密码加密 | bcrypt |
| 容器化 | Docker + Docker Compose |

## 项目结构

```
user-login-system/
├── app.py                 # Flask 主应用
├── config.py              # 配置文件
├── models/
│   ├── __init__.py
│   └── user.py            # 用户模型
├── routes/
│   ├── __init__.py
│   └── auth.py            # 认证路由
├── services/
│   ├── __init__.py
│   ├── user_service.py    # 用户业务逻辑
│   └── session_service.py # 会话管理逻辑
├── utils/
│   ├── __init__.py
│   └── auth.py            # 认证工具
├── templates/
│   └── index.html         # 前端演示页面
├── requirements.txt       # Python 依赖
├── init_db.sql            # 数据库初始化脚本
├── test_api.py            # API 测试脚本
├── Dockerfile             # Docker 构建文件
├── docker-compose.yml     # Docker Compose 配置
├── .env.example           # 环境变量示例
└── README.md              # 项目说明
```

## 快速开始

### 方式一：Docker Compose（推荐）

```bash
# 1. 进入项目目录
cd user-login-system

# 2. 启动所有服务
docker-compose up -d

# 3. 查看日志
docker-compose logs -f app

# 4. 访问应用
# 前端页面: http://localhost:5000/
# API 地址: http://localhost:5000/api/
```

### 方式二：本地运行

#### 1. 安装依赖

```bash
# 安装 Python 依赖
pip install -r requirements.txt
```

#### 2. 配置环境

```bash
# 复制环境变量示例
cp .env.example .env

# 编辑配置文件，修改数据库连接信息
vim .env
```

#### 3. 初始化数据库

```bash
# 连接 MySQL 执行初始化脚本
mysql -u root -p < init_db.sql

# 或者手动在 MySQL 中执行 init_db.sql 的内容
```

#### 4. 启动 Redis

```bash
# 使用 Docker 启动 Redis
docker run -d --name redis -p 6379:6379 redis:7-alpine

# 或者使用本地 Redis 服务
redis-server
```

#### 5. 启动应用

```bash
python app.py
```

## API 文档

### 1. 用户注册

**POST** `/api/register`

请求体：
```json
{
    "username": "testuser",
    "password": "TestPass123!",
    "email": "user@example.com"
}
```

响应：
```json
{
    "success": true,
    "message": "注册成功",
    "data": {
        "user_id": 1,
        "username": "testuser"
    }
}
```

### 2. 用户登录

**POST** `/api/login`

请求体：
```json
{
    "username": "testuser",
    "password": "TestPass123!"
}
```

响应：
```json
{
    "success": true,
    "message": "登录成功",
    "data": {
        "token": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "expires_in": 86400,
        "user_id": 1,
        "username": "testuser"
    }
}
```

### 3. 会话验证

**GET** `/api/verify`

请求头：
```
Authorization: Bearer {token}
```

响应：
```json
{
    "success": true,
    "message": "会话有效",
    "data": {
        "user_id": 1,
        "username": "testuser"
    }
}
```

### 4. 用户登出

**POST** `/api/logout`

请求头：
```
Authorization: Bearer {token}
```

响应：
```json
{
    "success": true,
    "message": "登出成功"
}
```

### 5. 获取用户信息

**GET** `/api/user/info`

请求头：
```
Authorization: Bearer {token}
```

响应：
```json
{
    "success": true,
    "message": "获取成功",
    "data": {
        "id": 1,
        "username": "testuser",
        "email": "user@example.com",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00"
    }
}
```

### 6. 健康检查

**GET** `/api/health`

响应：
```json
{
    "success": true,
    "message": "服务正常",
    "data": {
        "status": "healthy"
    }
}
```

## 运行测试

```bash
# 确保服务已启动
python test_api.py
```

测试内容：
1. 健康检查
2. 用户注册
3. 用户登录（正确/错误密码）
4. 会话验证
5. 获取用户信息
6. 用户登出
7. 登录失败锁定测试

## 配置说明

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| MYSQL_HOST | localhost | MySQL 主机地址 |
| MYSQL_PORT | 13306 | MySQL 端口 |
| MYSQL_USER | root | MySQL 用户名 |
| MYSQL_PASSWORD | root123 | MySQL 密码 |
| MYSQL_DATABASE | user_login_db | 数据库名称 |
| REDIS_HOST | localhost | Redis 主机地址 |
| REDIS_PORT | 16379 | Redis 端口 |
| MAX_LOGIN_ATTEMPTS | 5 | 最大登录尝试次数 |
| LOCK_TIME_SECONDS | 900 | 账户锁定时间（秒） |
| SESSION_EXPIRE_SECONDS | 86400 | 会话过期时间（秒） |

## 安全特性

1. **密码加密** - 使用 bcrypt 进行密码哈希，rounds=12
2. **登录限制** - 连续5次失败后锁定账户15分钟
3. **会话管理** - Token 存储在 Redis 中，支持自动过期
4. **输入验证** - 用户名、密码、邮箱格式验证
5. **CORS 配置** - 支持跨域请求配置

## 常见问题

### Q: 数据库连接失败？

检查 MySQL 服务是否启动，以及 `.env` 文件中的配置是否正确。

```bash
# 测试 MySQL 连接
mysql -h localhost -u root -p
```

### Q: Redis 连接失败？

检查 Redis 服务是否启动。

```bash
# 测试 Redis 连接
redis-cli ping
```

### Q: 如何重置用户密码？

目前需要直接操作数据库：

```sql
-- 查看用户
SELECT * FROM users;

-- 删除用户后重新注册
DELETE FROM users WHERE username = 'testuser';
```

## 许可证

MIT License
