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
            "本“游戏”入场费为125草莓\n" +
            "“游戏”开始时系统会为你从52张扑克牌（除去大小王）中随机抽取一张，你要做的就是猜测这一张牌\n" +
            "你的猜测可以是点数、大于/小于某值，或者具体的花色\n" +
            "如果猜对了，你将获得大量草莓奖励！祝你好运~\n" +
            "输入.bet 1 游玩此“游戏”"
        )
    elif game_type == '2':
        await rule.finish(
            "“游戏”2：恶魔轮盘du(2人)\n" +
            "本“游戏”入场费为125草莓\n" +
            "“游戏”开始时，双方的血量在区间内随机（上限为6），并且都可以获得等量道具，然后由随机一人开始\n" +
            "在枪里面有不定量的子弹，实弹空弹随机\n" +
            "你可以向自己开枪，也可以向对方开枪，向自己开枪后无论是否实弹下一回合都是你行动\n" +
            "如果你向对方开枪，无论是否实弹都是对方行动\n" +
            "在回合内，每个人都可以使用道具，道具内容可以使用 .恶魔道具 查看\n" +
            "获胜的一方将获得466颗草莓奖励~\n" +
            "注意！步时为10min，使用道具和开枪（无论是否自己）都会刷新步时！若超时对方返还草莓，本回合玩家不返还！\n" +
            "使用 .恶魔帮助 指令可以查看所有的指令~ \n" +
            "输入 .bet 2 游玩此“游戏”"
        )
    elif game_type == '3':
        await rule.finish(
            "“游戏”3：Madeline竞技场竞猜\n" +
            "本“游戏”入场费为150草莓\n" +
            "用 `.bet 3/擂台号码` 竞猜一个擂台，当该擂台的玛德琳被踢下或替换时，你会得到（（120-原擂主常驻战力）*原擂主存活回合数*0.15）*（3/4））的奖励。\n" +
            "如果本局擂台结束，将给所有参与竞猜的玩家发对应的草莓，并存储在du场里！请通过 `.ck` 查看哦！\n" +
            "可以使用命令 `.bank take 数量/all` 从du场中提取草莓哦！\n"+
            "你在竞猜的时候同时也能玩其他“游戏”哦！\n" +
            "注意1：每局Madeline竞技场只能使用竞猜一次！\n" +
            "注意2：不能对在场超过5回合的玛德琳下注"
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
    try:
        game_type_split = args.strip().split("/") # 检测需不需要分割
        game_type = game_type_split[0]
        second_game_type = game_type_split[1]
    except:
        game_type = args  # 获取玩家选择的“游戏”
        second_game_type = False
    # 如果该用户不在用户名单中，则先抓
    if user_id not in data:
        if(not 'berry' in data[str(user_id)]):
            data[user_id]['berry'] = 0
        await bet.finish("请先抓一次madeline再来玩“游戏”哦！", at_sender=True)
    # 如果该用户不在酒馆名单中，则先创建数据
    if user_id not in bar_data:
        bar_data[user_id] = {}
        bar_data[user_id]['status'] = 'nothing'
    # 添加全局冷却
    now_time = time.time()
    cd_data = open_data(cd_path)
    if user_id not in cd_data:
        cd_data[user_id] = {}
    if group_id not in cd_data:
         cd_data['group']= {}
         cd_data['group'][group_id] = {}
    cd_data[user_id]["coldtime"] = now_time
    cd_data['group'][group_id]["coldtime"] = now_time
    save_data(cd_path, cd_data)
    # 写入数据
    save_data(full_path, data)
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
    if(data[str(user_id)].get('buff','normal')=='confuse' ) and game_type != "2": 
        await bet.finish(f"你现在正在找到了个碎片，疑惑着呢，不能玩“游戏”。", at_sender=True)
    if(data[str(user_id)].get('buff','normal')=='hurt') and game_type != "2": 
        await bet.finish(f"你现在受伤了，没有精力玩“游戏”！", at_sender=True)
    if(data[str(user_id)].get('status','nornal')=='working' and game_type != "2"): 
        await bet.finish(f"你正在维护草莓加工器中，没有精力玩除了恶魔轮盘以外的其他“游戏”！", at_sender=True)
    # 如果该用户不在酒馆名单中，则先创建数据
    if user_id not in bar_data:
        bar_data[user_id] = {}
        bar_data[user_id]['status'] = 'nothing'

    if bar_data[user_id]['status'] != 'nothing':
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
            hp = random.randint(3 + int(add_max*1.5), 6+add_max*2)
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
        # if user_id != '121096913':
        #     await bet.finish("目前还有bug，暂不支持哦！", at_sender=True)
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
    now_time = time.time()
    cd_data = open_data(cd_path)
    if user_id not in cd_data:
        cd_data[user_id] = {}
    if group_id not in cd_data:
         cd_data['group']= {}
         cd_data['group'][group_id] = {}
    cd_data[user_id]["coldtime"] = now_time
    cd_data['group'][group_id]["coldtime"] = now_time
    save_data(cd_path, cd_data)
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
        "大于7": 260,
        "小于7": 260,
        "花色": 480,
        "点数": 780
    }

    if len(guess_type) != 1 and len(guess_type) != 2:
        await guess.finish(message="请输入一个正确的猜测值", at_sender=True)
    elif len(guess_type) == 1:
        guess_type = guess_type[0]
        if guess_type == "大于7":
            original_berry = int(REWARD_MAPPING[guess_type])
            tax = int(original_berry*0.25)
            berry = int(original_berry - tax)
            if card_value > 7:
                data[user_id]['berry'] += berry
                msg_text = f"你抽到的牌是{card_type}{card_name}，点数大于7，你的猜测成功了！获得{original_berry}颗草莓奖励！但是由于草莓税法的实行，需要上交25%，所以你最终获得了{berry}颗草莓，上交了{tax}颗草莓税！"
            else:
                msg_text = f"你抽到的牌是{card_type}{card_name}，点数小于等于7，你的猜测失败了！"
        elif guess_type == "小于7":
            original_berry = int(REWARD_MAPPING[guess_type])
            tax = int(original_berry*0.25)
            berry = int(original_berry - tax)
            if card_value < 7:
                data[user_id]['berry'] += berry
                msg_text = f"你抽到的牌是{card_type}{card_name}，点数小于7，你的猜测成功了！获得{original_berry}颗草莓奖励！但是由于草莓税法的实行，需要上交25%，所以你最终获得了{berry}颗草莓，上交了{tax}颗草莓税！"
            else:
                msg_text = f"你抽到的牌是{card_type}{card_name}，点数大于等于7，你的猜测失败了！"
        elif guess_type in ["梅花", "方片", "黑桃", "红桃"]:
            send_guess_type = "花色"
            original_berry = int(REWARD_MAPPING[send_guess_type])
            tax = int(original_berry*0.25)
            berry = int(original_berry - tax)
            if card_type == guess_type:
                data[user_id]['berry'] += berry
                msg_text = f"你抽到的牌是{card_type}{card_name}，你的猜测成功了！获得{original_berry}颗草莓奖励！但是由于草莓税法的实行，需要上交25%，所以你最终获得了{berry}颗草莓，上交了{tax}颗草莓税！"
            else:
                msg_text = f"你抽到的牌是{card_type}{card_name}，你的猜测失败了！"
        else:
            await guess.finish(message="请输入一个正确的猜测值", at_sender=True)
    elif len(guess_type) == 2:
        send_guess_type = "点数"
        original_berry = int(REWARD_MAPPING[send_guess_type])
        tax = int(original_berry*0.25)
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
                    msg_text = f"你抽到的牌是{card_type}{card_name}，你的猜测成功了！获得奇想扑克！\n输入.cp 奇想扑克 以查看具体效果"
                else:
                    data[user_id]['berry'] += berry
                    msg_text = f"你抽到的牌是{card_type}{card_name}，你的猜测成功了！获得{original_berry}颗草莓奖励！但是由于草莓税法的实行，需要上交25%，所以你最终获得了{berry}颗草莓，上交了{tax}颗草莓税！"    
            else:                
                data[user_id]['berry'] += berry
                msg_text = f"你抽到的牌是{card_type}{card_name}，你的猜测成功了！获得{original_berry}颗草莓奖励！但是由于草莓税法的实行，需要上交25%，所以你最终获得了{berry}颗草莓，上交了{tax}颗草莓税！"
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
    }
