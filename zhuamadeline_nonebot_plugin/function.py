from nonebot.log import logger
from nonebot import get_driver
from nonebot.adapters.onebot.v11 import Bot
from operator import itemgetter
from pathlib import Path
from .list1 import *
from .list2 import *
from .list3 import *
from .list4 import *
from .list5 import *
from .shop import item
from .collection import collections
from .config import *
import random
import math
import re
import datetime
import json
import threading
import requests
import asyncio
import json
import time

__all__ = [
    'madeline_path_lc1',
    'madeline_path_lc2',
    'madeline_path_lc3',
    'madeline_path_lc4',
    'current_liechang',
    'madeline_level1',
    'madeline_level2',
    'madeline_level3',
    'madeline_level4',
    'madeline_level5',
    'madeline_filename',
    'give_berry',
    'print_zhua',
    'zhua_random',
    'shop_list',
    'find_madeline',
    'time_text',
    'get_time_from_data',
    'time_decode',
    'open_data',
    'save_data',
    'data2_count',
    'debuff_clear',
    'tool_zhuamadeline',
    "get_madeline_data",
    "get_sorted_madelines",
    "madelinejd",
    'get_user_data',
    'emoji_like',
    'get_alias_name',
    'all_cool_time',
    'get_nickname',
    'calculate_spare_chance',
    'calculate_level_and_exp',
    'buff2_change_status',
    'init_data',
    'spawn_boss',
    'attack_boss',
    'get_boss_rewards',
    'get_world_boss_rewards'
]

#madeline图鉴
madeline_level1 = "madeline1"
madeline_level2 = "madeline2"
madeline_level3 = "madeline3"
madeline_level4 = "madeline4"
madeline_level5 = "madeline5"

#madeline名字
madeline_filename = "madeline{index}"

# 开新猎场要改
file_names = {
    '1': "UserList1.json",
    '2': "UserList2.json",
    '3': "UserList3.json",
    '4': "UserList4.json",
    '5': "UserList5.json",
}
# 字典映射来选择不同的 madeline_data
madeline_data_mapping = {
    '1': madeline_data1,
    '2': madeline_data2,
    '3': madeline_data3,
    '4': madeline_data4,
    '5': madeline_data5,
}

# 获取 NoneBot2 配置对象
config = get_driver().config

url_emoji_msg = f'http://localhost:9635/set_msg_emoji_like'

# 创建同步锁
lock = threading.Lock()

def init_data():
    """初始化全部数据文件"""
    if not boss_data_path.exists():
        with open(boss_data_path, 'w', encoding='utf-8') as f:
            json.dump({}, f)
    if not world_boss_data_path.exists():
        with open(world_boss_data_path, 'w', encoding='utf-8') as f:
            json.dump({"active": False, "hp": 0, "contributors": {}}, f)
    if not pvp_path.exists():
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump({}, f)
    if not pvp_coldtime_path.exists():
        with open(pvp_coldtime_path, 'w', encoding='utf-8') as f:
            json.dump({}, f)
    if not user_path1.exists():
        with open(user_path1, 'w', encoding='utf-8') as f:
            json.dump({}, f)
    if not user_path2.exists():
        with open(user_path2, 'w', encoding='utf-8') as f:
            json.dump({}, f)
    if not user_path3.exists():
        with open(user_path3, 'w', encoding='utf-8') as f:
            json.dump({}, f)
    if not user_path4.exists():
        with open(user_path4, 'w', encoding='utf-8') as f:
            json.dump({}, f)
    if not user_path5.exists():
        with open(user_path5, 'w', encoding='utf-8') as f:
            json.dump({}, f)
    if not garden_path.exists():
        with open(garden_path, 'w', encoding='utf-8') as f:
            json.dump({}, f)
    if not bar_path.exists():
        with open(bar_path, 'w', encoding='utf-8') as f:
            json.dump({}, f)
    if not demon_path.exists():
        with open(demon_path, 'w', encoding='utf-8') as f:
            json.dump({}, f)
    if not stuck_path.exists():
        with open(stuck_path, 'w', encoding='utf-8') as f:
            json.dump({}, f)
    if not cd_path.exists():
        with open(cd_path, 'w', encoding='utf-8') as f:
            json.dump({}, f)

