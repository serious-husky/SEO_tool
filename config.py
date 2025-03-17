"""
SEO 优化工具配置文件

这个文件包含 SEO 优化工具的配置参数，可以根据需要修改。
"""

# 网站基本信息
SITE_INFO = {
    "name": "Cantian AI Wiki",
    "url": "https://your-docusaurus-site.example.com",
    "author": "Cantian AI Team",
    "default_locale": "en",
    "locales": ["en", "ja", "ko", "zh-Hans", "zh-Hant"],
}

# SEO 分析配置
SEO_ANALYSIS = {
    "min_description_length": 50,
    "max_description_length": 160,
    "min_keywords_count": 3,
    "max_keywords_count": 10,
    "min_content_length": 200,
    "max_paragraph_length": 300,
    "min_internal_links": 2,
}

# 结构化数据配置
STRUCTURED_DATA = {
    "default_type": "Article",
    "organization": {
        "name": "Cantian AI",
        "url": "https://cantian.ai",
        "logo": "https://your-docusaurus-site.example.com/img/logo_light.svg",
    },
    "default_image": "https://your-docusaurus-site.example.com/img/docusaurus-social-card.jpg",
}

# 目录关键词映射
DIRECTORY_KEYWORDS = {
    "十神": ["十神", "命理", "八字", "中国传统文化", "命理学"],
    "天干": ["天干", "命理", "八字", "中国传统文化", "命理学", "干支"],
    "地支": ["地支", "命理", "八字", "中国传统文化", "命理学", "干支"],
    "神煞": ["神煞", "命理", "八字", "中国传统文化", "命理学", "吉凶"],
    "星运_十二长生_": ["十二长生", "星运", "命理", "八字", "中国传统文化", "命理学"],
    "其他名词解释": ["命理", "八字", "中国传统文化", "命理学", "术语"],
}

# 多语言 SEO 配置
MULTILINGUAL = {
    "generate_hreflang": True,
    "generate_language_sitemaps": True,
    "translate_structured_data": True,
    "translate_meta_tags": True,
}

# 站点地图配置
SITEMAP = {
    "changefreq": "weekly",
    "priority": 0.5,
    "ignore_patterns": ["/tags/**", "/search/**"],
    "filename": "sitemap.xml",
}

# robots.txt 配置
ROBOTS = {
    "allow_all": True,
    "disallow_paths": ["/private/", "/temp/"],
    "sitemap_path": "sitemap-index.xml",
}

# 文件路径配置
PATHS = {
    "docs_dir": "../cantian-ai-wiki/docs",
    "static_dir": "../cantian-ai-wiki/static",
    "output_dir": "seo_reports",
}
