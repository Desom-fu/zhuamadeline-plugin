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

# 常量定义
SEED_COST = 10
STEAL_COST = 15
FERT_ENERGY = 1200
BASIC_REWARD = 15
# BUFF_MESSAGES = {
#     'lost': "你现在正在迷路中，连路都找不到，怎么进入果园呢？",
#     'confuse': "你现在正在找到了个碎片，疑惑着呢，不能进入果园。",
#     'hurt': "你现在受伤了，没有精力进入果园！",
#     'tentacle': "你刚被触手玩弄到失神，没有精力进入果园！"
# }

# 命令别名表
garden_aliases = {
    '收菜': ['take', '收获', '收割'],
    '施肥': ['fert', '肥料', '施肥'],
    '偷菜': ['steal', '偷取', '窃取', '偷草莓'],
    '播种': ['seed', '种植', '种菜'],
    '查询': ['ck', 'query', 'check', '状态', '查看']
}

# 全局更新 
async def update_all_gardens(garden_data: dict):
    current_time = int(time.time())
    current_date_str = datetime.date.today().strftime("%Y-%m-%d")
    
    for user_id in garden_data:
        garden = garden_data[user_id]
        if garden.get("be_steal_date",'2000-01-01') != current_date_str:
            garden["be_steal_date"] = current_date_str
            garden["issteal"] = 0
    
        if garden["isseed"] == 1:
            # 初始化最后更新时间（使用播种时间）
            last_update_time = garden.get("last_update_time", garden["seed_time"])
            
            # 计算完整的小时数差（不足1小时舍弃）
            elapsed_hours = (current_time - last_update_time) // 3600
            
            if elapsed_hours > 0:
                total_new = 0
                remaining_hours = 24 - (current_time - garden["seed_time"]) // 3600
                effective_hours = min(elapsed_hours, remaining_hours)
                
                # 计算施肥有效小时数
                fert_hours = 0
                if garden.get("isfert") == 1:
                    fert_end_time = garden["fert_time"] + 12 * 3600
                    # 计算施肥有效期内的小时数
                    for hour in range(effective_hours):
                        hour_time = last_update_time + (hour + 1) * 3600
                        if garden["fert_time"] <= hour_time <= fert_end_time:
                            fert_hours += 1
                
                # 总产量 = 基础产量 + 施肥加成
                total_new = effective_hours * BASIC_REWARD + fert_hours * BASIC_REWARD
                
                # 更新数据（严格整数运算）
                garden["garden_berry"] = garden.get("garden_berry", 0) + total_new
                garden["last_update_time"] = last_update_time + effective_hours * 3600
            
            # 24小时生长周期检测
            if (current_time - garden["seed_time"]) // 3600 >= 24:
                garden["isseed"] = 0
            # 施肥失效检测
            if (current_time - garden["fert_time"]) // 3600 >= 12:
                garden["isfert"] = 0
    
    save_data(garden_path, garden_data)
    return garden_data

# 主命令
berry_garden = on_command("garden", aliases={"berrygarden", 'berry_garden'}, permission=GROUP, priority=1, block=True, rule=whitelist_rule)

