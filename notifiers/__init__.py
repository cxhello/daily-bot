"""通知器工厂模块"""
import logging
from typing import Optional

from .base import BaseNotifier
from .telegram import TelegramNotifier
from .dingtalk import DingTalkNotifier
from .feishu import FeishuNotifier
from .wecom import WeComNotifier

logger = logging.getLogger(__name__)


def get_notifier(config) -> Optional[BaseNotifier]:
    """创建通知器实例

    根据配置创建对应的通知器实例

    Args:
        config: 配置对象

    Returns:
        BaseNotifier: 通知器实例,如果配置不正确则返回 None
    """
    notifier_type = getattr(config, 'NOTIFIER_TYPE', 'telegram').lower()

    try:
        if notifier_type == 'telegram':
            if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
                logger.error("❌ Telegram 配置不完整")
                return None
            return TelegramNotifier(
                bot_token=config.TELEGRAM_BOT_TOKEN,
                chat_id=config.TELEGRAM_CHAT_ID
            )

        elif notifier_type == 'dingtalk':
            if not config.DINGTALK_WEBHOOK:
                logger.error("❌ 钉钉 Webhook URL 未配置")
                return None
            return DingTalkNotifier(
                webhook_url=config.DINGTALK_WEBHOOK,
                secret=getattr(config, 'DINGTALK_SECRET', None)
            )

        elif notifier_type == 'feishu':
            if not config.FEISHU_WEBHOOK:
                logger.error("❌ 飞书 Webhook URL 未配置")
                return None
            return FeishuNotifier(
                webhook_url=config.FEISHU_WEBHOOK
            )

        elif notifier_type == 'wecom':
            if not config.WECOM_WEBHOOK:
                logger.error("❌ 企业微信 Webhook URL 未配置")
                return None
            return WeComNotifier(
                webhook_url=config.WECOM_WEBHOOK
            )

        else:
            logger.error(f"❌ 不支持的通知器类型: {notifier_type}")
            return None

    except AttributeError as e:
        logger.error(f"❌ 配置缺失: {e}")
        return None


__all__ = ['get_notifier', 'BaseNotifier', 'TelegramNotifier', 'DingTalkNotifier', 'FeishuNotifier', 'WeComNotifier']
