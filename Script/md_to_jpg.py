from PIL import Image, ImageDraw, ImageFont
import textwrap
import os
import shutil
import re
from html import unescape

# 避头尾字符定义（更精确的集合）
FORBIDDEN_START_CHARS = set('，,。.、！!？?：:；;")）〕］】》」』】〗〞〟〉》›»}])')
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

def get_bold_font(font_size=20):
    """
    获取粗体中文字体
    """
    font_paths = [
        "C:/Windows/Fonts/simhei.ttf",      # 黑体
        "C:/Windows/Fonts/msyhbd.ttc",      # 微软雅黑粗体
        "C:/Windows/Fonts/simkai.ttf",      # 楷体
        "/System/Library/Fonts/PingFang.ttc",
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, font_size)
            except:
                continue
    
    # 如果找不到粗体字体，返回普通字体
    return get_chinese_font(font_size)

def get_italic_font(font_size=20):
    """
    获取斜体中文字体（模拟斜体效果）
    """
    try:
        # 尝试获取普通字体，然后应用斜体变换
        font = get_chinese_font(font_size)
        # 返回普通字体，在渲染时进行偏移模拟斜体
        return font
    except:
        return get_chinese_font(font_size)

def parse_markdown(text):
    """
    解析Markdown文本，返回格式化后的行列表
    """
    lines = []
    in_list = False
    list_type = None
    list_counter = 1
    
    # 分割段落
    paragraphs = text.split('\n\n')
    
    for paragraph in paragraphs:
        if not paragraph.strip():
            lines.append(('empty', ''))
            continue
            
        # 处理标题
        if paragraph.startswith('# '):
            lines.append(('h1', paragraph[2:].strip()))
        elif paragraph.startswith('## '):
            lines.append(('h2', paragraph[3:].strip()))
        elif paragraph.startswith('### '):
            lines.append(('h3', paragraph[4:].strip()))
        elif paragraph.startswith('#### '):
            lines.append(('h4', paragraph[5:].strip()))
            
        # 处理水平线
        elif re.match(r'^[-*_]{3,}$', paragraph.strip()):
            lines.append(('hr', ''))
            
        # 处理代码块
        elif paragraph.startswith('    ') or paragraph.startswith('\t'):
            code_lines = paragraph.split('\n')
            for code_line in code_lines:
                lines.append(('code', code_line.strip()))
                
        # 处理列表
        elif paragraph.startswith('- ') or paragraph.startswith('* ') or re.match(r'^\d+\. ', paragraph):
            if not in_list:
                in_list = True
                if re.match(r'^\d+\. ', paragraph):
                    list_type = 'ol'
                else:
                    list_type = 'ul'
            
            # 处理列表项
            list_items = paragraph.split('\n')
            for item in list_items:
                if item.strip():
                    # 移除列表标记
                    if item.startswith('- ') or item.startswith('* '):
                        clean_item = item[2:].strip()
                        lines.append(('li', clean_item, list_type, list_counter))
                    else:
                        clean_item = re.sub(r'^\d+\.\s*', '', item).strip()
                        lines.append(('li', clean_item, list_type, list_counter))
                        list_counter += 1
        else:
            # 处理普通段落中的格式
            formatted_lines = process_inline_formatting(paragraph)
            for line_type, line_text in formatted_lines:
                lines.append((line_type, line_text))
            
        # 结束列表
        if in_list:
            in_list = False
            list_counter = 1
            lines.append(('list_end', ''))
    
    return lines

def process_inline_formatting(text):
    """
    处理行内Markdown格式：粗体、斜体、链接等
    """
    lines = []
    current_text = text
    
    # 先处理代码块，避免干扰其他格式
    code_pattern = r'`(.*?)`'
    current_text = re.sub(code_pattern, lambda m: f"[code]{m.group(1)}[/code]", current_text)
    
    # 处理粗体 (**text** 或 __text__)
    bold_pattern = r'(\*\*|__)(.*?)\1'
    current_text = re.sub(bold_pattern, lambda m: f"[bold]{m.group(2)}[/bold]", current_text)
    
    # 处理斜体 (*text* 或 _text_)
    italic_pattern = r'(\*|_)(.*?)\1'
    current_text = re.sub(italic_pattern, lambda m: f"[italic]{m.group(2)}[/italic]", current_text)
    
    # 处理链接 ([text](url))
    link_pattern = r'\[(.*?)\]\((.*?)\)'
    current_text = re.sub(link_pattern, lambda m: f"[link]{m.group(1)}[/link]", current_text)
    
    # 分割回行
    paragraph_lines = current_text.split('\n')
    for line in paragraph_lines:
        if line.strip():
            # 添加段落缩进（仅对中文段落）
            if any('\u4e00' <= c <= '\u9fff' for c in line):
                lines.append(('p', "　　" + line))
            else:
                lines.append(('p', line))
        else:
            lines.append(('empty', ''))
    
    return lines

