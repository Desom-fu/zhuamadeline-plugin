from nonebot import on_command, on_fullmatch
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GROUP, Message
from .npc import npc_da
from .whitelist import whitelist_rule
from .config import liechang_count

__all__ = ['help', 'gong_gao', 'npc', 'cklc', 'pvpck']

# 查看帮助菜单和更新信息
help = on_fullmatch(
    ['.help', '。help'], 
    permission=GROUP, 
    priority=1, 
    block=True, rule=whitelist_rule
)

@help.handle()
async def zhua_help():
    text = (
        "游戏玩法及全部命令请前往抓kid/madeline wiki\n"
        "https://docs.qq.com/smartsheet/DVUZtQWlNTG1zZVhN\n"
        "进行查看\n"
        "此处仅列出常用指令，其它指令请看wiki：\n"
        "- .zhua: 抓一个madeline\n"
        "- .qd: 每日签到\n"
        "- .show (madeline名字): 展示抓过的madeline\n"
        "- .count (madeline名字): 查看该madeline数量\n"
        "- .ck (all): 查看草莓余额及一些其他状态\n"
        "- .mymadeline (猎场号): 查询对应猎场拥有的madeline及数量\n"
        "- .myitem/mycp: 查询自己拥有的道具/藏品\n"
        "- .jd (1,2,3): 查看自己抓madeline进度\n"
        "- .shop: 查看今日商品\n"
        "- .buy (数量)（道具名): 购买道具/藏品\n"
        "- .use (道具名): 使用道具/藏品"
    )
    await help.finish(text)

# 更新公告
gong_gao = on_fullmatch(
    ['.公告', '。公告'], 
    permission=GROUP, 
    priority=1, 
    block=True, rule=whitelist_rule
)

@gong_gao.handle()
async def gong_gao_handle():
    text = (
        "“那只狐娘在准备什么呢？”\n"
        "“听说她在准备4猎呢，这可是隔壁抓kid都没有达成过的猎场！”\n"
        "“也就是说……这回是她的原创吗？”\n"
        "“没错！据说4猎的玩法将会彻底不同……”\n"
        "“并且有足足10个独占藏品！”\n"
        "“我去，这么多啊！”\n"
        "“耐心等着吧，听说愚人节可能就会开放了？”"
    )
    await gong_gao.finish(text)

# NPC档案
npc = on_command(
    'npc', 
    permission=GROUP, 
    priority=1, 
    block=True, 
    rule=whitelist_rule
)

@npc.handle()
async def npc_handle(arg: Message = CommandArg()):
    name = str(arg).strip().lower()  # 将输入转换为小写
    npc_da_lower = {k.lower(): v for k, v in npc_da.items()}  # 将字典的键转换为小写
    if name in npc_da_lower: 
        await npc.finish(npc_da_lower[name])
    else:
        await npc.finish("未找到相关NPC信息。")

# 猎场信息
cklc = on_command(
    'cklc', 
    permission=GROUP, 
    priority=0, 
    block=True, rule=whitelist_rule
)

