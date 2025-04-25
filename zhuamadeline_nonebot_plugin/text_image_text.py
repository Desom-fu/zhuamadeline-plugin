from PIL import Image, ImageDraw, ImageFont, ImageSequence 
from pathlib import Path
import textwrap  
import uuid
import re
from .config import save_dir, font_path
from nonebot.adapters.onebot.v11 import MessageSegment

# 字体设置
font_size = 24  # 基础字体大小
font = ImageFont.truetype(str(font_path), font_size)  # 加载字体

# 画布参数
MAX_WIDTH = 800           # 画布最大宽度（像素）
MAX_IMAGE_HEIGHT = 600    # 图片最大高度（像素）
PADDING = 30              # 四周留白（像素）
LINE_SPACING = 5          # 行间距（像素）
CACHE_LIMIT = 40          # 缓存文件保留数量

# 愚人节特供！
# def wrap_text(text, max_chars=20):
#     """
#     将文本按段落拆分，并按单词/数字块自动换行
#     - 连续的字母（如 "hello"）视为 1 个单元
#     - 连续的数字（如 "123"）视为 1 个单元
#     - 其他字符（标点、空格、换行）仍按 1 个字符处理
#     """
#     lines = []
#     paragraphs = text.split("\n")
    
#     for paragraph in paragraphs:
#         if not paragraph.strip():
#             lines.append("\n")  # 保留空行
#             continue
        
#         # 使用正则表达式分割单词和数字块
#         tokens = re.findall(r'([a-zA-Z]+|\d+|\s|[^\w\s])', paragraph)
        
#         current_line = []
#         current_length = 0
        
#         for token in tokens:
#             token_length = len(token)
            
#             # 如果当前行 + 新 token 不超过 max_chars，则加入当前行
#             if current_length + token_length <= max_chars:
#                 current_line.append(token)
#                 current_length += token_length
#             else:
#                 # 否则，换行
#                 if current_line:
#                     lines.append("".join(current_line))
#                 current_line = [token]
#                 current_length = token_length
        
#         # 添加最后一行
#         if current_line:
#             lines.append("".join(current_line))
    
#     return lines

def wrap_text(text, max_chars=20):
    """
    智能换行函数（支持中英文混合、特殊符号处理）
    
    参数：
    - text: 输入文本
    - max_chars: 每行最大字符单位数
    
    返回：
    - 按语义分块的文本行列表
    
    处理规则：
    1. 数学表达式（如1+2）视为1单元
    2. 英文单词（含下划线）视为1单元
    3. 符号组合（如@#）视为1单元
    4. 单个中文字符视为1单元
    """
    lines = []
    paragraphs = text.split("\n")
    
    # 改进后的正则表达式模式
    token_pattern = re.compile(
        r"($$\d+[\+\-\*/=]+\d+$$|"   # 数学表达式
        r"[a-zA-Z_]+(?:'[a-zA-Z_]+)*|"  # 英文单词（含下划线）
        r"\d+|"          # 连续数字
        r"[^\w\s\u4e00-\u9fff]{2,}|"  # 符号组合（2+字符）
        r"[^\w\s\u4e00-\u9fff]|"  # 单个符号
        r"[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]|"  # 中文字符
        r"\s)"           # 空白字符
    )
    
    for paragraph in paragraphs:
        if not paragraph.strip():
            lines.append("\n")  # 保留空行
            continue
        
        tokens = token_pattern.findall(paragraph)
        current_line = []
        current_length = 0
        
        for token in tokens:
            # 每个token视为1个字符单位（实际宽度后续计算）
            token_length = 1
            
            if current_length + token_length <= max_chars:
                current_line.append(token)
                current_length += token_length
            else:
                if current_line:
                    lines.append("".join(current_line))
                current_line = [token]
                current_length = token_length
        
        if current_line:
            lines.append("".join(current_line))
    
    return lines

