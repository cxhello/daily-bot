"""配置管理模块"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """配置类"""

    # 通知器配置
    NOTIFIER_TYPE = os.getenv("NOTIFIER_TYPE", "telegram")  # telegram/dingtalk/feishu/wecom

    # Telegram 配置
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    # 钉钉配置
    DINGTALK_WEBHOOK = os.getenv("DINGTALK_WEBHOOK")
    DINGTALK_SECRET = os.getenv("DINGTALK_SECRET")  # 可选,加签密钥

    # 飞书配置
    FEISHU_WEBHOOK = os.getenv("FEISHU_WEBHOOK")

    # 企业微信配置
    WECOM_WEBHOOK = os.getenv("WECOM_WEBHOOK")

    # 功能开关
    ENABLE_GITHUB_ISSUE = os.getenv("ENABLE_GITHUB_ISSUE", "false").lower() == "true"
    ENABLE_XIAOMI_SPORT = os.getenv("ENABLE_XIAOMI_SPORT", "true").lower() == "true"
    ENABLE_WEREAD = os.getenv("ENABLE_WEREAD", "true").lower() == "true"
    ENABLE_DUOLINGO = os.getenv("ENABLE_DUOLINGO", "true").lower() == "true"
    ENABLE_GITHUB_STATS = os.getenv("ENABLE_GITHUB_STATS", "true").lower() == "true"
    ENABLE_POEM = os.getenv("ENABLE_POEM", "true").lower() == "true"
    ENABLE_TODO_REMINDER = (
        os.getenv("ENABLE_TODO_REMINDER", "true").lower() == "true"
    )

    # 小米运动
    XIAOMI_USERNAME = os.getenv("XIAOMI_USERNAME")
    XIAOMI_PASSWORD = os.getenv("XIAOMI_PASSWORD")

    # 微信读书
    WEREAD_COOKIE = os.getenv("WEREAD_COOKIE")

    # 多邻国
    DUOLINGO_USERNAME = os.getenv("DUOLINGO_USERNAME")
    DUOLINGO_JWT_TOKEN = os.getenv("DUOLINGO_JWT_TOKEN")

    # GitHub
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")

    # 提醒配置
    CONTACT_REMINDER_DAYS = int(os.getenv("CONTACT_REMINDER_DAYS", "7"))
    SLEEP_GOAL_HOURS = float(os.getenv("SLEEP_GOAL_HOURS", "7.5"))
    STEP_GOAL = int(os.getenv("STEP_GOAL", "10000"))

    @classmethod
    def validate(cls):
        """验证必需的配置项"""
        notifier_type = cls.NOTIFIER_TYPE.lower()

        if notifier_type == "telegram":
            if not cls.TELEGRAM_BOT_TOKEN:
                raise ValueError("TELEGRAM_BOT_TOKEN 未设置")
            if not cls.TELEGRAM_CHAT_ID:
                raise ValueError("TELEGRAM_CHAT_ID 未设置")
        elif notifier_type == "dingtalk":
            if not cls.DINGTALK_WEBHOOK:
                raise ValueError("DINGTALK_WEBHOOK 未设置")
        elif notifier_type == "feishu":
            if not cls.FEISHU_WEBHOOK:
                raise ValueError("FEISHU_WEBHOOK 未设置")
        elif notifier_type == "wecom":
            if not cls.WECOM_WEBHOOK:
                raise ValueError("WECOM_WEBHOOK 未设置")
        else:
            raise ValueError(f"不支持的通知器类型: {notifier_type}")


# 导出配置实例
config = Config()
