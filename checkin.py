import os
import json
import time
import random
import hashlib
import hmac
import base64
import urllib.parse
import requests

# ---------- 配置 ----------
CHECKIN_URL = "https://glados.cloud/api/user/checkin"
STATUS_URL = "https://glados.cloud/api/user/status"
POINTS_URL = "https://glados.cloud/api/user/points"
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
TIMEOUT = 12


# ---------- 工具函数 ----------
def safe_json(resp):
    """安全解析 JSON 响应"""
    try:
        return resp.json()
    except Exception:
        return {}


# ---------- 推送函数 ----------
def push_deer(key, title, content):
    """推送到 PushDeer（直接调用 HTTP API，无需第三方库）
    API 文档: https://github.com/easychen/pushdeer
    接口地址: https://api2.pushdeer.com/message/push
    """
    if not key:
        return
    try:
        url = "https://api2.pushdeer.com/message/push"
        # type=text 时 text 为完整消息内容；避免 markdown 误解析 | 等符号
        data = {
            "pushkey": key,
            "text": f"{title}\n\n{content}",
            "type": "text",
        }
        r = requests.post(url, json=data, timeout=TIMEOUT)
        resp = safe_json(r)
        if r.ok and resp.get("code") == 0:
            print("✅ PushDeer 推送成功")
        else:
            print(f"⚠️ PushDeer 推送失败: {resp.get('message', r.text)}")
    except Exception as e:
        print(f"⚠️ PushDeer 推送异常: {e}")


def push_serverchan(key, title, content):
    """推送到 Server酱 (Turbo 版)
    API 文档: https://sct.ftqq.com/sendkey
    接口地址: https://sctapi.ftqq.com/<sendkey>.send
    """
    if not key:
        return
    try:
        r = requests.post(
            f"https://sctapi.ftqq.com/{key}.send",
            data={"title": title, "desp": content},
            timeout=TIMEOUT,
        )
        resp = safe_json(r)
        if r.ok and resp.get("code") == 0:
            print("✅ Server酱推送成功")
        else:
            print(f"⚠️ Server酱推送失败: {resp.get('message', r.text)}")
    except Exception as e:
        print(f"⚠️ Server酱推送异常: {e}")


def push_telegram(bot_token, chat_id, title, content):
    """推送到 Telegram Bot
    API 文档: https://core.telegram.org/bots/api#sendmessage
    接口地址: https://api.telegram.org/bot<token>/sendMessage
    """
    if not bot_token or not chat_id:
        return
    text = f"{title}\n\n{content}"
    # Telegram 单条消息上限 4096 字符，做截断避免发送失败
    if len(text) > 4000:
        text = text[:3990] + "\n..."
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {"chat_id": chat_id, "text": text}
        r = requests.post(url, json=data, timeout=TIMEOUT)
        resp = safe_json(r)
        if r.ok and resp.get("ok"):
            print("✅ Telegram 推送成功")
        else:
            print(
                f"⚠️ Telegram 推送失败: HTTP {r.status_code} | "
                f"{resp.get('description', r.text)}"
            )
    except Exception as e:
        print(f"⚠️ Telegram 推送异常: {e}")


def push_pushplus(token, title, content):
    """推送到 PushPlus（推送加）
    API 文档: https://www.pushplus.plus/doc/guide/api.html
    接口地址: https://www.pushplus.plus/send
    注意: 官方域名 www.pushplus.plus 已恢复使用，支持 HTTP/HTTPS
    """
    if not token:
        return
    try:
        url = "https://www.pushplus.plus/send"
        data = {
            "token": token,
            "title": title,
            "content": content,
            "template": "html",
        }
        r = requests.post(url, json=data, timeout=TIMEOUT)
        resp = safe_json(r)
        if r.ok and resp.get("code") == 200:
            print("✅ PushPlus 推送成功")
        else:
            print(f"⚠️ PushPlus 推送失败: {resp.get('msg', r.text)}")
    except Exception as e:
        print(f"⚠️ PushPlus 推送异常: {e}")


def push_dingtalk(webhook_url, title, content):
    """推送到钉钉群机器人
    API 文档: https://open.dingtalk.com/document/orgapp/custom-bot-send-message
    接口地址: https://oapi.dingtalk.com/robot/send?access_token=xxx
    支持 text 和 markdown 消息格式，支持加签安全验证
    """
    if not webhook_url:
        return
    try:
        # 处理加签安全设置（如果配置了 DINGTALK_SECRET）
        secret = os.getenv("DINGTALK_SECRET", "")
        if secret:
            timestamp = str(round(time.time() * 1000))
            string_to_sign = f"{timestamp}\n{secret}"
            hmac_code = hmac.new(
                secret.encode("utf-8"),
                string_to_sign.encode("utf-8"),
                digestmod=hashlib.sha256,
            ).digest()
            sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
            separator = "&" if "?" in webhook_url else "?"
            webhook_url = f"{webhook_url}{separator}timestamp={timestamp}&sign={sign}"

        # 使用 markdown 格式，更美观
        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": f"### {title}\n\n{content}",
            },
        }
        headers = {"Content-Type": "application/json"}
        r = requests.post(webhook_url, json=data, headers=headers, timeout=TIMEOUT)
        resp = safe_json(r)
        if r.ok and resp.get("errcode") == 0:
            print("✅ 钉钉机器人推送成功")
        else:
            print(f"⚠️ 钉钉机器人推送失败: {resp.get('errmsg', r.text)}")
    except Exception as e:
        print(f"⚠️ 钉钉机器人推送异常: {e}")