# 身份模式道具列表
item_dic2 = { 
    15: '双转团',
    16: '天秤', 
    17: '休养生息',
    18: '玩具枪',
    19: '烈弓',
    20: '血刃',
    21: '黑洞',
    22: '金苹果',
    23: '铂金草莓',
    24: '肾上腺素',
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

# 定义不同状态对应的轮数限制
turn_limit = {
    1: death_turn,  # "死斗模式" 开启的轮数限制
    2: 1,    # "膀胱模式" 开启的轮数限制
    999: 1    # "跑团专用999模式" 开启的轮数限制
}

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
    "双转团": "（该道具为“身份”模式专属道具）把这个道具转移到对方道具栏里，若对方道具已达上限则丢弃本道具，无其他效果。但由于其富含identity，可能有其他的非bet2游戏内的效果？",
    "天秤": "（该道具为“身份”模式专属道具）如果你的道具数量≥对方道具数量，你对对方造成一点伤害；你的道具数量<对方道具数量，你回一点血",
    "休养生息": "（该道具为“身份”模式专属道具）自己的hp恢复2，对方的hp恢复1，不跳回合",
    "玩具枪": "（该道具为“身份”模式专属道具）1/2的概率无事发生，1/2的概率对对面造成1点伤害",
    "烈弓": "（该道具为“身份”模式专属道具）使用烈弓后，下一发子弹伤害+1，且伤害类道具（小刀、酒、烈弓）的加伤效果可以无限叠加！",
    "血刃": "（该道具为“身份”模式专属道具）可以扣除自己1点hp，获得两个道具！并且获得的道具直到本轮实弹耗尽前可以超出上限（本轮实弹耗尽后超出上限的道具会消失）",
    "黑洞": "（该道具为“身份”模式专属道具）召唤出黑洞，随机夺取对方的任意一个道具！\n如果对方没有道具，黑洞将在沉寂中回到你的身边。",
    "金苹果": "（该道具为“身份”模式专属道具）金苹果可以让你回复3点hp！但是作为代价你会跳过接下来的两个回合！不过对面的手铐和禁止卡也似乎不能使用了……",
    "铂金草莓": "（该道具为“身份”模式专属道具）因为是铂金草莓，所以能做到！自己回复1点hp，并且双方各加1点hp上限！",
    "肾上腺素": "（该道具为“身份”模式专属道具）双方的hp上限-1，道具上限+1，并且使用者获得一个新道具！如果你的血量大于hp上限，血量会被强制调整到hp上限！并且如果你们的hp上限为1，无法使用该道具！",
}