# 获取QQ昵称
async def get_nickname(bot: Bot, user_id: str) -> str:
    try:
        user_info = await bot.get_stranger_info(user_id=int(user_id))
        return user_info.get("nickname", f"{user_id}")
    except:
        return f"玩家{user_id}"  # 获取失败时使用默认名称

# 用 run_in_executor 使 requests 在单独的线程中运行
async def async_request(url, data):
    loop = asyncio.get_event_loop()
    # 使用 run_in_executor 在后台线程执行 requests 请求
    response = await loop.run_in_executor(None, requests.post, url, data)
    return response

async def emoji_like(event, eid: int) -> dict:
    # 使用封装好的 json_emoji_like 函数
    data = json_emoji_like(event, eid)
    
    try:
        # 使用 run_in_executor 异步调用 requests
        response = await async_request(url_emoji_msg, data)
        
        # 检查响应状态码
        if response.status_code == 200:
            response_data = response.json()
            return response_data.get('data', None)
        else:
            logger.error(f"请求失败，状态码：{response.status_code}")
            return None
    except Exception as e:
        logger.error(f"调用 emoji_like 时出错: {e}")
        return None


def json_emoji_like(event, eid: int) -> dict:
    return {
        "message_id": event.message_id,
        "emoji_id": str(eid)
    }

# buff2逻辑处理
def buff2_change_status(data, user_id, buff2_status: str, change_status: int):
    """
    处理buff2状态逻辑
    参数:
        data: 完整数据字典
        user_id: 用户ID
        buff2_status: 看是哪种状态
        change_status: 1是加，0是扣
    返回:
        更新后的data
    """
    user_info = data.setdefault(str(user_id), {})
    user_info.setdefault("buff2", "normal")
    user_info.setdefault(f"{buff2_status}_times", 0)

    # 为1就加
    if change_status == 1:
        # 检查是否存在buff2状态
        if user_info["buff2"] == buff2_status:
            # 如果存在次数记录且大于0，增加次数
            if user_info[f"{buff2_status}_times"] > 0:
                user_info[f"{buff2_status}_times"] += 1
            # 如果次数为0，清除状态
            else:
                user_info["buff2"] = "normal"
    # 为0就扣
    elif change_status == 0:
        # 检查是否存在buff2状态
        if user_info["buff2"] == buff2_status:
            # 如果存在次数记录且大于0，增加次数
            if user_info[f"{buff2_status}_times"] > 0:
                user_info[f"{buff2_status}_times"] -= 1
            # 如果次数为0，清除状态
            else:
                user_info["buff2"] = "normal"
    # 其他数字直接返回
    return data

# 时隙沙漏相关计算
def calculate_spare_chance(data, user_id):
    if user_id not in data:
        return 0

    try:
        current_time = datetime.datetime.now()
        collections = data[user_id].get('collections', {})
        
        # 获取并解析时间节点
        time_nodes = []
        for time_key in ['work_end_time', 'next_time', 'last_valid_time']:
            if time_key in data[user_id]:
                time_nodes.append(datetime.datetime.strptime(
                    data[user_id][time_key], 
                    "%Y-%m-%d %H:%M:%S"
                ))
        
        # 计算最后限制时间
        last_limit = max(time_nodes) if time_nodes else current_time
        
        # 计算有效时间差
        time_diff = current_time - last_limit
        if time_diff.total_seconds() <= 0:
            return 0

        # 计算可累积次数
        interval_mins = 29 if collections.get("回想之核") else 30
        intervals = int(time_diff.total_seconds() / (interval_mins * 60))
        
        # 更新记录时间（仅当确实有时间积累时）
        if intervals > 0:
            data[user_id]['last_valid_time'] = current_time.strftime("%Y-%m-%d %H:%M:%S")
        
        return min(intervals, hourglass_max)
        
    except Exception as e:
        logger.error(f"时隙沙漏计算错误: {e}")
        return 0

#------------mymadeline相关指令----------------

# 获取猎场文件和对应数据
def get_madeline_data(file_name: str, user_id: str):
    data = open_data(user_path / file_name)

    if str(user_id) not in data:
        return None
    
    return data[str(user_id)]

