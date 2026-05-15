import os
import json
import time
import random
import requests
from pypushdeer import PushDeer
from urllib.parse import quote

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

# 推送相关函数 (保持不变)
def push_deer(sckey: str, title: str, text: str):
    """推送消息到 PushDeer"""
    if sckey:
        PushDeer(pushkey=sckey).send_text(title, desp=text)

def push_serverchan(sendkey: str, title: str, content: str):
    """推送消息到 Server 酱 (Turbo 版)"""
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
    """推送到所有配置的服务"""
    if sendkey_deer:
        push_deer(sendkey_deer, title, content)
    if sendkey_sc:
        push_serverchan(sendkey_sc, title, content)
    if not sendkey_deer and not sendkey_sc:
        print("⚠️ 未配置任何推送服务，请在 Secrets 中配置 SENDKEY 或 SERVERCHAN_KEY")

def safe_json(resp):
    try:
        return resp.json()
    except Exception:
        return {}

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
            # --- 1. 执行签到操作 ---
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
                points = j.get("points", "-")  # 签到成功时，返回结果中可能包含本次增加/总计积分，但这里先用j.get获取，不过更可靠的数据在后面状态接口中
                status = "✅ 成功"
            elif "repeat" in msg_lower or "already" in msg_lower:
                repeat += 1
                status = "🔁 已签到"
            else:
                fail += 1
                status = "❌ 失败"

            # --- 2. 查询用户状态 (包含总积分) ---
            s = session.get(STATUS_URL, headers=headers, timeout=TIMEOUT)
            sj = safe_json(s).get("data") or {}

            # 更新从状态接口获取的邮箱、天数和总积分
            email = sj.get("email", email)
            if sj.get("leftDays") is not None:
                days = f"{int(float(sj['leftDays']))} 天"
            if sj.get("points") is not None:
                points = sj.get("points")  # 👈 这里获取总积分

        except Exception:
            fail += 1
            status = "❌ 异常"

        lines.append(f"{idx}. {email} | {status} | 积分:{points} | 剩余:{days}")
        time.sleep(random.uniform(1, 2))

    title = f"GLaDOS 签到完成 ✅{ok} ❌{fail} 🔁{repeat}"
    content = "\n".join(lines)

    print(content)
    push_all(sendkey_deer, sendkey_sc, title, content)

if __name__ == "__main__":
    main()