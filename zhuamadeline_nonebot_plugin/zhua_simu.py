from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent
from nonebot.adapters.onebot.v11 import GROUP, Event
from nonebot.params import CommandArg
import random
import math
import datetime
from pathlib import Path
from .config import bot_owner_id
from .whitelist import whitelist_rule

test_max_grade = 100

# 经验增长规则字典
exp_growth = {
    range(1, 6): 5,   # 等级 1-5，max_exp +5
    range(6, 11): 10,  # 等级 6-10，max_exp +10
    range(11, 16): 15, # 等级 11-15，max_exp +15
    range(16, 21): 20, # 等级 16-20，max_exp +20
    range(21, 101): 25  # 等级 21-30，max_exp +25
}

# 5猎经验值计算
def calculate_level_and_exp(data, user_id, level, isitem):
    """
    计算等级和经验值的增长（显示溢出经验的版本）
    参数:
        data: 用户数据字典
        user_id: 用户ID
        level: 本次获得的等级点数
        isitem: 是不是道具
    返回:
        tuple: (经验消息，等级消息，data主数据)
    """
    user_data = data[user_id]
    original_exp = user_data.get("exp", 0)
    original_grade = user_data.get("grade", 1)
    original_max_exp = user_data.get("max_exp", 10)
    
    exp = original_exp
    grade = original_grade
    max_exp = original_max_exp
    collections = user_data.get("collections", {})
    
    exp_msg = ''
    grade_msg = ''
    
    # 如果满级直接返回
    if grade == test_max_grade:
        return exp_msg, grade_msg, data
        
    # 1. 计算获得的经验值
    if isitem == 1:
        gained_exp = math.floor(level / 2)  # 道具获得一半经验
    else:
        gained_exp = level
    
    # 第一阶段消息：显示获得的经验和当前状态（包含溢出经验）
    if gained_exp > 0:
        temp_exp = exp + gained_exp  # 临时计算包含本次获得的经验
        exp_msg = f'\n\n本次获得{gained_exp}点经验，当前经验：{temp_exp}/{max_exp}'
    
    # 2. 实际增加经验
    exp += gained_exp
    
    # 处理可能的多级升级情况
    upgraded = False
    while exp >= max_exp and grade < test_max_grade:
        upgraded = True
        # 计算升级
        exp -= max_exp
        grade += 1

        # 查找对应的经验增长值
        for level_range, increment in exp_growth.items():
            if grade in level_range:
                max_exp += increment
                break
        
        # 特殊等级消息
        special_grades = {
            6: f"\n恭喜升到{grade}级，现在你可以在深渊里面抓到2级的Madeline了！",
            11: f"\n恭喜升到{grade}级，现在你可以在深渊里面抓到3级的Madeline了！",
            16: f"\n恭喜升到{grade}级，现在你可以在深渊里面抓到4级的Madeline了！",
            21: f"\n恭喜升到{grade}级，现在你可以在深渊里面抓到5级的Madeline了，同时道具和祈愿的封印也解除了！",
        }

        if grade in special_grades:
            grade_msg += special_grades[grade]
    
    # 3. 如果有升级，添加升级后的状态
    if upgraded:
        grade_msg = f'\n恭喜升级！当前等级：{grade}/{test_max_grade}' + grade_msg
        # 没有满级才显示升级后经验
        if grade < test_max_grade:
            grade_msg += f'\n升级后经验：{exp}/{max_exp}'

    # 添加藏品
    if grade == test_max_grade and collections.get("时隙沙漏", 0) == 0:
        collections['时隙沙漏'] = 1
        grade_msg += f"\n你已经达到最大等级{test_max_grade}！\n倏然，你手中入场券的那一点金色光芒突然闪烁起来！\n你慢慢的看着它融化，重组，最后在你手中变成了散发着淡金色光芒的蓝色沙漏。\n输入.cp 时隙沙漏 以查看具体效果"
    
    # 更新数据
    user_data.update({
        "exp": exp, 
        "grade": grade, 
        "max_exp": max_exp,
        "collections": collections
    })
    
    # save_data(full_path, data)
    
    return exp_msg, grade_msg, data

