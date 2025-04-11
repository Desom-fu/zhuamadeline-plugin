#禁止回收道具
forbid_recycle_item = {"道具盲盒","烂胡萝卜","复仇之刃","招财猫","指南针","神秘碎片","幸运药水","赌徒之眼","音矿","残片","神权模拟器","草莓果酱","安定之音","体力","迅捷药水"}

#会掉坑的道具
trap_item = {"胡萝卜", "一次性小手枪", "弹弓"}

# 鱼类及其价值
fish_prices = {
    "海星": 50,
    "水母": 75,
    "胖头鱼": 100,
    "胖头鱼罐头": 125,
    "水晶胖头鱼": 200,
    "星鱼": 300,
    "阿拉胖头鱼": 3000
}

# 别名表
item_aliases = {
    'madeline充能器': ['充能器'],
    '草莓加工器': ['加工器', '果酱机', '草莓机'],
    'madeline提取器': ['提取器'],
    '草莓鱼竿': ['鱼竿', '钓竿', '草莓钓竿'],
    '道具盲盒': ['盲盒'],
    '时间秒表': ['秒表'],
    '充能陷阱': ['陷阱', '炸弹'],
    '安定之音': ['音符'],
    '万能解药': ['解药'],
    '幸运药水': ['幸运'],
    '迅捷药水': ['迅捷'],
    '一次性小手枪': ['小手枪', '手枪'],
    '时间献祭器': ['时间提取器','献祭器'],
    '草莓果酱': ['果酱'],
}

# 定义药水类型及其效果
potion_effects = {
    "幸运药水": {
        "buff_name": "lucky",
        "effect_per_potion": 20,
        "description": "提升运气的小道具，虽说不知道有没有真的提升...",
        "message": "现在正常抓madeline可额外获得15草莓"
    },
    "迅捷药水": {
        "buff_name": "speed",
        "effect_per_potion": 20,
        "description": "提升速度的小道具...",
        "message": "现在移动速度提升了"
    }
}

# 定义buff2类型及其属性和显示规则
buff2_config = {
    'lucky': {
        'name': '幸运',
        'show_condition': lambda berry_give: berry_give != 0,  # 只在berry_give!=0时显示
    },
    'speed': {
        'name': '迅捷',
        'show_condition': lambda _: True,  # 总是显示
    },
}


