"""Steam 数据源

通过 Steam Web API 获取游戏数据
参考: https://developer.valvesoftware.com/wiki/Steam_Web_API
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
import requests

logger = logging.getLogger(__name__)

# Steam API 基础 URL
STEAM_API_BASE = "https://api.steampowered.com"


class SteamAPI:
    """Steam API 封装"""

    def __init__(self, api_key: str, steam_id: str):
        self.api_key = api_key
        self.steam_id = steam_id
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        })

    def _request(self, endpoint: str, params: dict = None) -> Optional[dict]:
        """发送 API 请求"""
        try:
            url = f"{STEAM_API_BASE}/{endpoint}"
            params = params or {}
            params["key"] = self.api_key
            params["steamids"] = self.steam_id
            params["format"] = "json"

            response = self.session.get(url, params=params, timeout=10)

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Steam API 请求失败: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Steam API 异常: {e}")
            return None

    def get_player_info(self) -> Optional[dict]:
        """获取玩家基本信息"""
        data = self._request("ISteamUser/GetPlayerSummaries/v0002/")
        if data and "response" in data and "players" in data["response"]:
            players = data["response"]["players"]
            if players:
                return players[0]
        return None

    def get_owned_games(self) -> List[dict]:
        """获取拥有游戏列表"""
        try:
            url = f"{STEAM_API_BASE}/IPlayerService/GetOwnedGames/v0001/"
            params = {
                "key": self.api_key,
                "steamid": self.steam_id,
                "include_appinfo": 1,
                "include_played_free_games": 1,
                "format": "json"
            }
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data and "response" in data and "games" in data["response"]:
                    return data["response"]["games"]
            return []
        except Exception as e:
            logger.error(f"获取游戏列表失败: {e}")
            return []

    def get_recently_played(self) -> List[dict]:
        """获取最近游玩（最多 3 款游戏）"""
        try:
            url = f"{STEAM_API_BASE}/IPlayerService/GetRecentlyPlayedGames/v0001/"
            params = {
                "key": self.api_key,
                "steamid": self.steam_id,
                "count": 3,
                "format": "json"
            }
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data and "response" in data and "games" in data["response"]:
                    return data["response"]["games"]
            return []
        except Exception as e:
            logger.error(f"获取最近游戏失败: {e}")
            return []

    def get_game_schema(self, app_id: int) -> Optional[dict]:
        """获取游戏详细信息（成就等）"""
        data = self._request(
            f"ISteamUserStats/GetSchemaForGame/v2/",
            params={"appid": app_id}
        )
        if data and "game" in data:
            return data["game"]
        return None

    def get_player_achievements(self, app_id: int) -> Optional[dict]:
        """获取玩家成就"""
        data = self._request(
            f"ISteamUserStats/GetPlayerAchievements/v1/",
            params={"appid": app_id}
        )
        if data and "playerstats" in data:
            return data["playerstats"]
        return None


def _calculate_yesterday_playtime(games: List[dict]) -> float:
    """计算昨日游玩时长（小时）

    注意：Steam API 只提供总时长，无法直接获取昨日数据
    这里使用最近 2 周数据的差值估算
    """
    if not games:
        return 0.0

    # 取前 3 款游戏估算
    total_minutes = 0
    for game in games[:3]:
        minutes = game.get("playtime_2weeks", 0)
        total_minutes += minutes

    return round(total_minutes / 60, 1)


def _get_top_games(games: List[dict], limit: int = 3) -> List[dict]:
    """获取游玩时间最长的游戏"""
    sorted_games = sorted(games, key=lambda x: x.get("playtime_forever", 0), reverse=True)
    return sorted_games[:limit]


async def get_steam_stats(api_key: str, steam_id: str) -> Dict[str, Any]:
    """获取 Steam 统计数据

    Args:
        api_key: Steam Web API Key
        steam_id: Steam ID64

    Returns:
        包含 Steam 数据的字典
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _get_steam_stats_sync, api_key, steam_id)


