from nonebot.adapters.onebot.v11 import MessageSegment, Message
from nonebot.adapters.onebot.v11 import GROUP, Bot, Event
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.log import logger
from nonebot import on_command, on_fullmatch
from nonebot.params import CommandArg
#加载文件操作系统
import json
#加载读取系统时间相关
import datetime
#加载数学算法相关
import random
import time
#加载madeline档案信息
from .madelinejd import *
from .config import *
from .list1 import *
from .list2 import *
from .list3 import *
from .list4 import *
#加载商店信息和商店交互
from .shop import item, ban_item, item_aliases
from .collection import collection_aliases, collections
from .secret import secret_list
from .function import *
from .event import *
from .pvp import *
from .whitelist import whitelist_rule

__all__ = [
    "pray",
    "daoju",
    'myitem',
    "ckdj"
]

user_path = Path("data") / "UserList"  # 指定路径
file_name = "UserData.json"  # 文件名
full_path = user_path / file_name  # 拼接完整路径
#一些路径
pvp_path = Path() / "data" / "UserList" / "pvp.json"
user_list1 = Path() / "data" / "UserList" / "UserList1.json"
user_list2 = Path() / "data" / "UserList" / "UserList2.json"
user_list3 = Path() / "data" / "UserList" / "UserList3.json"
user_list4 = Path() / "data" / "UserList" / "UserList4.json"
pvp_coldtime_path = Path() / "data" / "UserList" / "pvp_coldtime.json"
# 石山，这么做试试
all_collections = collections

# 查看道具库存
myitem = on_fullmatch(['.myitem', '。myitem'], permission=GROUP, priority=1, block=True, rule=whitelist_rule)

@myitem.handle()
async def myitem_handle(bot: Bot, event: GroupMessageEvent):
    # 打开文件
    data = open_data(user_path / file_name)
    user_id = event.get_user_id()
    # 读取道具个数并转发消息
    if str(user_id) in data:
        # 检查是否有道具
        if 'item' not in data[str(user_id)] or not data[str(user_id)]['item']:
            await myitem.finish("你还没有任何道具哦！", at_sender=True)

        # 有道具则读取道具名字和其对应数量
        nickname = event.sender.nickname
        item_list = [
            (k, v) for k, v in data[str(user_id)]['item'].items() if v > 0
        ]

        # 按数量降序排序
        item_list.sort(key=lambda x: x[1], reverse=True)

        # 拼接文本
        if not item_list:
            await myitem.finish("你没有任何有效道具哦！", at_sender=True)  # 如果没有有效道具，提示用户

        text = f"这是 [{nickname}] 的道具列表\n"
        for k, v in item_list:
            text += f"\n- {k} x {v}"

        # 转发消息
        msg_list = [
            {
                "type": "node",
                "data": {
                    "name": "道具库存室",
                    "uin": event.self_id,
                    "content": text
                }
            }
        ]
        await bot.call_api("send_group_forward_msg", group_id=event.group_id, messages=msg_list)
    else:
        await myitem.finish("你还没尝试抓过madeline......", at_sender=True)

#祈愿功能，用于消耗能量以换取madeline，必须持有madeline充能器
pray = on_command('祈愿', aliases={"pray"}, permission=GROUP, priority=1, block=True, rule=whitelist_rule)
@pray.handle()
async def pray_handle(event: GroupMessageEvent, arg: Message = CommandArg()):
    data = open_data(full_path)
    user_id = str(event.get_user_id())
    group_id = str(event.group_id)
    # 添加全局冷却
    all_cool_time(cd_path, user_id, group_id)
    # 负债检测
    if data[user_id]['berry'] < 0:
        await pray.finish(f"你现在仍在负债中……无法进行祈愿！你只有{str(data[str(user_id)]['berry'])}颗草莓！", at_sender=True)
    liechang_number = data[str(user_id)].get('lc')
    energy = data[str(user_id)].get("energy")
    # # 处理命令参数，如果用户输入“能量”则查询能量
    # if arg.extract_plain_text().strip() in ["能量","energy"]:
    #     # 查询当前能量
    #     await pray.finish(f"你当前充能器里存储的能量为{energy}！", at_sender=True)
    #读取用户信息

    if (not 'buff' in data[str(user_id)]):
        data[str(user_id)].get('buff')=='normal'
    #一些啥都干不了的buff
    if data[str(user_id)].get('event',"nothing") != "nothing":
        await pray.finish("你还有正在进行中的事件", at_sender=True)
    if(data[str(user_id)].get('buff')=='lost'): 
        await pray.finish(f"你现在正在迷路中，连路都找不到，怎么祈愿呢？", at_sender=True)
    if(data[str(user_id)].get('buff')=='confuse'): 
        await pray.finish(f"你现在正在找到了个碎片，疑惑着呢，不能祈愿。", at_sender=True)
    #如果受伤了则无法祈愿
    if(data[str(user_id)].get("buff")=="hurt"): 
        #一些额外操作：如果还没过下次时间，计算与下次的时间间隔，如果过了，可以使用道具
        current_time = datetime.datetime.now()
        next_time_r = datetime.datetime.strptime(data.get(str(user_id)).get('next_time'), "%Y-%m-%d %H:%M:%S")
        if(current_time < next_time_r):
            delta_time = next_time_r - current_time
            await pray.finish(f"你受伤了，需要等{time_text(delta_time)}才能继续", at_sender=True)
        else:
            outofdanger(data,str(user_id),pray,current_time,next_time_r)

    #是否在加工状态

    #防止没有status这个键
    if ('status' in data[str(user_id)]):
        status = data[str(user_id)].get('status')
    else:
        status = 'normal'

    if(status =='working'): 
        current_time = datetime.datetime.now()
        #如果没有就写入，虽说这段代码完全不可能发生
        if(not 'work_end_time' in data[str(user_id)]):
            data[str(user_id)]['work_end_time'] = current_time.strftime("%Y-%m-%d %H:%M:%S")

        work_end_time = datetime.datetime.strptime(data.get(str(user_id)).get('work_end_time'), "%Y-%m-%d %H:%M:%S")
        if current_time < work_end_time:
            text = time_text(str(work_end_time-current_time))
            await pray.finish(f"你正在维护草莓加工器，还需要{text}！", at_sender=True)
        #时间过了自动恢复正常
        else:
            data[str(user_id)]['status'] = 'normal'
            save_data(user_path / file_name, data)
    
    if liechang_number == "0":
        await pray.finish("madeline竞技场不能祈愿哦，请切换到其他猎场再试试")      
    #打开文件
    data = open_data(user_path / file_name)

    user_id = event.get_user_id()

    #先检测有没有道具列表
    #判断是否开辟道具栏
    if(not 'item' in data[str(user_id)]):
        data[str(user_id)]['item'] = {}
    #检查是否有充能器
    if(data[str(user_id)].get("item").get('madeline充能器', 0) > 0):
        current_time = datetime.datetime.now()
        try:
            energy = int(energy)
        except:
            energy = 0
        try:
            next_time = datetime.datetime.strptime(data.get(str(user_id)).get('next_time'), "%Y-%m-%d %H:%M:%S")
        except:
            next_time = current_time
        #检查祈愿cd是否已到
        if current_time >= next_time:
            #查看能量有没有600
            if energy >= 600:
                # 4猎必须要有黄球才能祈愿
                if liechang_number == "4":
                    # 确保藏品栏存在
                    data[str(user_id)].setdefault('collections', {})
                    if(not '黄色球体' in data[str(user_id)]['collections']):
                        await pray.finish("地下终端的力量仍然强大……你未能满足条件，现在无法在地下终端内祈愿……", at_sender = True)
                #未解锁三猎场抓不了
                elif liechang_number=='3':
                    if data[str(user_id)].get("item").get('神秘碎片', 0) < 5:
                        await pray.finish("你还未解锁通往第三猎场的道路...", at_sender=True)
                    try:
                        helmat = data[str(user_id)]['collections']['矿工头盔']
                    except:
                        helmat = 0
                    rnd_hurt = 10
                    rnd_stuck = random.randint(1,100)
                    if helmat>=1:
                        rnd_hurt -=5
                    if(rnd_stuck<=rnd_hurt):
                        stuck_path = Path() / "data" / "UserList" / "Struct.json"
                        #打开被困名单
                        stuck_data = open_data(stuck_path)
                        #受伤1.5小时，在此期间什么都干不了
                        current_time = datetime.datetime.now()
                        next_time = current_time + datetime.timedelta(minutes=90)
                        #检测回想之核
                        try:
                            dream = data[str(user_id)]['collections'].get("回想之核", 0)
                        except:
                            dream = 0
                        if dream >= 1:
                            next_time = current_time + datetime.timedelta(minutes=89)
                        data[str(user_id)]['next_time'] = next_time.strftime("%Y-%m-%d %H:%M:%S")
                        data[str(user_id)]['buff'] = 'hurt'
                        #加入山洞被困名单
                        stuck_data[user_id] = '3'
                        #写入主数据表
                        save_data(user_path / file_name, data)
                        #写入山洞被困名单
                        save_data(stuck_path, stuck_data)

                        #随机事件文本
                        text = "你在闭眼祈愿的过程中，没有任何madeline响应你，结果一不小心你就撞到了山洞上！不过幸好祈愿失败不消耗能量……"
                        #发送消息
                        await pray.finish(text+"你需要原地等待90分钟，或者使用急救包自救，又或者等待他人来救你……", at_sender=True)
                # 2猎祈愿 50% 概率迷路
                elif liechang_number == "2":
                    stuck_path = Path() / "data" / "UserList" / "Struct.json"
                    #打开森林被困名单
                    stuck_data = open_data(stuck_path)
                    #迷路
                    lost = 1
                    #是否拥有指南针道具
                    if('item' in data[str(user_id)]):
                        if(data[str(user_id)]['item'].get('指南针',0) > 0):
                            lost = 0
                    #迷路事件
                    if(lost==1):
                        rnd = random.randint(1,10)
                        if(rnd >= 5):
                            #困在森林里八小时，在此期间什么都干不了
                            current_time = datetime.datetime.now()
                            next_time = current_time + datetime.timedelta(minutes=480)
                            data[str(user_id)]['next_time'] = next_time.strftime("%Y-%m-%d %H:%M:%S")
                            data[str(user_id)]['buff'] = 'lost'
                            #加入森林被困名单
                            stuck_data[user_id] = '2'
                            #写入主数据表
                            save_data(user_path / file_name, data)
                            #写入森林被困名单
                            save_data(stuck_path, stuck_data)   
                            #发送消息
                            await pray.finish("你在祈愿的时候，不小心在森林里迷路了，不知道何时才能走出去.....(请在你觉得可能找到路的时候使用zhuamadeline指令)", at_sender=True)
                #强行修复受伤bug
                data[str(user_id)]["buff"] = "normal"
                information = zhua_random(120, 360, 900, 999, liechang_number=liechang_number)
                data[str(user_id)]["energy"] -= 600
                #把冷却cd加上
                next_time_r = current_time + datetime.timedelta(minutes=30)
                # 添加全局冷却
                now_time = time.time()
                data[str(user_id)]["coldtime"] = now_time
                #检测回想之核
                try:
                    dream = data[str(user_id)]['collections'].get("回想之核", 0)
                except:
                    dream = 0
                if dream >= 1:
                    next_time_r = current_time + datetime.timedelta(minutes=29)
                    
                data[str(user_id)]['next_time'] = next_time_r.strftime("%Y-%m-%d %H:%M:%S")
                #检测奇想魔盒
                magicBox = data[str(user_id)]['collections'].get("奇想魔盒", 0)
                #检测奇想扑克
                puke = data[str(user_id)]['collections'].get("奇想扑克", 0)       
                
                information = tool_zhuamadeline(information, data, user_id)
                #得到madeline信息
                level       = information[0]   #等级
                name        = information[1]   #名字
                img         = information[2]   #图片
                description = information[3]   #描述
                num         = information[4]   #编号
                lc          = information[5]   #所属猎场
                new_print   = information[6]   #是否出新
                
                #如果是奇想魔盒相关道具则进行判定
                berry_give = 0
                magic_text = ''
                try:
                    if magicBox>=1:
                        berry_rnd=random.randint(1,100)
                        if berry_rnd<=10:
                            berry_give += 5 * int(level)
                            data[str(user_id)]['berry'] += berry_give
                            magic_text = '\n\n奇想魔盒震动了一下。'
                #否则无事发生
                except:
                    pass
                #奇想扑克判定
                puke_text = ''
                try:
                    if puke>=1:
                        puke_rnd=random.randint(1,100)
                        if puke_rnd<=10:
                            berry_give += 5 * int(level)
                            data[str(user_id)]['berry'] += berry_give
                            puke_text = '\n\n奇想扑克抽动了一下。'
                #否则无事发生
                except:
                    pass
                #判定乐谱
                sheet_text = ""
                try:
                    sheet_music = data[str(user_id)]['collections'].get('星光乐谱',0)
                except:
                    sheet_music = 0
                    
                if sheet_music >=1:   
                    sheet_rnd = random.randint(1,10)
                    if sheet_rnd <= 2:
                        # 没有草莓不触发
                        if berry_give > 0:
                            sheet_text = "\n\n在悠扬的乐曲声中，草莓似乎被唤醒了，焕发出勃勃生机，迅速分裂出更多的果实！"
                            berry_give *= 2
                berry_text = ""
                if berry_give != 0:
                    berry_text = '\n\n本次你获得了'+str(berry_give)+'颗草莓'
                
                save_data(full_path, data)
 
                #发送消息
                await pray.finish(new_print+
                                 f'\n等级: {level}\n'+
                                f'{name}'+
                                MessageSegment.image(img)+
                                f'{description}'+
                                f'{magic_text}'+
                                f'{puke_text}'+
                                f"{sheet_text}"+
                                f'{berry_text}',
                                at_sender = True)
            else:
                text = str(energy)
                await pray.finish(f"你的能量只有{text}，不足600，无法祈愿...", at_sender=True)
        else:
            text = time_text(str(next_time-current_time))
            await daoju.finish(f"请{text}后再来祈愿吧~", at_sender=True)
    else:
        await pray.finish("你还没有madeline充能器，无法祈愿...")

