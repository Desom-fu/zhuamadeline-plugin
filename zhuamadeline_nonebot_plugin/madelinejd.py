from nonebot.adapters.onebot.v11 import GROUP
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Event
from nonebot.adapters.onebot.v11 import MessageSegment, Message
from nonebot import on_command, on_fullmatch
from nonebot.params import CommandArg
from operator import itemgetter
from pathlib import Path
# import re
import json
import asyncio
#加载文件操作系统
import datetime
from .madelinejd import *
from .config import *
from .list1 import *
from .list2 import *
from .list3 import *
from .function import *
from .whitelist import whitelist_rule
from .shop import fish_prices

__all__ = [
    "mymadeline",
    "jd",
    'total_madelinejd_query',
    "display_all_liechang_inventory",
    "show",
    "count_madeline",
]

user_path = Path() / "data" / "UserList"
file_name = "UserData.json"
bar_path = Path() / "data" / "UserList" / "bar.json"

# 开新猎场要改
file_names = {
    '1': "UserList1.json",
    '2': "UserList2.json",
    '3': "UserList3.json",
    '4': "UserList4.json",
}

user_list1 = Path() / "data" / "UserList" / "UserList1.json"
user_list2 = Path() / "data" / "UserList" / "UserList2.json"
user_list3 = Path() / "data" / "UserList" / "UserList3.json"
user_list4 = Path() / "data" / "UserList" / "UserList4.json"


# 获取QQ昵称
async def get_nickname(bot: Bot, user_id: str) -> str:
    try:
        user_info = await bot.get_stranger_info(user_id=int(user_id))
        return user_info.get("nickname", f"用户{user_id}")
    except:
        return f"用户{user_id}"  # 获取失败时使用默认名称

# 草莓排行
ranking = on_command('berryrank', permission=GROUP, priority=1, block=True, rule=whitelist_rule)

