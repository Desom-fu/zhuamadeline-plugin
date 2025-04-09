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
    'hourglass_max'
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
madeline_path_lc4 = Path() / "data" / "madelineLc4"   #三号猎场

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
user_path = Path() / "Data" / "UserList"
file_name = "UserData.json"
full_path = user_path / file_name
cd_path = Path() / "Data" / "UserList" / "allcooldown.json"
bar_path = Path() / "data" / "UserList" / "bar.json"
garden_path = Path() / "data" / "UserList" / "garden.json"

#赌场信息
duchang_list = Path() / "data" / "DuChang" / "duchang.json"
duchang_open_img = Path() / "data" / "DuChang" / "duchang.png"