#!/usr/bin/env python3
"""
API 测试脚本 - 测试用户登录系统的所有功能
"""
import requests
import json
import time
import random
import string

# API 基础地址
BASE_URL = "http://localhost:5000/api"

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """打印标题"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text:^60}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'=' * 60}{Colors.RESET}\n")


def print_result(test_name, success, message="", data=None):
    """打印测试结果"""
    status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if success else f"{Colors.RED}✗ FAIL{Colors.RESET}"
    print(f"{status} - {test_name}")
    if message:
        print(f"    {Colors.YELLOW}消息: {message}{Colors.RESET}")
    if data:
        print(f"    数据: {json.dumps(data, ensure_ascii=False, indent=4)}")


def generate_random_username():
    """生成随机用户名"""
    return "test_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))


def test_health_check():
    """测试健康检查接口"""
    print_header("测试 1: 健康检查")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        data = response.json()
        
        success = response.status_code == 200 and data.get('success')
        print_result("健康检查", success, data.get('message'), data)
        return success
    except Exception as e:
        print_result("健康检查", False, str(e))
        return False


def test_register():
    """测试用户注册"""
    print_header("测试 2: 用户注册")
    
    username = generate_random_username()
    password = "TestPass123!"
    email = f"{username}@test.com"
    
    # 测试正常注册
    print(f"注册用户: {username}")
    
    try:
        response = requests.post(f"{BASE_URL}/register", json={
            "username": username,
            "password": password,
            "email": email
        })
        data = response.json()
        
        success = response.status_code == 201 and data.get('success')
        print_result("正常注册", success, data.get('message'), data.get('data'))
        
        # 测试重复注册
        if success:
            response2 = requests.post(f"{BASE_URL}/register", json={
                "username": username,
                "password": password
            })
            data2 = response2.json()
            
            is_duplicate_blocked = not data2.get('success') and '已存在' in data2.get('message', '')
            print_result("重复注册被拒绝", is_duplicate_blocked, data2.get('message'))
        
        # 测试弱密码
        response3 = requests.post(f"{BASE_URL}/register", json={
            "username": generate_random_username(),
            "password": "weak"
        })
        data3 = response3.json()
        
        is_weak_blocked = not data3.get('success')
        print_result("弱密码被拒绝", is_weak_blocked, data3.get('message'))
        
        return username, password if success else None
        
    except Exception as e:
        print_result("用户注册", False, str(e))
        return None, None


def test_login(username, password):
    """测试用户登录"""
    print_header("测试 3: 用户登录")
    
    if not username or not password:
        print_result("用户登录", False, "没有有效的测试用户")
        return None
    
    try:
        # 测试正确密码登录
        print(f"登录用户: {username}")
        
        response = requests.post(f"{BASE_URL}/login", json={
            "username": username,
            "password": password
        })
        data = response.json()
        
        success = response.status_code == 200 and data.get('success')
        print_result("正确密码登录", success, data.get('message'), data.get('data'))
        
        token = data.get('data', {}).get('token') if success else None
        
        # 测试错误密码登录
        response2 = requests.post(f"{BASE_URL}/login", json={
            "username": username,
            "password": "WrongPassword123!"
        })
        data2 = response2.json()
        
        is_wrong_blocked = not data2.get('success')
        remaining = data2.get('data', {}).get('remaining_attempts', 0)
        print_result("错误密码被拒绝", is_wrong_blocked, 
                    f"{data2.get('message')} (剩余尝试: {remaining})")
        
        return token
        
    except Exception as e:
        print_result("用户登录", False, str(e))
        return None


def test_verify(token):
    """测试会话验证"""
    print_header("测试 4: 会话验证")
    
    if not token:
        print_result("会话验证", False, "没有有效的Token")
        return False
    
    try:
        # 测试有效Token
        response = requests.get(f"{BASE_URL}/verify", headers={
            "Authorization": f"Bearer {token}"
        })
        data = response.json()
        
        success = response.status_code == 200 and data.get('success')
        print_result("有效Token验证", success, data.get('message'), data.get('data'))
        
        # 测试无效Token
        response2 = requests.get(f"{BASE_URL}/verify", headers={
            "Authorization": "Bearer invalid-token-12345"
        })
        data2 = response2.json()
        
        is_invalid_blocked = not data2.get('success')
        print_result("无效Token被拒绝", is_invalid_blocked, data2.get('message'))
        
        # 测试无Token请求
        response3 = requests.get(f"{BASE_URL}/verify")
        data3 = response3.json()
        
        is_no_token_blocked = not data3.get('success')
        print_result("无Token被拒绝", is_no_token_blocked, data3.get('message'))
        
        return success
        
    except Exception as e:
        print_result("会话验证", False, str(e))
        return False


def test_user_info(token):
    """测试获取用户信息"""
    print_header("测试 5: 获取用户信息")
    
    if not token:
        print_result("获取用户信息", False, "没有有效的Token")
        return False
    
    try:
        response = requests.get(f"{BASE_URL}/user/info", headers={
            "Authorization": f"Bearer {token}"
        })
        data = response.json()
        
        success = response.status_code == 200 and data.get('success')
        print_result("获取用户信息", success, data.get('message'), data.get('data'))
        
        return success
        
    except Exception as e:
        print_result("获取用户信息", False, str(e))
        return False


def test_logout(token):
    """测试用户登出"""
    print_header("测试 6: 用户登出")
    
    if not token:
        print_result("用户登出", False, "没有有效的Token")
        return False
    
    try:
        response = requests.post(f"{BASE_URL}/logout", headers={
            "Authorization": f"Bearer {token}"
        })
        data = response.json()
        
        success = response.status_code == 200 and data.get('success')
        print_result("用户登出", success, data.get('message'))
        
        # 验证Token已失效
        if success:
            response2 = requests.get(f"{BASE_URL}/verify", headers={
                "Authorization": f"Bearer {token}"
            })
            data2 = response2.json()
            
            is_token_invalid = not data2.get('success')
            print_result("登出后Token失效", is_token_invalid, data2.get('message'))
        
        return success
        
    except Exception as e:
        print_result("用户登出", False, str(e))
        return False


def test_login_lockout(username):
    """测试登录锁定功能"""
    print_header("测试 7: 登录失败锁定")
    
    if not username:
        # 注册一个新用户用于测试
        result = test_register()
        if result[1]:
            username = result[0]
        else:
            print_result("登录锁定测试", False, "无法创建测试用户")
            return False
    
    print(f"测试用户: {username}")
    print("尝试连续5次错误登录...")
    
    try:
        for i in range(5):
            response = requests.post(f"{BASE_URL}/login", json={
                "username": username,
                "password": f"WrongPass{i}!"
            })
            data = response.json()
            remaining = data.get('data', {}).get('remaining_attempts', 0)
            print(f"  第{i+1}次失败登录 - 剩余尝试次数: {remaining}")
        
        # 第6次尝试应该被锁定
        response = requests.post(f"{BASE_URL}/login", json={
            "username": username,
            "password": "WrongPassAgain!"
        })
        data = response.json()
        
        is_locked = data.get('data', {}).get('locked', False)
        print_result("账户被锁定", is_locked, data.get('message'))
        
        if is_locked:
            remaining_seconds = data.get('data', {}).get('remaining_seconds', 0)
            print(f"    锁定剩余时间: {remaining_seconds} 秒")
        
        return is_locked
        
    except Exception as e:
        print_result("登录锁定测试", False, str(e))
        return False


def run_all_tests():
    """运行所有测试"""
    print(f"\n{Colors.BOLD}{'=' * 60}")
    print("用户登录系统 API 测试")
    print(f"{'=' * 60}{Colors.RESET}")
    print(f"API 地址: {BASE_URL}")
    print(f"时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # 1. 健康检查
    results.append(("健康检查", test_health_check()))
    
    # 2. 注册
    username, password = test_register()
    results.append(("用户注册", username is not None))
    
    # 3. 登录
    token = test_login(username, password)
    results.append(("用户登录", token is not None))
    
    # 4. 会话验证
    results.append(("会话验证", test_verify(token)))
    
    # 5. 获取用户信息
    results.append(("获取用户信息", test_user_info(token)))
    
    # 6. 登出
    results.append(("用户登出", test_logout(token)))
    
    # 7. 登录锁定测试（使用新用户）
    results.append(("登录锁定", test_login_lockout(None)))
    
    # 打印汇总
    print_header("测试结果汇总")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = f"{Colors.GREEN}✓{Colors.RESET}" if result else f"{Colors.RED}✗{Colors.RESET}"
        print(f"  {status} {name}")
    
    print(f"\n{Colors.BOLD}总计: {passed}/{total} 测试通过{Colors.RESET}")
    
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}所有测试通过!{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}部分测试失败，请检查系统配置。{Colors.RESET}")


if __name__ == "__main__":
    run_all_tests()