@cklc.handle()
async def cklc_handle(arg: Message = CommandArg()):
    # 猎场详细信息映射表
    LC_INFO = {
        0: '''· 猎场名称：madeline竞技场
· 危险等级：PVP！！！
· 描述：坐落在塞莱斯特山脚小镇中心的圆形竞技场，由狐娘Desom-fu建造。场地采用特殊的反重力技术，悬浮平台会随着比赛进程随机重组。这里每天都会举办"玛德琳擂台赛"，参赛者可以使用自己捕捉的玛德琳进行对战！竞技场外围常年聚集着贩卖能量饮料和稀有道具的商贩，空气中总是弥漫着兴奋的呐喊声和电子记分牌的嗡嗡声。
· 准入需求：在古代遗迹中抓到过30个1+2级、4个4级、1个5级玛德琳''',

        1: '''· 猎场名称：古代遗迹
· 危险等级：0
· 描述：被时间遗忘的石质建筑群半掩在沙土中，刻满未知符号的方尖碑静静矗立。偶尔能听到风中传来远古的低语，但从未发现声源所在。这里似乎被庇护着，似乎从未有危险事件发生过……
· 准入需求：无''',

        2: '''· 猎场名称：异域茂林
· 危险等级：1
· 描述：这里的植物似乎已经适应了其以黑暗为主且潮湿的环境。然而，由塞莱斯特山的魔力所驱动的奇异光球刺破了黑暗，使得这里的植物瞬间活跃了起来。但是这里的地形错综复杂，似乎十分容易迷路……
· 准入需求：指南针（非必须，但是强烈推荐购买！）''',
        
        3: '''· 猎场名称：翡翠矿井
· 危险等级：3
· 描述：深入地下的矿道中，岩壁上镶嵌着会自主发光的翡翠晶体。这些晶体形成的网状脉络如同活物般缓慢脉动，照亮了矿道深处各种各样的挖掘痕迹。并且，里面遗留了各种爆炸装置，似乎显示着随时都可能有人进来继续开采矿井……在门口有一所合金制的大门，不知何人所建造，每位需要进入矿井的人都得先通过大门的考验……
· 准入需求：持有5片神秘碎片；前三个猎场持有的5级Madeline种类加起来超过9种''',
        
        4: '''· 猎场名称：地下终端
· 危险等级：4
· 描述：这座庞大的地下综合设施充满了闪烁的全息投影和嗡嗡运转的量子服务器组。自动清洁机器人无声穿梭在合金走廊间，而墙壁上不断刷新的数据流显示着未知的监控画面。偶尔能瞥见身穿防护服的研究人员匆匆走过转角，但他们从不对来访者做出回应，仿佛被困在另一个时空的幻影。通风系统中持续传来模糊的电子语音："协议执行中…人员请勿靠近核心区…"。门口的一个巨大机器，似乎有身份检测装置，只有经过验证的人员才能进入。不过似乎实验室人员和某人达成了一条协议，需要满足一定的要求也能通过验证……
· 准入需求：持有50000点能量（消耗，一次性）；满足前3个猎场的Madeline竞技场的准入需求；残片、音矿、安定之音的持有总价值超过15000草莓
· 猎场加成：裸抓加成5草莓''',
        
        5: '''· 猎场名称：遗忘神庙
· 危险等级：？
· 描述：这座深藏于山下的寺庙似乎昏昏欲睡，仿佛赋予它生命的魔法已经消耗殆尽。但这个地方仍在散发着一种奇怪的气息，表明了它隐藏的秘密比人们想象的更多。
· 准入需求：？？？''',
        
        999: '''· 猎场名称：？？？
· 警告，警告，本猎场极度危险！
· 描述：滋滋——数据损坏——检测到不稳定的空间裂缝——滋滋——有报告称在其中看到了——滋滋——暂未开放——建议保持安全距离
· 准入需求：？？？'''
    }

    # 默认总览信息
    DEFAULT_TEXT = """####### 猎场信息 #######
· 0号猎场：madeline竞技场
危险等级：PVP！！！
· 1号猎场：古代遗迹
危险等级：0
· 2号猎场：异域茂林
危险等级：1
· 3号猎场：翡翠矿井
危险等级：3
· 4号猎场：地下终端
危险等级：4
· 5号猎场：遗忘神庙
危险等级：？"""

    args = str(arg).strip().lower()
    
    # 处理特殊符号和数字转换
    if args in ['?', '？']:
        number_arg = 999
    else:
        try:
            number_arg = int(args)
        except ValueError:
            return await cklc.finish(DEFAULT_TEXT)

    # 验证数字范围
    if 0 <= number_arg <= liechang_count or number_arg == 999:
        # 获取详细信息并格式化
        detail = LC_INFO.get(number_arg, "")
        text = f"####### {number_arg}号猎场 #######\n{detail}" if number_arg != 999 else f"####### 危险…… #######\n{detail}"
    else:
        text = DEFAULT_TEXT

    await cklc.finish(text)

# 竞技场细则
pvpck = on_fullmatch(
    ['.0场细则', '。0场细则'], 
    permission=GROUP, 
    priority=1, 
    block=True, rule=whitelist_rule
)

@pvpck.handle()
async def pvpck_handle():
    text = (
        "有关madeline竞技场细则：\n\n"
        "在本猎场，.zhua将会从自己的1/2/3猎收集池里抓取。\n"
        "竞技场内共十个擂台，抓取完后系统会自动放上十个擂台中的某一个。\n"
        "但是如果该擂台被占用了，就会发生一次PK来决定谁使用这个擂台。\n"
        "若干回合后，十个擂台上留下的人将会根据回合数和时间发放一定数目的草莓奖励!\n"
        "休息一段时间后就会重新开始哦！\n"
        "详细规则可以查看抓kid wiki！因为基础规则是一样的我懒得重新写抓madeline wiki了！"
    )
    await pvpck.finish(text)