# 获取并排序madeline库存
async def get_sorted_madelines(file_name: str, user_id: str, liechang_number: str):
    # 获取madeline数据
    data = get_madeline_data(file_name, user_id)
    sorted_madelines = [[] for _ in range(5)]  # 按等级分类
    level_str = ["一", "二", "三", "四", "五"]

    # 根据猎场编号获取对应的madeline数据
    madeline_data = madeline_data_mapping.get(liechang_number)

    if not madeline_data:
        return "无效的猎场数据"

    # 遍历数据，按等级分类
    for k, v in data.items():
        k = k.split('_')
        level = int(k[0]) - 1  # 获取等级
        num = k[1]

        # 获取对应的madeline名字并添加到sorted_madelines中
        sorted_madelines[level].append((madeline_data.get(str(level + 1)).get(num).get('name'), v))

    # 排序并拼接：从高等级到低等级排列
    result = []
    for i in range(4, -1, -1):  # 从高到低 (5级到1级)
        if sorted_madelines[i]:
            sorted_madelines[i].sort(key=lambda x: x[1], reverse=True)  # 按数量降序排序
            result.append(f"\n{level_str[i]}级：\n" + "\n".join(f"- {name} x {v}" for name, v in sorted_madelines[i]))
    
    return "\n".join(result) if result else "没有库存"


    
#------------madelinejd相关指令----------------

def madelinejd(user_id, target_level=None, nickname=None):
    # 初始化计数
    count = [[0, 0, 0, 0, 0] for _ in range(liechang_count)]  # 每个猎场的各级别 madeline 数量 [猎场][等级-1]
    max_count = [[0, 0, 0, 0, 0] for _ in range(liechang_count)]  # 每个猎场的各级别 madeline 总数 [猎场][等级-1]
    total_progress = None # 初始化防报错
    progress = None # 初始化防报错
    # 计算每个猎场的最大数量
    for lc, madeline_data in enumerate(madeline_data_mapping.values()):
        if lc + 1 >= liechang_count+1:  # 忽略不存在的猎场
            continue
        for k, v in madeline_data.items():
            max_count[lc][int(k) - 1] = len(v)

    # 读取用户数据
    user_data = {}
    for lc, file_name in enumerate(file_names.values()):
        if lc + 1 >= liechang_count+1:  # 忽略不存在的猎场
            continue
        try:
            data = open_data(user_path / file_name)
            if str(user_id) in data:
                user_data[lc] = data[str(user_id)]
        except FileNotFoundError:
            continue

    # 计算收集数量
    for lc, madeline_data in enumerate(madeline_data_mapping.values()): 
        if lc + 1 >= liechang_count+1:  # 忽略不存在的猎场
            continue
        if lc not in user_data:
            continue
        for k, v in user_data[lc].items():
            k_parts = k.split('_')  # 分割 madeline 信息
            level = int(k_parts[0]) - 1
            count[lc][level] += 1

    # 生成进度消息
    if target_level:
        if target_level > liechang_count:  # 忽略超过开放的猎场
            return f"{target_level}号猎场暂未开放，无法查看进度。"
        target_idx = target_level - 1
        total_captured = sum(count[target_idx])
        total_max = sum(max_count[target_idx])
        progress = round((total_captured / total_max) * 100, 2) if total_max > 0 else 0.0

        progress_message = f"这是 [{nickname}] 的Madeline进度\n"
        progress_message += f"\n本猎场共有{total_max}种玛德琳\n"
        progress_message += f"本猎场已有{total_captured}种玛德琳被你捕捉过\n"
        progress_message += f"\n{target_level}号猎场进度：{progress}%\n"
        for level in range(5, 0, -1):
            progress_message += (
                f"\n - {level}级Madeline：{count[target_idx][level - 1]}/"
                f"{max_count[target_idx][level - 1]}"
            )
    else:
        progress_message = f"这是 [{nickname}] 的Madeline进度\n"
        total_captured_all = 0
        total_max_all = 0

        # 计算总进度
        for lc in range(liechang_count):  # 遍历
            total_captured = sum(count[lc])
            total_max = sum(max_count[lc])
            total_captured_all += total_captured
            total_max_all += total_max

        progress_message += f"\n玛德琳猎场共有{total_max_all}种玛德琳\n"
        progress_message += f"已有{total_captured_all}种玛德琳被你捕捉过\n"

        total_progress = round((total_captured_all / total_max_all) * 100, 2) if total_max_all > 0 else 0.0
        progress_message += f"\n总进度：{total_progress}%"
        
        total_level_count = [0] * 5
        total_level_max = [0] * 5
        
        # 总进度
        for level in range(4, -1, -1):  # 从4到0
            total_level_count[level] = sum(count[lc][level] for lc in range(liechang_count))
            total_level_max[level] = sum(max_count[lc][level] for lc in range(liechang_count))
            progress_message += (
                f"\n- {level + 1}级Madeline：{total_level_count[level]}/{total_level_max[level]}"
            )
        # 逐级显示每个猎场的数量
        for lc in range(liechang_count):  # 遍历 
            total_captured = sum(count[lc])
            total_max = sum(max_count[lc])
            hunt_progress = round((total_captured / total_max) * 100, 2) if total_max > 0 else 0.0

            progress_message += f"\n\n{lc + 1}号猎场进度：{hunt_progress}%"
            for level in range(5, 0, -1):
                progress_message += (
                    f"\n- {level}级Madeline：{count[lc][level - 1]}/{max_count[lc][level - 1]}"
                )

    return progress_message, total_progress, progress


