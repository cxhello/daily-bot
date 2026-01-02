# 📊 每日简报机器人 (Daily Report Bot)

> 一个基于 GitHub Actions 的自动化每日简报系统,每天为你汇总 GitHub 活动、学习进度、每日诗词等信息。

## ✨ 特性

- 🚀 **完全免费** - 基于 GitHub Actions,无需服务器
- 📱 **手机一键触发** - iOS Shortcuts / Android HTTP Shortcuts
- ⏰ **可选定时发送** - 支持 cron 定时任务
- 📊 **多数据源** - GitHub、多邻国、微信读书、小米运动等
- 📝 **每日诗词** - 中华诗词库,陶冶情操
- 🔔 **多平台通知** - 支持 Telegram、钉钉、飞书、企业微信
- 🎯 **高度可配置** - 自由开关各个功能模块

## 📦 支持的数据源

| 数据源 | 状态 | 说明 |
|--------|------|------|
| GitHub 统计 | ✅ 可用 | PR、Issue、Commit 等活动 |
| 多邻国 | ✅ 可用 | 学习天数、XP、连续打卡 |
| 每日诗词 | ✅ 可用 | 中华古诗词随机推送 |
| 小米运动 | ⚠️ 待修复 | API 变化需要更新 |
| 微信读书 | ⚠️ 待修复 | 需要验证和修复 |

## 🔔 支持的通知平台

| 平台 | 配置类型 | 特性 |
|------|---------|------|
| Telegram | `telegram` | 国际主流,功能强大 |
| 钉钉 | `dingtalk` | 支持 HMAC-SHA256 加签 |
| 飞书 | `feishu` | 字节跳动企业办公 |
| 企业微信 | `wecom` | 腾讯企业办公,支持 Markdown |

## 🚀 快速开始

### 1. Fork 本仓库

点击右上角 Fork 按钮,复制到你的账号下。

### 2. 配置 Secrets 和 Variables

进入仓库 `Settings` → `Secrets and variables` → `Actions`:

**通知平台配置 (四选一):**

使用 Telegram:
- `TELEGRAM_BOT_TOKEN` - Telegram Bot Token
- `TELEGRAM_CHAT_ID` - Telegram Chat ID

使用钉钉:
- `DINGTALK_WEBHOOK` - 钉钉机器人 Webhook URL
- `DINGTALK_SECRET` - 加签密钥 (可选)

使用飞书:
- `FEISHU_WEBHOOK` - 飞书机器人 Webhook URL

使用企业微信:
- `WECOM_WEBHOOK` - 企业微信机器人 Webhook URL

**Variables 配置:**
- `NOTIFIER_TYPE` - 通知器类型: `telegram`/`dingtalk`/`feishu`/`wecom` (默认 `telegram`)

**可选数据源配置:**
- `GITHUB_TOKEN` - GitHub Personal Access Token
- `GITHUB_USERNAME` - GitHub 用户名
- `DUOLINGO_USERNAME` - 多邻国用户名
- `DUOLINGO_JWT_TOKEN` - 多邻国 JWT Token
- `XIAOMI_USERNAME` - 小米账号
- `XIAOMI_PASSWORD` - 小米密码
- `WEREAD_COOKIE` - 微信读书 Cookie

### 3. 触发运行

**方式 1: GitHub 网页**
- 进入 Actions → Daily Report → Run workflow

**方式 2: 手机一键触发**
- iOS: 使用 Shortcuts 应用发送 HTTP 请求到 GitHub API
- Android: 使用 HTTP Shortcuts 应用触发 workflow

**方式 3: 定时自动发送**
- 编辑 `.github/workflows/daily.yml`
- 取消注释 schedule 部分

## 🏗️ 架构

```
手机触发 → GitHub Actions → Python 脚本 → 数据收集 → 多平台推送
                                              ├─ Telegram
                                              ├─ 钉钉
                                              ├─ 飞书
                                              └─ 企业微信
```

**优势:**
- ✅ 无需服务器 (GitHub 免费运行)
- ✅ 按需执行 (只在触发时运行)
- ✅ 完全无状态 (每次独立运行)
- ✅ 易于维护 (纯脚本,无复杂依赖)

## 🛠️ 本地开发

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入你的配置
```

### 运行脚本

```bash
python main.py
```

## 📊 消息示例

```
🌅 早安!今天是 2026年01月02日 星期五
今天是今年第 2 天

━━━━━━━━━━━━━━━━━━━━

📊 2026 年度进度
░░░░░░░░░░░░░░░░░░░░ 0.5% (2/365)

━━━━━━━━━━━━━━━━━━━━

💻 昨日编程
• 创建了 PR: fix: some bug
• 本周贡献: 连续 5 天 🔥

🌍 多邻国
• 今日未完成 ⚠️ (连续 678 天)
• 学习语言: 英语
• 总经验值: 23,286 XP

━━━━━━━━━━━━━━━━━━━━

📝 每日一诗
《静夜思》
床前明月光，疑是地上霜。
举头望明月，低头思故乡。

—— 唐代·李白
```

## 🔮 未来计划

- [ ] 修复小米运动和微信读书数据源
- [ ] Apple Health 数据集成
- [ ] 更多数据源 (天气、豆瓣、知乎等)
- [ ] 自定义消息模板
- [ ] Web Dashboard
- [ ] 周报/月报功能

## 🤝 贡献

欢迎提 Issue 和 PR!

## 📝 License

MIT License

## 🙏 致谢

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [今日诗词 API](https://www.jinrishici.com/)
- 所有开源数据源项目

---

Made with ❤️ and ☕
