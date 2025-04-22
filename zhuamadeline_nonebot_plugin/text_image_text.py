from PIL import Image, ImageDraw, ImageFont, ImageSequence 
from pathlib import Path
import textwrap  
import uuid
from .config import save_dir, font_path
from nonebot.adapters.onebot.v11 import MessageSegment

# 设置字体相关
font_size = 24  # 字体大小
font = ImageFont.truetype(str(font_path), font_size)  # 加载字体对象

# 设置图像最大尺寸和缓存限制
MAX_WIDTH = 800           # 画布最大宽度
MAX_IMAGE_HEIGHT = 600    # 图像最大高度（超过则缩放）
PADDING = 20              # 画布四周留白
CACHE_LIMIT = 20          # 缓存目录中保留最近生成的文件数


def wrap_text(text, max_chars=20):
    """
    将文本按段落拆分并自动换行，保留所有换行符
    text: 原始文本
    max_chars: 每行最大字符数
    返回列表形式的每行文本
    """
    lines = []
    paragraphs = text.split("\n")
    for paragraph in paragraphs:
        if paragraph.strip() == "":
            # 对于空段落，添加一个空行标记
            lines.append("\n")  # 使用特殊标记表示这是换行符产生的空行
        else:
            # 对非空段落进行自动换行处理
            wrapped = textwrap.wrap(paragraph, width=max_chars)
            if not wrapped:  # 处理空字符串但不是纯空白的情况
                wrapped = [""]
            lines.extend(wrapped)
    return lines


def draw_text(draw, lines, y, canvas_width, line_spacing=5, center=True):
    """
    在画布上绘制多行文本
    draw: ImageDraw 对象
    lines: 文本行列表
    y: 初始垂直坐标
    canvas_width: 画布宽度
    line_spacing: 行间距像素值
    center: 是否水平居中显示
    返回绘制结束后的 y 坐标
    """
    # 获取字体高度
    dummy_bbox = draw.textbbox((0, 0), "A", font=font)
    font_height = dummy_bbox[3] - dummy_bbox[1]
    
    for line in lines:
        if line == "\n":  # 这是换行符产生的空行
            y += font_height + line_spacing  # 只增加行高和间距
            continue
            
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]  # 文本宽度
        h = bbox[3] - bbox[1]  # 文本高度
        x = (canvas_width - w) // 2 if center else PADDING  # 居中使用计算位置，不居中使用PADDING
        draw.text((x, y), line, font=font, fill="black")
        y += h + line_spacing  # 更新 y 坐标到下一行，并添加行间距
    return y


def clean_cache():
    """
    清理旧图像文件，保留最新 CACHE_LIMIT 个文件
    """
    # 获取所有匹配的文件并按修改时间排序
    files = sorted(save_dir.glob("send_image*"), key=lambda f: f.stat().st_mtime)
    # 删除最旧的文件，保留最新的 CACHE_LIMIT 个
    for f in files[:-CACHE_LIMIT]:
        f.unlink()


