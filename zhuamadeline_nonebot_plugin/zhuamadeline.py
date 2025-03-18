from nonebot.adapters.onebot.v11 import MessageSegment, Message
from nonebot.adapters.onebot.v11 import GROUP
from nonebot.adapters.onebot.v11 import Bot, Event, GroupMessageEvent
from nonebot import on_command, on_fullmatch
from nonebot.log import logger
from nonebot.params import CommandArg
from pathlib import Path
#加载文件操作系统
import os
import json
#加载读取系统时间相关
import datetime
import time
#加载数学算法相关
import random
import math
#加载madeline档案信息
from .madelinejd import *
from .config import *
from .list1 import *
from .list2 import *
from .list3 import *
from .list4 import *
#加载抓madeline相关的函数
from .function import *
from .render import *
from .event import event_happen, outofdanger
from .pvp import madeline_pvp_event, pvp_opening, check_liechang
from .whitelist import whitelist_rule

__all__ = [
    "qhlc",
    "catch",
    "qd",
    "ck"
]

bar_path = Path() / "data" / "UserList" / "bar.json"
pvp_path = Path() / "data" / "UserList" / "pvp.json"

# 切换猎场
qhlc = on_command('qhlc', permission=GROUP, priority=1, block=True, rule=whitelist_rule)

@qhlc.handle()
async def qhlc_handle(event: GroupMessageEvent, arg: Message = CommandArg()):
    # 读取用户数据
    data = open_data(user_path / file_name)
    user_id = str(event.user_id)
    args = str(arg).strip().lower() 
    number_arg = str(args)  # 猎场编号
    
    if number_arg == "999":
        number_arg = "随便一个任何东西反正不能是999直接报错提示请输入正确的猎场号"
    if user_id not in data:
        await qhlc.finish("你还没尝试抓过madeline.....", at_sender=True)
        
    try:
        number_int = int(number_arg)
    except:
        await qhlc.finish(f"请输入正确的猎场号！现在只开放了1~{liechang_count}猎哦！", at_sender=True)
        
    number = str(number_int)
    
    # 特殊竞技猎场（0号）
    if number_int == 0:
        if data[user_id]['berry'] < 0:
            await qhlc.finish(f"你现在仍在负债中……不允许进入竞技场！你只有{data[user_id]['berry']}颗草莓！", at_sender=True)

        if data[user_id].get('lc') == number:
            await qhlc.finish("你现在就在这个猎场呀~", at_sender=True)

        data[user_id]['lc'] = number
        save_data(user_path / file_name, data)
        await qhlc.finish("已经成功切换到madeline竞技场！有关madeline竞技场的规则请输入[.0场细则]查看！", at_sender=True)

    # 普通收集型猎场
    elif 0 < number_int <= liechang_count:
        if data[user_id].get('lc') == number:
            await qhlc.finish("你现在就在这个猎场呀~", at_sender=True)

        data[user_id]['lc'] = number
        save_data(user_path / file_name, data)
        await qhlc.finish(f"已经成功切换到{number}号猎场！", at_sender=True)
    # 处理错误输入
    else:
        await qhlc.finish(f"请输入正确的猎场号！现在只开放了1~{liechang_count}猎哦！", at_sender=True)


