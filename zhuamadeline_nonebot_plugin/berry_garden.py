from nonebot.adapters.onebot.v11 import MessageSegment, Message
from nonebot.adapters.onebot.v11 import GROUP
from nonebot.adapters.onebot.v11 import Bot, Event, GroupMessageEvent
from nonebot import on_command, on_fullmatch
from nonebot.params import CommandArg
import time
import datetime
import random
import json
from pathlib import Path
from .config import *
from .function import *
from .whitelist import whitelist_rule

# 全局更新所有果园的状态
async def update_all_gardens(garden_data: dict):
    current_time = int(time.time())
    
    for user_id in garden_data:
        garden = garden_data[user_id]
        
        if garden["isseed"] == 1:
            # 基础生长时间计算（不超过24小时）
            seed_duration = current_time - garden["seed_time"]
            total_hours = min(seed_duration // 3600, 24)
            base_harvest = total_hours * 10
            
            # 有效施肥时间窗口判断
            if garden["isfert"] == 1:
                # 施肥有效期（12小时窗口）
                fert_window_start = garden["fert_time"]
                fert_window_end = fert_window_start + 12 * 3600
                
                # 播种有效期（24小时窗口）
                seed_window_start = garden["seed_time"]
                seed_window_end = seed_window_start + 24 * 3600
                
                # 计算施肥与当前播种的重叠时间
                overlap_start = max(fert_window_start, seed_window_start)
                overlap_end = min(fert_window_end, seed_window_end, current_time)
                
                if overlap_start < overlap_end:
                    fert_hours = (overlap_end - overlap_start) // 3600
                    base_harvest += fert_hours * 10  # 翻倍部分
            
            # 累积草莓产量
            garden["garden_berry"] += base_harvest
            
            # 自动过期处理（仅种子状态）
            if seed_duration >= 24 * 3600:
                garden["isseed"] = 0
    
    save_data(garden_path, garden_data)
    return garden_data

# 主命令
berry_garden = on_command("garden", aliases={"berrygarden", 'berry_garden'}, permission=GROUP, priority=1, block=True, rule=whitelist_rule)

@berry_garden.handle()
async def berry_garden_handle(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    # 常量定义
    SEED_COST = 10
    STEAL_COST = 20
    FERT_ENERGY = 5000
    BUFF_MESSAGES = {
        'lost': "你现在正在迷路中，连路都找不到，怎么进入果园呢？",
        'confuse': "你现在正在找到了个碎片，疑惑着呢，不能进入果园。",
        'hurt': "你现在受伤了，没有精力进入果园！",
        'tentacle': "你刚被触手玩弄到失神，没有精力进入果园！"
    }

    # 初始化数据
    user_id = str(event.user_id)
    group_id = str(event.group_id)
    timestamp = int(time.time())
    current_date = datetime.date.today()
    current_date_str = current_date.strftime("%Y-%m-%d")

    data = open_data(full_path)
    bar_data = open_data(bar_path)
    garden_data = open_data(garden_path)
    
    # 在命令处理前先全局更新
    garden_data = await update_all_gardens(garden_data)

    # 基础校验
    if user_id not in data:
        await berry_garden.finish("请先抓一次madeline再来玩“游戏”哦！", at_sender=True)

    # 初始化三个部分数据
    user_data = data.setdefault(user_id, {})
    user_bar = bar_data.setdefault(user_id, {})
    user_garden = garden_data.setdefault(user_id, {})
    
    # 用户数据初始化
    berry = data.setdefault('berry', 1000)
    user_data.setdefault('event', 'nothing')
    energy = user_data.setdefault('energy', 0)
    user_collections = user_data.setdefault('collections', {})
    user_data.setdefault('items', {})

    # 如果该用户不在酒馆名单中，则先创建数据
    user_bar.setdefault("status","nothing")
    user_bar.setdefault("game","1")
    user_bar.setdefault("bank",0)

    # 初始化果园数据
    for key in ["garden_berry", "isseed", "seed_time", "isfert", "fert_time", "steal_date"]:
        user_garden.setdefault(key, 0 if "time" not in key else timestamp) if key != "steal_date" else user_garden.setdefault(key, "2000-01-01")

    # 获取日期信息
    current_date_str = datetime.date.today().strftime("%Y-%m-%d")

    # 全局冷却检查
    all_cool_time(cd_path, user_id, group_id)
    
    # 检测是否有地契
    if user_collections.get("草莓果园地契", 0) == 0:
        await berry_garden.finish("你还没有获得草莓果园地契哦，无法进入草莓果园！", at_sender=True)

    # 事件检查
    if user_data['event'] != 'nothing':
        await berry_garden.finish("你还有正在进行中的事件", at_sender=True)
    
    # 状态检查
    if (buff := user_data.get('buff') or user_data.get('debuff')) and (msg := BUFF_MESSAGES.get(buff)):
        await berry_garden.finish(msg, at_sender=True)

    # 草莓余额检查
    if berry < 0:
        await berry_garden.finish(f"你现在仍在负债中……不允许进入果园！你只有{berry}颗草莓！", at_sender=True)
        
    # 解析命令
    command = str(args).strip()  # 去除前后空格
    valid_operations = ["收菜", "施肥", "偷菜", "播种"]

    if command not in valid_operations:
        await berry_garden.finish("请输入正确的指令哦！现在草莓果园可用指令：.garden 收菜/施肥/偷菜/播种", at_sender=True)

    operation = command  
    
    # 收菜操作
    if operation == "收菜":
        # 收货草莓
        harvest = user_garden["garden_berry"]
        
        if harvest <= 0:
            await berry_garden.finish("当前没有可收获的草莓！", at_sender=True)
            
        user_bar["bank"] += harvest
        user_garden["garden_berry"] = 0
        
        # 更新流程
        save_data(bar_path, bar_data)
        save_data(garden_path, garden_data)
        await berry_garden.finish(f"你成功从果园中自己的草莓地里收获{harvest}颗草莓，草莓已经存进银行里了哦！", at_sender=True)
        
    elif operation == "偷菜":
        if user_garden["steal_date"] == current_date_str:
            await berry_garden.finish("今天已经偷过菜了，请明天再来吧！", at_sender=True)
        
        if data[user_id]["berry"] < STEAL_COST:
            await berry_garden.finish(f"偷菜需要{STEAL_COST}颗草莓，你的草莓数量不足！", at_sender=True)
        
        # 随机选择目标（有种子且草莓数量>0的果园）
        targets = [
            uid for uid in garden_data 
            if uid != user_id 
            and garden_data[uid]["isseed"] == 1 
            and garden_data[uid]["garden_berry"] > 0  # 只选择有草莓的果园
        ]
        
        if not targets:
            await berry_garden.finish("现在没有可以偷的地，请早点过来或者晚点过来偷哦！", at_sender=True)
        
        target_id = random.choice(targets)
        target_garden = garden_data[target_id]
        steal_amount = random.randint(1, min(50, target_garden["garden_berry"]))
        
        # 更新数据
        data[user_id]["berry"] -= STEAL_COST
        user_garden["garden_berry"] += steal_amount
        target_garden["garden_berry"] -= steal_amount
        target_garden["isseed"] = 1
        user_garden["steal_date"] = current_date_str
        
        save_data(full_path, data)
        save_data(garden_path, garden_data)
        await berry_garden.finish(f"你花费了{STEAL_COST}颗草莓，成功偷取了"+ MessageSegment.at(target_id) +f" 的草莓地里的{steal_amount}颗草莓！偷取的草莓已放在你自己的果园里了哦！", at_sender=True)
        
    elif operation == "施肥":
        if user_garden["isseed"] != 1:
            await berry_garden.finish("请先播种后再进行施肥哦！", at_sender=True)
            
        if energy < FERT_ENERGY:
            await berry_garden.finish(f"施肥需要{FERT_ENERGY}点能量，你目前只有{energy}点！", at_sender=True)
        
        user_data["energy"] -= FERT_ENERGY
        user_garden["isfert"] = 1
        user_garden["fert_time"] = timestamp
        
        save_data(full_path, data)
        save_data(garden_path, garden_data)
        await berry_garden.finish("施肥成功！你的草莓地12小时内收获将会翻倍", at_sender=True)
        
    elif operation == "播种":
        if user_garden["isseed"] == 1:
            await berry_garden.finish("你已经播种过种子了哦，不能重复购买了哦！", at_sender=True)
        
        if berry < SEED_COST:
            await berry_garden.finish(f"购买种子需要{SEED_COST}颗草莓！你现在只有{berry}颗！", at_sender=True)
        
        data[user_id]["berry"] -= SEED_COST
        user_garden["isseed"] = 1
        user_garden["seed_time"] = timestamp
        
        save_data(full_path, data)
        save_data(garden_path, garden_data)
        await berry_garden.finish("播种成功！24小时内每小时草莓果园都会为你带来10草莓的收益哦！", at_sender=True)
        
    else:
        await berry_garden.finish("请输入正确的指令哦！现在草莓果园可用指令：.garden 收菜/施肥/偷菜/播种")
