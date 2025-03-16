from nonebot.adapters.onebot.v11 import MessageSegment, Message
from nonebot.adapters.onebot.v11 import GROUP
from nonebot.adapters.onebot.v11 import Bot, Event, GroupMessageEvent
from nonebot import on_command, on_fullmatch
from nonebot.params import CommandArg
#加载读取系统时间相关
import time
import datetime
#加载数学算法相关
import random
import json
from pathlib import Path
from .config import *
from .list1 import *
from .list2 import *
from .list3 import *
from .list4 import *
from .function import *
from .whitelist import whitelist_rule

__all__ = [
    "ticket",
    "dubo",
]

# 用户数据文件路径
full_path = Path() / "data" / "UserList" / "UserData.json"
bar_path = Path() / "data" / "UserList" / "bar.json"

########赌场系统#######

#买刮刮乐
ticket = on_fullmatch(['.ggl', '。ggl'], permission=GROUP, priority=1, block=True, rule=whitelist_rule)
@ticket.handle()
async def ticket_handle(event: GroupMessageEvent):

    current_time = datetime.datetime.now().time()
    hour = current_time.hour
    #if(hour > 5 and hour < 18): await ticket.finish("棋牌室的门已经关了")

    #打开文件
    data = open_data(full_path)
    bar_data = open_data(bar_path)

    user_id = str(event.get_user_id())
    group_id = str(event.group_id)
    # 添加全局冷却
    all_cool_time(cd_path, user_id, group_id)
    #判断是否开辟event事件栏
    if(not 'event' in data[str(user_id)]):
        data[str(user_id)]['event'] = 'nothing'
    #判断是否有强制次数随机
    if(not 'compulsion_count' in data[str(user_id)]):
        data[str(user_id)]['compulsion_count'] = 0
    if(str(user_id) in data):
        if(data[str(user_id)]['event']!='nothing'):
            if data[str(user_id)]['event']!='compulsion_ggl':
                await ticket.finish("你还有正在进行中的事件", at_sender=True)
        #一些啥都干不了的buff
        if(data[str(user_id)].get('buff')=='lost'): 
            await ticket.finish(f"你现在正在迷路中，连路都找不到，怎么刮刮乐呢？", at_sender=True)
        if(data[str(user_id)].get('buff')=='confuse'): 
            await ticket.finish(f"你现在正在找到了个碎片，疑惑着呢，不能刮刮乐。", at_sender=True)
        if(data[str(user_id)].get('buff')=='hurt'): 
            await ticket.finish(f"你现在受伤了，没有精力刮刮乐！", at_sender=True)

        if(data[str(user_id)]['berry'] >= 0):
            menpiao = 150
            berry = 50
            rnd = random.randint(1,100)
            if rnd <= 4:
                berry = 800
            elif rnd > 5 and rnd <= 15:
                berry = 400
            elif rnd > 15 and rnd <= 35:
                berry = 233
            elif rnd > 35 and rnd <= 75:
                berry = 100
            elif rnd > 75 and rnd <= 100:
                berry = 66
            #特别的对于藏品的判定
            if (rnd == 5):
                #判断是否开辟藏品栏
                if(not 'collections' in data[str(user_id)]):
                    data[str(user_id)]['collections'] = {}
                
                #是否已经持有藏品"奇想魔盒"
                #如果没有，则添加
                if(not '奇想魔盒' in data[str(user_id)]['collections']):
                    data[str(user_id)]['collections']['奇想魔盒'] = 1
                    #写入文件
                    with open(user_path / file_name, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=4)
                    await ticket.send(f"你交了{menpiao}颗草莓，进行了一个刮刮颗，获得一个奇怪的黑色小盒子！\n输入.cp 奇想魔盒 以查看具体效果", at_sender=True)
                #否则正常获得600草莓
                else:
                    berry = 800

            tax = berry * 25 // 100  # 计算 25%
            berry_real = berry - tax  # 减去 25%
            get_berry = berry_real - menpiao # 总共获得的草莓数量
            
            data[str(user_id)]['berry'] += get_berry
            # 初始化pots
            bar_data.setdefault("pots", 0)

            # 加入奖池
            bar_data["pots"] += tax
            msg = f"- 你花了{menpiao}颗草莓，购买了一张刮刮乐！\n-本次刮刮乐你获得{berry}颗草莓！\n- 但是由于草莓税法的实行，需要上交25%，所以你最终获得{berry_real}颗草莓，上交了{tax}颗草莓税！"
            if data[str(user_id)]['event']=='compulsion_ggl' and data[str(user_id)]['compulsion_count']!= 0:
                data[str(user_id)]['compulsion_count'] -= 1
                if data[str(user_id)]['compulsion_count']!= 0:
                    msg += f"\n你现在仍需强制刮刮乐{data[str(user_id)]['compulsion_count']}次。"
                else:
                    # 清除状态
                    data[str(user_id)]['event'] = "nothing"
                    data[str(user_id)]['compulsion_count'] = 0
                    msg += '\n你已经完成了黑帮布置的任务……现在你可以离开这个酒馆了。'
            if data[user_id]['berry'] < 0:
                data[user_id]['berry'] -= 250
                msg += f"\n\n哎呀，你负债进行了刮刮乐，并且没有赚回来！现在作为惩罚我要再扣除你250草莓，并且在抓回正数之前你无法使用道具，无法祈愿，无法进行pvp竞技！买卖蓝莓也是不允许的！\n\n你现在拥有的草莓数量为：{data[user_id]['berry']}颗！"
                if data[str(user_id)]['event']=='compulsion_ggl' and data[str(user_id)]['compulsion_count']!= 0:
                    data[str(user_id)]['event']=='nothing'
                    data[str(user_id)]['compulsion_count']= 0
                    data[user_id]['berry'] -= 300
                    msg += f"\n\n哇！你似乎在负债过程中还得强制刮刮乐啊……你抵押了300草莓作为担保，现在黑衣人放你出酒馆了！"
            #写入文件
            save_data(user_path / file_name, data)
            save_data(bar_path, bar_data)

            await ticket.finish(msg, at_sender=True)
        else:
            await ticket.finish(f"你现在仍在负债中……还想继续刮刮乐？你只有{str(data[str(user_id)]['berry'])}颗草莓！", at_sender=True)
    else:
        await ticket.finish("你还没尝试抓过madeline......", at_sender=True)

