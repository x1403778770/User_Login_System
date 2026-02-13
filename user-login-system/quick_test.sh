#!/bin/bash
# 快速 API 测试脚本

BASE_URL="http://localhost:5000/api"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "============================================"
echo "用户登录系统 API 快速测试"
echo "============================================"
echo ""

# 生成随机用户名
USERNAME="test_$(date +%s)"
PASSWORD="TestPass123!"

echo -e "${YELLOW}测试用户: $USERNAME${NC}"
echo ""

# 1. 健康检查
echo "----------------------------------------"
echo "1. 健康检查"
echo "----------------------------------------"
curl -s $BASE_URL/health | python3 -m json.tool 2>/dev/null || curl -s $BASE_URL/health
echo ""
echo ""

# 2. 用户注册
echo "----------------------------------------"
echo "2. 用户注册"
echo "----------------------------------------"
REGISTER_RESULT=$(curl -s -X POST $BASE_URL/register \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\",\"email\":\"$USERNAME@test.com\"}")
echo "$REGISTER_RESULT" | python3 -m json.tool 2>/dev/null || echo "$REGISTER_RESULT"
echo ""
echo ""

# 3. 用户登录
echo "----------------------------------------"
echo "3. 用户登录"
echo "----------------------------------------"
LOGIN_RESULT=$(curl -s -X POST $BASE_URL/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}")
echo "$LOGIN_RESULT" | python3 -m json.tool 2>/dev/null || echo "$LOGIN_RESULT"

# 提取 Token
TOKEN=$(echo "$LOGIN_RESULT" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
echo ""
echo ""

if [ -z "$TOKEN" ]; then
    echo -e "${RED}登录失败，无法继续测试${NC}"
    exit 1
fi

echo -e "${GREEN}Token 已获取: ${TOKEN:0:20}...${NC}"
echo ""

# 4. 会话验证
echo "----------------------------------------"
echo "4. 会话验证"
echo "----------------------------------------"
curl -s $BASE_URL/verify \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool 2>/dev/null || \
curl -s $BASE_URL/verify -H "Authorization: Bearer $TOKEN"
echo ""
echo ""

# 5. 获取用户信息
echo "----------------------------------------"
echo "5. 获取用户信息"
echo "----------------------------------------"
curl -s $BASE_URL/user/info \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool 2>/dev/null || \
curl -s $BASE_URL/user/info -H "Authorization: Bearer $TOKEN"
echo ""
echo ""

# 6. 错误密码测试
echo "----------------------------------------"
echo "6. 错误密码测试"
echo "----------------------------------------"
curl -s -X POST $BASE_URL/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"password\":\"WrongPass123!\"}" | python3 -m json.tool 2>/dev/null || \
curl -s -X POST $BASE_URL/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"password\":\"WrongPass123!\"}"
echo ""
echo ""

# 7. 用户登出
echo "----------------------------------------"
echo "7. 用户登出"
echo "----------------------------------------"
curl -s -X POST $BASE_URL/logout \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool 2>/dev/null || \
curl -s -X POST $BASE_URL/logout -H "Authorization: Bearer $TOKEN"
echo ""
echo ""

# 8. 验证登出后 Token 失效
echo "----------------------------------------"
echo "8. 验证登出后 Token 失效"
echo "----------------------------------------"
curl -s $BASE_URL/verify \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool 2>/dev/null || \
curl -s $BASE_URL/verify -H "Authorization: Bearer $TOKEN"
echo ""
echo ""

echo "============================================"
echo -e "${GREEN}测试完成！${NC}"
echo "============================================"
