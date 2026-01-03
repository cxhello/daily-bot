"""Apple Health 数据源

通过 iOS 快捷指令传入健康数据（步数和睡眠时长）
"""
import logging
from typing import Dict, Any
from config import config

logger = logging.getLogger(__name__)


async def get_health_stats() -> Dict[str, Any]:
    """从环境变量读取 Apple Health 数据

    Returns:
        包含步数和睡眠数据的字典
    """
    steps_str = config.APPLE_HEALTH_STEPS
    sleep_hours_str = config.APPLE_HEALTH_SLEEP_HOURS

    # 安全解析步数
    try:
        steps_int = int(steps_str) if steps_str else 0
        # 合理性检查：步数应该在 0 - 100000 之间
        steps_int = min(max(steps_int, 0), 100000)
    except ValueError:
        logger.warning(f"Invalid steps value: {steps_str}")
        steps_int = 0

    # 安全解析睡眠时长
    try:
        sleep_float = float(sleep_hours_str) if sleep_hours_str else 0.0
        # 合理性检查：睡眠时长应该在 0 - 24 小时之间
        sleep_float = min(max(sleep_float, 0.0), 24.0)
    except ValueError:
        logger.warning(f"Invalid sleep_hours value: {sleep_hours_str}")
        sleep_float = 0.0

    logger.info(f"Apple Health data parsed - steps: {steps_int}, sleep: {sleep_float}h")

    return {
        "steps": steps_int,
        "sleep_hours": sleep_float,
    }


def format_health_message(data: Dict[str, Any]) -> str:
    """格式化 Apple Health 消息

    Args:
        data: 健康数据字典

    Returns:
        格式化后的消息字符串
    """
    lines = ["💪 昨日健康"]

    steps = data.get("steps", 0)
    if steps > 0:
        # 步数目标：10000 步
        emoji = "✅" if steps >= config.STEP_GOAL else "📊"
        lines.append(f"• 步数: {steps:,} 步 {emoji}")

    sleep_hours = data.get("sleep_hours", 0)
    if sleep_hours > 0:
        # 睡眠目标：7 小时
        emoji = "✅" if sleep_hours >= config.SLEEP_GOAL_HOURS else "⚠️"
        lines.append(f"• 睡眠: {sleep_hours:.1f} 小时 {emoji}")

    # 如果没有任何数据
    if steps == 0 and sleep_hours == 0:
        lines.append("• 暂无数据")

    return "\n".join(lines)
