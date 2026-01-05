"""历史上的今天数据源"""
import logging
import random
import aiohttp
import pendulum
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

WIKIMEDIA_API = "https://api.wikimedia.org/feed/v1/wikipedia/zh/onthisday/events/{month}/{day}"
USER_AGENT = "DailyBot/1.0 (https://github.com/cxhello/daily-bot; daily report bot)"


async def get_history_today_events(birth_year: int) -> Optional[Dict[str, Any]]:
    """获取历史上的今天事件

    Args:
        birth_year: 出生年份，用于筛选事件和计算年龄

    Returns:
        包含事件列表的字典，格式:
        {
            "events": [{"year": 2000, "text": "事件描述", "age": 11}, ...],
            "count": 5
        }
        失败时返回 None
    """
    try:
        # 获取当前日期（北京时间）
        now = pendulum.now("Asia/Shanghai")
        month = now.month
        day = now.day
        current_year = now.year

        # 构建 API URL
        url = WIKIMEDIA_API.format(month=month, day=day)
        headers = {"User-Agent": USER_AGENT}

        # 请求 API
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status != 200:
                    logger.error(f"⚠️ Wikimedia API 返回状态码: {response.status}")
                    return None

                data = await response.json()

                # 提取事件列表
                events = data.get("events", [])
                if not events:
                    logger.warning("⚠️ API 返回空事件列表")
                    return None

                # 筛选出生年份之后的事件
                filtered_events = [
                    event for event in events
                    if event.get("year", 0) >= birth_year and event.get("year", 0) <= current_year
                ]

                if not filtered_events:
                    logger.warning(f"⚠️ 没有找到 {birth_year} 年之后的事件")
                    return None

                # 按年份降序排序
                filtered_events.sort(key=lambda x: x.get("year", 0), reverse=True)

                # 随机选择最多 5 个事件
                selected_count = min(5, len(filtered_events))
                selected_events = random.sample(filtered_events, selected_count)

                # 按年份降序排序（保证显示时从近到远）
                selected_events.sort(key=lambda x: x.get("year", 0), reverse=True)

                # 计算年龄并格式化
                result_events = []
                for event in selected_events:
                    year = event.get("year")
                    text = event.get("text", "")
                    age = year - birth_year

                    result_events.append({
                        "year": year,
                        "text": text,
                        "age": age
                    })

                logger.info(f"✅ 历史事件获取成功: {len(result_events)} 个事件")

                return {
                    "events": result_events,
                    "count": len(result_events)
                }

    except Exception as e:
        logger.error(f"⚠️ 历史事件获取失败: {e}")
        return None


def format_history_message(history_data: Optional[Dict[str, Any]]) -> str:
    """格式化历史事件消息

    Args:
        history_data: 历史事件数据

    Returns:
        格式化后的消息字符串，如果没有数据则返回空字符串
    """
    if not history_data or not history_data.get("events"):
        return ""

    lines = ["📜 历史上的今天", ""]

    for event in history_data["events"]:
        year = event["year"]
        text = event["text"]
        age = event["age"]
        lines.append(f"{year}年 - {text} (那年我 {age} 岁)")

    return "\n".join(lines)
