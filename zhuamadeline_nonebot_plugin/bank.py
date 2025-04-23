from nonebot.adapters.onebot.v11 import MessageSegment, Message
from nonebot.adapters.onebot.v11 import GROUP
from nonebot.adapters.onebot.v11 import Bot, Event, GroupMessageEvent
from nonebot import on_command, get_bots
from nonebot.params import CommandArg
from nonebot.log import logger

#导入定时任务库
from nonebot import require
require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

#加载读取系统时间相关
import time
import datetime
#加载数学算法相关
import random
import json
from pathlib import Path
from .config import *
from .list1 import *
from .list2 import *
from .list3 import *
from .list4 import *
from .function import *
from .whitelist import whitelist_rule
from .text_image_text import generate_image_with_text, send_image_or_text_forward, send_image_or_text, auto_send_message

# 用户数据文件路径
full_path = Path() / "data" / "UserList" / "UserData.json"
bar_path = Path() / "data" / "UserList" / "bar.json"
demon_path = Path() / "data" / "UserList" / "demon.json"
pvp_path = Path() / "data" / "UserList" / "pvp.json"

# 1:00重置报酬发放状态防止没执行
async def cancel_interest_send():
    bar_data = open_data(bar_path)
    bar_data["interest_send"] = False
    save_data(bar_path, bar_data)

# 2:00执行一次报酬发放
async def add_interest():
    bots = get_bots()
    if not bots:
        logger.error("没有可用的Bot实例，无法发放报酬！")
        return
    bot = list(bots.values())[0]
    
    bar_data = open_data(bar_path)
    bar_data.setdefault("pots", 0)
    
    # 检查是否已发放报酬
    if bar_data.get("interest_send", False):
        return
    
    add_pots = 0
    for user_id, user_bar in bar_data.items():
        if user_id.isdigit() and isinstance(user_bar, dict):
            user_bar.setdefault("bank", 0)
            user_bar.setdefault("interest", 0)
            user_bar.setdefault("interest_today", 0)
            
            if user_bar["bank"] > 0:
                bank = user_bar["bank"]
                interest = 0
            
                # 第一段：≤50,000，1/100
                part1 = min(bank, 50000)
                interest += int(part1 * 0.01)
            
                # 第二段：50,001~100,000，1/200
                if bank > 50000:
                    part2 = min(bank - 50000, 50000)
                    interest += int(part2 * 0.005)
                    # 第二段 add_pots = (part2的1/100) - (part2 * 0.005)，也就是5w-1w之间的50%
                    add_pots += int(part2 * 0.01) - int(part2 * 0.005)
            
                # 第三段：>100,000，1/1000
                if bank > 100000:
                    part3 = bank - 100000
                    interest += int(part3 * 0.001)
                    # 第三段 add_pots = (part3的1/100) - (part3 * 0.001)，也就是大于10w的90%
                    add_pots += int(part3 * 0.01) - int(part3 * 0.001)
                
                user_bar["interest_today"] = interest
                user_bar["interest"] += interest
                user_bar["bank"] += interest
    
    bar_data["pots"] += add_pots
    bar_data["interest_send"] = True
    save_data(bar_path, bar_data)
    
    message = "今日报酬已发放，请使用命令 .ck all\n查看今天增加报酬（向下取整）为多少哦~"

    await auto_send_message(message, bot, zhuama_group)

scheduler.scheduled_job("cron", hour=2, minute=0)(add_interest)
scheduler.scheduled_job("cron", hour=1, minute=0)(cancel_interest_send)

# 提取草莓命令
bank = on_command('bank', aliases = {"berrybank"}, permission=GROUP, priority=1, block=True, rule=whitelist_rule)

@bank.handle()
async def bank_handle(bot: Bot, event: GroupMessageEvent, arg: Message = CommandArg()):
    user_id = str(event.get_user_id())
    args = arg.extract_plain_text().strip().lower().split()
    now = datetime.datetime.now()

    # 参数校验
    if len(args) != 2:
        await send_image_or_text(bank, "指令格式错误，请使用：\n.bank save/take 数量/all", at_sender=True)
        return

    access, berry_number = args
    data = open_data(full_path)
    bar_data = open_data(bar_path)

    # 用户数据校验
    if user_id not in data:
        await send_image_or_text(bank, "请先抓一次Madeline再使用仓库哦！", at_sender=True)
        return

    user_data = data.setdefault(user_id, {})
    user_data.setdefault('berry', 0)

    if user_data['berry'] < 0:
        await send_image_or_text(bank, f"你现在仍处于失约状态中……\n不允许使用草莓仓库！\n你只有{data[user_id]['berry']}颗草莓！", at_sender=True)
        return

    # 初始化仓库数据
    user_bar = bar_data.setdefault(user_id, {})
    user_bar.setdefault("status","nothing")
    user_bar.setdefault("game","1")
    user_bar.setdefault("last_pvp_guess_berry", -1)
    user_bar.setdefault("bank",0)
    try:
        if access == "save":
            # 存入逻辑
            # 检查时间限制
            if not (8 <= now.hour < 20):
                await send_image_or_text(bank, "每天 8:00 - 20:00 才能进行存放哦！", at_sender=True)
                return
            if berry_number == "all":
                deposit = user_data['berry']
                if deposit <= 0:
                    await send_image_or_text(bank, "你当前没有草莓可以存入！", at_sender=True)
                    return
            else:
                deposit = int(berry_number)
                if deposit <= 0:
                    await send_image_or_text(bank, "草莓存入数必须是大于0的整数哦！", at_sender=True)
                    return
                if user_data['berry'] < deposit:
                    await send_image_or_text(bank, f"存入失败，你只有{user_data['berry']}颗草莓\n不足以存入{deposit}颗草莓哦！", at_sender=True)
                    return

            user_data['berry'] -= deposit
            user_bar['bank'] += deposit
            action = f"存入{deposit}颗草莓"

        elif access == "take":
            # 取出逻辑
            if berry_number == "all":
                withdraw = user_bar['bank']
                if withdraw <= 0:
                    await send_image_or_text(bank, "你的仓库账户空空如也！", at_sender=True)
                    return
            else:
                withdraw = int(berry_number)
                if withdraw <= 0:
                    await send_image_or_text(bank, "草莓取出数必须是大于0的整数哦！", at_sender=True)
                    return
                if user_bar['bank'] < withdraw:
                    await send_image_or_text(bank, f"取出失败，仓库只有{user_bar['bank']}颗草莓！", at_sender=True)
                    return

            user_bar['bank'] -= withdraw
            user_data['berry'] += withdraw
            action = f"取出{withdraw}颗草莓"

        else:
            await send_image_or_text(bank, "指令格式错误，请使用：\n.bank save/take 数量/all", at_sender=True)
            return

        # 保存数据并响应
        save_data(full_path, data)
        save_data(bar_path, bar_data)
        
        message = (
            f"{action}成功！\n"
            f"\n当前持有草莓：{user_data['berry']}颗"
            f"\n仓库草莓余额：{user_bar['bank']}颗"
        )
        await send_image_or_text(bank, message, at_sender=True)

    except ValueError:
        await send_image_or_text(bank, "指令格式错误，请使用：\n.bank save/take 数量/all", at_sender=True)