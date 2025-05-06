from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
from pathlib import Path
import textwrap
import random
from .config import save_dir, font_path, background_dir, background_template
from .shop import background_shop

__all__ = ["draw_qd", "generate_background_preview"]  # 定义模块公开接口

def texture_render(image: Image, file: str, x: int, y: int, scale: int = 1):
    """
    将纹理图片渲染到目标图像上
    
    参数:
        image: 目标图像对象
        file: 纹理文件路径
        x: 粘贴位置的x坐标
        y: 粘贴位置的y坐标
        scale: 缩放比例(默认为1)
    """
    try:
        texture = Image.open(file)
        # 确保图像是RGBA模式(带透明度)
        if texture.mode != 'RGBA':
            texture = texture.convert('RGBA')
            
        new_size = (int(texture.size[0] * scale), int(texture.size[1] * scale))
        texture = texture.resize(new_size)
        
        # 分离alpha通道作为蒙版
        if texture.mode == 'RGBA':
            r, g, b, a = texture.split()
            image.paste(texture, (x, y), a)  # 使用alpha通道作为蒙版
        else:
            image.paste(texture, (x, y))  # 没有透明度则直接粘贴
    except Exception as e:
        print(f"渲染纹理时出错: {e}")

def is_dark_background(image: Image, threshold: int = 128) -> bool:
    """
    检测图片是否为暗色调背景
    
    参数:
        image: 要检测的图像
        threshold: 亮度阈值(默认128)
    返回:
        bool: 如果平均亮度低于阈值返回True
    """
    gray_image = image.convert('L')  # 转换为灰度图像
    histogram = gray_image.histogram()  # 获取直方图
    pixels = sum(histogram)
    brightness = sum(i * num for i, num in enumerate(histogram)) / pixels  # 计算平均亮度
    return brightness < threshold  # 判断是否低于阈值

def draw_centered_text_outline(draw: ImageDraw, image: Image, add_x: int, add_y: int, 
                             text: str, font: ImageFont, color: str, outline_color: str, 
                             image_width: int, image_height: int, blur_bg: bool = True):
    """
    绘制带描边的居中文本，可选择模糊背景
    
    参数:
        draw: ImageDraw对象
        image: 图像对象
        add_x: x轴偏移量
        add_y: y轴偏移量
        text: 要绘制的文本
        font: 字体对象
        color: 文本颜色
        outline_color: 描边颜色
        image_width: 图像宽度
        image_height: 图像高度
        blur_bg: 是否模糊背景(默认为True)
    """
    # 计算文本边界框
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]  # 文本实际宽度
    text_height = text_bbox[3] - text_bbox[1]  # 文本实际高度

    # 计算中心位置
    x = (image_width - text_width) // 2
    y = (image_height - text_height) // 2
    
    # 应用偏移量
    x += add_x
    y += add_y
    
    # 如果需要模糊背景
    if blur_bg:
        # 设置背景区域边距和羽化范围
        padding = 30
        feather = 20  # 渐变范围
        
        # 计算背景区域坐标(确保不超出图像边界)
        bg_x1 = max(0, x - padding)
        bg_y1 = max(0, y - padding)
        bg_x2 = min(image_width, x + text_width + padding)
        bg_y2 = min(image_height, y + text_height + padding)
        
        # 创建渐变遮罩
        mask = Image.new("L", (bg_x2 - bg_x1, bg_y2 - bg_y1), 255)
        draw_mask = ImageDraw.Draw(mask)
        
        # 绘制渐变边缘
        for i in range(feather):
            alpha = int(255 * (i / feather))
            draw_mask.rectangle(
                (i, i, mask.width - i, mask.height - i),
                outline=alpha
            )
        
        # 裁剪背景区域
        bg_region = image.crop((bg_x1, bg_y1, bg_x2, bg_y2))
        # 应用高斯模糊
        blurred_bg = bg_region.filter(ImageFilter.GaussianBlur(radius=5))
        
        # 使用渐变遮罩合成模糊效果
        image.paste(blurred_bg, (bg_x1, bg_y1), mask)
    
    # 绘制描边(四个方向的偏移)
    draw.text((x-1, y-1), text, fill=outline_color, font=font, align="center")
    draw.text((x+1, y-1), text, fill=outline_color, font=font, align="center")
    draw.text((x-1, y+1), text, fill=outline_color, font=font, align="center")
    draw.text((x+1, y+1), text, fill=outline_color, font=font, align="center")
    # 绘制主文本
    draw.text((x, y), text, fill=color, font=font, align="center")

# 全局变量用于循环保存文件名
current_index = 1

