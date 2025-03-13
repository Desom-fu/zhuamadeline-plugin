from nonebot.adapters.onebot.v11 import MessageSegment, Message
from nonebot.adapters.onebot.v11 import GROUP
from nonebot.adapters.onebot.v11 import Bot, Event, GroupMessageEvent
from nonebot.params import CommandArg
from nonebot.log import logger
from nonebot import on_command, on_fullmatch, require
import datetime
#加载文件操作系统
import os
import math
import time
from pathlib import Path
#加载商店信息和商店交互
from .shop import item, today_item, forbid_recycle_item, fish_prices, item_aliases
from .collection import collections, collection_aliases
import json
#加载读取系统时间相关
import datetime
from .madelinejd import *
from .config import *
from .function import *
from .whitelist import whitelist_rule
from .admin import restock_shop

scheduler = require("nonebot_plugin_apscheduler").scheduler

__all__ = [
    "shop",
    "buy"
]

#商店商品查看
shop = on_fullmatch(['.shop', '。shop'], permission=GROUP, priority=1, block=True, rule=whitelist_rule)
@shop.handle()
async def madeline_shop(bot: Bot, event: Event):
    logger.info("商店系统开启成功")  #日志

    shop_data = {}
    #比较营业时间与时间点
    current_time = datetime.datetime.now().time()
    hour = current_time.hour
    if(hour < 6): await shop.finish("便利店还没开门，请再等一会吧")
    data = open_data(user_path / file_name)
    user_id = str(event.user_id)
    # 事件检测
    if data[str(user_id)].get('event',"nothing") != "nothing":
        await buy.finish("你还有正在进行中的事件", at_sender=True)
    #输出商店仓库
    current_date = datetime.date.today()  #返回今天日期
    current_date_str = current_date.strftime("%Y-%m-%d")  #日期时间对象转字符串
    if(os.path.exists(shop_database)):

        #打开商店仓库
        shop_data = open_data(shop_database)

        #根据是否为同一天来查看是否刷新商品
        previous_date_str = shop_data["date"]

        if (previous_date_str!=current_date_str):
            shop_data["item"] = today_item
            shop_data["date"] = current_date_str
            #写入商店库存
            save_data(shop_database, shop_data)
        #写入商店库存
        save_data(shop_database, shop_data)

    else:
        shop_data["item"] = today_item
        shop_data["date"] = current_date_str
        
        #写入商店库存
        save_data(shop_database, shop_data)
    # 创建转发消息内容
    item_text = shop_list(shop_data["item"])
    forward_messages = [
        {
            "type": "node",
            "data": {
                "name": "商品列表",
                "uin": event.self_id,  # 设置为机器人的QQ号
                "content": item_text
            }
        }
    ]
        
    # 转发消息
    if forward_messages:
        await bot.send_group_forward_msg(
            group_id=event.group_id,  # 转发到当前群组
            messages=forward_messages
        )

# 定时任务：每天 18:00 自动补货
@scheduler.scheduled_job("cron", hour=18, minute=0)
async def auto_restock():
    await restock_shop(send_message=True)

# 购买商品
buy = on_command('buy', permission=GROUP, priority=1, block=True, rule=whitelist_rule)