def is_forbidden_start_char(char):
    """检查字符是否为避头字符"""
    return char in FORBIDDEN_START_CHARS

def is_forbidden_end_char(char):
    """检查字符是否为避尾字符"""
    return char in FORBIDDEN_END_CHARS

def wrap_text_simple(text, font, max_width):
    """
    简单的文本换行函数，不使用避头尾规则
    """
    if not text:
        return [""]
    
    lines = []
    current_line = ""
    
    for char in text:
        test_line = current_line + char
        if font.getlength(test_line) <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = char
    
    if current_line:
        lines.append(current_line)
    
    return lines

def wrap_text_with_formatting(text, font, max_width):
    """
    包装包含格式标签的文本，遵守中文避头尾规则
    """
    if not text:
        return [""]
    
    # 移除格式标签来计算纯文本长度
    clean_text = re.sub(r'\[.*?\]', '', text)
    if not clean_text.strip():
        return [""]
    
    # 首先进行简单的换行
    lines = wrap_text_simple(text, font, max_width)
    
    # 然后应用避头尾规则进行调整
    adjusted_lines = []
    
    for i, line in enumerate(lines):
        clean_line = re.sub(r'\[.*?\]', '', line)
        
        # 检查行首避头字符
        if clean_line and is_forbidden_start_char(clean_line[0]):
            if i > 0 and adjusted_lines:
                # 尝试将避头字符移到上一行
                prev_line = adjusted_lines[-1]
                prev_clean = re.sub(r'\[.*?\]', '', prev_line)
                
                if prev_clean and not is_forbidden_end_char(prev_clean[-1]):
                    # 将避头字符移到上一行
                    first_char = line[0]
                    adjusted_lines[-1] = prev_line + first_char
                    line = line[1:]
                    clean_line = clean_line[1:]
        
        # 检查行尾避尾字符
        if clean_line and is_forbidden_end_char(clean_line[-1]):
            if i < len(lines) - 1:
                # 尝试将避尾字符移到下一行
                next_line = lines[i + 1]
                next_clean = re.sub(r'\[.*?\]', '', next_line)
                
                if next_clean and not is_forbidden_start_char(next_clean[0]):
                    # 将避尾字符移到下一行
                    last_char = line[-1]
                    line = line[:-1]
                    lines[i + 1] = last_char + next_line
        
        if line:
            adjusted_lines.append(line)
    
    return adjusted_lines

def calculate_text_height(lines, font, bold_font, max_width, line_height):
    """
    计算文本渲染所需的总高度
    """
    total_height = 0
    list_counter = 1
    
    for line_type, *line_content in lines:
        if line_type == 'empty':
            total_height += line_height
            continue
            
        elif line_type == 'hr':
            total_height += line_height
            continue
            
        elif line_type.startswith('h'):
            total_height += int(line_height * 1.5)
            
        elif line_type == 'li':
            list_type = line_content[1] if len(line_content) > 1 else 'ul'
            bullet = "• " if list_type == 'ul' else f"{list_counter}. "
            list_text = bullet + line_content[0]
            
            if list_type == 'ol':
                list_counter += 1
            
            # 计算列表项高度
            wrapped_lines = wrap_text_with_formatting(list_text, font, max_width)
            total_height += len(wrapped_lines) * line_height
                
        elif line_type == 'code':
            total_height += line_height
            
        elif line_type == 'p':
            # 计算段落高度
            wrapped_lines = wrap_text_with_formatting(line_content[0], font, max_width)
            total_height += len(wrapped_lines) * line_height
    
    return total_height

def calculate_optimal_width(font_size, scale_factor=2):
    """
    根据字体大小计算适合手机屏幕的宽度（考虑缩放因子）
    """
    phone_widths = {
        'narrow': 360,
        'standard': 390,
        'wide': 428,
        'max': 480
    }
    
    if font_size <= 20:
        base_width = phone_widths['wide']
    elif font_size <= 24:
        base_width = phone_widths['standard']
    else:
        base_width = phone_widths['narrow']
    
    return int(base_width * scale_factor)

