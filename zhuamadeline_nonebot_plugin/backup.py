from pathlib import Path
import datetime
from nonebot import require, get_driver, on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from .config import user_path, backup_path, zhuama_group, bot_owner_id
from nonebot.log import logger
from .whitelist import whitelist_rule
from nonebot import get_bot
import asyncio
import shutil
from nonebot.exception import FinishedException  # 新增导入

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

async def cleanup_old_backups(max_backups=100):
    """清理旧备份，保留最多max_backups个"""
    try:
        # 获取所有备份文件夹并按创建时间排序
        backups = sorted(backup_path.glob("Backup_*"), key=lambda x: x.stat().st_ctime)
        
        # 如果超过限制数量，删除最旧的
        if len(backups) > max_backups:
            for old_backup in backups[:len(backups)-max_backups]:
                shutil.rmtree(old_backup)
                logger.info(f"已删除旧备份: {old_backup}")
                
    except Exception as e:
        logger.error(f"清理旧备份时出错: {e}")

async def backup_user_data(bot: Bot = None, group_id = int):
    """备份用户数据"""
    if not user_path.exists():
        logger.warning("用户数据目录不存在，跳过备份")
        return False
    
    try:
        # 创建 Backup 文件夹（如果不存在）
        backup_path.mkdir(parents=True, exist_ok=True)

        # 生成带时间的备份文件夹名（精确到分钟）
        backup_dir = backup_path / f"Backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}"

        # 如果文件夹已存在，先删除再重新创建
        if backup_dir.exists():
            shutil.rmtree(backup_dir)

        # 复制新数据
        shutil.copytree(user_path, backup_dir)
        logger.success(f"用户数据已备份到：{backup_dir}")

        # 清理旧备份
        await cleanup_old_backups()

        # 发送完成通知到指定群
        if bot and zhuama_group:
            backups = sorted(backup_path.glob("Backup_*"), key=lambda x: x.stat().st_ctime)
            message = f"用户数据备份已完成\n当前备份数量: {len(backups)}/100"
            await bot.send_group_msg(group_id=group_id, message=message)
        
        return True
        
    except Exception as e:
        logger.error(f"备份过程中发生错误: {e}")
        return False

# 每天凌晨4点定时备份
@scheduler.scheduled_job("cron", hour=4, minute=0, id="daily_backup")
async def daily_backup():
    try:
        bot = get_bot()
        await backup_user_data(bot, zhuama_group)
    except Exception as e:
        logger.error(f"定时备份失败: {e}")

# # 启动时立即备份（可选）
# @get_driver().on_startup
# async def test_backup():
#     try:
#         logger.info("等待5秒后开始备份...")
#         await asyncio.sleep(5)
#         bot = get_bot()
#         await backup_user_data(bot, zhuama_group)
#     except Exception as e:
#         logger.error(f"启动备份失败: {e}")