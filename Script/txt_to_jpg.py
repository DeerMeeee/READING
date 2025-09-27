from PIL import Image, ImageDraw, ImageFont
import textwrap
import os
import shutil
import re

# 避头尾字符定义
FORBIDDEN_START_CHARS = set('，,。.、！!？?：:；;”\'）]}》›»〉》〗】〕》」』】〗〞〟〉》›»〗〞〟"\'》›»}])）')
FORBIDDEN_END_CHARS = set('‘"（([{《‹「『【〖〝〝〈《‹「『【〖')

def get_chinese_font(font_size=20):
    """
    获取中文字体，尝试多个可能的字体路径
    """
    font_paths = [
        "C:/Windows/Fonts/simsun.ttc",      # 宋体
        "C:/Windows/Fonts/msyh.ttc",        # 微软雅黑
        "C:/Windows/Fonts/simkai.ttf",      # 楷体
        "C:/Windows/Fonts/simfang.ttf",     # 仿宋
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, font_size)
            except:
                continue
    
    try:
        return ImageFont.load_default()
    except:
        raise Exception("无法找到支持中文的字体")

def is_forbidden_start_char(char):
    """检查字符是否为避头字符"""
    return char in FORBIDDEN_START_CHARS

def is_forbidden_end_char(char):
    """检查字符是否为避尾字符"""
    return char in FORBIDDEN_END_CHARS

def wrap_text_with_indent_and_kinsoku(text, font, max_width, indent_chars="　　"):
    """
    智能文本换行，支持段首缩进2个全角空格和中文避头尾规则
    """
    lines = []
    paragraphs = text.split('\n')
    
    for paragraph in paragraphs:
        if not paragraph.strip():  # 空行
            lines.append("")
            continue
            
        # 段首添加2个全角空格
        current_text = indent_chars + paragraph.strip()
        
        # 处理避头尾规则的换行
        current_line = ""
        char_list = list(current_text)
        i = 0
        
        while i < len(char_list):
            char = char_list[i]
            
            # 测试添加当前字符后的行宽
            test_line = current_line + char
            line_width = font.getlength(test_line)
            
            if line_width <= max_width:
                current_line = test_line
                i += 1
            else:
                # 需要换行，检查避头尾规则
                if current_line:
                    # 检查当前行尾字符是否为避尾字符
                    if current_line and is_forbidden_end_char(current_line[-1]):
                        # 避尾字符不能出现在行尾，需要调整
                        if i < len(char_list) and not is_forbidden_start_char(char_list[i]):
                            # 将避尾字符移到下一行
                            last_char = current_line[-1]
                            current_line = current_line[:-1]
                            lines.append(current_line)
                            current_line = last_char + char
                            i += 1
                        else:
                            # 无法调整，强制换行
                            lines.append(current_line)
                            current_line = char
                            i += 1
                    else:
                        # 正常换行
                        lines.append(current_line)
                        current_line = char
                        i += 1
                else:
                    # 单个字符就超宽，强制换行
                    lines.append(char)
                    current_line = ""
                    i += 1
        
        # 处理剩余内容
        if current_line:
            # 检查行首是否为避头字符
            if current_line and is_forbidden_start_char(current_line[0]):
                if lines:
                    # 尝试将避头字符移到上一行
                    last_line = lines[-1]
                    if last_line and not is_forbidden_end_char(last_line[-1]):
                        # 可以移动
                        lines[-1] = last_line + current_line[0]
                        current_line = current_line[1:]
            
            if current_line:
                lines.append(current_line)
    
    return lines

def apply_kinsoku_rules(lines):
    """
    对已经换行的文本应用避头尾规则进行后处理
    """
    adjusted_lines = []
    
    for i in range(len(lines)):
        current_line = lines[i]
        
        if not current_line.strip():
            adjusted_lines.append(current_line)
            continue
            
        # 检查行首避头字符
        if is_forbidden_start_char(current_line[0]):
            if i > 0 and adjusted_lines:
                # 尝试将避头字符移到上一行
                prev_line = adjusted_lines[-1]
                if prev_line and not is_forbidden_end_char(prev_line[-1]):
                    # 可以移动
                    adjusted_lines[-1] = prev_line + current_line[0]
                    current_line = current_line[1:]
        
        # 检查行尾避尾字符
        if current_line and is_forbidden_end_char(current_line[-1]):
            if i < len(lines) - 1 and lines[i + 1]:
                # 尝试将避尾字符移到下一行
                next_line = lines[i + 1]
                if next_line and not is_forbidden_start_char(next_line[0]):
                    # 可以移动
                    lines[i + 1] = current_line[-1] + next_line
                    current_line = current_line[:-1]
        
        if current_line:
            adjusted_lines.append(current_line)
    
    return adjusted_lines

