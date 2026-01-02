"""企业微信通知器"""
import logging
from typing import Dict, Any
import aiohttp

from .base import BaseNotifier

logger = logging.getLogger(__name__)


class WeComNotifier(BaseNotifier):
    """企业微信群机器人通知器

    支持企业微信群机器人的 Webhook 推送
    """

    def __init__(self, webhook_url: str):
        """初始化企业微信通知器

        Args:
            webhook_url: 企业微信机器人 Webhook URL
        """
        self.webhook_url = webhook_url

    async def send_message(self, data: Dict[str, Any]) -> bool:
        """发送消息到企业微信

        Args:
            data: 数据字典

        Returns:
            bool: 发送是否成功
        """
        try:
            message = self.format_message(data)

            # 构造企业微信消息体
            payload = {
                "msgtype": "markdown",
                "markdown": {
                    "content": message
                }
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as resp:
                    result = await resp.json()

                    if resp.status == 200 and result.get('errcode') == 0:
                        logger.info("✅ 企业微信消息发送成功!")
                        return True
                    else:
                        logger.error(f"❌ 企业微信消息发送失败: {result}")
                        return False

        except Exception as e:
            logger.error(f"❌ 企业微信消息发送异常: {e}")
            return False

    def format_message(self, data: Dict[str, Any]) -> str:
        """格式化企业微信消息

        企业微信支持 Markdown 格式
        """
        return super().format_message(data)
