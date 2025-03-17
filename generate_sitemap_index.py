#!/usr/bin/env python3
"""
生成多语言站点地图索引文件

这个脚本用于生成一个站点地图索引文件（sitemap index），
包含指向各个语言版本站点地图的链接。
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

SITEMAP_INDEX_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{sitemaps}
</sitemapindex>
"""

SITEMAP_ENTRY_TEMPLATE = """  <sitemap>
    <loc>{url}</loc>
    <lastmod>{lastmod}</lastmod>
  </sitemap>
"""

def generate_sitemap_index(base_url, languages, output_path):
    """生成站点地图索引文件"""
    # 确保基础URL以斜杠结尾
    if not base_url.endswith('/'):
        base_url += '/'
    
    # 获取当前日期作为lastmod
    lastmod = datetime.now().strftime("%Y-%m-%d")
    
    # 生成各语言站点地图条目
    sitemap_entries = []
    
    # 添加默认语言站点地图
    sitemap_entries.append(SITEMAP_ENTRY_TEMPLATE.format(
        url=f"{base_url}sitemap.xml",
        lastmod=lastmod
    ))
    
    # 添加各语言站点地图
    for lang in languages:
        sitemap_entries.append(SITEMAP_ENTRY_TEMPLATE.format(
            url=f"{base_url}{lang}/sitemap.xml",
            lastmod=lastmod
        ))
    
    # 组合站点地图索引内容
    sitemap_index_content = SITEMAP_INDEX_TEMPLATE.format(
        sitemaps="".join(sitemap_entries)
    )
    
    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(sitemap_index_content)
    
    print(f"站点地图索引文件已生成: {output_path}")
    print(f"包含 {len(sitemap_entries)} 个站点地图条目")

def main():
    parser = argparse.ArgumentParser(description='生成多语言站点地图索引文件')
    parser.add_argument('--base-url', required=True, help='网站的基础URL，例如 https://example.com/')
    parser.add_argument('--languages', nargs='+', default=['en', 'zh-Hans', 'zh-Hant', 'ja', 'ko'], 
                        help='支持的语言列表，默认为 en zh-Hans zh-Hant ja ko')
    parser.add_argument('--output', default='sitemap-index.xml', help='输出文件路径，默认为 sitemap-index.xml')
    args = parser.parse_args()
    
    generate_sitemap_index(args.base_url, args.languages, args.output)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
