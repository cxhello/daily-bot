"""Telegram 通知器"""
import logging
from typing import Dict, Any
from telegram import Bot

from .base import BaseNotifier

logger = logging.getLogger(__name__)


class TelegramNotifier(BaseNotifier):
    """Telegram 消息通知器"""
    
    def __init__(self, bot_token: str, chat_id: str):
        """初始化 Telegram 通知器
        
        Args:
            bot_token: Telegram Bot Token
            chat_id: Telegram Chat ID
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
    
    async def send_message(self, data: Dict[str, Any]) -> bool:
        """发送消息到 Telegram
        
        Args:
            data: 数据字典
            
        Returns:
            bool: 发送是否成功
        """
        try:
            message = self.format_message(data)
            
            bot = Bot(token=self.bot_token)
            await bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode="Markdown",
                disable_web_page_preview=True,
            )
            
            logger.info("✅ Telegram 消息发送成功!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Telegram 消息发送失败: {e}")
            return False
    
    def format_message(self, data: Dict[str, Any]) -> str:
        """格式化 Telegram 消息
        
        Telegram 支持 Markdown 格式
        """
        return super().format_message(data)
