"""小米运动数据源

参考:
- https://github.com/yihong0618/running_page
- https://github.com/georgehuan1994/Zepp-Life-Data-Download
"""
import asyncio
from typing import Dict, Any
import requests
import hashlib
import time
import random
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class XiaomiSportAPI:
    """小米运动 API 封装"""

    # 小米运动 API 基础 URL (华米 Zepp Life)
    LOGIN_URL = "https://api-user.huami.com/registrations/{}/tokens"
    ACCOUNT_URL = "https://account.huami.com/v2/client/login"

    def __init__(self, username: str, password: str):
        self.session = requests.Session()
        self.username = username
        self.password = password
        self.access_token = None
        self.user_id = None

        # 设置通用请求头
        self.session.headers.update({
            "User-Agent": "MiFit/4.6.0 (iPhone; iOS 14.0; Scale/2.00)",
            "Content-Type": "application/x-www-form-urlencoded",
        })

    def login(self):
        """登录小米运动

        Returns:
            bool: 登录是否成功
        """
        try:
            # 第一步: 使用手机号/邮箱和密码登录
            # 密码需要 MD5 加密
            password_hash = hashlib.md5(self.password.encode()).hexdigest()

            # 生成随机设备 ID
            device_id = self._generate_device_id()

            # 构造登录数据
            login_data = {
                "country_code": "CN",
                "device_id": device_id,
                "device_model": "iPhone",
                "app_version": "4.6.0",
                "device_type": "ios",
                "third_name": "huami_phone",
            }

            # 如果是邮箱登录
            if "@" in self.username:
                login_url = self.LOGIN_URL.format(self.username.replace("@", "%40"))
                login_data["client_id"] = "HuaMi"
                login_data["password"] = password_hash
                login_data["redirect_uri"] = "https://s3-us-west-2.amazonaws.com/hm-registration/successsignin.html"
            else:
                # 手机号登录 - 需要加国家代码
                login_url = self.ACCOUNT_URL
                # 如果手机号没有 + 前缀,自动添加 +86 (中国)
                phone = self.username if self.username.startswith("+") else f"+86{self.username}"
                login_data["account"] = phone
                login_data["password"] = password_hash
                login_data["grant_type"] = "password"
                logger.info(f"使用手机号登录: {phone}")

            response = self.session.post(login_url, data=login_data)

            logger.info(f"登录响应状态: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                logger.info(f"登录响应: {result}")

                # 检查是否登录成功
                if "token_info" in result:
                    self.access_token = result["token_info"]["access_token"]
                    self.user_id = result["token_info"]["user_id"]
                    logger.info(f"小米运动登录成功: user_id={self.user_id}")
                    return True
                elif "access_token" in result:
                    self.access_token = result["access_token"]
                    self.user_id = result.get("user_id")
                    logger.info(f"小米运动登录成功: user_id={self.user_id}")
                    return True
                else:
                    logger.error(f"登录失败,返回数据: {result}")
                    return False
            else:
                logger.error(f"登录请求失败: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"小米运动登录异常: {e}", exc_info=True)
            return False

    def _generate_device_id(self):
        """生成随机设备 ID"""
        return hashlib.md5(str(random.random()).encode()).hexdigest()

    def get_steps_data(self, date: datetime):
        """获取步数数据

        Args:
            date: 日期

        Returns:
            dict: 步数数据
        """
        try:
            if not self.access_token:
                logger.error("未登录,无法获取步数数据")
                return None

            # 小米运动步数 API (可能需要调整)
            url = f"https://api-mifit.huami.com/v1/sport/run/history.json"

            date_str = date.strftime("%Y-%m-%d")

            params = {
                "date": date_str,
                "source": "run,walk",
            }

            headers = {
                "apptoken": self.access_token,
            }

            response = self.session.get(url, params=params, headers=headers)

            if response.status_code == 200:
                data = response.json()
                logger.info(f"步数数据获取成功: {data}")
                return data.get("data", {})
            else:
                logger.error(f"获取步数失败: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"获取步数异常: {e}", exc_info=True)
            return None

    def get_sleep_data(self, date: datetime):
        """获取睡眠数据

        Args:
            date: 日期

        Returns:
            dict: 睡眠数据
        """
        try:
            if not self.access_token:
                logger.error("未登录,无法获取睡眠数据")
                return None

            # 小米运动睡眠 API
            url = f"https://api-mifit.huami.com/v1/sleep/stay_bed"

            date_str = date.strftime("%Y-%m-%d")

            params = {
                "date": date_str,
            }

            headers = {
                "apptoken": self.access_token,
            }

            response = self.session.get(url, params=params, headers=headers)

            if response.status_code == 200:
                data = response.json()
                logger.info(f"睡眠数据获取成功: {data}")
                return data.get("data", {})
            else:
                logger.error(f"获取睡眠失败: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"获取睡眠异常: {e}", exc_info=True)
            return None


async def get_xiaomi_stats(username: str, password: str) -> Dict[str, Any]:
    """获取小米运动统计数据

    Args:
        username: 小米账号 (手机号或邮箱)
        password: 密码

    Returns:
        包含小米运动数据的字典
    """
    # 在线程池中运行同步代码
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _get_xiaomi_stats_sync, username, password)


def _get_xiaomi_stats_sync(username: str, password: str) -> Dict[str, Any]:
    """同步版本的小米运动统计数据获取"""
    try:
        api = XiaomiSportAPI(username, password)

        # 登录
        if not api.login():
            return {
                "error": "登录失败,请检查账号密码",
                "sleep": {},
                "steps": 0,
                "running": {},
            }

        # 获取昨天的数据
        yesterday = datetime.now() - timedelta(days=1)

        # 获取睡眠数据
        sleep_data = api.get_sleep_data(yesterday)

        # 获取步数数据
        steps_data = api.get_steps_data(yesterday)

        # 解析数据
        result = {
            "sleep": {},
            "steps": 0,
            "running": {},
        }

        # 睡眠数据
        if sleep_data:
            total_sleep = sleep_data.get("total_stay_bed_time", 0)
            deep_sleep = sleep_data.get("deep_sleep_time", 0)
            start_time = sleep_data.get("start", 0)

            if total_sleep > 0:
                result["sleep"] = {
                    "total_hours": total_sleep / 3600,  # 转换为小时
                    "deep_hours": deep_sleep / 3600,
                    "sleep_start": time.strftime("%H:%M", time.localtime(start_time)),
                }

        # 步数数据
        if steps_data:
            result["steps"] = steps_data.get("steps", 0)

            # 跑步数据
            distance = steps_data.get("distance", 0)
            if distance > 0:
                result["running"] = {
                    "distance_km": distance / 1000,  # 转换为公里
                    "week_total_km": 0,  # 需要额外查询
                }

        return result

    except Exception as e:
        logger.error(f"获取小米运动数据失败: {e}", exc_info=True)
        return {
            "error": str(e),
            "sleep": {},
            "steps": 0,
            "running": {},
        }


def format_xiaomi_message(data: Dict[str, Any]) -> str:
    """格式化小米运动消息"""
    lines = []

    # 错误处理
    if "error" in data:
        lines.append(f"⚠️  小米运动: {data['error']}")
        return "\n".join(lines)

    # 睡眠数据
    sleep = data.get("sleep", {})
    if sleep:
        lines.append("😴 昨日睡眠")
        total_hours = sleep.get("total_hours", 0)
        if total_hours > 0:
            emoji = "✅" if total_hours >= 7 else "⚠️"
            lines.append(f"• 睡眠时长: {total_hours:.1f}小时 {emoji}")

            deep_hours = sleep.get("deep_hours", 0)
            if deep_hours > 0:
                lines.append(f"• 深度睡眠: {deep_hours:.1f}小时")

            sleep_start = sleep.get("sleep_start")
            if sleep_start:
                lines.append(f"• 入睡时间: {sleep_start}")

    # 运动数据
    steps = data.get("steps", 0)
    if steps > 0 or sleep:  # 如果有睡眠数据,也显示运动部分
        if lines:  # 如果前面有睡眠数据,添加空行
            lines.append("")
        lines.append("🏃 昨日运动")

        if steps > 0:
            lines.append(f"• 步数: {steps:,} 步")
        else:
            lines.append("• 昨日未运动")

    running = data.get("running", {})
    if running.get("distance_km"):
        distance = running["distance_km"]
        lines.append(f"• 跑步: {distance:.1f} 公里")

        week_total = running.get("week_total_km", 0)
        if week_total > 0:
            lines.append(f"• 本周累计: {week_total:.1f} 公里")

    return "\n".join(lines)