#商店货物系统，结构为：{物品名称：[价格，等级]}
item = {
    #永久道具
    'madeline充能器':
    [
        2000,
        6,
        '你在为低等级madeline太多无处使用而烦恼吗？使用这个道具可以将你的低等级madeline化作能量注入其中。\n当能量达到一定值后你可以消耗能量进行一次祈愿，祈愿获得高等级madeline的概率将大幅提升\n\n使用方法：\n输入.use madeline充能器/用来充能的madeline/数量 来进行充能\n输入.use madeline充能器/all/猎场号/等级(可以为all，all为所有等级)/至少保留多少个Madeline 来进行按等级的批量充能\n输入.pray 来进行祈愿\n输入.ck 来查询现在拥有的能量\n限购1个！'
    ],
    '草莓加工器':
    [
        1500,
        6,
        '使用草莓加工器可以瞬间将你的草莓加工成非常美味的草莓果酱，一瓶果酱的原料要150草莓，草莓果酱可以卖到一个不菲的价钱！但是每制作一瓶果酱加工器就会过载2h，这2h内你必须不停地给它控温，不能离开。加工器最多能同时制作12瓶果酱，但同样的过载时间也会对应的增加！\n输入.use 草莓加工器/数量 来确定你本次要加工多少瓶果酱。请确保你的原料数量充足。\n限购1个！'
    ],
    '时间献祭器':
    [
        1500,
        6,
        '用你的时间换取更好的运气！！！可永久使用~\n限购1个！'
    ],
    '草莓鱼竿':
    [
        1500,
        6,
        '以草莓为饵料，向淹漠之海甩出鱼竿钓鱼吧！可能会出现藏品哦！不过，要是万一空军了就不好了……可永久使用~\n限购1个！\n\n每11h可使用一次，使用方法：`.use 草莓鱼竿`'
    ],
    '招财猫': 
    [
        180, 
        6,
        '好运伴随君。持有后每天签到可额外获得3草莓，效果可叠加。\n限购20个!'
    ],
    #额外次数抓捕类道具
    '道具盲盒':
    [
        100,
        3,
        '你永远都不知道道具盲盒会开出什么！没准下一秒就是大奖呢？注：有概率抽出超级大奖哦！\n使用方法：.use 道具盲盒(单抽/五连/十连) 括号内可以省略，省略默认单抽'
    ],
    '弹弓': 
    [
        50, 
        1,
        '半小时内忍不住想抓madeline的心？没关系，弹弓能让你额外抓取一次！'
    ],
    '一次性小手枪': 
    [
        80, 
        2,
        '和弹弓一样满足你半小时内想抓madeline的心，但是因为是枪械，能额外提高概率，应该吧……'
    ],
    '充能陷阱': 
    [
        100, 
        2,
        '充能陷阱的能量十分强大，能让你几乎抓不到1、2级的madeline！但是代价是什么呢……？'
    ],
    '胡萝卜': 
    [
        200, 
        3,
        '胡萝卜，感觉像是能诱惑兔子的道具啊，难道madeline里面也有兔子吗？'
    ],
    '烂胡萝卜': 
    [
        1, 
        7,
        '你是怎么觉得这种东西能成为一个道具的？'
    ],
    '时间秒表': 
    [
        310, 
        4,
        '具有一定不稳定性的四次元道具。使用后理论上能清除任意原因导致的冷却时长......不过似乎对草莓加工器无效？'
    ],
    'madeline提取器': 
    [
        300, 
        4,
        'madeline提取器使用条例\n1. 输入“.use madeline提取器/madeline名称”来使用\n2. 只能提取当下的确存在的madeline\n3. 提取失败会产生巨大爆炸，请做好防护措施\n4. 严禁递归'
    ],
    #BUFF道具
    '万能解药': 
    [
        50, 
        2,
        '解除身上除爆炸受伤外的不良状态（前提是你能使用这个道具）'
    ],
    '幸运药水': 
    [
        1, 
        4,
        '神奇的药水，在喝下之后好运程度可以比肩抓madeline大神。接下来20次正常的抓madeline时，每抓到一次madeline都将额外获得15草莓，并且抓madeline时不会获得任何debuff。\n（由环境要素导致的意外危险除外）\n\n使用方法：.use 幸运药水(/次数)\n若批量使用必须带有斜杠'
    ],
    '迅捷药水': 
    [
        1, 
        4,
        '神奇的药水，在喝下后将身轻如燕，不会掉入任何陷阱，并且抓madeline时不会获得任何debuff！\n\n使用方法：.use 迅捷药水(/次数)\n若批量使用必须带有斜杠'
    ],
    '急救包': 
    [
        25, 
        1,
        '探索路上每位探索者必备的物品。尝试自救吧......在你陷入危险的时候。虽说不一定会成功\n\n使用方法：\n输入 `.use 急救包` 可单个使用\n输入 `.use 急救包/auto` 可一直使用到成功为止，或者急救包用完'
    ],
    #特殊道具
    '赌徒之眼':
    [
        20,
        1,
        '能够让你进du局前查看当前局势，但是...只能用一次'
    ],
    '草莓果酱':
    [
        248, #这个是平均值，范围是230-265
        4,
        '特别好吃的草莓果酱！使用.use 草莓果酱即可卖出此物品\n使用.use 草莓果酱/数量可批量卖出此物品'
    ],
# 开放猎场类道具
    '指南针': 
    [
        2500, 
        7,
        '给你指路的有力道具！！！限购1个！'
    ],
    '神秘碎片': 
    [
        2000, 
        7,
        '不知道有什么作用的神秘碎片，看起来能拼成一把钥匙，隐隐泛着淡蓝色的光芒'
    ],
    '音矿':
    [
        15,
        7,
        '这个道具可以永久提高你裸抓5级的概率！但可能需要一定数量级之后才有效果。。。该道具限购2000个！'
    ],
    '安定之音':
    [
        5,
        7,
        '音符？唱歌来振奋你要上竞技场的Madeline吧！到了一定数量级之后会增强Madeline的士气！该道具限购5000个！'
    ],
    '残片':
    [
        1,
        7,
        '1块钱的残片？能用什么用呢。。。该不会只能收藏吧！没准到了一定数量级之后就能永久提升些什么？该道具限购29997个！'
    ],
    #0猎道具
    '复仇之刃':
    [
        50,
        7,
        '这些都是鲜血之刃的分身，但是因为实力差又爱吹牛，所以被鲜血之刃嫌弃，最后失去作用了。'
    ],
    # 搞笑道具
    '神权模拟器':
    [
        1,
        7,
        '这个道具能让你获得0.001ms的神权！但是由于过于强大已经被万恶的给禁了！'
    ],
    # 鱼
    '海星':
    [
        50,
        1,
        '非常普通的海星，小心别撞上去了！使用recycle能卖出50颗草莓哦！'
    ],
    '水母':
    [
        75,
        1,
        '非常普通的水母，这下不得不反丢奥欻反丢奥欻平u了。使用recycle能卖出75颗草莓哦！'
    ],
    '胖头鱼':
    [
        100,
        2,
        '稍微有点值钱的胖头鱼，下次记得别在金限里面超级弹了！使用recycle能卖出100颗草莓哦！'
    ],
    '胖头鱼罐头':
    [
        125,
        2,
        '胖头鱼罐头经过包装非常适合食用，就是小心打开的时候别爆炸了！使用recycle能卖出125颗草莓哦！'
    ],
    '水晶胖头鱼':
    [
        200,
        3,
        '由水晶制成的胖头鱼，非常值钱！不过就算是水晶胖头鱼也会爆炸……使用recycle能卖出200颗草莓哦！'
    ],
    '星鱼':
    [
        300,
        3,
        '起星鱼了！使用recycle能卖出300颗草莓哦！'
    ],
    '阿拉胖头鱼':
    [
        3000,
        4,
        '诶，你怎么掉出来一条外星人？使用recycle能卖出3000颗草莓哦！'
    ],
    # 旅行玛德琳道具
    '体力':
    [
        1,
        5,
        '你的体力，在外出工作时必不可少的要素，保持充足的体力才能更好的完成工作。'
    ],
    # 旅行玛德琳食物
    '树莓':
    [
        40,
        5,
        '最基础的果子，虽然简单但能补充体力。适合短途工作携带。'
    ],
    '芒果':
    [
        60,
        5,
        '香甜的热带水果，能快速补充能量。带上此食物时，工作有10%概率额外获得1-20颗草莓'
    ],
    '杨桃':
    [
        600,
        5,
        '精致的星形果实，象征着好运，能让你的工作事半功倍！不过由于价格昂贵，建议长途工作的时候再携带哦！带上此食物时，触发高薪工作的概率提升10%'
    ],
    '菠萝':
    [
        650,
        5,
        '比玛德琳整个身体还要大的菠萝，一定能很好的满足口欲吧！不过由于价格昂贵，建议长途工作的时候再携带哦！带上此食物时，每次工作获得的道具+1'
    ],
    '百香果':
    [
        700,
        5,
        '珍稀的芳香果实，能激发工作潜能。不过由于价格昂贵，建议长途工作的时候再携带哦！带上此食物时，每小时必定增加一次额外工作机会'
    ],
}

#今日物品，前期道具较少，采用固定商品固定数量
today_item = {
    # 物品
    '草莓加工器': 5000,
    '胡萝卜': 50,
    '招财猫': 100,
    '一次性小手枪': 100,
    '充能陷阱': 300,
    '弹弓': 200,
    'madeline充能器': 5000,
    '时间献祭器': 5000,
    'madeline提取器': 50,
    '时间秒表': 50,
    '音矿': 500,
    '指南针': 5000,
    '急救包': 1000,
    '残片': 5000,
    '道具盲盒': 100,
    '神秘碎片': 5000,
    '安定之音': 1000,
    '草莓鱼竿': 5000,
    #旅行玛德琳相关
    '树莓':500,
    '芒果':500,
    '杨桃':500,
    '菠萝':500,
    '百香果':500,
    '体力':100000,
    #藏品
    '星辰碎屑': 1,
    '草莓果园地契': 20,
    '房产证': 100,
}
