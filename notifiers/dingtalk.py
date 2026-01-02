"""钉钉通知器"""
import logging
import time
import hmac
import hashlib
import base64
import urllib.parse
from typing import Dict, Any
import aiohttp

from .base import BaseNotifier

logger = logging.getLogger(__name__)


class DingTalkNotifier(BaseNotifier):
    """钉钉机器人通知器
    
    支持钉钉群机器人的 Webhook 推送
    """
    
    def __init__(self, webhook_url: str, secret: str = None):
        """初始化钉钉通知器
        
        Args:
            webhook_url: 钉钉机器人 Webhook URL
            secret: 加签密钥 (可选,推荐使用以提高安全性)
        """
        self.webhook_url = webhook_url
        self.secret = secret
    
    def _generate_sign(self) -> tuple:
        """生成钉钉加签
        
        Returns:
            (timestamp, sign): 时间戳和签名
        """
        timestamp = str(round(time.time() * 1000))
        secret_enc = self.secret.encode('utf-8')
        string_to_sign = f'{timestamp}\n{self.secret}'
        string_to_sign_enc = string_to_sign.encode('utf-8')
        
        hmac_code = hmac.new(
            secret_enc,
            string_to_sign_enc,
            digestmod=hashlib.sha256
        ).digest()
        
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return timestamp, sign
    
    async def send_message(self, data: Dict[str, Any]) -> bool:
        """发送消息到钉钉
        
        Args:
            data: 数据字典
            
        Returns:
            bool: 发送是否成功
        """
        try:
            message = self.format_message(data)
            
            # 构造 URL (如果有密钥则加签)
            url = self.webhook_url
            if self.secret:
                timestamp, sign = self._generate_sign()
                url = f"{self.webhook_url}&timestamp={timestamp}&sign={sign}"
            
            # 构造消息体
            payload = {
                "msgtype": "markdown",
                "markdown": {
                    "title": "📊 每日简报",
                    "text": message
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as resp:
                    result = await resp.json()
                    
                    if resp.status == 200 and result.get('errcode') == 0:
                        logger.info("✅ 钉钉消息发送成功!")
                        return True
                    else:
                        logger.error(f"❌ 钉钉消息发送失败: {result}")
                        return False
                        
        except Exception as e:
            logger.error(f"❌ 钉钉消息发送异常: {e}")
            return False
    
    def format_message(self, data: Dict[str, Any]) -> str:
        """格式化钉钉消息
        
        钉钉支持 Markdown 格式,但语法略有不同
        """
        # 钉钉 Markdown 格式与标准 Markdown 基本兼容
        # 只需要确保标题格式正确
        message = super().format_message(data)
        
        # 钉钉要求标题用 # 格式
        # 如果需要特殊处理,可以在这里修改
        
        return message
