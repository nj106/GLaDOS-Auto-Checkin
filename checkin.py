import os
import json
import time
import random
import requests
from pypushdeer import PushDeer

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
TIMEOUT = 10

def push_deer(sckey: str, title: str, text: str):
    if sckey:
        PushDeer(pushkey=sckey).send_text(title, desp=text)

def push_serverchan(sendkey: str, title: str, content: str):
    if not sendkey:
        return
    url = f"https://sctapi.ftqq.com/{sendkey}.send"
    data = {"title": title, "desp": content}
    try:
        resp = requests.post(url, data=data, timeout=TIMEOUT)
        if resp.status_code == 200:
            result = resp.json()
            if result.get("code") == 0:
                print("✅ Server 酱推送成功")
            else:
                print(f"⚠️ Server 酱推送失败: {result.get('message')}")
        else:
            print(f"⚠️ Server 酱推送失败: HTTP {resp.status_code}")
    except Exception as e:
        print(f"⚠️ Server 酱推送异常: {e}")

def push_all(sendkey_deer: str, sendkey_sc: str, title: str, content: str):
    if sendkey_deer:
        push_deer(sendkey_deer, title, content)
    if sendkey_sc:
        push_serverchan(sendkey_sc, title, content)
    if not sendkey_deer and not sendkey_sc:
        print("⚠️ 未配置任何推送服务")

def safe_json(resp):
    try:
        return resp.json()
    except Exception:
        return {}

def get_points_from_data(data):
    """从 status 接口的 data 字典中提取积分，支持多种字段名"""
    for key in ["points", "point", "total_points", "balance"]:
        if key in data and data[key] is not None:
            return data[key]
    return None

def main():
    sendkey_deer = os.getenv("SENDKEY", "")
    sendkey_sc = os.getenv("SERVERCHAN_KEY", "")
    cookies_env = os.getenv("COOKIES", "")
    cookies = [c.strip() for c in cookies_env.split("&") if c.strip()]

    if not cookies:
        push_all(sendkey_deer, sendkey_sc, "GLaDOS 签到", "❌ 未检测到 COOKIES")
        return

    session = requests.Session()
    ok = fail = repeat = 0
    lines = []

    for idx, cookie in enumerate(cookies, 1):
        headers = dict(HEADERS_BASE)
        headers["cookie"] = cookie

        email = "unknown"
        points = "-"
        days = "-"

        try:
            # 签到请求
            r = session.post(
                CHECKIN_URL,
                headers=headers,
                data=json.dumps(PAYLOAD),
                timeout=TIMEOUT,
            )
            j = safe_json(r)
            msg = j.get("message", "")
            msg_lower = msg.lower()

            if "got" in msg_lower:
                ok += 1
                # 签到接口可能返回本次获得点数，但不一定包含总计，所以还是依赖 status 接口
                status = "✅ 成功"
            elif "repeat" in msg_lower or "already" in msg_lower:
                repeat += 1
                status = "🔁 已签到"
            else:
                fail += 1
                status = "❌ 失败"

            # 状态接口（获取积分和剩余天数）
            s = session.get(STATUS_URL, headers=headers, timeout=TIMEOUT)
            sj_raw = safe_json(s)
            sj = sj_raw.get("data") or {}

            # 提取邮箱
            if sj.get("email"):
                email = sj["email"]

            # 剩余天数
            if sj.get("leftDays") is not None:
                days = f"{int(float(sj['leftDays']))} 天"

            # 积分（使用增强提取函数）
            points_val = get_points_from_data(sj)
            if points_val is not None:
                points = points_val
            else:
                # 如果找不到，打印警告（仅第一次）
                if idx == 1:
                    print(f"⚠️ 未在状态响应中找到积分字段，响应结构: {list(sj.keys())}")

        except Exception as e:
            fail += 1
            status = "❌ 异常"
            print(f"处理账号 {idx} 时出错: {e}")

        lines.append(f"{idx}. {email} | {status} | 积分:{points} | 剩余:{days}")
        time.sleep(random.uniform(1, 2))

    title = f"GLaDOS 签到完成 ✅{ok} ❌{fail} 🔁{repeat}"
    content = "\n".join(lines)
    print(content)
    push_all(sendkey_deer, sendkey_sc, title, content)

if __name__ == "__main__":
    main()