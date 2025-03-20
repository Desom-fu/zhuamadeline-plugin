from nonebot.adapters.onebot.v11 import MessageSegment, Message
from nonebot.adapters.onebot.v11 import GROUP, Bot, Event
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.log import logger
from nonebot import on_command, on_fullmatch
from nonebot.params import CommandArg
#加载文件操作系统
import json
#加载读取系统时间相关
import datetime
#加载数学算法相关
import random
import time
#加载商店信息和商店交互
from .collection import collections, collection_aliases
from .function import *
from .event import *
from .pvp import *
from .whitelist import whitelist_rule
from .config import full_path

#查看藏品信息
ckcp = on_command('藏品', aliases={"cp"}, permission=GROUP, priority=1, block=True, rule=whitelist_rule)
@ckcp.handle()
async def ckcp_handle(arg: Message = CommandArg()):
    cp_name = str(arg)
    standard_collection = get_alias_name(cp_name, collections, collection_aliases)
    if(standard_collection in collections):
        await ckcp.finish(standard_collection+":\n"+collections[standard_collection][3])
    else:
        await ckcp.finish("请输入正确的藏品名称哦！", at_sender=True)

#查看自身所持有的藏品
ckcplist = on_fullmatch(['.mycp', '。mycp'], permission=GROUP, priority=1, block=True, rule=whitelist_rule)
@ckcplist.handle()
async def ckcplist_handle(bot: Bot, event: GroupMessageEvent):
    # 打开文件
    data = open_data(full_path)
    user_id = event.get_user_id()

    # 读取藏品个数并转发消息
    if str(user_id) in data:
        # 检查是否有藏品
        if 'collections' not in data[str(user_id)] or not data[str(user_id)]['collections']:
            await ckcplist.finish("你还没有任何藏品哦！", at_sender=True)

        # 有道具则读取道具名字和其对应数量
        nickname = event.sender.nickname
        collections_list = [
            (k, v) for k, v in data[str(user_id)]['collections'].items() if v > 0
        ]

        # 按数量降序排序
        collections_list.sort(key=lambda x: x[1], reverse=True)

        text = f"这是 [{nickname}] 的藏品列表\n"
        for k, v in collections_list:
            text += f"\n- {k}"

        # 转发消息
        msg_list = [
            {
                "type": "node",
                "data": {
                    "name": "藏品库存室",
                    "uin": event.self_id,
                    "content": text
                }
            }
        ]
        await bot.call_api("send_group_forward_msg", group_id=event.group_id, messages=msg_list)
    else:
        await ckcplist.finish("你还没尝试抓过madeline......", at_sender=True)
        