async def simulate_event(user_data, current_time):
    """模拟事件系统的影响"""
    # 初始化事件结果
    bonus_exp_multiplier = 1.0
    bonus_catches = 1
    delay_hours = 0.0
    
    # 10%概率无效事件（什么都不发生，类比抓到鱼类之类的，救人没加，因为我想大概率没人能救）
    if random.random() < 0.10:
        return 0.0, 1, 0  # 无加成，有抓取，无延迟
    
    # 17.5%概率掉坑（冷却2小时）
    if random.random() < 0.175:
        delay_hours = 1.5
        user_data["buff"] = "hurt"
        user_data["next_time"] = (current_time + datetime.timedelta(hours=delay_hours)).strftime("%Y-%m-%d %H:%M:%S")
        return bonus_exp_multiplier, bonus_catches, delay_hours
    
    # 判断是否触发Boss事件（5%概率，世界boss解锁后4.5%+0.5%）
    boss_chance = 0.05
    world_boss_unlocked = user_data["grade"] >= 11  # 11级解锁世界boss
    if world_boss_unlocked:
        boss_chance = 0.045  # 普通boss概率降为4.5%
    
    if random.random() < boss_chance:
        # 确定boss类型
        if world_boss_unlocked and random.random() < 0.1:  # 10%概率是世界boss
            boss_type = "world"
            bonus_catches = random.randint(20, 80)
            bonus_exp_multiplier = 2.0
        else:
            if user_data["grade"] < 6:
                boss_type = "mini"
                bonus_catches = random.randint(10, 20)
                bonus_exp_multiplier = 1.3
            elif user_data["grade"] < 11:
                boss_type = random.choice(["mini", "normal"])
                bonus_catches = random.randint(30, 50) if boss_type == "normal" else random.randint(10, 20)
                bonus_exp_multiplier = 1.4 if boss_type == "normal" else 1.3
            else:
                boss_type = random.choice(["mini", "normal", "hard"])
                if boss_type == "mini":
                    bonus_catches = random.randint(10, 20)
                    bonus_exp_multiplier = 1.3
                elif boss_type == "normal":
                    bonus_catches = random.randint(30, 50)
                    bonus_exp_multiplier = 1.4
                else:
                    bonus_catches = random.randint(60, 80)
                    bonus_exp_multiplier = 1.5
    
    return bonus_exp_multiplier, bonus_catches, delay_hours

async def run_single_simulation(max_grade):
    """运行单次模拟"""
    user_data = {
        "berry": 0,
        "collections": {
            "星辰碎屑": 1,
            "音矿": 5000,
            "回想之核": 1  # 新增：默认持有回想之核
        },
        "item": {},
        "lc": "5",
        "exp": 0,
        "grade": 1,
        "max_exp": 10,
        "next_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "buff2": "normal",
        "buff": "normal",
        "debuff": "normal",
        "event": "nothing"
    }
    
    total_catches = 0
    total_time = datetime.timedelta()
    # 根据是否持有回想之核决定冷却时间
    base_catch_interval = 29 if user_data["collections"].get("回想之核", 0) >= 1 else 30
    catch_interval = datetime.timedelta(minutes=base_catch_interval)
    total_delay_hours = 0.0
    boss_events = 0
    pit_events = 0
    null_events = 0
    
    while user_data["grade"] < max_grade:
        current_time = datetime.datetime.now() + total_time
        
        # 模拟事件
        exp_multiplier, bonus_catches, delay_hours = await simulate_event(user_data, current_time)
        
        # 统计事件类型
        is_pit_event = delay_hours >= 0.5
        is_boss_event = bonus_catches > 1
        is_null_event = exp_multiplier == 0.0 and bonus_catches == 1 and delay_hours == 0
        
        if is_pit_event:
            pit_events += 1
        elif is_boss_event:
            boss_events += 1
        elif is_null_event:
            null_events += 1
        
        total_delay_hours += delay_hours

        # 如果是掉坑事件，只增加时间不计算经验
        if is_pit_event:
            total_time += catch_interval  # 消耗一次抓取机会
            total_time += datetime.timedelta(hours=delay_hours)  # 增加延迟时间
            total_catches += 1
            continue

        # 如果是无效事件，直接跳过
        if is_null_event:
            total_time += catch_interval  # 消耗一次抓取机会
            total_catches += 1
            continue
        
        # 确定概率分布
        star_add = 100 if user_data["collections"].get("星辰碎屑", 0) >= 1 else 0
        increment = math.floor(0.01 * user_data["collections"].get("音矿", 0)) if user_data["grade"] >= 21 else 0
        
        probabilities = {'a': 0, 'b': 0, 'c': 0, 'd': 0}
        if user_data["grade"] >= 6:
            probabilities.update({'d': 300 + star_add})
        if user_data["grade"] >= 11:
            probabilities.update({'c': 150, 'd': 450 + star_add})
        if user_data["grade"] >= 16:
            probabilities.update({'b': 40, 'c': 190, 'd': 490 + star_add})
        if user_data["grade"] >= 21:
            probabilities = {
                'a': 10 + increment,
                'b': 50 + increment,
                'c': 200 + increment,
                'd': 500 + increment + star_add
            }
        
        # 计算本次抓取
        catches_in_this_round = max(bonus_catches, 1)
        total_exp_in_round = 0
        
        for _ in range(catches_in_this_round):
            rnd = random.randint(1, 1000)
            level = 1
            if rnd <= probabilities['a']: level = 5
            elif rnd <= probabilities['b']: level = 4
            elif rnd <= probabilities['c']: level = 3
            elif rnd <= probabilities['d']: level = 2
            
            exp_gain = math.floor(level * exp_multiplier)
            total_exp_in_round += exp_gain
        
        # 更新经验
        _, _, user_data = calculate_level_and_exp(
            {"dummy_user": user_data}, 
            "dummy_user", 
            total_exp_in_round, 
            0
        )
        user_data = user_data["dummy_user"]
        
        # 更新时间
        total_time += catch_interval * catches_in_this_round
        if delay_hours > 0:
            total_time += datetime.timedelta(hours=delay_hours)
        
        total_catches += catches_in_this_round
    
    return {
        "total_catches": total_catches,
        "total_time": total_time,
        "boss_events": boss_events,
        "pit_events": pit_events,
        "total_delay": total_delay_hours,
        "null_events": null_events  # 新增：返回无效事件次数
    }