@buy.handle()
async def buy_handle(event: GroupMessageEvent, arg: Message = CommandArg()):
    # 获取当前时间
    current_time = datetime.datetime.now().time()
    if current_time.hour < 6:
        await buy.finish("便利店还没开门，请再等一会吧")

    # 读取或初始化商店数据
    current_date = datetime.date.today().strftime("%Y-%m-%d")
    shop_data = open_data(shop_database) if os.path.exists(shop_database) else {}
    
    if shop_data.get("date") != current_date:
        shop_data["item"] = today_item
        shop_data["date"] = current_date
        save_data(shop_database, shop_data)

    # 读取用户数据
    user_id = str(event.get_user_id())
    group_id = str(event.group_id)
    user_data = open_data(user_path / file_name)
    if user_id not in user_data:
        await buy.finish("你还没尝试抓过madeline.....", at_sender=True)

    # 处理冷却时间
    all_cool_time(cd_path, user_id, group_id)

    # 解析购买参数
    args = str(arg).strip().lower().split()

    if len(args) == 1:
        buy_item_name = args[0]
        n = 1  # 默认为 1
    elif len(args) == 2:
        buy_item_name = args[0]
        try:
            n = int(args[1])  # 解析数量
            if n <= 0:
                await buy.finish("购买数量必须大于 0 哦~", at_sender=True)
        except ValueError:
            await buy.finish("请输入正确的道具数量哦~", at_sender=True)
    else:
        await buy.finish("请检查购买指令或购买道具/藏品名称是否正确，正确指令为 .buy 道具|藏品 数量~", at_sender=True)

    # 处理别名转换
    standard_item = get_alias_name(buy_item_name, item, item_aliases)
    standard_collection = get_alias_name(buy_item_name, collections, collection_aliases)

    # 如果匹配到道具或藏品的标准名称，就替换
    if standard_item:
        buy_item_name = standard_item
    elif standard_collection:
        buy_item_name = standard_collection

    # 检查是否是今日商品
    if buy_item_name not in today_item:
        await buy.finish("请检查购买道具/藏品名称是否正确哦~", at_sender=True)

    answer = 0
    # buy_arg = decode_buy_text(today_item, args)
    # buy_item_name, n = buy_arg[0], int(buy_arg[1])
    # if not buy_arg:
    #     await buy.send("请检查购买指令或购买道具名称是否正确，正确指令为 .buy 道具 数量~", at_sender=True)
    #     return
    
    if n <= 0:
        await buy.finish(f"你为什么会想着买{n}个商品呢？")

    # 检查商品库存
    if shop_data["item"].get(buy_item_name, 0) == 0:
        await buy.finish(f"来晚啦，{buy_item_name} 已经售空啦！")
    if shop_data["item"][buy_item_name] < n:
        await buy.finish(f"没有那么多 {buy_item_name} 了......", at_sender=True)

    # 处理购买逻辑
    try:
        pay_per = item[buy_item_name][0]  # 物品单价
        pay = n * pay_per  # 总价格

        if user_data[user_id]['berry'] < pay:
            await buy.send(f"本次你需要花费 {pay} 颗草莓，你只有 {user_data[user_id]['berry']} 颗草莓", at_sender=True)
            return

        # 扣除草莓并更新用户道具
        user_data[user_id]['berry'] -= pay
        user_data[user_id].setdefault('item', {}).setdefault(buy_item_name, 0)
        user_data[user_id]['item'][buy_item_name] += n

        # 定义道具限购
        item_limits = {
            '指南针': 1, 'madeline充能器': 1, '时间提取器': 1, '草莓加工器': 1,
            '招财猫': 20, '音矿': 2000, '残片': 29997, '安定之音': 5000,
            '神秘碎片': 5, '草莓鱼竿': 1,
        }
        if buy_item_name in item_limits and user_data[user_id]['item'][buy_item_name] > item_limits[buy_item_name]:
            await buy.finish(f"{buy_item_name} 已经到达你的获取上限啦，不能再买了！", at_sender=True)

        # 处理 "神秘碎片" 终身限购
        if buy_item_name == '神秘碎片':
            user_data[user_id].setdefault("buy_fragments_num", 0)
            if user_data[user_id]["buy_fragments_num"] + n > 5:
                await buy.finish(f"你不能买这么多，该道具终身限购 5 个，你已经购买了 {user_data[user_id]['buy_fragments_num']} 个")
            user_data[user_id]['buy_fragments_num'] += n
        answer = 0
        
    except KeyError:  # 处理购买藏品的情况
        if n >= 2:
            await buy.finish(f"藏品只能购买一个哦！")

        user_data[user_id].setdefault("collections", {})
        if user_data[user_id]['collections'].get(buy_item_name, 0) >= 1:
            await buy.finish(f"{buy_item_name} 已经到达你的获取上限啦，不能再买了！", at_sender=True)

        pay_per = collections[buy_item_name][0]
        pay = n * pay_per
        if user_data[user_id]['energy'] < pay:
            await buy.send(f"本次你需要花费 {pay} 点能量，你只有 {user_data[user_id]['energy']} 点能量", at_sender=True)
            return

        user_data[user_id]['energy'] -= pay
        user_data[user_id]['collections'][buy_item_name] = n
        answer = 1

    # 更新商店库存
    shop_data["item"][buy_item_name] -= n

    # 保存数据
    save_data(user_path / file_name, user_data)
    save_data(shop_database, shop_data)

    # 记录购买日志
    buytime = datetime.datetime.today().strftime("%H:%M:%S")
    today = datetime.date.today().strftime("%Y-%m-%d")
    bili_path = Path() / "data" / "Shop" / f"{today}.json"
    data_bili = open_data(bili_path) if os.path.exists(bili_path) else {"list": []}
    data_bili['list'].append(f"[{buytime}] {event.sender.nickname} 购买了 {n} 个 {buy_item_name}")
    save_data(bili_path, data_bili)

    # 发送购买成功消息
    if answer == 0:
        await buy.finish(f"购买成功！你还剩 {user_data[user_id]['berry']} 颗草莓！", at_sender=True)
    elif answer == 1:
        await buy.finish(f"购买成功！你还剩 {user_data[user_id]['energy']} 点能量！", at_sender=True)


