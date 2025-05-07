from nonebot.adapters.onebot.v11 import MessageSegment, Message
from nonebot.adapters.onebot.v11 import GROUP, Bot, Event
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.log import logger
from nonebot import on_command
from nonebot.params import CommandArg
#加载文件操作系统
import json
#加载读取系统时间相关
import datetime
#加载数学算法相关
import random
import time
#加载商店信息和商店交互
from .achievements import achievements, achievements_aliases
from .function import *
from .event import *
from .pvp import *
from .whitelist import whitelist_rule
from .config import achievement_path
from .text_image_text import generate_image_with_text, send_image_or_text_forward, send_image_or_text

#查看成就信息
ckcj = on_command('成就', aliases={"cj", "achievement", "achievements"}, permission=GROUP, priority=1, block=True, rule=whitelist_rule)
@ckcj.handle()
async def ckcj_handle(event: GroupMessageEvent, arg: Message = CommandArg()):
    user_id = str(event.user_id)
    cp_name = str(arg)
    standard_achievement = get_alias_name(cp_name, achievements, achievements_aliases)
    if(standard_achievement in achievements):
        await send_image_or_text(user_id, ckcj, standard_achievement+":\n"+achievements[standard_achievement][2], True, None, 25)
    else:
        await send_image_or_text(user_id, ckcj, '请输入正确的成就名称哦！')

#查看成就目标信息
ckcj_target = on_command('成就目标', aliases={"cj_target", "cjmb", "achievement_target", "achievements_target"}, permission=GROUP, priority=1, block=True, rule=whitelist_rule)
@ckcj_target.handle()
async def ckcj_target_handle(event: GroupMessageEvent, arg: Message = CommandArg()):
    user_id = str(event.user_id)
    cp_name = str(arg)
    standard_achievement = get_alias_name(cp_name, achievements, achievements_aliases)
    if(standard_achievement in achievements):
        await send_image_or_text(user_id, ckcj_target, standard_achievement+":\n"+achievements[standard_achievement][1], True, None, 25)
    else:
        await send_image_or_text(user_id, ckcj_target, '请输入正确的成就名称哦！')

#查看自身所持有的成就
ckcjlist = on_command('mycj', aliases={"mycj", "myachievement", "myachievements"}, permission=GROUP, priority=1, block=True, rule=whitelist_rule)
@ckcjlist.handle()
async def ckcjlist_handle(bot: Bot, event: GroupMessageEvent):
    # 打开文件
    data = open_data(full_path)
    achievement_data = open_data(achievement_path)
    user_id = event.get_user_id()

    # 读取成就个数并转发消息
    if str(user_id) in data:
        
        # 这里调用函数先添加成就
        achievement_data = achievement_get(str(user_id))
        
        # 检查是否有成就
        if 'achievement' not in achievement_data[str(user_id)] or len(achievement_data[str(user_id)].get('achievement', {})) <= 0:
            msg = "你还没有任何成就哦！"
            await send_image_or_text(user_id, ckcjlist, msg)

        # 有道具则读取道具名字和其对应数量
        nickname = event.sender.nickname
        achievements_list = [
            (k, v) for k, v in achievement_data[str(user_id)]['achievement'].items() if v > 0
        ]

        # 按数量降序排序
        achievements_list.sort(key=lambda x: x[1], reverse=True)

        # 构建成就列表文本
        text = f"【{nickname}的成就列表】\n"
        for k, v in achievements_list:
            text += f"\n· {k} ×{v}"
        
        await send_image_or_text_forward(user_id, ckcjlist, text, '成就列表', bot, event.self_id, event.group_id, 30, True)

    else:
        msg = "请先抓Madeline再来看成就哦！"
        await send_image_or_text(user_id, ckcjlist, msg, True)
