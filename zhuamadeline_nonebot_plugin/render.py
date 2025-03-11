#roris的渲染模块，给roris提高颜值
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import textwrap  # 用于处理文本换行

__all__ = ["draw_qd"]

#保存目录
save_dir = Path()/"Data"/"Image"

#素材和字体
font_path = Path()/"Data"/"Image"/"ZhanKu.ttf"
background_qd = Path()/"Data"/"Image"/"background_qd.png"

#将图片渲染到绘制对象上
def texture_render(image: Image, file: str, x: int, y: int, scale: int=1):
    texture = Image.open(file)
    new_size = (int(texture.size[0]*scale), int(texture.size[1]*scale))
    texture = texture.resize(new_size)
    image.paste(texture, (x, y), texture)

#渲染带边缘的作文本
def draw_text_outline(draw: ImageDraw, x: int, y: int, text: str, font: ImageFont, color: str, outline_color: str):
    draw.text((x-1, y-1), text, fill=outline_color, font=font, align="center")
    draw.text((x+1, y-1), text, fill=outline_color, font=font, align="center")
    draw.text((x-1, y+1), text, fill=outline_color, font=font, align="center")
    draw.text((x+1, y+1), text, fill=outline_color, font=font, align="center")
    draw.text((x, y), text, fill=color, font=font, align="center")

# 引入一个全局变量来跟踪文件名
current_index = 1

def draw_qd(nickname: str, berry: int, extra_berry: int = 0, double_berry: int = 0):
    global current_index  # 声明为全局变量
    # 创建一个白色背景的图像
    width, height = 960, 608
    image = Image.new("RGB", (width, height), "white")

    # 创建一个可以在上面绘制的对象
    draw = ImageDraw.Draw(image)

    # 绘制背景图
    texture_render(image, background_qd, 0, 0)

    # 设置字体和颜色
    font = ImageFont.truetype(font_path, 46)
    if extra_berry == 0:
        text = f"签到成功，奖励{berry}颗草莓"
    else:
        text = f"签到成功，奖励{berry}+{extra_berry}颗草莓"
    text_color = "black"
    outline_color = "white"

    # 随机文案
    luck_dict = {
        1: "哇哦，大成功诶！但是这不是coc，祝你好运！",
        (2, 10): "三军听令，自刎归天！",
        (11, 15): "质疑。唉我真的是服了，天天今日人品这么差劲。",
        16: "抽的好！奖励你去到处都是果冻的塔进行劲爆路线解密！",
        (17, 30): "质疑。唉我真的是服了，天天今日人品这么差劲。",
        (31, 50): "O-O 小芙能有什么坏心眼呢？",
        (51, 65): "超过一半了，或许今天运气还不错？",
        66: "抽的好！奖励你蹲着跑去LXVI和一堆圆刺激情碰撞！",
        (67, 70): "超过一半了，或许今天的运气还不错？",
        (71, 73): "没准今天你能出个金草莓或者过一个榜图？",
        74: "抽的好！奖励你跑到全是咖啡跳的无名旅馆和冰球斗智斗勇！",
        (75, 90): "没准今天你能出个金草莓或者过一个榜图？",
        (91, 99): "快去刮刮乐吧，奇想盲盒和600草莓在等着你！",
        100: "哇哦，100诶！那你一定能一把理论测试如果Y PP毕加索 秒杀大屠杀 AP+脆肚！"
    }

    # 设置默认文案
    luck_text = "不可能有这条消息，你升桂了！"

    # 遍历字典查找匹配的范围
    for key, value in luck_dict.items():
        if isinstance(key, tuple):  # 如果键是一个元组，表示一个范围
            if key[0] <= berry <= key[1]:
                luck_text = value
                break
        elif berry == key:  # 如果键是单个值
            luck_text = value
            break

    # 文本分行（每 11 个字换行）
    wrapped_luck_text = "\n".join(textwrap.wrap(luck_text, width=11))

    # 文本位置
    x = 325
    y = 245
    
    text2 = f"检测到你拥有鱼之契约\n本次签到获得草莓翻倍为{(berry+extra_berry)*2}颗！"
    # 获取文本的边界框
    text_bbox = draw.textbbox((0, 0), text2, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # 计算中心位置
    center_x = (image.width - text_width) // 2
    center_y = (image.height - text_height) // 2
    
    # 在图片上绘制文本
    if double_berry == 1:
        draw_text_outline(draw, center_x, y-170, text2, font, text_color, outline_color)
    draw_text_outline(draw, x, y - 64, f"{nickname}", font, text_color, outline_color)  # 绘制用户名称
    draw_text_outline(draw, x, y, text, font, text_color, outline_color)  # 绘制奖励多少草莓
    draw_text_outline(draw, x + 115, y + 96, wrapped_luck_text, font, text_color, outline_color)  # 绘制文案

    # 保存图像为 PNG 文件，文件名为 output1.png 到 output15.png
    file_name = save_dir / f"output{current_index}.png"
    image.save(file_name)

    # 更新文件名索引，循环回 1 到 15
    current_index = (current_index % 15) + 1

    # 输出文件路径
    return str(file_name), text, luck_text
