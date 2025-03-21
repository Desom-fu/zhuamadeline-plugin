from nonebot.adapters.onebot.v11 import MessageSegment, Message
from nonebot.adapters.onebot.v11 import GROUP
from nonebot.adapters.onebot.v11 import Bot, Event, GroupMessageEvent
from nonebot import on_command, on_fullmatch, get_bots
from nonebot.params import CommandArg
from nonebot.log import logger

#导入定时任务库
from nonebot import require
require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

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
    "rule",
    "bet",
    "guess",
    "demon_default"
]

# 用户数据文件路径
full_path = Path() / "data" / "UserList" / "UserData.json"
bar_path = Path() / "data" / "UserList" / "bar.json"
demon_path = Path() / "data" / "UserList" / "demon.json"
pvp_path = Path() / "data" / "UserList" / "pvp.json"

#--------------------bet游戏-------------------------

# “游戏”规则命令
rule = on_command('rule', permission=GROUP, priority=1, block=True, rule=whitelist_rule)

@rule.handle()
async def rule_handle(bot: Bot, event: GroupMessageEvent, arg: Message = CommandArg()):
    game_type = str(arg)  # 获取玩家请求的“游戏”编号
    if game_type == '1':
        await rule.finish(
            "“游戏”1：预言大师(1人)\n" +
            "- 本“游戏”入场费为125草莓\n" +
            "- “游戏”开始时系统会为你从52张扑克牌（除去大小王）中随机抽取一张，你要做的就是猜测这一张牌\n" +
            "- 你的猜测可以是点数、大于/小于某值，或者具体的花色\n" +
            "- 如果猜对了，你将获得大量草莓奖励！祝你好运~\n" +
            "- 输入.bet 1 游玩此“游戏”"
        )
    elif game_type == '2':
        await rule.finish(
            "“游戏”2：恶魔轮盘du(2人)\n" +
            "- 本“游戏”入场费为125草莓\n" +
            "- “游戏”开始时，双方的血量在区间内随机（上限为6），并且都可以获得等量道具，然后由随机一人开始\n" +
            "- 在枪里面有不定量的子弹，实弹空弹随机\n" +
            "- 你可以向自己开枪，也可以向对方开枪，向自己开枪后无论是否实弹下一回合都是你行动\n" +
            "- 如果你向对方开枪，无论是否实弹都是对方行动\n" +
            "- 在回合内，每个人都可以使用道具，道具内容可以使用 .恶魔道具 查看\n" +
            "- 获胜的一方将获得388颗草莓奖励~\n" +
            "- 注意！步时为10min，使用道具和开枪（无论是否自己）都会刷新步时！若超时对方返还草莓，本回合玩家不返还！\n" +
            "- 使用 .恶魔帮助 指令可以查看所有的指令~ \n" +
            "- 输入 .bet 2 游玩此“游戏”"
        )
    elif game_type == '3':
        await rule.finish(
            "“游戏”3：Madeline竞技场竞猜\n" +
            "- 本“游戏”入场费为150草莓\n" +
            "- 用 `.bet 3/擂台号码` 竞猜一个擂台，当该擂台的玛德琳被踢下或替换时，你会得到（120-原擂主常驻战力）*原擂主存活回合数*1/6的奖励。\n" +
            "- 如果本局擂台结束，将给所有参与竞猜的玩家发对应的草莓，并存储在du场里！请通过 `.ck` 查看哦！\n" +
            "- 可以使用命令 `.bank take 数量/all` 从du场中提取草莓哦！\n"+
            "- 你在竞猜的时候同时也能玩其他“游戏”哦！\n" +
            "- 注意1：每局Madeline竞技场只能使用竞猜一次！\n" +
            "- 注意2：不能对在场超过5回合的玛德琳下注"
        )
    elif game_type == '4':
        await rule.finish(
            "“游戏”4：三球竞猜\n" +
            "- 本“游戏”入场费为50-300草莓（随奖池变化），入场费计入奖池！\n" +
            "- 本“游戏”开放时间为每天的6:00 - 22:00！\n" +
            "- 在开放时间内，使用 `.bet 4/红色球数字(1-10)/蓝色球数字(1-10)/黄色球数字(1-10)` 来进行押注哦！\n" +
            "- 每天的 22:30 将会开奖，若有人三球对应号码均匹配，将直接获得奖池的最少50%的份额哦！若双球匹配，将获得最少10%的份额哦！如果多人同时中奖，将平分当前份额的奖池哦！\n" +
            "- 如果只猜中一个也不用担心，也有小奖！小奖的金额是入场费的150%！\n"+
            "- 你在竞猜的时候同时也能玩其他“游戏”哦！"
        )
    else:
        await rule.finish("请输入正确的“游戏”编号，例如.rule 1", at_sender=True)

# 地下酒馆 - “游戏”判定
bet = on_command('bet', permission=GROUP, priority=1, block=True, rule=whitelist_rule)

