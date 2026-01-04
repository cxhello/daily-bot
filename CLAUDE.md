# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A GitHub Actions-based automated daily report bot that aggregates personal data from multiple sources (GitHub, Duolingo, WeRead, Xiaomi Sports, Steam, Apple Health, History Today, daily poems) and sends notifications via multiple platforms (Telegram, DingTalk, Feishu, WeChat Work).

**Key architectural principle:** Serverless, stateless execution on GitHub Actions. All state is external - data sources are APIs and notifications are webhooks.

## Common Commands

### Local Development
```bash
# Setup
pip install -r requirements.txt
cp .env.example .env  # Edit .env with your credentials

# Run locally (uses .env for configuration)
python main.py
```

### Testing
```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_specific_file.py
```

### GitHub Actions
- Workflow dispatch: Go to Actions → Daily Report → Run workflow
- Schedule: Edit `.github/workflows/daily.yml` and uncomment the `schedule` section

## Architecture

### Entry Point
- `main.py`: Async entry point. Validates config, collects data via `collector.collect_all_data()`, sends via `notifier.send_message()`

### Configuration
- `config.py`: Central `Config` class with `validate()` method. All env vars loaded via `python-dotenv`
- Feature flags: `ENABLE_*` variables control which data sources are active
- Notifier selection: `NOTIFIER_TYPE` env var (telegram/dingtalk/feishu/wecom)

### Data Collection Pattern
All data sources follow the collector pattern defined in `collector.py`:
1. Each source has a `collect_<source>_data()` async function
2. `collect_all_data()` runs all enabled sources concurrently via `asyncio.gather()`
3. Errors are caught and logged without stopping the entire pipeline
4. Returns dict: `{"timestamp": ..., "sources": {...}, "errors": [...]}`

### Data Sources (`data_sources/`)
- `base.py`: `DataSource` ABC with `fetch_data()` and `format_message()` methods
- Each data source module exports a `get_<source>_stats()` async function
- Implementations: `github.py`, `duolingo.py`, `poem.py`, `steam.py`, `apple_health.py`, `history.py`, `weread.py`, `xiaomi.py`
- Note: `xiaomi.py` and `weread.py` are currently marked as needing fixes

### Notifiers (`notifiers/`)
- `base.py`: `BaseNotifier` ABC with `send_message(data)` abstract method
- `__init__.py`: `get_notifier(config)` factory function - instantiates the correct notifier based on `config.NOTIFIER_TYPE`
- Implementations: `telegram.py`, `dingtalk.py`, `feishu.py`, `wecom.py`
- Each notifier handles its own message formatting via `format_message()`

### Message Formatting
- `utils/message_formatter.py`: `format_daily_message(data)` creates the final message text
- `utils/progress_bar.py`: Progress bar visualization for year progress

## Adding a New Data Source

1. Create `data_sources/<source>.py` with async `get_<source>_stats(*args)` function
2. Add import and task in `collector.py` following the existing pattern:
   ```python
   if config.ENABLE_<SOURCE> and config.<SOURCE>_CREDENTIAL:
       tasks.append(("<source>", collect_<source>_data()))
   ```
3. Add feature flag `ENABLE_<SOURCE>` to `config.py`
4. Add credentials to `.env.example` and `config.py`
5. Optional: Add formatting section in `utils/message_formatter.py`

## Adding a New Notifier

1. Create `notifiers/<platform>.py` inheriting from `BaseNotifier`
2. Implement `async def send_message(self, data) -> bool`
3. Add to `notifiers/__init__.py`:
   - Import the class
   - Add case in `get_notifier()` factory
   - Add to `__all__`
4. Add config validation in `config.py:validate()`
5. Add env vars to `.env.example` and workflow in `.github/workflows/daily.yml`

## Environment Variables Reference

### Required (choose one notifier)
- `NOTIFIER_TYPE`: telegram/dingtalk/feishu/wecom
- `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` (if telegram)
- `DINGTALK_WEBHOOK` (+ `DINGTALK_SECRET` optional) (if dingtalk)
- `FEISHU_WEBHOOK` (if feishu)
- `WECOM_WEBHOOK` (if wecom)

### Optional (data sources)
- `GITHUB_TOKEN` + `GITHUB_USERNAME`: GitHub stats
- `DUOLINGO_USERNAME` + `DUOLINGO_JWT_TOKEN`: Duolingo progress
- `WEREAD_COOKIE`: WeRead reading stats
- `XIAOMI_USERNAME` + `XIAOMI_PASSWORD`: Xiaomi sports data
- `STEAM_API_KEY` + `STEAM_ID`: Steam gaming stats
- `ENABLE_HISTORY_TODAY` + `BIRTH_YEAR`: History Today events with personalized age
- `APPLE_HEALTH_STEPS` + `APPLE_HEALTH_SLEEP_HOURS`: Apple Health data (from workflow input)
- `ENABLE_*`: Feature flags for each data source

## Python Environment
- Python 3.12 (also used in GitHub Actions)
- Key dependencies: `python-telegram-bot`, `aiohttp`, `PyGithub`, `pendulum`, `python-dotenv`
