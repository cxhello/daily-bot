"""飞书通知器"""
import logging
from typing import Dict, Any
import aiohttp

from .base import BaseNotifier

logger = logging.getLogger(__name__)


class FeishuNotifier(BaseNotifier):
    """飞书机器人通知器

    支持飞书群机器人的 Webhook 推送
    使用交互式卡片格式提供更好的视觉体验
    """

    def __init__(self, webhook_url: str):
        """初始化飞书通知器

        Args:
            webhook_url: 飞书机器人 Webhook URL
        """
        self.webhook_url = webhook_url

    async def send_message(self, data: Dict[str, Any]) -> bool:
        """发送消息到飞书

        Args:
            data: 数据字典

        Returns:
            bool: 发送是否成功
        """
        try:
            message = self.format_message(data)

            # 构造飞书消息体 - 使用文本格式
            payload = {
                "msg_type": "text",
                "content": {
                    "text": message
                }
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as resp:
                    result = await resp.json()

                    if resp.status == 200 and result.get('StatusCode') == 0:
                        logger.info("✅ 飞书消息发送成功!")
                        return True
                    else:
                        logger.error(f"❌ 飞书消息发送失败: {result}")
                        return False

        except Exception as e:
            logger.error(f"❌ 飞书消息发送异常: {e}")
            return False

    def format_message(self, data: Dict[str, Any]) -> str:
        """格式化飞书消息

        飞书文本格式不支持完整 Markdown
        需要转换为纯文本格式
        """
        message = super().format_message(data)

        # 飞书文本消息不支持 Markdown 链接格式
        # 将 [title](url) 转换为 title: url
        import re
        message = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'\1: \2', message)

        return message