#使用道具，整个抓madeline里最繁琐的函数，且会持续更新
daoju = on_command('use', permission=GROUP, priority=1, block=True, rule=whitelist_rule)
@daoju.handle()
async def daoju_handle(event: GroupMessageEvent, bot: Bot, arg: Message = CommandArg()):
    user_path = Path() / "data" / "UserList"
    file_name = "UserData.json"
    full_path = user_path / file_name
    item_text = ""
    #打开文件
    data = open_data(full_path)
    user_id = str(event.get_user_id())
    panding_debuff = 0 # 为以后方便扩展，0无事发生，其他数值无法使用某些特定道具
    # 负债检测
    if data[user_id]['berry'] < 0:
        await daoju.finish(f"你现在仍在负债中……无法使用道具！你只有{str(data[str(user_id)]['berry'])}颗草莓！", at_sender=True)
    # 事件检测
    if data[str(user_id)].get('event',"nothing") != "nothing":
        await daoju.finish("你还有正在进行中的事件", at_sender=True)
    # 笨拙检测
    if data[str(user_id)].get('debuff',"normal") == "clumsy":
        panding_debuff = 1
    pan_current_time = datetime.datetime.now()  #读取当前系统时间
    pan_next_time_r = datetime.datetime.strptime(data.get(str(user_id)).get('next_time'), "%Y-%m-%d %H:%M:%S")
    if(str(user_id) in data):
        group_id = str(event.group_id)
        # 添加全局冷却
        all_cool_time(cd_path, user_id, group_id)
        # 检测是否有藏品栏
        data[str(user_id)].setdefault('collections', {})
        if("item" in data[str(user_id)]):
            # 处理道具名称
            use_item_name = str(arg).strip().lower()  # 获取输入道具名

            # 判断是否包含 "/"
            if "/" in use_item_name:
                command_parts = use_item_name.split("/")  # 分割字符串
                item_base_name = command_parts[0]  # 取第一个部分

                # 查找别名映射
                standard_item = get_alias_name(item_base_name, item, item_aliases)
                standard_collection = get_alias_name(item_base_name, all_collections, collection_aliases)

                # 选择最终的标准名称
                if standard_item:
                    use_item_name = "/".join([standard_item] + command_parts[1:])  # 组合回完整命令
                elif standard_collection:
                    use_item_name = "/".join([standard_collection] + command_parts[1:])  # 组合回完整命令
            else:
                # 直接查找别名
                standard_item = get_alias_name(use_item_name, item, item_aliases)
                standard_collection = get_alias_name(use_item_name, all_collections, collection_aliases)

                # 选择最终的标准名称
                if standard_item:
                    use_item_name = standard_item  # 匹配到道具
                elif standard_collection:
                    use_item_name = standard_collection  # 匹配到藏品
                    
            success = 0  #0代表没有效果，1代表成功，2代表失败
            # 检查道具名称是否在商品列表中，防止使用空气掉坑
            usepanding = use_item_name.split("/")
            panding_item = usepanding[0]
            if use_item_name not in item or panding_item not in item or use_item_name in ban_item:
                success = 999
            if(data[str(user_id)].get("item").get(use_item_name, 0) <= 0):
                success = 999
            if(data[str(user_id)].get("item").get(panding_item, 0) <= 0):
                success = 999
            if use_item_name == '时间献祭器' and pan_current_time < pan_next_time_r:
                success = 999
            fail_text = "失败！"   #失败文本
        #--------------------这些道具不限制所在猎场的使用--------------------
            # 身份徽章作为例外不受影响
            if use_item_name.startswith("身份徽章"):
                if not "/" in use_item_name:
                    await daoju.finish("命令格式不正确，请使用 .use 身份徽章/0 或 .use 身份徽章/1 或 .use 身份徽章/2", at_sender=True)
                if data.get(user_id).get('collections').get('身份徽章', 0) > 0:
                    # 从命令中提取状态值（如 0, 1, 2）
                    usepanding = use_item_name.split("/")  # 提取“/”后面的状态值
                    try:
                        command_status = int(usepanding[1])
                    except:
                        await daoju.finish("无效的状态值，请使用 0（停用），1（身份模式），或 2（急速模式）。", at_sender=True)
                        
                    # 检查状态值是否合法
                    if command_status not in [0, 1, 2]:
                        await daoju.finish("无效的状态值，请使用 0（停用），1（身份模式），或 2（急速模式）。", at_sender=True)
                        return

                    # 获取当前状态，如果没有则默认初始化为 0（停用）
                    if 'identity_status' not in data[str(user_id)]:
                        data[str(user_id)]['identity_status'] = 0  # 默认是“欲速则不达”状态（停用）

                    current_status = data[str(user_id)]['identity_status']

                    # 如果目标状态是 2（急速模式），需要满足条件
                    if command_status == 2:
                        if data[str(user_id)].get('pangguang', 0) != 1:
                            await daoju.finish("你需要先满足“膀胱”条件，才能切换到急速模式。", at_sender=True)
                            return
                    # 确定状态描述
                    if command_status == 0:
                        status_text = "“欲速则不达”状态（停用）"
                    elif command_status == 1:
                        status_text = "“2ed”状态（身份模式）"
                    else:  # command_status == 2
                        status_text = "“膀胱”状态（急速模式）"
                    # 如果当前状态和目标状态不同，则切换
                    if current_status != command_status:
                        # 更新状态
                        data[str(user_id)]['identity_status'] = command_status
                        save_data(full_path, data)
                        await daoju.finish(f"你已经成功切换至{status_text}。", at_sender=True)
                    else:
                        await daoju.finish(f"你已经处于{status_text}，无需切换哦。", at_sender=True)
                else:
                    await daoju.finish(f"你没有足够的“Identity”，无法切换状态。", at_sender=True)
                    
            if use_item_name == "万能解药":
                user_data = data.get(str(user_id), {})
                user_items = user_data.get("item", {})
                user_debuff = user_data.get("debuff", "normal")

                antidote_count = user_items.get(use_item_name, 0)

                if antidote_count <= 0:
                    await daoju.finish(f"你现在没有{use_item_name}，无法解除debuff！", at_sender=True)

                if user_debuff == "normal":
                    await daoju.finish(f"你现在没有debuff，无需解除！", at_sender=True)
                    
                # 定义不同 debuff 需要的解药数量
                debuff_cost = {
                    "forbidguess": 2,  # forbidguess需要2瓶
                    "notjam": 2,  # notjam需要2瓶
                    "weaken": 2,  # weaken需要2瓶
                    "clumsy": 2,  # clumsy需要2瓶
                    "default": 1        # 默认1瓶
                }

                required_amount = debuff_cost.get(user_debuff, debuff_cost["default"])

                if antidote_count < required_amount:
                    await daoju.finish(f"你的{use_item_name}数量不足，无法解除，需要至少{required_amount}瓶{use_item_name}才能解除这个debuff，你目前只有{antidote_count}瓶！", at_sender=True)

                # 解除 debuff
                if user_debuff == "forbidguess":
                    text_rec = f"*forbid_guess_recover {user_id}"
                    await bot.send_group_msg(group_id=1020661785, message=text_rec)

                data[str(user_id)]["debuff"] = "normal"
                data[str(user_id)]["item"][use_item_name] -= required_amount

                # 记录下次恢复时间
                data[str(user_id)]["next_recover_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # 保存数据
                save_data(user_path / file_name, data)

                # 反馈信息
                remaining = data[str(user_id)]["item"][use_item_name]
                await daoju.finish(f"debuff已解除，这个debuff需要消耗{required_amount}瓶{use_item_name}，你现在还剩{remaining}瓶{use_item_name}", at_sender=True)

            # 笨拙判定
            if panding_debuff == 1:
                await daoju.finish("这股能量仍然在你的身体里游荡，你现在无法使用除万能解药以外的绝大部分道具/藏品……", at_sender=True)

            if use_item_name == "草莓鱼竿":
                # 初始化
                user_data = data.get(str(user_id), {})
                user_item = user_data.setdefault("item", {})
                user_collections = user_data.setdefault("collections", {})

                if user_item.get("草莓鱼竿", 0) < 1:
                    await daoju.finish("你现在没有草莓鱼竿哦，无法钓鱼！", at_sender=True)

                # 获取以及初始化时间
                current_time = datetime.datetime.now()
                next_time_r = datetime.datetime.strptime(user_data.get("next_time", "1900-01-01 00:00:00"), "%Y-%m-%d %H:%M:%S")
                next_fishing_time = datetime.datetime.strptime(user_data.get("next_fishing_time", "1900-01-01 00:00:00"), "%Y-%m-%d %H:%M:%S")

                # 初始化钓鱼次数和空军次数
                kongjun = user_data.setdefault("kongjun", 0)
                fishing = user_data.setdefault("fishing", 0)

                if next_fishing_time > current_time:
                    fishing_text = time_text(str(next_fishing_time - current_time))
                    await daoju.finish(f"你刚刚才钓过鱼，水里的鱼都跑光啦！还需要{fishing_text}鱼才会游回来！", at_sender=True)

                # 扣除 10 草莓作为饵料
                erliao = 10
                if user_data.get("berry", 0) < erliao:
                    await daoju.finish(f"你身上的草莓不足以作为饵料来钓鱼哦！你现在只有{user_data.get('berry', 0)}颗草莓！", at_sender=True)

                # 增加钓鱼次数
                fishing += 1
                user_data["berry"] -= erliao

                # 记录冷却时间
                next_fishing_time_r = current_time + datetime.timedelta(hours=11)
                user_data["fishing"] = fishing
                user_data["next_fishing_time"] = next_fishing_time_r.strftime("%Y-%m-%d %H:%M:%S")

                message = f"你使用了{erliao}颗草莓作为饵料，"

                # 判断是否空军（30% 概率）
                gailv = random.randint(1,10)
                # if random.random() < 0.3:  # 30% 概率空军
                if gailv < 3:
                    kongjun += 1
                    user_data["kongjun"] = kongjun
                    
                    # 空军随机事件文本
                    kongjun_text = [
                        "但是你空军了，什么也没钓到……\n",
                        "钓上来一块电池！是哪位玛德琳这么没有公德心把电池抛接到海里去了？你遗憾的把电池丢回海里去了！\n",
                        "钓上来一只小猫！为啥海里会有猫？很遗憾，这只猫被钓上来后直接跑了！\n",
                        "钓上来一个岩浆块！海里有岩浆块很合理吧，但是由于过于烫手你把它丢了！\n",
                        "钓上来一只小飞机！但是这只小飞机花溜溜的飞走了！\n",
                        '钓上来一个UFO！外星人举着『禁止非法垂钓』的牌子抗议，你尴尬地把飞碟塞回海里！\n',
                        '钓上来Desom的狐狸尾巴毛！这搓毛突然BOOM了，转眼间就404 NOT FOUND了！\n',
                        '钓上来kevin房彩蛋房间！但里面塞满500个金草莓，焦虑值爆表的你直接剪断了鱼线！\n',
                        '钓上来官方速通计时器！眼看要破纪录时，鱼钩被判定为『非法捷径』强制重置！\n',
                        '钓上来像素平台！你试图攀爬时触发滑落机制，结果把整个钓鱼平台砸塌了！\n',
                        '钓上来自拍手机！你突然摆出胜利姿势，鱼群趁机集体大逃亡！\n',
                        '钓上来次元裂缝！另一个世界的钓鱼佬从里面钓走了你，你俩在空中交换了懵逼眼神！\n',
                        '钓上来美人鱼！但她开口就是男高音，吓得你主动要求被消除记忆！\n',
                        '钓上来WIFI路由器！显示『信号强度-10086』，你愤怒地把它砸成电子珊瑚！\n',
                        '钓上来一颗长有翅膀的金草莓！它突然开始发光闪烁，你本能地按C键冲刺——结果草莓飞走了！\n',
                        '钓上来一个弹球！结果弹球叮叮叮把你弹到水里去了！\n',
                        '钓上来一只蓝鸟！结果蓝鸟“嘎”的一声就飞走了，顺便教了你凌波微步！\n',
                    ]
                    
                    message += random.choice(kongjun_text)

                    # 第 10 次空军时给予 "鱼之契约" 藏品（如果还没有）
                    if kongjun >= 10 and "鱼之契约" not in user_collections:
                        user_collections["鱼之契约"] = 1
                        message += "\n为了感谢你空军了这么多次放过了不少鱼，所以鱼群拟定了一个契约送给你！\n输入.cp 鱼之契约 以查看具体效果"
                else:
                    # 70% 钓到鱼，使用权重随机选择鱼
                    fish_probabilities = {
                        "海星": 0.50,
                        "水母": 0.20,
                        "胖头鱼": 0.15,
                        "胖头鱼罐头": 0.09,
                        "水晶胖头鱼": 0.045,
                        "星鱼": 0.014,
                        "阿拉胖头鱼": 0.001,
                    }

                    fish = random.choices(list(fish_probabilities.keys()), weights=fish_probabilities.values(), k=1)[0]

                    # 将钓到的鱼加入 user_item
                    user_item[fish] = user_item.get(fish, 0) + 1
                    message += f"成功钓上来一条{fish}！\n"

                # 统一保存数据
                save_data(user_path / file_name, data)
                # 发送消息
                await daoju.finish(message.strip(), at_sender=True)

            if(use_item_name=="充能箱"):
                if(data.get(user_id).get('collections').get('充能箱',0) > 0):
                    #身份命令检测逻辑
                    #没有就先加上
                    if(not 'elect_status' in data[str(user_id)]):
                        data[str(user_id)]['elect_status'] = False
                        
                    current_status = data[str(user_id)]['elect_status']
                    new_status = not current_status
                    status_text = "撞开（启用）" if new_status else "关闭（停用）"
                    
                    data[str(user_id)]['elect_status'] = new_status
                    save_data(full_path,data)
                    await daoju.finish(f"你已经成功切换至{status_text}状态。", at_sender=True)
                else:
                    await daoju.finish(f"你的藏品中没有充能箱，无法切换状态。", at_sender=True)

            if(use_item_name=="时间秒表"):
                if(data.get(user_id).get('item').get('时间秒表',0) > 0):
                    current_time = datetime.datetime.now()
                    next_time_r = datetime.datetime.strptime(data.get(str(user_id)).get('next_time'), "%Y-%m-%d %H:%M:%S")
                    try:
                        work_end_time_r = datetime.datetime.strptime(data.get(str(user_id)).get('work_end_time'), "%Y-%m-%d %H:%M:%S")
                    except:
                        work_end_time_r = current_time
                    
                    #防止没有status这个键
                    if ('status' in data[str(user_id)]):
                        status = data[str(user_id)].get('status')
                    else:
                        status = 'normal'
                        
                    # 果酱加工不能用秒表
                    if(status =='working'): 
                        current_time = datetime.datetime.now()
                        #如果没有就写入，虽说这段代码完全不可能发生
                        if(not 'work_end_time' in data[str(user_id)]):
                            data[str(user_id)]['work_end_time'] = current_time.strftime("%Y-%m-%d %H:%M:%S")

                        work_end_time = datetime.datetime.strptime(data.get(str(user_id)).get('work_end_time'), "%Y-%m-%d %H:%M:%S")
                        if current_time < work_end_time:
                            text = time_text(str(work_end_time-current_time))
                            await pray.finish(f"你正在维护草莓加工器，还需要{text}！维护加工器的过程不能使用秒表哦！", at_sender=True)
                        #时间过了自动恢复正常
                        else:
                            data[str(user_id)]['status'] = 'normal'
                    #首先判断有没有冷却
                    if(current_time < next_time_r or current_time < work_end_time_r):
                        next_time = get_time_from_data(data[str(user_id)])
                        # 判定回想之核
                        dream = data[str(user_id)].get('collections',{}).get("回想之核", 0)
                        try:
                            next_clock_time = datetime.datetime.strptime(data.get(str(user_id)).get('next_clock_time'), "%Y-%m-%d %H:%M:%S")
                        except:
                            next_clock_time = current_time
                        #然后判断是否能使用秒表
                        if current_time >= next_clock_time:
                            data[str(user_id)]["item"][use_item_name] -= 1 
                            #清除全部冷却时长
                            next_time_r = current_time + datetime.timedelta(seconds=1)
                            next_clock_time_r = current_time + datetime.timedelta(minutes=30-dream)
                            data[str(user_id)]['next_time'] = next_time_r.strftime("%Y-%m-%d %H:%M:%S")
                            data[str(user_id)]['next_charge_time'] = next_time_r.strftime("%Y-%m-%d %H:%M:%S")
                            data[str(user_id)]['work_end_time'] = next_time_r.strftime("%Y-%m-%d %H:%M:%S")
                            data[str(user_id)]['next_clock_time'] = next_clock_time_r.strftime("%Y-%m-%d %H:%M:%S")
                            # 以下为移除名单
                            # 清除普通buff
                            data[user_id]["buff"] = "normal"
                            if data[str(user_id)]["item"].get(use_item_name) <= 0:
                                del data[str(user_id)]["item"][use_item_name]
                            # 由于是自救，需要从被困名单中移除
                            stuck_path = Path() / "data" / "UserList" / "Struct.json"
                            # 打开森林被困名单
                            stuck_data = open_data(stuck_path)
                            # 从被困名单里移除
                            if user_id in stuck_data:
                                del stuck_data[user_id]
                                # 更新森林被困名单
                                save_data(stuck_path, stuck_data)
                            #写入文件
                            save_data(user_path / file_name, data)
                            await daoju.finish("使用成功，冷却被全部清除了！", at_sender=True)
                        else:
                            text = time_text(str(next_clock_time-current_time))
                            await daoju.finish(f"不久前使用的时间秒表似乎使你所有的秒表都停止运转了。请{text}后再尝试使用", at_sender=True)
                    else:
                        await daoju.finish("你现在没有冷却呀，无需使用此道具", at_sender=True)
                else:
                    await daoju.finish(f"你现在没有{use_item_name}", at_sender=True)
            
            if use_item_name.startswith("道具盲盒"):
                # 用户输入命令映射：默认单抽
                COMMAND_MAP = {
                    "道具盲盒": "单抽",
                    "道具盲盒单抽": "单抽",
                    "道具盲盒五连抽": "五连抽",
                    "道具盲盒五连": "五连抽",
                    "道具盲盒十连抽": "十连抽",
                    "道具盲盒十连": "十连抽",
                    "道具盲盒模拟一万连": "模拟一万连",
                }
                item_name = use_item_name.replace(" ", "")
                user_choice = COMMAND_MAP.get(item_name)
                if not user_choice:
                    await daoju.finish("道具盲盒只能单抽、五连或十连哦，具体指令如下: .use 道具盲盒(单抽/五连/十连)，默认为单抽。", at_sender=True)

                # 奖品及其权重
                PRIZES = [
                    ("急救包", 9.99),
                    ("弹弓", 19.5),
                    ("万能解药+急救包礼包组合", 15),
                    ("一次性小手枪", 15.5),
                    ("充能陷阱", 10),
                    ("胡萝卜", 19.51),
                    ("madeline提取器", 3.5),
                    ("时间秒表", 3),
                    ("幸运药水", 3),
                    ("madeline提取器+时间秒表礼包组合", 0.5),
                    ("鲜血之刃", 0.25),
                    ("尘封的秘宝", 0.25),
                ]
                # 礼包组合拆分映射（库存更新时拆分成单个道具）
                COMBO_MAP = {
                    "急救包+复仇之刃礼包组合": ("急救包", "复仇之刃"),
                    "万能解药+急救包礼包组合": ("万能解药", "急救包"),
                    "madeline提取器+时间秒表礼包组合": ("madeline提取器", "时间秒表"),
                }

                def draw_prize():
                    """随机抽奖，返回奖品字符串"""
                    prizes = [p for p, _ in PRIZES]
                    weights = [w for _, w in PRIZES]
                    return random.choices(prizes, weights=weights, k=1)[0]

                def add_to_inventory(user_data, item, count=1):
                    """将单个道具加入库存"""
                    user_data.setdefault("item", {})
                    user_data["item"][item] = user_data["item"].get(item, 0) + count

                def get_special_message(prize, is_duplicate=False):
                    """返回指定奖品的特殊文案"""
                    if is_duplicate and prize in ["鲜血之刃", "尘封的秘宝"]:
                        return (
                            "你打开了道具盲盒，误打误撞间触发了一股神秘的力量，眼前的场景骤然变换。"
                            "你仿佛置身于一处幽暗的溶洞，四周一片寂静，隐约传来低沉的嗡鸣声。\n"
                            "洞内一片寂静，昏暗中一张桌子上散落着几件道具：草莓果酱×5、时间秒表×1、madeline提取器×1"
                        )
                    messages = {
                        "madeline提取器": "我去，是madeline提取器，这下可以好好爆madeline了！",
                        "时间秒表": "居然是时间秒表，这下不用怕爆炸了！",
                        "幸运药水": "原来道具盲盒里还能爆出幸运药水的吗？",
                        "madeline提取器+时间秒表礼包组合": "恭喜！你获得了稀有组合：madeline提取器+时间秒表！这下赚翻了啊。",
                        "鲜血之刃": (
                            "你打开了道具盲盒，误打误撞间触发了一股神秘的力量，眼前的场景骤然变换。"
                            "你仿佛置身于一处幽暗的溶洞，四周一片寂静，隐约传来低沉的嗡鸣声。\n"
                            "微光中，一柄通体漆黑、血迹斑驳的长刀静静伫立在裂纹密布的石台上，"
                            "当你靠近它时，刀身突然散发出猩红的光芒，整个洞穴随之震颤，尖锐的嗡鸣声中似乎蕴含着无尽的愤怒与渴望！"
                        ),
                        "尘封的秘宝": (
                            "你打开了道具盲盒，误打误撞间触发了一股神秘的力量，眼前的场景骤然变换。"
                            "你仿佛置身于一处幽暗的溶洞，四周一片寂静，隐约传来低沉的嗡鸣声。\n"
                            "在溶洞的一处昏暗角落，你意外发现了一件布满灰尘的秘宝。它静静地躺在那里，尘封已久，散发着神秘的气息，但你一时无法找出打开它的方法。"
                        ),
                    }
                    return messages.get(prize)

                def process_prize(prize, user_data):
                    """
                    处理单次抽奖：
                      - 若为礼包组合，则更新库存时拆分成单品，但显示文案仍为礼包组合
                      - 对于鲜血之刃和尘封的秘宝，首次加入库存，重复则奖励超级大礼包
                      - 普通奖品直接加入库存
                    返回 (显示文案, 对应特殊文案)
                    """
                    special_msg = None
                    if "礼包组合" in prize:
                        if prize in COMBO_MAP:
                            for sub_item in COMBO_MAP[prize]:
                                add_to_inventory(user_data, sub_item)
                        else:
                            for sub_item in prize.split("+"):
                                add_to_inventory(user_data, sub_item)
                        special_msg = get_special_message(prize)
                        return prize, special_msg

                    if prize in ["鲜血之刃", "尘封的秘宝"]:
                        user_data.setdefault("collections", {})
                        if prize in user_data["collections"]:
                            # 重复获得：奖励超级大礼包（拆分库存更新）
                            add_to_inventory(user_data, "madeline提取器", 1)
                            add_to_inventory(user_data, "时间秒表", 1)
                            add_to_inventory(user_data, "草莓果酱", 5)
                            special_msg = get_special_message(prize, is_duplicate=True)
                            return "超级大礼包（madeline提取器 x1 + 时间秒表 x1 + 草莓果酱 x5）", special_msg
                        else:
                            user_data["collections"][prize] = 1
                            special_msg = get_special_message(prize)
                            return prize, special_msg

                    # 普通奖品直接加入库存
                    add_to_inventory(user_data, prize)
                    special_msg = get_special_message(prize)
                    return prize, special_msg

                # 模拟一万连抽（仅限机器人主人权限）
                if user_choice == "模拟一万连":
                    if str(event.user_id) not in bot_owner_id:
                        await daoju.finish("你没有权限执行模拟一万连！", at_sender=True)
                    sim_results = [draw_prize() for _ in range(10000)]
                    sim_summary = {}
                    for p in sim_results:
                        sim_summary[p] = sim_summary.get(p, 0) + 1
                    sim_msg = "模拟一万连抽奖结果：\n" + "\n".join(f"{k} x{v}" for k, v in sim_summary.items())
                    await daoju.finish(sim_msg, at_sender=True)

                # 合并单抽、五连、十连：确定抽奖次数
                draw_count = 1 if user_choice == "单抽" else (5 if user_choice == "五连抽" else 10)
                if data[str(user_id)]["item"].get("道具盲盒", 0) < draw_count:
                    await daoju.finish(f"你的道具盲盒不足{draw_count}个，无法进行{user_choice}！", at_sender=True)

                # 执行抽奖，统计显示文案、数量及特殊文案
                result_summary = {}  # 格式：{显示文案: {"count": 数量, "msg": 特殊文案}}
                for _ in range(draw_count):
                    prize = draw_prize()
                    display_text, special_msg = process_prize(prize, data[str(user_id)])
                    if display_text not in result_summary:
                        result_summary[display_text] = {"count": 0, "msg": special_msg}
                    result_summary[display_text]["count"] += 1

                data[str(user_id)]["item"]["道具盲盒"] -= draw_count
                save_data(full_path, data)
                
                # 根据抽奖次数确定输出头部文案
                output_lines = []
                if draw_count == 1:
                    output_lines.append("\n你打开了道具盲盒，获得了：")
                else:
                    output_lines.append(f"\n你连续打开了{draw_count}个道具盲盒，结果如下:")
                for blindbox_item, info in result_summary.items():
                    output_lines.append(f"· {blindbox_item} x {info['count']}")
                    if info["msg"]:
                        output_lines.append(info["msg"])
                output_msg = "\n".join(output_lines)
                await daoju.finish(output_msg, at_sender=True)


            if use_item_name.startswith("急救包"): 
                success = 999
                command = use_item_name.split("/")
                item_name = command[0]
                auto_mode = len(command) == 2 and command[1] == "auto"
                auto_reply = False
                used_count = 0  # 记录消耗的急救包数量

                while data.get(user_id, {}).get('item', {}).get('急救包', 0) > 0:
                    auto_reply = True
                    current_time = datetime.datetime.now()
                    next_time_r = datetime.datetime.strptime(
                        data.get(str(user_id), {}).get('next_time', "2099-12-31 23:59:59"),
                        "%Y-%m-%d %H:%M:%S"
                    )
                    hurt_time = (next_time_r - current_time).total_seconds()

                    if data.get(user_id, {}).get("buff", "normal") != "hurt":
                        await daoju.finish("你现在并没有受伤哦！", at_sender=True)
                        return

                    # 计算成功率
                    current_rate = random.randint(1, 100)
                    success_rate_map = {
                        3600: 50,
                        5400: 33,
                        7200: 25,
                        10800: 15,
                        14400: 10
                    }
                    success_rate = next((rate for time, rate in success_rate_map.items() if hurt_time <= time), 3)

                    # 消耗一个急救包
                    data[user_id]["item"]["急救包"] -= 1
                    used_count += 1  # 记录消耗数量

                    if data[user_id]["item"]["急救包"] <= 0:
                        del data[user_id]["item"]["急救包"]

                    # 判定是否成功
                    if current_rate <= success_rate:
                        data[user_id]['next_time'] = (current_time + datetime.timedelta(seconds=1)).strftime("%Y-%m-%d %H:%M:%S")
                        data[user_id]["buff"] = "normal"

                        # 移除被困名单
                        stuck_path = Path() / "data" / "UserList" / "Struct.json"

                        # 读取被困数据
                        try:
                            stuck_data = open_data(stuck_path)
                        except (FileNotFoundError, json.JSONDecodeError):
                            stuck_data = {}


                        # 从列表中删除
                        if str(user_id) in stuck_data:
                            del stuck_data[str(user_id)]
                            save_data(stuck_path, stuck_data)

                        # 保存用户数据
                        user_path = Path() / "data" / "UserList"
                        file_name = "UserData.json"
                        save_data(user_path / file_name, data)

                        remaining_kits = data[user_id]["item"].get("急救包", 0)
                        await daoju.finish(
                            f"恭喜你自救成功，你的伤势得到了治疗！\n你消耗了{used_count}个急救包，还剩{remaining_kits}个。",
                            at_sender=True
                        )
                        return

                    # 如果失败且不是自动模式，直接返回
                    if not auto_mode:
                        break
                    
                # 统一保存用户数据（循环结束后）
                user_path = Path() / "data" / "UserList"
                file_name = "UserData.json"
                save_data(user_path / file_name, data)

                # 根据模式返回结果
                remaining_kits = data[user_id]["item"].get("急救包", 0)
                if auto_mode and auto_reply:
                    await daoju.finish(
                        f"你的急救包已经用完，但仍然没有自救成功...\n"
                        f"你一共消耗了{used_count}个急救包，还剩{remaining_kits}个。",
                        at_sender=True
                    )
                elif not auto_mode:
                    await daoju.finish(
                        f"似乎是自救失败了，也许你可以再试一次，亦或继续等待救援。你还剩{remaining_kits}个急救包。",
                        at_sender=True
                    )
                else:
                    await daoju.finish(f"你现在没有{item_name}", at_sender=True)

            
            if ('status' in data[str(user_id)]):
                status = data[str(user_id)].get('status')
            else:
                status = 'normal'
            #一些啥都干不了的buff
            if(data[str(user_id)].get('buff')=='lost'): 
                await daoju.finish(f"你现在正在迷路中，连路都找不到，怎么使用这个道具呢？", at_sender=True)
            if(data[str(user_id)].get('buff')=='confuse'): 
                await daoju.finish(f"你现在正在找到了个碎片，疑惑着呢，不能使用这个道具。", at_sender=True)

            #草莓果酱的使用判定，要写在加工物品的判定之前
            #两个参数的指令(判定于是否加工之前)
            cmd_sell = use_item_name.split("/")
            use_name = cmd_sell[0]   #参数1
            if(use_name.lower()=="草莓果酱"):
                #可以不输入售卖数量
                try:
                    num_of_sell = cmd_sell[1]   #参数2
                except:
                    num_of_sell = 1

                #判定是否是整数
                try:
                    num_of_sell = int(num_of_sell)
                except:
                    await daoju.finish("请输入一个正确的整数", at_sender=True)
                
                #判定是否是非正数
                if (num_of_sell <= 0):
                    await daoju.finish(f"你为什么会想售卖{str(num_of_sell)}瓶果酱呢？别想卡bug了！", at_sender=True)
                    
                if(data[str(user_id)].get("item").get(use_name, 0) >= num_of_sell):
                    price_total=0
                    berry_bonus = 0
                    berry_bonus_all = 0
                    #判断是否开辟藏品栏
                    player_data = data[user_id]
                    player_data.setdefault('collections', {})
                    collections = player_data['collections']
                    if collections.get('脉冲雷达', 0) > 0:
                        berry_bonus = 10
                    for _ in range(num_of_sell):
                        berry = random.randint(230,265)
                        berry_bonus_all += berry_bonus
                        price_total += berry + berry_bonus
                    data[user_id]['berry'] += price_total
                    data[str(user_id)]["item"][use_name] -= num_of_sell
                    if(data[str(user_id)]["item"].get(use_name)<=0): del data[str(user_id)]["item"][use_name]
                    #写入文件
                    save_data(user_path / file_name, data)
                    if berry_bonus_all != 0:
                        await daoju.finish(f"恭喜！{str(num_of_sell)}瓶草莓果酱卖出了{str(price_total)-str(berry_bonus_all)}+{str(berry_bonus_all)}={str(price_total)}草莓！", at_sender=True)
                    else:
                        await daoju.finish(f"恭喜！{str(num_of_sell)}瓶草莓果酱卖出了{str(price_total)}草莓！", at_sender=True)
                else:
                    await daoju.finish(f"你现在没有这么多{use_name}", at_sender=True)
                
            #加工果酱时无法使用道具
            if(status =='working'): 
                current_time = datetime.datetime.now()
                work_end_time = datetime.datetime.strptime(data.get(str(user_id)).get('work_end_time'), "%Y-%m-%d %H:%M:%S")
                if current_time < work_end_time:
                    text = time_text(str(work_end_time-current_time))
                    await daoju.finish(f"你正在维护草莓加工器，还需要{text}！", at_sender=True)
                #时间过了自动恢复正常
                else:
                    data[str(user_id)]['status'] = 'normal'
                    save_data(user_path / file_name, data)
            #如果受伤了则无法使用道具(时间秒表除外)
            if(data[str(user_id)].get("buff")=="hurt"): 
                #一些额外操作：如果还没过下次时间，计算与下次的时间间隔，如果过了，可以使用道具
                current_time = datetime.datetime.now()
                next_time_r = datetime.datetime.strptime(data.get(str(user_id)).get('next_time'), "%Y-%m-%d %H:%M:%S")
                if(current_time < next_time_r):
                    delta_time = next_time_r - current_time
                    await daoju.finish(f"你受伤了，需要等{time_text(delta_time)}才能继续", at_sender=True)
                else:
                    outofdanger(data,str(user_id),daoju,current_time,next_time_r)
            #两个参数的指令
            command = use_item_name.split("/")
            if(len(command)==2):
                item_name = command[0]   #参数1
                arg2 = command[1]   #参数2
                    
                if(item_name=="草莓加工器"):
                    success = 999
                    if(data[str(user_id)].get("item").get(item_name, 0) > 0):

                        """
                        草莓加工器：使用后进入4h道具加工期，期间不能抓madeline，不能用道具(但是立刻给果酱)
                        """

                        #首先判定有没有开辟这一栏
                        if (not '草莓果酱' in data[str(user_id)].get("item")):
                            data[str(user_id)]["item"]['草莓果酱'] = 0
                        if (not 'buff' in data[str(user_id)]):
                            data[str(user_id)].get('buff')=='normal'
                        #一些啥都干不了的buff
                        if(data[str(user_id)].get('buff')=='lost'): 
                            await daoju.finish(f"你现在正在迷路中，连路都找不到，怎么加工果酱呢？", at_sender=True)
                        if(data[str(user_id)].get('buff')=='confuse'): 
                            await daoju.finish(f"你现在正在找到了个碎片，疑惑着呢，不能加工果酱。", at_sender=True)
                        #如果受伤了则无法使用道具(时间秒表除外)
                        if(data[str(user_id)].get("buff")=="hurt"): 
                            #一些额外操作：如果还没过下次时间，计算与下次的时间间隔，如果过了，可以使用道具
                            current_time = datetime.datetime.now()
                            next_time_r = datetime.datetime.strptime(data.get(str(user_id)).get('next_time'), "%Y-%m-%d %H:%M:%S")
                            if(current_time < next_time_r):
                                delta_time = next_time_r - current_time
                                await daoju.finish(f"你受伤了，需要等{time_text(delta_time)}才能继续", at_sender=True)
                            else:
                                outofdanger(data,str(user_id),daoju,current_time,next_time_r)

                        #首先判定是不是整数
                        try:
                            num = int(arg2)
                        except:
                            await daoju.finish(f"请输入正确的想要加工果酱的瓶数（1-12）哦！", at_sender=True)
                        #其次判定是不是1-4之间的
                        if num<1 or num>12:
                            await daoju.finish(f"请输入正确的想要加工果酱的瓶数（1-12）哦！", at_sender=True)

                        #依然是不可能的代码，但我还是写上了
                        if(not 'berry' in data[str(user_id)]):
                            data[str(user_id)]['berry'] = 1000
                        spend = 150
                        #检测草莓数量是否足够
                        if (data[str(user_id)].get('berry', 0) >= spend * num):
                            data[str(user_id)]['berry'] -= spend * num
                        else:
                            berry_in_need = str(spend * num)
                            berry_you_have = str(data[str(user_id)].get('berry', 0))
                            await daoju.finish(f"你的草莓不足，总共需要{berry_in_need}草莓来制作果酱，你只有{berry_you_have}草莓", at_sender=True)

                        current_time = datetime.datetime.now()
                        if(not 'work_end_time' in data[str(user_id)]):
                            data[str(user_id)]['work_end_time'] = current_time.strftime("%Y-%m-%d %H:%M:%S")
                        data[str(user_id)]["item"]['草莓果酱'] += num    #直接给果酱
                        work_end_time = current_time + datetime.timedelta(minutes=120*num)
                        data[str(user_id)]['work_end_time'] = time_decode(work_end_time)
                        data[str(user_id)]['status'] = 'working'    
                        #写入文件
                        save_data(user_path / file_name, data)
                        text_time = 120*num // 60
                        await daoju.finish(f"你将{spend}x{num}={spend*num}颗草莓放入草莓加工器中，加工出了{num}瓶草莓果酱，但是你需要维护加工器{text_time}小时！", at_sender=True)
                    else:
                        await daoju.finish(f"你现在没有{item_name}", at_sender=True)

            if(use_item_name=="赌徒之眼"):
                """
                在进du局前使用这个道具可以查看该局是否有人想狙你的某个madeline
                """
                await daoju.finish(f"du局都封了，你用这个干什么？", at_sender=True)
                # #没有这个道具
                # if(data[str(user_id)].get("item").get(use_item_name, 0) == 0):
                #     await daoju.finish(f"你现在没有{use_item_name}")
                # #先查看当前为哪个赌场
                # data_du = open_data(duchang_list)
                # group = event.group_id
                # if(not str(group) in data_du):
                #     await daoju.finish("当前还没有du局哦~~~", at_sender=True)
                # liechang_number = data_du[str(group)]['lc']
                # #是否已经在du局中
                # if(str(user_id) in data_du[str(group)]['member']):
                #     await daoju.finish("你脑子是不是坏掉了，这个道具不应该在进du场前用吗？", at_sender=True)
                # data[str(user_id)]["item"][use_item_name] -= 1
                # #写入文件
                # save_data(user_path / file_name, data)
                # if(liechang_number=='1'):
                #     for k in data_du[str(group)]['want']:
                #         if(k in data[str(user_id)]):
                #             await daoju.finish(f"你的{k}面临被掠夺的风险.....", at_sender=True)
                #     await daoju.finish("当前du局非常安全，你可以放心进入", at_sender=True)
                # else:
                #     data2 = open_data(user_path / f"UserList{liechang_number}.json")
                #     for k in data_du[str(group)]['want']:
                #         if(data2[str(user_id)].get(k,0)>0):
                #             k = k.split('_')
                #             name = eval(f"madeline_data{liechang_number}.get(k[0]).get(k[1]).get('name')")
                #             await daoju.finish(f"你的{name}面临被掠夺的风险.....", at_sender=True)
                #     await daoju.finish("当前du局非常安全，你可以放心进入", at_sender=True) 
            if(use_item_name=="幸运药水"):
                """
                提升运气的小道具，虽说不知道有没有真的提升...
                """
                if(data[str(user_id)].get("item").get(use_item_name, 0) > 0):
                    #确保自身没有幸运状态
                    if data[str(user_id)].get('buff2')!='lucky':
                        data[str(user_id)]["buff2"]='lucky'
                        data[str(user_id)]["lucky_times"] = 21
                        data[str(user_id)]["item"][use_item_name] -= 1
                        #写入文件
                        save_data(user_path / file_name, data)
                        await daoju.finish("使用成功，现在正常抓madeline可额外获得15草莓，持续20次。", at_sender=True)
                    else:
                        data[str(user_id)]["lucky_times"] += 20
                        restLucky = data.get(str(user_id)).get("lucky_times", 0) - 1
                        data[str(user_id)]["item"][use_item_name] -= 1
                        #写入文件
                        save_data(user_path / file_name, data)
                        await daoju.finish(f"使用成功，你幸运buff的次数额外增加了20次！当前剩余次数为：{restLucky}", at_sender=True)
                else:
                    await daoju.finish(f"你现在没有{use_item_name}", at_sender=True)
            
            command = use_item_name.split("/")
            #两个参数的指令
            if (len(command) == 2):
                item_name = command[0]  # 参数1(使用的道具名)
                if item_name == "幸运药水":
                    success = 999
                    try:
                        use_count = int(command[1])  # 参数2(使用的数量)
                    except ValueError:
                        await daoju.finish("请输入正确的幸运药水使用数量！", at_sender=True)
                    # 获取玩家的药水数量
                    user_items = data[str(user_id)].get("item", {})
                    current_potions = user_items.get(item_name, 0)
                    if use_count <= 0:
                        await daoju.finish("使用数量必须大于0！", at_sender=True)
                    if current_potions < use_count:
                        await daoju.finish(f"你的{item_name}数量不足！你只有{current_potions}瓶{item_name}！", at_sender=True)
                    # 确保自身没有幸运状态
                    if data[str(user_id)].get('buff2', "normal") != 'lucky' or data[str(user_id)].get('lucky_times', 0) == 0:
                        data[str(user_id)]["buff2"] = 'lucky'
                        data[str(user_id)]["lucky_times"] = 1  # 初始设定
                    # 增加幸运次数
                    data[str(user_id)]["lucky_times"] += 20 * use_count
                    restLucky = data[str(user_id)]["lucky_times"] - 1
                    # 扣除药水
                    data[str(user_id)]["item"][item_name] -= use_count
                    # 写入文件
                    save_data(user_path / file_name, data)
                    await daoju.finish(f"使用成功！你幸运buff的次数增加了{20 * use_count}次！当前剩余次数：{restLucky}", at_sender=True)
            #三个参数的指令
            if (len(command)==3):
                item_name = command[0]   #参数1(一般是使用的道具名)
                if (item_name.lower()=="madeline充能器"):
                    success = 999
                    arg2 = command[1]   #参数2(充能的madeline)
                    arg3 = command[2]   #参数2(充能的数量)
                    #首先判定有没有
                    if(data[str(user_id)].get("item").get(item_name, 0) > 0):
                        #选中madeline
                        nums = find_madeline(arg2.lower())
                        #查不到这个madeline的档案，终止
                        if(nums==0): 
                            await daoju.finish("请输入正确的Madeline名称哦！", at_sender=True)
                        #统计充能个数
                        try:
                            num_of_charge = int(arg3)
                        except:
                            await daoju.finish("请输入一个整数，谢谢。", at_sender=True)
                        #这不能是个负数或零
                        if num_of_charge <= 0:
                            await daoju.finish("我也想这么做，但是不允许。", at_sender=True)
                        data2 = open_data(user_path/f"UserList{nums[2]}.json")
                        level_num = nums[0]+'_'+nums[1]
                        if(data2[str(user_id)].get(level_num,0) >= num_of_charge):
                            data2[str(user_id)][level_num] -= num_of_charge
                            save_data(user_path/f"UserList{nums[2]}.json",data2)
                        else:
                            await daoju.finish(f"你没有这么多{arg2.lower()}可以拿来充能了！", at_sender=True)
                        if nums[0]=='5':
                            energy = 1800
                        elif nums[0]=='4':
                            energy = 600
                        elif nums[0]=='3':
                            energy = 200
                        elif nums[0]=='2':
                            energy = 100
                        elif nums[0]=='1':
                            energy = 60
                        else:
                            raise KeyError("Not an invalid madeline level")
                        #尝试加上能量
                        try:
                            data[str(user_id)]["energy"] += num_of_charge * energy
                        except:
                            #否则直接等于
                            data[str(user_id)]["energy"] = num_of_charge * energy
                        #写入文件
                        save_data(user_path / file_name, data)
                        text = str(num_of_charge * energy)
                        total_energy = str(data[str(user_id)]["energy"])
                        await daoju.finish(f"使用成功，你获得了{text}点能量值，你现在拥有{total_energy}点能量", at_sender=True)
                    else:
                        await daoju.finish(f"你现在没有{item_name}", at_sender=True) 
                        
            # 五个参数的指令
            # 批量充能指令
            if (len(command) == 5):
                item_name = command[0]  # 参数1：使用的道具
                arg2 = command[1]  # 参数2："all"（指定一次性充能）
                if item_name.lower() == "madeline充能器" and arg2.lower() == "all":
                    success = 999
                    arg3 = command[2]  # 参数3：猎场号
                    arg4 = command[3]  # 参数4：指定的 Madeline 等级（或 "all"）
                    arg5 = command[4]  # 参数5：每个 Madeline 保留的数量
                    # 检查道具是否足够
                    if data[str(user_id)].get("item", {}).get(item_name, 0) > 0:
                        liechang = str(arg3)  # 猎场号
                        if liechang not in ["1","2","3"]:
                            await daoju.finish("请输入正确的猎场号！", at_sender=True)
                        try:
                            min_keep = int(arg5)  # 需要保留的最小数量
                            if min_keep < 0:
                                await daoju.finish("不能设置负数的保留数量！", at_sender=True)
                        except ValueError:
                            await daoju.finish("请输入有效的保留数量！", at_sender=True)
                        # 读取用户 Madeline 数据
                        data2 = open_data(user_path / f"UserList{liechang}.json")
                        total_charged = 0  # 充能总数
                        total_energy = 0  # 总能量
                        madelines_charged = {}  # 记录充能的 madeline
                        # 如果 arg4 是 "all"，则充能所有等级
                        if arg4.lower() == "all":
                            levels_to_charge = ["1", "2", "3", "4", "5"]
                        else:
                            # 检查 arg4 是否是一个有效的数字
                            try:
                                level = int(arg4)
                                # 确保该数字在 1 到 5 之间
                                if 1 <= level <= 5:
                                    levels_to_charge = [str(level)]
                                else:
                                    await daoju.finish(f"请输入有效的Madeline等级（1-5）或者all！", at_sender=True)
                            except ValueError:
                                await daoju.finish(f"请输入一个有效的数字或者all作为Madeline等级！", at_sender=True)
                        for level in levels_to_charge:
                            if level not in ["1", "2", "3", "4", "5"]:
                                continue  # 如果是无效等级，直接跳过
                            # 遍历用户的 Madeline 数据，查找所有符合条件的 Madeline
                            for madeline_key, count in data2.get(str(user_id), {}).items():
                                madeline_level, madeline_id = madeline_key.split("_")
                                # 只处理指定等级的 Madeline
                                if madeline_level == level:
                                    chargeable = max(0, count - min_keep)  # 计算可充能数量
                                    if chargeable > 0:
                                        data2[str(user_id)][madeline_key] -= chargeable  # 扣除 Madeline
                                        total_charged += chargeable  # 统计总数
                                        madelines_charged[madeline_key] = chargeable  # 记录哪些 Madeline 充能了
                                        # 根据等级计算能量值
                                        energy_map = {"5": 1800, "4": 600, "3": 200, "2": 100, "1": 60}
                                        total_energy += chargeable * energy_map.get(level, 0)  # 计算总能量
                        # **没有 Madeline 可充能**
                        if total_charged == 0:
                            if min_keep == 0:
                                if arg4.lower() == "all":
                                    await daoju.finish(f"猎场{liechang}中，你没有任何Madeline可用于充能！", at_sender=True)
                                else:
                                    await daoju.finish(f"猎场{liechang}中，你没有任何{arg4}级的Madeline可用于充能！", at_sender=True)
                            else:
                                if arg4.lower() == "all":
                                    await daoju.finish(f"如果要保留{min_keep}个Madeline的话，你的猎场{liechang}中的Madeline数量不够，不足以充能哦！", at_sender=True)
                                else:
                                    await daoju.finish(f"如果要保留{min_keep}个Madeline的话，你的猎场{liechang}中的{arg4}级Madeline数量不够，不足以充能哦！", at_sender=True)
            
                        # **增加用户能量**
                        data[str(user_id)]["energy"] = data[str(user_id)].get("energy", 0) + total_energy
                        all_energy = str(data[str(user_id)]["energy"])
            
                        # **保存数据**
                        save_data(user_path / f"UserList{liechang}.json", data2)
                        # 写入文件
                        save_data(user_path / file_name, data)
            
                        if min_keep == 0:
                            if arg4.lower() == "all":
                                await daoju.finish(f"你已成功充能了猎场{liechang}所有等级的Madeline，获得了{total_energy}点能量，你现在拥有{all_energy}点能量！", at_sender=True)
                            else:
                                await daoju.finish(f"你已成功充能了猎场{liechang}所有{arg4}级的Madeline，获得了{total_energy}点能量，你现在拥有{all_energy}点能量！", at_sender=True)
                        else:
                            if arg4.lower() == "all":
                                await daoju.finish(f"你已成功充能了猎场{liechang}中所有数量大于{min_keep}个的Madeline，并且这些Madeline都保留了{min_keep}个！充能这些Madeline让你获得了{total_energy}点能量！你现在总共拥有{all_energy}点能量！", at_sender=True)
                            else:
                                await daoju.finish(f"你已成功充能了猎场{liechang}中所有数量大于{min_keep}个的{arg4}级Madeline，并且这些Madeline都保留了{min_keep}个！充能这些Madeline让你获得了{total_energy}点能量！你现在总共拥有{all_energy}点能量！", at_sender=True)
                    else:
                        await daoju.finish(f"你现在没有{item_name}", at_sender=True)
                        
        #--------------------这些道具只有在0猎才能使用--------------------
            #此处判定是否在0猎
            liechang_number = data[str(user_id)].get('lc')
            if(liechang_number=='0'): 
                #两个参数的指令
                # 只有在包含斜杠时才进行分割
                await daoju.finish("madeline竞技场目前无法使用这件道具哦~") 
                # valid_item_names = ["复仇之刃", "鲜血之刃"]
                # if "/" in use_item_name:
                #     command = use_item_name.split("/")
                #     if len(command) in [2, 3]:
                #         item_name = command[0]   #参数1
                #         if item_name == "仇刃":
                #             item_name = "复仇之刃"
                #         elif item_name == "血刃":
                #             item_name = "鲜血之刃"
                #         if item_name in valid_item_names:
                #             try:
                #                 pos = int(command[1]) - 1  # 将 pos 转换为整数   #参数2
                #                 if pos not in range(0, 10):  # 允许范围 0-9
                #                     raise ValueError
                #             except ValueError:
                #                 await daoju.finish("请输入你要进攻的正确的擂台号（1-10）！", at_sender=True)
                #             # 初始化第三个参数
                #             phase = 1
                #             # 鲜血之刃阶段
                #             if len(command) == 3 and item_name == "鲜血之刃":
                #                 try:
                #                     phase = int(command[2])  # 参数3
                #                     if phase not in range(1, 7):  # 允许范围 [1, 2, 3, 4, 5, 6]
                #                         raise ValueError
                #                 except ValueError:
                #                     await daoju.finish("请输入你需要使用鲜血之刃的正确阶段（1-6）", at_sender=True)
                #                     # 当前时间戳
                #             if (user_id in ban):
                #                 await daoju.finish("很抱歉，0猎不让使用脚本，您已经被封禁，请联系Desom-fu哦~", at_sender=True)
                #             if (data[str(user_id)].get("item", {}).get(item_name, 0) > 0 or data[str(user_id)].get("collections", {}).get(item_name, 0) > 0):
                #                 """
                #                 复仇之刃：使用后基础战斗力+10，挑战指定擂台大于50战力的madeline，使用后冷却时间10min，会受伤
                #                 """
                #                 """
                #                 鲜血之刃：使用后基础战斗力+阶段*2，挑战指定擂台大于60战力的madeline，使用后冷却时间阶段*5min，会受伤
                #                 """
                #                 current_time = datetime.datetime.now()
                #                 next_time_r = datetime.datetime.strptime(data.get(str(user_id)).get('next_time'), "%Y-%m-%d %H:%M:%S")
                #                 delta_time = next_time_r - current_time
                #                 delta_minutes = divmod(delta_time.total_seconds(), 60)  # 获取分钟和秒
                #                 minutes = int(delta_minutes[0])
                #                 seconds = int(delta_minutes[1])
                #                 total_time = minutes*60 + seconds
                #                 if(total_time >= 600):
                #                     await daoju.finish(f"大于10min的冷却期间不能使用{item_name}！你还需要等{minutes - 10}分钟{seconds}秒才能使用本道具！", at_sender=True)
                #                 # 检查开放时间
                #                 is_open, close_text = pvp_opening(current_time)
                #                 if not is_open:
                #                     await daoju.finish(close_text, at_sender=True)
                #                 user_data = open_data(user_path / file_name)
                #                 pvp_data = open_data(pvp_path)
                #                     # 检查当前是否有猎场
                #                 if not pvp_data:
                #                     await daoju.finish("madeline竞技场尚未开启, 暂无法使用该道具！", at_sender=True)
                #                 pvp_coldtime_data = open_data(pvp_coldtime_path)
                #                 kc_data = open_data(user_list2)
                #                 kc_data3 = open_data(user_list3)
                #                 nickname = event.sender.nickname
                #                 ranliechangnum = random.randint(1, 3)
                #                 #提前设定一些默认值
                #                 rana = 0
                #                 bonus_rank = 10 # 复仇之刃初始值+10
                #                 if item_name == "鲜血之刃":
                #                     phase_bonus = {1: 5, 2: 10, 3: 15, 4: 20, 5: 25, 6: 30}
                #                     bonus_rank = phase_bonus.get(phase, 0)  # 默认值为 0，防止 phase 不在范围内
                #                 lie3 = 0
                #                 lie3chou = 0
                #                 final_rank = 0
                #                 #如果没有注册二号猎场
                #                 if(not user_id in kc_data):
                #                     await daoju.finish("你还没有解锁二号猎场哦，无法进入pvp竞技场，也无法使用道具~", at_sender=True)
                #                 #若解锁三猎，将3猎加入可选池，并且初始概率+5
                #                 daoju_liechang_number = "2"
                #                 if (user_id in kc_data3):
                #                     if (ranliechangnum <=1):
                #                         daoju_liechang_number = "3"
                #                         rana += 5
                #                         lie3 += 5 #如果是3猎max和min都加5
                #                     #从库存中随机抓出一个madeline，概率均匀
                #                 if (daoju_liechang_number == "2"):
                #                     madeline = random.choice(list(kc_data[user_id].keys()))
                #                 #随机到3猎就从3猎抓
                #                 if (daoju_liechang_number == "3"):
                #                     madeline = random.choice(list(kc_data3[user_id].keys()))                                    
                #                 #在猎场文件中找到位置
                #                 list_current = pvp_data['list']
                #                 stat = 0        #0为默认回复，3、4赢，5输
                #                 madelinea = madeline.split('_')     #将字符串转为信息列表
                #                 levela = int(madelinea[0])          #我的等级
                #                 numa = int(madelinea[1])            #我的编号
                #                 levelb = 0                     #对面等级
                #                 numb = 0                       #对面编号
                #                 rana += random.randint(levela*10, levela*10+50)  #战力系统，1级madeline10-60，2级20-70以此类推
                #                 # 根据队列人数调用逻辑函数
                #                 if len(list_current) < 10:
                #                     #还没满十个不让用，依次排队进入
                #                     await daoju.finish("现在擂台上人数都没满，不能进攻！", at_sender=True)
                #                 else:
                #                     if(list_current[pos][0]==user_id):
                #                         # 无法向自己复仇
                #                         await daoju.finish("你为什么会向自己进攻啊？？？", at_sender=True)
                #                     else:
                #                         ranb = list_current[pos][3]  # 获取对方的战力
                #                         if ranb < 50 and item_name == "复仇之刃":
                #                             await daoju.finish(f"由于对面战力为 [{ranb}]<50，无法让复仇之刃提起兴趣，你无法对他进行复仇！", at_sender=True)
                #                         if ranb < 60 and item_name == "鲜血之刃":
                #                             await daoju.finish(f"由于对面战力为 [{ranb}]<60，无法让鲜血之刃提起兴趣，你无法进攻他！", at_sender=True)
                #                         stat, nicknameb, ranb, ranbrank, kicked_user_id, lie3chou, levelb, numb, pos, bonus_rank, final_rank = pk_combat(
                #                             list_current, pos, user_id, madeline, nickname, rana, lie3, bonus_rank, final_rank
                #                             )
                #                 #增加回合次数
                #                 pvp_data['count'] += 1
                #                 #更新pvp文件
                #                 pvp_data['list'] = list_current
                #                 save_data(pvp_path,pvp_data)
                #                 ####通告PK结果####
                #                 pk_text = ""
                #                 #自己madeline的信息(查等级，查名字，查描述，查图片)
                #                 information = print_zhua(levela,numa,daoju_liechang_number)
                #                 madelinenamea = information[1]
                #                 # img = information[2]
                #                 # description = information[3]
                #                 #根据不同状态添加额外反馈信息
                #                 if lie3chou == 2:
                #                 # lie3chou == 2时，levela 和 madelinenamea 从 liechang_number = "2" 查，levelb 和 madelinenameb 从 liechang_number = "3" 查
                #                     madelinenameb = print_zhua(levelb, numb, "3")
                #                 elif lie3chou == 1:
                #                     # lie3chou == 1时，levela 和 madelinenamea 以及 levelb 和 madelinenameb 都从 liechang_number = "2" 查
                #                     madelinenameb = print_zhua(levelb, numb, "2")
                #                 elif lie3chou == 0:
                #                     # lie3chou == 0时，没有madelineb，返回none
                #                     madelinenameb = "none"
                #                 if item_name == "复仇之刃":
                #                     # 通用部分
                #                     common_text = (
                #                         f"\n你抽出了 [{levela}级的{madelinenamea}]，这个madeline的本次进攻战力为 [{rana}]+[{bonus_rank}]=[{final_rank}]\n\n"
                #                         f"你满怀愤怒的让你的madeline向 [擂台{pos+1}] 的擂主 [{nicknameb}] 的 [{levelb}级{madelinenameb[1]}] 挥出复仇之刃！\n"
                #                         f"该madeline的常驻战力为 [{ranb}]\n\n"
                #                         f"你的 [{levela}级的{madelinenamea}] 的本次进攻战力为 [{final_rank}]；"
                #                         f" [{nicknameb}] 的 [{levelb}级的{madelinenameb[1]}] 的防守战力为 [{ranbrank}]"
                #                     )
                #                     # 根据 stat 更新 pk_text
                #                     if stat == 5:
                #                         pk_text = common_text + f"\n\n你复仇失败了！(｡•́︿•̀｡)"
                #                     elif stat == 4:
                #                         pk_text = common_text + f"\n\n你站上擂台的madeline的常驻战力为 [{rana}]！\n\n你的madeline的战力和擂主的madeline的本次战力相等，但是由于你是复仇者，复仇成功！ヽ(o^ ^o)ﾉ"
                #                     elif stat == 3:
                #                         pk_text = common_text + f"\n\n你站上擂台的madeline的常驻战力为 [{rana}]！\n\n你复仇成功了！ヽ(o^ ^o)ﾉ"
                #                     elif stat == 0:
                #                         pk_text = "如果出现这条回复请向Desom-fu报告bug，按理来说不可能出现这条回复的（"
                #                 else: 
                #                     #鲜血之刃回复
                #                     common_text = (
                #                         f"\n你抽出了 [{levela}级的{madelinenamea}]。你向鲜血之刃祈求，献祭了{phase*50}ml鲜血，提升了{madelinenamea}{bonus_rank}点战斗力，本次进攻战力为 [{rana}]+[{bonus_rank}]=[{final_rank}]\n\n"
                #                         f"你的madeline遇到了 [擂台{pos+1}] 的擂主 [{nicknameb}] 的 [{levelb}级{madelinenameb[1]}]，该madeline的常驻战力为 [{ranb}]\n\n"
                #                         f"你的 [{levela}级的{madelinenamea}] 的本次进攻战力为 [{final_rank}]；"
                #                         f" [{nicknameb}] 的 [{levelb}级的{madelinenameb[1]}] 的防守战力为 [{ranbrank}]"
                #                     )
                #                     # 根据 stat 更新 pk_text
                #                     if stat == 5:
                #                         pk_text = common_text + f"\n\n你的进攻失败了！(｡•́︿•̀｡)"
                #                     elif stat == 4:
                #                         pk_text = common_text + f"\n\n你的madeline的战力和擂主的madeline的本次战力相等，但是由于你是挑战者，进攻成功！ヽ(o^ ^o)ﾉ\n\n你站上擂台的madeline的常驻战力为 [{rana}]！"
                #                     elif stat == 3:
                #                         pk_text = common_text + f"\n\n进攻成功！ヽ(o^ ^o)ﾉ\n\n你站上擂台的madeline的常驻战力为 [{rana}]！"
                #                     elif stat == 0:
                #                         pk_text = "如果出现这条回复请向Desom-fu报告bug，按理来说不可能出现这条回复的（"
                #                 # 如果被踢下去的对方战力大于60，发放安慰奖
                #                 # 添加@被踢下去的玩家的逻辑
                #                 if stat in (3, 4):  # 挑战成功或平战力胜利
                #                     # 确保列表不为空
                #                     if list_current:
                #                         pk_text += "\n\n啊呀，" + MessageSegment.at(kicked_user_id) + "被踢下了擂台了！"
                #                         # 如果被踢下的玩家的战力大于 60，发放安慰奖
                #                         if ranb >= 60:
                #                             user_data[kicked_user_id]['berry'] += 10  # 给被踢玩家发放 10 草莓作为安慰奖
                #                             pk_text += f"\n因为 [{nicknameb}] 被踢下擂台的madeline的常驻战力达到了 [{ranb}]≥60，所以获得了10草莓的安慰奖！"
                #                     else:
                #                         pk_text += "\n\n当前没有玩家被踢下擂台。"

                #                 if stat == 5:  # 挑战失败
                #                     # 确保列表不为空
                #                     if list_current:
                #                         if rana >= 80:
                #                             user_data[user_id]['berry'] += 20  # 失败玩家发放 20 草莓作为安慰奖
                #                             pk_text += f"\n因为 [{nickname}] 未能复仇成功的madeline的战力 [{rana}]≥80，所以获得了20草莓的安慰奖！"
                #                     else:
                #                         pk_text += "\n\n当前没有玩家被踢下擂台。"
                #                 if item_name == "复仇之刃":
                #                     pk_text += "\n\n你献祭了鲜血使用了复仇之刃，受到了反噬，需要休息10min才能继续！"
                #                 else:
                #                     pk_text += f"\n\n你献祭了鲜血使用了鲜血之刃，进入了虚弱状态，需要休息{bonus_rank}min才能继续！"
                #                 # 发送挑战结果
                #                 await daoju.send(pk_text, at_sender=True)
                #                 #公布结果(回合数达到totalCount决出胜负)
                #                 set_final, total, reward, timeReward = process_results(list_current, pvp_data)
                #                 if set_final:
                #                     text = "恭喜"
                #                     for v in set_final:
                #                         text += MessageSegment.at(v)
                #                         user_data[v]['berry'] += total

                #                     text += f"在这场角逐中取得胜利,全员获得{reward}+{timeReward}={total}草莓奖励！"
                #                     pvp_data.clear()
                #                     timestamp3 = int(time.time())
                #                     pvp_coldtime_data = open_data(pvp_coldtime_path)
                #                     pvp_coldtime_data['last_pvp_end_time'] = timestamp3  # 保存当前时间戳

                #                     # 发消息
                #                     await bot.call_api("send_group_msg", group_id=zhuama_group, message=text)
                #                 user_data[user_id]["buff"] = "hurt"
                #                 if item_name == "复仇之刃":
                #                     user_data[user_id]['next_time'] = time_decode(datetime.datetime.now()+datetime.timedelta(minutes=10))
                #                     user_data[user_id]["item"][item_name] -= 1 
                #                 else:
                #                     user_data[user_id]['next_time'] = time_decode(datetime.datetime.now()+datetime.timedelta(minutes=bonus_rank))
                #                 save_data(pvp_coldtime_path, pvp_coldtime_data)   
                #                 save_data(user_path / file_name ,user_data)
                #                 save_data(pvp_path,pvp_data)                         
                #             else:
                #                 await daoju.finish(f"你现在没有{item_name}", at_sender=True)
                #         else:
                #             await daoju.finish("madeline竞技场目前无法使用这件道具哦~") 
                #     else:
                #         await daoju.finish("请输入正确的指令哦！正确的指令如下：/use 复仇之刃(鲜血之刃)/擂台号/(鲜血之刃阶段)！") 
                # else:   
                #     await daoju.finish("madeline竞技场目前无法使用这件道具哦~") 
            else:          
            #--------------------以下道具0号猎场不能使用--------------------                           

            #--------------------这些道具需要限制所在猎场的使用--------------------
                #两个参数的指令 提取器放猎场判定之前
                # madeline提取器
                if(len(command)==2):
                    item_name = command[0]   #参数1
                    if(item_name.lower()=="madeline提取器"):
                        success = 999
                        arg2 = command[1]   #madeline名字
                        if not arg2:
                             await daoju.finish("请输入正确的Madeline名称哦！", at_sender=True)
                        #若是解密相关不检查是否拥有提取器
                        """
                        隐藏madeline和一些隐藏线索
                        """
                        if(arg2.lower()=="madeline提取器"):
                            await daoju.finish("请输入.puzzle confr1ngo来查询confr1ngo相关谜题哦！\n请输入.puzzle other来查询其他谜题哦！")
                        #隐藏madeline线索
                        for k in range(len(secret_list)):
                            if(arg2.lower()==secret_list[k][0]):
                                img = madeline_level0_path / f"madeline{str(k+1)}.png"
                                description = secret_list[k][1]
                                await daoju.finish("等级：？？？\n" + f"{arg2}\n" + MessageSegment.image(img) + description)
                            #一个特别的隐藏，使用后不获得madeline，而是获得一个新的藏品，并且移除木质十字架
                            if(arg2.lower()=="kmngkggarnkto"):
                                if data[str(user_id)].get("collections",{}).get('圣十字架', 0) >= 1:
                                    await daoju.finish("你已经有了一个圣十字架了，所以这串咒语再无意义……" , at_sender=True)  
                                if data[str(user_id)].get("collections",{}).get('木质十字架', 0) > 0:
                                    #只有在持有木质十字架时输入才有效
                                    if (data[str(user_id)].get("collections").get('木质十字架', 0) >= 1):
                                        data[str(user_id)]['collections']['木质十字架'] = 0
                                        del data[str(user_id)]['collections']['木质十字架']
                                        data[str(user_id)]['collections']['圣十字架'] = 1
                                        #写入文件
                                        save_data(user_path / file_name, data)
                                        await daoju.finish("一瞬间，十字架中的宝石散发出耀眼的光芒。光辉穿透浓厚的迷雾，将四周映照得清晰无比。你感受到一股奇异的力量从十字架中涌出，仿佛某种封印正在被解除。光芒逐渐汇聚，形成一个模糊的影像，那是一片神秘的符号与文字交织而成的图案。十字架轻微震颤，仿佛在回应某种远古的力量。\n没过一会，你感受到madeline们的属性被强化：动作更加迅捷，力量更加充沛，甚至连周围的细微动静都变得清晰可辨。尽管光芒渐渐收敛，但这股力量却深深烙印在你体内，成为前行的支柱。\n 输入.藏品 圣十字架 以查看具体效果")                            
                                else:
                                    await daoju.finish("似乎是缺少了什么东西，你输入这串咒语后什么都没有发生。" , at_sender=True)
                        if(data[str(user_id)].get("item").get(item_name, 0) > 0):
                            """
                            可以提取特定的一个madeline，但是等级越高成功概率越低，且若失败了会给与更长的冷却时间
                            """
                            # 开新猎场要改
                            nums = find_madeline(arg2.lower())
                            # 没有对应的玛德琳
                            if nums == 0:
                                await daoju.finish("请输入正确的Madeline名称哦！", at_sender=True)
                            data2 = open_data(user_list2)
                            data3 = open_data(user_list3)
                            data4 = open_data(user_list4)
                            # 检查返回值
                            if not nums or len(nums) < 3:
                                await daoju.finish("请输入正确的Madeline名称哦！", at_sender=True)
                            # 判定猎场
                            if liechang_number=='2' or nums[2] == "2":  
                                if str(user_id) not in data2:
                                    await daoju.finish("你还未解锁通往异域茂林的道路，请先在第异域茂林抓到任意一个Madeline哦！", at_sender=True)
                            if liechang_number=='3' or nums[2] == "3":  
                                if data[str(user_id)].get("item").get('神秘碎片', 0) < 5:
                                    await daoju.finish("你还未解锁通往翡翠矿井的道路...", at_sender=True)
                                if str(user_id) not in data3:
                                    await daoju.finish("请先在翡翠矿井抓到任意一个Madeline吧！", at_sender=True)
                            # 4猎必须要有黄球才能使用提取器
                            if liechang_number == "4" or nums[2] == "4":
                                if(not '黄色球体' in data[str(user_id)]['collections']):
                                    await daoju.finish("地下终端的力量仍然强大……你未能满足条件，现在无法在地下终端内使用Madeline提取器……", at_sender = True)
                                if str(user_id) not in data:
                                    await daoju.finish("请先在地下终端抓到任意一个Madeline吧！", at_sender=True)
                                    
                            rnd = random.randint(1,100)
                            if(rnd <= 20+15*(5-int(nums[0]))):
                                success = 1
                                information = print_zhua(int(nums[0]), int(nums[1]), nums[2])
                            else:
                                #受伤，更新下次抓的时间
                                hitNumber = random.randint(1,100)
                                noHitRate = 0
                                #判定道具的部分
                                wing = data[str(user_id)].get("collections",{}).get('天使之羽', 0)
                                crystal = data[str(user_id)].get("collections",{}).get('紫晶魄', 0)
                                #增加免伤率的部分
                                #天使之羽，增加2%
                                if (wing >= 1):
                                    noHitRate += 2
                                #紫晶魄，增加3%
                                if (crystal >= 1):
                                    noHitRate += 3
                                if hitNumber > noHitRate:
                                    cd_time = random.randint(int(nums[0])*60, int(nums[0])*60+120)
                                    current_time = datetime.datetime.now()
                                    #检测回想之核
                                    dream = data[str(user_id)].get("collections",{}).get("回想之核", 0)
                                    next_time = current_time + datetime.timedelta(minutes=cd_time-dream)
                                    data[str(user_id)]['next_time'] = next_time.strftime("%Y-%m-%d %H:%M:%S")
                                    data[str(user_id)]["buff"] = "hurt"  #受伤
                                    fail_text = f"提取失败！提取器爆炸了，你受伤了，需要休息{str(cd_time)}分钟"  #失败文本
                                else:
                                    fail_text = f"提取失败！提取器爆炸了，但是有一股神秘的力量抵挡了本次爆炸伤害"  #失败文本
                                success = 2
                            data[str(user_id)]["item"][item_name] -= 1
                        else:
                            await daoju.finish(f"你现在没有{item_name}", at_sender=True)

                #此处判定猎场是否已解锁
                #此处判定如果2猎是否有指南针，若没有则迷路
                if liechang_number == "2":
                    if success != 0:
                        pass
                    else:
                        stuck_path = Path() / "data" / "UserList" / "Struct.json"
                        #打开森林被困名单
                        stuck_data = open_data(stuck_path)
                        #迷路
                        lost = 1
                        #是否拥有指南针道具
                        if('item' in data[str(user_id)]):
                            if(data[str(user_id)]['item'].get('指南针',0) > 0):
                                lost = 0
                        #迷路事件
                        if(lost==1):
                            rnd = random.randint(1,10)
                            if(rnd >= 5):
                                #困在森林里八小时，在此期间什么都干不了
                                current_time = datetime.datetime.now()
                                next_time = current_time + datetime.timedelta(minutes=480)
                                #检测回想之核
                                try:
                                    dream = data[str(user_id)]['collections'].get("回想之核", 0)
                                except:
                                    dream = 0
                                if dream >= 1:
                                    next_time = current_time + datetime.timedelta(minutes=479)
                                data[str(user_id)]['next_time'] = next_time.strftime("%Y-%m-%d %H:%M:%S")
                                data[str(user_id)]['buff'] = 'lost'
                                #加入森林被困名单
                                stuck_data[user_id] = '2'
                                #写入主数据表
                                save_data(user_path / file_name, data)
                                #写入森林被困名单
                                save_data(stuck_path, stuck_data)   
                                #发送消息
                                await daoju.finish("你在使用道具的时候，一不小心在森林里迷路了，不知道何时才能走出去……(请在你觉得可能找到路的时候使用zhuamadeline指令)", at_sender=True)
                            
                if liechang_number=='3':
                    if success != 0:
                        pass
                    else:
                        if data[user_id]['item'].get('神秘碎片',0) < 5:
                            await daoju.finish("你还未解锁通往第三猎场的道路...", at_sender=True)
                        try:
                            helmat = data[str(user_id)]['collections']['矿工头盔']
                        except:
                            helmat = 0
                        rnd_hurt = 10
                        rnd_stuck = random.randint(1,100)
                        if helmat>=1:
                            rnd_hurt -=5
                        if(rnd_stuck<=rnd_hurt):
                            stuck_path = Path() / "data" / "UserList" / "Struct.json"
                            full_path = Path() / "data" / "UserList" / "UserData.json"
                            #打开被困名单
                            stuck_data = open_data(stuck_path)
                            #受伤1.5小时，在此期间什么都干不了
                            current_time = datetime.datetime.now()
                            next_time = current_time + datetime.timedelta(minutes=90)
                            #检测回想之核
                            try:
                                dream = data[str(user_id)]['collections'].get("回想之核", 0)
                            except:
                                dream = 0
                            if dream >= 1:
                                next_time = current_time + datetime.timedelta(minutes=89)
                            data[str(user_id)]['next_time'] = next_time.strftime("%Y-%m-%d %H:%M:%S")
                            data[str(user_id)]['buff'] = 'hurt'
                            #加入山洞被困名单
                            stuck_data[user_id] = '3'
                            #写入主数据表
                            save_data(full_path, data)
                            #写入山洞被困名单
                            save_data(stuck_path, stuck_data)

                            #随机事件文本
                            text = "你在使用道具的过程中，没有任何madeline被道具吸引，结果一不小心你就撞到了山洞上！不过幸好道具没消耗……"
                            #发送消息
                            await daoju.finish(text+"你需要原地等待90分钟，或者使用急救包自救，又或者等待他人来救你……", at_sender=True)

                #debuff清除逻辑(使用其他抓madeline道具前判定)
                debuff_clear(data,user_id)
                if(use_item_name=="胡萝卜"):
                    if(data[str(user_id)].get("item").get(use_item_name, 0) > 0):

                        """
                        胡萝卜：打破cd额外抓一次，使用的时候有70%的概率抓出兔类madeline,
                        也有30%概率正常抓取
                        """

                        #随机选择是正常抓取还是从兔类madeline里抓
                        rnd = random.randint(1,10)
                        if(rnd <= 7):
                            #从兔类里抓
                            weights = {
                                3: 30,  # 3级的概率为30%
                                4: 45,  # 4级的概率为45%
                                5: 25   # 5级的概率为25%
                            }
                            weighted_choices = []
                            for level, weight in weights.items():
                                weighted_choices.extend([level] * weight)
                            chosen_level = random.choice(weighted_choices)
                            #----后续如果新加猎场了，直接修改这里----
                            liechang_mapping = {
                                '1': rabbit_madeline1,
                                '2': rabbit_madeline2,
                                '3': rabbit_madeline3
                            }
                            # 获取对应的列表并筛选
                            rabbit_madeline_list = liechang_mapping.get(liechang_number, [])
                            rabbit = [rabbit for rabbit in rabbit_madeline_list if rabbit[0] == chosen_level]
                            #rabbit = eval(f"rabbit_madeline{liechang_number}")

                            rabbit_rnd = random.randint(0, len(rabbit)-1)  #随机选择一个
                            information = print_zhua(rabbit[rabbit_rnd][0], rabbit[rabbit_rnd][1], liechang_number)
                            #检测奇想魔盒
                            magicBox = data[str(user_id)]['collections'].get("奇想魔盒", 0) 
                            #检测奇想扑克
                            puke = data[str(user_id)]['collections'].get("奇想扑克", 0)    
                            success = 1
                        else:
                            #正常抓取
                            information = zhua_random(30, 150, 600, 850, liechang_number=data[str(user_id)]['lc'])
                            success = 1
                        data[str(user_id)]["item"][use_item_name] -= 1                
                    else:
                        await daoju.finish(f"你现在没有{use_item_name}", at_sender=True)
                if(use_item_name=="弹弓"):
                    """
                    没啥特殊的，只是额外正常地再抓一次
                    """
                    if(data[str(user_id)].get("item").get(use_item_name, 0) > 0):
                        information = zhua_random(liechang_number=liechang_number)
                        data[str(user_id)]["item"][use_item_name] -= 1
                        #检测奇想魔盒
                        magicBox = data[str(user_id)]['collections'].get("奇想魔盒", 0) 
                        #检测奇想扑克
                        puke = data[str(user_id)]['collections'].get("奇想扑克", 0)
                        success = 1  
                    else:
                        await daoju.finish(f"你现在没有{use_item_name}", at_sender=True)
                if(use_item_name=="一次性小手枪"):
                    if(data[str(user_id)].get("item").get(use_item_name, 0) > 0):
                        """
                        没啥特殊的，只是额外正常地再抓一次
                        """
                        information = zhua_random(20, 100, 500, 800, liechang_number=liechang_number)
                        data[str(user_id)]["item"][use_item_name] -= 1
                        #检测奇想魔盒
                        magicBox = data[str(user_id)]['collections'].get("奇想魔盒", 0) 
                        #检测奇想扑克
                        puke = data[str(user_id)]['collections'].get("奇想扑克", 0)
                        success = 1 
                    else:
                        await daoju.finish(f"你现在没有{use_item_name}", at_sender=True)
                if(use_item_name=="充能陷阱"):
                    if(data[str(user_id)].get("item").get(use_item_name, 0) > 0):
                        """
                        50%概率受伤2h，50%抓345级madeline
                        """
                        #获取充能箱状态
                        elect_status = data[user_id].get("elect_status", False)
                        boom = random.randint(1,100)
                        #充能箱100%爆炸
                        if elect_status == True:
                            boom = 100
                        if boom >= 51:
                            #受伤，更新下次抓的时间
                            hitNumber = random.randint(1,100)
                            noHitRate = 0
                            #判定道具的部分
                            wing = data[str(user_id)].get("collections",{}).get('天使之羽', 0)
                            crystal = data[str(user_id)].get("collections",{}).get('紫晶魄', 0)
                            #增加免伤率的部分
                            #天使之羽，增加2%
                            if (wing >= 1):
                                noHitRate += 2
                            #紫晶魄，增加3%
                            if (crystal >= 1):
                                noHitRate += 3
                            #充能箱100%爆炸
                            if elect_status == True:
                                noHitRate = 0
                            if hitNumber > noHitRate:
                                cd_time = 120
                                elect_text = ''
                                # 开启充能箱cd只有60min
                                if elect_status == True:
                                    cd_time = 60
                                    elect_text = '由于你把充能箱撞开了，你使用的这个充能陷阱必定爆炸，但是只会炸伤你60min！\n'
                                current_time = datetime.datetime.now()
                                next_time = current_time + datetime.timedelta(minutes=cd_time)
                                #检测回想之核
                                try:
                                    dream = data[str(user_id)]['collections'].get("回想之核", 0)
                                except:
                                    dream = 0
                                if dream >= 1:
                                    next_time = current_time + datetime.timedelta(minutes=cd_time-1)
                                data[str(user_id)]['next_time'] = next_time.strftime("%Y-%m-%d %H:%M:%S")
                                data[str(user_id)]["buff"] = "hurt"  #受伤
                                fail_text = elect_text + f"你在布置充能陷阱的时候，突然间能量迸发，充能陷阱爆炸了！你受伤了，需要休息{str(cd_time)}分钟"  #失败文本
                            else:
                                fail_text = f"你在布置充能陷阱的时候，突然间能量迸发，充能陷阱爆炸了！但是有一股神秘的力量抵挡了本次爆炸伤害"  #失败文本
                            success = 2
                        else:
                            information = zhua_random(50, 350, 1000, 1001, liechang_number=liechang_number)
                            #检测奇想魔盒
                            magicBox = data[str(user_id)]['collections'].get("奇想魔盒", 0) 
                            #检测奇想扑克
                            puke = data[str(user_id)]['collections'].get("奇想扑克", 0)
                            success = 1
                        data[str(user_id)]["item"][use_item_name] -= 1

                    else:
                        await daoju.finish(f"你现在没有{use_item_name}", at_sender=True)

                if(use_item_name=="时间献祭器"):
                    if(data.get(user_id).get('item').get('时间献祭器',0) > 0):
                        next_time = get_time_from_data(data[str(user_id)])
                        current_time = datetime.datetime.now()
                        if (not 'buff' in data[str(user_id)]):
                            data[str(user_id)].get('buff')=='normal'
                        #一些啥都干不了的buff
                        if(data[str(user_id)].get('buff')=='lost'): 
                            await daoju.finish(f"你现在正在迷路中，连路都找不到，怎么使用时间献祭器呢？", at_sender=True)
                        if(data[str(user_id)].get('buff')=='confuse'): 
                            await daoju.finish(f"你现在正在找到了个碎片，疑惑着呢，不能使用时间献祭器。", at_sender=True)
                        #如果受伤了则无法使用道具(时间秒表除外)
                        if(data[str(user_id)].get("buff")=="hurt"): 
                            #一些额外操作：如果还没过下次时间，计算与下次的时间间隔，如果过了，可以使用道具
                            current_time = datetime.datetime.now()
                            next_time_r = datetime.datetime.strptime(data.get(str(user_id)).get('next_time'), "%Y-%m-%d %H:%M:%S")
                            if(current_time < next_time_r):
                                delta_time = next_time_r - current_time
                                await daoju.finish(f"你受伤了，需要等{time_text(delta_time)}才能继续", at_sender=True)
                            else:
                                outofdanger(data,str(user_id),daoju,current_time,next_time_r)
                        #没到下一次抓的时间
                        if(current_time < next_time):
                            text = time_text(str(next_time-current_time))
                            await daoju.finish(f"别抓啦，{text}后再来吧", at_sender = True)

                        #延长下次抓的cd
                        next_time = current_time + datetime.timedelta(minutes=60)
                        #检测回想之核
                        try:
                            dream = data[str(user_id)]['collections'].get("回想之核", 0)
                        except:
                            dream = 0
                        if dream >= 1:
                            next_time = current_time + datetime.timedelta(minutes=59)
                        data[str(user_id)]['next_time'] = time_decode(next_time)
                        # 强制修复bug
                        data[str(user_id)]["buff"] = "normal"
                        #zhuamadeline并增加爆率
                        information = zhua_random(50,300,500,999,liechang_number=liechang_number)
                        #检测奇想魔盒
                        magicBox = data[str(user_id)]['collections'].get("奇想魔盒", 0)
                        #检测奇想扑克
                        puke = data[str(user_id)]['collections'].get("奇想扑克", 0)
                        success = 1
                    else:
                        await daoju.finish(f"你现在没有{use_item_name}", at_sender=True)
            
                #使用成功
                if(success==1):

                    information = tool_zhuamadeline(information, data, user_id)
                    #得到madeline信息
                    level       = information[0]   #等级
                    name        = information[1]   #名字
                    img         = information[2]   #图片
                    description = information[3]   #描述
                    num         = information[4]   #编号
                    lc          = information[5]   #所属猎场
                    new_print   = information[6]   #是否出新

                    #如果是奇想魔盒相关道具则进行判定
                    berry_give = 0
                    magic_text = ''
                    try:
                        if magicBox>=1:
                            berry_rnd=random.randint(1,100)
                            if berry_rnd<=20:
                                berry_give += 5 * int(level)
                                data[str(user_id)]['berry'] += berry_give
                                magic_text = '\n\n奇想魔盒震动了一下。'
                    #否则无事发生
                    except:
                        pass
                    #奇想扑克判定
                    puke_text = ''
                    try:
                        if puke>=1:
                            puke_rnd=random.randint(1,100)
                            if puke_rnd<=20:
                                berry_give += 5 * int(level)
                                data[str(user_id)]['berry'] += berry_give
                                puke_text = '\n\n奇想扑克抽动了一下。'
                    #否则无事发生
                    except:
                        pass
                    #判定乐谱
                    sheet_text = ""
                    try:
                        sheet_music = data[str(user_id)]['collections'].get('星光乐谱',0)
                    except:
                        sheet_music = 0
                        
                    if (sheet_music >=1):   
                        sheet_rnd = random.randint(1,10)
                        if sheet_rnd <= 2:
                            # 没有草莓不触发
                            if berry_give >0:
                                sheet_text = "\n\n在悠扬的乐曲声中，草莓似乎被唤醒了，焕发出勃勃生机，迅速分裂出更多的果实！"
                                berry_give *= 2
                            
                    berry_text = ""
                    if berry_give != 0:
                        berry_text = '\n\n本次你获得了'+str(berry_give)+'颗草莓'         

                    #写入文件
                    save_data(user_path / file_name, data)
                    #发送消息
                    await daoju.finish(item_text+new_print+
                                     f'\n等级: {level}\n'+
                                    f'{name}'+
                                    MessageSegment.image(img)+
                                    f'{description}'+
                                    f'{magic_text}'+
                                    f'{puke_text}'+
                                    f"{sheet_text}"+
                                    f'{berry_text}',
                                    at_sender = True)
                #使用失败
                if(success==2):

                    #写入文件
                    save_data(user_path / file_name, data)

                    await daoju.finish(fail_text, at_sender=True)
                    
                # 最后检查道具名称是否在商品列表中
                if use_item_name not in item:
                    await daoju.finish(f"现在整个抓玛德琳都没有这个道具 [{use_item_name}]，你为什么会想用呢？", at_sender=True)
                # 在商品列表里面就直接回答暂无法使用
                await daoju.finish(f"[{use_item_name}] 使用方法有误或者现在无法使用哦!", at_sender=True)
        else:
            await daoju.finish("你还没有任何道具哦", at_sender=True)
    else:
        await daoju.finish("你还没尝试抓过madeline.....")

#查看道具信息
ckdj = on_command('item', permission=GROUP, priority=1, block=True, rule=whitelist_rule)
@ckdj.handle()
async def ckdj_handle(arg: Message = CommandArg()):
    dj_name = str(arg)
    standard_item = get_alias_name(dj_name, item, item_aliases)
    if(standard_item in item):
        await ckdj.finish(standard_item+":\n"+item[standard_item][2])
    else:
        await ckdj.finish("请输入正确的道具名称哦！", at_sender=True)