"""GitHub 数据源"""
import asyncio
import logging
from typing import Dict, Any
import pendulum
import requests

logger = logging.getLogger(__name__)
TIMEZONE = "Asia/Shanghai"


def _get_repo_name_from_url(url):
    """从仓库 URL 中提取仓库名称"""
    return "/".join(url.split("/")[-2:])


def _make_api_request(url, headers, params=None):
    """统一的 API 请求函数"""
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"API 请求失败: {response.status_code}"
    except Exception as e:
        return None, f"请求出错: {e}"


def _process_search_items(items, username, item_type):
    """处理搜索结果（PR 或 Issue）"""
    activities = []
    action_text = "创建了 PR" if item_type == "pr" else "创建了 Issue"

    for item in items:
        try:
            user = item.get("user", {})
            if user.get("login") == username:
                repo_url = item.get("repository_url", "")
                repo_name = _get_repo_name_from_url(repo_url) if repo_url else "Unknown"
                title = item.get("title", "No title")
                url = item.get("html_url", "")
                activities.append({
                    "type": item_type,
                    "action": "created",
                    "title": title,
                    "url": url,
                    "repo": repo_name,
                })
        except Exception as e:
            logger.warning(f"处理 {item_type} 数据时出错: {e}")
            continue

    return activities


def _process_events(events, yesterday_start, yesterday_end):
    """处理用户事件"""
    activities = []

    logger.info(f"开始处理事件，时间范围: {yesterday_start} 到 {yesterday_end}")
    logger.info(f"收到 {len(events)} 个事件")

    for event in events[:100]:
        try:
            created_at = event.get("created_at")
            if not created_at:
                continue

            event_created = pendulum.parse(created_at)

            if event_created < yesterday_start:
                logger.debug(f"事件时间 {event_created} 早于起始时间，停止处理")
                break

            if not (yesterday_start <= event_created <= yesterday_end):
                logger.debug(f"事件时间 {event_created} 不在目标范围内")
                continue

            if not event.get("public", True):
                logger.debug("跳过私有事件")
                continue

            event_type = event.get("type")
            if not event_type:
                continue

            repo = event.get("repo", {})
            repo_name = repo.get("name", "Unknown")

            logger.debug(f"处理事件: type={event_type}, repo={repo_name}, time={event_created}")

            if event_type == "PullRequestEvent":
                action = event.get("payload", {}).get("action")
                pr_data = event.get("payload", {}).get("pull_request", {})

                logger.info(f"PullRequestEvent: action={action}, merged={pr_data.get('merged')}, repo={repo_name}")

                # GitHub API 两种情况都要支持：
                # 1. action="merged" (某些 webhook 事件)
                # 2. action="closed" 且 pull_request.merged=true (标准 Events API)
                is_merged = (
                    action == "merged" or
                    (action == "closed" and pr_data.get("merged") is True)
                )

                if is_merged:
                    # 如果 pr_data 为空，尝试从其他地方获取信息
                    title = pr_data.get("title") if pr_data else None
                    url = pr_data.get("html_url") if pr_data else None

                    # 如果没有详细数据，使用基本信息
                    if not title:
                        title = f"PR in {repo_name}"
                        logger.warning(f"PR 缺少完整数据，使用仓库名称作为标题")

                    logger.info(f"✅ 找到合并的 PR: {title}")
                    activities.append({
                        "type": "pr",
                        "action": "merged",
                        "title": title,
                        "url": url or f"https://github.com/{repo_name}",
                        "repo": repo_name,
                    })
                else:
                    logger.debug(f"PR 不符合合并条件: action={action}, merged={pr_data.get('merged')}")
            elif event_type == "IssuesEvent":
                action = event.get("payload", {}).get("action")
                if action == "closed":
                    issue_data = event.get("payload", {}).get("issue", {})
                    activities.append({
                        "type": "issue",
                        "action": "closed",
                        "title": issue_data.get("title", "No title"),
                        "url": issue_data.get("html_url", ""),
                        "repo": repo_name,
                    })
            elif event_type == "WatchEvent":
                action = event.get("payload", {}).get("action")
                if action == "started":
                    activities.append({
                        "type": "star",
                        "action": "starred",
                        "repo": repo_name,
                        "url": f"https://github.com/{repo_name}",
                    })
            elif event_type == "PushEvent":
                # 统计 commits
                commits_count = len(event.get("payload", {}).get("commits", []))
                if commits_count > 0:
                    activities.append({
                        "type": "push",
                        "action": "pushed",
                        "commits": commits_count,
                        "repo": repo_name,
                    })
        except Exception as e:
            logger.warning(f"处理事件时出错: {e}")
            continue

    logger.info(f"事件处理完成，共找到 {len(activities)} 个活动")
    return activities