def generate_image_with_text(text1, image_path, text2, max_chars=20, center=True):
    """
    主函数：根据上下两段文本和可选图片生成静态图或 GIF
    text1: 顶部文字，可为空
    image_path: 图片路径，可为 None 或不存在(若是gif则是透明)
    text2: 底部文字，可为空
    max_chars: 每行最大字符数，默认20
    center: 是否水平居中显示，默认True
    返回生成文件的 Path 对象，或 None
    """
    # 若三者都为空，则无需生成
    if not text1 and not image_path and not text2:
        return None

    # 将可能为 Path 的 image_path 转成字符串
    image_path = str(image_path) if image_path else None

    # 对上下文字分别调用换行处理，使用传入的max_chars参数
    lines1 = wrap_text(text1, max_chars) if text1 else []
    lines2 = wrap_text(text2, max_chars) if text2 else []

    # 尝试打开图片文件
    image = None
    if image_path and Path(image_path).exists():
        image = Image.open(image_path)

    # 判断是否为 GIF 动图
    is_gif = image_path and image_path.lower().endswith(".gif")

    # 内部函数：生成单帧画布
    def generate_frame(base_image=None):
        # 用于测量文本尺寸的临时画布
        dummy = Image.new("RGB", (1, 1))
        draw = ImageDraw.Draw(dummy)

        # 辅助函数：计算多行文本的最大宽度和总高度
        def get_text_size(lines):
            widths = []
            total_height = 0
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                w = bbox[2] - bbox[0]
                h = bbox[3] - bbox[1]
                widths.append(w)
                total_height += h
            return max(widths) if widths else 0, total_height

        # 计算上下文字的宽度和高度
        text1_width, text1_height = get_text_size(lines1)
        text2_width, text2_height = get_text_size(lines2)

        # 处理图片缩放
        image_w, image_h = (0, 0)
        resized_image = None
        if base_image:
            iw, ih = base_image.size  # 原图宽高
            # 缩放比例：保持高度不超限，并且不放大
            scale = min((MAX_IMAGE_HEIGHT - 2 * PADDING) / ih, 1)
            image_w, image_h = int(iw * scale), int(ih * scale)
            resized_image = base_image.resize((image_w, image_h), Image.LANCZOS)
            # 内容最宽值需考虑图片宽度
            max_content_width = max(text1_width, text2_width, image_w)
        else:
            max_content_width = max(text1_width, text2_width)

        # 计算画布宽度（内容最大宽度 + 两侧PADDING，不超过MAX_WIDTH）
        canvas_width = min(max_content_width + 2 * PADDING, MAX_WIDTH)
        
        # 创建临时画布计算内容高度
        temp_canvas = Image.new("RGBA", (canvas_width, 1), "white")
        temp_draw = ImageDraw.Draw(temp_canvas)
        
        # 计算内容高度
        y = 0
        y = draw_text(temp_draw, lines1, y, canvas_width, center=center)
        if base_image:
            y += font_size  # 图片前留白
            y += image_h + font_size  # 图片高度和间距
        y = draw_text(temp_draw, lines2, y, canvas_width, center=center)
        
        # 计算实际需要的高度（内容高度 + 上下PADDING）
        content_height = y
        total_height = content_height + 2 * PADDING
        
        # 创建最终 RGBA 画布（确保四周都是PADDING）
        canvas = Image.new("RGBA", (canvas_width, total_height), "white")
        draw = ImageDraw.Draw(canvas)

        # 纵向起始位置：上方PADDING
        y = PADDING
        # 绘制上段文字并更新 y，使用传入的center参数
        y = draw_text(draw, lines1, y, canvas_width, center=center)
        
        # 如有图，粘贴并更新 y，保留gif透明度
        if resized_image:
            y += font_size  # 图片前留白
            x_pos = (canvas_width - image_w) // 2 if center else PADDING  # 图片位置同样遵循center参数
            canvas.paste(resized_image, (x_pos, y), resized_image)
            y += image_h + font_size  # 图片高度和间距

        # 绘制下段文字，使用传入的center参数
        y = draw_text(draw, lines2, y, canvas_width, center=center)
        
        # 确保底部留白为PADDING
        current_bottom_padding = total_height - y
        if current_bottom_padding != PADDING:
            # 调整画布高度
            new_total_height = y + PADDING
            new_canvas = Image.new("RGBA", (canvas_width, new_total_height), "white")
            new_canvas.paste(canvas, (0, 0))
            canvas = new_canvas
        
        return canvas

    # 清理旧缓存
    clean_cache()
    # 生成唯一文件名后缀
    current_send = uuid.uuid4().hex[:8]

    # 如果是 GIF 动图，逐帧处理
    if is_gif:
        frames = []
        durations = []

        for frame in ImageSequence.Iterator(image):
            frame = frame.convert("RGBA")

            # 创建和帧一样大小的透明画布
            full_frame = Image.new("RGBA", image.size, (255, 255, 255, 0))
            full_frame.paste(frame, (0, 0), frame)  # 确保 alpha 合成

            # 生成文字和图像结合后的帧
            result_frame = generate_frame(full_frame)
            frames.append(result_frame)
            durations.append(frame.info.get("duration", image.info.get("duration", 100)))

        # 保存GIF
        gif_path = save_dir / f"send_image{current_send}.gif"
        frames[0].save(
            gif_path,
            save_all=True,
            append_images=frames[1:],
            loop=0,
            duration=durations,
            disposal=2,  # 每帧清除之前内容
            optimize=False
        )
        return gif_path
    
    else:
        # 静态图，单帧处理
        result = generate_frame(image.convert("RGBA") if image else None)
        png_path = save_dir / f"send_image{current_send}.png"
        result.save(png_path)
        return png_path

async def send_image_or_text(handler, text, max_chars = 50, forward_text = ""):
    '''方便于直接发送的一个函数
    handler: 前缀，用于finish
    text: 发送的文本
    max_chars: 每一行最大字符串
    forward_text: 发在图片前的文本
    '''
    img = generate_image_with_text(
        text1=text,
        image_path=None,
        text2=None,
        max_chars=max_chars,
        center=False
    )
    if img:
        await handler.finish(forward_text + MessageSegment.image(img))
    else:
        await handler.finish(forward_text + text)

async def send_image_or_text_forward(handler, text, bot, bot_id, forward_name, group_id, max_chars = 50):
    '''方便于直接发送的一个函数（用转发）
    handler: 前缀，用于finish
    text: 发送的文本
    bot: 当前bot传递一下，一般就是bot
    bot_id: 一般是event.self_id
    forward_name: 转发的名字
    group_id: 发到哪个群
    max_chars: 每一行最大字符串
    '''
    img = generate_image_with_text(
        text1=text,
        image_path=None,
        text2=None,
        max_chars = max_chars,
        center=False
    )
    if img:
        await handler.finish(MessageSegment.image(img))
    else:
        # 图片生成失败，回退到转发消息
        msg_list = [
            {
                "type": "node",
                "data": {
                    "name": forward_name,
                    "uin": bot_id,
                    "content": text
                }
            }
        ]
        await bot.call_api("send_group_forward_msg", group_id=group_id, messages=msg_list)
        await handler.finish()  # 结束处理，避免重复发送消息