#随机抓出一个madeline，且有时间间隔限制
catch = on_command("zhua", aliases={"抓",'ZHUA','Zhua'}, permission=GROUP, priority=1, block=True, rule=whitelist_rule)
@catch.handle()
async def zhuamadeline(bot: Bot, event: GroupMessageEvent):
    answer = -1
    #----------读取用户信息并交互----------
    if(os.path.exists(user_path / file_name)):
        data = open_data(user_path / file_name)

        user_id = str(event.user_id)  #qq号
        group_id = str(event.group_id)
        current_time = datetime.datetime.now()  #读取当前系统时间
        if (str(user_id) in data):
            # 添加全局冷却

            all_cool_time(cd_path, user_id, group_id)
            
            # 确保 event 字段存在
            data[user_id].setdefault('event', 'nothing')
            exp = data[user_id].setdefault("exp", 0)
            grade = data[user_id].setdefault("grade", 1)
            max_exp = data[user_id].setdefault("max_exp", 10)
            max_grade = data[user_id].setdefault("max_grade", 25)
            
            #确保collections存在
            collections = data[str(user_id)].get('collections', {})
            items = data[str(user_id)].get('item', {})
                
            #读取信息
            next_time_r = datetime.datetime.strptime(data.get(str(user_id)).get('next_time'), "%Y-%m-%d %H:%M:%S")
            
            #加工果酱时无法抓madeline
            #防止没有status这个键
            if ('status' in data[str(user_id)]):
                status = data[str(user_id)].get('status')
            else:
                status = 'normal'

            if(status =='working'): 
                if(not 'work_end_time' in data[str(user_id)]):
                    data[str(user_id)]['work_end_time'] = current_time.strftime("%Y-%m-%d %H:%M:%S")
                current_time = datetime.datetime.now()
                work_end_time = datetime.datetime.strptime(data.get(str(user_id)).get('work_end_time'), "%Y-%m-%d %H:%M:%S")
                if current_time < work_end_time:
                    text = time_text(str(work_end_time-current_time))
                    await catch.finish(f"你正在维护草莓加工器，还需要{text}！", at_sender=True)
                #时间过了自动恢复正常
                else:
                    data[str(user_id)]['status'] = 'normal'
                    save_data(user_path / file_name, data)
            
            #如果受伤了则无法抓
            if(data[str(user_id)].get("buff")=="hurt"): 
                if(current_time < next_time_r):
                    delta_time = next_time_r - current_time
                    await catch.finish(f"你受伤了，需要等{time_text(delta_time)}后才能抓", at_sender=True)
                    
            #有其他正在进行的事件未完成
            if(data[str(user_id)]['event']!='nothing'):
                await catch.finish("你还有正在进行中的事件", at_sender=True)
                
            #正面buff检测逻辑
            #没有就先加上
            if(not 'buff2' in data[str(user_id)]):
                data[str(user_id)]['buff2'] = 'normal'
            if(not 'lucky_times' in data[str(user_id)]):
                data[str(user_id)]['lucky_times'] = 0
            #幸运
            if data[str(user_id)]["lucky_times"] > 0 and data[str(user_id)]['buff2'] == 'lucky':
                data[str(user_id)]["lucky_times"] -= 1
            else:
                data[str(user_id)]['buff2'] = 'normal'
                data[str(user_id)]["lucky_times"] = 0
            #迷路脱险事件
            await outofdanger(data,str(user_id),catch,current_time,next_time_r)
            
            #debuff清除逻辑
            debuff_clear(data,user_id)
            
            #正常抓的逻辑
            if(current_time < next_time_r):
                delta_time = next_time_r - current_time
                answer = 0
            else:
                next_time = current_time + datetime.timedelta(minutes=30)
                #检测回想之核
                dream = data[str(user_id)]['collections'].get("回想之核", 0)
                if dream >= 1:
                    next_time = current_time + datetime.timedelta(minutes=29)                
                data[str(user_id)]['next_time'] = next_time.strftime("%Y-%m-%d %H:%M:%S")
                answer = 1
        else:
            #注册用户
            data[str(user_id)] = {}
            collections = data[str(user_id)].setdefault('collections', {})
            items = data[str(user_id)].setdefault('item', {})
            next_time = current_time + datetime.timedelta(minutes=30)
            # #检测回想之核
            # dream = collections.get("回想之核", 0)
            # if dream >= 1:
            #     next_time = current_time + datetime.timedelta(minutes=29)
            data[str(user_id)]['next_time'] = next_time.strftime("%Y-%m-%d %H:%M:%S")
            answer = 1
    else:
        ##注册第一个用户
        user_id = event.get_user_id()
        data[str(user_id)] = {}
        collections = data[str(user_id)].setdefault('collections', {})
        items = data[str(user_id)].setdefault('item', {})
        current_time = datetime.datetime.now()
        next_time = current_time + datetime.timedelta(minutes=30)
        # #检测回想之核
        # dream = collections.get("回想之核", 0)
        # if dream >= 1:
        #     next_time = current_time + datetime.timedelta(minutes=29)
        data[str(user_id)]['next_time'] = next_time.strftime("%Y-%m-%d %H:%M:%S")
        answer = 1

    #----------给出回应-----------
    if(answer == 0):
        #幸运
        if data[str(user_id)]["lucky_times"] > 0 and data[str(user_id)]['buff2'] == 'lucky':
            data[str(user_id)]["lucky_times"] += 1
        else:
            data[str(user_id)]['buff2'] = 'normal'
            data[str(user_id)]["lucky_times"] = 0
        text = time_text(str(delta_time))
        await catch.finish(f"别抓啦，{text}后再来吧", at_sender = True)
    elif(answer == 1):
        #第一次抓
        if(not 'lc' in data[str(user_id)]):
            data[str(user_id)]['lc'] = '1'

        #特殊猎场madeline竞技场内事件
        if(data[str(user_id)]['lc']=='0'):
            # if str(user_id) not in bot_owner_id:
                # await message.finish("现在madeline竞技场暂未开放哦，敬请期待！", at_sender=True)
            # 负债检测
            if data[user_id]['berry'] < 0:
                await catch.finish(f"你现在仍在负债中……不允许进入竞技场！你只有{str(data[str(user_id)]['berry'])}颗草莓！", at_sender=True)
            nickname = event.sender.nickname
            # next_time = current_time + datetime.timedelta(minutes=10)
            # #检测回想之核
            # dream = data[str(user_id)]['collections'].get("回想之核", 0)
            # if dream >= 1:
            #     next_time = current_time + datetime.timedelta(minutes=9)
            # data[str(user_id)]['next_time'] = next_time.strftime("%Y-%m-%d %H:%M:%S")
            await madeline_pvp_event(data,str(user_id),nickname,catch,bot)
            #后面的程序不执行
            return

        #触发事件
        await event_happen(data,str(user_id),catch)

        #写入副表
        data2 = open_data(user_path / f"UserList{data[str(user_id)]['lc']}.json")
        # 获取debuff
        debuff = data[str(user_id)].get('debuff', 'normal')
        # 确定抓到哪个madeline
        # 默认概率设置
        star = collections.get("星辰碎屑", 0)
        star_add = 50 if star >= 1 else 0
        probabilities = {'a': 10, 'b': 50, 'c': 200, 'd': 500 + star_add}
        liechang_number = data[str(user_id)]['lc']

        life_leaf = collections.get("生命之叶", 0)
        yinkuang = items.get("音矿", 0)
        red_ball = collections.get("红色球体", 0)
        green_ball = collections.get("绿色球体", 0)
        yellow_ball = collections.get("黄色球体", 0)
        increment = math.floor(0.01 * yinkuang)
        # 计算音矿加成
        increment = math.floor(0.01 * yinkuang)

        # 应用音矿加成
        if yinkuang >= 1:
            probabilities['a'] += increment
            probabilities['b'] += increment
            probabilities['c'] += increment
            probabilities['d'] += increment

        # 应用生命之叶加成（非猎场 3/4）
        if life_leaf >= 1 and liechang_number not in ["3", "4"]:
            factor = 1.5
            probabilities['a'] = math.floor(probabilities['a'] * factor)
            probabilities['b'] = math.floor(probabilities['b'] * factor)
            probabilities['c'] = probabilities['b'] + 150
            probabilities['d'] = probabilities['c'] + 300
                
        # 虚弱debuff全局生效
        if debuff == 'weaken':
            probabilities = {'a': 0, 'b': 0, 'c': 0, 'd': 0}  # 只能抓出1

        # 最终概率结果
        a, b, c, d = probabilities.values()

            
        # if str(user_id) == "121096913":
        #     a, b, c, d = 996, 997, 998, 999
        madeline = zhua_random(a, b, c, d, liechang_number)
        level       = madeline[0]   #等级
        name        = madeline[1]   #名字
        img         = madeline[2]   #图片
        description = madeline[3]   #描述
        num         = madeline[4]   #编号
        
        #奖励草莓
        lucky_give = 0
        sheet_text = ""
        #判定秘宝
        treasure = data[str(user_id)]['collections'].get('尘封的秘宝',0)

        #判定乐谱
        sheet_music = data[str(user_id)]['collections'].get('星光乐谱',0)

        if (debuff=='poisoned'):
            berry_give = 0
        else:
            # 用字典映射不同 level 的 berry_give 值
            berry_give_map = {1: 10, 2: 20, 3: 30, 4: 40, 5: 50}
            berry_give = berry_give_map.get(level, 0)  # 默认为 0，避免 level 不在范围内时报错
            
            # 4猎裸抓加成 +10，宝藏加成 +5
            if data[str(user_id)]['lc'] == '4':
                berry_give += 10

            if treasure >= 1:
                berry_give += 5
            
            # sheet_music 触发双倍奖励
            if sheet_music >= 1 and random.randint(1, 10) <= 2:
                if berry_give > 0:
                    berry_give *= 2
                    sheet_text = "\n\n在悠扬的乐曲声中，草莓似乎被唤醒了，焕发出勃勃生机，迅速分裂出更多的果实！"

        # 新人送1000草莓
        if(not 'berry' in data[str(user_id)]):
            data[str(user_id)]['berry'] = 1000
        
        if data[str(user_id)]["lucky_times"] > 0 and berry_give > 0:
            lucky_give = 15

        data[str(user_id)]['berry'] += berry_give + lucky_give
        #将抓到的结果加入库存
        new_print = ""
        lc = data[str(user_id)]['lc']
        countList = data2_count(user_id, level, num, lc)
        data2 = countList[0]
        new_print = countList[1]
        
        #写入madeline收集表(副统计表)
        save_data(user_path / f"UserList{data[str(user_id)]['lc']}.json", data2)

        #写入主数据表
        save_data(user_path / file_name, data)
        #发送消息
        if(debuff!='poisoned'):
            lucky_num = data[str(user_id)].get('lucky_times') - 1
            text = str(lucky_num)
            if (lucky_num == -1):
                data[str(user_id)]['buff2'] = 'normal'
                data[str(user_id)]['lucky_times'] = 0
            if (data[str(user_id)].get('buff2')=='lucky'):
                await catch.finish(new_print+
                            f'\n等级: {level}\n'+
                            f'{name}'+
                            MessageSegment.image(img)+
                            f'{description}'+
                            f"{sheet_text}" +
                            '\n\n本次奖励'+f'{berry_give}+{lucky_give}={berry_give+lucky_give}颗草莓\n'+
                            f'幸运加成剩余{text}次'+
                            exp_msg + grade_msg,
                            at_sender = True)
            else:
                await catch.finish(new_print+
                                f'\n等级: {level}\n'+
                                f'{name}'+
                                MessageSegment.image(img)+
                                f'{description}'+
                                f"{sheet_text}" +
                                '\n\n本次奖励'+f'{berry_give}颗草莓' +
                                exp_msg + grade_msg,
                                at_sender = True)
        else:
            await catch.finish(new_print+
                            f'\n等级: {level}\n'+
                            f'{name}'+
                            MessageSegment.image(img)+
                            f'{description}' +
                            exp_msg + grade_msg,
                            at_sender = True)