@ranking.handle()
async def ranking_handle(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    user_id = str(event.user_id)  # 获取当前用户 ID
    
    arg = str(args).strip().lower()
    if not arg:
        arg = ""

    # 读取数据
    try:
        data = open_data(user_path / file_name)
        bar_data = open_data(bar_path)
    except (FileNotFoundError, json.JSONDecodeError):
        await ranking.finish("❌ 无法读取用户数据！", at_sender=True)
        return

    # 计算所有用户的草莓总量
    berry_rank = []
    for uid, user_data in data.items():
        if not isinstance(user_data, dict):
            continue

        berry = user_data.get("berry", 0)
        bank = bar_data.get(uid, {}).get("bank", 0)
        jam = user_data.get("item", {}).get('草莓果酱', 0) * 248

        # 计算鱼类的总价值
        fish_total_value = sum(user_data.get("item", {}).get(fish, 0) * price for fish, price in fish_prices.items())

        # 总草莓 = 现有草莓 + 银行 + 果酱 + 鱼的总价值
        total_berry = berry + bank + jam + fish_total_value
        berry_rank.append((uid, berry, bank, jam, fish_total_value, total_berry))

    # 按草莓总量降序排序
    berry_rank.sort(key=lambda x: x[5], reverse=True)

    if not berry_rank:
        await ranking.finish("⚠️ 当前没有任何玩家的数据！", at_sender=True)
        return

    # **按草莓总数降序排列（全服排名）**
    rank_msg = ""
    user_rank = None

    # **先计算所有用户的实际排名**
    actual_ranks = {}  # 存储所有用户的排名
    prev_total_berry = None
    displayed_rank = 0  # 记录实际排名

    for i, (uid, _, _, _, _, total_berry) in enumerate(berry_rank, start=1):
        if total_berry != prev_total_berry:
            displayed_rank = i  # 只有当草莓总量变化时，排名才变化
        prev_total_berry = total_berry
        actual_ranks[uid] = displayed_rank  # 存储每个用户的实际排名

    # **选择显示正序或倒序**
    if arg == "down":  # **倒数排名**
        title_msg = '倒数前10名'
        rank_msg = "📉 倒数前 10 名 🍓\n\n"
        selected_users = berry_rank[-10:]  # 取后 10 名
    else:
        title_msg = '全服草莓排名'
        rank_msg = "📜 全服草莓排名 🍓\n\n"
        selected_users = berry_rank[:10]  # 取前 10 名

    # 获取选中玩家的昵称
    selected_nicknames = await asyncio.gather(*[get_nickname(bot, uid) for uid, _, _, _, _, _ in selected_users])

    for (uid, berry, bank, jam, fish_value, total_berry), nickname in zip(selected_users, selected_nicknames):
        rank_msg += (
            f"{actual_ranks[uid]}. {nickname} • {total_berry} 颗草莓\n"
            f"（持有: {berry}颗）\n（银行: {bank}颗）\n（果酱: {jam//248}*248={jam}颗）\n（鱼类: {fish_value}颗）\n\n"
        )

    # 查找当前用户排名（如果不在前10或倒数10）
    if user_rank is None:
        prev_total_berry = None
        for i, (uid, _, _, _, _, total_berry) in enumerate(berry_rank, start=1):
            if total_berry != prev_total_berry:
                displayed_rank = i  # 只有草莓总数变化时，才更新排名
            prev_total_berry = total_berry

            if uid == user_id:
                user_rank = displayed_rank
                break

    # 显示当前用户排名
    user_berry = data.get(user_id, {}).get("berry", 0)
    user_bank_berry = bar_data.get(user_id, {}).get("bank", 0)
    user_jam_berry = data.get(user_id, {}).get("item", {}).get("草莓果酱", 0) * 248
    user_fish_value = sum(data.get(user_id, {}).get("item", {}).get(fish, 0) * price for fish, price in fish_prices.items())

    user_nickname = await get_nickname(bot, user_id)
    rank_msg += (
        f"🔹 {user_nickname}的排名为：{user_rank}，"
        f"拥有 {user_berry} + {user_bank_berry} + {user_jam_berry} + {user_fish_value} = "
        f"{user_berry + user_bank_berry + user_jam_berry + user_fish_value} 颗草莓"
    )

    # 构建转发消息
    forward_messages = [
        {
            "type": "node",
            "data": {
                "name": title_msg,
                "uin": event.self_id,
                "content": rank_msg
            }
        }
    ]

    # 转发消息
    if forward_messages:
        await bot.send_group_forward_msg(
            group_id=event.group_id,
            messages=forward_messages
        )

# 统一处理mymadeline命令，支持查询单个猎场或所有猎场的库存，并保留0点的特殊事件
mymadeline = on_command('mymadeline', aliases={"mymade","mymadline","my玛德琳","我的玛德琳","my"}, permission=GROUP, priority=1, block=True, rule=whitelist_rule)
@mymadeline.handle()
async def mymadeline_handle(bot: Bot, event: GroupMessageEvent, arg: Message = CommandArg()):
    # 获取当前时间（小时、分钟、秒）
    current_time = datetime.datetime.now().time()
    hour, minute, second = current_time.hour, current_time.minute, current_time.second
    user_id = event.get_user_id()

    # 半夜0点整查看库存时，隐藏并返回特殊事件
    if hour == 0 and minute == 0 and 0 <= second <= 30:
        msg_list = [{
            "type": "node",
            "data": {
                "name": "库存查询室",
                "uin": event.self_id,
                "content": 'please give me your eyes'
            }
        }]
        await bot.call_api("send_group_forward_msg", group_id=event.group_id, messages=msg_list)
        return
    
    # 如果没有输入猎场号，默认展示所有猎场的库存
    if not arg:
        await display_all_liechang_inventory(bot, event, user_id)
        return
    
    # 获取输入的猎场号
    args = str(arg).split()
    # 判断是否输入了有效的猎场号（1, 2, 3）
    if all(liechang not in file_names for liechang in args):
        await bot.send(event, "输入的猎场号无效，请重新输入！", at_sender=True)
        return

    # 遍历输入的猎场号，分别显示对应猎场的库存
    for liechang_number in args:
        if liechang_number in file_names:
            await display_liechang_inventory(bot, event, liechang_number, user_id)

# 查询并展示指定猎场的库存
async def display_liechang_inventory(bot: Bot, event: GroupMessageEvent, liechang_number: str, user_id):
    file_name = file_names.get(liechang_number)
    
    # 获取madeline数据
    data = get_madeline_data(file_name, user_id)
    if data is None:
        await bot.send(event, f"你没有抓到过{liechang_number}号猎场的madeline", at_sender=True)
        return
    
    # 获取madeline库存并按等级分类
    sorted_madelines = await get_sorted_madelines(file_name, user_id, liechang_number)
    
    # 返回库存信息
    user_info = await bot.get_stranger_info(user_id=int(user_id))
    nickname = user_info.get("nickname", "未知昵称")
    
    msg_list = [{
        "type": "node",
        "data": {
            "name": "库存查询室",
            "uin": event.self_id,
            "content": f"这是 [{nickname}] 的{liechang_number}号猎场的madeline库存\n{sorted_madelines}"
        }
    }]
    
    await bot.call_api("send_group_forward_msg", group_id=event.group_id, messages=msg_list)

# 查询并展示所有猎场的库存
async def display_all_liechang_inventory(bot: Bot, event: GroupMessageEvent, user_id):
    all_sorted_madelines = []

    # 遍历所有猎场，获取每个猎场的库存
    for liechang_number in file_names:
        file_name = file_names[liechang_number]

        # 获取madeline数据
        data = get_madeline_data(file_name, user_id)
        if data is None:
            all_sorted_madelines.append(f"你没有抓到过{liechang_number}号猎场的madeline")
            continue

        # 获取madeline库存并按等级分类
        sorted_madelines = await get_sorted_madelines(file_name, user_id, liechang_number)
        
        all_sorted_madelines.append(f"猎场{liechang_number}的madeline库存:\n{sorted_madelines}")

    # 合并并发送所有猎场的库存
    user_info = await bot.get_stranger_info(user_id=int(event.get_user_id()))
    nickname = user_info.get("nickname", "未知昵称")
    
    msg_list = [{
        "type": "node",
        "data": {
            "name": "库存查询室",
            "uin": event.self_id,
            "content": f"这是 [{nickname}] 的所有猎场madeline库存"
        }
    }]
    
    for sorted_madeline in all_sorted_madelines:
        msg_list.append({
            "type": "node",
            "data": {
                "name": "库存查询室",
                "uin": event.self_id,
                "content": sorted_madeline
            }
        })

    await bot.call_api("send_group_forward_msg", group_id=event.group_id, messages=msg_list)

# 查询进度，具体函数也丢function.py里了
jd = on_command('jd', aliases={"madelinejd"}, permission=GROUP, priority=1, block=True, rule=whitelist_rule)
@jd.handle()
async def zhuajd(bot: Bot, event: Event, args: Message = CommandArg()):
    user_id = event.get_user_id()
    message = args.extract_plain_text().strip()  # 提取指令后的参数
    target_level = None
    if message:
        try:
            target_level = int(message)
            if target_level < 1 or target_level > liechang_count:
                raise ValueError
        except ValueError:
            await jd.finish(f"猎场等级只能是1到{liechang_count}之间的整数！")
            return
    # 获取进度消息
    progress_message, total_progress, progress = madelinejd(user_id, target_level, event.sender.nickname)
    if progress_message is None:
        await jd.finish("你还没有尝试抓过madeline.....")
        return
    # 发送进度消息
    msg_list = [
        {
            "type": "node",
            "data": {
                "name": "进度",
                "uin": event.self_id,
                "content": progress_message
            }
        }
    ]

    await bot.call_api("send_group_forward_msg", group_id=event.group_id, messages=msg_list)

# 全服进度排名指令
rankingjd = on_command('jdrank', permission=GROUP, priority=1, block=True, rule=whitelist_rule)

@rankingjd.handle()
async def rankingjd_handle(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    user_id = str(event.user_id)  # 获取当前用户 ID
    
    arg = str(args).strip().lower()
    if not arg:
        arg = ""
    else:
        # 猎场号转换为int，方便扩展
        try:
            arg = int(arg)
        except:
            await rankingjd.finish("请输入正确的猎场号！", at_sender=True)
            
    # 读取数据
    try:
        data = open_data(user_path / file_name)
    except (FileNotFoundError, json.JSONDecodeError):
        await rankingjd.finish("❌ 无法读取用户数据！", at_sender=True)
        return

    # 获取所有玩家的 UID
    player_uids = [uid for uid, user_data in data.items() if isinstance(user_data, dict)]

    if not player_uids:
        await rankingjd.finish("⚠️ 当前没有任何玩家的数据！", at_sender=True)
        return

    # 存储每个用户的 total_progress 和 progress
    progress_data = []

    # 遍历每个UID并调用 madelinejd 函数
    for id in player_uids:
        try:
            arg_value = int(arg) if arg else None
            progress_message, total_progress, progress = madelinejd(id, arg_value)
            progress_data.append({
                'user_id': id,
                'total_progress': total_progress,
                'progress': progress
            })
        except ValueError:
            await rankingjd.finish("无效的猎场号！请确保 <猎场号> 是一个整数且目前存在该猎场。", at_sender=True)
            return

    # **总进度排名**
    if arg == '':  
        title_msg = '全服总进度排名'
        rank_msg = "📜 全服总进度排名 📊\n"
        sorted_rank = sorted(progress_data, key=lambda x: x['total_progress'], reverse=True)

        top_10 = sorted_rank[:10]
        top_10_nicknames = await asyncio.gather(*[get_nickname(bot, uid) for uid in [entry['user_id'] for entry in top_10]])

        rank = 0
        prev_progress = None
        user_rank = None  # 当前用户的排名

        for i, (entry, nickname) in enumerate(zip(top_10, top_10_nicknames)):
            if entry['total_progress'] != prev_progress:
                rank = i + 1  # 只有进度变化才更新排名
            prev_progress = entry['total_progress']

            rank_msg += f"{rank}. {nickname} • 总进度：{entry['total_progress']}%\n"

            # 查找当前用户的排名
            if entry['user_id'] == user_id:
                user_rank = rank

        # 获取用户的排名信息
        if user_rank is None:
            for i, entry in enumerate(sorted_rank):
                if entry['user_id'] == user_id:
                    if entry['total_progress'] != prev_progress:
                        user_rank = i + 1
                    else:
                        user_rank = rank  # 共享相同排名
                    break

        user_progress = next((entry['total_progress'] for entry in sorted_rank if entry['user_id'] == user_id), 0)
        user_nickname = await get_nickname(bot, user_id)
        rank_msg += f"\n🔹 {user_nickname}的排名为：{user_rank}，总进度：{user_progress}%"

    # **猎场进度排名**
    # 开新猎场要改
    elif 0 < arg <= liechang_count:
        title_msg = f'全服{arg}号猎场进度排名'
        rank_msg = f"📜 全服 {arg} 号猎场进度排名 📊\n"
        sorted_rank = sorted(progress_data, key=lambda x: x['progress'], reverse=True)

        top_10 = sorted_rank[:10]
        top_10_nicknames = await asyncio.gather(*[get_nickname(bot, uid) for uid in [entry['user_id'] for entry in top_10]])

        rank = 0
        prev_progress = None
        user_rank = None  # 当前用户的排名

        for i, (entry, nickname) in enumerate(zip(top_10, top_10_nicknames)):
            if entry['progress'] != prev_progress:
                rank = i + 1  # 只有进度变化才更新排名
            prev_progress = entry['progress']

            rank_msg += f"{rank}. {nickname} • {arg}号猎场进度：{entry['progress']}%\n"

            # 查找当前用户的排名
            if entry['user_id'] == user_id:
                user_rank = rank

        # 获取用户的排名信息
        if user_rank is None:
            for i, entry in enumerate(sorted_rank):
                if entry['user_id'] == user_id:
                    if entry['progress'] != prev_progress:
                        user_rank = i + 1
                    else:
                        user_rank = rank  # 共享相同排名
                    break

        user_progress = next((entry['progress'] for entry in sorted_rank if entry['user_id'] == user_id), 0)
        user_nickname = await get_nickname(bot, user_id)
        rank_msg += f"\n🔹 {user_nickname}的排名为：{user_rank}，{arg}号猎场进度：{user_progress}%"

    else:
        await rankingjd.finish("无效的参数！请使用 `.jdrank` 或 `.jdrank <猎场号>`。", at_sender=True)
    forward_messages = [
        {
            "type": "node",
            "data": {
                "name": title_msg,
                "uin": event.self_id,  # 设置为机器人的QQ号
                "content": rank_msg
            }
        }
    ]
    # 转发消息
    if forward_messages:
        await bot.send_group_forward_msg(
            group_id=event.group_id,  # 转发到当前群组
            messages=forward_messages
        )


# 查询全服madeline总进度
total_madelinejd_query = on_command(
    "全服jd", 
    aliases={"查询全服jd","qfjd"}, 
    permission=GROUP, 
    priority=1, 
    block=True,
    rule=whitelist_rule
)
@total_madelinejd_query.handle()
async def handle_total_madelinejd_query(bot: Bot, event: GroupMessageEvent):
    # 初始化计数 # 添加新猎场时更新
    hunt_count = [[0, 0, 0, 0, 0] for _ in range(liechang_count)]  # 各猎场的各级别 madeline 数量
    hunt_max_count = [[0, 0, 0, 0, 0] for _ in range(liechang_count)]  # 各猎场的各级别 madeline 总数
    unique_madelines = [set() for _ in range(liechang_count)]  # 每个猎场独立的 madeline 唯一集

    # 计算每个猎场的最大数量
    for lc, madeline_data in enumerate([madeline_data1, madeline_data2, madeline_data3]):  # 添加新猎场时更新
        for k, v in madeline_data.items():
            hunt_max_count[lc][int(k) - 1] = len(set(v))  # 确保唯一性

    # 读取所有玩家的数据
    try:
        for lc, file_name in enumerate(file_names.values()):
            data = open_data(user_path / file_name)
            for user_id, user_data in data.items():
                for k, v in user_data.items():
                    k_parts = k.split('_')
                    level = int(k_parts[0]) - 1
                    if level < 0 or level >= 5:
                        continue
                    madeline_key = k  # 唯一标识
                    if madeline_key not in unique_madelines[lc]:
                        hunt_count[lc][level] += 1
                        unique_madelines[lc].add(madeline_key)
    except FileNotFoundError:
        await total_madelinejd_query.finish("未找到猎场的数据文件！")
    except json.JSONDecodeError:
        await total_madelinejd_query.finish("猎场数据文件格式错误，无法解析！")

    # 计算总进度
    total_count = [sum(hunt) for hunt in zip(*hunt_count)]
    total_max_count = [sum(hunt) for hunt in zip(*hunt_max_count)]
    total_captured = sum(total_count)
    total_max = sum(total_max_count)
    total_progress = round((total_captured / total_max) * 100, 2) if total_max > 0 else 0.0

    # 构建总进度信息
    progress_message = f"全服madeline总进度：\n\n总进度：{total_progress}%\n"
    for level in range(5, 0, -1):
        progress_message += f"- {level}级madeline：{total_count[level - 1]}/{total_max_count[level - 1]}\n"

    # 构建猎场进度信息
    for lc in range(liechang_count):  # 添加新猎场时更新
        hunt_captured = sum(hunt_count[lc])
        hunt_max = sum(hunt_max_count[lc])
        hunt_progress = round((hunt_captured / hunt_max) * 100, 2) if hunt_max > 0 else 0.0
        progress_message += f"\n{lc + 1}号猎场总进度：{hunt_progress}%\n"
        for level in range(5, 0, -1):
            progress_message += f"- {level}级madeline：{hunt_count[lc][level - 1]}/{hunt_max_count[lc][level - 1]}\n"

    # 构建转发消息
    forward_message = [
        {
            "type": "node",
            "data": {
                "name": "全服进度",
                "uin": str(bot.self_id),
                "content": progress_message.strip(),
            },
        }
    ]

    # 发送转发消息
    await bot.call_api(
        "send_group_forward_msg",
        group_id=event.group_id,
        messages=forward_message,
    )



#展示madeline
show = on_command('show', permission=GROUP, priority=1, block=True, rule=whitelist_rule)

@show.handle()
async def zhanshi(event: Event, arg: Message = CommandArg()):
    name = str(arg).lower()  # 获取输入的名字
    user_id = event.get_user_id()  # 获取用户ID

    # 打开主文件
    data = open_data(user_path / file_name)

    # 查找 madeline
    nums = find_madeline(name)
    if nums == 0:
        await show.finish(f"未找到名为 {name} 的 madeline", at_sender=True)
        return

    # 获取对应猎场文件
    file_path = user_path / f"UserList{nums[2]}.json"
    if not file_path.exists():
        await show.finish("对应的猎场数据文件不存在", at_sender=True)
        return

    # 打开猎场文件
    
    hunt_data = open_data(file_path)

    # 查询用户数据
    if str(user_id) in data:
        user_hunt_data = hunt_data.get(str(user_id), {})
        key = f"{nums[0]}_{nums[1]}"
        if key in user_hunt_data:
            # 根据等级和编号获取坐标
            level = int(nums[0])
            number = int(nums[1])

            madeline = print_zhua(level, number, nums[2])
            level = madeline[0]
            name = madeline[1]
            img = madeline[2]
            description = madeline[3]

            # 发送图片和描述
            await show.finish(f"\n等级：{level}\n{name}\n" + MessageSegment.image(img) + description, at_sender=True)
        else:
            await show.finish(f"你还没抓到过 {name}", at_sender=True)
    else:
        await show.finish("你还没尝试抓过 madeline.....", at_sender=True)

# 查看某 madeline 数量
count_madeline = on_command('count', permission=GROUP, priority=1, block=True, rule=whitelist_rule)

@count_madeline.handle()
async def cha_madeline_number(event: Event, arg: Message = CommandArg()):
    # 获取输入的名字
    name = str(arg).strip().lower()
    if not name:
        await count_madeline.finish("请输入要查询的 madeline 名称", at_sender=True)

    # 查找该名字的 madeline 的图像文件坐标
    nums = find_madeline(name)
    if not nums:
        await count_madeline.finish(f"未找到名为 {name} 的 madeline", at_sender=True)

    # 获取用户 ID
    user_id = str(event.get_user_id())

    # 打开主文件，检查用户是否已注册
    main_data = open_data(user_path / file_name)

    if user_id not in main_data:
        await count_madeline.finish("你还没尝试抓过 madeline.....", at_sender=True)

    # 根据猎场号打开对应文件
    liechang_number = nums[2]
    try:
        arena_data = open_data(user_path / f"UserList{liechang_number}.json")
    except FileNotFoundError:
        await count_madeline.finish(f"猎场 {liechang_number} 的数据文件缺失，请联系管理员。", at_sender=True)

    # 检查用户数据
    user_data = arena_data.get(user_id, {})
    madeline_key = f"{nums[0]}_{nums[1]}"

    # 查找 madeline 数量
    if madeline_key in user_data:
        number = user_data[madeline_key]
        await count_madeline.finish(f"你有 {number} 个 {name}", at_sender=True)
    else:
        await count_madeline.finish(f"你还没抓到过 {name}", at_sender=True)