def _calculate_streak(username: str, headers: Dict[str, str]) -> int:
    """计算连续贡献天数（最近7天）

    Args:
        username: GitHub 用户名
        headers: API 请求头

    Returns:
        int: 连续贡献天数
    """
    try:
        now = pendulum.now(TIMEZONE)
        events_url = f"https://api.github.com/users/{username}/events"

        # 获取最近的事件（多获取几页以确保覆盖7天）
        all_events = []
        for page in range(1, 6):  # 获取5页，每页30个事件
            events_data, error = _make_api_request(
                events_url,
                headers,
                {"page": page, "per_page": 30}
            )

            if error or not events_data:
                break

            all_events.extend(events_data)

            if len(events_data) < 30:
                break

        # 按日期分组活动
        activity_dates = set()
        for event in all_events:
            try:
                created_at = event.get("created_at")
                if created_at:
                    event_time = pendulum.parse(created_at).in_timezone(TIMEZONE)
                    # 只记录日期（年-月-日）
                    date_str = event_time.format("YYYY-MM-DD")
                    activity_dates.add(date_str)
            except Exception as e:
                logger.debug(f"解析事件时间出错: {e}")
                continue

        logger.info(f"最近有活动的日期: {sorted(activity_dates, reverse=True)[:7]}")

        # 从昨天开始往回查，计算连续天数
        streak = 0
        for i in range(7):
            check_date = now.subtract(days=i+1)  # 从昨天开始（i+1）
            date_str = check_date.format("YYYY-MM-DD")

            if date_str in activity_dates:
                streak += 1
                logger.debug(f"✅ {date_str} 有活动")
            else:
                logger.debug(f"❌ {date_str} 无活动，连续中断")
                break  # 一旦有一天没活动，连续就中断了

        logger.info(f"连续贡献天数: {streak} 天")
        return streak

    except Exception as e:
        logger.error(f"计算连续天数出错: {e}")
        return 0


async def get_github_stats(token: str, username: str) -> Dict[str, Any]:
    """获取 GitHub 统计数据

    Args:
        token: GitHub Token
        username: GitHub 用户名

    Returns:
        包含 GitHub 数据的字典
    """
    # 在线程池中运行同步代码
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _get_github_stats_sync, token, username)


