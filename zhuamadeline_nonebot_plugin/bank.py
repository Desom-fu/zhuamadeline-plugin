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

# 用户数据文件路径
full_path = Path() / "data" / "UserList" / "UserData.json"
bar_path = Path() / "data" / "UserList" / "bar.json"
demon_path = Path() / "data" / "UserList" / "demon.json"
pvp_path = Path() / "data" / "UserList" / "pvp.json"

# 设定每日 2:00 自动增加利息
async def add_interest():
    bots = get_bots()
    if not bots:
        logger.error("没有可用的Bot实例，无法发放利息！")
        return
    bot = list(bots.values())[0]  # 获取第一个 Bot 实例
    bar_data = open_data(bar_path)
    bar_data.setdefault("pots", 0)
    add_pots = 0
    interest_send = bar_data.setdefault("interest_send", False)
    if interest_send:
        return
    for user_id, user_bar in bar_data.items():
        if user_id.isdigit() and isinstance(user_bar, dict):  # 跳过非用户数据
            user_bar.setdefault("bank",0)
            user_bar.setdefault("interest", 0)  # 初始化利息
            user_bar.setdefault("interest_today", 0)  # 初始化今日利息
            if user_bar["bank"] > 0:
                interest = int(user_bar["bank"] * 0.01)  # 计算 1% 利息
                # 大于1000，超出的全部投给奖池
                if interest > 1000:
                    add_pots += interest - 750
                    interest = 750
                # 大于500，超出的部分自己获得50%，剩余的投入奖池
                elif interest > 500:
                    half = (interest - 500) // 2
                    add_pots += half
                    interest -= half
                user_bar["interest_today"] = interest  # 记录今日利息
                user_bar["interest"] += interest  # 记录总利息
                user_bar["bank"] += interest  # 利息加到银行存款中
    # 所有人的累计add_pots加上底池
    bar_data["pots"] += add_pots
    bar_data["interest_send"] = True
    save_data(bar_path, bar_data)
    # 发送通知
    await bot.send_group_msg(
        group_id=zhuama_group,
        message=f"今日利息已发放，请使用命令.ck all查看今天增加利息（向下取整）为多少哦~"
    )

#取消
def cancel_interest_send():
    bar_data = open_data(bar_path)
    bar_data.setdefault("interest_send", False)
    bar_data["interest_send"] = False
    save_data(bar_path, bar_data)

scheduler.scheduled_job("cron", hour=2, minute=0)(add_interest)
scheduler.scheduled_job("cron", hour=1, minute=0)(cancel_interest_send)

# 提取草莓命令
bank = on_command('bank', permission=GROUP, priority=1, block=True, rule=whitelist_rule)

@bank.handle()
async def bank_handle(bot: Bot, event: GroupMessageEvent, arg: Message = CommandArg()):
    user_id = str(event.get_user_id())
    args = arg.extract_plain_text().strip().lower().split()
    now = datetime.datetime.now()

    # 参数校验
    if len(args) != 2:
        await bank.finish("指令格式错误，请使用：.bank save/take 数量/all", at_sender=True)

    access, berry_number = args
    data = open_data(full_path)
    bar_data = open_data(bar_path)

    # 用户数据校验
    if user_id not in data:
        await bank.finish("请先抓一次Madeline再使用银行哦！", at_sender=True)

    user_data = data.setdefault(user_id, {})
    user_data.setdefault('berry', 0)

    if user_data['berry'] < 0:
        await bank.finish(f"你现在仍在负债中……不允许使用草莓银行！你只有{data[user_id]['berry']}颗草莓！", at_sender=True)

    # 初始化银行数据
    user_bar = bar_data.setdefault(user_id, {})
    user_bar.setdefault("status","nothing")
    user_bar.setdefault("game","1")
    user_bar.setdefault("last_pvp_guess_berry",0)
    user_bar.setdefault("bank",0)
    try:
        if access == "save":
            # 存入逻辑
            # 检查时间限制
            if not (8 <= now.hour < 20):
                await bank.finish("每天 8:00 - 20:00 才能进行存款哦！", at_sender=True)
            if berry_number == "all":
                deposit = user_data['berry']
                if deposit <= 0:
                    await bank.finish("你当前没有草莓可以存入！", at_sender=True)
            else:
                deposit = int(berry_number)
                if deposit <= 0:
                    await bank.finish("草莓存款数必须是大于0的整数哦！", at_sender=True)
                if user_data['berry'] < deposit:
                    await bank.finish(f"存款失败，你只有{user_data['berry']}颗草莓！", at_sender=True)

            user_data['berry'] -= deposit
            user_bar['bank'] += deposit
            action = f"存入{deposit}颗草莓"

        elif access == "take":
            # 取出逻辑
            if berry_number == "all":
                withdraw = user_bar['bank']
                if withdraw <= 0:
                    await bank.finish("你的银行账户空空如也！", at_sender=True)
            else:
                withdraw = int(berry_number)
                if withdraw <= 0:
                    await bank.finish("草莓取款数必须是大于0的整数哦！", at_sender=True)
                if user_bar['bank'] < withdraw:
                    await bank.finish(f"取款失败，银行只有{user_bar['bank']}颗草莓！", at_sender=True)

            user_bar['bank'] -= withdraw
            user_data['berry'] += withdraw
            action = f"取出{withdraw}颗草莓"

        else:
            await bank.finish("指令格式错误，请使用：.bank save/take 数量/all", at_sender=True)

        # 保存数据并响应
        save_data(full_path, data)
        save_data(bar_path, bar_data)
        await bank.finish(
            f"{action}成功！"
            f"\n当前持有草莓：{user_data['berry']}颗"
            f"\n银行草莓余额：{user_bar['bank']}颗",
            at_sender=True
        )

    except ValueError:
        await bank.finish("指令格式错误，请使用：.bank save/take 数量/all", at_sender=True)