@berry_garden.handle()
async def berry_garden_handle(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
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
        await berry_garden.finish("请先抓一次madeline再来草莓果园吧！", at_sender=True)

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
    for key in ["garden_berry", "isseed", "seed_time", "isfert", "issteal", "fert_time", "steal_date", "last_update_time", 'be_steal_date']:
        user_garden.setdefault(key, 0 if "time" not in key else timestamp) if key not in ["steal_date", 'be_steal_date'] else user_garden.setdefault(key, "2000-01-01")

    # 获取日期信息
    current_date_str = datetime.date.today().strftime("%Y-%m-%d")

    # 全局冷却检查
    all_cool_time(cd_path, user_id, group_id)
    
    # 检测是否有地契
    if user_collections.get("草莓果园地契", 0) == 0:
        await berry_garden.finish("你还没有获得草莓果园地契哦，无法进入草莓果园！", at_sender=True)

    # 事件检查
    # if user_data['event'] != 'nothing':
    #     await berry_garden.finish("你还有正在进行中的事件", at_sender=True)
    
    # # 状态检查
    # if (buff := user_data.get('buff') or user_data.get('debuff')) and (msg := BUFF_MESSAGES.get(buff)):
    #     await berry_garden.finish(msg, at_sender=True)

    # 草莓余额检查
    if berry < 0:
        await berry_garden.finish(f"你现在仍在负债中……不允许进入果园！你只有{berry}颗草莓！", at_sender=True)
        
    # 解析命令
    command = str(args).strip().lower()
    
    # 查找匹配的命令
    operation = None
    for main_cmd, aliases in garden_aliases.items():
        if command == main_cmd or command in aliases:
            operation = main_cmd
            break
    
    if not operation:
        # 构建帮助信息
        help_msg = "请输入正确的指令哦！可用指令："
        for main_cmd, aliases in garden_aliases.items():
            help_msg += f"\n.garden {main_cmd}({'/'.join(aliases)})"
        await berry_garden.finish(help_msg, at_sender=True)

    # 查询操作
    if operation == "查询":
        # 计算播种剩余时间
        if user_garden["isseed"] == 1:
            seed_age = timestamp - user_garden["seed_time"]
            remaining_time = max(0, 24 * 3600 - seed_age)
            hours, remainder = divmod(remaining_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            seed_status = f"已播种，剩余时间: {hours}小时{minutes}分钟"
        else:
            seed_status = "未播种"
        
        # 计算施肥剩余时间
        if user_garden["isfert"] == 1:
            fert_age = timestamp - user_garden["fert_time"]
            remaining_time = max(0, 12 * 3600 - fert_age)
            hours, remainder = divmod(remaining_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            fert_status = f"已施肥，剩余时间: {hours}小时{minutes}分钟"
        else:
            fert_status = "未施肥"
        
        # 偷菜状态
        if user_garden["steal_date"] == current_date_str:
            steal_status = "今日已偷草莓"
        else:
            steal_status = "今日未偷草莓"
        
        if user_garden["issteal"] == 1:
            besteal_status = "今日已被偷草莓"
        else:
            besteal_status = "今日没被偷草莓，要小心了"
        
        # 构建回复消息
        reply_msg = (
            f"\n【土地状态查询】\n"
            f"当前草莓数量: {user_garden['garden_berry']}\n"
            f"播种状态: {seed_status}\n"
            f"施肥状态: {fert_status}\n"
            f"偷菜状态: {steal_status}\n"
            f"被偷状态: {besteal_status}"
        )
        
        await berry_garden.finish(reply_msg, at_sender=True)
    # 收菜操作
    elif operation == "收菜":
        harvest = user_garden["garden_berry"]

        if harvest <= 0:
            message = "当前没有可收获的草莓！"
        else:
            # # 计算基础产量和施肥加成
            # seed_time = user_garden["seed_time"]
            # fert_time = user_garden.get("fert_time", 0)
            # isfert = user_garden.get("isfert", 0)

            # current_time = int(time.time())
            # total_hours = min(24, (current_time - seed_time) // 3600)  # 总生长小时数（不超过24h）

            # # 基础产量 = 总小时数 × 15
            # base_harvest = total_hours * BASIC_REWARD

            # # 施肥加成 = 施肥有效时间 × 15
            # if isfert == 1:
            #     fert_hours = min(12, (current_time - fert_time) // 3600)  # 施肥有效时间（不超过12h）
            #     bonus_harvest = min(fert_hours, total_hours) * BASIC_REWARD  # 不能超过总生长时间
            # else:
            #     bonus_harvest = 0

            # # 理论上 harvest = base_harvest + bonus_harvest，但可能有误差（比如手动修改数据）
            # # 所以取最小值，防止显示错误
            # base_harvest = min(base_harvest, harvest)
            # bonus_harvest = min(bonus_harvest, harvest - base_harvest)

            # 更新银行数据
            user_bar["bank"] += harvest
            user_garden["garden_berry"] = 0

            # 保存数据
            save_data(bar_path, bar_data)
            save_data(garden_path, garden_data)

            # 构建回复消息
            message = (
                f"\n🍓 收获报告 🍓\n"
                # f"基础产量: {base_harvest}颗 ({total_hours}小时×{BASIC_REWARD}/h)\n"
            )

            # if bonus_harvest > 0:
            #     message += f"施肥加成: +{bonus_harvest}颗 (施肥有效时间: {fert_hours}小时)\n"

            message += f"本次收获: {harvest}颗草莓\n"
            message += "草莓已经存进银行里了哦！"
            
        if user_garden["isseed"] == 0:
            message += "\n你的草莓已经全部收获完毕啦，需要再次播种哦！"
            
        if user_garden["isfert"] == 0:
            message += "\n施肥时间已到，如需要可以重新施肥哦！"
        
        await berry_garden.finish(message, at_sender=True)
        
    elif operation == "偷菜":
        if user_garden["steal_date"] == current_date_str:
            await berry_garden.finish("今天你已经偷过草莓了，请明天再来吧！", at_sender=True)
        
        if data[user_id]["berry"] < STEAL_COST:
            await berry_garden.finish(f"偷草莓需要{STEAL_COST}颗草莓，你的草莓数量不足！", at_sender=True)
        
        # 随机选择目标（未被偷过且草莓数量>0的果园）
        targets = [
            uid for uid in garden_data 
            if uid != user_id 
            and garden_data[uid]["issteal"] == 0 # 只偷没偷过的
            and garden_data[uid]["garden_berry"] > 0  # 只选择有草莓的果园
        ]
        
        if not targets:
            await berry_garden.finish("现在没有可以偷的土地，请早点过来或者晚点过来偷哦！", at_sender=True)
        
        # 随机选择
        target_id = random.choice(targets)
        target_garden = garden_data[target_id]
        steal_amount = random.randint(1, min(50, target_garden["garden_berry"]))
        
        # 更新数据
        data[user_id]["berry"] -= STEAL_COST
        user_garden["garden_berry"] += steal_amount
        target_garden["garden_berry"] -= steal_amount
        target_garden["issteal"] = 1
        user_garden["steal_date"] = current_date_str
        target_garden["be_steal_date"] = current_date_str
        
        save_data(full_path, data)
        save_data(garden_path, garden_data)
        await berry_garden.finish(f"你花费了{STEAL_COST}颗草莓，成功偷取了"+ MessageSegment.at(target_id) +f" 的草莓地里的{steal_amount}颗草莓！偷取的草莓已放在你自己地里了哦！", at_sender=True)
        
    elif operation == "施肥":
        if user_garden["isseed"] != 1:
            await berry_garden.finish("请先播种后再进行施肥哦！", at_sender=True)
            
        if user_garden["isfert"] == 1:
            await berry_garden.finish("你已经施肥过了，没必要重新施肥哦！", at_sender=True)
            
        if energy < FERT_ENERGY:
            await berry_garden.finish(f"施肥需要{FERT_ENERGY}点能量，你目前只有{energy}点！", at_sender=True)
        
        user_data["energy"] -= FERT_ENERGY
        user_garden["isfert"] = 1
        user_garden["fert_time"] = timestamp
        
        save_data(full_path, data)
        save_data(garden_path, garden_data)
        await berry_garden.finish(f"你使用了{FERT_ENERGY}点能量对土地施肥成功！接下来的12h内你的草莓地收获将会翻倍！", at_sender=True)
        
    elif operation == "播种":
        if user_garden["isseed"] == 1:
            await berry_garden.finish("你已经播种过种子了哦，不能重复购买了哦！", at_sender=True)
        
        if berry < SEED_COST:
            await berry_garden.finish(f"购买种子需要{SEED_COST}颗草莓！你现在只有{berry}颗！", at_sender=True)
        
        data[user_id]["berry"] -= SEED_COST
        user_garden["isseed"] = 1
        user_garden["seed_time"] = timestamp
        user_garden["last_update_time"] = timestamp
        
        save_data(full_path, data)
        save_data(garden_path, garden_data)
        await berry_garden.finish(f"播种成功！24小时内每小时草莓地都会为你带来{BASIC_REWARD}颗草莓的收益哦！", at_sender=True)
        
    else:
        # 构建帮助信息
        help_msg = "请输入正确的指令哦！可用指令：\n"
        for main_cmd, aliases in garden_aliases.items():
            help_msg += f".garden {main_cmd}({'/'.join(aliases)})\n"
        await berry_garden.finish(help_msg, at_sender=True)
