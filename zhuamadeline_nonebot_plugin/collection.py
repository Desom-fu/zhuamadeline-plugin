﻿#藏品别名
collection_aliases = {
    "身份徽章": ["身份", "徽章", "学费"],
    "充能箱": ["电箱"],
    "madeline飞升器": ["飞升器"],
    "木质十字架": ["木制十字架"],
    "鲜血之刃": ["血刃"],
    "尘封的秘宝": ["秘宝"],
    "星光乐谱": ["乐谱"],
}

#藏品系统，结构为：{藏品名称：[能量价格，商店位置，等级，描述]}
collections = {
    '生命之叶':
    [
        30000,
        7,
        3,
        '看似平平无奇的叶子，似乎有着强大的生命力。对部分猎场的高等级madeline似乎有着强大的吸引力。\n持有此收藏品时，在1、2猎场正常抓madeline时，抓到4、5级madeline的概率微量提升'#提升至原本的1.5倍
    ],
    '天使之羽':
    [
        20000,
        7,
        2,
        '天使之翼似乎守护着古代遗迹，使得古代遗迹不会发生任何危险的事件。\n这是天使之翼上的一片羽毛。\n持有此收藏品时，使用madeline提取器和充能陷阱时将有额外微量的概率使你免除本次爆炸伤害。'#有2%概率
    ],
    '紫晶魄':
    [
        50000,
        7,
        4,
        '不知道为什么，很多特别难挖的紫水晶中都能发现此类物质。或许此物携带在身上的话...有时可以抵挡非常强劲的伤害？\n持有此收藏品时，使用madeline提取器和充能陷阱时将有额外少量的概率使你免除本次爆炸伤害。'#有3%概率
    ],
    '木质十字架':
    [
        10000,
        7,
        1,
        '似乎只是一个木质的十字架，正中心有一个六边形的暗红色宝石，完全没有宝石的光泽，但仍能看到宝石之上隐约浮现着madeline的形状。看不出来他的作用是什么，不过这个十字架旁边似乎附上了一句话。\n请闭上双眼，\n倾听并提取内心的低语，\n或许答案镌刻在85秒之后。\n<愿神明保佑你>\n✟救済執行✟'
    ],
    '圣十字架':
    [
        30000,
        7,
        3,
        '愿神明保佑你，✟救済執行✟\n持有此收藏品时，在madeline竞技场对战时，作为防守方的情况下会略微提高所发挥出的战斗力的下限。'#下限+3，为-12 到 +15
    ],
    '鲜血之刃':
    [
        100000,
        7,
        5,
        '据说目前所有的复仇之刃都是它的投影，力量仅为它的一小部分。由于复仇之刃无法让鲜血之刃满意，现在它已经收回了所有复仇之刃\n你可以献祭鲜血让鲜血之刃强化你的madeline，增加你的madeline的进攻的战力。由于鲜血之刃过于强大，你只能中量提高常驻战力，少量提高进攻战力。'#加3点常驻战力，1-3点随机进攻战力
    ],
    '尘封的秘宝':
    [
        50000,
        7,
        4,
        '它承载了时间的记忆与无尽的价值，尘封的秘宝是智慧与奇迹的结晶，在抓madeline可以获得草莓的情况下，每次抓到madeline时将额外获得少量草莓。'#加2草莓
    ],
    '奇想魔盒':
    [
        30000,
        7,
        3,
        '充满魔力的黑色盒子，在成功使用消耗类抓捕道具抓madeline时，有一定概率会获得草莓！\n祈愿和使用时间献祭器的时候也有少量概率获得草莓！可与奇想扑克叠加使用！'#道具20%获得，祈愿10%获得 3*等级 的草莓
    ],
    '奇想扑克':
    [
        30000,
        7,
        3,
        '充满魔力的白色扑克，在成功使用消耗类抓捕道具抓madeline时，有一定概率会获得草莓！\n祈愿和使用时间献祭器的时候也有少量概率获得草莓！可与奇想魔盒叠加使用！'#道具20%获得，祈愿10%获得 3*等级 的草莓
    ],
    '矿工头盔':
    [
        50000,
        7,
        4,
        '挖矿必备的安全工具，头上带灯即使身处黑暗的矿洞也可以清晰看到前方路况。在矿洞类猎场抓Madeline时，掉坑几率中幅度降低'#掉坑概率从15%降低至10%
    ],
    '调律器':
    [
        50000,
        7,
        4,
        '对你想调律的地方进行调率吧！拥有这个藏品后所有猎场的草莓/金矿获得概率少量上升！'#金矿获得概率加2%
    ],
    '回想之核':
    [
        100000,
        7,
        5,
        '传说中，这是抓玛德琳世界中的十大秘宝之一，当你拥有这个秘宝之时，你将身轻如燕，力大无穷！不过毕竟只是传说中，实际上并没有如此之神力，不过也能减少你抓玛德琳的冷却！'#所有冷却-1min
    ],
    '星光乐谱':
    [
        100000,
        7,
        5,
        '这是一份古老的乐谱，纸页上似乎镶嵌着微弱的星光。你翻动它时，乐谱中的音符仿佛在空中轻轻舞动。传说中，星光乐谱能调动天上的星辰，带来绝美的音乐。据说这段音乐，有概率让草莓的活性大大增强！' #20%概率翻倍（先计算秘宝再计算翻倍，最后计算幸运加成）
    ],
    '身份徽章':
    [
        20000,
        7,
        2,
        '身份的证明！但是没准会因为这个徽章交不少学费？要记住Masker_^(2^ed)的一句话：欲速则不达，见小利则大事不成！\n\n当你拥有这个徽章时，你可以使用命令 `.use 身份徽章/(0,1,2)` 来切换状态。\n\n当状态切换为“2ed”或“膀胱”时，你参加的所有恶魔轮盘du中，将会有数值的变动，并且有额外的新道具！'
    ],
    '鱼之契约':
    [
        30000,
        7,
        3,
        '为了感谢你空军了这么多次放过了不少鱼，所以鱼群拟定了这么一个契约——这个契约能让你每天签到的获得的草莓数量翻倍（能与招财猫叠加！）！'
    ],
    '星辰碎屑':
    [
        100000,
        7,
        2,
        '传说这是一块从天上陨落的星屑，而老板不知道从哪里搞出一个有效的进货渠道……不过产量稀少，一天也只能进货2个！持有本藏品，能有效降低裸抓出1级Madeline的概率！并且似乎能无视某些猎场的限制发挥作用……'# 降5%，给2级
    ],
}