help_msg = f"""
输入 .开枪 自己/对方 -|- 向自己/对方开枪
输入 .查看局势 -|- 查看当前局势
输入 .恶魔道具 道具名/all -|- 查看道具的使用说明
输入 .恶魔投降 -|- 进行投降
输入 .使用道具 道具名 -|- 使用道具"""

# 奖励设置
jiangli = 466
bet_tax = (jiangli * 25) // 100  # 向下取整计算 25%
final_jiangli = jiangli - bet_tax

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
    identity_mode_items = [3, 4, 8, 18] # 身份模式需要增加权重的道具（放大镜，眼镜，小刀，玩具枪）
    
    # 动态生成权重表
    weights = {i: 0 for i in range(1, item_count + 1)}  # 初始化所有道具权重为0
    
    if identity_found == 0:
        # 普通模式：前 normal_mode_limit 个道具权重设为1，其他保持0
        for i in range(1, normal_mode_limit + 1):
            weights[i] = 1
    else:
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
        msg +=f'\n- 你开枪了，子弹未击中{args}！{args}剩余hp：{str(hp[pl-stp])}/{hp_max}\n'
    del clip[-1]

    if len(clip) == 0 or clip.count(1) == 0:
        msg += '- 子弹用尽，重新换弹，道具更新！\n'
        # 游戏轮数+1
        demon_data[group_id]['game_turn'] += 1
        # 判断是否开启死斗模式：根据不同的状态和轮数进行血量上限扣减
        if identity_found in turn_limit and demon_data[group_id]['game_turn'] > turn_limit[identity_found]:
            msg += f'- 轮数大于{turn_limit[identity_found]}，死斗模式开启！\n'
            if identity_found in [1,2] and demon_data[group_id]["hp_max"] > 1:
                demon_data[group_id]["hp_max"] -= 1
                new_hp_max = demon_data[group_id]["hp_max"]
                msg += f'- {new_hp_max+1}>1，扣1点hp上限，当前hp上限：{new_hp_max}\n'
                # 校准所有玩家血量不得超过hp上限
                for player_index, player_id in enumerate(demon_data[group_id]['pl']):
                    current_hp = demon_data[group_id]["hp"][player_index]
                    if current_hp > new_hp_max:
                        demon_data[group_id]["hp"][player_index] = new_hp_max
                        
            # 跑团专用999模式，就是极速模式的基础上加了一个hpmax-2
            elif identity_found == 999 and demon_data[group_id]["hp_max"] > 1:
                old_hp_max = demon_data[group_id]["hp_max"]
                demon_data[group_id]["hp_max"] -= 2
                if demon_data[group_id]["hp_max"] <= 1:
                    demon_data[group_id]["hp_max"] = 1
                new_hp_max = demon_data[group_id]["hp_max"]
                msg += f'- {old_hp_max}>1，扣2点hp上限，当前hp上限：{new_hp_max}\n'
                # 校准所有玩家血量不得超过hp上限
                for player_index, player_id in enumerate(demon_data[group_id]['pl']):
                    current_hp = demon_data[group_id]["hp"][player_index]
                    if current_hp > new_hp_max:
                        demon_data[group_id]["hp"][player_index] = new_hp_max

        msg += f'- 当前轮数：{demon_data[group_id]['game_turn']}\n\n'
        # 重新获取hp_max
        hp_max = demon_data.get(group_id, {}).get('hp_max')
        clip = load()
        for i in range(random.randint(1+pangguang_add,3+add_max)):
            demon_data[group_id]['item_0'].append(get_random_item(identity_found, len(item_dic) - idt_len, player0))
            demon_data[group_id]['item_1'].append(get_random_item(identity_found, len(item_dic) - idt_len, player1))
        # 检查并限制道具数量上限为max
        demon_data[group_id]['item_0'] = demon_data[group_id]['item_0'][:item_max]  # 截取前max个道具
        demon_data[group_id]['item_1'] = demon_data[group_id]['item_1'][:item_max]  # 截取前max个道具
        hp0 = demon_data[group_id]["hp"][0]
        hp1 = demon_data[group_id]["hp"][1]
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
        msg += MessageSegment.at(player1) + f"\nhp：{hp1}/{hp_max}\n" + f"道具({len(items_1)}/{item_max})：" +f"\n{item_1}\n\n"
    
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
        user_data[winner]['berry'] += final_jiangli
        msg += '- 游戏结束！' + MessageSegment.at(str(winner))+ f'胜利！恭喜获得{jiangli}颗草莓！但是由于草莓税法的实行，需要上交25%，所以你最终获得了{final_jiangli}颗草莓，上交了{bet_tax}颗草莓税！'
        rndshenfen = random.randint(1,4)
        if rndshenfen == 1:
            #判断是否开辟藏品栏
            if(not 'collections' in user_data[str(winner)]):
                user_data[str(winner)]['collections'] = {}
            #是否已经持有藏品"身份徽章"
            #如果没有，则添加
            if(not '身份徽章' in user_data[str(winner)]['collections']):
                user_data[str(winner)]['collections']['身份徽章'] = 1
                msg += f"\n\n游戏结束时，你意外从桌子底下看到了一个亮闪闪的徽章，上面写着“identity”，你感到十分疑惑，便捡了起来。输入.cp 身份徽章 以查看具体效果"
        # 移除两位玩家游戏状态
        bar_data[player0]['game'] = '1'
        bar_data[player0]['status'] = 'nothing'
        bar_data[player1]['game'] = '1'
        bar_data[player1]['status'] = 'nothing'
        # 初始化pots
        bar_data.setdefault("pots", 0)
        # 加入奖池
        bar_data["pots"] += bet_tax
        if demon_data[group_id]['game_turn'] > death_turn:
            if user_data[player0].get("pangguang", 0) == 0 or user_data[player1].get("pangguang", 0) == 0:
                msg += f"\n- 你们已经打了{demon_data[group_id]['game_turn']}轮，超过{death_turn}轮了……这股膀胱的怨念射入身份徽章里面！现在你们的身份徽章已解锁极速模式！就算暂时没有身份徽章以后也能直接切换！请使用 .use 身份徽章/2 切换！"
            # 设置玩家的 pangguang 状态为 1
            user_data[player0]["pangguang"] = 1
            user_data[player1]["pangguang"] = 1
        # 重置游戏
        demon_data[group_id] = demon_default
        demon_data[group_id]['demon_coldtime'] = int(int(time.time()) + 60*20) # 20min冷却
        # 写入主数据
        save_data(full_path, user_data)
    elif demon_data[group_id]['hp'][1] <= 0:
        winner = demon_data[group_id]['pl'][0]
        user_data[winner]['berry'] += final_jiangli
        msg += '- 游戏结束！' + MessageSegment.at(str(winner))+ f'胜利！恭喜获得{jiangli}颗草莓！但是由于草莓税法的实行，需要上交25%，所以你最终获得了{final_jiangli}颗草莓，上交了{bet_tax}颗草莓税！'
        rndshenfen = random.randint(1,4)
        if rndshenfen == 1:
            #判断是否开辟藏品栏
            if(not 'collections' in user_data[str(winner)]):
                user_data[str(winner)]['collections'] = {}
            #是否已经持有藏品"身份徽章"
            #如果没有，则添加
            if(not '身份徽章' in user_data[str(winner)]['collections']):
                user_data[str(winner)]['collections']['身份徽章'] = 1
                msg += f"\n\n游戏结束时，你意外从桌子底下看到了一个亮闪闪的徽章，上面写着“identity”，你感到十分疑惑，便捡了起来。输入.cp 身份徽章 以查看具体效果"
        # 移除两位玩家游戏状态
        bar_data[player0]['game'] = '1'
        bar_data[player0]['status'] = 'nothing'
        bar_data[player1]['game'] = '1'
        bar_data[player1]['status'] = 'nothing'
        # 初始化pots
        bar_data.setdefault("pots", 0)
        # 加入奖池
        bar_data["pots"] += bet_tax
        if demon_data[group_id]['game_turn'] > death_turn:
            if user_data[player0].get("pangguang", 0) == 0 or user_data[player1].get("pangguang", 0) == 0:
                msg += f"\n- 你们已经打了超过death_turn轮了……这股膀胱的怨念射入身份徽章里面！现在你们的身份徽章已解锁极速模式！就算暂时没有身份徽章以后也能直接切换！请使用 .use 身份徽章/2 切换！"
            # 设置玩家的 pangguang 状态为 1
            user_data[player0]["pangguang"] = 1
            user_data[player1]["pangguang"] = 1
        # 重置游戏
        demon_data[group_id] = demon_default
        demon_data[group_id]['demon_coldtime'] =  int(int(time.time()) + 60*20)# 20min冷却
        # 写入主数据
        save_data(full_path, user_data)
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
    now_time = time.time()
    cd_data = open_data(cd_path)
    if user_id not in cd_data:
        cd_data[user_id] = {}
    if group_id not in cd_data:
         cd_data['group']= {}
         cd_data['group'][group_id] = {}
    cd_data[user_id]["coldtime"] = now_time
    cd_data['group'][group_id]["coldtime"] = now_time
    save_data(cd_path, cd_data)
    
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
    now_time = time.time()
    cd_data = open_data(cd_path)
    if user_id not in cd_data:
        cd_data[user_id] = {}
    if group_id not in cd_data:
         cd_data['group']= {}
         cd_data['group'][group_id] = {}
    cd_data[user_id]["coldtime"] = now_time
    cd_data['group'][group_id]["coldtime"] = now_time
    save_data(cd_path, cd_data)
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
    player_items = demon_data[group_id][f"item_{player_turn}"]
    opponent_turn = (player_turn + 1) % len(demon_data[group_id]['pl'])
    opponent_items = demon_data[group_id][f"item_{opponent_turn}"]
    # 道具名称匹配
    if args not in item_dic.values():  # 检查输入的名称是否存在于 item_dic
        await prop_demon.finish("你输入的道具不存在，请确认后再使用！")

    # 查找玩家的道具中是否存在该道具
    try:
        # 遍历玩家的道具ID，找到第一个匹配的道具名称
        item_idx = next(i for i, item_id in enumerate(player_items) if item_dic[item_id] == args)
    except StopIteration:
        await prop_demon.finish("你并没有这个道具，请确认后再使用！", at_sender = True)

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
            msg += f"只剩最后一颗子弹：{'实弹' if demon_data[group_id]['clip'][-1] == 1 else '空弹'}\n"

    elif item_name == "手铐":
        if demon_data[group_id]['hcf'] == 0:
            demon_data[group_id]['hcf'] = 1
            msg += "你成功拷住了对方！\n"
        else:
            player_items.append(5)
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
                opponent_items.append(14)  # 只有在对方道具少于 max_item 个时才增加禁止卡
                msg += f"你成功禁止住了对方！禁止了{skip_turn}个回合，但同时对方也获得了一张禁止卡！\n"
            else:
                msg += f"你成功禁止住了对方！禁止了{skip_turn}个回合，但对方道具已满，并未获得这张禁止卡！\n"
        else:
            player_items.append(14)
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
            # 判断是否开启死斗模式：根据不同的状态和轮数进行血量上限扣减
            if identity_found in turn_limit and demon_data[group_id]['game_turn'] > turn_limit[identity_found]:
                msg += f'- 轮数大于{turn_limit[identity_found]}，死斗模式开启！\n'

                if identity_found in [1,2] and demon_data[group_id]["hp_max"] > 1:
                    demon_data[group_id]["hp_max"] -= 1
                    new_hp_max = demon_data[group_id]["hp_max"]
                    msg += f'- {new_hp_max+1}>1，扣1点hp上限，当前hp上限：{new_hp_max}\n'

                    # 校准所有玩家血量不得超过hp上限
                    for player_index, player_id in enumerate(demon_data[group_id]['pl']):
                        current_hp = demon_data[group_id]["hp"][player_index]
                        if current_hp > new_hp_max:
                            demon_data[group_id]["hp"][player_index] = new_hp_max
                # 跑团专用999模式，就是极速模式的基础上加了一个hpmax-2
                elif identity_found == 999 and demon_data[group_id]["hp_max"] > 1:
                    old_hp_max = demon_data[group_id]["hp_max"]
                    demon_data[group_id]["hp_max"] -= 2
                    if demon_data[group_id]["hp_max"] <= 1:
                        demon_data[group_id]["hp_max"] = 1
                    new_hp_max = demon_data[group_id]["hp_max"]
                    msg += f'- {old_hp_max}>1，扣2点hp上限，当前hp上限：{new_hp_max}\n'

                    # 校准所有玩家血量不得超过hp上限
                    for player_index, player_id in enumerate(demon_data[group_id]['pl']):
                        current_hp = demon_data[group_id]["hp"][player_index]
                        if current_hp > new_hp_max:
                            demon_data[group_id]["hp"][player_index] = new_hp_max
                            
            msg += f'- 当前轮数：{demon_data[group_id]['game_turn']}\n\n'
            msg += f"- 新弹夹总数：{len(demon_data[group_id]['clip'])} 实弹数：{demon_data[group_id]['clip'].count(1)}\n\n"
            player0 = str(demon_data[group_id]['pl'][0])
            player1 = str(demon_data[group_id]['pl'][1])
            hp0 = demon_data[group_id]["hp"][0]
            hp1 = demon_data[group_id]["hp"][1]
            # 重新获取hp_max
            hp_max = demon_data.get(group_id, {}).get('hp_max')
            for i in range(random.randint(1+pangguang_add,3+add_max)):
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
        if len(opponent_items) < item_max:
            opponent_items.append(15)  # 只有在对方道具少于 max_item 个时才获得双转团
            msg += f"这件物品太“IDENTITY”了，对方十分感兴趣，所以拿走了这件物品！\n"
        else:
            msg += f"这件物品太“IDENTITY”了，对方十分感兴趣，但是由于道具已满，没办法拿走这件物品，所以把双转团丢了！\n"
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
        demon_data[group_id]["hp"][player_turn] += 2
        demon_data[group_id]["hp"][opponent_turn] += 1
        if demon_data[group_id]["hp"][player_turn] >= hp_max:
            demon_data[group_id]["hp"][player_turn] = hp_max
        if demon_data[group_id]["hp"][opponent_turn] >= hp_max:
            demon_data[group_id]["hp"][opponent_turn] = hp_max
        msg += f"休养生息，备战待敌；止兵止战，休养生息。\n你恢复了2点体力，对方恢复了1点体力（最高恢复至上限）。\n\n你的体力为{demon_data[group_id]["hp"][player_turn]}/{hp_max}\n对方的体力为{demon_data[group_id]["hp"][opponent_turn]}/{hp_max}\n"
    
    elif item_name == "玩具枪":
        randchoice = random.randint(1, 2)
        if randchoice == 1:
            demon_data[group_id]["hp"][opponent_turn] -= 1
            msg += f"你使用了玩具枪，可没想到里面居然是真弹！你对对面造成了一点伤害！\n对方目前剩余hp为：{demon_data[group_id]['hp'][opponent_turn]}\n"    
        else: 
            msg += f"你使用了玩具枪，这确实是一个可以滋水的玩具水枪，无事发生。\n"
    
    elif item_name == "血刃":
        if demon_data[group_id]["hp"][player_turn] == 1:
            player_items.append(20)
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
            player_items.append(21)
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
            player_items.append(24) 
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
            for player_id in demon_data[group_id]['pl']:
                player_index = demon_data[group_id]['pl'].index(player_id)
                current_hp = demon_data[group_id]["hp"][player_index]
                if current_hp > new_hp_max:
                    demon_data[group_id]["hp"][player_index] = new_hp_max
            msg += (
                f"你注射了肾上腺素！心跳如雷，时间仿佛放慢，力量在血管中沸腾！\n"
                f"- 双方道具上限+1！\n"
                f"- 你获得了新道具：{new_item_name}\n"
                f"- 当前道具上限：{item_max}\n\n"
                f"然而，一丝生命力被悄然抽离……对手也感到一阵莫名的心悸。\n"
                f"- 双方HP上限 -1！\n"
                f"- 当前HP上限：{hp_max}\n"
            )
    else:
        msg += "道具不存在或无法使用！\n"

    next_player_turn = demon_data[group_id]['turn']  # 获取下一位玩家的 turn
    next_player_id = str(demon_data[group_id]["pl"][next_player_turn])  # 下一位玩家的 ID
    msg += "\n- 现在轮到" + MessageSegment.at(str(next_player_id)) + "行动！"
    if demon_data[group_id]['hp'][0] <= 0: 
        winner = demon_data[group_id]['pl'][1]
        user_data[winner]['berry'] += final_jiangli
        msg += '\n- 游戏结束！' + MessageSegment.at(str(winner))+ f'胜利！恭喜获得{jiangli}颗草莓！但是由于草莓税法的实行，需要上交25%，所以你最终获得了{final_jiangli}颗草莓，上交了{bet_tax}颗草莓税！'
        # 初始化pots
        bar_data.setdefault("pots", 0)
        # 加入奖池
        bar_data["pots"] += bet_tax
        rndshenfen = random.randint(1,4)
        if rndshenfen == 1:
            #判断是否开辟藏品栏
            if(not 'collections' in user_data[str(winner)]):
                user_data[str(winner)]['collections'] = {}
            #是否已经持有藏品"身份徽章"
            #如果没有，则添加
            if(not '身份徽章' in user_data[str(winner)]['collections']):
                user_data[str(winner)]['collections']['身份徽章'] = 1
                msg += f"\n\n游戏结束时，你意外从桌子底下看到了一个亮闪闪的徽章，上面写着“identity”，你感到十分疑惑，便捡了起来。输入.cp 身份徽章 以查看具体效果"
        # 生成玩家信息
        player0 = str(demon_data[group_id]['pl'][0])
        player1 = str(demon_data[group_id]['pl'][1])
        # 移除两位玩家游戏状态
        bar_data[player0]['game'] = '1'
        bar_data[player0]['status'] = 'nothing'
        bar_data[player1]['game'] = '1'
        bar_data[player1]['status'] = 'nothing'
        if demon_data[group_id]['game_turn'] > death_turn:
            if user_data[player0].get("pangguang", 0) == 0 or user_data[player1].get("pangguang", 0) == 0:
                msg += f"\n- 你们已经打了{demon_data[group_id]['game_turn']}轮，超过{death_turn}轮了……这股膀胱的怨念射入身份徽章里面！现在你们的身份徽章已解锁极速模式！就算暂时没有身份徽章以后也能直接切换！请使用 .use 身份徽章/2 切换！"
            # 设置玩家的 pangguang 状态为 1
            user_data[player0]["pangguang"] = 1
            user_data[player1]["pangguang"] = 1
        # 重置游戏
        demon_data[group_id] = demon_default
        demon_data[group_id]['demon_coldtime'] = int(int(time.time()) + 60*20) # 20min冷却
        # 写入主数据
        save_data(full_path, user_data)
    elif demon_data[group_id]['hp'][1] <= 0:
        winner = demon_data[group_id]['pl'][0]
        user_data[winner]['berry'] += final_jiangli
        msg += '\n- 游戏结束！' + MessageSegment.at(str(winner))+ f'胜利！恭喜获得{jiangli}颗草莓！但是由于草莓税法的实行，需要上交25%，所以你最终获得了{final_jiangli}颗草莓，上交了{bet_tax}颗草莓税！'
        # 初始化pots
        bar_data.setdefault("pots", 0)
        # 加入奖池
        bar_data["pots"] += bet_tax
        rndshenfen = random.randint(1,4)
        if rndshenfen == 1:
            #判断是否开辟藏品栏
            if(not 'collections' in user_data[str(winner)]):
                user_data[str(winner)]['collections'] = {}
            #是否已经持有藏品"身份徽章"
            #如果没有，则添加
            if(not '身份徽章' in user_data[str(winner)]['collections']):
                user_data[str(winner)]['collections']['身份徽章'] = 1
                msg += f"\n\n游戏结束时，你意外从桌子底下看到了一个亮闪闪的徽章，上面写着“identity”，你感到十分疑惑，便捡了起来。输入.cp 身份徽章 以查看具体效果"
        # 生成玩家信息
        player0 = str(demon_data[group_id]['pl'][0])
        player1 = str(demon_data[group_id]['pl'][1])
        if demon_data[group_id]['game_turn'] > death_turn:
            if user_data[player0].get("pangguang", 0) == 0 or user_data[player1].get("pangguang", 0) == 0:
                msg += f"\n- 你们已经打了{demon_data[group_id]['game_turn']}轮，超过{death_turn}轮了……这股膀胱的怨念射入身份徽章里面！现在你们的身份徽章已解锁极速模式！就算暂时没有身份徽章以后也能直接切换！请使用 .use 身份徽章/2 切换！"
            # 设置玩家的 pangguang 状态为 1
            user_data[player0]["pangguang"] = 1
            user_data[player1]["pangguang"] = 1
        # 移除两位玩家游戏状态
        bar_data[player0]['game'] = '1'
        bar_data[player0]['status'] = 'nothing'
        bar_data[player1]['game'] = '1'
        bar_data[player1]['status'] = 'nothing'
        # 重置游戏
        demon_data[group_id] = demon_default
        demon_data[group_id]['demon_coldtime'] =  int(int(time.time()) + 60*20)# 20min冷却
        # 写入主数据
        save_data(full_path, user_data)
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
    remaining_seconds = 600 - elapsed# 计算剩余冷却时间
    remaining_minutes = remaining_seconds // 60  # 剩余分钟数
    remaining_seconds = remaining_seconds % 60  # 剩余秒数
    msg = "- 本局模式："
    if identity_found == 1:
        # death_turn轮以后死斗模式显示
        if demon_data[group_id]['game_turn'] > death_turn:
            msg += '（死斗）'
        msg += "身份模式\n"
    elif identity_found in [2,999]:
        # 1轮以后死斗模式显示
        if demon_data[group_id]['game_turn'] > 1:
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
    user_data = open_data(full_path)  # 加载用户数据
    bar_data = open_data(bar_path)  # 加载bar数据

    # 判断玩家是否在游戏中
    if demon_data[group_id]['start'] == False:
        await demon_surrender.finish("当前没有进行中的游戏！", at_sender=True)
    # 获取当前游戏的玩家信息
    players = demon_data[group_id]['pl']  # 当前游戏中的两位玩家ID
    if player_id not in players:
        await demon_surrender.finish("你当前不在游戏中，无法投降！", at_sender=True)

    # 确定投降的玩家和获胜的玩家
    if player_id == players[0]:
        winner = players[1]
        loser = players[0]
    else:
        winner = players[0]
        loser = players[1]

    # 奖励设置
    user_data[winner]['berry'] += final_jiangli  # 给获胜玩家奖励

    msg = "玩家"+MessageSegment.at(loser)+"已投降。\n游戏结束，"+MessageSegment.at(winner)+f" 获胜！恭喜获得{jiangli}颗草莓！但是由于草莓税法的实行，需要上交25%，所以你最终获得了{final_jiangli}颗草莓，上交了{bet_tax}颗草莓税！"

    # 可能触发身份徽章的掉落
    rndshenfen = random.randint(1, 4)
    if rndshenfen == 1:
        if 'collections' not in user_data[winner]:
            user_data[winner]['collections'] = {}
        if '身份徽章' not in user_data[winner]['collections']:
            user_data[winner]['collections']['身份徽章'] = 1
            msg += f"\n\n游戏结束时，你意外从桌子底下看到了一个亮闪闪的徽章，上面写着“identity”，你感到十分疑惑，便捡了起来。输入 .cp 身份徽章 以查看具体效果"

    # 更新玩家的游戏状态
    bar_data[loser]['game'] = '1'
    bar_data[loser]['status'] = 'nothing'
    bar_data[winner]['game'] = '1'
    bar_data[winner]['status'] = 'nothing'
    # 初始化pots
    bar_data.setdefault("pots", 0)
    # 加入奖池
    bar_data["pots"] += bet_tax
    if demon_data[group_id]['game_turn'] > death_turn:
        if user_data[winner].get("pangguang", 0) == 0 or user_data[loser].get("pangguang", 0) == 0:
            msg += f"\n- 你们已经打了{demon_data[group_id]['game_turn']}轮，超过{death_turn}轮了……这股膀胱的怨念射入身份徽章里面！现在你们的身份徽章已解锁极速模式！就算暂时没有身份徽章以后也能直接切换！请使用 .use 身份徽章/2 切换！"
        # 设置玩家的 pangguang 状态为 1
        user_data[winner]["pangguang"] = 1
        user_data[loser]["pangguang"] = 1

    # 重置游戏状态
    demon_data[group_id] = demon_default
    demon_data[group_id]['demon_coldtime'] = int(time.time()) + 60 * 20  # 设置20分钟冷却

    # 保存更新的数据
    save_data(full_path, user_data)
    save_data(bar_path, bar_data)
    save_data(demon_path, demon_data)

    # 发送投降结果消息
    await demon_surrender.finish(msg)

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
    else:  # 如果是查询指定道具
        # 查询道具效果
        effect = item_effects.get(prop_name)

        if effect:
            # 如果找到道具效果，发送效果
            await prop_demon_query.finish(f"\n道具【{prop_name}】的效果是：\n{effect}", at_sender=True)
        else:
            # 如果没有找到道具，提示用户
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
    user_data = open_data(full_path)
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
    if elapsed > 600:  # 10分钟
        # 判断游戏是否开始
        if demon_data[group_id]['start']:
            # 获取双方玩家
            player_turn = demon_data[group_id]["turn"]
            opponent_turn = (player_turn + 1) % len(demon_data[group_id]['pl'])
            player = demon_data[group_id]['pl'][player_turn]
            non_current_player = demon_data[group_id]['pl'][opponent_turn]
            
            # 发草莓
            user_data[str(non_current_player)]['berry'] += final_jiangli
            rndshenfen = random.randint(1,4)
            msg = ''
            if rndshenfen == 1:
                #判断是否开辟藏品栏
                if(not 'collections' in user_data[str(non_current_player)]):
                    user_data[str(non_current_player)]['collections'] = {}
                #是否已经持有藏品"身份徽章"
                #如果没有，则添加
                if(not '身份徽章' in user_data[str(non_current_player)]['collections']):
                    user_data[str(non_current_player)]['collections']['身份徽章'] = 1
                    msg += f"\n\n游戏结束时，你意外从桌子底下看到了一个亮闪闪的徽章，上面写着“identity”，你感到十分疑惑，便捡了起来。输入.cp 身份徽章 以查看具体效果"
            # 生成玩家信息
            # 移除两位玩家游戏状态
            bar_data[player]['game'] = '1'
            bar_data[player]['status'] = 'nothing'
            bar_data[non_current_player]['game'] = '1'
            bar_data[non_current_player]['status'] = 'nothing'
            if demon_data[group_id]['game_turn'] > death_turn:
                if user_data[player].get("pangguang", 0) == 0 or user_data[non_current_player].get("pangguang", 0) == 0:
                    msg += f"\n- 你们已经打了{demon_data[group_id]['game_turn']}轮，超过{death_turn}轮了……这股膀胱的怨念射入身份徽章里面！现在你们的身份徽章已解锁极速模式！就算暂时没有身份徽章以后也能直接切换！请使用 .use 身份徽章/2 切换！"
                # 设置玩家的 pangguang 状态为 1
                user_data[player]["pangguang"] = 1
                user_data[non_current_player]["pangguang"] = 1
            # 重置游戏
            demon_data[group_id] = demon_default
            demon_data[group_id]['demon_coldtime'] =int(int(time.time()) + 60*20) # 20min冷却作为惩罚
            # 初始化pots
            bar_data.setdefault("pots", 0)
            # 加入奖池
            bar_data["pots"] += bet_tax
            save_data(demon_path, demon_data)
            save_data(full_path, user_data)
            save_data(bar_path, bar_data)
            # 发送通知
            await bot.send_group_msg(
                group_id=group_id,
                message=f"回合超时！当前回合玩家"+MessageSegment.at(player)+"自动判负，恭喜"+MessageSegment.at(non_current_player)+f"获胜！获得{jiangli}颗草莓！但是由于草莓税法的实行，需要上交25%，所以你最终获得了{final_jiangli}颗草莓，上交了{bet_tax}颗草莓税！" + msg
            )
            return True
        else:
            # 判断是否有人
            if len(demon_data[group_id]['pl']) == 1:
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