#------------其他指令----------------
# 添加全局冷却
def all_cool_time(cd_path, user_id, group_id):
    # 添加全局冷却
    now_time = time.time()
    cd_data = open_data(cd_path)
    cd_data.setdefault(user_id, {})["coldtime"] = now_time
    cd_data.setdefault("group", {}).setdefault(group_id, {})["coldtime"] = now_time
    save_data(cd_path, cd_data)

# 辅助函数：获取标准名称
def get_alias_name(name, item_dict, alias_dict):
    """
    智能别名匹配（支持任意位置的别名替换）
    修改后的逻辑：
        1. 直接匹配完整名称（优先检查）
        2. 检查字符串中是否已经包含任何全称，如果有则返回None
        3. 扫描整个字符串，查找最长的别名匹配
        4. 替换匹配到的别名，保留其余部分
    """
    # 1. 直接匹配完整名称（优先检查）
    if name in item_dict:
        return name
    
    # 2. 检查字符串中是否已经包含任何全称
    for std_name in alias_dict.keys():
        if std_name in name:
            return None  # 如果已经包含全称，则不进行别名匹配
    
    max_len = max(len(alias) for aliases in alias_dict.values() for alias in aliases) if alias_dict else 0
    best_match = None
    best_len = 0
    
    # 3. 扫描整个字符串，查找最长的别名匹配
    for i in range(len(name)):
        for l in range(min(max_len, len(name) - i), 0, -1):
            substring = name[i:i+l]
            
            for std_name, aliases in alias_dict.items():
                if substring in aliases and l > best_len:
                    best_match = (i, l, std_name)
                    best_len = l
    
    # 4. 替换匹配到的别名
    if best_match:
        i, l, std_name = best_match
        return name[:i] + std_name + name[i+l:]
    
    return None  # 未找到匹配

# 获取用户数据的方法，避免重复的 try-except
def get_user_data(user_data, user_id, key, default='normal'):
    return user_data.get(str(user_id), {}).get(key, default)

#确定猎场路径
def current_liechang(command):
    # 动态获取对应的路径变量
    path = globals().get(f"madeline_path_lc{command}")
    if path is None:  # 如果路径无效
        raise ValueError("错误的猎场号")
    return path


#奖励草莓
def give_berry(level):
    if(level==1): berry_give = 5
    if(level==2): berry_give = 10
    if(level==3): berry_give = 15
    if(level==4): berry_give = 20
    if(level==5): berry_give = 25   
    return berry_give

