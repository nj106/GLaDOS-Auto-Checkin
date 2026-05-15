# 📌 GLaDOS 自动签到
一个基于 **GitHub Actions** 的 **GLaDOS 自动签到脚本**。
**无需服务器、无需编程基础**，每天自动帮你签到。
------
## ✨ 功能说明
- ✅ **每天自动签到**
- 🔁 **已签到自动识别，不会报错**
- 👥 **支持多个账号**
- 📊 **查询总积分和剩余天数**
- 📬 **多种签到结果推送渠道（PushDeer / Server酱 / Telegram / PushPlus / 钉钉 / 飞书 / 企业微信机器人 / 云湖）**
- 🔧 **每月自动空提交保活，防止 GitHub Actions 被暂停**
- 🆓 **完全免费，使用 GitHub Actions**
------
## 📂 项目结构
```
.
├── checkin.py                 # 签到脚本（不用动）
└── .github/workflows/
    └── glados.yml              # GitHub Actions 配置（不用动）
```
------
## 🚀 使用教程
### 第一步：Fork 本项目
1. 点击右上角 **Fork**
2. Fork 到你自己的 GitHub 账号下
👉 后续所有操作都在你 **自己的仓库** 中完成
------
### 第二步：获取 GLaDOS Cookie
1. 打开浏览器，登录：https://glados.cloud
2. 按 **F12** 打开开发者工具
3. 找到：
   - Chrome：`Application` → `Cookies`
   - Firefox：`存储` → `Cookies`
4. 选择 `glados.cloud`
5. **复制完整 Cookie 内容**
示例（示意）：
```
koa:sess=xxxxxx; koa:sess.sig=yyyyyy
```
⚠️ **必须是完整的一整段，不要只复制一半**
------
### 第三步：添加 GitHub Secrets
进入你 Fork 后的仓库：
1. 点击 **Settings**
2. 左侧选择 **Secrets and variables → Actions**
3. 点击 **New repository secret**
#### 添加第一个 Secret（必填）
- **Name**：`COOKIES`
- **Value**：粘贴刚才复制的 Cookie
点击 **Save**
------
### （可选）第四步：开启签到结果推送
项目支持 **八种推送渠道**，你可以按需配置任意一种或多种：
#### 🦌 方式一：PushDeer
开源轻量推送，支持 iOS / Android / Web。
1. 注册 PushDeer：https://www.pushdeer.com
2. 获取你的 `SENDKEY`
3. 在 GitHub Secrets 中添加：
   - **Name**：`SENDKEY`
   - **Value**：你的 PushDeer key
#### 🔔 方式二：Server酱 (S酱)
通过微信推送通知，注册即用。
1. 注册 Server酱 Turbo：https://sct.ftqq.com
2. 获取你的 SendKey
3. 在 GitHub Secrets 中添加：
   - **Name**：`SERVERCHAN_KEY`
   - **Value**：你的 Server酱 SendKey
#### 🤖 方式三：Telegram Bot
通过 Telegram 机器人推送，全球可用。
1. 在 Telegram 搜索 `@BotFather`
2. 发送 `/newbot` 创建机器人，拿到 `TG_BOT_TOKEN`
3. 打开你新建的机器人，先发一条任意消息
4. 访问：`https://api.telegram.org/bot<你的TG_BOT_TOKEN>/getUpdates`
5. 在返回内容中找到你的 `chat.id`（这就是 `TG_CHAT_ID`）
6. 在 GitHub Secrets 中添加：
   - **Name**：`TG_BOT_TOKEN`
   - **Value**：你的 Telegram Bot Token
   - **Name**：`TG_CHAT_ID`
   - **Value**：你的聊天 ID（数字，可能是负数）
#### 📮 方式四：PushPlus（推送加）
通过微信公众号推送通知。
1. 注册 PushPlus：https://www.pushplus.plus
2. 微信扫码登录，获取你的 Token
3. 在 GitHub Secrets 中添加：
   - **Name**：`PUSHPLUS_TOKEN`
   - **Value**：你的 PushPlus Token