## 每日签到
qd = on_fullmatch(['.签到', '.qd', '。签到', '。qd'], permission=GROUP, priority=1, block=True, rule=whitelist_rule)

@qd.handle()
async def dailyqd(event: GroupMessageEvent):
    # 读取数据
    data = open_data(user_path / file_name) if os.path.exists(user_path / file_name) else {}

    user_id = str(event.user_id)
    nickname = event.sender.nickname

    if user_id not in data:
        await qd.finish("你还没尝试抓过madeline.....", at_sender=True)

    user_data = data.setdefault(user_id, {"berry": 0, "jrrp": 0, "item": {}, "date": "2000-01-01"})
    collections = user_data.setdefault('collections', {})
    # 获取日期信息
    current_date_str = datetime.date.today().strftime("%Y-%m-%d")
    
    if user_data.get("date", "2000-01-01") == current_date_str:
        await qd.finish("一天只能签到一次吧......", at_sender=True)

    # 计算随机奖励
    base_berry = random.randint(1, 100)
    extra_berry = user_data["item"].get("招财猫", 0) * 3
    double_berry = collections.get("鱼之契约", 0)
    total_berry = (base_berry + extra_berry) * (double_berry + 1)
    
    # 更新用户数据
    user_data["berry"] += total_berry
    user_data["jrrp"] = base_berry
    user_data["date"] = current_date_str
    save_data(user_path / file_name, data)

    # 获取签到图片、文案
    picture_str, text, luck_text = draw_qd(nickname, base_berry, extra_berry, double_berry)
    picture = Path(picture_str)

    # 发送签到信息
    await qd.finish(MessageSegment.image(picture), at_sender=True)