@bet.handle()
async def bet_handle(bot: Bot, event: GroupMessageEvent, arg: Message = CommandArg()):
    # 打开文件
    data = open_data(full_path)
    demon_data = open_data(demon_path)
    bar_data = open_data(bar_path)
    user_id = str(event.get_user_id())  # 获取玩家ID
    group_id = str(event.group_id)
    nick_name = event.sender.nickname
    current_time = int(time.time())  # 当前时间戳
    args = str(arg)
    game_type_split = args.strip().split("/")  # 按 "/" 分割输入
    # 查找游戏类型
    game_type = game_type_split[0] if len(game_type_split) > 0 else args
    second_game_type = game_type_split[1] if len(game_type_split) > 1 else False
    third_game_type = game_type_split[2] if len(game_type_split) > 2 else False
    forth_game_type = game_type_split[3] if len(game_type_split) > 3 else False

    # 如果该用户不在用户名单中，则先抓
    if user_id not in data:
        if(not 'berry' in data[str(user_id)]):
            data[user_id]['berry'] = 1000
            # 写入数据
            save_data(full_path, data)
        await bet.finish("请先抓一次madeline再来玩“游戏”哦！", at_sender=True)
    #debuff清除逻辑
    debuff_clear(data,user_id)
    # 如果该用户不在酒馆名单中，则先创建数据
    if user_id not in bar_data:
        bar_data[user_id] = {}
        bar_data[user_id]['status'] = 'nothing'
    # 添加全局冷却
    all_cool_time(cd_path, user_id, group_id)
    #一些啥都干不了的buff
    #判断是否开辟event事件栏
    if(not 'event' in data[str(user_id)]):
        data[str(user_id)]['event'] = 'nothing'
    #判断是否有强制次数随机
    if(not 'compulsion_count' in data[str(user_id)]):
        data[str(user_id)]['compulsion_count'] = 0
        
    if(data[str(user_id)]['event']!='nothing' and game_type != "2"):
        if data[str(user_id)]['event']!='compulsion_bet1':
            await bet.finish("你还有正在进行中的事件", at_sender=True)
            
    if(data[str(user_id)].get('buff','normal')=='lost') and game_type != "2": 
        await bet.finish(f"你现在正在迷路中，连路都找不到，怎么能玩“游戏”呢？", at_sender=True)
        
    if(data[str(user_id)].get('buff','normal')=='confuse' ) and game_type not in ["2","4"]: 
        await bet.finish(f"你现在正在找到了个碎片，疑惑着呢，不能玩“游戏”。", at_sender=True)
        
    if(data[str(user_id)].get('buff','normal')=='hurt') and game_type != "2": 
        await bet.finish(f"你现在受伤了，没有精力玩“游戏”！", at_sender=True)
        
    if(data[str(user_id)].get('status','nornal')=='working' and game_type not in ["2","4"]): 
        await bet.finish(f"你正在维护草莓加工器中，没有精力玩大部分“游戏”！", at_sender=True)
    # 如果该用户不在酒馆名单中，则先创建数据
    if user_id not in bar_data:
        bar_data[user_id] = {}
        bar_data[user_id]['status'] = 'nothing'

    if bar_data[user_id]['status'] != 'nothing' and game_type not in ['3','4']:
        await bet.finish("你已经在玩“游戏”了，请结束本局“游戏”再进行游玩新的“游戏”哦！", at_sender=True)

    if game_type == '1' and not '/' in args:
        if data[user_id]['berry'] < 0:
            await bet.finish(f"你现在仍在负债中……还想继续bet1？你只有{str(data[str(user_id)]['berry'])}颗草莓！", at_sender=True)

        cooldown_time = 2 * 60  # 2 分钟冷却时间
        # 事件中bet1无冷却
        if data[str(user_id)]['event']=='compulsion_bet1' and data[str(user_id)]['compulsion_count']!= 0:
            cooldown_time = 0
        if user_id in data:
            # 检查是否有冷却时间记录
            last_bet_time = data[user_id].get('last_bet_time', 0)
            time_left = cooldown_time - (current_time - last_bet_time)

            if time_left > 0:
                await bet.finish(
                    f"请冷静一会！距离下次游玩还要{time_left // 60}分钟{time_left % 60}秒。",
                    at_sender=True
                )
        # 更新用户的最后游戏时间
        data[user_id]['last_bet_time'] = current_time

        # 将玩家添加至“游戏”状态
        bar_data[user_id]['game'] = '1'
        bar_data[user_id]['status'] = 'beting'

        # 写入数据
        save_data(full_path, data)
        save_data(bar_path, bar_data)
        
        message = ("发牌已完成，请选择如下指令中的一条进行猜测。\n" +
            "输入.猜测 大于7/小于7 以猜测该牌是否大于7/小于7，猜测正确可以获得少量奖励！\n" +
            "输入.猜测 梅花/方片/黑桃/红桃 以猜测该牌的花色，猜测正确可以获得中量奖励！\n" +
            "输入.猜测 (任意两个数字，用/分隔，如10/Q) 以猜测该牌是否为这两个点数，猜测正确可以获得大量奖励！")
        
        # 破产提醒
        if data[user_id]['berry'] < 125:
            message += "\n\n记得检查一下……你的草莓数量是否足够支撑呢？"

        await bet.finish(message, at_sender=True)
        
    elif game_type == '2' and not '/' in args:
        # 获取当前时间戳
        current_time = int(time.time())

        # 确保 'demon_data' 和 'group_id' 存在
        # 初始化 group_id 中的游戏数据
        if group_id not in demon_data:
            demon_data[group_id] = demon_default
            save_data(demon_path, demon_data)
        # 检查是否有冷却时间，如果没有设置，默认为 0
        demon_coldtime = demon_data[group_id].get('demon_coldtime', 0)

        # 检查全局冷却时间
        if current_time < demon_coldtime:
            remaining_time = demon_coldtime - current_time
            await bet.finish(
                f"恶魔轮盘du处于冷却中，请晚点再来吧！剩余冷却时间：{remaining_time // 60}分钟{remaining_time % 60}秒。",
                at_sender=True
            )

        # 检查游戏是否已经开始，如果已经开始，禁止其他玩家加入
        if demon_data[group_id]['start']:
            await bet.finish("游戏已开始，无法加入！")
        if data[user_id]['berry'] < 125:
            await bet.finish("你需要有至少125草莓才能进来玩哦", at_sender=True)
        else:
            data[user_id]['berry'] -= 125
        # 将玩家添加至“游戏”状态
        bar_data[user_id]['game'] = '2'
        bar_data[user_id]['status'] = 'demon'
        # 判断玩家是否为第一位或第二位加入
        if len(demon_data[group_id]['pl']) == 0:
            # 第一位玩家加入
            demon_data[group_id]['pl'].append(user_id)
            demon_data[group_id]['turn_start_time'] = current_time
            # 写入数据
            save_data(full_path, data)
            save_data(bar_path, bar_data)
            save_data(demon_path, demon_data)
            await bet.finish(f"玩家 {nick_name} 加入游戏，等待第二位玩家加入。", at_sender=True)

        elif len(demon_data[group_id]['pl']) == 1:
            # 第二位玩家加入前检查是否已经加入
            if user_id in demon_data[group_id]['pl']:
                await bet.finish(f"你已经加入了游戏，无需重复加入！", at_sender=True)
            # 第二位玩家加入，初始化游戏
            demon_data[group_id]['pl'].append(user_id)
            # 游戏开始标志
            demon_data[group_id]['start'] = True
            add_max = 0
            # 膀胱加成
            pangguang_add = 0
            # 获取两个玩家的身份状态
            player_ids = [str(demon_data[group_id]['pl'][i]) for i in range(2)]
            identity_status_list = [data.get(player_id, {}).get("identity_status", 0) for player_id in player_ids]

            # 如果两个玩家的身份状态不同
            if identity_status_list[0] != identity_status_list[1]:
                identity_found = random.choice(identity_status_list)  # 随机选择一个状态，50% 概率选择其中一个
            else:
                identity_found = identity_status_list[0]  # 如果两个状态相同，直接选择该状态
            # 更新身份状态
            demon_data[group_id]['identity'] = identity_found
            idt_len = len(item_dic2)
            if identity_found == 1:
                add_max = 2
                idt_len = 0
            elif identity_found in [2,999]:
                add_max = 2
                pangguang_add = 2
                idt_len = 0
            # 设置玩家血量，随机生成血量值(放在上面后面好改)
            hp = random.randint(3 + int(add_max*2-1) + pangguang_add, 6+add_max*2 + pangguang_add)
            demon_data[group_id]['hp'] = [hp, hp]
            # 设定轮数
            demon_data[group_id]['game_turn'] = 1
            # 设定血量上限
            demon_data[group_id]['hp_max'] = 6 + add_max*2 + pangguang_add
            # 设定道具上限
            demon_data[group_id]['item_max'] = 6 + add_max + pangguang_add
            # 加载弹夹状态
            demon_data[group_id]['clip'] = load()
            # 设定无限叠加攻击默认值
            demon_data[group_id]['add_atk'] = False
            # 随机决定先手玩家
            demon_data[group_id]['turn_start_time'] = int(time.time())
            demon_data[group_id]['turn'] = random.randint(0, 1)
            # 随机生成道具并分配给两位玩家
            player0 = str(demon_data[group_id]['pl'][0])
            player1 = str(demon_data[group_id]['pl'][1])
            # 跑团状态指定第一个玩家先手，全局变量可随便改
            if int(player0) == kp_pl:
                demon_data[group_id]['turn'] = 0
            for i in range(random.randint(1 + add_max//2 + pangguang_add//2, 4 + add_max//2)):
                demon_data[group_id]['item_0'].append(get_random_item(identity_found, len(item_dic) - idt_len, player0))  # 玩家1的道具
                demon_data[group_id]['item_1'].append(get_random_item(identity_found, len(item_dic) - idt_len, player1))  # 玩家2的道具
            # 生成道具信息
            item_0 = ", ".join(item_dic.get(i, "未知道具") for i in demon_data[group_id]['item_0'])
            item_1 = ", ".join(item_dic.get(i, "未知道具") for i in demon_data[group_id]['item_1'])
            # 获取玩家道具信息
            items_0 = demon_data[group_id]['item_0']  # 玩家0道具列表
            items_1 = demon_data[group_id]['item_1']  # 玩家1道具列表
            # 发送初始化消息
            msg = "恶魔轮盘du，开局!\n"
            msg += "- 本局模式："
            if identity_found == 1:
                msg += "身份模式\n\n"
            elif identity_found in [2,999]:
                msg += "急速模式\n\n"
            else:
                msg += "正常模式\n\n"
            msg += MessageSegment.at(player0) + f"\n道具({len(items_0)}/{demon_data[group_id]['item_max']})：" +f"\n{item_0}\n\n"
            msg += MessageSegment.at(player1) + f"\n道具({len(items_1)}/{demon_data[group_id]['item_max']})：" +f"\n{item_1}\n\n"
            msg += f"- 双方hp:{str(hp)}/{demon_data[group_id]['hp_max']}\n"
            msg += f"- 总弹数{str(len(demon_data[group_id]['clip']))}，实弹数{str(demon_data[group_id]['clip'].count(1))}\n"
            pid = demon_data[group_id]['pl'][demon_data[group_id]['turn']]
            msg += "- 当前是"+ MessageSegment.at(pid) + "的回合"
            save_data(full_path, data)
            save_data(bar_path, bar_data)
            save_data(demon_path, demon_data)
            await bet.finish(msg)
        else:
            await bet.finish("游戏已开始，无法再次加入！")
    elif game_type == '3':
        # 初始化必要字段
        pvp_guess = bar_data[user_id].setdefault('pvp_guess', {})
        bar_data[user_id].setdefault('last_pvp_guess_berry', 0)
        bar_data[user_id].setdefault('bank', 0)
        # 判断本轮是否猜测
        if pvp_guess.get('ifguess', 0) == 1:
            await bet.finish("本轮你已经猜测过擂台了，不能再猜测了哦！", at_sender=True)
        # 检测指令
        if not second_game_type:
            await bet.finish("请输入正确的指令哦！正确指令为 `.bet 3/擂台号`", at_sender=True)

        # 检测输入是否合法
        if not second_game_type.isdigit() or not (1 <= int(second_game_type) <= 10):
            await bet.finish("请输入正确的猜测擂台号！1~10 之间哦！", at_sender=True)
        # 转换座位号
        pos = int(second_game_type) - 1
            
        pvp_data = open_data(pvp_path)
        # 检测是否为空
        if not pvp_data:
            await bet.finish("当前Madeline竞技暂未开始哦，无法进行猜测！", at_sender=True)
        # 检测是否存在该擂台
        try:
            pvp_choose = pvp_data['list'][pos]
        except:
            await bet.finish(f"目前暂无此擂台哦！", at_sender=True)
        # 获取轮数
        turn = pvp_data.get('count', 100)
        choose_user = int(pvp_data['list'][pos][0])
        choose_user_name = await bot.get_group_member_info(group_id=int(group_id), user_id=choose_user)
        choose_nickname = choose_user_name["card"] or choose_user_name["nickname"]  # 先取群昵称（card），没有则取QQ昵称
        # 目标战力和目标轮数    
        choose_rank = pvp_choose[3]
        choose_turn = pvp_choose[5]
        if choose_turn <= 10:
            choose_turn = 10
        # 设定超过多少回合不能选
        overtake = 5
        # 判定是否超过
        if turn - overtake > choose_turn:
            await bet.finish(f"你所选的擂台的上台回合为[{pvp_choose[5]}]，当前回合为[{turn}]，已经上台超过{overtake}回合了哦，请选择其他擂台哦！", at_sender=True)
        # 填入擂台，战力，轮数，以及本轮已猜的判定标准
        pvp_guess['ifguess'] = 1 # 1为已猜，0为未猜
        pvp_guess['pos'] = pos
        pvp_guess['choose_rank'] = choose_rank
        pvp_guess['choose_turn'] = pvp_choose[5] # 不能用choose_turn
        pvp_guess['choose_nickname'] = choose_nickname
        # 上轮猜测清零
        bar_data[user_id]['last_pvp_guess_berry'] = 0
        # 扣除草莓
        kouchu_berry = 150
        if data[user_id]['berry'] < kouchu_berry:
            await bet.finish(f"你需要有至少{kouchu_berry}颗草莓才能进行竞技场猜测哦！", at_sender=True)
        else:
            data[user_id]['berry'] -= kouchu_berry
        save_data(bar_path, bar_data)
        save_data(full_path, data)
        # 上台回合只能写pvp_choose[5]以防显示错误
        await bet.finish(f"你已经消耗{kouchu_berry}颗草莓成功进行竞技场猜测！你所选的擂台为[{pos+1}]，该擂台擂主为[{choose_nickname}]，上台回合为[{pvp_choose[5]}]，所选占擂Madeline的战力为[{choose_rank}]！", at_sender=True)
    # “游戏”4逻辑：三球竞猜
    elif game_type == '4':
        if len(game_type_split) != 4:
            await bet.finish("请输入正确的红蓝黄三球的号码哦！", at_sender=True)
            
        try:
            red_points = int(second_game_type)
            blue_points = int(third_game_type)
            yellow_points = int(forth_game_type)
        except ValueError:
            await bet.finish("请输入正确的红蓝黄三球的号码哦！", at_sender=True)
        
        if not (1 <= red_points <= 10) or not (1 <= blue_points <= 10):
            await bet.finish("红蓝黄三球的号码只能是1-10之间哦！", at_sender=True)
        
        # 获取当前时间
        current_time = datetime.datetime.now()
        current_hour = current_time.hour
        
        # 不在开放时间内，不开放
        if not (6 <= current_hour < 22):
             await bet.finish("当前不在三球竞猜开放时间（6:00 - 22:00）内，无法进行三球竞猜哦！", at_sender=True)
    
        # 获取用户数据
        user_bar = bar_data.setdefault(user_id, {})
        user_double_ball = user_bar.setdefault('double_ball', {})
    
        # 检查是否已经玩过
        if user_double_ball.get("ifplay") == 1:
             await bet.finish("你今天已经已经猜测过了，无法重复进行哦！", at_sender=True)
    
        # 读取奖池
        pots = bar_data.setdefault("pots", 0)
        if not isinstance(pots, int) or pots < 0:
            pots = 0  # 确保 pots 是有效数值
    
        # 获取门票费用
        ticket_cost = reward_amount(pots)
    
        # 扣除门票费用
        if data.get(user_id, {}).get("berry", 0) < ticket_cost:
             await bet.finish(f"你的草莓数量不足！需要{ticket_cost}颗草莓。", at_sender=True)
    
        data[user_id]["berry"] -= ticket_cost
        bar_data["pots"] += ticket_cost
    
        # 记录游戏数据
        user_double_ball["ticket_cost"] = ticket_cost
        user_double_ball["red_points"] = int(red_points)
        user_double_ball["blue_points"] = int(blue_points)
        user_double_ball["yellow_points"] = int(yellow_points)
        user_double_ball["ball_prize"] = 0
        user_double_ball["refund"] = 0
        user_double_ball["ifplay"] = 1
        user_double_ball['guess_date'] = datetime.datetime.now().strftime("%Y-%m-%d")

        save_data(bar_path, bar_data)
        save_data(full_path, data)
        await bet.finish(f"你已成功参与三球竞猜！本次入场费用：{ticket_cost}颗草莓。\n你竞猜的红色球点数：{red_points}，蓝色球点数：{blue_points}，黄色球点数：{yellow_points}", at_sender=True)
    else:
        await bet.finish("请输入正确的游戏类型哦！", at_sender=True)

# “游戏”1逻辑 - 猜测
guess = on_command('猜测', permission=GROUP, priority=1, block=True, rule=whitelist_rule)
@guess.handle()
async def guess_handle(bot: Bot, event: GroupMessageEvent, arg: Message = CommandArg()):
    # 打开文件
    data = open_data(full_path)
    user_id = str(event.get_user_id())  # 获取玩家ID
    group_id = str(event.group_id)

    bar_data = open_data(bar_path)
    # 添加全局冷却
    all_cool_time(cd_path, user_id, group_id)
    #判断是否开辟event事件栏
    if(not 'event' in data[str(user_id)]):
        data[str(user_id)]['event'] = 'nothing'
    #判断是否有强制次数随机
    if(not 'compulsion_count' in data[str(user_id)]):
        data[str(user_id)]['compulsion_count'] = 0
    # 判断是否开始了“游戏”
    try:
        game_type = bar_data[user_id]['game']
        game_status = bar_data[user_id]['status']
    except:
        game_type = "-1"
        game_status = "-1"

    if game_type == '1' and game_status == 'beting':
        pass
    else:
        await guess.finish("你似乎没有参与本场“游戏”呢~")
    
    # 扣除门票费
    data[user_id]['berry'] -= 125

    # 构建52张扑克牌集合
    card_collection = []
    for i in range(1, 14):  # 1到13的点数，分别代表A到K
        for _ in range(4):  # 每种点数4张牌
            card_collection.append(i)

    # 随机抽取一张牌
    card_value = random.choice(card_collection)
    card_type = random.choice(["梅花", "方片", "黑桃", "红桃"])

    # 处理特殊牌值
    if card_value == 1:
        card_name = "A"
    elif card_value == 11:
        card_name = "J"
    elif card_value == 12:
        card_name = "Q"
    elif card_value == 13:
        card_name = "K"
    else:
        card_name = str(card_value)

    # 处理玩家猜测
    guess_type = str(arg).split("/")
    REWARD_MAPPING = {
        "大于7": 216,
        "小于7": 216,
        "花色": 400,
        "点数": 650
    }

    if len(guess_type) != 1 and len(guess_type) != 2:
        await guess.finish(message="请输入一个正确的猜测值", at_sender=True)
    elif len(guess_type) == 1:
        guess_type = guess_type[0]
        if guess_type == "大于7":
            original_berry = int(REWARD_MAPPING[guess_type])
            tax = int(original_berry*0.1)
            berry = int(original_berry - tax)
            if card_value > 7:
                data[user_id]['berry'] += berry
                msg_text = f"- 你抽到的牌是{card_type}{card_name}，点数大于7，你的猜测成功了！获得{original_berry}颗草莓奖励！\n- 但是由于草莓税法的实行，需要上交10%，所以你最终获得了{berry}颗草莓，上交了{tax}颗草莓税！"
            else:
                msg_text = f"- 你抽到的牌是{card_type}{card_name}，点数小于等于7，你的猜测失败了！"
        elif guess_type == "小于7":
            original_berry = int(REWARD_MAPPING[guess_type])
            tax = int(original_berry*0.1)
            berry = int(original_berry - tax)
            if card_value < 7:
                data[user_id]['berry'] += berry
                msg_text = f"- 你抽到的牌是{card_type}{card_name}，点数小于7，你的猜测成功了！获得{original_berry}颗草莓奖励！\n- 但是由于草莓税法的实行，需要上交10%，所以你最终获得了{berry}颗草莓，上交了{tax}颗草莓税！"
            else:
                msg_text = f"- 你抽到的牌是{card_type}{card_name}，点数大于等于7，你的猜测失败了！"
        elif guess_type in ["梅花", "方片", "黑桃", "红桃"]:
            send_guess_type = "花色"
            original_berry = int(REWARD_MAPPING[send_guess_type])
            tax = int(original_berry*0.1)
            berry = int(original_berry - tax)
            if card_type == guess_type:
                data[user_id]['berry'] += berry
                msg_text = f"- 你抽到的牌是{card_type}{card_name}，你的猜测成功了！获得{original_berry}颗草莓奖励！\n- 但是由于草莓税法的实行，需要上交10%，所以你最终获得了{berry}颗草莓，上交了{tax}颗草莓税！"
            else:
                msg_text = f"- 你抽到的牌是{card_type}{card_name}，你的猜测失败了！"
        else:
            await guess.finish(message="请输入一个正确的猜测值", at_sender=True)
    elif len(guess_type) == 2:
        send_guess_type = "点数"
        original_berry = int(REWARD_MAPPING[send_guess_type])
        tax = int(original_berry*0.1)
        berry = int(original_berry - tax)
        # 处理用户输入的牌值
        available_type = ["a", "2", "3", "4", "5", "6", "7", "8", "9", "10", "j", "q", "k"]
        for i in range(len(guess_type)):
            if guess_type[i].lower() not in available_type:
                await guess.finish(message="请输入一个正确的牌值", at_sender=True)
            if guess_type[i].lower() == "a":
                guess_type[i] = 1
            elif guess_type[i].lower() == "j":
                guess_type[i] = 11
            elif guess_type[i].lower() == "q":
                guess_type[i] = 12
            elif guess_type[i].lower() == "k":
                guess_type[i] = 13
            else:
                guess_type[i] = int(guess_type[i])
        if card_value in guess_type:
            rnd = random.randint(1,15)
            if rnd <= 2:
                #判断是否开辟藏品栏
                if(not 'collections' in data[str(user_id)]):
                    data[str(user_id)]['collections'] = {}
                #是否已经持有藏品"奇想扑克"
                #如果没有，则添加
                if(not '奇想扑克' in data[str(user_id)]['collections']):
                    data[str(user_id)]['collections']['奇想扑克'] = 1
                    msg_text = f"你抽到的牌是{card_type}{card_name}，你的猜测成功了！你在酒馆的桌子地下看到了一副奇怪的白色扑克，你将这副扑克捡了起来\n输入.cp 奇想扑克 以查看具体效果"
                else:
                    data[user_id]['berry'] += berry
                    msg_text = f"你抽到的牌是{card_type}{card_name}，你的猜测成功了！获得{original_berry}颗草莓奖励！但是由于草莓税法的实行，需要上交10%，所以你最终获得了{berry}颗草莓，上交了{tax}颗草莓税！"    
            else:                
                data[user_id]['berry'] += berry
                msg_text = f"你抽到的牌是{card_type}{card_name}，你的猜测成功了！获得{original_berry}颗草莓奖励！但是由于草莓税法的实行，需要上交10%，所以你最终获得了{berry}颗草莓，上交了{tax}颗草莓税！"
        else:
            msg_text = f"你抽到的牌是{card_type}{card_name}，你的猜测失败了！"
    if data[str(user_id)]['event']=='compulsion_bet1' and data[str(user_id)]['compulsion_count']!= 0:
        data[str(user_id)]['compulsion_count'] -= 1
        if data[str(user_id)]['compulsion_count']!= 0:
            msg_text += f"\n你现在仍需强制进行预言大师{data[str(user_id)]['compulsion_count']}次。"
        else:
            # 清除状态
            data[str(user_id)]['event'] = "nothing"
            data[str(user_id)]['compulsion_count'] = 0
            msg_text += '\n你已经完成了黑帮布置的任务……现在你可以离开这个酒馆了。'
    # 写入主数据表
    bar_data[user_id]['status'] = 'nothing'
    # 初始化pots
    bar_data.setdefault("pots", 0)
    # 加入奖池
    bar_data["pots"] += tax
    if data[user_id]['berry'] < 0:
        data[user_id]['berry'] -= 250
        msg_text += f"\n\n哎呀，你负债进行了预言大师，并且没有赚回来！现在作为惩罚我要再扣除你250草莓，并且在抓回正数之前你无法使用道具，无法祈愿，无法进行pvp竞技！买卖蓝莓也是不允许的！\n\n你现在拥有的草莓数量为：{data[user_id]['berry']}颗！"
        if data[str(user_id)]['event']=='compulsion_bet1' and data[str(user_id)]['compulsion_count']!= 0:
            data[str(user_id)]['event']=='nothing'
            data[str(user_id)]['compulsion_count']= 0
            data[user_id]['berry'] -= 300
            msg_text += f"\n\n哇！你似乎在负债过程中还得强制预言大师啊……你抵押了300草莓作为担保，现在黑衣人放你出酒馆了！"

    save_data(full_path, data)
    save_data(bar_path, bar_data)
    await guess.finish(message=msg_text, at_sender=True)

# “游戏2”：恶魔赌局
# 本游戏原设计来自 作者：樱井咲夜 https://forum.olivos.run/d/611 的 Olivos恶魔赌局的插件
# 我将其移植并且进行了大量魔改和添加新道具，进行了消息发送的修改和排版，大量减少了消息量，防止风控
# demon道具列表及相关函数
item_dic1 = {
    1: "桃",
    2: "医疗箱",
    3: "放大镜",
    4: "眼镜",
    5: "手铐",
    6: "欲望之盒",
    7: "无中生有",
    8: "小刀",
    9: "酒",
    10: "啤酒",
    11: "刷新票",
    12: "手套",
    13: '骰子',
    14: "禁止卡",
    15: '墨镜',
    }
# 身份模式道具列表
item_dic2 = { 
    16: '双转团',
    17: '天秤', 
    18: '休养生息',
    19: '玩具枪',
    20: '烈弓',
    21: '血刃',
    22: '黑洞',
    23: '金苹果',
    24: '铂金草莓',
    25: '肾上腺素',
    26: '烈性TNT',
    }

item_dic = item_dic1 | item_dic2

# demon_default
demon_default = {
    "pl": [],
    "hp": [],
    "item_0": [],
    "item_1": [],
    'hcf': 0,
    'clip': [],
    'turn': 0,
    'atk': 0,
    'hp_max': 0,
    'item_max': 0,
    'game_turn': 1,
    'add_atk': False,
    'start': False,
    'identity': 0,
    'demon_coldtime': int(time.time()),
    'turn_start_time': int(time.time())
}

# 定义身份模式死斗回合数方便更改
death_turn = 12
pangguang_turn = 5

# 定义不同状态对应的轮数限制
turn_limit = {
    1: death_turn,  # "死斗模式" 开启的轮数限制
    2: pangguang_turn,    # "膀胱模式" 开启的轮数限制
    999: pangguang_turn    # "跑团专用999模式" 开启的轮数限制
}

# 设定kp必定先手
kp_pl = 1234567890

# 定义道具效果的字典
item_effects = {
    "桃": "回复1点hp",
    "医疗箱": "回复2点hp，但跳过你的这一回合，并且对方的所有束缚解除！",
    "放大镜": "观察下一颗子弹的种类",
    "眼镜": "观察下两颗子弹的种类，但顺序未知",
    "手铐": "跳过对方下一回合（不可重复使用/与禁止卡一同使用）",
    "禁止卡": "跳过对方下1~2（随机）个回合，对方获得禁止卡（若对方道具已达6个上限，将不会获得禁止卡）",
    "欲望之盒": "50%抽取一个道具，30%恢复一点血量（若血量达到上限将赠与一个本轮无视道具上限的桃），20%对对方造成一点伤害",
    "无中生有": "抽取两个道具，然后跳过回合，对方若有束缚，束缚的回合-1！并且无中生有生成的道具直到本轮实弹耗尽前可以超出上限（本轮实弹耗尽后超出上限的道具会消失）！",
    "小刀": "伤害变为2（注：同时使用多个小刀或酒会导致浪费！）",
    "酒": "伤害变为2，同时若hp等于1时，回复1hp（注：同时使用多个小刀或酒会导致浪费！）",
    "啤酒": "退掉下一发子弹（若退掉的是最后一发子弹，进行道具的刷新）",
    "刷新票": "使用后，重新抽取和剩余道具数量相等的道具",
    "手套": "重新换弹，不进行道具刷新",
    "骰子": "你的hp变为1到4的随机值",
    "墨镜": "观察第一颗和最后一颗子弹的种类，但顺序未知",
    "双转团": "（该道具为“身份”模式专属道具）把这个道具转移到对方道具栏里，若对方道具已达上限则丢弃本道具；另外还有概率触发特殊效果？可能会掉血，可能会回血，可能会送给对方道具……但由于其富含identity，可能有其他的非bet2游戏内的效果？",
    "天秤": "（该道具为“身份”模式专属道具）如果你的道具数量≥对方道具数量，你对对方造成一点伤害；你的道具数量<对方道具数量，你回一点血",
    "休养生息": "（该道具为“身份”模式专属道具）自己的hp恢复2，对方的hp恢复1，不跳回合；若对面为满血，则只回一点体力。",
    "玩具枪": "（该道具为“身份”模式专属道具）1/2的概率无事发生，1/2的概率对对面造成1点伤害",
    "烈弓": "（该道具为“身份”模式专属道具）使用烈弓后，下一发子弹伤害+1，且伤害类道具（小刀、酒、烈弓）的加伤效果可以无限叠加！",
    "血刃": "（该道具为“身份”模式专属道具）可以扣除自己1点hp，获得两个道具！并且获得的道具直到本轮实弹耗尽前可以超出上限（本轮实弹耗尽后超出上限的道具会消失）",
    "黑洞": "（该道具为“身份”模式专属道具）召唤出黑洞，随机夺取对方的任意一个道具！\n如果对方没有道具，黑洞将在沉寂中回到你的身边。",
    "金苹果": "（该道具为“身份”模式专属道具）金苹果可以让你回复3点hp！但是作为代价你会跳过接下来的两个回合！不过对面的手铐和禁止卡也似乎不能使用了……",
    "铂金草莓": "（该道具为“身份”模式专属道具）因为是铂金草莓，所以能做到！自己回复1点hp，并且双方各加1点hp上限！",
    "肾上腺素": "（该道具为“身份”模式专属道具）双方的hp上限-1，道具上限+1，并且使用者获得一个新道具！如果你们的hp上限为1，无法使用该道具！",
    "烈性TNT": "（该道具为“身份”模式专属道具）双方的hp上限-1，hp各-1！注意，是先扣hp上限，然后再扣hp！另外，如果使用后会自杀，则无法使用该道具！",
}

help_msg = f"""
输入 .开枪 自己/对方 -|- 向自己/对方开枪
输入 .查看局势 -|- 查看当前局势
输入 .恶魔道具 道具名/all -|- 查看道具的使用说明
输入 .恶魔投降 -|- 进行投降
输入 .使用道具 道具名 -|- 使用道具"""

# 奖励设置
jiangli = 388
bet_tax = int(jiangli * 0.1) # 向下取整计算 10%
final_jiangli = jiangli - bet_tax

# 全局变量——事件（单位s）
turn_time = 600

#特殊user_id增加bet2权重（为跑团而生的一个东西（（（）
special_users = {
    '123456': {19: 1000, 21: 3},
    '789101': {22: 4}
}

# 定义权重表
def get_random_item(identity_found, normal_mode_limit, user_id):
    """根据模式返回一个随机道具"""
    
    item_count = len(item_dic)  # 道具总数
    normal_mode_items = [] # 普通模式需要增加权重的道具（暂无）
    identity_mode_items = [3] # 身份模式需要增加权重的道具（放大镜）
    
    # 动态生成权重表
    weights = {i: 0 for i in range(1, item_count + 1)}  # 初始化所有道具权重为0
    
    if identity_found == 0:
        # 普通模式：前 normal_mode_limit 个道具权重设为1，其他保持0
        for i in range(1, normal_mode_limit + 1):
            weights[i] = 1
    elif identity_found in [1,2]:
        # 身份模式：所有道具启用，部分稀有道具权重设为2
        for i in range(1, item_count + 1):
            weights[i] = 1
        for i in identity_mode_items:
            weights[i] = 2  # 增加稀有道具的出现概率
    
    # 特殊用户指定道具加成
    if user_id in special_users:
        for item_id, bonus in special_users[user_id].items():
            if 1 <= item_id <= len(item_dic):  # 确保道具ID合法
                weights[item_id] += bonus  

    # 生成候选列表（按照权重扩展）
    valid_items = [i for i in weights if weights[i] > 0]
    item_choices = [i for i in valid_items for _ in range(weights[i])]

    return random.choice(item_choices)

# 上弹函数
def load():
    """上弹，1代表实弹，0代表空弹"""
    clip_size = random.randint(2, 8)  # 随机生成弹夹容量
    if clip_size == 2:
        # 如果总弹数为2，强制设置一个实弹
        clip = [0, 1]
        random.shuffle(clip)  # 随机打乱弹夹顺序
    else:
        bullets = random.randint(1, clip_size // 2 + 1)  # 随机生成实弹数量
        clip = [0] * clip_size
        bullet_positions = random.sample(range(clip_size), bullets)  # 确定实弹位置
        for pos in bullet_positions:
            clip[pos] = 1
    return clip

def handle_game_end(
    group_id: str,
    winner: str,
    prefix_msg: str,
    bar_data: dict,
    demon_data: dict
):
    """处理游戏结束的公共逻辑（使用全局变量）"""
    user_data = open_data(full_path)
    
    players = demon_data[group_id]['pl']
    player0 = str(players[0])
    player1 = str(players[1])
    
    # 发放奖励
    user_data[winner]['berry'] += final_jiangli
    
    # 构建基础消息
    msg = prefix_msg + "恭喜" + MessageSegment.at(str(winner)) + (
        f'胜利！恭喜获得{jiangli}颗草莓！但由于草莓税法的实行，需上交10%，'
        f'最终获得{final_jiangli}颗，上交{bet_tax}颗税！'
    )
    
    # 处理身份徽章掉落（1/4概率）
    if random.randint(1, 4) == 1:
        user_data.setdefault(str(winner), {}).setdefault('collections', {})
        if '身份徽章' not in user_data[str(winner)]['collections']:
            user_data[str(winner)]['collections']['身份徽章'] = 1
            msg += "\n\n游戏结束时，你意外从桌子底下看到了一个亮闪闪的徽章，上面写着“identity”，你感到十分疑惑，便捡了起来。输入.cp 身份徽章 以查看具体效果"
    
    # 更新玩家状态
    for player in [player0, player1]:
        bar_data[player]['game'] = '1'
        bar_data[player]['status'] = 'nothing'
    
    # 更新奖池
    bar_data.setdefault('pots', 0)
    bar_data['pots'] += bet_tax
    
    # 膀胱模式检测
    game_turn = demon_data[group_id]['game_turn']
    if game_turn > death_turn:
        if any(user_data[p].get('pangguang', 0) == 0 for p in [player0, player1]):
            msg += f"\n- 你们已经打了{demon_data[group_id]['game_turn']}轮，超过{death_turn}轮了……这股膀胱的怨念射入身份徽章里面！现在你们的身份徽章已解锁极速模式！就算暂时没有身份徽章以后也能直接切换！请使用 .use 身份徽章/2 切换！"
        for p in [player0, player1]:
            user_data[p]['pangguang'] = 1
    
    # 重置游戏数据
    demon_data[group_id] = demon_default.copy()
    demon_data[group_id]['demon_coldtime'] = int(time.time()) + 1200
    
    # 统一保存数据
    save_data(full_path, user_data)
    
    return msg, bar_data, demon_data

# 死斗函数
def death_mode(identity_found, group_id, demon_data, item_dic):
    '''判断是否开启死斗模式：根据不同的状态和轮数进行血量上限扣减，保存状态后最后返回msg'''
    player0 = str(demon_data[group_id]['pl'][0])
    player1 = str(demon_data[group_id]['pl'][1])
    msg = ''
    
    if identity_found in turn_limit and demon_data[group_id]['game_turn'] > turn_limit[identity_found]:
        msg += f'\n- 轮数大于{turn_limit[identity_found]}，死斗模式开启！\n'
        
        # HP 上限减少
        if identity_found in [1,2] and demon_data[group_id]["hp_max"] > 1:
            demon_data[group_id]["hp_max"] -= 1
            new_hp_max = demon_data[group_id]["hp_max"]
            msg += f'- {new_hp_max+1}>1，扣1点hp上限，当前hp上限：{new_hp_max}\n'
            
            # 校准所有玩家血量不得超过 hp 上限
            for i in range(len(demon_data[group_id]["hp"])):
                demon_data[group_id]["hp"][i] = min(demon_data[group_id]["hp"][i], demon_data[group_id]["hp_max"])

        # 额外扣除 1 点道具上限，并随机删除 1-2 个道具
        if identity_found == 2:
            if demon_data[group_id]["item_max"] > 6:
                demon_data[group_id]["item_max"] -= 1  # 扣 1 点道具上限（最低仍为 6）
                new_item_max = demon_data[group_id]["item_max"]
                msg += f'- {new_item_max+1}>6，扣1点道具上限，当前道具上限：{demon_data[group_id]["item_max"]}\n'

            remove_random = random.randint(1, 2)
            
            # 计算可删除的道具数量
            remove_count0 = min(remove_random, len(demon_data[group_id]['item_0'])) if demon_data[group_id]['item_0'] else 0
            remove_count1 = min(remove_random, len(demon_data[group_id]['item_1'])) if demon_data[group_id]['item_1'] else 0

            # 随机选择要删除的道具
            removed_items_0 = random.sample(demon_data[group_id]['item_0'], remove_count0) if remove_count0 else []
            removed_items_1 = random.sample(demon_data[group_id]['item_1'], remove_count1) if remove_count1 else []

            # 逐个删除选定的道具实例
            for item in removed_items_0:
                demon_data[group_id]['item_0'].remove(item)

            for item in removed_items_1:
                demon_data[group_id]['item_1'].remove(item) 

            # 记录被删除的道具名称
            removed_names_0 = [item_dic.get(i, "未知道具") for i in removed_items_0]
            removed_names_1 = [item_dic.get(i, "未知道具") for i in removed_items_1]

            # 记录删除的信息
            if removed_names_0:
                msg += '- '+ MessageSegment.at(player0) + f'失去了{remove_count0}个道具：{"、".join(removed_names_0)}！\n'
            if removed_names_1:
                msg += '- '+ MessageSegment.at(player1) + f'失去了{remove_count1}个道具：{"、".join(removed_names_1)}！\n'

        # 跑团专用999模式，额外扣2点HP上限
        elif identity_found == 999 and demon_data[group_id]["hp_max"] > 1:
            old_hp_max = demon_data[group_id]["hp_max"]
            demon_data[group_id]["hp_max"] -= 2
            if demon_data[group_id]["hp_max"] <= 1:
                demon_data[group_id]["hp_max"] = 1
            new_hp_max = demon_data[group_id]["hp_max"]
            msg += f'- {old_hp_max}>1，扣2点hp上限，当前hp上限：{new_hp_max}\n'

            # 校准所有玩家血量不得超过hp上限
            for i in range(len(demon_data[group_id]["hp"])):
                demon_data[group_id]["hp"][i] = min(demon_data[group_id]["hp"][i], demon_data[group_id]["hp_max"])
    
    return msg, demon_data

# 刷新道具函数
def refersh_item(identity_found, group_id, demon_data):
    idt_len = len(item_dic2)
    add_max = 0
    pangguang_add = 0
    msg = ''
    if identity_found == 1:
        idt_len = 0
        add_max += 1
    elif identity_found in [2,999]:
        idt_len = 0
        add_max += 1
        pangguang_add += 2
    player0 = str(demon_data[group_id]['pl'][0])
    player1 = str(demon_data[group_id]['pl'][1])
    hp0 = demon_data[group_id]["hp"][0]
    hp1 = demon_data[group_id]["hp"][1]
    # 重新获取hp_max
    hp_max = demon_data.get(group_id, {}).get('hp_max')
    item_max = demon_data.get(group_id, {}).get('item_max')
    for i in range(random.randint(1+pangguang_add//2,3+add_max)):
        demon_data[group_id]['item_0'].append(get_random_item(identity_found, len(item_dic) - idt_len, player0))
        demon_data[group_id]['item_1'].append(get_random_item(identity_found, len(item_dic) - idt_len, player1))
    # 检查并限制道具数量上限为max
    demon_data[group_id]['item_0'] = demon_data[group_id]['item_0'][:item_max]  # 截取前max个道具
    demon_data[group_id]['item_1'] = demon_data[group_id]['item_1'][:item_max]  # 截取前max个道具
    # 生成道具信息
    item_0 = ", ".join(item_dic.get(i, "未知道具") for i in demon_data[group_id]['item_0'])
    item_1 = ", ".join(item_dic.get(i, "未知道具") for i in demon_data[group_id]['item_1'])
    # 获取玩家道具信息
    items_0 = demon_data[group_id]['item_0']  # 玩家0道具列表
    items_1 = demon_data[group_id]['item_1']  # 玩家1道具列表
    if len(items_0) == 0:
        item_0 = "你目前没有道具哦！"
    if len(items_1) == 0:
        item_1 = "你目前没有道具哦！"
    msg += MessageSegment.at(player0) + f"\nhp：{hp0}/{hp_max}\n" + f"道具({len(items_0)}/{item_max})：" +f"\n{item_0}\n\n"
    msg += MessageSegment.at(player1) + f"\nhp：{hp1}/{hp_max}\n" + f"道具({len(items_1)}/{item_max})：" +f"\n{item_1}\n"

    return msg, demon_data

# 开枪函数
async def shoot(stp, group_id, message,args):
    demon_data = open_data(demon_path)
    user_data = open_data(full_path)
    bar_data = open_data(bar_path)
    hp_max = demon_data.get(group_id, {}).get('hp_max')
    item_max = demon_data.get(group_id, {}).get('item_max')
    clip = demon_data.get(group_id, {}).get('clip')
    hp = demon_data.get(group_id, {}).get('hp')
    pl = demon_data.get(group_id, {}).get('turn')
    player0 = str(demon_data[group_id]['pl'][0])
    player1 = str(demon_data[group_id]['pl'][1])
    identity_found = demon_data[group_id]['identity'] 
    add_max = 0
    pangguang_add = 0
    # 身份模式开了就更新dlc
    idt_len = len(item_dic2)
    if identity_found == 1:
        idt_len = 0
        add_max += 1
    elif identity_found in [2,999]:
        idt_len = 0
        add_max += 1
        pangguang_add += 2
    msg = ""
    if clip[-1] == 1:
        atk = demon_data[group_id]['atk']
        hp[pl-stp] -= 1 + atk
        demon_data[group_id]['atk'] = 0
        demon_data[group_id]['add_atk'] = False
        if atk != 0:
            msg += f"\n- 这颗子弹伤害为……{atk+1}点！"
        if atk in [3, 4]:
            msg += '\n- 癫狂屠戮！'
        if atk >= 5:
            msg += '\n- 无双，万军取首！'
        msg += f'\n- 你开枪了，子弹 *【击中了】* {args}！{args}剩余hp：{str(hp[pl-stp])}/{hp_max}\n'
    else:
        demon_data[group_id]['atk'] = 0
        demon_data[group_id]['add_atk'] = False
        msg += f'\n- 你开枪了，子弹未击中{args}！{args}剩余hp：{str(hp[pl-stp])}/{hp_max}\n'
    del clip[-1]
    
    if len(clip) == 0 or clip.count(1) == 0:
        msg += '- 子弹用尽，重新换弹，道具更新！\n'
        # 游戏轮数+1
        demon_data[group_id]['game_turn'] += 1
        # 获取死斗模式信息
        death_msg, demon_data = death_mode(identity_found, group_id, demon_data)
        msg += f'\n- 当前轮数：{demon_data[group_id]['game_turn']}'
        msg += death_msg
        # 增加换行，优化排版
        msg += "\n"
        clip = load()
        # 获取刷新道具
        item_msg, demon_data = refersh_item(identity_found, group_id, demon_data)
        msg += item_msg
        # 增加换行，优化排版
        msg += "\n"
    
    if demon_data[group_id]['hcf'] < 0 and stp != 0:
        demon_data[group_id]['hcf'] = 0
        out_pl = demon_data[group_id]['pl'][demon_data[group_id]['turn']-1]
        msg += "- "+MessageSegment.at(str(out_pl)) + "已挣脱束缚！\n"
    if demon_data[group_id]['hcf'] == 0 or stp == 0:
        pl += stp
        pl = pl%2   
    else:
        demon_data[group_id]['hcf'] -= 2
    hcf = demon_data.get(group_id, {}).get('hcf')
    if hcf != 0:
        msg += f"- 当前对方剩余束缚回合数：{(hcf+1)//2}\n"
    demon_data[group_id]['turn'] = pl
    demon_data[group_id]['clip'] = clip
    demon_data[group_id]['hp'] = hp
    # 刷新时间
    demon_data[group_id]['turn_start_time'] = int(time.time())
    if demon_data[group_id]['hp'][0] <= 0: 
        winner = demon_data[group_id]['pl'][1]
        end_msg, bar_data, demon_data = handle_game_end(
            group_id=str(group_id),
            winner=winner,
            prefix_msg="- 游戏结束！",
            bar_data=bar_data,
            demon_data=demon_data
        )
        msg += end_msg
    elif demon_data[group_id]['hp'][1] <= 0:
        winner = demon_data[group_id]['pl'][0]
        end_msg, bar_data, demon_data = handle_game_end(
            group_id=str(group_id),
            winner=winner,
            prefix_msg="- 游戏结束！",
            bar_data=bar_data,
            demon_data=demon_data
        )
        msg += end_msg
    else:
        pid = demon_data[group_id]['pl'][demon_data[group_id]['turn']]
        msg += '- 本局总弹数为'+str(len(demon_data[group_id]['clip']))+'，实弹数为'+str(demon_data[group_id]['clip'].count(1))+"\n" + "- 当前是"+ MessageSegment.at(pid) + "的回合"
    save_data(bar_path, bar_data)
    save_data(demon_path, demon_data)
    await message.finish(msg, at_sender = True)

# 开枪命令
fire = on_command("开枪",aliases={"射击"}, permission=GROUP, priority=1, block=True, rule=whitelist_rule)
@fire.handle()
async def fire_handle(bot: Bot, event: GroupMessageEvent, arg: Message = CommandArg()):
    group_id = str(event.group_id)
    if await check_timeout(group_id):
        return
    user_id = str(event.user_id)
    args = str(arg).strip()
    demon_data = open_data(demon_path)
    player_turn = demon_data[group_id]["turn"]
    # 添加全局冷却
    all_cool_time(cd_path, user_id, group_id)
    
    if demon_data[group_id]["start"] == False:
        await fire.finish("恶魔轮盘du尚未开始！",at_sender = True)
        
    if user_id not in demon_data[group_id]['pl']:
        await fire.finish("只有当前局内玩家能行动哦！",at_sender = True)

    if demon_data[group_id]["pl"][player_turn] != user_id:
        await fire.finish("现在不是你的回合，请等待对方操作！",at_sender = True)
    
    if args == "自己":
        stp = 0
        # 调用开枪函数
        await shoot(stp,group_id,fire,args)
    elif args == "对方":
        stp = 1
        # 调用开枪函数
        await shoot(stp,group_id,fire,args)
    else:
        await fire.finish("指令错误！请输入 <.开枪 自己> 或者 <.开枪 对方> 来开枪哦！",at_sender = True)

# 使用道具
prop_demon = on_command("使用",aliases={"使用道具"}, permission=GROUP, priority=1, block=True, rule=whitelist_rule)

@prop_demon.handle()
async def prop_demon_handle(bot: Bot, event: GroupMessageEvent, arg: Message = CommandArg()):
    group_id = str(event.group_id)
    if await check_timeout(group_id):
        return
    user_id = str(event.user_id)
    args = str(arg).strip()
    user_data = open_data(full_path)
    bar_data = open_data(bar_path)
    demon_data = open_data(demon_path)
    player_turn = demon_data[group_id]["turn"]
    # 添加全局冷却
    all_cool_time(cd_path, user_id, group_id)
    add_max = 0
    pangguang_add = 0
    if demon_data[group_id]["start"] == False:
        await prop_demon.finish("恶魔轮盘du尚未开始！", at_sender=True)

    if user_id not in demon_data[group_id]['pl']:
        await prop_demon.finish("只有当前局内玩家能行动哦！", at_sender=True)

    if demon_data[group_id]["pl"][player_turn] != user_id:
        await prop_demon.finish("现在不是你的回合，请等待对方操作！", at_sender=True)
    identity_found = demon_data[group_id]['identity'] 
    # 身份模式开了就更新dlc
    idt_len = len(item_dic2)
    if identity_found == 1:
        idt_len = 0
        add_max += 1
    elif identity_found in [2,999]:
        idt_len = 0
        add_max += 1
        pangguang_add += 2
    
    # 提取数据
    player_items = demon_data[group_id][f"item_{player_turn}"]
    opponent_turn = (player_turn + 1) % len(demon_data[group_id]['pl'])
    opponent_items = demon_data[group_id][f"item_{opponent_turn}"]

    # 道具名称匹配（忽略大小写）
    args_lower = args.lower()
    item_dic_lower = {key: value.lower() for key, value in item_dic.items()}  # 生成一个忽略大小写的字典

    if args_lower not in item_dic_lower.values():  # 检查输入的名称是否存在于 item_dic（忽略大小写）
        await prop_demon.finish("你输入的道具不存在，请确认后再使用！")

    # 查找玩家的道具中是否存在该道具
    try:
        # 遍历玩家的道具ID，找到第一个匹配的道具名称（忽略大小写）
        item_idx = next(i for i, item_id in enumerate(player_items) if item_dic[item_id].lower() == args_lower)
    except StopIteration:
        await prop_demon.finish("你并没有这个道具，请确认后再使用！", at_sender=True)

    # 提取数据
    item_id = player_items[item_idx]
    item_name = item_dic[item_id]
    hp_max = demon_data.get(group_id, {}).get('hp_max')
    item_max = demon_data.get(group_id, {}).get('item_max')
    msg = MessageSegment.at(str(demon_data[group_id]["pl"][player_turn])) + f"使用了道具：{item_name}\n\n"
    player_items.pop(item_idx)
    demon_data[group_id]['turn_start_time'] = int(time.time()) # 更新回合时间
    
    if item_name == "桃":
        demon_data[group_id]["hp"][player_turn] += 1
        if demon_data[group_id]["hp"][player_turn] >= hp_max:
            demon_data[group_id]["hp"][player_turn] = hp_max
        msg += f"你的hp回复1点（最高恢复至体力上限）。\n当前hp：{demon_data[group_id]['hp'][player_turn]}/{hp_max}\n"

    elif item_name == "医疗箱":
        demon_data[group_id]["hp"][player_turn] += 2
        demon_data[group_id]["hcf"] = 0
        demon_data[group_id]["atk"] = 0
        if demon_data[group_id]["hp"][player_turn] >= hp_max:
            demon_data[group_id]["hp"][player_turn] = hp_max
        demon_data[group_id]['turn'] = (player_turn + 1) % len(demon_data[group_id]['pl'])
        msg += f"你的hp回复2点（最高恢复至体力上限），但是代价是跳过本回合，而且对方的束缚将自动挣脱！\n当前hp：{demon_data[group_id]['hp'][player_turn]}/{hp_max}\n"

    elif item_name == "放大镜":
        next_bullet = "实弹" if demon_data[group_id]['clip'][-1] == 1 else "空弹"
        msg += f"下一颗子弹是：{next_bullet}！\n"

    elif item_name == "眼镜":
        if len(demon_data[group_id]['clip']) > 1:
            count_real_bullets = demon_data[group_id]['clip'][-2:].count(1)
            msg += f"前两颗子弹中有 {count_real_bullets} 颗实弹。\n"
        else:
            msg += f"枪膛里只剩最后一颗子弹了，是{'实弹' if demon_data[group_id]['clip'][-1] == 1 else '空弹'}！\n"

    elif item_name == "手铐":
        if demon_data[group_id]['hcf'] == 0:
            demon_data[group_id]['hcf'] = 1
            msg += "你成功拷住了对方！\n"
        else:
            player_items.append(item_id)
            msg += "不可使用！对方仍处于束缚状态！\n"

    elif item_name == "禁止卡":
        # 获取对方的回合编号
        if demon_data[group_id]['hcf'] == 0:
            add_turn = (random.randint(0,1)*2)
            if add_turn == 0:
                skip_turn = 1
            else:
                skip_turn = 2
            demon_data[group_id]['hcf'] = 1 + add_turn
            if len(opponent_items) < item_max:
                opponent_items.append(item_id)  # 只有在对方道具少于 max_item 个时才增加禁止卡
                msg += f"你成功禁止住了对方！禁止了{skip_turn}个回合，但同时对方也获得了一张禁止卡！\n"
            else:
                msg += f"你成功禁止住了对方！禁止了{skip_turn}个回合，但对方道具已满，并未获得这张禁止卡！\n"
        else:
            player_items.append(item_id)
            msg += "不可使用！对方仍处于束缚状态！\n"

    elif item_name == "欲望之盒":
        randchoice = random.randint(1, 10)
        if randchoice <= 5:
            new_item = get_random_item(identity_found, len(item_dic) - idt_len, user_id)
            player_items.append(new_item)
            new_item_name = item_dic[new_item]
            msg += f"你打开了欲望之盒，获得了道具：{new_item_name}\n"
        elif randchoice <= 8:
            msg += f"你打开了欲望之盒，恢复了1点体力\n"
            demon_data[group_id]["hp"][player_turn] += 1
            if demon_data[group_id]["hp"][player_turn] >= hp_max + 1:
                demon_data[group_id]["hp"][player_turn] = hp_max
                player_items.append(1)
                msg += f"但是由于你的体力已经到达上限，这点体力将转化为桃送给你。这个桃无视道具上限，但只有这轮有效。\n"
            msg += f"当前hp：{demon_data[group_id]['hp'][player_turn]}/{hp_max}\n"
        elif randchoice <= 10:
            demon_data[group_id]["hp"][opponent_turn] -= 1
            msg += f"你打开了欲望之盒，对对面造成了一点伤害！\n对方目前剩余hp为：{demon_data[group_id]['hp'][opponent_turn]}\n"

    elif item_name == "无中生有":
        new_items = [get_random_item(identity_found, len(item_dic) - idt_len, user_id) for _ in range(2)]
        player_items.extend(new_items)  # 添加新道具
        new_items_names = [item_dic[item] for item in new_items]
        if demon_data[group_id]["hcf"] <= 0:
            demon_data[group_id]["atk"] = 0
            demon_data[group_id]["hcf"] = 0
            demon_data[group_id]['turn'] = (player_turn + 1) % len(demon_data[group_id]['pl'])
            msg += f"你使用了无中生有，获得了道具：{', '.join(new_items_names)}\n代价是跳过了自己的回合!\n"
        elif demon_data[group_id]["hcf"] >= 1:
            demon_data[group_id]["hcf"] -= 2
            msg += f"你使用了无中生有，获得了道具：{', '.join(new_items_names)}\n代价是对方的束缚的回合将-1！\n"

    elif item_name == "小刀":
        if demon_data[group_id]["add_atk"]:
            demon_data[group_id]['atk'] += 1
            msg += f"你装备了小刀，由于受到烈弓的效果，这颗子弹的攻击力可以无限叠加！目前这颗子弹的攻击力为{demon_data[group_id]['atk'] + 1}！\n"
        else:
            demon_data[group_id]['atk'] = 1
            msg += "你装备了小刀，攻击力提升至两点！\n"

    elif item_name == "酒":
        if demon_data[group_id]["add_atk"]:
            demon_data[group_id]['atk'] += 1
            msg += f"你喝下了酒，由于受到烈弓的效果，这颗子弹的攻击力可以无限叠加！目前这颗子弹的攻击力为{demon_data[group_id]['atk'] + 1}！\n"
        else:
            demon_data[group_id]['atk'] = 1
            msg += "你喝下了酒，需不需要一把古锭刀？攻击力提升至两点！\n"

        if demon_data[group_id]['hp'][player_turn] == 1:
            demon_data[group_id]['hp'][player_turn] += 1
            msg += f"酒精振奋了你，hp恢复到2点！\n"

    elif item_name == "啤酒":
        if demon_data[group_id]['clip']:
            removed_bullet = demon_data[group_id]['clip'].pop()
            bullet_type = "实弹" if removed_bullet == 1 else "空弹"
            msg += f"你退掉了一颗子弹，这颗子弹是：{bullet_type}\n"
        if not demon_data[group_id]['clip'] or all(b == 0 for b in demon_data[group_id]['clip']):
            demon_data[group_id]['clip'] = load()
            msg += "- 子弹已耗尽，重新装填！\n"
            # 游戏轮数+1
            demon_data[group_id]['game_turn'] += 1
            # 获取死斗模式信息
            death_msg, demon_data = death_mode(identity_found, group_id, demon_data)
            msg += death_msg
            
            # 获取刷新道具
            item_msg, demon_data = refersh_item(identity_found, group_id, demon_data)
            msg += item_msg
            
            # 增加弹数消息，优化排版
            msg += '- 本局总弹数为'+str(len(demon_data[group_id]['clip']))+'，实弹数为'+str(demon_data[group_id]['clip'].count(1))
            
    elif item_name == "刷新票":
        num_items = len(player_items)
        player_items.clear()
        player_items.extend([get_random_item(identity_found, len(item_dic) - idt_len, user_id) for _ in range(num_items)])
        new_items_names = [item_dic[item] for item in player_items]
        msg += f"你刷新了你的所有道具，新道具为：{', '.join(new_items_names)}\n"

    elif item_name == "手套":
        demon_data[group_id]['clip'] = load()
        msg += f"你重新装填了子弹！新弹夹总数：{len(demon_data[group_id]['clip'])} 实弹数：{demon_data[group_id]['clip'].count(1)}\n"

    elif item_name == "骰子":
        random_hp = random.randint(1, 4)  # 生成一个随机的 hp 值
        if random_hp >= hp_max:
            random_hp = hp_max
        demon_data[group_id]["hp"][player_turn] = random_hp
        msg += "恶魔掷出骰子……骰子掷出了新的hp值：\n"
        msg += f"你的的 hp 已变更成：{random_hp}！\n"
        
    elif item_name == "天秤":
        len_player_items = len(player_items)
        len_opponent_items = len(opponent_items)
        if len_player_items >= len_opponent_items:
            demon_data[group_id]["hp"][opponent_turn] -= 1
            msg += f"天秤的指针开始转动…… 检测到你的道具数量为：{len_player_items}，对面的道具数量为：{len_opponent_items}；\n由于{len_player_items}≥{len_opponent_items}，你成功对对方造成一点伤害！\n对方目前剩余hp为：{demon_data[group_id]['hp'][opponent_turn]}\n"
        else:
            demon_data[group_id]["hp"][player_turn] += 1
            if demon_data[group_id]["hp"][player_turn] >= hp_max:
                demon_data[group_id]["hp"][player_turn] = hp_max
            msg += f"天秤的指针开始转动…… 检测到你的道具数量为：{len_player_items}，对面的道具数量为：{len_opponent_items}；\n由于{len_player_items}<{len_opponent_items}，你回复一点体力（最高恢复至上限！）！\n你目前的hp为：{demon_data[group_id]['hp'][player_turn]}\n"  

    elif item_name == "双转团":
        # 获取原始道具长度
        original_opponent_count = len(opponent_items)

        if len(opponent_items) < item_max:
            opponent_items.append(item_id)  # 只有在对方道具少于 max_item 个时才获得双转团
            msg += f"这件物品太“IDENTITY”了，对方十分感兴趣，所以拿走了这件物品！\n"
        else:
            msg += f"这件物品太“IDENTITY”了，对方十分感兴趣，但是由于道具已满，没办法拿走这件物品，所以把双转团丢了！\n"

        # 获取新的道具列表（双转团转移后的状态）
        now_player_items = demon_data[group_id][f"item_{player_turn}"]
        now_opponent_items = demon_data[group_id][f"item_{opponent_turn}"]
        # 首先 1/4 触发事件
        kou_first = random.randint(1, 4)
        kou_second = 0
        if kou_first == 1:
            kou_second = random.randint(1, 3)
        # 功能1：1/3概率转移随机道具
        if kou_second == 1 and len(now_player_items) > 0:  # 确保玩家还有道具
            random_idx = random.randint(0, len(now_player_items)-1)
            random_item_id = player_items.pop(random_idx)
            random_item_name = item_dic[random_item_id]
            # 检查转移后的道具栏状态
            if len(now_opponent_items) < item_max:
                opponent_items.append(random_item_id)
                msg += f"- 对方还顺手拿走了你的【{random_item_name}】！\n"
                # 1/2扣对面一点血
                if random.randint(1, 2) == 1:
                    demon_data[group_id]["hp"][opponent_turn] -= 1
                    demon_data[group_id]["hp"][player_turn] = current_hp
                    msg += f"但是一不小心刷了一跤，hp-1！\n- 当前对方hp：{demon_data[group_id]["hp"][opponent_turn]}/{hp_max}\n"
            else:
                msg += f"- 对方还顺手拿走了你的【{random_item_name}】，但是由于物品栏已满，他遗憾的把这件道具丢了！\n"

        # 功能2：1/3概率扣自己1点血，1/3加一点血
        elif kou_second == 2:
            demon_data[group_id]["hp"][player_turn] -= 1
            msg += f"你在丢双转团的时候太急了！人一旦急，就会更急，神就不会定，所以你一不小心把血条往左滑了一下，损失了1点hp！\n- 当前自己hp：{demon_data[group_id]["hp"][player_turn]}/{hp_max}\n"
        
        elif kou_second == 3:
            demon_data[group_id]["hp"][player_turn] += 1
            # 无法超过上限
            if demon_data[group_id]["hp"][player_turn] >= hp_max:
                demon_data[group_id]["hp"][player_turn] = hp_max
            msg += f"你在丢双转团的时候太急了！人一旦急，就会更急，神就不会定，所以你一不小心把血条往右滑了一下，增加了1点hp！\n- 当前自己hp：{demon_data[group_id]["hp"][player_turn]}/{hp_max}\n"
        
        # 功能3：对方初始已满时获得徽章
        if original_opponent_count >= item_max:
            #判断是否开辟藏品栏
            if(not 'collections' in user_data[str(user_id)]):
                user_data[str(user_id)]['collections'] = {}
            #是否已经持有藏品"身份徽章"
            #如果没有，则添加
            if(not '身份徽章' in user_data[str(user_id)]['collections']):
                user_data[str(user_id)]['collections']['身份徽章'] = 1
                #写入文件
                save_data(full_path, user_data)
                msg += f"\n你在丢双转团的时候，意外从这个东西身上看到了一个亮闪闪的徽章，上面写着“identity”，你感到十分疑惑，便捡了起来。输入.cp 身份徽章 以查看具体效果\n"
    
    elif item_name == "休养生息":
        if demon_data[group_id]["hp"][opponent_turn] == hp_max:
            demon_data[group_id]["hp"][player_turn] += 1  # 只回 1 点血
            msg += f"休养生息，备战待敌；止兵止战，休养生息。\n对方hp已满，你仅恢复了1点hp。\n"
        else:
            demon_data[group_id]["hp"][player_turn] += 2
            demon_data[group_id]["hp"][opponent_turn] += 1
            msg += f"休养生息，备战待敌；止兵止战，休养生息。\n你恢复了2点hp，对方恢复了1点hp（最高恢复至上限）。\n"
        
        # 校准所有玩家血量不得超过hp上限
        for i in range(len(demon_data[group_id]["hp"])):
            demon_data[group_id]["hp"][i] = min(demon_data[group_id]["hp"][i], demon_data[group_id]["hp_max"])

        # 追加体力信息
        msg += f"\n你的体力为 {demon_data[group_id]['hp'][player_turn]}/{hp_max}\n"
        msg += f"对方的体力为 {demon_data[group_id]['hp'][opponent_turn]}/{hp_max}\n"

    
    elif item_name == "玩具枪":
        randchoice = random.randint(1, 2)
        if randchoice == 1:
            demon_data[group_id]["hp"][opponent_turn] -= 1
            msg += f"你使用了玩具枪，可没想到里面居然是真弹！你对对面造成了一点伤害！\n对方目前剩余hp为：{demon_data[group_id]['hp'][opponent_turn]}\n"    
        else: 
            msg += f"你使用了玩具枪，这确实是一个可以滋水的玩具水枪，无事发生。\n"
    
    elif item_name == "血刃":
        if demon_data[group_id]["hp"][player_turn] == 1:
            player_items.append(item_id)
            msg +=f'你的血量无法支持你使用血刃！\n'
        else:
            randchoice = random.randint(1, 5)
            demon_data[group_id]["hp"][player_turn] -= 1
            new_items = [get_random_item(identity_found, len(item_dic) - idt_len, user_id) for _ in range(2)]
            player_items.extend(new_items)  # 添加新道具
            new_items_names = [item_dic[item] for item in new_items]
            msg += f"你使用了血刃，献祭自己1盎司鲜血，祈祷，获得了道具：{', '.join(new_items_names)}\n你目前剩余hp为：{demon_data[group_id]['hp'][player_turn]}/{hp_max}\n"    
            if randchoice == 5:
                msg += f"\n“血刃？你怎么会在这里？0猎的工资不够你用的吗，还跑过来再就业？”"
                msg += f"\n“唉，工作困难啊……抓玛德琳我太没存在感了，总是被人遗忘，必须要出来再就业了。”\n"
    
    elif item_name == "烈弓":
        demon_data[group_id]['atk'] += 1
        demon_data[group_id]['add_atk'] = True
        msg += f"你使用了烈弓，开始叠花色！烈弓解除了限制，并且伤害+1！现在酒和小刀的伤害可无限叠加！这颗子弹的攻击力可以无限叠加！目前这颗子弹的攻击力为{demon_data[group_id]['atk'] + 1}！\n"
    
    elif item_name == "黑洞":
        if opponent_items:  # 对方有道具
            # 随机选择对方道具
            stolen_idx = random.randint(0, len(opponent_items) - 1)
            stolen_item_id = opponent_items.pop(stolen_idx)
            stolen_item_name = item_dic[stolen_item_id]

            player_items.append(stolen_item_id)  # 抢夺道具

            msg += (f"你召唤出黑洞！\n"
                    f"空间开始剧烈扭曲……\n"
                    f"对方的【{stolen_item_name}】被黑洞吞噬，送进你的背包！\n")
        else:
            # 如果对方没有道具，黑洞会重新回到玩家背包
            player_items.append(item_id)
            msg += "你召唤出黑洞！然而对方空无一物，黑洞在无尽的沉寂中回到了你的手中。\n"

    elif item_name == "金苹果":
        demon_data[group_id]["hp"][player_turn] += 3
        demon_data[group_id]["hcf"] = 1
        demon_data[group_id]["atk"] = 0
        if demon_data[group_id]["hp"][player_turn] >= hp_max:
            demon_data[group_id]["hp"][player_turn] = hp_max
        demon_data[group_id]['turn'] = (player_turn + 1) % len(demon_data[group_id]['pl'])
        msg += f"你吃下了金苹果，因为太美味了，hp回复3点！但是由于过于美味，接下来你要好好回味这种味道，将直接跳过两个回合！不过对方的手铐和禁止卡也不能用了……\n当前hp：{demon_data[group_id]['hp'][player_turn]}/{hp_max}\n"
    
    elif item_name == "铂金草莓":
        demon_data[group_id]["hp"][player_turn] += 1
        hp_max += 1
        demon_data[group_id]["hp_max"] = hp_max
        if demon_data[group_id]["hp"][player_turn] >= hp_max:
            demon_data[group_id]["hp"][player_turn] = hp_max
        msg += f"因为是铂金草莓，所以能做到。吃下铂金草莓后，你的hp回复1点，并且双方的hp上限均+1！要不要尝试去拿一个9dp？\n当前hp：{demon_data[group_id]['hp'][player_turn]}/{hp_max}\n当前hp上限：{hp_max}\n"        
    
    elif item_name == "肾上腺素":
        # 检查血量上限是否为1
        if demon_data[group_id]["hp_max"] <= 1:
            player_items.append(item_id) 
            msg += "你想使用肾上腺素，但是血量上限已经过低，你无法承受这种后果！\n"
        else:
            # 增加使用者的道具
            new_item = get_random_item(identity_found, len(item_dic) - idt_len, user_id)
            player_items.append(new_item)
            new_item_name = item_dic[new_item]
            # 调整hp上限和道具上限
            hp_max -= 1
            item_max += 1
            demon_data[group_id]["hp_max"] = max(1, demon_data[group_id]["hp_max"])  # 血量上限保护锁
            demon_data[group_id]["item_max"] = item_max
            demon_data[group_id]["hp_max"] = hp_max
            new_hp_max = demon_data[group_id]["hp_max"]
            # 校准所有玩家血量不得超过hp上限
            for i in range(len(demon_data[group_id]["hp"])):
                demon_data[group_id]["hp"][i] = min(demon_data[group_id]["hp"][i], demon_data[group_id]["hp_max"])
                    
            msg += (
                f"你注射了肾上腺素！心跳如雷，时间仿佛放慢，力量在血管中沸腾！\n"
                f"- 双方道具上限 +1！\n"
                f"- 你获得了新道具：{new_item_name}\n"
                f"- 当前道具上限：{item_max}\n\n"
                f"然而，一丝生命力被悄然抽离……对手也感到一阵莫名的心悸。\n"
                f"- 双方HP上限 -1！\n"
                f"- 当前HP上限：{hp_max}\n"
            )
    elif item_name == "烈性TNT":
        # 获取当前 HP 和 HP 上限
        current_hp = demon_data[group_id]["hp"][player_turn]
        current_hp_max = demon_data[group_id]["hp_max"]
        # 判定是否禁止使用 TNT
        if current_hp_max <= 1 or current_hp <= 1 or (current_hp_max == 2 and current_hp == 2):
            player_items.append(item_id)
            msg += "你想引爆烈性TNT，但你的血量/血量上限已经过低，这样做无异于自杀！\n"
        else:
            demon_data[group_id]["hp_max"] -= 1
            demon_data[group_id]["hp_max"] = max(1, demon_data[group_id]["hp_max"])  # 确保体力上限不会降到 0，虽然前面有判断了

            # 校准所有玩家血量不得超过hp上限
            for i in range(len(demon_data[group_id]["hp"])):
                demon_data[group_id]["hp"][i] = min(demon_data[group_id]["hp"][i], demon_data[group_id]["hp_max"])
            
            # 扣完上限调整血量后再扣血
            demon_data[group_id]["hp"][player_turn] -= 1
            demon_data[group_id]["hp"][opponent_turn] -= 1

            msg += (
                "你点燃了烈性TNT，产生了巨大的爆炸！\n"
                f"- 双方HP上限 -1！\n- 当前HP上限：{demon_data[group_id]['hp_max']}\n"
                f"- 双方HP -1！\n- 你的HP：{demon_data[group_id]['hp'][player_turn]}/{demon_data[group_id]['hp_max']}\n- 对方HP：{demon_data[group_id]['hp'][opponent_turn]}/{demon_data[group_id]['hp_max']}\n"
            )
            
    elif item_name == "墨镜":
        if len(demon_data[group_id]['clip']) > 1:
            first_bullet = demon_data[group_id]['clip'][0]
            last_bullet = demon_data[group_id]['clip'][-1]
            real_bullet_count = (first_bullet + last_bullet)  # 计算两个位置的实弹数量
            msg += f"你戴上了墨镜，观察枪膛……\n第一颗和最后一颗子弹加起来，有{real_bullet_count}颗实弹！\n"
        else:
            msg += f"枪膛里只剩最后一颗子弹了，是{'实弹' if demon_data[group_id]['clip'][-1] == 1 else '空弹'}！\n"
    else:
        msg += "道具不存在或无法使用！\n"

    next_player_turn = demon_data[group_id]['turn']  # 获取下一位玩家的 turn
    next_player_id = str(demon_data[group_id]["pl"][next_player_turn])  # 下一位玩家的 ID
    msg += "\n- 现在轮到" + MessageSegment.at(str(next_player_id)) + "行动！"
    if demon_data[group_id]['hp'][0] <= 0: 
        winner = demon_data[group_id]['pl'][1]
        end_msg, bar_data, demon_data = handle_game_end(
            group_id=str(group_id),
            winner=winner,
            prefix_msg="- 游戏结束！",
            bar_data=bar_data,
            demon_data=demon_data
        )
        msg += end_msg
    elif demon_data[group_id]['hp'][1] <= 0:
        winner = demon_data[group_id]['pl'][0]
        end_msg, bar_data, demon_data = handle_game_end(
            group_id=str(group_id),
            winner=winner,
            prefix_msg="- 游戏结束！",
            bar_data=bar_data,
            demon_data=demon_data
        )
        msg += end_msg
    save_data(demon_path, demon_data)
    save_data(bar_path, bar_data)
    await prop_demon.finish(msg)

# 查看局势
check = on_fullmatch(['.查看局势', '。查看局势'], permission=GROUP, priority=1, block=True, rule=whitelist_rule)
@check.handle()
async def check_handle(event: GroupMessageEvent):
    group_id = str(event.group_id)
    if await check_timeout(group_id):
        return
    user_id = str(event.user_id)
    demon_data = open_data(demon_path)
    if demon_data[group_id]['start'] == False:
        await check.finish("当前并没有开始任何一句恶魔轮盘du哦！",at_sender = True)
    if user_id not in demon_data[group_id]['pl']:
        await check.finish("只有当前局内玩家能查看局势哦！",at_sender = True)
    # 生成玩家信息
    player0 = str(demon_data[group_id]['pl'][0])
    player1 = str(demon_data[group_id]['pl'][1])
    game_turn = demon_data.get(group_id, {}).get('game_turn')
    hp_max = demon_data.get(group_id, {}).get('hp_max')
    item_max = demon_data.get(group_id, {}).get('item_max')
    hcf = demon_data.get(group_id, {}).get('hcf')
    identity_found = demon_data[group_id]['identity'] 
    # 生成道具信息
    item_0 = ", ".join(item_dic.get(i, "未知道具") for i in demon_data[group_id]['item_0'])
    item_1 = ", ".join(item_dic.get(i, "未知道具") for i in demon_data[group_id]['item_1'])
    # 获取玩家道具信息
    items_0 = demon_data[group_id]['item_0']  # 玩家0道具列表
    items_1 = demon_data[group_id]['item_1']  # 玩家1道具列表
    if len(items_0) == 0:
        item_0 = "你目前没有道具哦！"
    if len(items_1) == 0:
        item_1 = "你目前没有道具哦！"
    # 生成血量信息
    hp0 = demon_data[group_id]['hp'][0]
    hp1 = demon_data[group_id]['hp'][1]
    atk = demon_data[group_id]['atk']
    identity_found = demon_data[group_id]['identity']
    # 步时信息
    elapsed = int(time.time()) - demon_data[group_id]['turn_start_time']
    remaining_seconds = turn_time - elapsed # 计算剩余冷却时间, 全局变量，设定时间（秒）
    remaining_minutes = remaining_seconds // 60  # 剩余分钟数
    remaining_seconds = remaining_seconds % 60  # 剩余秒数
    msg = "- 本局模式："
    if identity_found == 1:
        # death_turn轮以后死斗模式显示
        if identity_found in turn_limit and demon_data[group_id]['game_turn'] > turn_limit[identity_found]:
            msg += '（死斗）'
        msg += "身份模式\n"
    elif identity_found in [2,999]:
        # 1轮以后死斗模式显示
        if identity_found in turn_limit and demon_data[group_id]['game_turn'] > turn_limit[identity_found]:
            msg += '（死斗）'
        msg += "急速模式\n"
    else:
        msg += "正常模式\n"
    msg += f"- 本步剩余时间：{remaining_minutes}分{remaining_seconds}秒\n"
    msg += f"- 当前轮数：{game_turn}\n"
    if hcf != 0:
        msg += f"- 当前对方剩余束缚回合数：{(hcf+1)//2}\n"
    if atk > 0:
        msg += f"- 本颗子弹伤害为：{atk+1}点\n"
    msg += '\n' + MessageSegment.at(player0) + f"\nhp：{hp0}/{hp_max}\n" + f"道具({len(items_0)}/{item_max})：" +f"\n{item_0}\n\n"
    msg += MessageSegment.at(player1) + f"\nhp：{hp1}/{hp_max}\n" + f"道具({len(items_1)}/{item_max})：" +f"\n{item_1}\n\n"
    msg += f"- 总弹数{str(len(demon_data[group_id]['clip']))}，实弹数{str(demon_data[group_id]['clip'].count(1))}\n"
    pid = demon_data[group_id]['pl'][demon_data[group_id]['turn']]
    msg += "- 当前是"+ MessageSegment.at(pid) + "的回合"
    await check.finish(msg)
        

# 恶魔投降指令：随时投降
demon_surrender = on_command("恶魔投降", permission=GROUP, priority=1, block=True)

@demon_surrender.handle()
async def demon_surrender_handle(event: Event):
    group_id = str(event.group_id)  # 获取群组ID
    player_id = str(event.user_id)  # 获取发出投降指令的玩家ID
    
    demon_data = open_data(demon_path)  # 加载恶魔数据
    bar_data = open_data(bar_path)  # 加载bar数据

    # 判断玩家是否在游戏中
    if demon_data[group_id]['start'] == False:
        await demon_surrender.finish("当前没有进行中的游戏！", at_sender=True)
    # 获取当前游戏的玩家信息
    players = demon_data[group_id]['pl']  # 当前游戏中的两位玩家ID
    if player_id not in players:
        await demon_surrender.finish("你当前不在游戏中，无法投降！", at_sender=True)

    # 确定投降的玩家和获胜的玩家
    loser = player_id
    winner = str(players[1] if loser == players[0] else players[0])
    end_msg, bar_data, demon_data = handle_game_end(
        group_id=str(group_id),
        winner=winner,
        prefix_msg=f"玩家"+MessageSegment.at(loser)+"已投降。\n游戏结束，",
        bar_data=bar_data,
        demon_data=demon_data
    )

    save_data(bar_path, bar_data)
    save_data(demon_path, demon_data)

    # 发送投降结果消息
    await demon_surrender.finish(end_msg)

# 恶魔道具查询功能：展示指定道具的效果
prop_demon_query = on_command("恶魔道具", permission=GROUP, priority=1, block=True, rule=whitelist_rule)
@prop_demon_query.handle()
async def prop_demon_query_handle(bot: Bot, event: Event, arg: Message = CommandArg()):
    # 去除前后空格，处理用户输入
    prop_name = str(arg).strip().lower()

    if prop_name == "": # 没有输入默认all
        prop_name = 'all'
    if prop_name == "all":  # 如果是查询所有道具
        # 构建所有道具的效果信息
        all_effects = "\n".join([f"-【{prop}】：{effect}" for prop, effect in item_effects.items()])
        
        # 构建转发的消息内容
        msg_list = [
            {
                "type": "node",
                "data": {
                    "name": "全部恶魔道具",
                    "uin": event.self_id,
                    "content": all_effects
                }
            }
        ]
        # 转发全部道具效果消息
        await bot.call_api("send_group_forward_msg", group_id=event.group_id, messages=msg_list)
        await prop_demon_query.finish()
    else:  # 查询指定道具
        # 创建一个忽略大小写的映射字典
        lower_to_original = {key.lower(): key for key in item_effects.keys()}

        # 查找原始名称
        original_name = lower_to_original.get(prop_name)

        if original_name:
            # 使用原始名称查询效果
            effect = item_effects[original_name]
            await prop_demon_query.finish(f"\n道具【{original_name}】的效果是：\n{effect}", at_sender=True)
        else:
            # 没找到匹配项
            await prop_demon_query.finish(f"未找到名为【{prop_name}】的道具，请检查道具名称是否正确！", at_sender=True)

# 恶魔帮助
prop_demon_help = on_fullmatch(['.恶魔帮助', '。恶魔帮助'], permission=GROUP, priority=1, block=True, rule=whitelist_rule)
@prop_demon_help.handle()
async def prop_demon_help_handle():
    await prop_demon_help.finish(help_msg,at_sender = True)

# 超时检查
async def check_timeout(group_id):
    demon_data = open_data(demon_path)
    bar_data = open_data(bar_path)
    bots = get_bots()
    if not bots:
        logger.error("没有可用的Bot实例，无法检测bet2！")
        return
    bot = list(bots.values())[0]  # 获取第一个 Bot 实例
    # 确保 'demon_data' 和 'group_id' 存在
    # 初始化 group_id 中的游戏数据
    if group_id not in demon_data:
        demon_data[group_id] = demon_default
    elapsed = int(time.time()) - demon_data[group_id]['turn_start_time']
    if elapsed > turn_time:  # 全局变量，设定时间（秒）
        # 判断游戏是否开始
        if demon_data[group_id]['start']:
            # 获取双方玩家
            player_turn = demon_data[group_id]["turn"]
            opponent_turn = (player_turn + 1) % len(demon_data[group_id]['pl'])
            player = demon_data[group_id]['pl'][player_turn]
            non_current_player = demon_data[group_id]['pl'][opponent_turn]
            
            end_msg, bar_data, demon_data = handle_game_end(
                group_id=str(group_id),
                winner=non_current_player,
                prefix_msg="回合超时！当前回合玩家"+MessageSegment.at(player)+"自动判负！",
                bar_data=bar_data,
                demon_data=demon_data
            )
            msg = end_msg
            save_data(demon_path, demon_data)
            save_data(bar_path, bar_data)
            # 发送通知
            await bot.send_group_msg(
                group_id=group_id,
                message=msg
            )
            return True
        else:
            # 判断是否有人
            if len(demon_data[group_id]['pl']) == 1:
                user_data = open_data(full_path)
                player = demon_data[group_id]['pl'][0]
                # 退还草莓
                user_data[str(player)]['berry'] += 125 
                # 移除玩家游戏状态
                bar_data[player]['game'] = '1'
                bar_data[player]['status'] = 'nothing'
                # 重置游戏
                demon_data[group_id] = demon_default
                save_data(demon_path, demon_data)
                save_data(full_path, user_data)
                save_data(bar_path, bar_data)
                # 发送通知
                await bot.send_group_msg(
                    group_id=group_id,
                    message=f"由于长时间无第二人进入恶魔轮盘du，现已向"+ MessageSegment.at(player) + "返还125草莓的门票费并重置游戏。"
                )
                return True
    return False

# 30s检测是不是回合超时
@scheduler.scheduled_job("interval", seconds=30)
async def check_all_games():
    demon_data = open_data(demon_path)
    for group_id in list(demon_data.keys()):
        if isinstance(group_id, str) and group_id.isdigit():
            await check_timeout(group_id)

# 游戏4，三球竞猜
def reward_percentage(pool: int) -> int:
    """根据奖池金额计算中奖奖励比例（双球）"""
    if pool <= 1000:
        return 100  # 100%
    elif pool <= 3000:
        return int(75 + (100 - 75) * (3000 - pool) / (3000 - 1000))  # 100% -> 75%
    elif pool <= 7000:
        return int(50 + (75 - 50) * (7000 - pool) / (7000 - 3000))  # 75% -> 50%
    elif pool <= 15000:
        return int(30 + (50 - 30) * (15000 - pool) / (15000 - 7000))  # 50% -> 30%
    elif pool <= 30000:
        return int(20 + (30 - 20) * (30000 - pool) / (30000 - 15000))  # 30% -> 20%
    elif pool <= 50000:
        return int(10 + (20 - 10) * (50000 - pool) / (50000 - 30000))  # 20% -> 10%
    else:
        return 10  # 5%

def reward_percentage_triple(pool: int) -> int:
    """根据奖池金额计算中奖奖励比例（三球）"""
    if pool <= 25000:
        return 100
    elif pool <= 50000:  
        return int(50 + (100 - 50) * (50000 - pool) / (50000 - 25000))  # 100% -> 50%
    else:
        return 50  # 50%

    
def reward_amount(pool: int) -> int:
    """门票费"""
    if pool < 5000:
        return 50
    elif pool <= 10000:
        return 100
    elif pool <= 20000:
        return 150
    elif pool <= 30000:
        return 200
    elif pool <= 40000:
        return 250
    else:
        return 300
    
# 22:15 重置 double_ball_send
@scheduler.scheduled_job("cron", hour=22, minute=15)
async def reset_double_ball_send():
    bar_data = open_data(bar_path)
    bar_data.setdefault("double_ball_send", False)
    bar_data["double_ball_send"] = False
    save_data(bar_path, bar_data)

# 22:30 开奖
@scheduler.scheduled_job("cron", hour=22, minute=30)
async def double_ball_lottery():
    bots = get_bots()
    if not bots:
        logger.error("没有可用的Bot实例，无法开奖！")
        return
    bot = list(bots.values())[0]

    bar_data = open_data(bar_path)
    pots = bar_data.setdefault("pots", 0)

    if bar_data.get("double_ball_send", False):
        return  # 如果已经开奖，则返回

    red_ball = random.randint(1, 10)
    blue_ball = random.randint(1, 10)
    yellow_ball = random.randint(1, 10)

    # 记录开奖历史
    bar_data.setdefault("double_ball_history", [])
    bar_data["double_ball_history"].append({
        "date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "red": red_ball,
        "blue": blue_ball,
        "yellow": yellow_ball
    })

    big_winners = []
    winners = []
    single_match_users = []
    total_refund = 0

    for user_id, user_bar in bar_data.items():
        if user_id.isdigit() and isinstance(user_bar, dict) and user_bar.get("double_ball",{}).get("ifplay",0) == 1:
            user_bar.setdefault("bank", 0)
            user_bar.setdefault("double_ball", {})

            bet_data = user_bar["double_ball"]
            if not bet_data:
                continue  # 用户没有下注

            ticket_cost = bet_data.get("ticket_cost", 0)
            user_red = bet_data.get("red_points", 0)
            user_blue = bet_data.get("blue_points", 0)
            user_yellow = bet_data.get("yellow_points", 0)

            # 先检查三球中奖
            if user_red == red_ball and user_blue == blue_ball and user_yellow == yellow_ball:
                big_winners.append(user_id)
                
            # 再检查双球中奖（任意两个）
            elif (
                (user_red == red_ball and user_blue == blue_ball) or
                (user_red == red_ball and user_yellow == yellow_ball) or
                (user_blue == blue_ball and user_yellow == yellow_ball)
            ):
                winners.append(user_id)

            # 只猜中一个数字的玩家
            elif user_red == red_ball or user_blue == blue_ball or user_yellow == yellow_ball:
                bet_data["refund"] = int(ticket_cost * 1.5)  # 记录返还的门票费用
                total_refund += int(ticket_cost * 1.5)
                user_bar["bank"] += int(ticket_cost * 1.5)
                single_match_users.append(user_id)

            # 开奖后，重置 ifplay
            bet_data["ifplay"] = 0

    # 计算奖金
    # 百分比
    triple_reward_percentage_val = reward_percentage_triple(pots)
    reward_percentage_val = reward_percentage(pots)
    # 奖金
    total_reward = pots * reward_percentage_val // 100
    triple_total_reward = pots * triple_reward_percentage_val // 100
    msg_text = f"🎉 本期开奖号码：\n红 {red_ball} | 蓝 {blue_ball} | 黄 {yellow_ball}\n"
    msg_text += f"🏆 奖池总额：[{pots}]颗草莓\n"
    msg_text += f"🎁 本期一等奖奖金：[{triple_total_reward}]颗草莓\n"
    msg_text += f"🎁 本期二等奖奖金：[{total_reward}]颗草莓\n\n"

    if big_winners:
        big_reward_per_winner = triple_total_reward // len(big_winners)
        msg_text += "🎊 恭喜 "
        total_refund += big_reward_per_winner * len(big_winners)
        
        for big_winner in big_winners:
            bar_data[str(big_winner)]["bank"] += big_reward_per_winner
            bar_data[str(big_winner)]["double_ball"]["prize"] = big_reward_per_winner
            msg_text += MessageSegment.at(big_winner)  # @中奖者

        msg_text += "中了一等奖！"
        # 按人数分文案
        if len(big_winners) > 1:
            msg_text += f"每人"
        else:
            msg_text += f"你"

        msg_text += f"获得[{big_reward_per_winner}]颗草莓！草莓已经发放至你的银行账户里面了哦！请通过`.ck all`查看\n\n"
        
    else:
        msg_text += "很遗憾，本次无人中一等奖！\n\n"

    if winners:
        reward_per_winner = total_reward // len(winners)
        msg_text += "🎊 恭喜 "
        total_refund += reward_per_winner * len(winners)
        
        for winner in winners:
            bar_data[str(winner)]["bank"] += reward_per_winner
            bar_data[str(winner)]["double_ball"]["prize"] = reward_per_winner
            msg_text += MessageSegment.at(winner)  # @中奖者

        msg_text += "中了二等奖！"
        # 按人数分文案
        if len(winners) > 1:
            msg_text += "每人"
        else:
            msg_text += "你"

        msg_text += f"获得[{reward_per_winner}]颗草莓！草莓已经发放至你的银行账户里面了哦！请通过`.ck all`查看\n\n"

    else:
        msg_text += "很遗憾，本次无人中二等奖！\n\n"

    # 额外信息：只猜中一个数字的玩家
    if single_match_users:
        msg_text += '🎊 恭喜 '
        for user_id in single_match_users:
            msg_text += MessageSegment.at(user_id)
        msg_text += "猜中了单球，成功中了小奖哦！将获得入场费用的150%的草莓！请通过`.ck all`查看\n"

    # 扣除奖池金额
    bar_data["pots"] -= total_refund
    msg_text += f"\n当前奖池剩余{bar_data['pots']}颗草莓！"
    msg_text += f"\n\n若忘记开奖号码，可以通过命令 '.threeball (日期)' 来查询哦！"
    bar_data["double_ball_send"] = True  # 设置开奖标记

    save_data(bar_path, bar_data)

    await bot.send_group_msg(group_id=zhuama_group, message=msg_text)