def _get_github_stats_sync(token: str, username: str) -> Dict[str, Any]:
    """同步版本的 GitHub 统计数据获取"""
    try:
        # 时间设置
        yesterday = pendulum.now(TIMEZONE).subtract(days=1)
        yesterday_start = yesterday.start_of("day").in_timezone("UTC")
        yesterday_end = yesterday.end_of("day").in_timezone("UTC")
        yesterday_date = yesterday.format("YYYY-MM-DD")

        # 请求头设置
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }

        all_activities = []

        # 获取创建的 PR
        search_url = "https://api.github.com/search/issues"
        pr_query = f"is:pr is:public author:{username} created:{yesterday_date}"
        pr_data, error = _make_api_request(
            search_url,
            headers,
            {"q": pr_query, "per_page": 100},
        )
        if pr_data:
            pr_items = pr_data.get("items", [])
            pr_activities = _process_search_items(pr_items, username, "pr")
            all_activities.extend(pr_activities)

        # 获取创建的 Issue
        issue_query = f"is:issue is:public author:{username} created:{yesterday_date}"
        issue_data, error = _make_api_request(
            search_url,
            headers,
            {"q": issue_query, "per_page": 100},
        )
        if issue_data:
            issue_items = issue_data.get("items", [])
            issue_activities = _process_search_items(issue_items, username, "issue")
            all_activities.extend(issue_activities)

        # 获取其他事件（合并、关闭、Star、Push 等）
        events_url = f"https://api.github.com/users/{username}/events"

        for page in range(1, 4):  # 检查前3页
            page_params = {"page": page, "per_page": 30}
            events_data, error = _make_api_request(events_url, headers, page_params)

            if error or not events_data:
                break

            page_activities = _process_events(
                events_data, yesterday_start, yesterday_end
            )
            all_activities.extend(page_activities)

            if len(events_data) < 30:
                break

        # 统计数据
        logger.info(f"总共收集到 {len(all_activities)} 个活动")

        commits_count = sum(
            a.get("commits", 0) for a in all_activities if a["type"] == "push"
        )
        prs_created = [a for a in all_activities if a["type"] == "pr" and a["action"] == "created"]
        prs_merged = [a for a in all_activities if a["type"] == "pr" and a["action"] == "merged"]
        issues_closed = [a for a in all_activities if a["type"] == "issue" and a["action"] == "closed"]
        stars = [a for a in all_activities if a["type"] == "star"]

        logger.info(f"统计: commits={commits_count}, PRs创建={len(prs_created)}, PRs合并={len(prs_merged)}, Issues关闭={len(issues_closed)}, Stars={len(stars)}")

        # 计算连续贡献天数
        week_streak = _calculate_streak(username, headers)

        return {
            "commits": commits_count,
            "prs_created": prs_created,
            "prs_merged": prs_merged,
            "issues_closed": issues_closed,
            "stars": stars,
            "week_streak": week_streak,
            "has_activity": len(all_activities) > 0,
        }

    except Exception as e:
        logger.error(f"GitHub 数据获取失败: {e}")
        return {
            "commits": 0,
            "prs_created": [],
            "prs_merged": [],
            "issues_closed": [],
            "stars": [],
            "week_streak": 0,
            "has_activity": False,
            "error": str(e),
        }


def format_github_message(data: Dict[str, Any]) -> str:
    """格式化 GitHub 消息"""
    if not data.get("has_activity"):
        return "💻 昨日编程\n• 昨天没有 GitHub 活动"

    lines = ["💻 昨日编程"]

    # Commits
    commits = data.get("commits", 0)
    if commits > 0:
        lines.append(f"• 提交了 {commits} 个 commits")

    # 创建的 PR
    prs_created = data.get("prs_created", [])
    for pr in prs_created[:3]:  # 最多显示3个
        lines.append(f"• 创建了 PR: [{pr['title']}]({pr['url']}) ({pr['repo']})")

    # 合并的 PR
    prs_merged = data.get("prs_merged", [])
    for pr in prs_merged[:2]:  # 最多显示2个
        lines.append(f"• 合并了 PR: [{pr['title']}]({pr['url']}) ({pr['repo']})")

    # 关闭的 Issue
    issues_closed = data.get("issues_closed", [])
    for issue in issues_closed[:2]:  # 最多显示2个
        lines.append(f"• 关闭了 Issue: [{issue['title']}]({issue['url']}) ({issue['repo']})")

    # Star
    stars = data.get("stars", [])
    for star in stars[:2]:  # 最多显示2个
        lines.append(f"• Star 了项目: [{star['repo']}]({star['url']})")

    # 连续天数
    week_streak = data.get("week_streak", 0)
    if week_streak > 0:
        lines.append(f"• 本周贡献: 连续 {week_streak} 天 🔥")

    return "\n".join(lines)