def render_formatted_text(draw, text, x, y, font, bold_font, italic_font, max_width, text_color):
    """
    渲染格式化的文本，支持自动换行
    """
    current_y = y
    
    # 包装文本
    wrapped_lines = wrap_text_with_formatting(text, font, max_width)
    
    for line in wrapped_lines:
        current_x = x
        
        # 解析格式标签
        format_pattern = r'\[(bold|italic|code|link)\](.*?)\[/\1\]'
        segments = []
        last_pos = 0
        
        for match in re.finditer(format_pattern, line):
            if match.start() > last_pos:
                segments.append(('normal', line[last_pos:match.start()]))
            
            segments.append((match.group(1), match.group(2)))
            last_pos = match.end()
        
        if last_pos < len(line):
            segments.append(('normal', line[last_pos:]))
        
        # 渲染分段文本
        for seg_type, seg_text in segments:
            if seg_type == 'normal':
                draw.text((current_x, current_y), seg_text, font=font, fill=text_color)
                current_x += font.getlength(seg_text)
            elif seg_type == 'bold':
                draw.text((current_x, current_y), seg_text, font=bold_font, fill=text_color)
                current_x += bold_font.getlength(seg_text)
            elif seg_type == 'italic':
                # 斜体效果：轻微偏移
                draw.text((current_x + 1, current_y), seg_text, font=italic_font, fill=text_color)
                current_x += italic_font.getlength(seg_text)
            elif seg_type == 'code':
                code_bg_color = (240, 240, 240)
                code_text_color = (100, 100, 100)
                code_width = font.getlength(seg_text) + 8
                code_height = font.size + 4
                
                draw.rectangle([(current_x, current_y), 
                              (current_x + code_width, current_y + code_height)], 
                              fill=code_bg_color, outline=(200, 200, 200))
                draw.text((current_x + 4, current_y), seg_text, font=font, fill=code_text_color)
                current_x += code_width
            elif seg_type == 'link':
                link_color = (0, 0, 255)
                draw.text((current_x, current_y), seg_text, font=font, fill=link_color)
                # 添加下划线
                text_width = font.getlength(seg_text)
                draw.line([(current_x, current_y + font.size + 2), 
                          (current_x + text_width, current_y + font.size + 2)], 
                         fill=link_color, width=1)
                current_x += text_width
        
        current_y += int(font.size * 1.6)
    
    return current_y