# jrrp（必须签到后才能使用，用来查看今天发了多少草莓以及文案）
jrrp = on_command("jrrp", permission=GROUP, priority=1, block=True, rule=whitelist_rule)

@jrrp.handle()
async def dailyjrrp(event: GroupMessageEvent):
    data = open_data(full_path)
    user_id = str(event.get_user_id())
    nickname = event.sender.nickname

    # 检查用户是否注册
    if user_id not in data:
        await jrrp.finish("你还没抓过madeline，无法进行今日人品的查询哦！", at_sender=True)

    user_data = data.setdefault(user_id, {"jrrp": 0, "date": ""})
    collections = user_data.setdefault('collections', {})

    # 获取日期信息
    current_date_str = datetime.date.today().strftime("%Y-%m-%d")

    # 判断是否已经签到
    if user_data["date"] != current_date_str:
        await jrrp.finish("请先签到后再查询jrrp哦！", at_sender=True)

    # 获取 jrrp 数值
    jrrp_int = user_data.get("jrrp", 0)
    if jrrp_int == 0:
        await jrrp.finish("啊哦，出错了，今日人品似乎没能成功查询到呢！(可能是因为签到后没有成功保存 jrrp 的数值？)", at_sender=True)
    extra_berry = user_data["item"].get("招财猫", 0) * 3
    
    # 检测是否翻倍
    double = collections.get("鱼之契约", 0)
    double_jrrp = (jrrp_int + extra_berry) * (double+ 1)

    # 获取图片、文案
    picture_str, text, luck_text = draw_qd(nickname, jrrp_int, extra_berry, double)
    
    reply_text = f"\n你今日的人品（签到）值为：{jrrp_int}\n{luck_text}"
    reply_text += f"\n检测到你拥有鱼之契约，你今日签到获得的草莓翻倍，为{double_jrrp}！（包含了招财猫加成哦）" if double == 1 else ''
    # 发送信息
    await jrrp.finish(f"\n你今日的人品（签到）值为：{jrrp_int}\n{luck_text}", at_sender=True)