#5人场赌博
dubo = on_command('du', permission=GROUP, priority=1, block=True, rule=whitelist_rule)
@dubo.handle()
async def dubo_handle(event: GroupMessageEvent, arg: Message = CommandArg()):
    await dubo.finish("du场出bug，我懒得修，直接封", at_sender=True)

    # person_num = 5  #一局最多人数

    # user_id = event.get_user_id()
    # group = event.group_id

    # current_time = datetime.datetime.now().time()
    # hour = current_time.hour
    # if(hour > 5 and hour < 18): await dubo.finish("棋牌室的门已经关了")

    # #打开用户文件
    # data = {}
    # with open(user_path / file_name, 'r', encoding='utf-8') as f:
    #     data = json.load(f)

    # #打开赌场信息文件
    # data_du = {}
    # with open(duchang_list, 'r', encoding='utf-8') as f:
    #     data_du = json.load(f)

    # if(str(user_id) in data):

    #     #一些啥都干不了的buff
    #     if(data[str(user_id)].get('buff')=='lost'): 
    #         await ticket.finish(f"你现在正在迷路中，连路都找不到，怎么du呢？", at_sender=True)
    #     if(data[str(user_id)].get('buff')=='confuse'): 
    #         await ticket.finish(f"你现在正在找到了个碎片，疑惑着呢，不能du。", at_sender=True)
    #     if(data[str(user_id)].get('buff')=='hurt'): 
    #         await ticket.finish(f"你现在受伤了，没有精力du！", at_sender=True)

    #     want_madeline = str(arg).lower()

    #     nums = find_madeline(want_madeline)

    #     if(nums==0): return

    #     #如果不是du池里的madeline就被踢出
    #     if(str(group) in data_du):
    #         if(nums[2]!=data_du[str(group)]['lc']):
    #             await dubo.finish("当前局du不了这个madeline", at_sender=True)       

    #     #打开副数据表
    #     with open(user_path / f"UserList{nums[2]}.json", 'r', encoding='utf-8') as f:
    #         data2 = json.load(f)
    #     #没有开通猎场的判定
    #     if(not str(user_id) in data2):
    #         await dubo.finish(f"你现在du不了{nums[2]}号猎场的madeline，请至少拥有该猎场的一个madeline", at_sender=True)

    #     #加入赌场
    #     if(not str(group) in data_du):
    #         data_du[str(group)] = {}
    #         data_du[str(group)]['lc'] = nums[2]
    #         data_du[str(group)]['person'] = 0
    #         data_du[str(group)]['member'] = []
    #         data_du[str(group)]['want'] = []
    #     else:
    #         if(nums[2]!=data_du[str(group)]['lc']):
    #             await dubo.finish("当前局du不了这个madeline", at_sender=True)

    #     if(not user_id in data_du[str(group)]['member']):

    #         if(data[str(user_id)]['berry'] < 20):
    #             await dubo.finish("你需要花费20草莓进入该局，你的草莓不够了")

    #         data_du[str(group)]['person'] += 1   #加入一人
    #         data_du[str(group)]['member'].append(user_id)

    #         if(nums[2]=='1'):
    #             data_du[str(group)]['want'].append(want_madeline)
    #         else:
    #             data_du[str(group)]['want'].append(nums[0]+'_'+nums[1])

    #         data[str(user_id)]['berry'] -= 20
    #         with open(user_path / file_name, 'w', encoding='utf-8') as f:
    #             json.dump(data, f, indent=4)

    #     else:
    #         await dubo.finish("你已经加入该局啦！", at_sender=True)

    #     #如果满5个人了就开赌
    #     if(data_du[str(group)]['person'] >= person_num):
    #         msg = ""  #消息段
    #         point = []
    #         #给出5个点数
    #         for i in range(person_num):
    #             point.append(random.randint(10000, 20000))

    #         #对副数据表进行修改
    #         data = data2
            
    #         #根据点数大小来决定数据交换
    #         for i in range(person_num):
    #             self_id = data_du[str(group)]['member'][i]
    #             for j in range(person_num):
    #                 if(point[j]<point[i]):
    #                     #查询输家的ID
    #                     other_id = data_du[str(group)]['member'][j]
    #                     #查询赢家想要的madeline
    #                     k = data_du[str(group)]['want'][i]

    #                     #若有则进行分配
    #                     if(data[str(other_id)].get(k,0) > 0):
    #                         #对手减少madeline
    #                         data[str(other_id)][k] -= 1
    #                         #你增加madeline
    #                         if(not k in data[str(self_id)]): data[str(self_id)][k] = 0
    #                         data[str(self_id)][k] += 1
    #                         #增加消息段
    #                         msg += MessageSegment.at(self_id)
    #                         msg += "获得了"
    #                         msg += MessageSegment.at(other_id)
    #                         if(nums[2]!='1'):
    #                             k = k.split('_')
    #                             k = eval(f"madeline_data{nums[2]}.get(k[0]).get(k[1]).get('name')")
    #                         msg += f"的{k}一个\n"

    #                         break  #结束该循环

        
    #         #写入文件
    #         del data_du[str(group)]

    #         with open(duchang_list, 'w', encoding='utf-8') as f:
    #             json.dump(data_du, f, indent=4)

    #         #更新用户数据文件
    #         with open(user_path / f"UserList{nums[2]}.json", 'w', encoding='utf-8') as f:
    #             json.dump(data, f, indent=4)             

    #         #发送消息
    #         await dubo.send("正在结算本场赌局.....")  #加载消息

    #         # time.sleep(3)    #延时三秒

    #         if(msg==""): await dubo.finish("本局没有人得到任何东西。")
    #         await dubo.finish(msg)

    #     else:

    #         #写入用户主文件
    #         with open(user_path / file_name, 'w', encoding='utf-8') as f:
    #             json.dump(data, f, indent=4)

    #         #写入文件
    #         with open(duchang_list, 'w', encoding='utf-8') as f:
    #             json.dump(data_du, f, indent=4)

    #         await dubo.finish(f"成功进入该局！当前共{data_du[str(group)]['person']}人，本局du池为猎场{data_du[str(group)]['lc']}", at_sender=True)


    # else:
    #     await dubo.finish("你还没尝试抓过madeline......", at_sender=True)
