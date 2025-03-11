from nonebot import require, on_command
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment, GROUP
from nonebot import get_bots
from .whitelist import whitelist_rule
from .config import zhuama_group
import httpx

NEWS_URL = "http://excerpt.rubaoo.com/toolman/getMiniNews"

scheduler = require("nonebot_plugin_apscheduler").scheduler

async def fetch_news_image():
    """获取新闻图片地址"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(NEWS_URL, timeout=10)
            data = response.json()
            return data.get("data", {}).get("image")
    except Exception as e:
        return None

@scheduler.scheduled_job("cron", hour=8, minute=0)
async def send_daily_news():
    """每天早上 8:00 发送新闻图片"""
    
    image_url = await fetch_news_image()
    text = ""
    if not image_url:
        return

    message = MessageSegment.image(image_url)
    bots = get_bots()
    if not bots:
        return
    for bot in bots.values():
        # await bot.send_private_msg(user_id=你的QQ号, message=message)  # 发送给特定用户
        text += "早上好呀！8点了，花60s来看看今日新闻吧！"
        await bot.send_group_msg(group_id=zhuama_group, message=text+message)  # 发送到群聊（解开注释）

news = on_command('60s', aliases={"60秒",'每日新闻','dailynews','1min'}, permission=GROUP, priority=1, block=True, rule=whitelist_rule)
@news.handle()
async def news_command(bot: Bot, event: Event):
    """手动触发获取新闻图片"""
    image_url = await fetch_news_image()
    if image_url:
        await bot.send(event, MessageSegment.image(image_url))
    else:
        await bot.send(event, "啊呀，获取新闻图片失败，没准是api炸了！")
