#!/usr/bin/env python3
"""
GPT-4o 增强模块

这个模块使用 GPT-4o 模型来增强 SEO 优化工具的功能，
提供更智能的内容分析、元数据生成和多语言支持。
"""

import os
import json
import urllib.request
import ssl
import time
import re
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# 导入配置
from config import SITE_INFO, STRUCTURED_DATA, DIRECTORY_KEYWORDS

# GPT-4o API 配置
GPT4O_CONFIG = {
    "url": "https://cantian-openai.openai.azure.com/openai/deployments/gpt-4o/v1/completions",
    "api_key": os.environ.get("GPT4O_API_KEY", ""),  # 从环境变量获取 API 密钥
    "max_tokens": 2000,
    "temperature": 0.7,
    "top_p": 0.95,
    "frequency_penalty": 0,
    "presence_penalty": 0,
    "stop": None
}

def allow_self_signed_https(allowed):
    """允许自签名 HTTPS 证书"""
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

class GPT4OEnhancer:
    """GPT-4o 增强器类，提供各种 SEO 增强功能"""
    
    def __init__(self, api_key=None):
        """初始化 GPT-4o 增强器"""
        allow_self_signed_https(True)
        self.api_key = api_key or GPT4O_CONFIG["api_key"]
        if not self.api_key:
            raise ValueError("必须提供 GPT-4o API 密钥，可以通过环境变量 GPT4O_API_KEY 设置")
        
        self.url = GPT4O_CONFIG["url"]
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
    
    def call_gpt4o(self, prompt, max_tokens=None, temperature=None):
        """调用 GPT-4o API"""
        data = {
            "prompt": prompt,
            "max_tokens": max_tokens or GPT4O_CONFIG["max_tokens"],
            "temperature": temperature or GPT4O_CONFIG["temperature"],
            "top_p": GPT4O_CONFIG["top_p"],
            "frequency_penalty": GPT4O_CONFIG["frequency_penalty"],
            "presence_penalty": GPT4O_CONFIG["presence_penalty"],
            "stop": GPT4O_CONFIG["stop"]
        }
        
        body = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(self.url, body, self.headers)
        
        try:
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode("utf-8"))
            return result.get("choices", [{}])[0].get("text", "").strip()
        except urllib.error.HTTPError as error:
            print(f"API 请求失败，状态码: {error.code}")
            print(error.info())
            print(error.read().decode("utf8", 'ignore'))
            return None
    
    def generate_meta_description(self, content, target_length=150):
        """生成优化的元描述"""
        prompt = f"""
        请为以下内容生成一个吸引人的 SEO 元描述，长度在 {target_length} 字符左右。
        描述应该包含关键词，并且能够吸引用户点击。
        
        内容:
        {content[:2000]}  # 限制内容长度，避免 token 过多
        
        只返回元描述文本，不要包含任何其他解释或格式。
        """
        
        return self.call_gpt4o(prompt, max_tokens=200, temperature=0.7)
    
    def optimize_keywords(self, content, directory_name=None, existing_keywords=None):
        """优化关键词列表"""
        base_keywords = DIRECTORY_KEYWORDS.get(directory_name, ["命理", "八字", "中国传统文化"]) if directory_name else []
        existing_kw_str = ", ".join(existing_keywords) if existing_keywords else ""
        
        prompt = f"""
        请为以下内容生成 5-8 个优化的 SEO 关键词，关键词应该与内容高度相关，并且有搜索量。
        
        内容:
        {content[:2000]}  # 限制内容长度，避免 token 过多
        
        基础关键词（如果适用，请包含这些）: {", ".join(base_keywords)}
        现有关键词（如果适用，请考虑这些）: {existing_kw_str}
        
        只返回关键词列表，用逗号分隔，不要包含任何其他解释或格式。
        """
        
        result = self.call_gpt4o(prompt, max_tokens=200, temperature=0.7)
        if result:
            # 清理结果，确保只有关键词列表
            result = re.sub(r'^[^a-zA-Z0-9\u4e00-\u9fff,]+', '', result)
            result = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff,]+$', '', result)
            return result
        return existing_kw_str
    
    def generate_structured_data(self, content, metadata, file_path):
        """生成优化的结构化数据"""
        file_name = os.path.basename(file_path)
        dir_name = os.path.basename(os.path.dirname(file_path))
        
        # 确定结构化数据类型
        is_glossary_term = dir_name in ["十神", "天干", "地支", "神煞", "星运_十二长生_", "其他名词解释"]
        if is_glossary_term and not file_name.endswith("介绍.md"):
            data_type = "DefinedTerm"
        else:
            data_type = "Article"
        
        prompt = f"""
        请为以下内容生成优化的 JSON-LD 结构化数据，类型为 {data_type}。
        
        内容:
        {content[:1500]}  # 限制内容长度，避免 token 过多
        
        元数据:
        标题: {metadata.get('title', '未知标题')}
        描述: {metadata.get('description', '未知描述')}
        关键词: {metadata.get('keywords', '')}
        
        文件路径: {file_path}
        
        只返回 JSON 格式的结构化数据，不要包含任何其他解释或格式。
        确保 JSON 格式正确，可以被解析。
        """
        
        result = self.call_gpt4o(prompt, max_tokens=1000, temperature=0.3)
        if result:
            # 尝试解析 JSON 结果
            try:
                # 提取 JSON 部分
                json_match = re.search(r'```json\s*(.*?)\s*```', result, re.DOTALL)
                if json_match:
                    result = json_match.group(1)
                
                # 尝试解析 JSON
                structured_data = json.loads(result)
                return structured_data
            except json.JSONDecodeError:
                print(f"无法解析生成的结构化数据 JSON: {result}")
                return None
        return None
    
    def analyze_content_for_seo(self, content, file_path):
        """分析内容并提供 SEO 改进建议"""
        prompt = f"""
        请分析以下内容的 SEO 状况，并提供具体的改进建议。
        关注以下方面：
        1. 内容质量和相关性
        2. 关键词使用和密度
        3. 标题和小标题结构
        4. 内部链接
        5. 内容长度和深度
        6. 可读性和用户体验
        
        内容:
        {content[:3000]}  # 限制内容长度，避免 token 过多
        
        文件路径: {file_path}
        
        请提供具体的、可操作的建议，以改进内容的 SEO 表现。
        """
        
        return self.call_gpt4o(prompt, max_tokens=1500, temperature=0.5)
    
    def translate_content(self, content, source_lang, target_lang):
        """翻译内容到目标语言，保持格式和结构"""
        prompt = f"""
        请将以下{source_lang}内容翻译成{target_lang}，保持原始的 Markdown 格式和结构。
        确保翻译准确、自然，并且适合 SEO。
        
        内容:
        {content[:4000]}  # 限制内容长度，避免 token 过多
        
        只返回翻译后的内容，保持原始格式，不要包含任何其他解释。
        """
        
        return self.call_gpt4o(prompt, max_tokens=4000, temperature=0.3)
    
    def enhance_frontmatter(self, file_path):
        """增强 Markdown 文件的前置元数据"""
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
        
        # 生成优化的元描述
        if not frontmatter.get('description') or len(frontmatter.get('description', '')) < 50:
            description = self.generate_meta_description(content_without_frontmatter)
            if description:
                frontmatter['description'] = description
        
        # 优化关键词
        dir_name = os.path.basename(os.path.dirname(file_path))
        keywords = self.optimize_keywords(
            content_without_frontmatter,
            directory_name=dir_name,
            existing_keywords=frontmatter.get('keywords', '').split(',') if frontmatter.get('keywords') else None
        )
        if keywords:
            frontmatter['keywords'] = keywords
        
        # 确保有日期信息
        if not frontmatter.get('datePublished'):
            frontmatter['datePublished'] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        frontmatter['dateModified'] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # 添加作者信息
        if not frontmatter.get('author'):
            frontmatter['author'] = SITE_INFO.get('author', 'Cantian AI Team')
        
        # 生成结构化数据配置
        if not frontmatter.get('structuredData'):
            frontmatter['structuredData'] = {}
        
        structured_data = self.generate_structured_data(content_without_frontmatter, frontmatter, file_path)
        if structured_data:
            # 只提取类型信息到前置元数据，完整结构化数据由插件生成
            frontmatter['structuredData']['type'] = structured_data.get('@type', 'Article')
        
        # 生成新的前置元数据YAML
        new_frontmatter_yaml = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False)
        
        # 组合新的文件内容
        new_content = f"---\n{new_frontmatter_yaml}---\n{content_without_frontmatter}"
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"已增强: {file_path}")
        return True
    
    def batch_enhance_directory(self, directory, preview=False):
        """批量增强目录中的所有 Markdown 文件"""
        success_count = 0
        error_count = 0
        
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    print(f"处理: {file_path}")
                    
                    if preview:
                        # 预览模式，只分析不修改
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        analysis = self.analyze_content_for_seo(content, file_path)
                        print(f"\n{'='*50}\n文件: {file_path}\n{'='*50}")
                        print(f"SEO 分析:\n{analysis}")
                    else:
                        # 实际增强模式
                        try:
                            if self.enhance_frontmatter(file_path):
                                success_count += 1
                            else:
                                error_count += 1
                        except Exception as e:
                            print(f"错误: 处理 {file_path} 时出错: {e}")
                            error_count += 1
        
        if not preview:
            print(f"\n处理完成: 成功 {success_count} 个文件, 失败 {error_count} 个文件")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='使用 GPT-4o 增强 SEO 优化')
    parser.add_argument('path', help='要处理的文件或目录路径')
    parser.add_argument('--api-key', help='GPT-4o API 密钥，如果不提供则使用环境变量 GPT4O_API_KEY')
    parser.add_argument('--preview', action='store_true', help='预览模式，只分析不修改文件')
    parser.add_argument('--translate', help='翻译内容到指定语言，例如 en, ja, ko, zh-Hans, zh-Hant')
    parser.add_argument('--source-lang', default='zh-Hans', help='源语言，默认为 zh-Hans')
    args = parser.parse_args()
    
    try:
        enhancer = GPT4OEnhancer(api_key=args.api_key)
        
        path = Path(args.path)
        if not path.exists():
            print(f"错误: 路径不存在: {path}")
            return 1
        
        if args.translate:
            # 翻译模式
            if path.is_file():
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                translated = enhancer.translate_content(content, args.source_lang, args.translate)
                output_path = f"{path.stem}_{args.translate}{path.suffix}"
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(translated)
                print(f"翻译完成: {output_path}")
            else:
                print("错误: 翻译模式只支持单个文件，不支持目录")
                return 1
        else:
            # 增强模式
            if path.is_file():
                if path.suffix != '.md':
                    print(f"错误: 不是 Markdown 文件: {path}")
                    return 1
                
                if args.preview:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    analysis = enhancer.analyze_content_for_seo(content, str(path))
                    print(f"SEO 分析:\n{analysis}")
                else:
                    enhancer.enhance_frontmatter(str(path))
            else:
                enhancer.batch_enhance_directory(str(path), preview=args.preview)
        
        return 0
    except Exception as e:
        print(f"错误: {e}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