def push_feishu(webhook_url, title, content):
    """推送到飞书群机器人
    API 文档: https://open.feishu.cn/document/ukTMukTMukTM/ucTM5YjL3ETO14yNxkJN
    接口地址: https://open.feishu.cn/open-apis/bot/v2/hook/xxx
    支持 text 和 interactive (卡片) 消息格式，支持加签安全验证
    """
    if not webhook_url:
        return
    try:
        # 处理加签安全设置（如果配置了 FEISHU_SECRET）
        secret = os.getenv("FEISHU_SECRET", "")
        data = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": title,
                    },
                    "template": "blue",
                },
                "elements": [
                    {
                        "tag": "markdown",
                        "content": content,
                    }
                ],
            },
        }
        if secret:
            timestamp = str(round(time.time()))
            string_to_sign = f"{timestamp}\n{secret}"
            hmac_code = hmac.new(
                string_to_sign.encode("utf-8"),
                digestmod=hashlib.sha256,
            ).digest()
            sign = base64.b64encode(hmac_code).decode("utf-8")
            data["timestamp"] = timestamp
            data["sign"] = sign

        headers = {"Content-Type": "application/json"}
        r = requests.post(webhook_url, json=data, headers=headers, timeout=TIMEOUT)
        resp = safe_json(r)
        if r.ok and resp.get("code") == 0:
            print("✅ 飞书机器人推送成功")
        else:
            print(f"⚠️ 飞书机器人推送失败: {resp.get('msg', r.text)}")
    except Exception as e:
        print(f"⚠️ 飞书机器人推送异常: {e}")


def push_wecom_bot(webhook_url, title, content):
    """推送到企业微信群机器人
    API 文档: https://developer.work.weixin.qq.com/document/path/91770
    接口地址: https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx
    支持 text 和 markdown 消息格式
    """
    if not webhook_url:
        return
    try:
        # 使用 markdown 格式，更美观
        data = {
            "msgtype": "markdown",
            "markdown": {
                "content": f"### {title}\n\n{content}",
            },
        }
        headers = {"Content-Type": "application/json"}
        r = requests.post(webhook_url, json=data, headers=headers, timeout=TIMEOUT)
        resp = safe_json(r)
        if r.ok and resp.get("errcode") == 0:
            print("✅ 企业微信机器人推送成功")
        else:
            print(f"⚠️ 企业微信机器人推送失败: {resp.get('errmsg', r.text)}")
    except Exception as e:
        print(f"⚠️ 企业微信机器人推送异常: {e}")


def push_yunhu(token, recv_id, title, content):
    """推送到云湖机器人
    API 文档: https://www.yhchat.com/document/1-3
    接口地址: https://chat-go.jwzhd.com/open-apis/v1/bot/send-message
    支持给用户或群发送消息
    """
    if not token or not recv_id:
        return
    try:
        url = "https://chat-go.jwzhd.com/open-apis/v1/bot/send-message"
        # recv_type: group 或 user，默认 group
        recv_type = os.getenv("YUNHU_RECV_TYPE", "group")
        data = {
            "token": token,
            "recvId": recv_id,
            "recvType": recv_type,
            "contentType": 1,  # 1=文本, 2=markdown, 3=HTML
            "content": f"**{title}**\n\n{content}",
        }
        headers = {"Content-Type": "application/json"}
        r = requests.post(url, json=data, headers=headers, timeout=TIMEOUT)
        resp = safe_json(r)
        if r.ok and resp.get("code") == 1:
            print("✅ 云湖机器人推送成功")
        else:
            print(f"⚠️ 云湖机器人推送失败: {resp.get('msg', resp.get('message', r.text))}")
    except Exception as e:
        print(f"⚠️ 云湖机器人推送异常: {e}")