> ⚠️ **注意**：PushPlus 官方域名为 `www.pushplus.plus`，API 地址为 `https://www.pushplus.plus/send`。本项目已适配最新官方域名。
#### 🔔 方式五：钉钉机器人
通过钉钉群机器人推送通知，支持加签安全验证。
1. 在钉钉群中添加自定义机器人
2. 安全设置选择"自定义关键词"，关键词填写 **pushplus**（注意：关键词匹配是钉钉的安全策略要求，消息中必须包含该关键词才能发送成功）
3. 复制机器人的 Webhook 地址
4. 在 GitHub Secrets 中添加：
   - **Name**：`DINGTALK_WEBHOOK`
   - **Value**：完整的 Webhook 地址（如 `https://oapi.dingtalk.com/robot/send?access_token=xxx`）
   - **Name**：`DINGTALK_SECRET`（可选，加签验证密钥）
   - **Value**：机器人的加签密钥
> 💡 **提示**：如果机器人设置了加签安全验证，必须配置 `DINGTALK_SECRET`，否则消息会发送失败。
#### 🐦 方式六：飞书机器人
通过飞书群机器人推送通知，支持加签安全验证。
1. 在飞书群中添加自定义机器人
2. 复制机器人的 Webhook 地址
3. 在 GitHub Secrets 中添加：
   - **Name**：`FEISHU_WEBHOOK`
   - **Value**：完整的 Webhook 地址（如 `https://open.feishu.cn/open-apis/bot/v2/hook/xxx`）
   - **Name**：`FEISHU_SECRET`（可选，加签验证密钥）
   - **Value**：机器人的加签密钥
> 💡 **提示**：如果机器人设置了加签安全验证，必须配置 `FEISHU_SECRET`，否则消息会发送失败。
#### 💼 方式七：企业微信机器人
通过企业微信群机器人推送通知。
1. 在企业微信群中添加自定义机器人
2. 复制机器人的 Webhook 地址
3. 在 GitHub Secrets 中添加：
   - **Name**：`WECOM_BOT_WEBHOOK`
   - **Value**：完整的 Webhook 地址（如 `https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx`）
> ⚠️ **注意**：请勿泄露 Webhook 地址，避免被他人利用发送垃圾消息。
#### 🌊 方式八：云湖机器人
通过云湖社交APP机器人推送通知，支持给用户或群发送消息。
1. 下载并注册云湖：https://www.yhchat.com
2. 在云湖中创建机器人，获取 Token
3. 获取接收消息的用户ID或群ID（recvId）
4. 在 GitHub Secrets 中添加：
   - **Name**：`YUNHU_TOKEN`
   - **Value**：你的云湖机器人 Token
   - **Name**：`YUNHU_RECV_ID`
   - **Value**：接收消息的用户ID或群ID
   - **Name**：`YUNHU_RECV_TYPE`（可选，默认 `group`）
   - **Value**：`group`（群消息）或 `user`（用户消息）
