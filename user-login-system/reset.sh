#!/bin/bash
# 重置所有服务并重新初始化

echo "============================================"
echo "用户登录系统 - 环境重置"
echo "============================================"

echo "警告: 这将删除所有数据！"
read -p "确定要继续吗? (y/N): " confirm

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "已取消"
    exit 0
fi

echo ""
echo "1. 停止所有服务..."
docker compose down

echo ""
echo "2. 删除数据卷..."
docker volume rm user-login-system_mysql_data 2>/dev/null || true
docker volume rm user-login-system_redis_data 2>/dev/null || true

echo ""
echo "3. 重新启动服务..."
docker compose up -d

echo ""
echo "4. 等待 MySQL 就绪..."
sleep 10

echo ""
echo "5. 初始化数据库..."
docker exec -i user_login_mysql mysql -uroot -proot123 < init_db.sql

echo ""
echo "============================================"
echo "✓ 环境重置完成！"
echo "============================================"
echo "访问地址: http://localhost:5000/"
echo ""