# 查看状态
ck = on_command('ck', permission=GROUP, priority=1, block=True, rule=whitelist_rule)

@ck.handle()
async def cha_berry(event: Event, arg: Message = CommandArg()):
    data = open_data(user_path / file_name)
    pvp_data = open_data(pvp_path)
    bar_info = open_data(bar_path)
    user_id = str(event.get_user_id())

    if user_id not in data:
        await ck.finish("你还没尝试抓过Madeline.....", at_sender=True)
        return
    
    all_judge = str(arg).strip().lower()
    
    current_time = datetime.datetime.now()
    user_data = data[user_id]
    bar_data = bar_info.get(user_id,{})

    # 初始化必要字段，避免 KeyError
    work_end_time_r = user_data.get('work_end_time', current_time.strftime("%Y-%m-%d %H:%M:%S"))
    next_recover_time_r = user_data.get('next_recover_time', current_time.strftime("%Y-%m-%d %H:%M:%S"))
    next_fishing_time_r = user_data.get('next_fishing_time', current_time.strftime("%Y-%m-%d %H:%M:%S"))
    next_clock_time_r = user_data.get('next_clock_time', current_time.strftime("%Y-%m-%d %H:%M:%S"))
    collections = user_data.get('collections', {})
    pvp_guess = bar_data.get('pvp_guess', {})
    double_ball = bar_data.get('double_ball', {})
    

    # 获取主数据
    berry = user_data.get('berry', 0)
    liechang_number = user_data.get('lc', '1')
    energy = user_data.get("energy", 0)
    last_pvp_guess_berry = bar_data.get("last_pvp_guess_berry", 0)
    identity_status = user_data.get("identity_status", 0)
    elect_status = user_data.get("elect_status", False)
    kongjun = user_data.get("kongjun", 0)
    fishing = user_data.get("fishing", 0)
    lucky_times = get_user_data(data, user_id, "lucky_times", 0)
    compulsion_count = get_user_data(data, user_id, "compulsion_count", 0)
    get_ball_value = get_user_data(data, user_id, "get_ball_value", 0)
    
    # 获取酒店数据
    bank = bar_data.get("bank", 0)
    interest = bar_data.get("interest", 0)
    interest_today = bar_data.get("interest_today", 0)
    ifguess = pvp_guess.get("ifguess", 0)
    pos = pvp_guess.get("pos", -1)
    choose_rank = pvp_guess.get("choose_rank", -1)
    choose_turn = pvp_guess.get("choose_turn", -1)
    choose_nickname = pvp_guess.get("choose_nickname", "暂无数据")
    pots = bar_info.setdefault("pots", 0)
    ball_prize = double_ball.get("prize", 0)
    refund = double_ball.get("refund", 0)
    ball_ifplay = double_ball.get("ifplay", 0)
    ticket_cost = double_ball.get("ticket_cost", 0)
    user_red = double_ball.get("red_points")
    user_blue = double_ball.get("blue_points")
    bar_data = open_data(bar_path)
    history = bar_data.get("double_ball_history", [])

    # 获取时间数据
    next_recover_time = datetime.datetime.strptime(next_recover_time_r, "%Y-%m-%d %H:%M:%S")
    next_clock_time = datetime.datetime.strptime(next_clock_time_r, "%Y-%m-%d %H:%M:%S")
    work_end_time = datetime.datetime.strptime(work_end_time_r, "%Y-%m-%d %H:%M:%S")
    next_fishing_time = datetime.datetime.strptime(next_fishing_time_r, "%Y-%m-%d %H:%M:%S")
    next_time = max(get_time_from_data(user_data), work_end_time)
    
    # 获取pvp数据
    turn = pvp_data.get('count', 100)  # 获取当前轮数
    
    # 清除过期 debuff
    debuff_clear(data, user_id)

    # 获取状态
    debuff = get_user_data(data, user_id, 'debuff')
    status = get_user_data(data, user_id, 'status')
    buff = get_user_data(data, user_id, 'buff')
    buff2 = get_user_data(data, user_id, 'buff2')
    event = get_user_data(data, user_id, 'event', 'nothing')

    # 状态映射
    # 负债
    liability_message = "负债"
    # 事件
    status_messages = {
        "trading": "交易进行中", "compulsion_ggl": "强制刮刮乐", "compulsion_bet1": "强制预言大师", "working": "维护加工器中", "getspider": "神秘事件1", "getbomb": "神秘事件2"
    }
    # debuff
    debuff_messages = {
        "illusory": "缺氧", "poisoned": "中毒", "unlucky": "不幸", "weaken": "虚弱", "notjam": "通缉", "forbidguess": "生气的小小卒", "clumsy": "笨拙"
    }
    # buff
    buff_messages = {"hurt": "受伤", "lost": "迷路"}
    # 幸运
    buff2_messages = {"lucky": "幸运"}

    # 生成状态信息
    status_list = list(filter(None, [
        liability_message if berry < 0 else "",
        status_messages.get(event, ""), 
        status_messages.get(status, ""), 
        buff_messages.get(buff, ""),
        buff2_messages.get(buff2, "") if lucky_times > 1 else "",
        debuff_messages.get(debuff, "")
    ]))
    msg_status = "，".join(status_list) if status_list else ''
    # 显示猎场名称
    # 开新猎场要改
    liechang_names = {
        '0': 'Madeline竞技场',
        '1': '一号猎场 - 古代遗迹',
        '2': '二号猎场 - 异域茂林',
        '3': '三号猎场 - 翡翠矿井',
        '4': '四号猎场 - 地下终端',
        '5': '五号猎场 - 遗忘深渊',
    }
    liechang_name = liechang_names.get(liechang_number, "未知猎场")
    # 生成消息
    message = (
        f"\n- 所处猎场：{liechang_name}"
        f"\n- 当前持有草莓：{berry}颗"
        )
    
    # 显示草莓银行草莓（若有）
    message += (f"\n- 银行草莓余额：{bank}颗") if bank > 0 else ''

    if all_judge == "all":
        # 显示当日增加的利息（若有）
        message += (f"\n• 今日草莓银行利息：{interest_today}颗") if interest_today > 0 else ''
    
        # 显示总增加的利息（若有）
        message += (f"\n• 草莓银行总利息：{interest}颗") if interest > 0 else ''
    
        # 显示当前奖池积累（若有）
        message += (f"\n• 当前奖池积累草莓：{pots}颗") if pots > 0 else ''
        
        # 显示上次竞猜获得的草莓（若有）
        message += (f"\n• 上次bet3获得草莓：{last_pvp_guess_berry}颗") if last_pvp_guess_berry > 0 else ''

        if ball_ifplay == 0:
            # 优先显示中奖信息，然后显示门票信息
            if ball_prize > 0:
                message += f"\n• 上次双球中奖草莓：{ball_prize}颗"
            
            elif refund > 0:
                message += f"\n• 上次双球中奖草莓：{refund}颗"

    # 显示能量（若有）
    message += (f"\n- 剩余能量：{energy}点") if energy > 0 else ''
    
    #添加状态（若有）
    message += (f"\n- 状态：{msg_status}") if msg_status else ''
    
    # 显示钓鱼次数（若有）
    message += (f"\n- 钓鱼次数：{fishing} | 空军次数：{kongjun}") if fishing > 0 else ''

    # 显示4猎当前目标（要在4猎才显示）
    if liechang_number == "4":
        if collections.get('红色球体', 0) == 0:
            message += f"\n- 当前目标：红色球体\n- 已积累次数：{get_ball_value}/10"
        elif collections.get('绿色球体', 0) == 0:
            message += f"\n- 当前目标：绿色球体\n- 已积累次数：{get_ball_value}/7"
        elif collections.get('黄色球体', 0) == 0:
            message += f"\n- 当前目标：黄色球体\n- 已积累次数：{get_ball_value}/4"
        else:
            message += f"\n- 当前目标：无，地下终端已完全开放"
            
    if all_judge == 'all':
        # 处理“身份徽章”和“充能箱”状态
        if collections.get('身份徽章', 0) > 0:
            # 根据 identity_status 显示对应的状态文本
            if identity_status == 0:
                message += "\n• “身份”状态：欲速则不达（停用）"
            elif identity_status == 1:
                message += "\n• “身份”状态：2ed（身份模式）"
            elif identity_status == 2:
                message += "\n• “身份”状态：膀胱（急速模式）"

        message += f"\n• 充能箱状态：{'撞开（启用）' if elect_status else '关闭（停用）'}" if collections.get('充能箱', 0) > 0 else ''
    
    # 显示下次抓取的时间（若有）
    message += (f"\n- 下次可抓取时间：\n{next_time}") if current_time < next_time else ''

    if all_judge == 'all':   

        # 显示事件（若有）
        message += (f"\n• 事件 {status_messages.get(event, '')} 的剩余次数：{compulsion_count}次") if event in ['compulsion_ggl', 'compulsion_bet1'] else ''

        # 显示幸运次数（若有）
        message += (f"\n• 剩余幸运次数：{lucky_times - 1}次") if lucky_times > 1 else ''

        # 显示下次钓鱼的时间（若有）
        message += (f"\n• 下次可钓鱼时间：\n{next_fishing_time}") if current_time < next_fishing_time else ''

        # 判断是否进入时间秒表冷却（若有）
        message += (f"\n• 时间秒表冷却结束时间：\n{next_clock_time}") if current_time < next_clock_time else ''

        # 显示debuff时间（若有）
        message += (f"\n• debuff {debuff_messages.get(debuff, '')} 的持续时间至：\n{next_recover_time}") if debuff != 'normal' else ''

        if ball_ifplay == 1:
            # 显示双色球以及本场门票
            message += (f"\n• 本场入场费：{ticket_cost}颗草莓")
        
        message += (f"\n• 本次双球猜测号码：红 {user_red} | 蓝 {user_blue}")

        if history and ball_ifplay == 0:
            latest_draw = history[-1]  # 取列表最后一个元素
            latest_red = latest_draw["red"]
            latest_blue = latest_draw["blue"]
            latest_date = latest_draw["date"]
            message += (f"\n• {latest_date}开奖号码：红 {latest_red} | 蓝 {latest_blue}")
        
        # 显示竞猜（若有）
        if ifguess == 1:
            if pos != -1:
                jisuan_turn = turn
                jisuan_choose_turn = choose_turn
                if choose_turn <= 10:
                    jisuan_choose_turn = 10
                if len(pvp_data['list']) < 10:
                    jisuan_turn = 10
                # 计算目前为止的收益
                berry_reward = int((120 - choose_rank) * (jisuan_turn - jisuan_choose_turn) * (1 / 6))
                tax = int(berry_reward * 0.1) # 计算草莓税
                final_berry_reward = berry_reward - tax  # 计算税后收益

                message += (
                    f"\n· 本次Madeline竞技场竞猜你所选的擂台为[{pos+1}]，"
                    f"该擂台擂主为[{choose_nickname}]，上台回合为[{choose_turn}]，"
                    f"所选占擂Madeline的战力为[{choose_rank}]！\n"
                    f"截至目前第[{turn}]轮的草莓收益为：[{berry_reward}]颗草莓，"
                    f"草莓税为[{tax}]颗草莓，税后草莓收益为[{final_berry_reward}]颗草莓！"
                )
            else:
                message += f"\n• 本次Madeline竞技场竞猜已结算"

    await ck.finish(message, at_sender=True)