#给定madeline的文件坐标，输出该madeline相关的信息 [等级，名字，图像路径，描述，编号，猎场编号]
def print_zhua(level, num, liechang_number):
    madeline_path = current_liechang(liechang_number)
    #锁定madeline档案
    # 使用globals()动态获取变量
    current_data = globals().get(f"madeline_data{liechang_number}")
    if current_data is None:  # 检查变量是否存在
        raise ValueError("错误的猎场号")

    #根据猎场确定路径
    madeline_level1_path = madeline_path / madeline_level1
    madeline_level2_path = madeline_path / madeline_level2
    madeline_level3_path = madeline_path / madeline_level3
    madeline_level4_path = madeline_path / madeline_level4
    madeline_level5_path = madeline_path / madeline_level5
    #根据等级确定坐标
    if(level == 1): zhua_path = madeline_level1_path
    if(level == 2): zhua_path = madeline_level2_path
    if(level == 3): zhua_path = madeline_level3_path
    if(level == 4): zhua_path = madeline_level4_path
    if(level == 5): zhua_path = madeline_level5_path
    #名字信息
    name = current_data.get(str(level)).get(str(num)).get('name')
    #图片信息
    houzhui = '.png'
    if(current_data.get(str(level)).get(str(num)).get('gif',False)): houzhui = '.gif' #自动加后缀名
    if(current_data.get(str(level)).get(str(num)).get('jpg',False)): houzhui = '.jpg' #自动加后缀名
    madeline_file_name = madeline_filename.format(index=str(num)) + houzhui
    img = zhua_path / madeline_file_name
    #描述信息
    description = current_data.get(str(level)).get(str(num)).get('description')
    #确定该madeline的打印信息
    madeline = [level, name, img, description, num, liechang_number]
    return madeline

#madeline的抓取函数
def zhua_random(a=10, b=50, c=200, d=500, liechang_number='1'):
    #随机选择一个等级
    rnd = random.randint(1,1000)
    level = 1
    if(rnd <= a): level = 5
    if(rnd > a and rnd <= b): level = 4
    if(rnd > b and rnd <= c): level = 3
    if(rnd > c and rnd <= d): level = 2
    if(rnd > d and rnd <= 1000): level = 1
    #根据猎场确定路径
    madeline_path = current_liechang(liechang_number)
    #各等级路径
    madeline_level1_path = madeline_path / madeline_level1
    madeline_level2_path = madeline_path / madeline_level2
    madeline_level3_path = madeline_path / madeline_level3
    madeline_level4_path = madeline_path / madeline_level4
    madeline_level5_path = madeline_path / madeline_level5
    #锁定madeline档案
    # 动态拼接变量名获取值
    current_name_list = globals().get(f"madeline_name_list{liechang_number}")
    current_data = globals().get(f"madeline_data{liechang_number}")

    if current_name_list is None or current_data is None:  # 检查变量是否存在
        raise ValueError("错误的猎场号")
    #根据等级确定坐标
    if(level == 1): zhua_path = madeline_level1_path
    if(level == 2): zhua_path = madeline_level2_path
    if(level == 3): zhua_path = madeline_level3_path
    if(level == 4): zhua_path = madeline_level4_path
    if(level == 5): zhua_path = madeline_level5_path
    #选好等级后在该等级中随机抓取
    length = len(current_name_list[str(level)])
    num = random.randint(1,length)
    logger.info(f"{level}级madeline，该级共{length}个，选择了{num}号")
    #名字信息
    name = current_data.get(str(level)).get(str(num)).get('name')
    #图片信息
    houzhui = '.png'
    if(current_data.get(str(level)).get(str(num)).get('gif',False)): houzhui = '.gif' #自动加后缀名
    if(current_data.get(str(level)).get(str(num)).get('jpg',False)): houzhui = '.jpg' #自动加后缀名
    madeline_file_name = madeline_filename.format(index=str(num)) + houzhui
    img = zhua_path / madeline_file_name
    #描述信息
    description = current_data.get(str(level)).get(str(num)).get('description')
    #确定该madeline的打印信息
    madeline = [level, name, img, description, num, liechang_number]
    return madeline

######打印商品信息######
def shop_list(item_list):
    # 配置映射表（数据源、价格单位、名称后缀）
    LEVEL_CONFIG = {
        7: {"source": collections, "unit": "点能量", "suffix": "藏品"},
        8: {"source": collections, "unit": "颗草莓", "suffix": "藏品"},
    }
    # 默认配置：0-6级道具
    for level in range(7):
        LEVEL_CONFIG[level] = {"source": item, "unit": "颗草莓", "suffix": "道具"}
    
    # 等级名称映射
    LEVEL_NAME = {
        0: "一级", 1: "二级", 2: "三级", 3: "四级", 4:'旅行',
        5: "永久", 6: "特殊", 7: "能量", 8: "草莓"
    }
    
    parts = []
    # 倒序处理所有等级
    for level in range(8, -1, -1):
        config = LEVEL_CONFIG[level]
        items = []
        # 遍历数据源收集商品
        for name, details in config["source"].items():
            # 兼容不同长度的数据结构
            price = details[0]
            lv = details[1]
            
            if lv == level + 1 and name in item_list:
                items.append((name, price, item_list[name]))
        
        if not items:
            continue
        
        # 构建该等级文本
        title = f"\n{LEVEL_NAME[level]}{config['suffix']}："
        item_lines = []
        for name, price, qty in items:
            item_lines.append(
                f"- {name} x {qty}\n   单价：[{price}]{config['unit']}"
            )
        parts.append(title + "\n" + "\n".join(item_lines))
    
    # 拼接最终文本
    if not parts:
        return "今日商品\n————————————\n\n暂无商品"
    
    divider = "\n————————————\n"
    return (
        "今日商品" + 
        divider + 
        divider.join(parts) + 
        ("\n————————————\n" if len(parts) > 1 else "")
    )