# 主函数
simu_5 = on_command("simu_5", permission=GROUP, priority=6, block=True, rule=whitelist_rule)
@simu_5.handle()
async def handle_simulation(event: GroupMessageEvent, arg: Message = CommandArg()):
    if str(event.user_id) not in bot_owner_id:
        return
    
    args = arg.extract_plain_text().strip().split()
    if len(args) < 2:
        await simu_5.finish("命令格式错误！正确格式：\n.simu_5 最高等级 模拟次数")
        return
    
    try:
        max_grade = int(args[0])
        simulations = int(args[1])
    except ValueError:
        await simu_5.finish("参数必须是数字！格式：\n.simu_5 最高等级 模拟次数")
        return
    
    if max_grade < 1 or max_grade > test_max_grade:
        await simu_5.finish(f"最高等级必须在1-{test_max_grade}之间")
        return
    if simulations < 1 or simulations > 100:
        await simu_5.finish("模拟次数必须在1-100之间")
        return
    
    # 运行多次模拟
    results = []
    individual_results = []
    for i in range(simulations):
        result = await run_single_simulation(max_grade)
        results.append(result)
        individual_results.append(f"第{i+1}次: {result['total_catches']}次")
    
    # 平均获得经验
    total_exp_required = 0
    current_max_exp = 10

    # 计算从1级升到max_grade需要的总经验
    for grade in range(1, max_grade):
        if grade < 6:
            total_exp_required += current_max_exp
            current_max_exp += 5
        elif grade < 11:
            total_exp_required += current_max_exp
            current_max_exp += 10
        elif grade < 16:
            total_exp_required += current_max_exp
            current_max_exp += 15
        elif grade < 21:
            total_exp_required += current_max_exp
            current_max_exp += 20
        else:
            total_exp_required += current_max_exp
            current_max_exp += 25
    
    # 计算统计数据
    avg_catches = sum(r["total_catches"] for r in results) / simulations
    avg_time = sum(r["total_time"].total_seconds() for r in results) / simulations
    avg_boss = sum(r["boss_events"] for r in results) / simulations
    avg_pit = sum(r["pit_events"] for r in results) / simulations
    avg_delay = sum(r["total_delay"] for r in results) / simulations
    avg_null_events = sum(r.get("null_events", 0) for r in results) / simulations
    # 平均经验
    avg_exp_per_catch = total_exp_required / avg_catches
    
    # 格式化时间
    avg_time = datetime.timedelta(seconds=avg_time)
    days = avg_time.days
    hours = avg_time.seconds // 3600
    minutes = (avg_time.seconds % 3600) // 60
    
    # 构建最终消息
    message = (
        f"模拟完成！{simulations}次模拟结果:\n"
        f"各次模拟抓取次数:\n"
        f"{' | '.join(individual_results)}\n\n"
        f"默认持有星辰碎屑和回想之核\n"
        f"平均结果（升到{max_grade}级）:\n"
        f"- 平均抓取次数: {avg_catches:.1f} 次\n"
        f"- 平均耗时: {days}天 {hours}小时 {minutes}分钟\n"
        f"- 平均无效事件（鱼类）: {avg_null_events:.1f} 次\n"
        f"- 平均Boss事件: {avg_boss:.1f} 次\n"
        f"- 平均掉坑事件: {avg_pit:.1f} 次\n"
        f"- 平均延迟时间: {avg_delay:.1f} 小时\n"
        f"- 平均每次获得经验: {avg_exp_per_catch:.2f}\n\n"
        f"概率分布变化:\n"
        f"6级后: 可抓2级 | 11级后: 可抓3级\n"
        f"16级后: 可抓4级 | 21级后: 可抓5级+音矿生效（满音矿）"
    )
    
    await simu_5.finish(message)