def render_markdown_content(draw, lines, font, bold_font, italic_font, x, y, line_height, max_width, text_color):
    """
    渲染Markdown内容到图片
    """
    current_y = y
    list_counter = 1
    
    for line_type, *line_content in lines:
        if line_type == 'empty':
            current_y += line_height
            continue
            
        elif line_type == 'hr':
            draw.line([(x, current_y + line_height//2), 
                      (x + max_width, current_y + line_height//2)], 
                     fill=(200, 200, 200), width=2)
            current_y += line_height
            continue
            
        elif line_type.startswith('h'):
            header_level = int(line_type[1])
            header_font_size = font.size * (1.8 - 0.2 * header_level)
            header_font = get_chinese_font(header_font_size)
            header_bold_font = get_bold_font(header_font_size)
            
            draw.text((x, current_y), line_content[0], font=header_bold_font, fill=text_color)
            current_y += int(line_height * 1.5)
            
        elif line_type == 'li':
            list_type = line_content[1] if len(line_content) > 1 else 'ul'
            item_number = line_content[2] if len(line_content) > 2 else list_counter
            bullet = "• " if list_type == 'ul' else f"{item_number}. "
            list_text = bullet + line_content[0]
            
            if list_type == 'ol':
                list_counter += 1
            
            current_y = render_formatted_text(
                draw, list_text, x, current_y, 
                font, bold_font, italic_font, max_width, text_color
            )
                
        elif line_type == 'code':
            code_bg_color = (240, 240, 240)
            code_text_color = (100, 100, 100)
            code_padding = 4
            
            code_text = line_content[0]
            code_width = font.getlength(code_text) + code_padding * 2
            
            draw.rectangle([(x, current_y), (x + code_width, current_y + line_height)], 
                          fill=code_bg_color, outline=(200, 200, 200))
            draw.text((x + code_padding, current_y), code_text, font=font, fill=code_text_color)
            current_y += line_height
            
        elif line_type == 'p':
            current_y = render_formatted_text(
                draw, line_content[0], x, current_y, 
                font, bold_font, italic_font, max_width, text_color
            )
    
    return current_y

def txt_to_jpg_batch(input_dir, output_dir, backup_dir, font_size=26, bg_color=(255, 255, 255), text_color=(0, 0, 0)):
    """
    批量将TXT文件转换为高清JPG图片（支持Markdown）
    """
    
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(backup_dir, exist_ok=True)
    
    supported_extensions = ['.txt', '.md']
    input_files = [f for f in os.listdir(input_dir) 
                  if any(f.lower().endswith(ext) for ext in supported_extensions)]
    
    if not input_files:
        print(f"在目录 {input_dir} 中没有找到支持的文件")
        return
    
    print(f"找到 {len(input_files)} 个文件，开始高清转换...")
    print(f"使用字体大小: {font_size}px (高清模式)")
    
    success_count = 0
    fail_count = 0
    
    for input_file in input_files:
        input_path = os.path.join(input_dir, input_file)
        output_filename = os.path.splitext(input_file)[0] + '.jpg'
        output_path = os.path.join(output_dir, output_filename)
        backup_path = os.path.join(backup_dir, input_file)
        
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
            
            scale_factor = 2
            hd_font_size = font_size * scale_factor
            
            font = get_chinese_font(hd_font_size)
            bold_font = get_bold_font(hd_font_size)
            italic_font = get_italic_font(hd_font_size)
            
            img_width = calculate_optimal_width(font_size, scale_factor)
            margin = int(img_width * 0.08)
            usable_width = img_width - 2 * margin
            line_height = int(hd_font_size * 1.6)
            
            print(f"处理文件: {input_file}, 图片宽度: {img_width}px, 高清模式: {scale_factor}x")
            
            # 解析Markdown
            if input_file.lower().endswith('.md') or any(c in text for c in '#*_-`[]()'):
                print(f"  检测到Markdown格式，进行解析...")
                parsed_lines = parse_markdown(text)
                
                # 准确计算所需高度
                content_height = calculate_text_height(parsed_lines, font, bold_font, usable_width, line_height)
                img_height = content_height + 80  # 上下边距
                
                # 确保最小高度
                min_height = 1000
                if img_height < min_height:
                    img_height = min_height
                
                print(f"  计算高度: {img_height}px (内容高度: {content_height}px)")
                
                image = Image.new('RGB', (img_width, img_height), color=bg_color)
                draw = ImageDraw.Draw(image)
                
                final_y = render_markdown_content(
                    draw, parsed_lines, font, bold_font, italic_font, 
                    margin, 40, line_height, usable_width, text_color
                )
                
                # 如果实际渲染高度超过预估高度，重新调整图片大小
                if final_y + 40 > img_height:
                    new_height = final_y + 40
                    print(f"  调整图片高度: {img_height}px -> {new_height}px")
                    new_image = Image.new('RGB', (img_width, new_height), color=bg_color)
                    new_image.paste(image, (0, 0))
                    image = new_image
                    draw = ImageDraw.Draw(image)
                    # 重新渲染到最后的位置
                    render_markdown_content(
                        draw, parsed_lines, font, bold_font, italic_font, 
                        margin, 40, line_height, usable_width, text_color
                    )
                
            else:
                # 普通文本处理
                is_chinese = any('\u4e00' <= c <= '\u9fff' for c in text)
                
                # 计算普通文本高度
                avg_char_width = font.getlength("中")
                chars_per_line = max(1, int(usable_width / avg_char_width))
                lines_count = len(text) // chars_per_line + 2
                img_height = lines_count * line_height + 80
                
                min_height = 800
                if img_height < min_height:
                    img_height = min_height
                
                image = Image.new('RGB', (img_width, img_height), color=bg_color)
                draw = ImageDraw.Draw(image)
                
                # 简单换行渲染
                y_pos = 40
                current_line = ""
                
                for char in text:
                    test_line = current_line + char
                    if font.getlength(test_line) <= usable_width:
                        current_line = test_line
                    else:
                        if current_line:
                            draw.text((margin, y_pos), current_line, font=font, fill=text_color)
                            y_pos += line_height
                        current_line = char
                
                if current_line:
                    draw.text((margin, y_pos), current_line, font=font, fill=text_color)
            
            image.save(
                output_path, 
                'JPEG', 
                quality=95,  # 稍微降低质量以减少文件大小
                optimize=True,
                subsampling=0,
                qtables='web_high'
            )
            
            shutil.move(input_path, backup_path)
            
            print(f"✓ 成功转换: {input_file} -> {output_filename} ({image.width}x{image.height}, 质量:95%)")
            success_count += 1
            
        except Exception as e:
            print(f"✗ 转换失败: {input_file} - 错误: {str(e)}")
            import traceback
            traceback.print_exc()
            fail_count += 1
    
    print(f"\n高清转换完成！成功: {success_count}, 失败: {fail_count}")
    print(f"高清图片保存在: {output_dir}")
    print(f"原文件备份在: {backup_dir}")

# 高清配置参数
CONFIG = {
    'font_size': 20,
    'scale_factor': 2,
    'line_spacing': 1.6,
    'margin_percent': 0.08,
    'jpeg_quality': 95,  # 调整为95%
    'indent_chars': "　　",
}

if __name__ == "__main__":
    input_directory = "D:/Fanfic/Script/article"
    output_directory = "D:/Fanfic/Script/JPG"
    backup_directory = "D:/Fanfic/Script/BACKUP"
    
    if not os.path.exists(input_directory):
        print(f"错误: 输入目录不存在: {input_directory}")
        print("请创建目录或修改脚本中的路径")
    else:
        txt_to_jpg_batch(
            input_dir=input_directory,
            output_dir=output_directory,
            backup_dir=backup_directory,
            font_size=CONFIG['font_size'],
            bg_color=(244, 238, 235),
            text_color=(59, 4, 0)
        )