#根据名字查找madeline的所在的猎场和等级和位置[等级，编号，几号猎场]
def find_madeline(value):
    # 开新猎场要改
    for lc in ['1', '2', '3', '4', "5"]:
        # 动态获取对应的 madeline_data
        data = globals().get(f"madeline_data{lc}")
        if data is None:
            continue  # 如果没有找到该猎场的数据，跳过
        # 遍历数据
        for k, v in data.items():
            for i, j in v.items():
                if j['name'].lower() == value:
                    return [k, i, lc]  # 返回等级、编号、猎场编号
    return 0


#将日期间隔转化成想要表达的形式
def time_text(delta_time):
    a = re.findall(r'\d+', str(delta_time))
    logger.info(f"{a[-4]}小时{a[-3]}分钟{a[-2]}秒：f{delta_time}")
    text = ""
    if(int(a[-4])!=0):
        text += f"{a[-4]}小时"
    if(int(a[-3])!=0):
        text += f"{a[-3]}分钟"
    text += f"{a[-2]}秒"
    
    return text

##频繁调用的长语句##
#读取某用户数据中的日期信息
def get_time_from_data(data):
    return datetime.datetime.strptime(data.get('next_time'), "%Y-%m-%d %H:%M:%S")

#将时间对象转换成可储存在用户数据中的字符串
def time_decode(time):
    return time.strftime("%Y-%m-%d %H:%M:%S")

# 打开数据文件
def open_data(file):
    data = {}
    with lock:  # 在读写文件时加锁，确保只有一个线程/协程能执行此操作
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    return data

# 保存数据结构到数据文件内
def save_data(file, data):
    with lock:  # 在读写文件时加锁，确保只有一个线程/协程能执行此操作
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)


#--------------------------暂时先把这些可能的常用函数放在这里--------------------------

def data2_count(user_id = '121096913', level = '1', num = '1', lc = '1') -> list:
    '''
    对于二猎及以后的计数方法
    参数需要输入的东西已经很明确了
    返回一个列表，如果没出新则列表第二项为""
    '''
    data2 = open_data(user_path / f"UserList{lc}.json")
    new_print = ""
    if(str(user_id) in data2):
        if(not (str(level)+'_'+str(num)) in data2[str(user_id)]):
            new_print = "恭喜你抓出来一个新madeline！\n"  #如果出新就添加文本
            data2[str(user_id)][str(level)+'_'+str(num)] = 0
        data2[str(user_id)][str(level)+'_'+str(num)] += 1  #数量+1
    else:
        new_print = "恭喜你抓出来一个新madeline！\n"  #如果出新就添加文本
        data2[str(user_id)] = {}
        data2[str(user_id)][str(level)+'_'+str(num)] = 1  
    result = []
    result.append(data2)
    result.append(new_print)
    return result

def debuff_clear(data,user_id):
    '''
    这个方法如果玩家恢复时间已到，则直接将debuff清除
    不需要返回任何东西
    参数需要输入对应的data和用户id
    '''
    current_time = datetime.datetime.now()
    if(not 'next_recover_time' in data[str(user_id)]):
        data[str(user_id)]['next_recover_time'] = current_time.strftime("%Y-%m-%d %H:%M:%S")
        save_data(user_path / file_name, data)

    recover_time = datetime.datetime.strptime(data.get(str(user_id)).get('next_recover_time'), "%Y-%m-%d %H:%M:%S")
    if recover_time <= current_time:
        data[str(user_id)]["debuff"] = "normal"
        save_data(user_path / file_name, data)

