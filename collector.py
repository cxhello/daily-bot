"""数据收集协调器"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

from config import config

logger = logging.getLogger(__name__)


async def collect_all_data() -> Dict[str, Any]:
    """并发收集所有数据源的数据

    Returns:
        包含所有数据的字典
    """
    tasks = []
    data = {
        "timestamp": datetime.now(),
        "sources": {},
        "errors": [],
    }

    # GitHub 数据
    if config.ENABLE_GITHUB_STATS and config.GITHUB_TOKEN:
        tasks.append(("github", collect_github_data()))

    # 小米运动数据
    if config.ENABLE_XIAOMI_SPORT and config.XIAOMI_USERNAME:
        tasks.append(("xiaomi", collect_xiaomi_data()))

    # 微信读书数据
    if config.ENABLE_WEREAD and config.WEREAD_COOKIE:
        tasks.append(("weread", collect_weread_data()))

    # 多邻国数据
    if config.ENABLE_DUOLINGO and config.DUOLINGO_USERNAME:
        tasks.append(("duolingo", collect_duolingo_data()))

    # 诗词数据
    if config.ENABLE_POEM:
        tasks.append(("poem", collect_poem_data()))

    # Apple Health 数据
    if config.ENABLE_APPLE_HEALTH and (
        config.APPLE_HEALTH_STEPS or config.APPLE_HEALTH_SLEEP_HOURS
    ):
        tasks.append(("apple_health", collect_apple_health_data()))

    # Steam 数据
    if config.ENABLE_STEAM and config.STEAM_API_KEY and config.STEAM_ID:
        tasks.append(("steam", collect_steam_data()))

    # 并发执行所有任务
    if tasks:
        results = await asyncio.gather(
            *[task for _, task in tasks], return_exceptions=True
        )

        for i, (source_name, _) in enumerate(tasks):
            result = results[i]
            if isinstance(result, Exception):
                logger.error(f"{source_name} 数据获取失败: {result}")
                data["errors"].append(f"{source_name}: {str(result)}")
            else:
                data["sources"][source_name] = result
                logger.info(f"{source_name} 数据获取成功")

    return data


async def collect_github_data() -> Dict[str, Any]:
    """收集 GitHub 数据"""
    from data_sources.github import get_github_stats

    return await get_github_stats(config.GITHUB_TOKEN, config.GITHUB_USERNAME)


async def collect_xiaomi_data() -> Dict[str, Any]:
    """收集小米运动数据"""
    # TODO: 实现小米运动数据收集
    from data_sources.xiaomi import get_xiaomi_stats

    return await get_xiaomi_stats(config.XIAOMI_USERNAME, config.XIAOMI_PASSWORD)


async def collect_weread_data() -> Dict[str, Any]:
    """收集微信读书数据"""
    # TODO: 实现微信读书数据收集
    from data_sources.weread import get_weread_stats

    return await get_weread_stats(config.WEREAD_COOKIE)


async def collect_duolingo_data() -> Dict[str, Any]:
    """收集多邻国数据"""
    from data_sources.duolingo import get_duolingo_stats

    return await get_duolingo_stats(config.DUOLINGO_USERNAME, config.DUOLINGO_JWT_TOKEN)


async def collect_poem_data() -> Dict[str, Any]:
    """收集诗词数据"""
    # TODO: 实现诗词数据收集
    from data_sources.poem import get_daily_poem

    return await get_daily_poem()


async def collect_apple_health_data() -> Dict[str, Any]:
    """收集 Apple Health 数据"""
    from data_sources.apple_health import get_health_stats

    return await get_health_stats()


async def collect_steam_data() -> Dict[str, Any]:
    """收集 Steam 数据"""
    from data_sources.steam import get_steam_stats

    return await get_steam_stats(config.STEAM_API_KEY, config.STEAM_ID)
