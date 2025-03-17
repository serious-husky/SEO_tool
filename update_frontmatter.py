#!/usr/bin/env python3
"""
SEO 前置元数据更新工具

这个脚本用于批量更新 Markdown 文件的前置元数据（frontmatter），
添加 SEO 相关的元数据字段，如描述、关键词、结构化数据等。
"""

import os
import re
import sys
import yaml
import argparse
from datetime import datetime
from pathlib import Path

# 默认的前置元数据模板
DEFAULT_FRONTMATTER = {
    "description": "",
    "keywords": "",
    "author": "Cantian AI Team",
    "datePublished": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
    "dateModified": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
    "structuredData": {
        "type": "Article",
    }
}

# 根据目录名称自动生成关键词
DIRECTORY_KEYWORDS = {
    "十神": ["十神", "命理", "八字", "中国传统文化", "命理学"],
    "天干": ["天干", "命理", "八字", "中国传统文化", "命理学", "干支"],
    "地支": ["地支", "命理", "八字", "中国传统文化", "命理学", "干支"],
    "神煞": ["神煞", "命理", "八字", "中国传统文化", "命理学", "吉凶"],
    "星运_十二长生_": ["十二长生", "星运", "命理", "八字", "中国传统文化", "命理学"],
    "其他名词解释": ["命理", "八字", "中国传统文化", "命理学", "术语"],
}

# 根据文件名自动生成结构化数据类型
def get_structured_data_type(file_path):
    """根据文件路径确定结构化数据类型"""
    dir_name = os.path.basename(os.path.dirname(file_path))
    file_name = os.path.basename(file_path)
    
    # 检查是否为术语定义页面
    if dir_name in ["十神", "天干", "地支", "神煞", "星运_十二长生_", "其他名词解释"]:
        if not file_name.endswith("介绍.md"):
            return "DefinedTerm"
    
    # 默认为文章类型
    return "Article"

# 从文件内容中提取关键词
def extract_keywords_from_content(content, max_keywords=5):
    """从内容中提取可能的关键词"""
    # 简单实现：提取所有中文词组（2-5个字符）
    chinese_words = re.findall(r'[\u4e00-\u9fff]{2,5}', content)
    # 按频率排序
    word_freq = {}
    for word in chinese_words:
        if word in word_freq:
            word_freq[word] += 1
        else:
            word_freq[word] = 1
    
    # 取频率最高的几个词
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in sorted_words[:max_keywords]]

# 从文件内容中提取描述
def generate_description(content, max_length=150):
    """从内容中生成描述"""
    # 移除Markdown标记
    plain_text = re.sub(r'#+ ', '', content)
    plain_text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', plain_text)
    plain_text = re.sub(r'[*_]{1,2}([^*_]+)[*_]{1,2}', r'\1', plain_text)
    
    # 提取第一段非空文本
    paragraphs = plain_text.split('\n\n')
    for p in paragraphs:
        p = p.strip()
        if p and not p.startswith('---'):
            # 截断到指定长度
            if len(p) > max_length:
                return p[:max_length] + '...'
            return p
    
    return ""

