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
from .berry_garden_level import GARDEN_LEVELS, get_level_config  # 导入等级配置

# 命令别名表
garden_aliases = {
    '收菜': ['take', '收获', '收割', '收草莓'],
    '施肥': ['fert', '肥料', '施肥'],
    '偷菜': ['steal', '偷取', '窃取', '偷草莓'],
    '播种': ['seed', '种植', '种菜'],
    '查询': ['ck', 'query', 'check', '状态', '查看'],
    '升级': ['upgrade', 'levelup', 'update' ,'提升等级']
}

# def migrate_user_data():
#     """迁移用户数据，移除等级相关字段"""
#     garden_data = open_data(garden_path)
#     changed = False
    
#     for user_id, data in garden_data.items():
#         # 保留必要字段
#         keep_fields = {
#             "garden_berry", "isseed", "seed_time", "isfert", 
#             "fert_time", "steal_date", "last_update_time",
#             "be_steal_date", "today_steal", "today_be_stolen",
#             "garden_level"  # 只保留等级数字
#         }
        
#         # 创建新数据字典
#         new_data = {k: v for k, v in data.items() if k in keep_fields}
        
#         # 检查是否有变化
#         if new_data != data:
#             garden_data[user_id] = new_data
#             changed = True
    
#     if changed:
#         save_data(garden_path, garden_data)
#         print("用户数据迁移完成！")
#     return changed