def draw_text(draw, lines, y, canvas_width, center=True):
    """
    在画布上绘制多行文本（自动处理溢出）
    
    参数：
    - draw: ImageDraw对象
    - lines: 文本行列表
    - y: 起始Y坐标
    - canvas_width: 画布可用宽度
    - center: 是否居中
    
    返回：
    - 绘制结束后的Y坐标
    """
    for line in lines:
        if line == "\n":  # 处理空行
            y += font_size + LINE_SPACING
            continue
            
        # 获取文本实际尺寸
        bbox = draw.textbbox((0, 0), line, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        
        # 非居中时的溢出处理
        if not center and w > canvas_width - 2 * PADDING:
            # 计算最大可容纳字符数（近似值）
            max_len = int(len(line) * (canvas_width - 2 * PADDING) / w)
            line = line[:max(max_len, 1)]  # 至少保留1字符
            bbox = draw.textbbox((0, 0), line, font=font)
            w = bbox[2] - bbox[0]
        
        # 计算X坐标（居中或左对齐）
        x = (canvas_width - w) // 2 if center else PADDING
        
        # 实际绘制
        draw.text((x, y), line, font=font, fill="black")
        y += h + LINE_SPACING
    
    return y

def calculate_content_size(draw, lines, image_size=None):
    """
    计算内容总尺寸（文本+图片）
    
    参数：
    - draw: 用于测量的ImageDraw对象
    - lines: 文本行列表
    - image_size: 图片尺寸（宽,高），可选
    
    返回：
    - (总宽度, 总高度)
    """
    max_width = 0
    total_height = 0
    
    # 测量文本尺寸
    for line in lines:
        if line == "\n":
            total_height += font_size + LINE_SPACING
            continue
            
        bbox = draw.textbbox((0, 0), line, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        max_width = max(max_width, w)
        total_height += h + LINE_SPACING
    
    # 加入图片尺寸
    if image_size:
        img_w, img_h = image_size
        max_width = max(max_width, img_w)
        total_height += img_h + 2 * font_size  # 图片前后间距
    
    return max_width, total_height

def generate_frame(text1, text2, base_image=None, center=True, max_chars=20):
    """
    生成单帧图像（核心逻辑）
    
    参数：
    - text1: 顶部文本
    - text2: 底部文本
    - base_image: PIL图像对象（可选）
    - center: 是否居中
    
    返回：
    - 生成的PIL图像对象
    """
    # 创建临时画布用于测量
    dummy = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(dummy)
    
    # 文本预处理
    lines1 = wrap_text(text1, max_chars) if text1 else [] 
    lines2 = wrap_text(text2, max_chars) if text2 else []
    
    # 图片尺寸计算
    img_size = None
    if base_image:
        # 动态计算最大图片宽度（考虑中文字符宽度）
        max_img_width = min(MAX_WIDTH - 2 * PADDING, font_size * 20)
        
        # 保持宽高比的缩放计算
        orig_w, orig_h = base_image.size
        scale = min(
            MAX_IMAGE_HEIGHT / orig_h,
            max_img_width / orig_w,
            1.0  # 不放大
        )
        img_size = (int(orig_w * scale), int(orig_h * scale))
    
    # 计算内容总尺寸
    content_width, content_height = calculate_content_size(
        draw, lines1 + lines2, img_size
    )
    
    # 确定画布尺寸（不超过最大限制）
    canvas_width = min(content_width + 2 * PADDING, MAX_WIDTH)
    canvas_height = content_height + 2 * PADDING
    
    # 创建实际画布
    canvas = Image.new("RGBA", (canvas_width, canvas_height), "white")
    draw = ImageDraw.Draw(canvas)
    y = PADDING  # 初始Y坐标
    
    # 绘制顶部文本
    y = draw_text(draw, lines1, y, canvas_width, center)
    
    # 绘制图片（如果有）
    if base_image and img_size:
        y += font_size  # 图片前间距
        img_w, img_h = img_size
        img_x = (canvas_width - img_w) // 2 if center else PADDING
        resized_img = base_image.resize(img_size, Image.LANCZOS)
        canvas.paste(resized_img, (img_x, y), resized_img)
        y += img_h + font_size  # 图片高度+后间距
    
    # 绘制底部文本
    y = draw_text(draw, lines2, y, canvas_width, center)
    
    return canvas

def clean_cache():
    """清理过期缓存文件"""
    files = sorted(save_dir.glob("send_image*"), key=lambda f: f.stat().st_mtime)
    for f in files[:-CACHE_LIMIT]:
        try:
            f.unlink()
        except:
            pass

def generate_image_with_text(text1, image_path, text2, max_chars=20, center=True):
    """
    主生成函数（支持静态图/GIF）
    
    参数：
    - text1: 顶部文本
    - image_path: 图片路径（可选）
    - text2: 底部文本
    - max_chars: 换行字符数限制
    - center: 是否居中
    
    返回：
    - 生成的文件Path对象
    """
    # 参数检查
    if not text1 and not image_path and not text2:
        return None
    
    # 预处理图片路径
    image_path = str(image_path) if image_path else None
    is_gif = image_path and image_path.lower().endswith(".gif")
    
    # 清理旧缓存
    clean_cache()
    
    # 生成唯一文件名
    file_id = uuid.uuid4().hex[:8]
    
    try:
        # GIF处理
        if is_gif and Path(image_path).exists():
            frames = []
            durations = []
            gif = Image.open(image_path)
            
            for frame in ImageSequence.Iterator(gif):
                frame = frame.convert("RGBA")
                result_frame = generate_frame(text1, text2, frame, center, max_chars)
                frames.append(result_frame)
                durations.append(frame.info.get("duration", 100))
            
            output_path = save_dir / f"send_image{file_id}.gif"
            frames[0].save(
                output_path,
                save_all=True,
                append_images=frames[1:],
                loop=0,
                duration=durations,
                disposal=2,
                optimize=False
            )
            return output_path
        
        # 静态图处理
        image = Image.open(image_path).convert("RGBA") if image_path else None
        result = generate_frame(text1, text2, image, center, max_chars)
        output_path = save_dir / f"send_image{file_id}.png"
        result.save(output_path)
        return output_path
    
    except Exception as e:
        print(f"图像生成失败: {str(e)}")
        return None

# 以下为消息发送相关函数（保持原样）
async def send_image_or_text(handler, text, at_sender=False, forward_text=None, max_chars=30):
    """发送图文消息的便捷函数"""
    img = generate_image_with_text(
        text1=text,
        image_path=None,
        text2=None,
        max_chars=max_chars,
        center=False
    )
    message = (forward_text or "") + (MessageSegment.image(img) if img else text)
    await handler.finish(message, at_sender=at_sender)

async def send_image_or_text_forward(handler, text, forward_text, bot, bot_id, group_id, max_chars=30, at_sender=False):
    """通过转发消息发送图文"""
    img = generate_image_with_text(
        text1=text,
        image_path=None,
        text2=None,
        max_chars=max_chars,
        center=False
    )
    if img:
        await handler.finish(forward_text + MessageSegment.image(img), at_sender=at_sender)
    else:
        msg_list = [{
            "type": "node",
            "data": {
                "name": forward_text,
                "uin": bot_id,
                "content": text
            }
        }]
        await bot.call_api("send_group_forward_msg", group_id=group_id, messages=msg_list)
        await handler.finish()

async def auto_send_message(text, bot, group_id, forward_text=None, max_chars=30):
    """自动发送消息到群组"""
    img = generate_image_with_text(
        text1=text,
        image_path=None,
        text2=None,
        max_chars=max_chars,
        center=False
    )
    message = (forward_text or "") + (MessageSegment.image(img) if img else text)
    await bot.send_group_msg(group_id=group_id, message=message)