def wrap_text_with_indent(text, font, max_width, indent_chars="　　"):
    """
    智能文本换行，支持段首缩进2个全角空格和避头尾规则
    """
    # 首先进行基本换行
    lines = []
    paragraphs = text.split('\n')
    
    for paragraph in paragraphs:
        if not paragraph.strip():  # 空行
            lines.append("")
            continue
            
        # 段首添加2个全角空格
        current_text = indent_chars + paragraph.strip()
        char_list = list(current_text)
        
        current_line = ""
        for char in char_list:
            test_line = current_line + char
            if font.getlength(test_line) <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = char
        
        if current_line:
            lines.append(current_line)
    
    # 应用避头尾规则进行后处理
    return apply_kinsoku_rules(lines)

def calculate_optimal_width(font_size, scale_factor=2):
    """
    根据字体大小计算适合手机屏幕的宽度（考虑缩放因子）
    """
    # 基础手机屏幕宽度（物理像素）
    phone_widths = {
        'narrow': 360,
        'standard': 390,
        'wide': 428,
        'max': 480
    }
    
    # 根据字体大小选择基础宽度
    if font_size <= 20:
        base_width = phone_widths['wide']
    elif font_size <= 24:
        base_width = phone_widths['standard']
    else:
        base_width = phone_widths['narrow']
    
    # 应用缩放因子
    return int(base_width * scale_factor)

def split_lines_into_pages(lines, max_lines_per_page=50):
    """
    将文本行分割成多个页面，每个页面最多max_lines_per_page行
    
    Args:
        lines: 所有文本行的列表
        max_lines_per_page: 每页最大行数
    
    Returns:
        包含多个页面（每个页面是行列表）的列表
    """
    pages = []
    current_page = []
    
    for line in lines:
        if len(current_page) < max_lines_per_page:
            current_page.append(line)
        else:
            pages.append(current_page)
            current_page = [line]
    
    # 添加最后一页
    if current_page:
        pages.append(current_page)
    
    return pages

def create_image_from_lines(lines, font, img_width, img_height, margin, bg_color, text_color, line_height):
    """
    从文本行创建图片
    
    Args:
        lines: 文本行列表
        font: 字体对象
        img_width: 图片宽度
        img_height: 图片高度
        margin: 边距
        bg_color: 背景颜色
        text_color: 文字颜色
        line_height: 行高
    
    Returns:
        PIL Image对象
    """
    # 创建图片
    image = Image.new('RGB', (img_width, img_height), color=bg_color)
    draw = ImageDraw.Draw(image)
    
    # 绘制文本（左对齐）
    y = 40
    for line in lines:
        if line.strip():
            draw.text((margin, y), line, font=font, fill=text_color)
        y += line_height
    
    return image

