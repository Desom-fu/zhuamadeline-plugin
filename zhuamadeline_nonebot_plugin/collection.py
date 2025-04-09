#藏品别名
collection_aliases = {
    "身份徽章": ["身份", "徽章", "学费"],
    "充能箱": ["电箱"],
    "madeline飞升器": ["飞升器"],
    "木质十字架": ["木制十字架"],
    "鲜血之刃": ["血刃"],
    "尘封的宝藏": ["秘宝", "宝藏"],
    "星光乐谱": ["乐谱"],
    "奇想魔盒": ["气笑魔盒", "奇效魔盒", "魔盒", "墨盒"],
    "奇想扑克": ["气笑魔牌", "奇效魔牌", "气笑扑克", "奇效扑克", "魔牌", "扑克"],
    "星辰碎屑": ["星尘碎屑", "碎屑"],
    "矿工头盔": ["头盔"],
    '草莓果园地契': ['草莓果园', '果园', '地契'],
    '灵魂机器人': ['机器人', '小机器人', '遥控机器人'],
    '脉冲雷达': ['雷达', '探测雷达'],
}

#藏品系统，结构为：{藏品名称：[能量价格，商店位置（草莓为8，能量为7），等级，描述]}
collections = {
    '生命之叶':
    [
        30000,
        8,
        3,
        '看似平平无奇的叶子，似乎有着强大的生命力。对部分猎场的高等级madeline似乎有着强大的吸引力。\n持有此收藏品时，在1、2猎场正常抓madeline时，抓到4、5级madeline的概率微量提升'#提升至原本的1.5倍
    ],
    '天使之羽':
    [
        20000,
        8,
        2,
        '天使之翼似乎守护着古代遗迹，使得古代遗迹不会发生任何危险的事件。\n这是天使之翼上的一片羽毛。\n持有此收藏品时，使用madeline提取器和充能陷阱时将有额外微量的概率使你免除本次爆炸伤害。'#有2%概率
    ],
    '紫晶魄':
    [
        50000,
        8,
        4,
        '不知道为什么，很多特别难挖的紫水晶中都能发现此类物质。或许此物携带在身上的话...有时可以抵挡非常强劲的伤害？\n持有此收藏品时，使用madeline提取器和充能陷阱时将有额外少量的概率使你免除本次爆炸伤害。'#有3%概率
    ],
    '木质十字架':
    [
        10000,
        8,
        1,
        '似乎只是一个木质的十字架，正中心有一个六边形的暗红色宝石，完全没有宝石的光泽，但仍能看到宝石之上隐约浮现着madeline的形状。看不出来他的作用是什么，不过这个十字架旁边似乎附上了一句话。\n请闭上双眼，\n倾听并提取内心的低语，\n或许答案镌刻在85秒之后。\n<愿神明保佑你>\n✟救済執行✟'
    ],
    '圣十字架':
    [
        30000,
        8,
        3,
        '愿神明保佑你，✟救済執行✟\n持有此收藏品时，在madeline竞技场对战时，作为防守方的情况下会略微提高所发挥出的战斗力的下限。'#下限+3，为-12 到 +15
    ],
    '鲜血之刃':
    [
        100000,
        8,
        5,
        '这是抓玛德琳世界中的十大秘宝之一。据说目前所有的复仇之刃都是它的投影，力量仅为它的一小部分。由于复仇之刃无法让鲜血之刃满意，现在它已经收回了所有复仇之刃\n你可以献祭鲜血让鲜血之刃强化你的madeline，增加你的madeline的进攻的战力。由于鲜血之刃过于强大，你只能中量提高常驻战力，少量提高进攻战力。'#加3点常驻战力，1-3点随机进攻战力
    ],
    '尘封的宝藏':
    [
        50000,
        8,
        4,
        '这是抓玛德琳世界中的十大秘宝之一。它承载了时间、记忆与无尽的价值。在抓madeline可以获得草莓的情况下，每次抓到madeline时将额外获得少量草莓。'#加2草莓
    ],
    '奇想魔盒':
    [
        30000,
        8,
        3,
        '充满魔力的黑色盒子，在成功使用消耗类抓捕道具抓madeline时，有一定概率会获得草莓！\n祈愿和使用时间献祭器的时候也有少量概率获得草莓！可与奇想扑克叠加使用！'#道具20%获得，祈愿10%获得 3*等级 的草莓
    ],
    '奇想扑克':
    [
        30000,
        8,
        3,
        '充满魔力的白色扑克，在成功使用消耗类抓捕道具抓madeline时，有一定概率会获得草莓！\n祈愿和使用时间献祭器的时候也有少量概率获得草莓！可与奇想魔盒叠加使用！'#道具20%获得，祈愿10%获得 3*等级 的草莓
    ],
    '矿工头盔':
    [
        50000,
        8,
        4,
        '挖矿必备的安全工具，头上带灯即使身处黑暗的矿洞也可以清晰看到前方路况。在矿洞类猎场抓Madeline时，掉坑几率中幅度降低'#掉坑概率从15%降低至10%
    ],
    '调律器':
    [
        50000,
        8,
        4,
        '对你想调律的地方进行调率吧！拥有这个藏品后所有猎场的草莓/金矿获得概率少量上升！'#金矿获得概率加2%
    ],
    '回想之核':
    [
        100000,
        8,
        5,
        '这是抓玛德琳世界中的十大秘宝之一。传说中，当你拥有回想之核之时，你将身轻如燕，力大无穷！不过毕竟只是传说中，实际上并没有如此之神力，不过也能减少你抓玛德琳的冷却！'#所有冷却-1min
    ],
    '星光乐谱':
    [
        100000,
        8,
        5,
        '这是抓玛德琳世界中的十大秘宝之一。这是一份古老的乐谱，纸页上似乎镶嵌着微弱的星光。你翻动它时，乐谱中的音符仿佛在空中轻轻舞动。传说中，星光乐谱能调动天上的星辰，带来绝美的音乐。据说这段音乐，有概率让草莓的活性大大增强！' #20%概率翻倍（先计算秘宝再计算翻倍，最后计算幸运加成）
    ],
    '身份徽章':
    [
        20000,
        8,
        2,
        '身份的证明！但是没准会因为这个徽章交不少学费？要记住Masker_^(2^ed)的一句话：欲速则不达，见小利则大事不成！\n\n当你拥有这个徽章时，你可以使用命令 `.use 身份徽章/(0,1,2)` 来切换状态。\n\n当状态切换为“2ed”或“膀胱”时，你参加的所有恶魔轮盘du中，将会有数值的变动，并且有额外的新道具！'
    ],
    'madeline飞升器':
    [
        10000000,
        8,
        5,
        '存在于地下终端门口的一个巨大的机械装置，需要50000点能量才能激活。\n在这个机器的表面有三个颜色的凹槽，可能是解除封印的关键？\n在这个机器的内部，有三个空位，似乎是让玛德琳进去的。\n这个机器有识别装置，只能识别地下终端这个猎场的玛德琳，其他猎场的玛德琳均无法进入这个机器内。\n激活后，该机器会随机选取你指定等级的三个玛德琳，进行飞升操作。\n飞升出来的玛德琳有小概率降1级，中等概率等级不变，大概率升一级。\n\n使用方法：\n.use madeline飞升器/等级'
    ],
    '红色球体':
    [
        10000000,
        8,
        3,
        '神秘的红色球体，似乎原本是Madeline飞升器的一部分，能够恢复Madeline飞升器的一部分力量。\n若获得了这个球体，你能在地下终端里面抓到3级Madeline。'
    ],
    '绿色球体':
    [
        10000000,
        8,
        4,
        '神秘的绿色球体，似乎原本是Madeline飞升器的一部分，能够恢复Madeline飞升器的一部分力量。\n你只能在获取了红色球体之后才能获取绿色球体。\n若集齐两个球体，你将能在地下终端里面抓到4级Madeline。'
    ],
    '黄色球体':
    [
        10000000,
        8,
        5,
        '神秘的黄色球体，似乎原本是Madeline飞升器的一部分，能够恢复Madeline飞升器的一部分力量。\n你只能在获取了绿色球体之后才能获取黄色球体。\n若集齐三个球体，你将能在地下终端里面抓到5级Madeline，同时道具、道具加成、祈愿将解封。'
    ],
    '充能箱':
    [
        20000,
        8,
        2,
        '（目前已无法获取，无法使用）一个充能箱，似乎还能被撞开？能有什么用呢？莫非是，给充能陷阱加强能量？\n\n当你拥有充能箱时，你可以使用命令 `.use 充能箱` 来切换状态。\n如果充能箱是“撞开”的状态，你的所有充能陷阱将会100%爆炸，但是你只会被炸伤60min无法行动！'
    ],
    '脉冲雷达':
    [
        30000,
        8,
        3,
        '这个脉冲雷达能找出草莓果酱中的微小杂质，使得草莓果酱更加干净和美味！\n\n你拥有这个脉冲雷达后，每瓶果酱可以多卖出20颗草莓！'
    ],
    '磁力吸附手套':
    [
        50000,
        8,
        4,
        '这是一幅上面附着着磁铁的手套，能辅助你进行各种攀爬跳跃！持有本手套时，能有效大量降低你获得debuff的几率！'#所有debuff的概率降低1/3
    ],
    '炸弹包':
    [
        50000,
        8,
        4,
        '无限容量的炸弹包，你已成为玩炸弹大师！因为你已经熟悉爆炸了，有时可以抵挡非常强劲的伤害？\n持有此收藏品时，使用madeline提取器和充能陷阱时将有额外中量的概率使你免除本次爆炸伤害。'# 5%概率
    ],
    '灵魂机器人':
    [
        30000,
        8,
        3,
        '这个灵魂机器人似乎……不是用遥控器遥控的？频繁使用这个机器人，能显著增加你的灵魂强度！让你和你的玛德琳融为一心，爆发出强力战力！'# 增加1点常驻战力和进攻战力
    ],
    '鱼之契约':
    [
        30000,
        8,
        3,
        '为了感谢你空军了这么多次放过了不少鱼，所以鱼群拟定了这么一个契约——这个契约能让你每天签到的获得的草莓数量翻倍（能与招财猫叠加！）！'
    ],
    '星辰碎屑':
    [
        100000,
        8,
        2,
        '传说这是一块从天上陨落的星屑，而老板不知道从哪里搞出一个有效的进货渠道……不过产量稀少，一天也只能进货2个！持有本藏品，能有效降低裸抓出1级Madeline的概率！并且似乎能无视某些猎场的限制发挥作用……'# 抓到1级概率降10%，给2级
    ], 
    '草莓果园地契':
    [
        2500,
        9,
        2,
        '仅需2500草莓，你就能购买草莓果园里的一块地！你可以种草莓，施肥，甚至可以偷别人的草莓！收获的草莓会放入银行哦！\n\n'
        '现在草莓果园可用指令：.garden 收菜(take)/施肥(fert)/偷菜(steal)/播种(seed)/升级(upgrade)\n\n'
        '- 收菜：可以将草莓果园里面的草莓全部收到银行里！\n'
        '- 施肥：使用1200能量对土地施肥，接下来12h内草莓产量翻倍！\n'
        '- 偷菜：入场券15颗草莓，可以随机偷别人果园里1-50颗草莓！但是注意一天只能偷一次别人，并且每个人一天只能被偷一次！\n'
        '- 播种：花费10颗草莓购买种子种到地里，接下来24h内每小时都可以收获15颗草莓！\n'
        '- 升级：消耗能量/草莓升级你的土地吧！'
        # 草莓果园入场券
    ],
    '星钻':
    [
        100000,
        8,
        5,
        '这是抓玛德琳世界中的十大秘宝之一。一颗由坠落的星辰核心凝练而成的宝石，表面流淌着银河般的微光。当星钻的光芒照耀时，持有者将获得"星光护佑"——柔和的星辉能驱散疲惫，让身心重获活力。' #5%概率直接清除冷却
    ],
    '喵喵呜呜':
    [
        100000,
        8,
        1,
        '据说这是在2099年的某一天，在离地球不知道多远的虹星上，喵梦在逃离白狐的魔爪之时发出的可爱的叫声~（2025愚人节活动限定藏品）'# 愚人节活动纪念藏品！
    ],
    '时隙沙漏': [
        100000,
        8, 
        5, 
        '这是抓玛德琳世界中的十大秘宝之一。一个由时之砂与虚空水晶制成的神秘沙漏，沙粒中闪烁着时间的碎片。当沙漏翻转时，持有者能暂时打破时间的桎梏——那些未被使用的等待时间将化作"时之砂"储存起来，在需要时释放出积蓄的时间能量。' #每29/30分钟(受回想之核影响)自动积累1次抓取机会，最多可储存10次机会，使用时不会触发冷却时间
    ],
}