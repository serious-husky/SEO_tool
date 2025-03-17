#!/usr/bin/env python3
"""
GPT-4o 增强器示例用法

这个脚本演示了如何使用 GPT-4o 增强器来优化内容的 SEO。
"""

import os
import sys
from dotenv import load_dotenv
from gpt4o_enhancer import GPT4OEnhancer

# 加载环境变量
load_dotenv()

# 示例内容
SAMPLE_CONTENT = """
# 十神介绍

十神是传统中国命理学中用于预测人生吉凶的术语，基于天干地支和五行相生相克理论，在八字命理分析中起核心作用。

十神包括：比肩、劫财、食神、伤官、偏财、正财、七杀、正官、偏印、正印。

在命理学中，日干代表"自己"，而其他天干地支则通过五行相生相克关系定义了十神。十神的分类基于这些相互作用，包括以下五种关系：
- 生我者：正印、偏印
- 我生者：食神、伤官
- 克我者：正官、七杀
- 我克者：正财、偏财
- 同我者：比肩、劫财

每个十神对应不同的象征意义，反映了命主的性格特质和命运走向。理解和应用十神是八字命理分析中最基本也是最关键的部分之一。
"""

def main():
    """主函数"""
    # 检查 API 密钥
    api_key = os.environ.get("GPT4O_API_KEY")
    if not api_key:
        print("错误: 未设置 GPT4O_API_KEY 环境变量")
        print("请设置环境变量或创建 .env 文件")
        return 1
    
    try:
        # 创建 GPT-4o 增强器实例
        enhancer = GPT4OEnhancer(api_key=api_key)
        
        print("=" * 50)
        print("示例内容:")
        print(SAMPLE_CONTENT)
        print("=" * 50)
        
        # 1. 生成优化的元描述
        print("\n1. 生成优化的元描述:")
        description = enhancer.generate_meta_description(SAMPLE_CONTENT)
        print(description)
        
        # 2. 优化关键词
        print("\n2. 优化关键词:")
        keywords = enhancer.optimize_keywords(SAMPLE_CONTENT, directory_name="十神")
        print(keywords)
        
        # 3. 生成结构化数据
        print("\n3. 生成结构化数据:")
        metadata = {
            "title": "十神介绍",
            "description": description,
            "keywords": keywords
        }
        structured_data = enhancer.generate_structured_data(
            SAMPLE_CONTENT, 
            metadata, 
            "example/十神/十神介绍.md"
        )
        if structured_data:
            import json
            print(json.dumps(structured_data, ensure_ascii=False, indent=2))
        
        # 4. 分析内容并提供 SEO 建议
        print("\n4. SEO 分析和建议:")
        analysis = enhancer.analyze_content_for_seo(SAMPLE_CONTENT, "example/十神/十神介绍.md")
        print(analysis)
        
        # 5. 翻译内容示例
        print("\n5. 翻译内容示例 (中文 -> 英文):")
        # 只翻译前两段作为示例
        sample_for_translation = "\n".join(SAMPLE_CONTENT.strip().split("\n")[:3])
        translated = enhancer.translate_content(sample_for_translation, "中文", "英文")
        print(translated)
        
        print("\n示例运行完成！")
        return 0
    
    except Exception as e:
        print(f"错误: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