def txt_to_jpg_batch(input_dir, output_dir, backup_dir, font_size=26, bg_color=(255, 255, 255), text_color=(0, 0, 0), max_lines_per_page=50):
    """
    批量将TXT文件转换为高清JPG图片（支持中文避头尾规则和分页功能）
    
    Args:
        input_dir: 输入目录
        output_dir: 输出目录
        backup_dir: 备份目录
        font_size: 基础字体大小
        bg_color: 背景颜色
        text_color: 文字颜色
        max_lines_per_page: 每页最大行数
    """
    
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(backup_dir, exist_ok=True)
    
    txt_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.txt')]
    
    if not txt_files:
        print(f"在目录 {input_dir} 中没有找到TXT文件")
        return
    
    print(f"找到 {len(txt_files)} 个TXT文件，开始高清转换...")
    print(f"使用字体大小: {font_size}px (高清模式)")
    print("启用中文避头尾规则处理")
    print(f"每页最多显示 {max_lines_per_page} 行文字")
    
    success_count = 0
    fail_count = 0
    total_pages = 0
    
    for txt_file in txt_files:
        input_path = os.path.join(input_dir, txt_file)
        base_filename = os.path.splitext(txt_file)[0]
        backup_path = os.path.join(backup_dir, txt_file)
        
        try:
            # 读取文本文件
            text = ""
            encodings = ['utf-8', 'gbk', 'gb2312', 'big5', 'utf-16']
            
            for encoding in encodings:
                try:
                    with open(input_path, 'r', encoding=encoding) as file:
                        text = file.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if not text:
                raise Exception("无法解码文件")
            
            # 高清缩放因子（2倍用于视网膜屏）
            scale_factor = 2
            hd_font_size = font_size * scale_factor
            
            # 获取中文字体（使用放大后的字体大小）
            font = get_chinese_font(hd_font_size)
            
            # 计算适合手机屏幕的宽度（考虑缩放因子）
            img_width = calculate_optimal_width(font_size, scale_factor)
            margin_px = int(img_width * 0.08)  # 8%的边距
            usable_width = img_width - 2 * margin_px
            
            print(f"处理文件: {txt_file}, 图片宽度: {img_width}px, 高清模式: {scale_factor}x")
            
            # 智能换行（支持段首缩进和避头尾规则）
            all_lines = wrap_text_with_indent(text, font, usable_width)
            
            # 将文本行分割成多个页面
            pages = split_lines_into_pages(all_lines, max_lines_per_page)
            
            # 计算每页的高度
            line_height = int(hd_font_size * 1.6)  # 1.6倍行距
            min_height = 800  # 最小高度（考虑缩放）
            
            # 为每个页面创建图片
            for page_num, page_lines in enumerate(pages, 1):
                # 计算当前页的高度
                page_height = line_height * len(page_lines) + 80
                if page_height < min_height:
                    page_height = min_height
                
                # 创建高清图片
                image = create_image_from_lines(
                    page_lines, font, img_width, page_height, 
                    margin_px, bg_color, text_color, line_height
                )
                
                # 生成带页码的输出文件名
                if len(pages) > 1:
                    output_filename = f"{base_filename}_页{page_num}.jpg"
                else:
                    output_filename = f"{base_filename}.jpg"
                
                output_path = os.path.join(output_dir, output_filename)
                
                # 保存超高质量图片
                image.save(
                    output_path, 
                    'JPEG', 
                    quality=100,           # 最高质量
                    optimize=True,         # 优化压缩
                    subsampling=0,         # 不进行色度抽样（保持最高色彩质量）
                    qtables='web_high'     # 使用高质量量化表
                )
                
                print(f"  ✓ 生成页面 {page_num}/{len(pages)}: {output_filename} ({img_width}x{page_height})")
            
            # 移动原文件到备份目录
            shutil.move(input_path, backup_path)
            
            print(f"✓ 成功转换: {txt_file} -> {len(pages)} 张图片")
            success_count += 1
            total_pages += len(pages)
            
        except Exception as e:
            print(f"✗ 转换失败: {txt_file} - 错误: {str(e)}")
            import traceback
            traceback.print_exc()
            fail_count += 1
    
    print(f"\n高清转换完成！成功: {success_count}, 失败: {fail_count}, 总页数: {total_pages}")
    print(f"高清图片保存在: {output_dir}")
    print(f"原文件备份在: {backup_dir}")

# 高清配置参数
CONFIG = {
    'font_size': 20,           # 基础字体大小（实际会放大2倍）
    'scale_factor': 2,         # 高清缩放因子（2倍用于视网膜屏）
    'line_spacing': 1.6,       # 行距倍数
    'margin_percent': 0.08,    # 边距百分比
    'jpeg_quality': 100,       # JPEG质量（100%最高）
    'indent_chars': "　　",     # 段首缩进
    'max_lines_per_page': 50,  # 每页最大行数
}

if __name__ == "__main__":
    # 设置目录路径
    input_directory = "D:/Fanfic/Script/article"
    output_directory = "D:/Fanfic/Script/JPG"
    backup_directory = "D:/Fanfic/Script/BACKUP"
    
    # 检查输入目录是否存在
    if not os.path.exists(input_directory):
        print(f"错误: 输入目录不存在: {input_directory}")
        print("请创建目录或修改脚本中的路径")
    else:
        # 执行高清批量转换
        txt_to_jpg_batch(
            input_dir=input_directory,
            output_dir=output_directory,
            backup_dir=backup_directory,
            font_size=CONFIG['font_size'],
            bg_color=(244, 238, 235),
            text_color=(59, 4, 0),
            max_lines_per_page=CONFIG['max_lines_per_page']
        )