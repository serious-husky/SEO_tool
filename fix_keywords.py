#!/usr/bin/env python3
"""
修复关键词格式脚本

这个脚本用于修复 Markdown 文件中的关键词格式，
将字符串格式的关键词转换为数组格式，以符合 Docusaurus 的要求。
"""

import os
import re
import yaml
from pathlib import Path

def fix_keywords_in_file(file_path):
    """修复单个文件中的关键词格式"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取前置元数据
    frontmatter_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if not frontmatter_match:
        print(f"警告: 文件 {file_path} 没有前置元数据")
        return False
    
    try:
        frontmatter = yaml.safe_load(frontmatter_match.group(1))
        if frontmatter is None:
            frontmatter = {}
        content_without_frontmatter = content[frontmatter_match.end():]
    except yaml.YAMLError as e:
        print(f"警告: 解析 {file_path} 的前置元数据时出错: {e}")
        return False
    
    # 检查关键词格式
    if 'keywords' in frontmatter:
        if isinstance(frontmatter['keywords'], str):
            # 将字符串格式的关键词转换为数组
            frontmatter['keywords'] = [k.strip() for k in frontmatter['keywords'].split(',')]
            print(f"已修复: {file_path}")
        elif not isinstance(frontmatter['keywords'], list):
            # 如果不是字符串也不是列表，强制转换为列表
            frontmatter['keywords'] = [str(frontmatter['keywords'])]
            print(f"已修复: {file_path}")
        else:
            # 已经是列表格式，不需要修复
            return True
    else:
        # 没有关键词字段，添加一个空列表
        frontmatter['keywords'] = []
        print(f"已添加空关键词: {file_path}")
    
    # 生成新的前置元数据YAML
    new_frontmatter_yaml = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False)
    
    # 组合新的文件内容
    new_content = f"---\n{new_frontmatter_yaml}---\n{content_without_frontmatter}"
    
    # 写入文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

def fix_keywords_in_directory(directory):
    """递归修复目录中所有 Markdown 文件的关键词格式"""
    success_count = 0
    error_count = 0
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                try:
                    if fix_keywords_in_file(file_path):
                        success_count += 1
                    else:
                        error_count += 1
                except Exception as e:
                    print(f"错误: 处理 {file_path} 时出错: {e}")
                    error_count += 1
    
    print(f"\n处理完成: 成功 {success_count} 个文件, 失败 {error_count} 个文件")
    return success_count, error_count

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='修复 Markdown 文件中的关键词格式')
    parser.add_argument('path', help='要处理的文件或目录路径')
    args = parser.parse_args()
    
    path = Path(args.path)
    if not path.exists():
        print(f"错误: 路径不存在: {path}")
        return 1
    
    if path.is_file():
        if path.suffix != '.md':
            print(f"错误: 不是 Markdown 文件: {path}")
            return 1
        
        try:
            fix_keywords_in_file(str(path))
            print(f"处理完成: {path}")
        except Exception as e:
            print(f"错误: {e}")
            return 1
    else:
        fix_keywords_in_directory(str(path))
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
