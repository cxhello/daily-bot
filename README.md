# 📊 Daily Report Bot

[中文文档](./README_CN.md) | [English](./README.md)

> An automated daily report system based on GitHub Actions that aggregates your GitHub activities, learning progress, daily poems, and more.

## ✨ Features

- 🚀 **Completely Free** - Based on GitHub Actions, no server required
- 📱 **One-Tap Mobile Trigger** - iOS Shortcuts / Android HTTP Shortcuts
- ⏰ **Optional Scheduling** - Support for cron scheduled tasks
- 📊 **Multiple Data Sources** - GitHub, Duolingo, WeRead, Xiaomi Sports, and more
- 📝 **Daily Poetry** - Chinese classical poetry to enrich your day
- 📜 **History Today** - Wikipedia historical events with personalized age display
- 🔔 **Multi-Platform Notifications** - Support for Telegram, DingTalk, Feishu, and WeChat Work
- 🎯 **Highly Configurable** - Enable/disable individual feature modules

## 📦 Supported Data Sources

| Data Source | Status | Description |
|-------------|--------|-------------|
| GitHub Stats | ✅ Available | PR, Issue, Commit activities |
| Duolingo | ✅ Available | Learning days, XP, streak |
| Daily Poetry | ✅ Available | Random Chinese classical poetry |
| Steam Games | ✅ Available | Game time, library statistics |
| History Today | ✅ Available | Wikipedia historical events with personalized age |
| Xiaomi Sports | ⚠️ Needs Fix | API changes require updates |
| WeRead | ⚠️ Needs Fix | Needs verification and fixes |
| Apple Health | 🚧 In Development | Steps, sleep data (requires iOS Shortcuts) |

## 🔔 Supported Notification Platforms

| Platform | Configuration Type | Features |
|----------|-------------------|----------|
| Telegram | `telegram` | International mainstream, powerful features |
| DingTalk | `dingtalk` | Supports HMAC-SHA256 signing |
| Feishu | `feishu` | ByteDance enterprise communication |
| WeChat Work | `wecom` | Tencent enterprise communication, supports Markdown |

## 🚀 Quick Start

### 1. Fork This Repository

Click the Fork button in the upper right corner to copy it to your account.

### 2. Configure Secrets and Variables

Go to repository `Settings` → `Secrets and variables` → `Actions`:

**Notification Platform Configuration (choose one):**

Using Telegram:
- `TELEGRAM_BOT_TOKEN` - Telegram Bot Token
- `TELEGRAM_CHAT_ID` - Telegram Chat ID

Using DingTalk:
- `DINGTALK_WEBHOOK` - DingTalk robot Webhook URL
- `DINGTALK_SECRET` - Signing secret (optional)

Using Feishu:
- `FEISHU_WEBHOOK` - Feishu robot Webhook URL

Using WeChat Work:
- `WECOM_WEBHOOK` - WeChat Work robot Webhook URL

**Variables Configuration:**
- `NOTIFIER_TYPE` - Notifier type: `telegram`/`dingtalk`/`feishu`/`wecom` (default `telegram`)

**Optional Data Source Configuration:**
- `GITHUB_TOKEN` - GitHub Personal Access Token
- `GITHUB_USERNAME` - GitHub username
- `DUOLINGO_USERNAME` - Duolingo username
- `DUOLINGO_JWT_TOKEN` - Duolingo JWT Token
- `XIAOMI_USERNAME` - Xiaomi account
- `XIAOMI_PASSWORD` - Xiaomi password
- `WEREAD_COOKIE` - WeRead Cookie
- `STEAM_API_KEY` - Steam Web API Key
- `STEAM_ID` - Steam ID64
- `ENABLE_HISTORY_TODAY` - History Today toggle
- `BIRTH_YEAR` - Birth year (for personalized age display)

### 3. Trigger Execution

**Method 1: GitHub Web Interface**
- Go to Actions → Daily Report → Run workflow

**Method 2: One-Tap Mobile Trigger**
- iOS: Use Shortcuts app to send HTTP request to GitHub API
- Android: Use HTTP Shortcuts app to trigger workflow

**Method 3: Automatic Scheduling**
- Edit `.github/workflows/daily.yml`
- Uncomment the schedule section

## 🏗️ Architecture

```
Mobile Trigger → GitHub Actions → Python Script → Data Collection → Multi-Platform Push
                                                                   ├─ Telegram
                                                                   ├─ DingTalk
                                                                   ├─ Feishu
                                                                   └─ WeChat Work
```

**Advantages:**
- ✅ No server required (runs free on GitHub)
- ✅ On-demand execution (runs only when triggered)
- ✅ Completely stateless (each run is independent)
- ✅ Easy to maintain (pure scripts, no complex dependencies)

## 🛠️ Local Development

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your configuration
```

### Run Script

```bash
python main.py
```

## 📊 Message Example

```
🌅 Good morning! Today is Friday, January 2, 2026
Day 2 of the year

━━━━━━━━━━━━━━━━━━━━

📊 2026 Year Progress
░░░░░░░░░░░░░░░░░░░░ 0.5% (2/365)

━━━━━━━━━━━━━━━━━━━━

💻 Yesterday's Coding
• Created PR: fix: some bug
• Weekly contributions: 5 days streak 🔥

🌍 Duolingo
• Not completed today ⚠️ (678 day streak)
• Learning language: English
• Total XP: 23,286 XP

━━━━━━━━━━━━━━━━━━━━

📝 Daily Poetry
"Quiet Night Thought"
Moonlight before my bed,
I suspect it's frost on the ground.
Lifting my head, I gaze at the bright moon,
Lowering it, I think of my hometown.

—— Li Bai, Tang Dynasty
```

## 🔮 Future Plans

- [ ] Fix Xiaomi Sports and WeRead data sources
- [ ] Apple Health data integration (requires iOS Shortcuts)
- [ ] More gaming platforms (PlayStation, Xbox, etc.)
- [ ] More data sources (weather, Douban, Zhihu, etc.)
- [ ] Custom message templates
- [ ] Web Dashboard
- [ ] Weekly/monthly report features

## 🤝 Contributing

Issues and Pull Requests are welcome!

## 📝 License

MIT License

## 🙏 Acknowledgments

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [Jinrishici API](https://www.jinrishici.com/)
- All open source data source projects

---

Made with ❤️ and ☕
