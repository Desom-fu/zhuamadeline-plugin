from pathlib import Path
from nonebot import get_driver

__all__ = [
    "group_img",
    "other",
    "madeline_level0",
    "madeline_level0_path",
    "shop_database",
    "shop_open_img",
    "shop_work_img",
    "bot_owner_id",
    "user_path",
    "file_name",
    "duchang_list",
    "duchang_open_img",
    "full_path",
    "cd_path",
    "ban",
    "liechang_count",
    "zhuama_group",
    'bar_path',
    'garden_path',
    'hourglass_max',
    'pvp_path',
    'pvp_coldtime_path',
    'madeline_path_lc1',
    'madeline_path_lc2',
    'madeline_path_lc3',
    'madeline_path_lc4',
    'madeline_path_lc5',
    'user_path1',
    'user_path2',
    'user_path3',
    'user_path4',
    'user_path5',
    'stuck_path',
    'max_grade',
    'exp_growth',
    'backup_path',
    'save_dir',
    'font_path',
    'background_qd',
    "boss_data_path",
    "world_boss_data_path",
    "boss_names",
    'demon_path',
    "berry_path"
]

# 隐藏行测试，如果push后看不见就说明成功了

########数据信息#######
# 配置默认值
driver = get_driver()

driver.config.HOST = "127.0.0.1"  # 如果没有从 .env 文件读取到
driver.config.PORT = 9635  # 默认端口

#抓madeline专用群

group_img = Path() / "data" / "group.jpg"

#除了madeline名字以外的其他key值
other = ["next_time", "next_recover_time", "berry", "date", "buff", "item", "lc"]

#madeline图鉴存放目录
madeline_path_lc1 = Path() / "data" / "madelineLc1"   #一号猎场
madeline_path_lc2 = Path() / "data" / "madelineLc2"   #二号猎场
madeline_path_lc3 = Path() / "data" / "madelineLc3"   #三号猎场
madeline_path_lc4 = Path() / "data" / "madelineLc4"   #四号猎场
madeline_path_lc5 = Path() / "data" / "madelineLc5"   #五号猎场

#隐藏级别madeline
madeline_level0 = "madeline0"
madeline_level0_path = madeline_path_lc1 / madeline_level0

#商店数据，商店的数据一天之内对所有玩家共通，每过一天就会刷新一次商品，每天早上6点到晚上10点营业中
shop_database = Path() / "data" / "Shop" / "Shop.json"
shop_open_img = Path() / "data" / "Shop" / "开张图.png"
shop_work_img = Path() / "data" / "Shop" / "营业图.png"

#管理员ID
#封禁人员名单
# 定义猎场数 全局变量 开新猎场要改
liechang_count = 4
# 定义时间沙漏最高次数
hourglass_max = 4
#定义通信群id
#用户信息
backup_path = Path() / "Data" / "UserList_Backup"
user_path = Path() / "Data" / "UserList"
file_name = "UserData.json"
full_path = user_path / file_name
cd_path = Path() / "Data" / "UserList" / "allcooldown.json"
bar_path = Path() / "data" / "UserList" / "bar.json"
garden_path = Path() / "data" / "UserList" / "garden.json"
pvp_path = Path() / "data" / "UserList" / "pvp.json"
pvp_coldtime_path = Path() / "data" / "UserList" / "pvp_coldtime.json"
#猎场path 开新猎场要改
user_path1 = Path() / "data" / "UserList" / "UserList1.json"
user_path2 = Path() / "data" / "UserList" / "UserList2.json"
user_path3 = Path() / "data" / "UserList" / "UserList3.json"
user_path4 = Path() / "data" / "UserList" / "UserList4.json"
user_path5 = Path() / "data" / "UserList" / "UserList5.json"
stuck_path = Path() / "data" / "UserList" / "Struct.json"
#5猎相关经验
max_grade = 30 # 满级固定30
# 经验增长规则字典
exp_growth = {
    range(1, 6): 5,   # 等级 1-5，max_exp +5
    range(6, 11): 10,  # 等级 6-10，max_exp +10
    range(11, 16): 15, # 等级 11-15，max_exp +15
    range(16, 21): 20, # 等级 16-20，max_exp +20
    range(21, 31): 25  # 等级 21-30，max_exp +25
}
# 绘图相关路径
save_dir = Path("Data") / "generate_image" 
font_path = Path("Data") / "fonts"  / "ZhanKu.ttf"
background_qd = Path()/"Data"/"Image"/"background_qd.png"

#赌场信息
duchang_list = Path() / "data" / "DuChang" / "duchang.json"
duchang_open_img = Path() / "data" / "DuChang" / "duchang.png"

# boss相关
boss_data_path = Path() / "data" / "UserList" / "boss_data.json"
world_boss_data_path = Path() / "data" / "UserList" / "world_boss_data.json"

# b2相关
demon_path = Path() / "data" / "UserList" / "demon.json"

# 解密相关
berry_path = Path() / "data" / "Userlist" / "secret.json"

# Boss名称库
boss_names = {
    "mini": ["暗影怪物", "创世纪", "鸟人像", "古迹守护者"],
    "normal": ["凌波微步", "奥歘", "海坡", "酥坡", "蹭墙", "牛抽奖"],
    "hard": ["Confringo", "野生小卒", "Desom-fu", "WaterDrop", "海豚", "prehasb"],
    "world": ["Fhloy", "Foxeline", "Fronia", "Mosed", "pbot", "水滴伯特", "小小卒", "猫猫伯特"]
}