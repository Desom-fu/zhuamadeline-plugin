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
from .collection import collections
from .function import *
from .event import *
from .pvp import *
from .whitelist import whitelist_rule
from dataclasses import dataclass
from typing import Dict, List, Optional

# 定义配置数据结构
@dataclass
class MadelineConfig:
    data: Dict
    user_path: str
    name_list: Dict

# 全局配置
MADELINE_CONFIGS = {
    1: MadelineConfig(
        data=madeline_data1,
        user_path=user_path1,
        name_list=madeline_name_list1
    ),
    2: MadelineConfig(
        data=madeline_data2,
        user_path=user_path2,
        name_list=madeline_name_list2
    ),
    3: MadelineConfig(
        data=madeline_data3,
        user_path=user_path3,
        name_list=madeline_name_list3
    ),
    4: MadelineConfig(
        data=madeline_data4,
        user_path=user_path4,
        name_list=madeline_name_list4
    )
}

LEVEL_EFFECTS = {
    '5': {'work_per_hour': 1},
    '4': {'work_simple_chance': -10},
    '3': {'bonus_berry': 10},
    '2': {'bonus_berry': 3}
}

AREA_CONFIGS = {
    '丛林': {
        'duration': 3,
        'power_require': 200
    },
    '7d': {
        'duration': 4,
        'power_require': 325
    },
    'mauve': {
        'duration': 8,
        'power_require': 1200
    },
    'lxvi': {
        'duration': 12,
        'power_require': 4500
    }
}

FOOD_EFFECTS = {
    '树莓': {},
    '芒果': {'bonus_berry': 20},
    '杨桃': {'work_simple_chance': -10},
    '百香果': {'work_per_hour': 1},
    '菠萝': {'bonus_item': 1}
}

@dataclass
class WorkState:
    work_per_hour: int = 3
    work_simple_chance: int = 90
    bonus_berry: int = 0
    bonus_item: int = 0

def apply_effects(state: WorkState, effects: List[Dict]):
    """应用效果到工作状态"""
    for effect in effects:
        state.work_per_hour += effect.get('work_per_hour', 0)
        state.work_simple_chance += effect.get('work_simple_chance', 0)
        state.bonus_berry += effect.get('bonus_berry', 0)
        state.bonus_item += effect.get('bonus_item', 0)

work = on_command('外出', aliases={'work'}, permission=GROUP, priority=2, block=True, rule=whitelist_rule)

@work.handle()
async def work_handle(event: GroupMessageEvent, bot: Bot, arg: Message = CommandArg()):
    # 解析命令参数
    command = str(arg).split("/")
    if len(command) != 3:
        await work.finish("输入不合规，请按照以下格式输入:\n.work 工作区域/携带食物/派遣madeline的名称")
    
    area, food, madeline = [part.lower() for part in command]
    
    # 获取用户数据
    user_id = str(event.get_user_id())
    data = open_data(full_path)
    
    if user_id not in data:
        await work.finish("你还没尝试抓过madeline......")
    
    # 获取当前时间
    current_time = datetime.datetime.now()
    
    # 初始化工作数据
    user_info = data.setdefault(user_id, {})
    user_info.setdefault('working', False)
    user_info.setdefault('work_area', None)
    user_info.setdefault('work_per_hour', 3)
    user_info.setdefault('work_simple_chance', 90)
    user_info.setdefault('bonus_berry', 0)
    user_info.setdefault('bonus_item', 0)
    user_info.setdefault('work_skiptime', 0)
    user_info.setdefault('work_exp', 0)
    user_info.setdefault('last_work_time', current_time.strftime("%Y-%m-%d %H:%M:%S"))
    
    # 修改时间检查部分
    try:
        last_work_time = datetime.datetime.strptime(
            user_info['last_work_time'], "%Y-%m-%d %H:%M:%S"
        )
    except (KeyError, ValueError):
        # 如果格式错误或不存在，使用当前时间
        last_work_time = current_time
        user_info['last_work_time'] = current_time.strftime("%Y-%m-%d %H:%M:%S")
    
    # 检查是否已在工作中
    if user_info['working']:
        working_endtime = datetime.datetime.strptime(
            user_info['working_endtime'], "%Y-%m-%d %H:%M:%S"
        )
        if current_time < working_endtime:
            text = time_text(str(working_endtime - current_time))
            await work.finish(
                f"你已经派遣madeline出去工作了，耐心等待吧。他/她/它/TA大概会在{text}后完成工作",
                at_sender=True
            )
        else:
            await work.finish("工作已结束，请先输入 .workjd 来结束本次外出工作", at_sender=True)
    
    # 验证工作区域
    if area not in AREA_CONFIGS:
        await work.finish("输入不合规，请输入一个合理的工作区域", at_sender=True)
    
    # 验证体力
    power_require = AREA_CONFIGS[area]['power_require']
    if user_info['item'].get("体力", 0) < power_require:
        await work.finish(
            f"你的体力不足，总共需要{power_require}点，而你现在只有{user_info['item'].get("体力", 0)}点，先去补充体力吧",
            at_sender=True
        )
    
    # 验证食物
    if food not in FOOD_EFFECTS:
        await work.finish("输入不合规，请输入一个合理的食物", at_sender=True)
    
    if user_info['item'].get(food, 0) <= 0:
        await work.finish(f"你现在没有{food}", at_sender=True)
    
    # 消耗食物
    user_info['item'][food] -= 1
    if user_info['item'][food] <= 0:
        del user_info['item'][food]
    
    # 查找 madeline 信息
    madeline_info = find_madeline(madeline)
    if madeline_info == 0:
        await work.finish("输入不合规，你输入了一个不存在的madeline", at_sender=True)
    
    # 获取对应猎场数据
    lc = madeline_info[2]  # 猎场编号
    config = MADELINE_CONFIGS[int(lc)]  # 注意转换为int
    madeline_check = open_data(config.user_path)
    
    # 初始化工作状态
    state = WorkState()
        
    # 修改为（利用 find_madeline 返回的信息）：
    madeline_key = f"{madeline_info[0]}_{madeline_info[1]}"  # 等级_编号
    if madeline_check[user_id].get(madeline_key, 0) <= 0:
        await work.finish("你没有抓到过此madeline，或者此madeline数量为0", at_sender=True)

    madeline_check[user_id][madeline_key] -= 1
    apply_effects(state, [LEVEL_EFFECTS.get(madeline_info[0], {})])  # madeline_info[0] 是等级
    apply_effects(state, [FOOD_EFFECTS.get(food, {})])
    
    # 设置工作时间以及消耗体力，重置日期
    duration = AREA_CONFIGS[area]['duration']
    user_info['item']['体力'] -= power_require
    next_time = current_time + datetime.timedelta(hours=duration)
    
    # 检查日期是否不同（年月日）
    if last_work_time.date() != current_time.date():
        user_info['work_skiptime'] = 0  # 重置跳过次数
    
    # 更新用户数据
    user_info.update({
        'working': True,
        'working_endtime': next_time.strftime("%Y-%m-%d %H:%M:%S"),
        'last_work_time': current_time.strftime("%Y-%m-%d %H:%M:%S"),
        'work_area': area,
        'work_per_hour': state.work_per_hour,
        'work_simple_chance': state.work_simple_chance,
        'bonus_berry': state.bonus_berry,
        'bonus_item': state.bonus_item
    })
    
    # 保存数据
    save_data(full_path, data)
    save_data(config.user_path, madeline_check)
    
    await work.finish(f"你成功派遣[{madeline}]携带着[{food}]去[{area}]工作了！预计需要工作{duration}个小时！")