# 回收道具 50%价格回收
recycle_item = on_command("recycle", permission=GROUP, priority=1, block=True, rule=whitelist_rule)
@recycle_item.handle()
async def handle_recycle_item(event: GroupMessageEvent, arg: Message = CommandArg()):
    user_id = str(event.user_id)
    # 解析参数
    args = str(arg).strip().lower().split()
    
    if len(args) not in [1, 2]:
        await recycle_item.finish("格式错误！请输入：.recycle 道具名称 (数量)", at_sender=True)
    
    # 获取道具名称
    item_name = args[0].strip()
    
    if not item_name:  # 防止用户输入空格导致 item_name 为空
        await recycle_item.finish("格式错误！请输入：.recycle 道具名称 (数量)", at_sender=True)
    
    # 进行别名转换
    standard_item = get_alias_name(item_name, item, item_aliases)
    standard_collection = get_alias_name(item_name, collections, collection_aliases)
    
    # 如果匹配到道具或藏品的标准名称，就替换
    if standard_item:
        item_name = standard_item
    elif standard_collection:
        item_name = standard_collection
    
    # 获取数量（默认 1）
    item_quantity = 1
    if len(args) == 2:
        try:
            item_quantity = int(args[1])
            if item_quantity <= 0:
                raise ValueError
        except ValueError:
            await recycle_item.finish("道具数量必须为正整数！", at_sender=True)
    # 检测道具名称是否在商品列表中
    if item_name not in item:
        await recycle_item.finish(f"现在整个抓玛德琳都没有这个道具 [{item_name}]，你为什么会想回收呢？", at_sender=True)
    # 检测道具名称是否在黑名单中
    if item_name in forbid_recycle_item:
        await recycle_item.finish(f"[{item_name}] 在道具回收黑名单中，你不能回收该道具哦！", at_sender=True)
    # 打开数据文件
    data = {}
    if not (user_path / file_name).exists():
        await recycle_item.finish("玩家数据文件不存在！", at_sender=True)
    data = open_data(user_path / file_name)
    # 检查玩家是否存在
    if user_id not in data:
        await recycle_item.finish(f"你未注册zhuamadeline账号哦！", at_sender=True)
    # 检查玩家是否有该道具
    if "item" not in data[user_id]:
        data[user_id]['item'] = {}
    if item_name not in data[user_id]["item"]:
        await recycle_item.finish(f"你没有道具 [{item_name}] 哦！", at_sender=True)
    # 检查道具数量是否足够
    if data[user_id]["item"][item_name] < item_quantity:
        await recycle_item.finish(f"你的道具 [{item_name}] 数量不足哦！", at_sender=True)
    recycle_per = int(item[item_name][0])  #查看物品单价
    
    # 鱼类全额回收
    if item_name in fish_prices:
        recycle_price = item_quantity * recycle_per
    else:
        recycle_price = (item_quantity * recycle_per) // 2 #本次回收价格（向下取整）
    
    # 扣除道具
    data[user_id]["item"][item_name] -= item_quantity
    # 如果道具数量为 0，删除该道具
    if data[user_id]["item"][item_name] <= 0:
        del data[user_id]["item"][item_name]
    #发放草莓
    data[user_id]['berry'] += recycle_price
    # 写入玩家数据文件
    save_data(user_path / file_name, data)
    owner_berry = data[user_id]['berry']
    await recycle_item.finish(f"你成功回收了{item_quantity}个{item_name}！本次回收获得{recycle_price}颗草莓！你目前拥有{owner_berry}颗草莓！", at_sender=True)