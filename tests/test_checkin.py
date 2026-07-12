"""
GLaDOS 签到脚本单元测试（M5：补充核心逻辑测试覆盖）。

运行方式：
    python -m unittest discover -s tests -v

依赖：仅标准库（unittest / unittest.mock），无需额外安装。
"""
import os
import sys
import base64
import hmac
import hashlib
import json
import unittest
from unittest import mock

import requests  # noqa: F401  (用于构造 requests 异常)

# 将仓库根目录加入 sys.path，使 `import checkin` 可用
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import checkin  # noqa: E402


def make_response(status_code=200, ok=True, payload=None, text=""):
    """构造一个 mock requests.Response，供 _push_request 使用。"""
    resp = mock.MagicMock()
    resp.status_code = status_code
    resp.ok = ok
    resp.text = text
    resp.json.return_value = payload if payload is not None else {}
    resp.headers = {}
    return resp


class TestMaskEmail(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(checkin.mask_email("test@example.com"), "te***t@example.com")

    def test_two_chars(self):
        self.assertEqual(checkin.mask_email("ab@example.com"), "ab***b@example.com")

    def test_one_char(self):
        self.assertEqual(checkin.mask_email("a@example.com"), "a***a@example.com")

    def test_no_at(self):
        self.assertEqual(checkin.mask_email("unknown"), "unknown")

    def test_empty(self):
        self.assertEqual(checkin.mask_email(""), "")


class TestMaskCookie(unittest.TestCase):
    def test_short_fully_masked(self):
        # COOKIE_MIN_LENGTH=24，<=24 必须整体脱敏（M3 边界）
        self.assertEqual(checkin.mask_cookie("x" * 23), "***")
        self.assertEqual(checkin.mask_cookie("x" * 24), "***")

    def test_long_partial(self):
        c = "a" * 10 + "MIDDLE" + "b" * 10
        self.assertEqual(checkin.mask_cookie(c), "a" * 10 + "..." + "b" * 10)

    def test_empty(self):
        self.assertEqual(checkin.mask_cookie(""), "***")

    def test_no_overlap_at_boundary(self):
        # 长度 > COOKIE_MIN_LENGTH(24)：前后各 10 字符，中间隐藏，不得重叠暴露
        c = "A" * 10 + "SECRET" + "B" * 10
        masked = checkin.mask_cookie(c)
        self.assertNotIn("SECRET", masked)
        self.assertTrue(masked.startswith("A" * 10))
        self.assertTrue(masked.endswith("B" * 10))


class TestValidateCookie(unittest.TestCase):
    def test_valid(self):
        ok, msg = checkin.validate_cookie("koa:sess=abc; koa:sess.sig=def")
        self.assertTrue(ok)
        self.assertEqual(msg, "")

    def test_missing_sess(self):
        ok, msg = checkin.validate_cookie("session=abc; other=1")
        self.assertFalse(ok)
        self.assertIn("koa:sess", msg)

    def test_missing_sig(self):
        ok, msg = checkin.validate_cookie("koa:sess=abc")
        self.assertFalse(ok)
        self.assertIn("koa:sess.sig", msg)

    def test_empty(self):
        ok, msg = checkin.validate_cookie("")
        self.assertFalse(ok)
        self.assertIn("为空", msg)


class TestParseEarnedPoints(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(checkin.parse_earned_points("已经签到成功，获得 1 点，请明天继续签到哦！"), 1)

    def test_multi_digit(self):
        self.assertEqual(checkin.parse_earned_points("获得 12 点"), 12)

    def test_no_points(self):
        self.assertEqual(checkin.parse_earned_points("签到成功"), 0)

    def test_empty(self):
        self.assertEqual(checkin.parse_earned_points(""), 0)


class TestClassifyCheckin(unittest.TestCase):
    def test_ok_code_zero(self):
        self.assertEqual(checkin.classify_checkin(0, ""), "ok")

    def test_repeat_code_one(self):
        self.assertEqual(checkin.classify_checkin(1, ""), "repeat")

    def test_fail(self):
        self.assertEqual(checkin.classify_checkin(-1, "error"), "fail")

    def test_got_keyword(self):
        self.assertEqual(checkin.classify_checkin(-2, "you got points"), "ok")

    def test_repeat_keywords(self):
        for kw in ("repeat", "already", "重复", "已签到", "签到过", "请勿"):
            with self.subTest(kw=kw):
                self.assertEqual(checkin.classify_checkin(-2, f"please {kw} later"), "repeat")

    def test_bad_code(self):
        self.assertEqual(checkin.classify_checkin("not_a_number", ""), "fail")


class TestSafeInt(unittest.TestCase):
    def test_int(self):
        self.assertEqual(checkin.safe_int(5), "5")

    def test_float_str(self):
        self.assertEqual(checkin.safe_int("3.0"), "3")

    def test_invalid(self):
        self.assertEqual(checkin.safe_int("abc", "-"), "-")


class TestIsRetryable(unittest.TestCase):
    def test_timeout_retryable(self):
        self.assertTrue(checkin.is_retryable(requests_timeout()))

    def test_connection_retryable(self):
        self.assertTrue(checkin.is_retryable(requests_connection_error()))

    def test_json_decode_retryable(self):
        self.assertTrue(checkin.is_retryable(requests_json_error()))

    def test_4xx_not_retryable(self):
        self.assertFalse(checkin.is_retryable(http_error(401)))
        self.assertFalse(checkin.is_retryable(http_error(403)))

    def test_5xx_retryable(self):
        self.assertTrue(checkin.is_retryable(http_error(502)))

    def test_other_exception_not_retryable(self):
        self.assertFalse(checkin.is_retryable(ValueError("x")))


def requests_timeout():
    import requests
    return requests.exceptions.Timeout("timeout")


def requests_connection_error():
    import requests
    return requests.exceptions.ConnectionError("conn")


def requests_json_error():
    import requests
    return requests.exceptions.JSONDecodeError("bad", "doc", 0)


def http_error(status):
    import requests
    resp = mock.MagicMock()
    resp.status_code = status
    return requests.exceptions.HTTPError(f"status {status}", response=resp)


class TestRequireJson(unittest.TestCase):
    def test_valid(self):
        resp = make_response(payload={"code": 0})
        self.assertEqual(checkin.require_json(resp), {"code": 0})

    def test_invalid_raises(self):
        import requests
        resp = make_response(payload={})
        resp.json.side_effect = requests.exceptions.JSONDecodeError("bad", "doc", 0)
        with self.assertRaises(requests.exceptions.RequestException):
            checkin.require_json(resp)


class TestPushAllDispatch(unittest.TestCase):
    """验证 push_all 仅调用已配置渠道，并正确统计成功数（L3/L4）。"""

    def setUp(self):
        # 清空可能残留的 env
        for v in ("SENDKEY", "SERVERCHAN_KEY", "TG_BOT_TOKEN", "TG_CHAT_ID",
                  "PUSHPLUS_TOKEN", "DINGTALK_WEBHOOK", "FEISHU_WEBHOOK",
                  "WECOM_BOT_WEBHOOK", "YUNHU_TOKEN", "YUNHU_RECV_ID"):
            os.environ.pop(v, None)

    def test_only_configured_called(self):
        os.environ["SENDKEY"] = "key1"
        os.environ["PUSHPLUS_TOKEN"] = "tok1"
        with mock.patch.object(checkin, "push_deer", return_value=True) as m_deer, \
             mock.patch.object(checkin, "push_pushplus", return_value=True) as m_plus, \
             mock.patch.object(checkin, "push_telegram", return_value=False) as m_tg:
            success, configured = checkin.push_all("t", "c")
        m_deer.assert_called_once()
        m_plus.assert_called_once()
        m_tg.assert_not_called()
        self.assertEqual(configured, 2)
        self.assertEqual(success, 2)

    def test_success_count(self):
        os.environ["SENDKEY"] = "key1"
        with mock.patch.object(checkin, "push_deer", return_value=False):
            success, configured = checkin.push_all("t", "c")
        self.assertEqual(configured, 1)
        self.assertEqual(success, 0)

    def test_nothing_configured(self):
        success, configured = checkin.push_all("t", "c")
        self.assertEqual(configured, 0)
        self.assertEqual(success, 0)


class TestDingtalkSign(unittest.TestCase):
    """钉钉加签算法端到端校验（L6 相关，确保签名正确）。"""

    @mock.patch.object(checkin.requests, "post")
    def test_sign(self, mock_post):
        mock_post.return_value = make_response(ok=True, payload={"errcode": 0})
        webhook = "https://oapi.dingtalk.com/robot/send?access_token=abc"
        secret = "mysecret"
        with mock.patch.object(checkin.os, "getenv", return_value=secret):
            checkin.push_dingtalk(webhook, "t", "c")

        called_url = mock_post.call_args[0][0]
        from urllib.parse import urlparse, parse_qsl
        qs = dict(parse_qsl(urlparse(called_url).query))
        self.assertIn("timestamp", qs)
        self.assertIn("sign", qs)

        # 用 URL 中的 timestamp 重新计算签名，验证与生产算法一致
        # （注意：URL 经 parse_qsl 解析后已还原 quote_plus，故 expected 取原始 base64）
        string_to_sign = f"{qs['timestamp']}\n{secret}"
        expected = base64.b64encode(
            hmac.new(secret.encode(), string_to_sign.encode(), hashlib.sha256).digest()
        ).decode()
        self.assertEqual(qs["sign"], expected)


class TestFeishuSign(unittest.TestCase):
    """飞书加签算法端到端校验。"""

    @mock.patch.object(checkin.requests, "post")
    def test_sign(self, mock_post):
        mock_post.return_value = make_response(ok=True, payload={"code": 0})
        webhook = "https://open.feishu.cn/open-apis/bot/v2/hook/abc"
        secret = "mysecret"
        with mock.patch.object(checkin.os, "getenv", return_value=secret):
            checkin.push_feishu(webhook, "t", "c")

        _, kwargs = mock_post.call_args
        payload = json.loads(kwargs["data"]) if "data" in kwargs else kwargs.get("json")
        self.assertIn("timestamp", payload)
        self.assertIn("sign", payload)

        string_to_sign = f"{payload['timestamp']}\n{secret}"
        expected = base64.b64encode(
            hmac.new(string_to_sign.encode(), b"", hashlib.sha256).digest()
        ).decode()
        self.assertEqual(payload["sign"], expected)


if __name__ == "__main__":
    unittest.main()
