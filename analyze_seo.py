#!/usr/bin/env python3
"""
SEO 分析工具

这个脚本用于分析网站内容的SEO状况，检查常见的SEO问题，
并生成报告，帮助改进网站的搜索引擎优化和大模型爬取效果。
"""

import os
import re
import sys
import yaml
import argparse
import csv
from pathlib import Path
from collections import defaultdict, Counter

# SEO 检查项
SEO_CHECKS = {
    "missing_title": "缺少标题",
    "missing_description": "缺少描述",
    "short_description": "描述过短 (< 50 字符)",
    "long_description": "描述过长 (> 160 字符)",
    "missing_keywords": "缺少关键词",
    "few_keywords": "关键词过少 (< 3 个)",
    "many_keywords": "关键词过多 (> 10 个)",
    "missing_structured_data": "缺少结构化数据",
    "missing_dates": "缺少日期信息",
    "duplicate_title": "标题重复",
    "duplicate_description": "描述重复",
    "missing_alt_text": "图片缺少 alt 文本",
    "no_internal_links": "没有内部链接",
    "few_internal_links": "内部链接过少 (< 2 个)",
    "no_headings": "没有小标题 (h2, h3)",
    "long_paragraphs": "段落过长 (> 300 字符)",
    "low_content_density": "内容密度低 (< 200 字)",
}

