"""每日诗词数据源"""
import logging
import aiohttp
from typing import Dict, Any

logger = logging.getLogger(__name__)
SENTENCE_API = "https://v2.jinrishici.com/one.json"

DEFAULT_POEM = """《苦笋》
赏花归去马如飞,
去马如飞酒力微,
酒力微醒时已暮,
醒时已暮赏花归。

—— 宋·苏轼"""


async def get_daily_poem() -> Dict[str, Any]:
    """获取每日诗词

    Returns:
        包含诗词数据的字典
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(SENTENCE_API, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()

                    origin = data.get("data", {}).get("origin", {})
                    title = origin.get("title", "")
                    dynasty = origin.get("dynasty", "")
                    author = origin.get("author", "")
                    content_list = origin.get("content", [])

                    if content_list and title and author:
                        content = "\n".join(content_list)
                        poem = f"《{title}》\n{content}\n\n—— {dynasty}·{author}"
                        return {"poem": poem}

        return {"poem": DEFAULT_POEM}

    except Exception as e:
        logger.error(f"获取诗词失败: {e}")
        return {"poem": DEFAULT_POEM}


def format_poem_message(data: Dict[str, Any]) -> str:
    """格式化诗词消息"""
    poem = data.get("poem", DEFAULT_POEM)
    return f"📝 每日一诗\n{poem}"
