"""消息格式化工具"""
from typing import Dict, Any
from utils.progress_bar import get_year_progress, get_day_info
from data_sources import github, xiaomi, weread, duolingo, poem


def format_daily_message(data: Dict[str, Any]) -> str:
    """格式化每日消息

    Args:
        data: 包含所有数据的字典

    Returns:
        格式化后的消息字符串
    """
    sections = []

    # 标题和日期
    day_info = get_day_info()
    header = f"🌅 早安!今天是 {day_info['date']} 星期{day_info['weekday']}\n\n"
    header += f"今天是今年第 {day_info['day_of_year']} 天"
    sections.append(header)

    # 年度进度
    sections.append("━━━━━━━━━━━━━━━━━━━━")
    year_progress = get_year_progress()
    sections.append(f"📊 {datetime.now().year} 年度进度\n{year_progress}")

    # 数据部分
    sections.append("━━━━━━━━━━━━━━━━━━━━")

    sources = data.get("sources", {})

    # 小米运动数据
    if "xiaomi" in sources:
        msg = xiaomi.format_xiaomi_message(sources["xiaomi"])
        sections.append(msg)

    # GitHub 数据
    if "github" in sources:
        msg = github.format_github_message(sources["github"])
        sections.append(msg)

    # 微信读书数据
    if "weread" in sources:
        sections.append("━━━━━━━━━━━━━━━━━━━━")
        msg = weread.format_weread_message(sources["weread"])
        sections.append(msg)

    # 多邻国数据
    if "duolingo" in sources:
        msg = duolingo.format_duolingo_message(sources["duolingo"])
        sections.append(msg)

    # 诗词
    if "poem" in sources:
        sections.append("━━━━━━━━━━━━━━━━━━━━")
        msg = poem.format_poem_message(sources["poem"])
        sections.append(msg)

    # 错误信息(如果有)
    errors = data.get("errors", [])
    if errors:
        sections.append("━━━━━━━━━━━━━━━━━━━━")
        sections.append("⚠️ 部分数据获取失败:")
        for error in errors[:3]:  # 最多显示3个错误
            sections.append(f"• {error}")

    return "\n\n".join(sections)


from datetime import datetime
