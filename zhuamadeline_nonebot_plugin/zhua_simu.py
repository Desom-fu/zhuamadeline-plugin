from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent
from nonebot.adapters.onebot.v11 import GROUP, Event
from nonebot.params import CommandArg
import random
import math
import datetime
from pathlib import Path
from .function import calculate_level_and_exp
from .config import bot_owner_id
from .whitelist import whitelist_rule

simu_5 = on_command("simu_5", permission=GROUP, priority=6, block=True, rule=whitelist_rule)

async def simulate_event(user_data, current_time):
    """模拟事件系统的影响"""
    # 初始化事件结果
    bonus_exp_multiplier = 1.0
    bonus_catches = 0
    delay_hours = 0
    
    # 17.5%概率掉坑（冷却2小时）
    if random.random() < 0.175:
        delay_hours = 2
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
            "音矿": 5000
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
    catch_interval = datetime.timedelta(minutes=30)
    total_delay_hours = 0
    boss_events = 0
    pit_events = 0
    
    while user_data["grade"] < max_grade:
        current_time = datetime.datetime.now() + total_time
        
        # 模拟事件
        exp_multiplier, bonus_catches, delay_hours = await simulate_event(user_data, current_time)
        total_delay_hours += delay_hours
        if delay_hours > 0:
            pit_events += 1
        if bonus_catches > 0:
            boss_events += 1
        
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
        catches_in_this_round = bonus_catches if bonus_catches > 0 else 1
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
        "total_delay": total_delay_hours
    }

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
    
    if max_grade < 1 or max_grade > 30:
        await simu_5.finish("最高等级必须在1-30之间")
        return
    if simulations < 1 or simulations > 100:
        await simu_5.finish("模拟次数必须在1-100之间")
        return
    
    # 运行多次模拟
    results = []
    individual_results = []  # 新增：存储每次模拟的单独结果
    for i in range(simulations):
        result = await run_single_simulation(max_grade)
        results.append(result)
        individual_results.append(f"第{i+1}次: {result['total_catches']}次")  # 新增：记录每次结果
    
    # 计算统计数据
    avg_catches = sum(r["total_catches"] for r in results) / simulations
    avg_time = sum(r["total_time"].total_seconds() for r in results) / simulations
    avg_boss = sum(r["boss_events"] for r in results) / simulations
    avg_pit = sum(r["pit_events"] for r in results) / simulations
    avg_delay = sum(r["total_delay"] for r in results) / simulations
    
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
        f"平均结果（升到{max_grade}级）:\n"
        f"- 平均抓取次数: {avg_catches:.1f} 次\n"
        f"- 平均耗时: {days}天 {hours}小时 {minutes}分钟\n"
        f"- 平均Boss事件: {avg_boss:.1f} 次\n"
        f"- 平均掉坑事件: {avg_pit:.1f} 次\n"
        f"- 平均延迟时间: {avg_delay:.1f} 小时\n"
        f"- 平均每次获得经验: {max_grade*10/avg_catches:.2f}\n"
        f"概率分布变化:\n"
        f"默认持有星辰碎屑\n"
        f"6级后: 可抓2级 | 11级后: 可抓3级\n"
        f"16级后: 可抓4级 | 21级后: 可抓5级+音矿生效（满音矿）"
    )
    
    await simu_5.finish(message)