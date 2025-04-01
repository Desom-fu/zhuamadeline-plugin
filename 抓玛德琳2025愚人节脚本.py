import re
import random
import os

class ChineseReplacer:
    def __init__(self):
        self.char_map = {}  # 全局字符映射表

    def replace(self, text):
        """执行逐字替换，但跳过白名单词汇中的所有中文字符"""
        # 定义白名单
        whitelist = {
            "生命之叶", "天使之羽", "紫晶魄", "木质十字架", "圣十字架", "鲜血之刃",
            "尘封的秘宝", "奇想魔盒", "奇想扑克", "矿工头盔", "调律器", "回想之核",
            "星光乐谱", "身份徽章", "飞升器", "红色球体", "绿色球体", "黄色球体",
            "充能箱", "脉冲雷达", "磁力吸附手套", "炸弹包", "遥控机器人", "鱼之契约",
            "星辰碎屑", "喵喵呜呜", "充能器", "草莓加工器", "时间献祭器", "果酱机",
            "草莓鱼竿", "招财猫", "道具盲盒", "弹弓", "一次性小手枪", "充能陷阱",
            "胡萝卜", "烂胡萝卜", "时间秒表", "提取器", "万能解药", "幸运药水",
            "急救包", "赌徒之眼", "草莓果酱", "指南针", "神秘碎片", "音矿", "安定之音",
            "残片", "复仇之刃", "神权模拟器", "海星", "水母", "胖头鱼", "胖头鱼罐头",
            "水晶胖头鱼", "星鱼", "阿拉胖头鱼", "桃", "医疗箱", "放大镜", "眼镜",
            "手铐", "欲望之盒", "无中生有", "小刀", "酒", "啤酒", "刷新票", "手套",
            "骰子", "禁止卡", "墨镜", "双转团", "天秤", "休养生息", "玩具枪", "烈弓",
            "血刃", "黑洞", "金苹果", "铂金草莓", "肾上腺素", "烈性", "梅花", "方片",
            "黑桃", "红桃", "大于7", "小于7", "花色", "点数", "开枪", "自己", "对方",
            "查看局势", "恶魔道具", "恶魔投降", "使用道具", "收菜", "收获", "收割",
            "施肥", "肥料", "偷菜", "偷取", "窃取", "播种", "种植", "种菜", "查询",
            "状态", "查看", "充能器", "加工器", "果酱机", "草莓机", "提取器", "鱼竿",
            "钓竿", "草莓钓竿", "盲盒", "秒表", "陷阱", "音符", "解药", "幸运",
            "神秘药水", "小手枪", "手枪", "时间提取器", "献祭器", "身份", "徽章",
            "学费", "电箱", "飞升器", "木制十字架", "血刃", "秘宝", "乐谱", "气笑魔盒",
            "奇效魔盒", "魔盒", "墨盒", "气笑魔牌", "奇效魔牌", "气笑扑克", "奇效扑克",
            "魔牌", "扑克", "星尘碎屑", "碎屑", "头盔", "草莓果园", "果园", "地契", "星钻", "抓"
            "宝藏"
        }

        # 提取白名单中的所有不重复中文字符
        whitelist_chars = set()
        for word in whitelist:
            whitelist_chars.update(re.findall(r'[\u4e00-\u9fff]', word))

        def replacer(match):
            char = match.group()
            # 如果字符在白名单中，直接返回原字符
            if char in whitelist_chars:
                return char
            # 否则进行替换
            if char not in self.char_map:
                self.char_map[char] = random.choices(
                    ['喵', '呜', '呣~', '呼~'],
                    weights=[40, 40, 10, 10]
                )[0]
            return self.char_map[char]

        return re.sub(r'[\u4e00-\u9fff]', replacer, text)
    

def process_directory(target_dir):
    """处理目录下所有Python文件"""
    replacer = ChineseReplacer()  # 创建统一的替换器
    
    for root, dirs, files in os.walk(target_dir):
        if 'venv' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                process_file(file_path, replacer)

def process_file(file_path, replacer):
    """处理单个文件"""
    try:
        with open(file_path, 'r+', encoding='utf-8') as f:
            content = f.read()
            new_content = replacer.replace(content)
            
            if new_content != content:
                f.seek(0)
                f.write(new_content)
                f.truncate()
                print(f"已处理：{file_path}")
    except Exception as e:
        print(f"处理失败 {file_path}: {str(e)}")

if __name__ == "__main__":
    # 设置随机种子确保可复现
    random.seed(114514)  
    
    target_path = input("请输入要处理的路径：").strip()
    
    if os.path.exists(target_path):
        print("== 注意：所有相同汉字将被统一替换 ==")
        print("== 操作注意事项 ==")
        print("1. 建议先备份整个项目")
        print("2. 处理后的代码可能无法运行")
        
        process_directory(target_path)
        
        print("处理完成！")
        print("请检查重要文件：")
        print("- 包含中文注释的逻辑文件")
        print("- 包含中文字符串的配置文件")
    else:
        print("路径不存在！")