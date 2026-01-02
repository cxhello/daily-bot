"""数据源基类"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class DataSource(ABC):
    """数据源抽象基类"""

    @abstractmethod
    async def fetch_data(self) -> Dict[str, Any]:
        """获取数据

        Returns:
            数据字典
        """
        pass

    @abstractmethod
    def format_message(self, data: Dict[str, Any]) -> str:
        """格式化消息

        Args:
            data: 数据字典

        Returns:
            格式化后的消息字符串
        """
        pass