------
## 👥 多账号如何添加？
### 规则很简单：
> **多个账号的 Cookie，用 `&` 连接**
示例：
```
cookie_账号1 & cookie_账号2 & cookie_账号3
```
⚠️ 注意事项：
- 不要换行
- 不要用逗号
- 每个 cookie 都是完整的一段
------
## ⏰ 自动签到时间说明
项目默认设置为：
```
每天 UTC 04:00 自动运行
```
换算成北京时间：
> 🕛 **每天中午 12 点自动签到**
你无需做任何操作，它会每天自动运行。
------
## 🔧 保活机制
GitHub 会对长期无活动的仓库暂停 Actions。本项目内置了 **每月自动空提交** 机制：
- 每月 1 号 UTC 00:00 自动创建一个空提交
- 防止仓库因"不活跃"被 GitHub 暂停 Actions
- 无需手动操作
------
## 📋 签到结果说明
签到完成后，推送内容包含：
| 字段 | 说明 |
|------|------|
| ✅ 成功 | 签到成功，显示本次获得积分 |
| 🔄 已签到 | 今日已签到过，不重复签到 |
| ❌ 失败 | 签到失败，显示失败原因 |
| 总积分 | 账号当前总积分 |
| 剩余 | 账号剩余天数 |
------
## 📬 推送渠道汇总
| 渠道 | 环境变量 | 必填参数 | 可选参数 |
|------|---------|---------|---------|
| PushDeer | `SENDKEY` | SENDKEY | - |
| Server酱 | `SERVERCHAN_KEY` | SERVERCHAN_KEY | - |
| Telegram | `TG_BOT_TOKEN` + `TG_CHAT_ID` | TG_BOT_TOKEN, TG_CHAT_ID | - |
| PushPlus | `PUSHPLUS_TOKEN` | PUSHPLUS_TOKEN | - |
| 钉钉机器人 | `DINGTALK_WEBHOOK` | DINGTALK_WEBHOOK | DINGTALK_SECRET |
| 飞书机器人 | `FEISHU_WEBHOOK` | FEISHU_WEBHOOK | FEISHU_SECRET |
| 企业微信机器人 | `WECOM_BOT_WEBHOOK` | WECOM_BOT_WEBHOOK | - |
| 云湖机器人 | `YUNHU_TOKEN` + `YUNHU_RECV_ID` | YUNHU_TOKEN, YUNHU_RECV_ID | YUNHU_RECV_TYPE |
------
## 🔄 项目更新日志
### v3.0.0 (2025-05)
- **修复** PushPlus 推送域名修复：官方域名 `www.pushplus.plus` 已恢复使用，API 地址更正为 `https://www.pushplus.plus/send`
- **新增** 钉钉群机器人推送渠道，支持 markdown 格式和加签安全验证
- **新增** 飞书群机器人推送渠道，支持卡片消息格式和加签安全验证
- **新增** 企业微信群机器人推送渠道，支持 markdown 格式
- **新增** 云湖社交APP机器人推送渠道，支持用户和群消息
- **优化** 推送渠道增加到 8 种，覆盖主流即时通讯工具
- **优化** 更新 GitHub Actions 工作流配置，添加新渠道环境变量
### v2.0.0 (2025-05)
- **新增** Telegram Bot 推送支持
- **新增** PushPlus（推送加）推送支持
- **优化** PushDeer 推送改为直接 HTTP API 调用，移除 `pypushdeer` 第三方库依赖，提升稳定性
- **优化** 签到结果判断逻辑：优先使用 API 返回的 `code` 字段，兜底用 `message` 关键词匹配
- **新增** 总积分查询功能
- **新增** 每月自动空提交保活，防止 GitHub Actions 被暂停
- **优化** Python 版本升级至 3.11
- **优化** 多账号间请求增加随机延迟，避免请求过快
- **优化** 仅非最后一个账号时延迟，最后一个不等待
### v1.0.0
- 基础签到功能
- PushDeer 推送
- Server酱推送
- 多账号支持
------
## ❓ 常见问题
**Q: PushPlus 推送失败怎么办？**
A: PushPlus 官方域名为 `www.pushplus.plus`，API 地址为 `https://www.pushplus.plus/send`。请确保你在官网 https://www.pushplus.plus 获取 Token。本项目已适配最新官方域名。

**Q: 钉钉机器人推送失败？**
A: 请确保在钉钉机器人的安全设置中选择了"自定义关键词"，关键词填写 **pushplus**，否则消息会被钉钉过滤。如果设置了加签验证，请同时配置 `DINGTALK_SECRET`。

**Q: 飞书机器人推送失败？**
A: 请确保机器人已添加到目标群聊中。如果设置了加签验证，请同时配置 `FEISHU_SECRET`。企业管理员需要开启"允许机器人发送消息"策略。

**Q: 企业微信机器人推送失败？**
A: 请确保 Webhook 地址正确且未泄露。企业微信机器人无需额外的密钥配置，只需 Webhook 地址即可。

**Q: 云湖机器人推送失败？**
A: 请确保 `YUNHU_TOKEN` 和 `YUNHU_RECV_ID` 都已正确配置。`YUNHU_RECV_TYPE` 默认为 `group`，如果是给用户发送消息请设置为 `user`。

**Q: 签到提示 Cookie 失效？**
A: Cookie 有有效期，请重新登录 GLaDOS 获取最新 Cookie 并更新 GitHub Secrets。

**Q: Actions 被暂停了？**
A: 本项目已内置每月空提交保活机制。如果仍被暂停，请手动在 Actions 页面触发一次 `workflow_dispatch`。

**Q: 可以同时配置多个推送渠道吗？**
A: 可以。配置多个 Secrets 即可同时推送到多个渠道，互不影响。
