#!/bin/bash
# 数据库初始化脚本 - 手动执行

echo "============================================"
echo "用户登录系统 - 数据库初始化"
echo "============================================"

# 检查 MySQL 容器是否运行
if ! docker ps | grep -q user_login_mysql; then
    echo "错误: MySQL 容器未运行"
    echo "请先执行: docker compose up -d mysql"
    exit 1
fi

echo "正在初始化数据库..."

# 执行初始化 SQL
docker exec -i user_login_mysql mysql -uroot -proot123 < init_db.sql

if [ $? -eq 0 ]; then
    echo "✓ 数据库初始化成功！"
    echo ""
    echo "已创建:"
    echo "  - 数据库: user_login_db"
    echo "  - 用户表: users"
    echo "  - 日志表: login_logs"
else
    echo "✗ 数据库初始化失败"
    exit 1
fi