def push_all(title, content):
    """推送到所有已配置的通知渠道
    支持的渠道（按优先顺序）：
    1. PushDeer      - 环境变量 SENDKEY
    2. Server酱      - 环境变量 SERVERCHAN_KEY
    3. Telegram      - 环境变量 TG_BOT_TOKEN + TG_CHAT_ID
    4. PushPlus      - 环境变量 PUSHPLUS_TOKEN
    5. 钉钉机器人    - 环境变量 DINGTALK_WEBHOOK (可选 DINGTALK_SECRET)
    6. 飞书机器人    - 环境变量 FEISHU_WEBHOOK (可选 FEISHU_SECRET)
    7. 企业微信机器人 - 环境变量 WECOM_BOT_WEBHOOK
    8. 云湖机器人    - 环境变量 YUNHU_TOKEN + YUNHU_RECV_ID (可选 YUNHU_RECV_TYPE)
    """
    configured = []
    # PushDeer
    deer_key = os.getenv("SENDKEY", "")
    if deer_key:
        push_deer(deer_key, title, content)
        configured.append("PushDeer")
    # Server酱
    sc_key = os.getenv("SERVERCHAN_KEY", "")
    if sc_key:
        push_serverchan(sc_key, title, content)
        configured.append("Server酱")
    # Telegram
    bot_token = os.getenv("TG_BOT_TOKEN", "")
    chat_id = os.getenv("TG_CHAT_ID", "")
    if bot_token and chat_id:
        push_telegram(bot_token, chat_id, title, content)
        configured.append("Telegram")
    # PushPlus
    pp_token = os.getenv("PUSHPLUS_TOKEN", "")
    if pp_token:
        push_pushplus(pp_token, title, content)
        configured.append("PushPlus")
    # 钉钉机器人
    dingtalk_webhook = os.getenv("DINGTALK_WEBHOOK", "")
    if dingtalk_webhook:
        push_dingtalk(dingtalk_webhook, title, content)
        configured.append("钉钉机器人")
    # 飞书机器人
    feishu_webhook = os.getenv("FEISHU_WEBHOOK", "")
    if feishu_webhook:
        push_feishu(feishu_webhook, title, content)
        configured.append("飞书机器人")
    # 企业微信机器人
    wecom_webhook = os.getenv("WECOM_BOT_WEBHOOK", "")
    if wecom_webhook:
        push_wecom_bot(wecom_webhook, title, content)
        configured.append("企业微信机器人")
    # 云湖机器人
    yunhu_token = os.getenv("YUNHU_TOKEN", "")
    yunhu_recv_id = os.getenv("YUNHU_RECV_ID", "")
    if yunhu_token and yunhu_recv_id:
        push_yunhu(yunhu_token, yunhu_recv_id, title, content)
        configured.append("云湖机器人")

    if not configured:
        print("⚠️ 未配置任何推送服务，请在 Secrets 中设置至少一种推送渠道")
    else:
        print(f"📬 已推送至: {', '.join(configured)}")


# ---------- 签到逻辑 ----------
def classify_checkin(code, message):
    """
    判断签到结果: 优先根据 code 字段，兜底用 message 关键词。
    GLaDOS API 返回值:
      - code=0  → 签到成功
      - code=1  → 今日已签到
      - 其他    → 签到失败
    部分旧接口或域名可能只返回 message，因此做兜底处理。
    """
    if code == 0:
        return "ok"
    if code == 1:
        return "repeat"
    # 兜底：关键词匹配
    msg = message.lower()
    if "got" in msg:
        return "ok"
    if any(kw in msg for kw in ("repeat", "already", "重复", "已签到", "签到过", "请勿")):
        return "repeat"
    return "fail"


# ---------- 主流程 ----------
def main():
    cookies = [c.strip() for c in os.getenv("COOKIES", "").split("&") if c.strip()]
    if not cookies:
        push_all("GLaDOS 签到", "❌ 未检测到 COOKIES，请配置 GitHub Secrets")
        return

    session = requests.Session()
    ok = fail = repeat = 0
    lines = []
    for idx, cookie in enumerate(cookies, 1):
        headers = dict(HEADERS_BASE)
        headers["cookie"] = cookie
        email, days, total_points = "unknown", "-", "-"
        try:
            # 1. 签到
            r = session.post(
                CHECKIN_URL,
                headers=headers,
                data=json.dumps(PAYLOAD),
                timeout=TIMEOUT,
            )
            j = safe_json(r)
            code = j.get("code", -2)
            message = j.get("message", "")
            earned = j.get("points", 0)
            result = classify_checkin(code, message)
            if result == "ok":
                ok += 1
                status = f"✅ 成功 (+{earned}积分)"
            elif result == "repeat":
                repeat += 1
                status = "🔄 已签到"
            else:
                fail += 1
                status = f"❌ 失败({message})"
            # 2. 查询账号状态（剩余天数、邮箱），允许失败
            try:
                s = session.get(STATUS_URL, headers=headers, timeout=TIMEOUT)
                data = safe_json(s).get("data") or {}
                email = data.get("email", email)
                if data.get("leftDays") is not None:
                    days = f"{int(float(data['leftDays']))} 天"
            except Exception:
                pass  # 状态查询失败不影响签到结果
            # 3. 查询总积分，允许失败
            try:
                p = session.get(POINTS_URL, headers=headers, timeout=TIMEOUT)
                pj = safe_json(p)
                if pj.get("points") is not None:
                    total_points = f"{int(float(pj['points']))} 积分"
            except Exception:
                pass  # 积分查询失败不影响签到结果
        except Exception as e:
            fail += 1
            status = f"❌ 异常({e})"
        lines.append(f"{idx}. {email} | {status} | 总积分:{total_points} | 剩余:{days}")
        # 非最后一个账号时随机延迟，避免请求过快
        if idx < len(cookies):
            time.sleep(random.uniform(1, 2))

    title = f"GLaDOS 签到完成 ✅{ok} ❌{fail} 🔄{repeat}"
    content = "\n".join(lines)
    print(content)
    push_all(title, content)


if __name__ == "__main__":
    main()