# 全局更新 
async def update_all_gardens(garden_data: dict):
    current_time = int(time.time())
    current_date_str = datetime.date.today().strftime("%Y-%m-%d")
    
    for user_id in garden_data:
        garden = garden_data[user_id]
        
        # 获取用户等级配置
        current_level = garden.get("garden_level", 1)
        level_config = get_level_config(current_level)
        
        # 重置每日偷菜状态
        if garden.get("be_steal_date",'2000-01-01') != current_date_str:
            garden["be_steal_date"] = current_date_str
            garden["today_steal"] = 0
            garden["today_be_stolen"] = 0
            
        # 处理播种状态
        if garden["isseed"] == 1:
            # 初始化最后更新时间（使用播种时间）
            last_update_time = garden.get("last_update_time", garden["seed_time"])
            
            # 计算完整的小时数差（不足1小时舍弃）
            elapsed_hours = (current_time - last_update_time) // 3600
            
            # 计算剩余生长时间（秒）
            remaining_seconds = 24 * 3600 - (current_time - garden["seed_time"])
            
            if elapsed_hours > 0 or remaining_seconds <= 0:
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
                
                # 总产量 = 基础产量 + 施肥加成（从等级配置读取basic_reward）
                base_reward = level_config["basic_reward"]
                total_new = effective_hours * base_reward + fert_hours * base_reward
                
                # 更新数据（严格整数运算）
                garden["garden_berry"] = garden.get("garden_berry", 0) + total_new
                garden["last_update_time"] = last_update_time + effective_hours * 3600
            
            # 检查24小时生长周期是否结束（包括不足1小时的情况）
            if (current_time - garden["seed_time"]) >= 24 * 3600:
                # 处理最后一小时的收成（如果还有剩余时间）
                if (current_time - garden["seed_time"]) > 24 * 3600:
                    # 计算最后一小时的收成
                    final_hour_time = garden["seed_time"] + 24 * 3600
                    if garden.get("last_update_time", garden["seed_time"]) < final_hour_time:
                        # 检查施肥是否有效
                        is_fert = 0
                        if garden.get("isfert") == 1 and garden["fert_time"] <= final_hour_time <= (garden["fert_time"] + 12 * 3600):
                            is_fert = 1
                        
                        # 计算最后一小时的收成（从等级配置读取basic_reward）
                        final_reward = base_reward + (is_fert * base_reward)
                        garden["garden_berry"] = garden.get("garden_berry", 0) + final_reward
                        garden["last_update_time"] = final_hour_time
                
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
    # migrate_user_data()

    # if user_id not in bot_owner_id:
    #     await berry_garden.finish("花园正在绝赞升级中，暂时不开放哦！不过正在播种的仍会计算产量！")

    # 基础校验
    if user_id not in data:
        await berry_garden.finish("请先抓一次madeline再来草莓果园吧！", at_sender=True)

    # 初始化三个部分数据
    user_data = data.setdefault(user_id, {})
    user_bar = bar_data.setdefault(user_id, {})
    user_garden = garden_data.setdefault(user_id, {})
    
    # 用户数据初始化
    berry = user_data.setdefault('berry', 1000)
    user_data.setdefault('event', 'nothing')
    energy = user_data.setdefault('energy', 0)
    user_collections = user_data.setdefault('collections', {})
    user_data.setdefault('items', {})

    # 如果该用户不在酒馆名单中，则先创建数据
    user_bar.setdefault("status","nothing")
    user_bar.setdefault("game","1")
    user_bar.setdefault("bank",0)

    # 初始化果园数据（只保留必要字段）
    user_garden.setdefault("garden_level", 1)
    current_level = user_garden["garden_level"]
    level_config = get_level_config(current_level)

    # 初始化其他原有字段
    for key in ["garden_berry", "isseed", "seed_time", "isfert",
                "fert_time", "steal_date", "last_update_time", 'be_steal_date', 
                'today_steal', 'today_be_stolen']:
        user_garden.setdefault(key, 0 if "time" not in key else timestamp) if key not in ["steal_date", 'be_steal_date'] else user_garden.setdefault(key, "2000-01-01")

    # 获取日期信息
    current_date_str = datetime.date.today().strftime("%Y-%m-%d")

    # 全局冷却检查
    all_cool_time(cd_path, user_id, group_id)
    
    # 检测是否有地契
    if user_collections.get("草莓果园地契", 0) == 0:
        await berry_garden.finish("你还没有获得草莓果园地契哦，无法进入草莓果园！", at_sender=True)

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
            seed_status = f"已播种，剩余时间: {hours}h{minutes}min{seconds}s"
        else:
            seed_status = "未播种"
        
        # 计算施肥剩余时间
        if user_garden["isfert"] == 1:
            fert_age = timestamp - user_garden["fert_time"]
            remaining_time = max(0, 12 * 3600 - fert_age)
            hours, remainder = divmod(remaining_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            fert_status = f"已施肥，剩余时间: {hours}h{minutes}min{seconds}s"
        else:
            fert_status = "未施肥"
        
        # 偷菜状态
        if user_garden["steal_date"] == current_date_str:
            steal_status = f"今日已偷草莓({user_garden['today_steal']}/{level_config['max_steal_times']})"
        else:
            steal_status = f"今日未偷草莓(0/{level_config['max_steal_times']})"
        
        if user_garden.get("today_be_stolen", 0) == 0:
            besteal_status = f"今日没被偷草莓(0/{level_config['max_be_stolen']})"
        else:
            besteal_status = f"今日已被偷草莓({user_garden['today_be_stolen']}/{level_config['max_be_stolen']})次"
        
        # 获取升级信息
        current_level = user_garden["garden_level"]
        if (next_level := current_level + 1) in GARDEN_LEVELS:
            next_config = get_level_config(next_level)
            cost_type = "草莓" if next_config["if_use_berry"] else "能量"
            cost = next_config[f"upgrade_{'berry' if next_config['if_use_berry'] else 'energy'}"]
            upgrade_info = f"升级到 Lv{next_level} 需要 {cost} {cost_type}"
        else:
            upgrade_info = "已达成最高等级"
        
        # 构建回复消息
        reply_msg = (
            f"\n【土地状态查询】"
            f"\n当前等级: Lv{current_level} | {upgrade_info}"
            f"\n当前草莓数量: {user_garden['garden_berry']}"
            f"\n播种状态: {seed_status}"
            f"\n施肥状态: {fert_status}"
            f"\n偷菜状态: {steal_status}"
            f"\n被偷状态: {besteal_status}"
            f"\n当前等级属性:"
            f"\n种子价格: {level_config['seed_cost']} 偷取成本: {level_config['steal_cost']}"
            f"\n施肥能耗: {level_config['fert_energy']} 基础产量: {level_config['basic_reward']}"
            f"\n偷取范围: {level_config['steal_min']}-{level_config['steal_max']}"
        )
        
        await berry_garden.finish(reply_msg, at_sender=True)
    
    # 收菜操作
    elif operation == "收菜":
        harvest = user_garden["garden_berry"]

        if harvest <= 0:
            message = "当前没有可收获的草莓！"
        else:
            # 更新银行数据
            user_bar["bank"] += harvest
            user_garden["garden_berry"] = 0

            # 保存数据
            save_data(bar_path, bar_data)
            save_data(garden_path, garden_data)

            # 构建回复消息
            message = (
                f"\n🍓 收获报告 🍓\n"
            )

            message += f"本次收获: {harvest}颗草莓\n"
            message += "草莓已经存进银行里了哦！"
            
        if user_garden["isseed"] == 0:
            message += "\n- 你的草莓已经全部收获完毕啦，需要再次播种哦！"
            
        if user_garden["isfert"] == 0:
            message += "\n- 施肥时间已到，如需要可以重新施肥哦！"
        
        await berry_garden.finish(message, at_sender=True)
        
    elif operation == "偷菜":
        # 检查每日偷菜次数限制
        if user_garden["today_steal"] >= level_config["max_steal_times"]:
            await berry_garden.finish(f"今日偷菜次数已达上限({level_config['max_steal_times']}次)！", at_sender=True)
        
        steal_cost = level_config["steal_cost"]
        if berry < steal_cost:
            await berry_garden.finish(f"偷草莓需要{steal_cost}颗草莓，你的草莓数量不足！", at_sender=True)
        
        # 随机选择目标（未被偷过且草莓数量>0的果园）
        targets = []
        for uid, target in garden_data.items():
            if uid == user_id:
                continue
            
            target_level = target.get("garden_level", 1)
            target_config = get_level_config(target_level)
            
            if (target.get("today_be_stolen", 0) < target_config["max_be_stolen"] and 
                target.get("garden_berry", 0) > 0):
                targets.append(uid)
        
        if not targets:
            await berry_garden.finish("现在没有可以偷的土地，请早点过来或者晚点过来偷哦！", at_sender=True)
        
        # 随机选择
        target_id = random.choice(targets)
        target_garden = garden_data[target_id]
        target_level = target_garden.get("garden_level", 1)
        target_config = get_level_config(target_level)
        
        steal_amount = random.randint(
            level_config["steal_min"], 
            min(level_config["steal_max"], target_garden["garden_berry"])
        )
        
        # 更新数据
        data[user_id]["berry"] -= steal_cost
        user_garden["garden_berry"] += steal_amount
        target_garden["garden_berry"] -= steal_amount
        user_garden["steal_date"] = current_date_str
        target_garden["be_steal_date"] = current_date_str
        user_garden["today_steal"] += 1
        target_garden["today_be_stolen"] = target_garden.get("today_be_stolen", 0) + 1
        
        save_data(full_path, data)
        save_data(garden_path, garden_data)
        await berry_garden.finish(
            f"你花费了{steal_cost}颗草莓，成功偷取了"+ MessageSegment.at(target_id) +
            f" 的草莓地里的{steal_amount}颗草莓！\n" +
            f"今日已偷: {user_garden['today_steal']}/{level_config['max_steal_times']}次",
            at_sender=True
        )
        
    elif operation == "施肥":
        if user_garden["isseed"] != 1:
            await berry_garden.finish("请先播种后再进行施肥哦！", at_sender=True)
            
        if user_garden["isfert"] == 1:
            await berry_garden.finish("你已经施肥过了，没必要重新施肥哦！", at_sender=True)
            
        fert_energy = level_config["fert_energy"]
        if energy < fert_energy:
            await berry_garden.finish(f"施肥需要{fert_energy}点能量，你目前只有{energy}点！", at_sender=True)
        
        user_data["energy"] -= fert_energy
        user_garden["isfert"] = 1
        user_garden["fert_time"] = timestamp
        
        save_data(full_path, data)
        save_data(garden_path, garden_data)
        await berry_garden.finish(
            f"你使用了{fert_energy}点能量对土地施肥成功！\n"
            f"接下来的12h内你的草莓地收获将会翻倍！",
            at_sender=True
        )
        
    elif operation == "播种":
        if user_garden["isseed"] == 1:
            await berry_garden.finish("你已经播种过种子了哦，不能重复购买了哦！", at_sender=True)
        
        seed_cost = level_config["seed_cost"]
        if berry < seed_cost:
            await berry_garden.finish(f"购买种子需要{seed_cost}颗草莓！你现在只有{berry}颗！", at_sender=True)
        
        data[user_id]["berry"] -= seed_cost
        user_garden["isseed"] = 1
        user_garden["seed_time"] = timestamp
        user_garden["last_update_time"] = timestamp
        
        save_data(full_path, data)
        save_data(garden_path, garden_data)
        await berry_garden.finish(
            f"播种成功！24小时内每小时草莓地都会为你带来{level_config['basic_reward']}颗草莓的收益哦！\n"
            f"施肥可使产量翻倍！",
            at_sender=True
        )
    
    # 升级操作
    elif operation == "升级":
        # 检查状态
        if user_garden["isseed"] == 1:
            await berry_garden.finish("播种期间无法升级！请先收割当前作物。", at_sender=True)
        if user_garden["isfert"] == 1:
            await berry_garden.finish("施肥期间无法升级！请等待施肥效果结束。", at_sender=True)
        
        current_level = user_garden["garden_level"]
        next_level = current_level + 1
        
        # 检查是否存在下一等级
        if next_level not in GARDEN_LEVELS:
            await berry_garden.finish(f"当前已是最高等级（Lv{current_level}）！", at_sender=True)
        
        # 获取下一等级配置
        next_config = get_level_config(next_level)
        
        # 确定升级所需资源
        if next_config["if_use_berry"] == 1:
            cost_type = "berry"
            cost_amount = next_config["upgrade_berry"]
            current_amount = berry
        else:
            cost_type = "energy"
            cost_amount = next_config["upgrade_energy"]
            current_amount = energy
        
        # 资源检查
        if current_amount < cost_amount:
            await berry_garden.finish(
                f"升级到 Lv{next_level} 需要[{cost_amount}]{'颗草莓' if cost_type == 'berry' else '点能量'}！\n"
                f"当前余额：{current_amount}", 
                at_sender=True
            )
        
        # 执行升级
        if cost_type == "berry":
            data[user_id]["berry"] -= cost_amount
        else:
            data[user_id]["energy"] -= cost_amount
        
        # 更新等级
        user_garden["garden_level"] = next_level
        
        save_data(full_path, data)
        save_data(garden_path, garden_data)
        await berry_garden.finish(
            f"成功升级到 Lv{next_level}！\n"
            f"消耗：{cost_amount} {'颗草莓' if cost_type == 'berry' else '点能量'}\n"
            f"新属性：\n"
            f"种子价格：{next_config['seed_cost']} 偷取成本：{next_config['steal_cost']}\n"
            f"施肥能耗：{next_config['fert_energy']} 基础产量：{next_config['basic_reward']}\n"
            f"偷取范围：{next_config['steal_min']}-{next_config['steal_max']}\n"
            f"每日偷取次数：{next_config['max_steal_times']} 每日被偷上限：{next_config['max_be_stolen']}",
            at_sender=True
        )
        
    else:
        # 构建帮助信息
        help_msg = "请输入正确的指令哦！可用指令：\n"
        for main_cmd, aliases in garden_aliases.items():
            help_msg += f".garden {main_cmd}({'/'.join(aliases)})\n"
        await berry_garden.finish(help_msg, at_sender=True)