status_work = on_command('工作进度', aliases={'workjd','jdwork'}, permission=GROUP, priority=1, block=True, rule=whitelist_rule)
@status_work.handle()
async def status_work_handle(bot: Bot, Bot_event: GroupMessageEvent):
    #打开文件
    data = open_data(full_path)

    user_id = str(Bot_event.get_user_id())
    current_time = datetime.datetime.now()
    #是否工作过
    if(not 'working' in data[str(user_id)]):
        await status_work.finish(f"你还没有派遣madeline外出工作过", at_sender=True)
    #是否已经派遣madeline去工作了
    if data[str(user_id)]['working']:
        working_endtime = datetime.datetime.strptime(data.get(str(user_id)).get('working_endtime'), "%Y-%m-%d %H:%M:%S")
        if current_time < working_endtime:
            text = time_text(str(working_endtime-current_time))
            work_skiptime = int(data[str(user_id)]['work_skiptime'])
            time_delta = working_endtime - current_time
            minutes_remaining = int(time_delta.total_seconds() // 60)
            skip_power_require = (minutes_remaining // 2) * pow(2, work_skiptime) + 1
            await status_work.finish(f"你已经派遣madeline出去工作了，耐心等待吧。他/她/它/TA大概会在{text}后完成工作，工作完成后他自然会将工作日志汇报给您的哦\n"+
                                     f"今日你加速了{work_skiptime}次，本次加速你需要{skip_power_require}点体力", at_sender=True)
        else:
            area = data[str(user_id)]['work_area']
            if area == '丛林':
                hours = 3
                tool_list = ['急救包','弹弓']
            elif area == '7d':
                hours = 4
                tool_list = ['急救包','弹弓','一次性小手枪']
            elif area == 'mauve':
                hours = 8
                tool_list = ['急救包','弹弓','一次性小手枪','充能陷阱','道具盲盒']
            elif area == 'lxvi':
                hours = 12
                tool_list = ['急救包','弹弓','一次性小手枪','充能陷阱','道具盲盒','胡萝卜','madeline提取器','时间秒表']
            data[str(user_id)]['working'] = False
            data[str(user_id)]['work_area'] = None
            work_per_hour = data[str(user_id)]['work_per_hour']
            work_simple_chance = data[str(user_id)]['work_simple_chance']
            bonus_berry = data[str(user_id)]['bonus_berry']
            bonus_item = data[str(user_id)].get('bonus_item', 0)
            work_exp = data[str(user_id)]['work_exp']
            final_log=""
            common_events=[
                "为了绿色出行，madeline选择骑车出行。",
                "突然下雨了，madeline没有带雨伞而被淋湿了。",
                "madeline看到路旁的小狗，很可爱，忍不住摸了摸它的头。",
                "madeline经过便利店，进去买了一瓶水解渴。",
                "阳光很好，madeline决定走一段人行道晒晒太阳。",
                "madeline在街头看到有人跳街舞，驻足看了一会。",
                "madeline不小心在路上踩到了口香糖，有点烦。",
                "madeline帮助一位迷路的老人指路，对方很感激。",
                "madeline走累了，在公园长椅上坐了一会儿。",
                "madeline点了一杯冰咖啡，在树荫下慢慢喝完。",
                "madeline听到附近店铺放着熟悉的歌曲，不由哼了起来。",
                "madeline看到橱窗里展示的手办，忍不住多看了几眼。",
                "一只蝴蝶落在madeline的肩膀上，又飞走了。",
                "madeline看到路边花坛里盛开的鲜花，忍不住拍了张照。",
                "有只鸽子突然飞起，把madeline吓了一跳。",
                "madeline买了个雪糕，结果吃得太快牙齿酸了。",
                "madeline看到别人家阳台晾着的猫咪很慵懒。",
                "一阵风吹过，madeline的帽子差点被吹跑。",
                "madeline走在小巷中，意外发现了一家文具杂货店。",
                "madeline在路边书摊翻看旧书，翻到了一本童年回忆。",
                "madeline听见一对情侣吵架，悄悄绕了个远路。",
                "路边小贩送了一颗糖果给madeline，味道还不错。",
                "有小朋友在追泡泡，madeline不小心被绊了一下。",
                "madeline看到公交上有人让座，感到一丝温暖。",
                "madeline在斑马线等灯时和隔壁的阿姨聊了两句天气。",
                "远处有烟火响起，madeline抬头看了一会儿。",
                "madeline闻到树莓店刚出炉的香味，肚子咕咕响了。",
                "madeline在饮水机旁排队，前面小朋友主动让了他一下。",
                "一只流浪猫绕着madeline转了几圈后离开了。",
                "madeline经过一个镜子橱窗，偷偷整理了一下头发。",
                "madeline试着走进一家店铺询问是否招人，对方说‘再等等吧’。",
                "madeline在墙上的招聘启事前拍了张照，准备回去再看。",
                "madeline刚走进一家公司，前台就说‘面试结束了’。",
                "madeline在求职路上听朋友说隔壁街有新店开张。",
                "madeline填写了一份简历，但写完名字就卡住了。",
                "madeline在招聘网站上刷到了一个心动的兼职。",
                "madeline收到一条短信提醒下午有场面试，赶紧确认地址。",
                "madeline排队等面试时，前面的人穿得特别正式，让他有点紧张。",
                "madeline今天跑了三家店，都说‘暂时不招人’。",
                "madeline在公交车上看着窗外，思考下一步的方向。",
                "madeline在公交站等车时，被一只毛茸茸的猫蹭了一下腿。",
                "madeline走进小巷，发现墙上有一幅涂鸦画得很有趣。",
                "madeline今天穿了双新鞋，结果脚被磨出了水泡。",
                "madeline路过花店，被一阵香气吸引停下了脚步。",
                "madeline看到地上的落叶，踩上去发出沙沙声，感觉很治愈。",
                "一个街头艺人正在唱老歌，madeline听得出神。",
                "madeline在路边买了包热乎的糖炒栗子，边走边吃。",
                "madeline刚坐上长椅，一只鸽子就跳到了他面前。",
                "madeline看到一辆复古自行车，忍不住多看了几眼。",
                "madeline用零钱买了一瓶汽水，咕咚咕咚喝光了。",
                "madeline经过幼儿园时，听到了小朋友们整齐的歌声。",
                "madeline看到有个孩子摔倒了，赶紧扶他起来。",
                "madeline走进一家书店，随手翻了本漫画书。",
                "风有点大，madeline被吹得眯起了眼睛。",
                "madeline经过公园时，看见有人在遛一只迷你猪。",
                "madeline走神撞到了路灯杆，有点尴尬地揉了揉头。",
                "madeline捡起路边掉落的零钱，交给了便利店老板。",
                "madeline帮一位骑三轮的老爷爷推上了坡。",
                "madeline站在天桥上，看着川流不息的车流发呆。",
                "一只麻雀落在madeline旁边的栏杆上，蹦蹦跳跳的。",
                "madeline走进一家小吃摊，点了份炸串当作午饭。",
                "madeline买了杯豆浆，不小心洒了一点在衣服上。",
                "madeline刚想过马路，结果红灯亮了，只能等。",
                "madeline顺手从地上捡起了一个空瓶，扔进垃圾桶。",
                "madeline看到有个小朋友在玩泡泡，他也试着吹了一个。",
                "madeline走进一间旧唱片店，店主放着上世纪的老歌。",
                "madeline在十字路口看到了身穿玩偶服跳舞的人。",
                "一个流浪艺人在拉小提琴，madeline听了一会后投了硬币。",
                "madeline在手机里记录下了一个突然闪现的好点子。",
                "一只小狗追着madeline跑了一小段，看上去很兴奋。",
                "madeline看到有人在街边摆摊卖旧书，好奇地翻了翻。",
                "有位年轻人递给madeline一张宣传单，他礼貌接过了。",
                "madeline走进地铁站，发现扶梯正在维修，只能爬楼梯。",
                "madeline发现自己鞋带松了，在路边系好继续前进。",
                "madeline看到一棵大树下聚着很多人拍照，好奇看了看。",
                "小贩喊着“新鲜水果”，madeline买了一点当点心。",
                "madeline走在桥上，低头看到水里倒映着蓝天白云。",
                "街上有位老人弹着二胡，madeline听得有些出神。",
                "madeline的手机快没电了，在便利店充电几分钟。",
                "突然刮起一阵大风，madeline赶紧护住了头发。",
                "一个小朋友对madeline打了个招呼，madeline也笑着回应。",
                "madeline走在路上看到一个熟悉的背影，结果认错人了。",
                "有个女孩递给madeline一张调查问卷，他认真填写了。",
                "madeline在路边听到一位阿姨讲笑话，忍不住笑出声。",
                "madeline经过一家照相馆，橱窗里是很多旧照片。",
                "madeline看到有辆车被贴了罚单，暗自庆幸没乱停车。",
                "一个小机器人在街头跳舞，吸引了madeline的注意。",
                "madeline走到一处施工路段，不得不绕了个大圈。",
                "madeline在街边喝水，不小心呛了一下。",
                "一个快递小哥骑电瓶车飞驰而过，madeline吓了一跳。",
                "madeline看到一群中学生在放风筝，风筝飞得很高。",
                "路边的树叶变黄了，madeline觉得秋天真的来了。",
                "madeline路过一个喷泉，忍不住靠近感受水雾。",
                "madeline和陌生人不小心撞了一下，对方连忙道歉。",
                "madeline走累了，在便利店坐了会儿休息。",
                "madeline喝了一杯冰饮料，头突然被冻了一下。",
                "madeline打了个喷嚏，引来路人好奇的目光。",
                "路边有位大爷在练太极，动作特别标准。",
                "madeline看到一辆婚车经过，车上洒出红色花瓣。",
                "madeline走过小吃街，香味混杂得让人垂涎欲滴。",
                "madeline在公交车上帮一位孕妇让了座。",
                "madeline不小心走错路，多绕了一大圈。",
                "一位小朋友给madeline比了个“耶”的手势，madeline也回了一个。",
                "madeline在超市买了瓶饮料，结果没看标签是苦的。",
                "madeline看到商场橱窗里的玩偶，童心泛起。",
                "madeline被刚洗过的地板滑了一下，差点摔倒。",
                "madeline在便利店排队结账时，后面的人打了个喷嚏。",
                "madeline用饮料瓶喂了街边的一只流浪狗。",
                "madeline看到一家老电影院，门口贴着复古海报。",
                "madeline刚进地铁站，听到广播说下一班车晚点。",
                "路边的共享单车一辆都没剩，madeline只能步行。",
                "madeline从背包里掏出地图，站在路口研究了一会。",
                "有人向madeline问路，他尽力帮忙解释清楚。",
                "madeline在路边买了份报纸，随手翻了几页。",
                "madeline经过一条幽静小路，两侧开满了花。",
                "madeline看见有人在打羽毛球，忍不住围观了一会。",
                "madeline捡到一张公交卡，交到了失物招领处。",
                "一位爷爷向madeline讲起了年轻时的故事。",
                "madeline帮一位妈妈拿了一袋重物上公交车。",
                "madeline无意中听到两位老人在讨论彩票号码。",
                "一个街头魔术师邀请madeline参与变魔术。",
                "路边有个自动贩卖机，madeline买了一瓶冰镇汽水。",
                "一个跳蚤市场在开张，madeline逛了一圈没买东西。",
                "madeline被迎面而来的泡泡枪打了一脸泡泡。",
                "madeline坐在路边长椅，闭上眼睛感受阳光。",
                "madeline遇到堵车，公交车一动不动。",
                "一辆电动车突然从人行道穿过，madeline赶紧避让。",
                "madeline看到天边的云像一只兔子，忍不住拍下来。",
                "madeline点了个奶茶，结果拿错了别人的单子。",
                "madeline向一家咖啡馆询问是否需要兼职，被礼貌拒绝了。",
                "madeline尝试递出简历，对方说“我们暂时不招人”。",
                "madeline在公告栏前认真地抄下了一个招聘信息。",
                "madeline刚走进公司大门，结果发现时间记错了。",
                "madeline听说附近新开张的甜品店正在招人。",
                "madeline面试时卡壳了几秒，但勉强回答了问题。",
                "madeline决定改简历上的自我介绍，希望能更吸引人。",
                "madeline加了一个求职交流群，看看大家都在找什么。",
                "madeline试图打电话咨询一份兼职，但无人接听。",
                "madeline走了一整天，终于找到一家愿意留下联系方式的店。",
                "madeline鼓起勇气推开办公室的门，面试官正好在喝水。",
                "madeline在等面试时遇到了一个也来求职的朋友。",
                "madeline在公交上与旁人闲聊时听到了工作机会的线索。",
                "madeline看到招聘启事时太激动，结果拍糊了照片。",
                "madeline写好了求职信，决定明天正式开始投递。"
            ]
            simple_work_events = [
                "madeline今天帮邻居搬了一些箱子，赚了一些零花钱。",
                "madeline在街头帮忙派发传单，得到了报酬。",
                "madeline在附近的咖啡馆做了几小时的兼职，学到了不少东西。",
                "madeline在商场试穿衣服当模特，赚了一些快钱。",
                "madeline帮忙清扫了公园，获得了些许劳动报酬。",
                "madeline在社区举办的集市上当了摊位助手。",
                "madeline帮忙给老邻居洗了车，赚了点小钱。",
                "madeline为小朋友们当了一次临时的保姆。",
                "madeline在附近的书店做了一次短期的清洁工作。",
                "madeline帮朋友捎了个包裹，顺便赚了一些零钱。",
                "madeline帮忙在超市整理货架，得到了报酬。",
                "madeline在宠物店帮忙照看了一下狗狗，赚了一些零花钱。",
                "madeline在街头的花店帮忙摆花，老板给了小费。",
                "madeline在附近的学校做了一次短期助教工作。",
                "madeline在健身房做了两小时的清洁工，赚了一些钱。",
                "madeline在餐厅帮忙做了几个小时的服务员。",
                "madeline帮邻居遛了狗，赚了一些小费。",
                "madeline在家附近的快餐店做了一次外卖送餐员。",
                "madeline帮忙在图书馆整理书籍，获得了一些报酬。",
                "madeline在一个宠物寄养中心工作了几小时，照顾了几只小动物。",
                "madeline在小区的停车场帮忙指挥停车，赚了一些零钱。",
                "madeline在朋友的婚礼上当了临时的接待员。",
                "madeline为一家小店做了几小时的收银员。",
                "madeline帮朋友整理了花园，获得了些许回报。",
                "madeline在超市当了几小时的促销员，发了不少优惠券。",
                "madeline在社交平台上做了几小时的网店客服。",
                "madeline在社区的垃圾分类活动中帮忙分拣垃圾，得到了奖励。",
                "madeline在宠物店帮忙喂养小动物，老板给了小费。",
                "madeline在小区的公共区域做了清洁工作，得到了报酬。",
                "madeline为朋友的生日派对布置场地，赚了一些零花钱。",
                "madeline在电影院做了临时的票务工作人员。",
                "madeline在附近的农场帮忙采摘水果，老板给了些零花钱。",
                "madeline在家附近的美容院做了短期的助手工作。",
                "madeline在当地市场帮忙做了销售助理，赚了一些钱。",
                "madeline在餐厅里做了几小时的清洁工，赚了小费。",
                "madeline在街头卖手工艺品，赚了一些零用钱。",
                "madeline帮忙做了社区活动的志愿者工作，获得了社区的感谢。",
                "madeline帮忙搬运了一些建筑材料，得到了报酬。",
                "madeline在街头卖了几小时的报纸，赚了一些零钱。",
                "madeline在商场当了试吃员，赚了些小钱。",
                "madeline在周末市场帮忙售卖自制的食品，得到了收入。"
            ]
            complex_work_events = [
                "madeline接到了一个高薪一天的摄影工作，为公司拍摄广告。",
                "madeline在大型会议上担任了一天的翻译，收获了一笔可观的报酬。",
                "madeline为某企业做了一天的市场调研，赚了相当高的工资。",
                "madeline为一个高端客户举办的私人派对担任了当天的保镖，赚了一大笔钱。",
                "madeline为某个产品做了一天的代言，收入比平时的工作高很多。",
                "madeline参加了一个技术培训班的讲解工作，一天的薪水相当可观。",
                "madeline做了一个品牌推广活动的主持人，收到了丰厚的报酬。",
                "madeline被某电影公司临时聘请，担任剧组的临时助理，工作一天，赚了不少。",
                "madeline在某酒店担任临时高端宴会的服务员，赚了高额的小费。",
                "madeline在一场时尚秀上担任了一天的模特，薪水非常高。",
                "madeline为某企业提供了一天的法律咨询服务，赚了丰厚的报酬。",
                "madeline为一个大品牌做了市场推广活动的主持人，一天内赚了很多。",
                "madeline参加了一次电视节目的录制，作为临时嘉宾，一天收入很可观。",
                "madeline在著名餐厅担任临时宴会侍应，得到了极高的服务费。",
                "madeline在一个大型拍卖会上担任了临时工作人员，收入远超预期。",
                "madeline为某知名品牌进行了一天的产品试用，获得了高额报酬。",
                "madeline担任了一个商业活动的顾客引导员，工作一天赚了不小的收入。",
                "madeline被某演出公司临时聘请，做了一个高薪的后台工作人员。",
                "madeline参加了一个大型活动的筹备工作，工作了一天，薪水很高。",
                "madeline帮助一家大公司做了一天的品牌调研，得到了丰厚的酬劳。",
                "madeline被聘为某产品的临时代言人，宣传一天后获得高额报酬。",
                "madeline在某科技公司担任一天的产品测试员，得到了优厚的薪水。",
                "madeline担任了一个短期广告拍摄的临时演员，收入相当可观。",
                "madeline在某个大型体育赛事上担任了临时工作人员，赚了高额的薪水。",
                "madeline做了一个大型展会的活动策划助手，工作一天薪水丰厚。",
                "madeline为某个知名品牌拍摄了广告视频，工作一天获得高薪。",
                "madeline为一个高端餐厅做了一个高端宴会的服务员，收入颇丰。",
                "madeline为一场大型婚礼提供了临时摄影服务，赚了相当高的报酬。",
                "madeline参与了一个时尚活动的临时工作人员，工作一天赚了不少钱。",
                "madeline被邀请为某个名人活动担任保镖，工作一天薪水非常高。",
                "madeline在某国际品牌的发布会上担任了临时主持，获得了丰厚的报酬。",
                "madeline作为临时司机接送高端客户，工作一天获得了相当高的工资。",
                "madeline在一家五星级酒店的高端宴会中做了临时侍应，得到了丰厚的小费。",
                "madeline被某公司聘请做了一天的临时人事助理，收入相对较高。",
                "madeline为一个知名品牌做了一个短期的产品推广，收到了高薪。",
                "madeline参加了一个大型活动，担任了临时的拍摄助理，工作一天，收入颇丰。",
                "madeline为一场大型会议做了一天的翻译，收到了相当丰厚的薪酬。",
                "madeline在某大公司做了一天的顾客关系管理，收入超出了预期。",
                "madeline为某企业进行了一天的IT支持工作，获得了高额报酬。",
                "madeline为一个艺术展览提供了一天的临时讲解工作，收入可观。",
                "madeline为一个重要客户的私人晚宴做了全天的礼仪工作，得到了极高的报酬。",
                "madeline为某个高端商业活动担任了主持人，工作一天薪酬丰厚。",
                "madeline为一家大公司担任了一天的财务临时助理，薪水不菲。",
                "madeline参加了一个名人活动的组织，作为临时工作人员，得到了高薪。",
                "madeline为一个著名品牌做了临时的视频拍摄工作，薪水非常高。"
            ]
            # 初始化总草莓，总道具
            total_berry = 0
            total_item = {}
            for hour in range(hours):
                selected_events = random.sample(common_events, 10 - work_per_hour)
                
                for i in range(work_per_hour):
                    # 插入工作事件
                    get_salary = random.randint(1,10)
                    if get_salary <= 7:
                        salary = random.randint(20,50)
                        tool_num = 0
                    elif get_salary <= 9:
                        salary = 0
                        tool_type = random.choice(tool_list)
                        tool_num = random.randint(1,3)
                        tool_num += bonus_item
                    else:
                        tool_num = 0
                        salary = 0
                    # 计算随机事件类型
                    if random.randint(1, 100) < work_simple_chance:
                        event = random.choice(simple_work_events)
                    else:
                        event = random.choice(complex_work_events)
                        salary *= 2
                        tool_num *= 2
                    
                    if salary > 0:
                        event += f"本次工作madeline获得了{salary}颗草莓。"
                        data[str(user_id)]['berry'] += salary
                        total_berry += salary
                    elif tool_num > 0:
                        event += f"本次工作madeline获得了{tool_num}个{tool_type}。"
                        if(not tool_type in data[str(user_id)]["item"]):
                            data[str(user_id)]["item"][tool_type] = 0
                        data[str(user_id)]["item"][tool_type] += tool_num
                        # 累加到total_item
                        if tool_type not in total_item:
                            total_item[tool_type] = 0
                        total_item[tool_type] += tool_num
                    else:
                        event += f"本次工作由于老板太黑心了，madeline什么都没获得。"

                    if bonus_berry>=1:
                        bonus_rate = random.randint(1,100)
                        # 5%的概率触发额外草莓
                        if bonus_rate <= 10:
                            bonus = random.randint(1,bonus_berry)
                            data[str(user_id)]['berry'] += bonus
                            total_berry += bonus
                            if salary == 0 and tool_num == 0:
                                event += f"但是由于表现非常好，老板额外奖励了{bonus}颗草莓。"
                            else:
                                event += f"同时因表现非常好，额外获得了{bonus}颗草莓。"
                    event += "\n"
                    selected_events.append(event)
                
                # 构造日志字符串
                random.shuffle(selected_events)  # 打乱顺序
                for i, event in enumerate(selected_events, start=1):
                    final_log += f"事件{i} - {event}\n"
                final_log += "-------------\n"
            
            final_log += f"本次工作你获得了{hours}点经验。"
            final_log += f"\n本次工作你获得了{total_berry}颗草莓。"
            # 修改道具汇总部分
            if total_item:
                final_log += "\n本次工作你获得了以下道具："
                for item, count in total_item.items():
                    final_log += f"\n- {item} × {count}"
            else:
                final_log += "\n本次工作你没有获得任何道具。"
            
            data[str(user_id)]['work_exp'] += hours
            tool_bonus = work_exp//100
            if (tool_bonus > 0):
                tool_type = random.choice(tool_list)
                if(not tool_type in data[str(user_id)]["item"]):
                    data[str(user_id)]["item"][tool_type] = 0
                data[str(user_id)]['item'][tool_type] += tool_bonus
                # 也累加到total_item
                if tool_type not in total_item:
                    total_item[tool_type] = 0
                total_item[tool_type] += tool_bonus
                final_log += f"\n同时因madeline非常出色的表现，额外获得了{tool_bonus}个{tool_type}!"
            
            save_data(full_path, data)

            # 构建转发的消息内容
            msg_list = [
                {
                    "type": "node",
                    "data": {
                        "name": "工作日志",
                        "uin": Bot_event.self_id,
                        "content": final_log
                    }
                }
            ]

            await bot.call_api("send_group_forward_msg", group_id=Bot_event.group_id, messages=msg_list)
            await status_work.finish("外出工作完成啦，madeline将所有收入和工作日志送给你以后也回到原本的猎场中休息了，期待下次与你的见面~", at_sender=True)
    else:
        work_exp = data[str(user_id)]['work_exp']
        await status_work.finish(f"你似乎没有派遣任何madeline去外出，你现在的工作经验点数是:{work_exp}，工作结束后将额外获得{work_exp//100}个随机道具", at_sender=True)

#休息
sleep = on_command('休息', aliases={'worksleep'}, permission=GROUP, priority=1, block=True, rule=whitelist_rule)
@sleep.handle()
async def sleep_handle(event: GroupMessageEvent, bot: Bot, arg: Message = CommandArg()):
    #打开文件
    data = open_data(full_path)

    user_id = str(event.get_user_id())
    current_time = datetime.datetime.now()
    if(str(user_id) in data):
        #初始化
        if(not 'working' in data[str(user_id)]):
            data[str(user_id)]['working'] = False
            data[str(user_id)]['work_area'] = None
            data[str(user_id)]['work_per_hour'] = 3
            data[str(user_id)]['work_simple_chance'] = 90
            data[str(user_id)]['bonus_berry'] = 0
            data[str(user_id)]['working_endtime'] = current_time.strftime("%Y-%m-%d %H:%M:%S")
            data[str(user_id)]['work_exp'] = 0
        
        if(not 'work_skiptime' in data[str(user_id)]):
            data[str(user_id)]['work_skiptime'] = 0
        
        if(not 'last_sleep_date' in data[str(user_id)]):
            data[str(user_id)]['last_sleep_date'] = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            data[str(user_id)]['last_sleep_time'] = current_time.strftime("%Y-%m-%d %H:%M:%S") #这个变量是检测是否可用时间秒表用的

        if(not 'item' in data[str(user_id)]):
            await sleep.finish("请先获取任意道具再来休息", at_sender=True)
        
        current_date = datetime.date.today()
        #判断今天是否已经休息过了
        last_sleep_str = data[str(user_id)]['last_sleep_date']
        last_sleep_date = datetime.datetime.strptime(last_sleep_str, "%Y-%m-%d").date()

        if last_sleep_date != current_date:
            today_sleep = 0
        else:
            today_sleep = 1
        
        if today_sleep == 0:
            data[str(user_id)]['last_sleep_date'] = current_date.strftime("%Y-%m-%d")
            power_per_hour = 50
            # 房产证加成
            power_per_hour += data[str(user_id)].get("collections").get('房产证', 0) * 100
            next_time_str = data[str(user_id)]['next_time'] 
            next_time_dt = datetime.datetime.strptime(next_time_str, "%Y-%m-%d %H:%M:%S")
            if next_time_dt < current_time:
                next_time_dt = current_time
            next_time_dt += datetime.timedelta(hours=4)

            sleep_time_str = data[str(user_id)]['last_sleep_time'] 
            sleep_time_dt = datetime.datetime.strptime(sleep_time_str, "%Y-%m-%d %H:%M:%S")
            sleep_time_dt += datetime.timedelta(hours=4)
            data[str(user_id)]['next_time'] = next_time_dt.strftime("%Y-%m-%d %H:%M:%S")
            data[str(user_id)]['last_sleep_time'] = sleep_time_dt.strftime("%Y-%m-%d %H:%M:%S")

            if not '体力' in data[str(user_id)]['item']:
                data[str(user_id)]['item']['体力'] = 0
            data[str(user_id)]['item']['体力'] += power_per_hour * 4

            save_data(full_path, data)
            await sleep.finish(f"开始休息了，下次可抓时间延长了4个小时，醒来后可以获得{power_per_hour*4}体力", at_sender=True)
        else:
            await sleep.finish("你今天已经休息过了，明天再来吧", at_sender=True)

#加速完成工作
skip_work = on_command('工作加速', aliases={'workspeed'}, permission=GROUP, priority=1, block=True, rule=whitelist_rule)
@skip_work.handle()
async def skip_work_handle(bot: Bot, Bot_event: GroupMessageEvent):
    #打开文件
    data = open_data(full_path)

    user_id = str(Bot_event.get_user_id())
    current_time = datetime.datetime.now()
    #是否工作过
    if(not 'working' in data[str(user_id)]):
        await skip_work.finish("你还没有派遣madeline外出工作过", at_sender=True)
    
    if data[str(user_id)]['working']:
        working_endtime = datetime.datetime.strptime(data.get(str(user_id)).get('working_endtime'), "%Y-%m-%d %H:%M:%S")
        if current_time < working_endtime:
            work_skiptime = int(data[str(user_id)]['work_skiptime'])
            time_delta = working_endtime - current_time
            minutes_remaining = int(time_delta.total_seconds() // 60)
            skip_power_require = (minutes_remaining // 2) * pow(2, work_skiptime) + 1
            if not '体力' in data[str(user_id)]['item']:
                data[str(user_id)]['item']['体力'] = 0
            if data[str(user_id)]['item']['体力'] >= skip_power_require:
                data[str(user_id)]['item']['体力'] -= skip_power_require
                data[str(user_id)]['working_endtime'] = current_time.strftime("%Y-%m-%d %H:%M:%S")
                data[str(user_id)]['work_skiptime'] += 1
                save_data(full_path, data)
                await skip_work.finish(f"你成功使用{skip_power_require}点体力提前结束了本次工作，你还剩{data[str(user_id)]['item']['体力']}点体力！", at_sender=True)
            else:
                await skip_work.finish(f"你的体力不足，需要{skip_power_require}点，你只有{data[str(user_id)]['item']['体力']}点", at_sender=True)
    else:
        await skip_work.finish("你暂时没有派遣任何madeline外出工作", at_sender=True)

# 查看帮助菜单和更新信息
work_help = on_fullmatch(['.工作帮助', '。工作帮助', '。workhelp', '.workhelp'], permission=GROUP, priority=1, block=True, rule=whitelist_rule)
@work_help.handle()
async def work_help_handle(bot: Bot, Bot_event: GroupMessageEvent):
    msg = (
        "以下是关于工作的一些指令：\n\n"
        ".work 工作区域/携带食物/派遣madeline的名称\n工作的主命令，派遣madeline出去工作，不过注意派出去的madeline不会回来哦！携带的食物和体力可以在商店里面购买，体力也可以通过休息来恢复，工作区域在下面有哦！\n\n"
        ".workspeed \n可以消耗体力来加速工作完成，但是随着每天加速次数的增加，消耗的体力越多\n\n"
        ".workjd\n查询Madeline工作的进度，工作完成后用这个命令来收取草莓/道具\n\n"
        ".worksleep\n休息4h，休息的这4h能恢复200体力（若有房产证藏品则是600），但是这个时间内不能抓，不过能和加工器同时使用。不过一天只能休息一次哦！\n\n"
        ".workhelp\n可以查询工作帮助，也就是本界面\n"
        "---------------------\n"
        "关于工作的一些帮助\n"+
        "首先，外出需要准备足够的体力，1份足够维持体力的食物，和1个你要派遣的madeline"+
        "每次外出都会消耗大量的时间和体力，并且外出完成后你所派遣的madeline不会回来。"+
        "你派遣的madeline等级越高，在工作中的加成收益就越明显。"+
        "加成增益效果如下：\n"
        "1级madeline: 无加成\n2级madeline: 工作获得的额外奖励上限+3\n3级madeline: 工作获得的额外奖励上限+10\n4级madeline: 工作类型是高薪工作的概率+10%\n5级madeline: 每个小时必定增加一次工作机会\n"+
        "同样的，这些效果可以与食物的加成叠加。工作的种类分为普通工作和高薪工作，只要遇到了就必定会获得一定的奖励。"+
        "目前可以工作的区域如下:\n"+
        "丛林: 消耗200体力，耗时3小时\n7d: 消耗325体力，耗时4小时\nmauve: 消耗1200体力，耗时8小时\nlxvi:消耗4500体力，耗时12小时\n"+
        "每次完成工作后，你都将获得一定的工作经验，工作经验越高，你在结束工作时能获得的额外奖励越多。\n加油吧，各位madeline~\n"+
        "---------------------\n"+
        "下面是不同区域单次普通工作可获得的收益:\n"+
        "丛林: 随机数量的草莓、急救包、弹弓\n"+
        "7d: 随机数量的草莓、急救包、弹弓、一次性小手枪\n"+
        "mauve: 随机数量的草莓、急救包、一次性小手枪、充能陷阱、道具盲盒\n"+
        "lxvi: 随机数量的草莓、急救包、一次性小手枪、充能陷阱、道具盲盒、胡萝卜、madeline提取器、时间秒表")
    # 构建转发的消息内容
    msg_list = [
        {
            "type": "node",
            "data": {
                "name": "工作帮助",
                "uin": Bot_event.self_id,
                "content": msg
            }
        }
    ]

    await bot.call_api("send_group_forward_msg", group_id=Bot_event.group_id, messages=msg_list)