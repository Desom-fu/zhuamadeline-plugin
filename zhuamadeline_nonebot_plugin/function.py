from nonebot.log import logger
from nonebot import get_driver
from nonebot.adapters.onebot.v11 import Bot
from operator import itemgetter
from pathlib import Path
from .list1 import *
from .list2 import *
from .list3 import *
from .list4 import *
from .shop import item
from .collection import collections
from .config import madeline_path_lc1, madeline_path_lc2, madeline_path_lc3, madeline_path_lc4 , liechang_count
from .config import *
import random
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
    'buff2_change_status'
]

#madeline图鉴
madeline_level1 = "madeline1"
madeline_level2 = "madeline2"
madeline_level3 = "madeline3"
madeline_level4 = "madeline4"
madeline_level5 = "madeline5"

#madeline名字
madeline_filename = "madeline{index}"

#开新猎场要改
file_names = {
    '1': "UserList1.json",
    '2': "UserList2.json",
    '3': "UserList3.json",
    '4': "UserList4.json",
}
# 字典映射来选择不同的 madeline_data
madeline_data_mapping = {
    '1': madeline_data1,
    '2': madeline_data2,
    '3': madeline_data3,
    '4': madeline_data4,
}

# 获取 NoneBot2 配置对象
config = get_driver().config

url_emoji_msg = f'http://localhost:9635/set_msg_emoji_like'

# 创建同步锁
lock = threading.Lock()

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

# 5猎经验值计算
def calculate_level_and_exp(data, user_id, level, isitem):
    """
    计算等级和经验值的增长
    参数:
        data: 用户数据字典
        user_id: 用户ID
        level: 本次获得的等级点数
        isitem: 是不是道具
    返回:
        tuple: (经验消息，等级消息，data主数据)
    """
    user_data = data[user_id]
    exp = user_data.get("exp", 0)
    grade = user_data.get("grade", 1)
    max_exp = user_data.get("max_exp", 10)
    collections = user_data.get("collections", {})
    
    exp_msg = ''
    grade_msg = ''
    
    # 如果满级直接返回
    if grade == max_grade:
        return exp_msg, grade_msg, data
        
    if isitem == 1:
        # 是道具就加levle//2的经验
        exp += level//2
    else:
        # 加等级点经验
        exp += level
        
    if exp > 0:
        # exp>0才加上消息
        exp_msg = f'\n本次抓Madeline获得{level}点经验，当前经验：{exp}/{max_exp}'

    if exp >= max_exp:
        # 计算升级
        exp -= max_exp
        grade += 1

        # 查找对应的经验增长值
        for level_range, increment in exp_growth.items():
            if grade in level_range:
                max_exp += increment
                break
        
        exp_msg = f'\n本次抓Madeline获得{level}点经验，当前经验：{exp}/{max_exp}'
        grade_msg = f'\n恭喜升级！当前等级：{grade}/{max_grade}'
        
        # 使用字典存储特殊等级消息
        special_grades = {
            6: f"恭喜升到{grade}级，现在你可以在神庙里面抓到2级的Madeline了！",
            11: f"恭喜升到{grade}级，现在你可以在神庙里面抓到3级的Madeline了！",
            16: f"恭喜升到{grade}级，现在你可以在神庙里面抓到4级的Madeline了！",
            21: f"恭喜升到{grade}级，现在你可以在神庙里面抓到5级的Madeline了，同时道具和祈愿的封印也解除了！",
        }

        if grade in special_grades:
            grade_msg += special_grades[grade]
        
        if grade == max_grade and collections.get("时隙沙漏", 0) == 0:
            collections['时隙沙漏'] = 1
            grade_msg += f"你已经达到最大等级{max_grade}，恭喜获得满级藏品奖励：时隙沙漏！这件由时之砂与虚空水晶制成的沙漏，能将你未使用的等待时间储存为抓取机会。输入.cp 时隙沙漏 以查看具体效果"

    # 更新数据
    user_data.update({"exp": exp, "grade": grade, "max_exp": max_exp})
    
    save_data(full_path, data)
    
    return exp_msg, grade_msg, data

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
    for lc, madeline_data in enumerate(madeline_data_mapping.values()):  # 开新猎场时要改
        if lc + 1 >= liechang_count+1:  # 忽略不存在的猎场 开新猎场时要改
            continue
        for k, v in madeline_data.items():
            max_count[lc][int(k) - 1] = len(v)

    # 读取用户数据
    user_data = {}
    for lc, file_name in enumerate(file_names.values()):
        if lc + 1 >= liechang_count+1:  # 忽略不存在的猎场 开新猎场时要改
            continue
        try:
            data = open_data(user_path / file_name)
            if str(user_id) in data:
                user_data[lc] = data[str(user_id)]
        except FileNotFoundError:
            continue

    # 计算收集数量
    for lc, madeline_data in enumerate(madeline_data_mapping.values()): # 开新猎场要改
        if lc + 1 >= liechang_count+1:  # 忽略不存在的猎场 开新猎场时要改
            continue
        if lc not in user_data:
            continue
        for k, v in user_data[lc].items():
            k_parts = k.split('_')  # 分割 madeline 信息
            level = int(k_parts[0]) - 1
            count[lc][level] += 1

    # 生成进度消息
    if target_level:
        if target_level > liechang_count:  # 忽略超过开放的猎场 开新猎场时要改
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
        for lc in range(liechang_count):  # 遍历 开新猎场时要改
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
        for lc in range(liechang_count):  # 遍历 开新猎场时要改
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

# def decode_buy_text(item_name_list, text):
#     a = text.split(" ")
#     item_name_lower = {name.lower(): name for name in item_name_list}  # 创建映射，保留原始大小写
#     item_key = a[0].lower()  # 用户输入的商品名转换为小写
    
#     # 检查两个参数的情况
#     if len(a) == 2:
#         if item_key in item_name_lower:
#             try:
#                 num = int(a[1])  # 检查数量是否是数字
#                 return [item_name_lower[item_key], num]  # 返回原始大小写的商品名
#             except ValueError:
#                 return None  # 第二个参数不是数字
#         else:
#             return None  # 商品名无效
#     # 只有一个参数时，默认数量为 1
#     elif len(a) == 1:
#         if item_key in item_name_lower:
#             return [item_name_lower[item_key], 1]  # 默认返回原始大小写的商品名
#         else:
#             return None
#     # 参数不符合预期
#     return None



#根据名字查找madeline的所在的猎场和等级和位置[等级，编号，几号猎场]
def find_madeline(value):
    # 遍历猎场编号1到4，开新猎场要改
    for lc in ['1', '2', '3', '4']:
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