def _get_steam_stats_sync(api_key: str, steam_id: str) -> Dict[str, Any]:
    """同步版本的 Steam 数据获取"""
    try:
        api = SteamAPI(api_key, steam_id)

        # 获取玩家信息
        player_info = api.get_player_info()

        # 获取最近游玩
        recent_games = api.get_recently_played()

        # 获取所有游戏
        all_games = api.get_owned_games()

        # 计算数据
        player_name = player_info.get("personaname", "Unknown") if player_info else "Unknown"
        avatar_url = player_info.get("avatarmedium", "") if player_info else ""

        # 昨日游玩时长（估算）
        yesterday_hours = _calculate_yesterday_playtime(recent_games)

        # 本周游玩时长（估算，基于最近 2 周数据）
        week_hours = 0
        for game in recent_games:
            week_hours += game.get("playtime_2weeks", 0) / 60

        # Top 游戏
        top_games = _get_top_games(all_games, limit=3)

        # 计算总游戏时间
        total_playtime_minutes = sum(g.get("playtime_forever", 0) for g in all_games)
        total_playtime_hours = round(total_playtime_minutes / 60, 1)

        # 构建游戏列表字符串
        recent_game_list = []
        for game in recent_games[:3]:
            name = game.get("name", "Unknown")[:20]
            minutes = game.get("playtime_2weeks", 0)
            hours = round(minutes / 60, 1)
            recent_game_list.append(f"{name} ({hours}h)")

        result = {
            "player_name": player_name,
            "avatar_url": avatar_url,
            "yesterday_hours": yesterday_hours,
            "week_hours": round(week_hours, 1),
            "total_games": len(all_games),
            "total_hours": total_playtime_hours,
            "recent_games": recent_game_list,
            "top_games": [
                {
                    "name": g.get("name", "")[:20],
                    "hours": round(g.get("playtime_forever", 0) / 60, 1)
                }
                for g in top_games
            ],
        }

        logger.info(f"Steam 数据获取成功: {result}")
        return result

    except Exception as e:
        logger.error(f"获取 Steam 数据失败: {e}", exc_info=True)
        return {
            "error": str(e),
            "player_name": "Unknown",
            "yesterday_hours": 0,
            "week_hours": 0,
            "total_games": 0,
            "total_hours": 0,
            "recent_games": [],
            "top_games": [],
        }


def format_steam_message(data: Dict[str, Any]) -> str:
    """格式化 Steam 消息"""
    lines = ["🎮 Steam 游戏"]

    # 错误处理
    if "error" in data:
        lines.append(f"• ⚠️  {data['error']}")
        return "\n".join(lines)

    # 玩家名称
    player_name = data.get("player_name", "")
    if player_name:
        lines.append(f"• 玩家: {player_name}")

    # 昨日游戏时长
    yesterday_hours = data.get("yesterday_hours", 0)
    if yesterday_hours > 0:
        lines.append(f"• 昨日时长: {yesterday_hours} 小时")
    else:
        lines.append("• 昨日未玩游戏")

    # 本周累计
    week_hours = data.get("week_hours", 0)
    if week_hours > 0:
        lines.append(f"• 本周累计: {week_hours} 小时")

    # 最近游戏
    recent_games = data.get("recent_games", [])
    if recent_games:
        lines.append("• 最近游戏:")
        for game in recent_games:
            lines.append(f"  - {game}")

    # Top 游戏
    top_games = data.get("top_games", [])
    if top_games:
        lines.append("• Top 游戏:")
        for game in top_games:
            lines.append(f"  - {game['name']}: {game['hours']}h")

    # 游戏总数
    total_games = data.get("total_games", 0)
    if total_games > 0:
        lines.append(f"• 游戏库: {total_games} 款")

    # 总游戏时间
    total_hours = data.get("total_hours", 0)
    if total_hours > 0:
        lines.append(f"• 总时长: {total_hours:.1f} h")

    return "\n".join(lines)
