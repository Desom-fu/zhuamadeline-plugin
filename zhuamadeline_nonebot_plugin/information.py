from nonebot import on_command, on_fullmatch
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GROUP, Message
from .npc import npc_da
from .whitelist import whitelist_rule

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
cklc = on_fullmatch(
    ['.cklc', '。cklc'], 
    permission=GROUP, 
    priority=0, 
    block=True, rule=whitelist_rule
)

@cklc.handle()
async def cklc_handle():
    text = (
        "####### 猎场信息 #######\n\n"
        "0号猎场：madeline竞技场\n"
        "危险等级：PVP！！！\n\n"
        "1号猎场：古代遗迹\n"
        "危险等级：0\n\n"
        "2号猎场：异域茂林\n"
        "危险等级：1\n\n"
        "3号猎场：翡翠矿井\n"
        "危险等级：3\n\n"
        "4号猎场：地下终端\n"
        "危险等级：4\n\n"
        "5号猎场：遗忘神庙\n"
        "危险等级：？"
    )
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