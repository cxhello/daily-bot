"""多邻国数据源

参考:
- Duolingo API: https://duolingo-api.fandom.com/wiki/Duolingo_API_Wiki
- https://github.com/KartikTalwar/Duolingo
"""
import asyncio
from typing import Dict, Any
import requests
import logging

logger = logging.getLogger(__name__)


class DuolingoAPI:
    """多邻国 API 封装"""

    BASE_URL = "https://www.duolingo.com"

    def __init__(self, username: str, jwt_token: str = None):
        self.session = requests.Session()
        self.username = username
        self.jwt = jwt_token
        self.user_id = None

        # 设置更真实的请求头,避免被识别为爬虫
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Content-Type": "application/json",
        })

        # 如果有 JWT token,添加到请求头
        if self.jwt:
            self.session.headers.update({
                "Authorization": f"Bearer {self.jwt}"
            })
            logger.info("使用 JWT token 认证")

    def verify_token(self):
        """验证 JWT token 是否有效

        Returns:
            bool: token 是否有效
        """
        if not self.jwt:
            logger.error("未提供 JWT token")
            return False

        try:
            # 通过获取用户信息来验证 token
            url = f"{self.BASE_URL}/users/{self.username}"

            logger.info(f"验证 JWT token,请求 URL: {url}")
            logger.info(f"Authorization header: Bearer {self.jwt[:20]}...{self.jwt[-20:]}")

            response = self.session.get(url)

            logger.info(f"响应状态: {response.status_code}")
            logger.info(f"响应内容: {response.text[:500]}")

            if response.status_code == 200:
                data = response.json()
                self.user_id = data.get("id")
                logger.info(f"JWT token 有效: user_id={self.user_id}")
                return True
            else:
                logger.error(f"JWT token 验证失败: {response.status_code}")
                logger.error(f"完整响应: {response.text[:1000]}")
                return False

        except Exception as e:
            logger.error(f"JWT token 验证异常: {e}", exc_info=True)
            return False

    def get_user_info(self):
        """获取用户信息

        Returns:
            dict: 用户信息,包含连续学习天数、XP 等
        """
        try:
            if not self.jwt:
                logger.error("未提供 JWT token")
                return None

            # 先获取基本用户信息以得到 user_id
            if not self.user_id:
                url = f"{self.BASE_URL}/users/{self.username}"
                response = self.session.get(url)
                if response.status_code == 200:
                    user_data = response.json()
                    self.user_id = user_data.get("id")
                else:
                    logger.error(f"获取用户基本信息失败: {response.status_code}")
                    return None

            # 使用 v2 API 获取详细信息
            url = f"{self.BASE_URL}/2017-06-30/users/{self.user_id}"
            response = self.session.get(url)

            if response.status_code == 200:
                data = response.json()

                return {
                    "streak": data.get("streak", 0),  # 连续学习天数
                    "xp_today": data.get("xpGainedToday", 0),  # 今日 XP
                    "total_xp": data.get("totalXp", 0),  # 总 XP
                    "lingots": data.get("lingots", 0),  # 虚拟货币
                    "learning_language": data.get("learningLanguage", ""),
                    "xp_goal": data.get("xpGoal", 20),  # 每日目标
                    "has_plus": data.get("hasPlus", False),  # 是否为 Plus 会员
                }
            else:
                logger.error(f"获取用户详细信息失败: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"获取用户信息异常: {e}")
            return None

    def get_calendar_data(self):
        """获取日历数据 (用于判断今天是否完成练习)

        Returns:
            dict: 日历数据
        """
        try:
            if not self.username:
                return None

            url = f"{self.BASE_URL}/users/{self.username}"
            response = self.session.get(url)

            if response.status_code == 200:
                data = response.json()
                return data.get("calendar", [])
            else:
                logger.error(f"获取日历数据失败: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"获取日历数据异常: {e}")
            return None


async def get_duolingo_stats(username: str, jwt_token: str) -> Dict[str, Any]:
    """获取多邻国统计数据

    Args:
        username: 多邻国用户名
        jwt_token: JWT token (从浏览器 Cookie 获取)

    Returns:
        包含多邻国数据的字典
    """
    # 在线程池中运行同步代码
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _get_duolingo_stats_sync, username, jwt_token)


def _get_duolingo_stats_sync(username: str, jwt_token: str) -> Dict[str, Any]:
    """同步版本的多邻国统计数据获取"""
    try:
        api = DuolingoAPI(username, jwt_token)

        # 验证 token
        if not api.verify_token():
            return {
                "error": "JWT token 无效或已过期,请重新获取",
                "streak": 0,
                "completed_today": False,
                "words_to_review": 0,
            }

        # 获取用户信息
        user_info = api.get_user_info()

        if not user_info:
            return {
                "error": "获取用户信息失败",
                "streak": 0,
                "completed_today": False,
                "words_to_review": 0,
            }

        # 判断今天是否完成
        xp_today = user_info.get("xp_today", 0)
        xp_goal = user_info.get("xp_goal", 20)
        completed_today = xp_today >= xp_goal

        return {
            "streak": user_info.get("streak", 0),
            "completed_today": completed_today,
            "xp_today": xp_today,
            "xp_goal": xp_goal,
            "total_xp": user_info.get("total_xp", 0),
            "learning_language": user_info.get("learning_language", ""),
            # 多邻国没有直接的"待复习单词"API,这里返回一个估算值
            "words_to_review": max(0, xp_goal - xp_today) // 10,  # 假设每个单词约 10 XP
        }

    except Exception as e:
        logger.error(f"获取多邻国数据失败: {e}")
        return {
            "error": str(e),
            "streak": 0,
            "completed_today": False,
            "words_to_review": 0,
        }


def format_duolingo_message(data: Dict[str, Any]) -> str:
    """格式化多邻国消息"""
    lines = ["🌍 多邻国"]

    # 错误处理
    if "error" in data:
        lines.append(f"• ⚠️  获取数据失败: {data['error']}")
        return "\n".join(lines)

    streak = data.get("streak", 0)
    completed = data.get("completed_today", False)
    xp_today = data.get("xp_today", 0)
    xp_goal = data.get("xp_goal", 20)

    # 完成状态
    if completed:
        lines.append(f"• 今日完成练习 ✅ (连续 {streak} 天)")
    else:
        if xp_today > 0:
            lines.append(f"• 今日进度: {xp_today}/{xp_goal} XP (连续 {streak} 天)")
        else:
            lines.append(f"• 今日未完成 ⚠️ (连续 {streak} 天)")

    # 学习语言
    if language := data.get("learning_language"):
        language_map = {
            "en": "英语",
            "es": "西班牙语",
            "fr": "法语",
            "de": "德语",
            "ja": "日语",
            "ko": "韩语",
            "zh": "中文",
        }
        language_name = language_map.get(language, language)
        lines.append(f"• 学习语言: {language_name}")

    # 总 XP
    if total_xp := data.get("total_xp"):
        lines.append(f"• 总经验值: {total_xp:,} XP")

    return "\n".join(lines)