# 转账 - 1000以下150手续费，1000上15%
#转移草莓
user_transfer_berry = on_command("transfer", permission=GROUP, priority=1, block=True, rule=whitelist_rule)

@user_transfer_berry.handle()
async def transfer_handle(event: GroupMessageEvent, arg: Message = CommandArg()):
    # 解析命令参数
    arg = str(arg).split(" ")
    if len(arg) != 2:
        await user_transfer_berry.finish("命令格式错误！正确格式：.transfer QQ号 数量", at_sender=True)
    user_a = str(event.user_id)
    user_b = arg[0]  # 转入方QQ号
    try:
        transfer_amount = int(arg[1])
    except ValueError:
        await user_transfer_berry.finish("转移数量必须为数字！", at_sender=True)
    if transfer_amount <= 0:
        await user_transfer_berry.finish("转移数量必须大于0！", at_sender=True)
    # 打开文件
    data = open_data(user_path / file_name)
    bar_data = open_data(bar_path)
    # 检查玩家是否存在
    if user_a not in data:
        await user_transfer_berry.finish(f"找不到 [{user_a}] 的信息", at_sender=True)
    if user_b not in data:
        await user_transfer_berry.finish(f"找不到 [{user_b}] 的信息", at_sender=True)
    if user_a == user_b:
        await user_transfer_berry.finish(f"你为什么想给自己转账，想送给我手续费吗？", at_sender=True)    
    tax = 100
    if transfer_amount <= 1000:
        tax = 100
    else:
        tax = math.floor(transfer_amount * 0.1)
    final_berry = transfer_amount + tax
    owner_berry = data[user_a]['berry']
    # 检查转出方草莓数量是否足够
    if data[user_a]['berry'] < final_berry:
        await user_transfer_berry.finish(f"你的草莓不足，你目前想转移{transfer_amount}颗草莓，草莓税为{tax}，总共为{final_berry}颗草莓，你目前只有{owner_berry}颗草莓！", at_sender=True)
    # 执行转移操作
    data[user_a]['berry'] -= final_berry
    data[user_b]['berry'] += transfer_amount
    # 税加入pots奖池里
    pots = bar_data.setdefault("pots", 0)
    bar_data["pots"] += tax
    # 写入文件
    save_data(bar_path, bar_data)
    save_data(user_path / file_name, data)
    await user_transfer_berry.finish(f"已成功将{transfer_amount}颗草莓从" +MessageSegment.at(user_a)+ "转移给" +MessageSegment.at(user_b)+f"！\n本次扣税{tax}颗草莓，已经从转出者的草莓内扣除！")
