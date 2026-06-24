#!/usr/bin/env python3
"""
本地测试脚本 - 用于快速诊断 GLaDOS 签到问题
直接在本地运行: python3 test_checkin.py
"""

import os
import json
import sys

# 从环境变量或提示获取 Cookie
cookie = os.getenv("COOKIES", "").strip()
if not cookie:
    print("❌ 未找到 COOKIES 环境变量")
    print("\n使用方法:")
    print("  export COOKIES='你的cookie'")
    print("  python3 test_checkin.py")
    print("\n或者直接运行 checkin.py:")
    print("  COOKIES='你的cookie' python3 checkin.py")
    sys.exit(1)

import requests

CHECKIN_URL = "https://glados.cloud/api/user/checkin"
STATUS_URL = "https://glados.cloud/api/user/status"

HEADERS_BASE = {
    "origin": "https://glados.cloud",
    "referer": "https://glados.cloud/console/checkin",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "content-type": "application/json;charset=UTF-8",
}

PAYLOAD = {"token": "glados.cloud"}

print("\n" + "="*60)
print("🔍 GLaDOS 签到诊断测试")
print("="*60 + "\n")

headers = dict(HEADERS_BASE)
headers["cookie"] = cookie

print(f"📝 Cookie 长度: {len(cookie)} 字符")
print(f"📝 Cookie 前50字符: {cookie[:50]}...")

# 测试签到接口
print("\n" + "-"*60)
print("🔄 测试签到接口...")
print("-"*60)

try:
    r = requests.post(
        CHECKIN_URL,
        headers=headers,
        data=json.dumps(PAYLOAD),
        timeout=10,
    )
    
    print(f"✅ HTTP 状态码: {r.status_code}")
    print(f"📄 响应内容:\n{r.text}\n")
    
    try:
        j = r.json()
        msg = j.get("message", "")
        print(f"📋 解析结果:")
        print(f"   - message: {msg}")
        print(f"   - status: {j.get('status', 'N/A')}")
        print(f"   - points: {j.get('points', 'N/A')}")
        
        msg_lower = msg.lower()
        if "got" in msg_lower:
            print(f"\n✅ 签到成功！")
        elif "repeat" in msg_lower or "already" in msg_lower:
            print(f"\n🔁 已签到过了")
        else:
            print(f"\n❌ 签到失败，返回信息: {msg}")
            
    except json.JSONDecodeError:
        print("❌ 无法解析 JSON 响应")
        
except requests.exceptions.RequestException as e:
    print(f"❌ 请求异常: {e}")

# 测试状态接口
print("\n" + "-"*60)
print("🔄 测试状态接口...")
print("-"*60)

try:
    s = requests.get(STATUS_URL, headers=headers, timeout=10)
    
    print(f"✅ HTTP 状态码: {s.status_code}")
    print(f"📄 响应内容:\n{s.text}\n")
    
    try:
        sj = s.json()
        data = sj.get("data", {})
        print(f"📋 解析结果:")
        print(f"   - email: {data.get('email', 'N/A')}")
        print(f"   - leftDays: {data.get('leftDays', 'N/A')}")
        print(f"   - status: {sj.get('status', 'N/A')}")
        
    except json.JSONDecodeError:
        print("❌ 无法解析 JSON 响应")
        
except requests.exceptions.RequestException as e:
    print(f"❌ 请求异常: {e}")

print("\n" + "="*60)
print("✅ 诊断完成")
print("="*60 + "\n")