def tool_zhuamadeline(information, data, user_id) -> list:
    '''
    这个方法用于处理道具抓和祈愿的情况，主要是直接写入
    返回最后一项加入了new_print的information列表
    参数需要输入对应的data和用户id
    '''
    new_print = ""
    #得到madeline信息
    level       = information[0]   #等级
    name        = information[1]   #名字
    img         = information[2]   #图片
    description = information[3]   #描述
    num         = information[4]   #编号
    lc          = information[5]   #所属猎场

    #打开副表
    data2 = open_data(user_path / f"UserList{lc}.json")

    #计数
    countList = data2_count(user_id, level, num, lc)
    data2 = countList[0]
    new_print = countList[1]
                
    #写入副表
    save_data(user_path / f"UserList{lc}.json", data2)                

    #写入文件
    save_data(user_path / file_name, data)
    
    result = information
    result.append(new_print)
    return result

# 5猎相关
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
    if grade == max_grade:
        return exp_msg, grade_msg, data
        
    # 1. 计算获得的经验值
    if isitem == 1:
        gained_exp = level // 2  # 道具获得一半经验
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
    while exp >= max_exp and grade < max_grade:
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
        grade_msg = f'\n恭喜升级！当前等级：{grade}/{max_grade}' + grade_msg
        # 没有满级才显示升级后经验
        if grade < max_grade:
            grade_msg += f'\n升级后经验：{exp}/{max_exp}'
    # 如果没有升级但经验有变化，也显示最终状态
    # elif gained_exp > 0:
        # exp_msg += f'\n当前经验：{exp}/{max_exp}'

    # 提添加藏品
    if grade == max_grade and collections.get("时隙沙漏", 0) == 0:
        collections['时隙沙漏'] = 1
        grade_msg += f"\n你已经达到最大等级{max_grade}！\n倏然，你手中入场券的那一点金色光芒突然闪烁起来！\n你慢慢的看着它融化，重组，最后在你手中变成了散发着淡金色光芒的蓝色沙漏。\n输入.cp 时隙沙漏 以查看具体效果"
    
    # 更新数据
    user_data.update({
        "exp": exp, 
        "grade": grade, 
        "max_exp": max_exp,
        "collections": collections
    })
    
    save_data(full_path, data)
    
    return exp_msg, grade_msg, data