class SEOAnalyzer:
    def __init__(self):
        self.issues = defaultdict(list)
        self.stats = defaultdict(int)
        self.titles = set()
        self.descriptions = set()
        self.all_keywords = Counter()
    
    def analyze_file(self, file_path):
        """分析单个文件的SEO状况"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取前置元数据
        frontmatter_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
        if not frontmatter_match:
            self.issues[file_path].append("missing_frontmatter")
            self.stats["missing_frontmatter"] += 1
            return
        
        try:
            frontmatter = yaml.safe_load(frontmatter_match.group(1))
            if frontmatter is None:
                frontmatter = {}
            content_without_frontmatter = content[frontmatter_match.end():]
        except yaml.YAMLError:
            self.issues[file_path].append("invalid_frontmatter")
            self.stats["invalid_frontmatter"] += 1
            return
        
        # 检查标题
        if not frontmatter.get('title'):
            self.issues[file_path].append("missing_title")
            self.stats["missing_title"] += 1
        else:
            title = frontmatter['title']
            if title in self.titles:
                self.issues[file_path].append("duplicate_title")
                self.stats["duplicate_title"] += 1
            self.titles.add(title)
        
        # 检查描述
        if not frontmatter.get('description'):
            self.issues[file_path].append("missing_description")
            self.stats["missing_description"] += 1
        else:
            description = frontmatter['description']
            if len(description) < 50:
                self.issues[file_path].append("short_description")
                self.stats["short_description"] += 1
            elif len(description) > 160:
                self.issues[file_path].append("long_description")
                self.stats["long_description"] += 1
            
            if description in self.descriptions:
                self.issues[file_path].append("duplicate_description")
                self.stats["duplicate_description"] += 1
            self.descriptions.add(description)
        
        # 检查关键词
        if not frontmatter.get('keywords'):
            self.issues[file_path].append("missing_keywords")
            self.stats["missing_keywords"] += 1
        else:
            keywords = [k.strip() for k in frontmatter['keywords'].split(',')]
            if len(keywords) < 3:
                self.issues[file_path].append("few_keywords")
                self.stats["few_keywords"] += 1
            elif len(keywords) > 10:
                self.issues[file_path].append("many_keywords")
                self.stats["many_keywords"] += 1
            
            # 统计关键词频率
            for keyword in keywords:
                self.all_keywords[keyword] += 1
        
        # 检查结构化数据
        if not frontmatter.get('structuredData'):
            self.issues[file_path].append("missing_structured_data")
            self.stats["missing_structured_data"] += 1
        
        # 检查日期信息
        if not frontmatter.get('datePublished') or not frontmatter.get('dateModified'):
            self.issues[file_path].append("missing_dates")
            self.stats["missing_dates"] += 1
        
        # 检查内容
        # 图片 alt 文本
        img_tags = re.findall(r'!\[(.*?)\]\((.*?)\)', content_without_frontmatter)
        for alt_text, _ in img_tags:
            if not alt_text:
                self.issues[file_path].append("missing_alt_text")
                self.stats["missing_alt_text"] += 1
                break
        
        # 内部链接
        internal_links = re.findall(r'\[(?!.*?http)[^\]]+\]\([^)]+\)', content_without_frontmatter)
        if not internal_links:
            self.issues[file_path].append("no_internal_links")
            self.stats["no_internal_links"] += 1
        elif len(internal_links) < 2:
            self.issues[file_path].append("few_internal_links")
            self.stats["few_internal_links"] += 1
        
        # 标题结构
        headings = re.findall(r'^##+ (.+)$', content_without_frontmatter, re.MULTILINE)
        if not headings:
            self.issues[file_path].append("no_headings")
            self.stats["no_headings"] += 1
        
        # 段落长度
        paragraphs = re.split(r'\n\s*\n', content_without_frontmatter)
        for p in paragraphs:
            if len(p.strip()) > 300 and not p.strip().startswith('#') and not p.strip().startswith('!'):
                self.issues[file_path].append("long_paragraphs")
                self.stats["long_paragraphs"] += 1
                break
        
        # 内容密度
        text_content = re.sub(r'#+ |\*\*|\*|_|`|!\[.*?\]\(.*?\)|\[.*?\]\(.*?\)', '', content_without_frontmatter)
        if len(text_content.strip()) < 200:
            self.issues[file_path].append("low_content_density")
            self.stats["low_content_density"] += 1
    
    def analyze_directory(self, directory):
        """分析目录中的所有Markdown文件"""
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    self.analyze_file(file_path)
    
    def generate_report(self, output_dir):
        """生成SEO分析报告"""
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成总体统计报告
        with open(os.path.join(output_dir, 'seo_stats.csv'), 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['问题类型', '数量', '描述'])
            for issue_type, count in sorted(self.stats.items(), key=lambda x: x[1], reverse=True):
                writer.writerow([
                    issue_type, 
                    count, 
                    SEO_CHECKS.get(issue_type, issue_type)
                ])
        
        # 生成文件问题详情报告
        with open(os.path.join(output_dir, 'seo_issues.csv'), 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['文件路径', '问题类型', '描述'])
            for file_path, issues in sorted(self.issues.items()):
                for issue in issues:
                    writer.writerow([
                        file_path, 
                        issue, 
                        SEO_CHECKS.get(issue, issue)
                    ])
        
        # 生成关键词统计报告
        with open(os.path.join(output_dir, 'keywords_stats.csv'), 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['关键词', '出现次数'])
            for keyword, count in self.all_keywords.most_common():
                writer.writerow([keyword, count])
        
        print(f"SEO分析报告已生成到目录: {output_dir}")
        print(f"共发现 {sum(self.stats.values())} 个SEO问题，涉及 {len(self.issues)} 个文件")

def main():
    parser = argparse.ArgumentParser(description='分析网站内容的SEO状况')
    parser.add_argument('path', help='要分析的文件或目录路径')
    parser.add_argument('--output', default='seo_reports', help='输出报告的目录，默认为 seo_reports')
    args = parser.parse_args()
    
    path = Path(args.path)
    if not path.exists():
        print(f"错误: 路径不存在: {path}")
        return 1
    
    analyzer = SEOAnalyzer()
    
    if path.is_file():
        if path.suffix != '.md':
            print(f"错误: 不是Markdown文件: {path}")
            return 1
        analyzer.analyze_file(str(path))
    else:
        analyzer.analyze_directory(str(path))
    
    analyzer.generate_report(args.output)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
