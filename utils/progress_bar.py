"""进度条生成工具"""
from datetime import datetime


def get_year_progress() -> str:
    """获取今年的进度条

    Returns:
        进度条字符串,格式: ████████░░░░░░░░░░░░ 0.3% (1/365)
    """
    now = datetime.now()
    day_of_year = now.timetuple().tm_yday

    # 判断是否为闰年
    is_leap_year = now.year % 4 == 0 and (now.year % 100 != 0 or now.year % 400 == 0)
    total_days = 366 if is_leap_year else 365

    # 计算进度百分比
    progress_percent = (day_of_year / total_days) * 100

    # 生成进度条 (20个字符宽度)
    progress_bar_width = 20
    filled_blocks = int((day_of_year / total_days) * progress_bar_width)
    empty_blocks = progress_bar_width - filled_blocks

    progress_bar = "█" * filled_blocks + "░" * empty_blocks

    return f"{progress_bar} {progress_percent:.1f}% ({day_of_year}/{total_days})"


def get_day_info() -> dict:
    """获取日期信息

    Returns:
        包含日期信息的字典
    """
    now = datetime.now()
    weekdays = ["一", "二", "三", "四", "五", "六", "日"]

    return {
        "date": now.strftime("%Y年%m月%d日"),
        "weekday": weekdays[now.weekday()],
        "day_of_year": now.timetuple().tm_yday,
    }
