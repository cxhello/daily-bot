"""通知器基类"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseNotifier(ABC):
    """消息通知器基类
    
    所有通知平台都需要继承这个基类并实现以下方法:
    - send_message: 发送消息
    - format_message: 格式化消息 (可选,不同平台格式不同)
    """
    
    @abstractmethod
    async def send_message(self, data: Dict[str, Any]) -> bool:
        """发送消息
        
        Args:
            data: 收集到的数据字典
            
        Returns:
            bool: 发送是否成功
        """
        pass
    
    def format_message(self, data: Dict[str, Any]) -> str:
        """格式化消息
        
        默认使用通用格式化函数,子类可以重写以适配特定平台
        
        Args:
            data: 收集到的数据字典
            
        Returns:
            str: 格式化后的消息文本
        """
        from utils.message_formatter import format_daily_message
        return format_daily_message(data)
