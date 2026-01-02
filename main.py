"""每日简报脚本 - GitHub Actions 版本"""
import asyncio
import logging
import sys

from config import config
from collector import collect_all_data
from notifiers import get_notifier

# 配置日志
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def main():
    """主函数"""
    try:
        # 验证必需配置
        try:
            config.validate()
        except ValueError as e:
            logger.error(f"❌ 配置验证失败: {e}")
            sys.exit(1)

        logger.info("📊 开始生成每日简报...")

        # 创建通知器
        logger.info(f"📱 初始化通知器: {config.NOTIFIER_TYPE}")
        notifier = get_notifier(config)
        if not notifier:
            logger.error("❌ 通知器创建失败")
            sys.exit(1)

        # 收集数据
        logger.info("📊 收集数据中...")
        data = await collect_all_data()

        # 发送消息 (通知器内部会自动格式化)
        logger.info(f"📤 发送消息到 {config.NOTIFIER_TYPE}...")
        success = await notifier.send_message(data)

        if success:
            logger.info("🎉 每日简报生成完成!")
            sys.exit(0)
        else:
            logger.error("💥 每日简报发送失败!")
            sys.exit(1)

    except Exception as e:
        logger.error(f"💥 运行出错: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