def draw_qd(
    nickname: str,
    berry: int,
    extra_berry: int = 0,
    double_berry: int = 0,
    background_variant: str = "1",
    blur_bg: bool = True
):
    """
    生成签到卡片图像
    
    参数:
        nickname: 用户昵称
        berry: 基础草莓数量
        extra_berry: 额外草莓数量(默认为0)
        double_berry: 是否双倍草莓(默认为0)
        background_variant: 背景变体编号(默认为"1")
        blur_bg: 是否模糊文本背景(默认为True)
    
    返回:
        tuple: (文件路径, 奖励文本, 运势文本)
    """
    global current_index

    # 设置图像尺寸(宽度960，高度720)
    width, height = 960, 719
    # 创建白色背景图像
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    # 根据模板生成背景文件名
    background_filename = background_template.format(background_variant)
    background_filepath = background_dir / background_filename

    # 检查背景文件是否存在，不存在则使用默认背景
    if not background_filepath.exists():
        background_filepath = background_dir / "qd1.png"

    # 渲染背景图像
    texture_render(image, background_filepath, 0, 0)
    
    # 检测背景亮度并设置文字颜色
    background_image = Image.open(background_filepath)
    if is_dark_background(background_image):
        text_color = "white"  # 暗背景使用白色文字
        outline_color = "black"  # 黑色描边
    else:
        text_color = "black"  # 亮背景使用黑色文字
        outline_color = "white"  # 白色描边

    # 加载字体(大小46px)
    font = ImageFont.truetype(font_path, 46)
    
    # 生成奖励文本
    if extra_berry == 0:
        text = f"签到成功，奖励{berry}颗草莓"
    else:
        text = f"签到成功，奖励{berry}+{extra_berry}颗草莓"

    # 运势文本字典(根据草莓数量返回不同文案)
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
        (91, 99): "快去抽卡吧，奇想盲盒和600草莓在等着你！",
        100: "哇哦，100诶！那你一定能一把理论测试如果Y PP毕加索 秒杀大屠杀 AP+脆肚！"
    }

    # 默认运势文本
    luck_text = "不可能有这条消息，你升桂了！"

    # 查找匹配的运势文本
    for key, value in luck_dict.items():
        if isinstance(key, tuple):  # 处理范围键
            if key[0] <= berry <= key[1]:
                luck_text = value
                break
        elif berry == key:  # 处理单个值键
            luck_text = value
            break

    # 文本自动换行(每行最多11个字符)
    wrapped_luck_text = "\n".join(textwrap.wrap(luck_text, width=11))

    # 双倍奖励文本
    text2 = f"检测到你拥有鱼之契约\n本次签到获得草莓翻倍为{(berry+extra_berry)*2}颗！"

    # 绘制所有文本元素
    if double_berry == 1:
        draw_centered_text_outline(draw, image, 0, -180, text2, font, text_color, outline_color, width, height, blur_bg)
        draw_centered_text_outline(draw, image, 0, -40, f"{nickname}", font, text_color, outline_color, width, height, blur_bg)
        draw_centered_text_outline(draw, image, 0, 39, text, font, text_color, outline_color, width, height, blur_bg)
        draw_centered_text_outline(draw, image, 0, 220, wrapped_luck_text, font, text_color, outline_color, width, height, blur_bg)
    else:
        draw_centered_text_outline(draw, image, 0, -160, f"{nickname}", font, text_color, outline_color, width, height, blur_bg)
        draw_centered_text_outline(draw, image, 0, -89, text, font, text_color, outline_color, width, height, blur_bg)
        draw_centered_text_outline(draw, image, 0, 120, wrapped_luck_text, font, text_color, outline_color, width, height, blur_bg)

    # 保存图像(output1.png到output15.png循环)
    file_name = save_dir / f"output{current_index}.png"
    image.save(file_name)

    # 更新文件索引(1-15循环)
    current_index = (current_index % 15) + 1

    return str(file_name), text, luck_text

def generate_background_preview():
    """生成所有背景的预览拼接图"""
    # 每行显示的图片数量
    IMAGES_PER_ROW = 4
    
    # 图片尺寸 (根据你的draw_qd函数输出尺寸调整)
    IMAGE_WIDTH = 960
    IMAGE_HEIGHT = 719
    
    # 保存路径
    REVIEW_IMAGE_PATH = background_dir / "qdbg_review.png"
    
    # 计算需要多少行
    bg_count = len(background_shop)
    rows = (bg_count + IMAGES_PER_ROW - 1) // IMAGES_PER_ROW
    
    # 创建最终的大图
    result_width = IMAGE_WIDTH * IMAGES_PER_ROW
    result_height = IMAGE_HEIGHT * rows
    result_image = Image.new('RGB', (result_width, result_height))
    
    # 生成每张预览图并拼接
    preview_images = []
    for bg_id in background_shop.keys():
        # 随机生成参数
        berry = random.randint(1, 100)
        extra_berry = random.choice([0, 60])
        double_berry = random.choice([0, 1])
        
        # 生成预览图
        picture_str, _, _ = draw_qd(
            nickname="预览",
            berry=berry,
            extra_berry=extra_berry,
            double_berry=double_berry,
            background_variant=str(bg_id)
        )
        
        # 打开图片并添加到列表
        img = Image.open(Path(picture_str))
        preview_images.append(img)
    
    # 拼接图片
    for i, img in enumerate(preview_images):
        row = i // IMAGES_PER_ROW
        col = i % IMAGES_PER_ROW
        x = col * IMAGE_WIDTH
        y = row * IMAGE_HEIGHT
        result_image.paste(img, (x, y))
    
    # 保存拼接后的图片
    result_image.save(REVIEW_IMAGE_PATH)
    
    return REVIEW_IMAGE_PATH