# boss相关
def spawn_boss(user_id, grade, boss_type=None):
    """生成Boss，可以指定类型"""
    if not boss_type:
        if grade < 6:
            boss_type = "mini"
        elif grade < 11:
            boss_type = random.choice(["mini", "normal"])
        else:
            boss_type = random.choice(["mini", "normal", "hard"])
    
    if boss_type == "mini":
        hp = random.randint(10, 20)
    elif boss_type == "normal":
        hp = random.randint(30, 50)
    else:  # hard
        hp = random.randint(60, 80)
    
    name = random.choice(boss_names[boss_type])
    
    boss_data = {
        "type": boss_type,
        "name": name,
        "hp": hp,
        "max_hp": hp,
        "spawn_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    data = open_data(boss_data_path)
    data[user_id] = boss_data
    save_data(boss_data_path, data)
    return boss_data

def spawn_world_boss():
    """生成世界Boss"""
    hp = random.randint(300, 500)
    name = random.choice(boss_names["world"])
    
    boss_data = {
        "active": True,
        "name": name,
        "hp": hp,
        "max_hp": hp,
        "spawn_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "contributors": {}
    }
    
    save_data(world_boss_data_path, boss_data)
    return boss_data

def attack_boss(user_id, damage, is_world_boss=False):
    """攻击Boss"""
    if is_world_boss:
        data = open_data(world_boss_data_path)
        boss_data = data
    else:
        data = open_data(boss_data_path)
        boss_data = data.get(user_id, {})
    
    # 指虎伤害翻倍
    big_damage_msg = ''
    user_data = open_data(full_path)
    big_attack = user_data[user_id]['collections'].get("暴击指虎", 0)
    if big_attack >= 1 and random.randint(1, 100) <= 10:
        damage *= 2
        big_damage_msg += '尖锐的指虎狠狠地扎进了boss的要害，本次攻击造成的伤害翻倍！\n'
    
    if not boss_data:
        return False, "没有找到Boss"
    
    boss_data["hp"] -= damage
    if boss_data["hp"] <= 0:
        boss_data["hp"] = 0
    
    # 记录贡献
    if is_world_boss:
        boss_data["contributors"][user_id] = boss_data["contributors"].get(user_id, 0) + damage
        if boss_data["hp"] <= 0:
            boss_data["active"] = False
    else:
        if boss_data["hp"] <= 0:
            del data[user_id]
    
    save_data(world_boss_data_path if is_world_boss else boss_data_path, data)
    return True, boss_data, big_damage_msg, damage

def get_boss_rewards(boss_data, user_id, grade):
    """获取击败Boss的奖励
    返回: (奖励字典, 经验值, 奖励消息)"""
    is_max_grade = grade >= max_grade
    reward_msg = ""
    
    if boss_data["type"] == "mini":
        exp = math.floor(boss_data["max_hp"] * 1.3)
        berry = random.randint(100, 200)
        if is_max_grade:
            berry *= 2
            reward_msg = f"你已击败迷你Boss[{boss_data['name']}]！\n由于已满级，获得双倍奖励：{berry}颗草莓"
            return {"berry": berry}, exp, reward_msg
        reward_msg = f"你已击败迷你Boss[{boss_data['name']}]！\n获得{berry}颗草莓"
        return {"berry": berry}, exp, reward_msg
        
    elif boss_data["type"] == "normal":
        exp = math.floor(boss_data["max_hp"] * 1.4)
        items = {
            "迅捷药水": random.randint(1, 2),
            "幸运药水": random.randint(1, 2),
        }
        if is_max_grade:
            items["迅捷药水"] *= 2
            items["幸运药水"] *= 2
            reward_msg = f"你已击败普通Boss[{boss_data['name']}]！\n由于已满级，获得双倍奖励："
        else:
            reward_msg = f"你已击败普通Boss[{boss_data['name']}]！\n获得："
        
        item_list = [f"{k}x{v}" for k, v in items.items() if v > 0]
        reward_msg += "、".join(item_list)
        return {"items": items}, exp, reward_msg
        
    elif boss_data["type"] == "hard":
        exp = math.floor(boss_data["max_hp"] * 1.5)
        berry = random.randint(200, 400)
        items = {
            "迅捷药水": random.randint(1, 2),
            "幸运药水": random.randint(1, 2),
            "道具盲盒": random.randint(5, 10),
        }
        if is_max_grade:
            berry *= 2
            for k in items:
                items[k] *= 2
            reward_msg = f"你已击败精英Boss[{boss_data['name']}]！\n由于已满级，获得双倍奖励：{berry}颗草莓、"
        else:
            reward_msg = f"你已击败精英Boss[{boss_data['name']}]！\n获得{berry}颗草莓、"
        
        item_list = [f"{k}x{v}" for k, v in items.items() if v > 0]
        reward_msg += "、".join(item_list)
        return {"berry": berry, "items": items}, exp, reward_msg
    
    return {}, 0, ""

def get_world_boss_rewards():
    """获取世界Boss奖励
    返回: (排行榜奖励列表, 全员奖励字典)"""
    data = open_data(world_boss_data_path)
    contributors = sorted(data["contributors"].items(), key=lambda x: x[1], reverse=True)[:5]
    
    # 排行榜奖励配置
    rank_rewards = [
        {"berry": 600, "items": {"迅捷药水": 5, "幸运药水": 5, "道具盲盒": 10}},  # 第一名
        {"berry": 550, "items": {"迅捷药水": 4, "幸运药水": 4, "道具盲盒": 9}},  # 第二名
        {"berry": 500, "items": {"迅捷药水": 3, "幸运药水": 3, "道具盲盒": 8}},  # 第三名
        {"berry": 450, "items": {"迅捷药水": 2, "幸运药水": 2, "道具盲盒": 7}},  # 第四名
        {"berry": 400, "items": {"迅捷药水": 1, "幸运药水": 1, "道具盲盒": 6}}   # 第五名
    ]
    
    # 构建排行榜数据
    rewards = []
    for i, (user_id, damage) in enumerate(contributors):
        rewards.append((user_id, rank_rewards[i], f"{i+1}名奖励"))
    
    # 全员奖励 (伤害x2)
    all_rewards = {}
    for user_id, damage in data["contributors"].items():
        all_rewards[user_id] = {"exp": damage * 2}
    
    return rewards, all_rewards