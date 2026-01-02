"""微信读书数据源

参考:
- 微信读书 Web API
- https://github.com/arry-lee/weread-exporter
"""
import asyncio
from typing import Dict, Any, List
import requests
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class WereadAPI:
    """微信读书 API 封装

    获取 Cookie 方式:
    1. 浏览器登录 weread.qq.com
    2. F12 打开开发者工具
    3. Network -> 刷新页面 -> 找到任意请求
    4. Headers -> Cookie -> 复制完整 Cookie
    """

    BASE_URL = "https://i.weread.qq.com"

    def __init__(self, cookie: str):
        self.headers = {
            "Cookie": cookie,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Referer": "https://weread.qq.com/",
        }

    def get_reading_stats(self):
        """获取阅读统计

        Returns:
            dict: 阅读统计数据
        """
        try:
            # 使用笔记本同步接口获取阅读数据
            url = f"{self.BASE_URL}/user/notebooks"

            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                data = response.json()

                # 检查是否登录成功
                if "synckey" in data or "books" in data:
                    logger.info("微信读书数据获取成功")
                    return data
                else:
                    logger.error(f"微信读书登录失败,返回数据: {data}")
                    return None
            else:
                logger.error(f"微信读书请求失败: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"微信读书获取数据异常: {e}")
            return None

    def get_reading_time(self):
        """获取阅读时长统计

        Returns:
            dict: 阅读时长数据
        """
        try:
            # 尝试使用 readinfo 端点
            url = f"{self.BASE_URL}/book/readinfo"

            response = requests.get(url, headers=self.headers, timeout=10)
            logger.info(f"微信读书 readinfo 响应状态: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                return data

            # 如果 readinfo 失败,尝试 readdata/detail
            logger.info("尝试 readdata/detail 端点")
            url = f"{self.BASE_URL}/readdata/detail"
            response = requests.get(url, headers=self.headers, timeout=10)
            logger.info(f"微信读书 readdata/detail 响应状态: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                return data
            else:
                logger.error(f"获取阅读时长失败: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"获取阅读时长异常: {e}")
            return None

    def get_shelf_books(self):
        """获取书架上的书籍

        Returns:
            list: 书籍列表
        """
        try:
            url = f"{self.BASE_URL}/shelf/sync"
            params = {"synckey": 0, "lectureSynckey": 0}

            response = requests.get(url, headers=self.headers, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return data.get("books", [])
            else:
                logger.error(f"获取书架失败: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"获取书架异常: {e}")
            return []


async def get_weread_stats(cookie: str) -> Dict[str, Any]:
    """获取微信读书统计数据

    Args:
        cookie: 微信读书 Cookie

    Returns:
        包含微信读书数据的字典
    """
    # 在线程池中运行同步代码
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _get_weread_stats_sync, cookie)


def _get_weread_stats_sync(cookie: str) -> Dict[str, Any]:
    """同步版本的微信读书统计数据获取"""
    try:
        api = WereadAPI(cookie)

        # 获取阅读时长统计
        reading_time = api.get_reading_time()

        if not reading_time:
            return {
                "error": "获取阅读数据失败,请检查 Cookie 是否有效",
                "yesterday_minutes": 0,
                "current_books": [],
                "monthly_minutes": 0,
            }

        # 获取书架上的书
        books = api.get_shelf_books()

        # 筛选在读的书
        reading_books = []
        for book in books[:20]:  # 限制数量,避免太多
            progress = book.get("readingProgress", 0)
            # 进度在 1-99% 之间的认为是在读
            if 0 < progress < 100:
                reading_books.append({
                    "title": book.get("title", "未知"),
                    "author": book.get("author", ""),
                    "progress": progress,
                    "cover": book.get("cover", ""),
                })

        # 解析阅读时长数据
        yesterday_minutes = reading_time.get("yesterdayReadingTime", 0) // 60
        monthly_minutes = reading_time.get("monthReadingTime", 0) // 60
        total_minutes = reading_time.get("totalReadingTime", 0) // 60

        # 获取本周阅读时长 (如果有的话)
        week_minutes = reading_time.get("weekReadingTime", 0) // 60

        return {
            "yesterday_minutes": yesterday_minutes,
            "current_books": reading_books[:3],  # 最多返回3本在读的书
            "monthly_minutes": monthly_minutes,
            "weekly_minutes": week_minutes,
            "total_hours": total_minutes // 60,
            "finished_books": reading_time.get("finishedBookCount", 0),
        }

    except Exception as e:
        logger.error(f"获取微信读书数据失败: {e}")
        return {
            "error": str(e),
            "yesterday_minutes": 0,
            "current_books": [],
            "monthly_minutes": 0,
        }


def format_weread_message(data: Dict[str, Any]) -> str:
    """格式化微信读书消息"""
    lines = ["📚 昨日阅读"]

    # 错误处理
    if "error" in data:
        lines.append(f"• ⚠️  {data['error']}")
        return "\n".join(lines)

    # 昨日阅读时长
    minutes = data.get("yesterday_minutes", 0)
    if minutes > 0:
        hours = minutes // 60
        remaining_mins = minutes % 60
        if hours > 0:
            lines.append(f"• 阅读时长: {hours}小时{remaining_mins}分钟")
        else:
            lines.append(f"• 阅读时长: {minutes}分钟")
    else:
        lines.append("• 昨日未阅读")

    # 在读书籍
    books = data.get("current_books", [])
    if books:
        for book in books[:2]:  # 最多显示2本
            title = book["title"]
            progress = book["progress"]
            lines.append(f"• 《{title}》进度: {progress}%")

    # 本月阅读统计
    monthly_minutes = data.get("monthly_minutes", 0)
    if monthly_minutes > 0:
        monthly_hours = monthly_minutes // 60
        if monthly_hours > 0:
            lines.append(f"• 本月累计: {monthly_hours}小时")
        else:
            lines.append(f"• 本月累计: {monthly_minutes}分钟")

    # 总阅读时长
    total_hours = data.get("total_hours", 0)
    if total_hours > 0:
        lines.append(f"• 总阅读: {total_hours}小时")

    # 完成书籍数
    finished = data.get("finished_books", 0)
    if finished > 0:
        lines.append(f"• 已读完: {finished}本")

    return "\n".join(lines)