def update_frontmatter(file_path, args):
    """更新指定文件的前置元数据"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已有前置元数据
    frontmatter_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    existing_frontmatter = {}
    
    if frontmatter_match:
        try:
            existing_frontmatter = yaml.safe_load(frontmatter_match.group(1))
            if existing_frontmatter is None:
                existing_frontmatter = {}
            content_without_frontmatter = content[frontmatter_match.end():]
        except yaml.YAMLError as e:
            print(f"警告: 解析 {file_path} 的前置元数据时出错: {e}")
            return False
    else:
        content_without_frontmatter = content
    
    # 准备新的前置元数据
    new_frontmatter = DEFAULT_FRONTMATTER.copy()
    
    # 保留现有的基本字段
    for key in ['title', 'sidebar_label', 'sidebar_position', 'hide_title', 'hide_table_of_contents']:
        if key in existing_frontmatter:
            new_frontmatter[key] = existing_frontmatter[key]
    
    # 如果没有标题，尝试从内容中提取
    if 'title' not in new_frontmatter:
        title_match = re.search(r'^# (.+)$', content_without_frontmatter, re.MULTILINE)
        if title_match:
            new_frontmatter['title'] = title_match.group(1)
    
    # 如果没有侧边栏标签，使用标题
    if 'sidebar_label' not in new_frontmatter and 'title' in new_frontmatter:
        new_frontmatter['sidebar_label'] = new_frontmatter['title']
    
    # 生成描述（如果不存在）
    if not existing_frontmatter.get('description'):
        new_frontmatter['description'] = generate_description(content_without_frontmatter)
    else:
        new_frontmatter['description'] = existing_frontmatter['description']
    
    # 生成关键词（如果不存在）
    if not existing_frontmatter.get('keywords'):
        # 从目录名获取基础关键词
        dir_name = os.path.basename(os.path.dirname(file_path))
        base_keywords = DIRECTORY_KEYWORDS.get(dir_name, ["命理", "八字", "中国传统文化"])
        
        # 从内容中提取额外关键词
        content_keywords = extract_keywords_from_content(content_without_frontmatter)
        
        # 合并关键词并去重
        all_keywords = base_keywords + content_keywords
        unique_keywords = []
        for kw in all_keywords:
            if kw not in unique_keywords:
                unique_keywords.append(kw)
        
        new_frontmatter['keywords'] = ", ".join(unique_keywords[:10])  # 最多10个关键词
    else:
        new_frontmatter['keywords'] = existing_frontmatter['keywords']
    
    # 设置结构化数据类型
    if not existing_frontmatter.get('structuredData', {}).get('type'):
        new_frontmatter['structuredData']['type'] = get_structured_data_type(file_path)
    else:
        new_frontmatter['structuredData']['type'] = existing_frontmatter.get('structuredData', {}).get('type')
    
    # 保留现有的日期信息
    if existing_frontmatter.get('datePublished'):
        new_frontmatter['datePublished'] = existing_frontmatter['datePublished']
    if existing_frontmatter.get('dateModified'):
        new_frontmatter['dateModified'] = existing_frontmatter['dateModified']
    else:
        # 如果没有修改日期，使用当前日期
        new_frontmatter['dateModified'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # 生成新的前置元数据YAML
    new_frontmatter_yaml = yaml.dump(new_frontmatter, allow_unicode=True, sort_keys=False)
    
    # 组合新的文件内容
    new_content = f"---\n{new_frontmatter_yaml}---\n{content_without_frontmatter}"
    
    # 如果是预览模式，只打印结果
    if args.preview:
        print(f"\n{'='*50}\n文件: {file_path}\n{'='*50}")
        print(f"新的前置元数据:\n{new_frontmatter_yaml}")
        return True
    
    # 写入文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"已更新: {file_path}")
    return True

def process_directory(directory, args):
    """处理目录中的所有Markdown文件"""
    success_count = 0
    error_count = 0
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                try:
                    if update_frontmatter(file_path, args):
                        success_count += 1
                except Exception as e:
                    print(f"错误: 处理 {file_path} 时出错: {e}")
                    error_count += 1
    
    print(f"\n处理完成: 成功 {success_count} 个文件, 失败 {error_count} 个文件")

def main():
    parser = argparse.ArgumentParser(description='更新Markdown文件的SEO前置元数据')
    parser.add_argument('path', help='要处理的文件或目录路径')
    parser.add_argument('--preview', action='store_true', help='预览模式，不实际修改文件')
    args = parser.parse_args()
    
    path = Path(args.path)
    if not path.exists():
        print(f"错误: 路径不存在: {path}")
        return 1
    
    if path.is_file():
        if path.suffix != '.md':
            print(f"错误: 不是Markdown文件: {path}")
            return 1
        update_frontmatter(str(path), args)
    else:
        process_directory(str(path), args)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
