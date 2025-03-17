# SEO 优化工具

这个工具集用于优化 Docusaurus 网站的 SEO，提高搜索引擎和大型语言模型的爬取效果。

## 功能概述

1. **SEO 分析**：分析网站内容的 SEO 状况，检查常见问题并生成报告
2. **前置元数据更新**：批量更新 Markdown 文件的前置元数据，添加 SEO 相关字段
3. **结构化数据模板**：提供各种类型的结构化数据模板，用于增强内容的语义信息
4. **多语言站点地图生成**：生成多语言站点地图索引文件，帮助搜索引擎更好地索引不同语言版本的内容
5. **GPT-4o 增强**：使用 GPT-4o 模型增强 SEO 优化效果，提供更智能的内容分析和优化建议
6. **一键优化**：集成所有功能的主程序，提供完整的自动化 SEO 优化流程

## 使用方法

### 1. 一键优化（推荐）

使用集成的主程序一键完成所有 SEO 优化：

```bash
# 设置 API 密钥（如果使用 GPT-4o 增强）
export GPT4O_API_KEY="your-api-key"

# 运行完整的 SEO 优化流程
python main.py

# 预览模式，不实际修改文件
python main.py --preview

# 指定目标目录
python main.py --target ../cantian-ai-wiki/docs/十神

# 禁用 GPT-4o 增强功能
python main.py --no-gpt4o

# 仅执行特定功能
python main.py --analyze-only  # 仅分析 SEO 状况
python main.py --update-only   # 仅更新前置元数据
python main.py --robots-only   # 仅创建 robots.txt 文件
python main.py --sitemap-only  # 仅生成站点地图索引
```

主程序会自动检测是否可以使用 GPT-4o 增强功能，如果可用则使用 GPT-4o 增强，否则使用基本方法。

### 2. GPT-4o 增强

使用 GPT-4o 模型增强 SEO 优化效果：

```bash
# 设置 API 密钥
export GPT4O_API_KEY="your-api-key"

# 分析单个文件并提供 SEO 建议（预览模式）
python gpt4o_enhancer.py ../cantian-ai-wiki/docs/十神/十神介绍.md --preview

# 增强单个文件的前置元数据
python gpt4o_enhancer.py ../cantian-ai-wiki/docs/十神/十神介绍.md

# 批量增强目录中的所有文件
python gpt4o_enhancer.py ../cantian-ai-wiki/docs/十神

# 翻译内容到其他语言
python gpt4o_enhancer.py ../cantian-ai-wiki/docs/十神/十神介绍.md --translate en
```

GPT-4o 增强器提供以下功能：

- **智能元描述生成**：生成优化的、吸引人的元描述
- **关键词优化**：分析内容生成最相关的 SEO 关键词
- **结构化数据生成**：为内容生成优化的 JSON-LD 结构化数据
- **内容 SEO 分析**：提供详细的 SEO 改进建议
- **多语言翻译**：将内容翻译到其他语言，保持原始格式和结构

### 2. SEO 分析

分析网站内容的 SEO 状况，检查常见问题并生成报告：

```bash
python analyze_seo.py ../cantian-ai-wiki/docs --output seo_reports
```

这将分析 `../cantian-ai-wiki/docs` 目录下的所有 Markdown 文件，并在 `seo_reports` 目录中生成以下报告：

- `seo_stats.csv`：总体统计报告，包含各类 SEO 问题的数量和描述
- `seo_issues.csv`：文件问题详情报告，列出每个文件存在的具体 SEO 问题
- `keywords_stats.csv`：关键词统计报告，统计所有关键词的使用频率

### 2. 前置元数据更新

批量更新 Markdown 文件的前置元数据，添加 SEO 相关字段：

```bash
# 预览模式，不实际修改文件
python update_frontmatter.py ../cantian-ai-wiki/docs/十神 --preview

# 实际更新文件
python update_frontmatter.py ../cantian-ai-wiki/docs/十神
```

这将更新指定目录下所有 Markdown 文件的前置元数据，添加以下 SEO 相关字段：

- `description`：页面描述，用于搜索结果摘要
- `keywords`：关键词列表，用于提高搜索相关性
- `author`：作者信息
- `datePublished`：发布日期
- `dateModified`：最后修改日期
- `structuredData`：结构化数据配置

### 3. 生成多语言站点地图索引

生成多语言站点地图索引文件，帮助搜索引擎更好地索引不同语言版本的内容：

```bash
python generate_sitemap_index.py --base-url https://your-docusaurus-site.example.com/ --output ../cantian-ai-wiki/static/sitemap-index.xml
```

这将生成一个站点地图索引文件，包含指向各个语言版本站点地图的链接。

### 4. 使用结构化数据模板

`structured_data_templates.js` 文件提供了各种类型的结构化数据模板，可以用于增强内容的语义信息。这些模板可以通过以下方式使用：

1. 在页面的前置元数据中配置结构化数据类型和属性
2. 使用 SEO 插件自动生成结构化数据
3. 在页面内容中直接嵌入结构化数据脚本

## SEO 最佳实践

### 基础 SEO 优化

1. **元标签优化**：为每个页面设置合适的标题、描述和关键词
2. **网站地图**：生成和提交网站地图，帮助搜索引擎更全面地了解网站结构
3. **robots.txt**：配置 robots.txt 文件，指导搜索引擎爬虫如何抓取网站内容

### 多语言 SEO 优化

1. **语言前缀 URL**：为不同语言版本的页面设置语言前缀 URL
2. **hreflang 标签**：添加 hreflang 标签，指示页面的其他语言版本
3. **多语言网站地图**：为每种语言生成独立的网站地图

### 针对大模型爬取的优化

1. **结构化数据标记**：使用 JSON-LD 结构化数据，帮助大模型理解内容语义
2. **内容组织优化**：使用清晰的标题层级和逻辑结构，便于大模型理解内容关系
3. **语义关联增强**：增加内部链接，建立内容之间的关联

## 配置文件

- `config.py`：工具的配置文件，可以根据需要修改
- `seo_frontmatter_template.md`：前置元数据模板，包含 SEO 相关字段的说明和示例

## 依赖项

- Python 3.6+
- PyYAML
- requests
- python-dotenv
- 其他依赖项可以通过 `pip install -r requirements.txt` 安装

## 注意事项

1. 在批量更新前置元数据前，建议先使用 `--preview` 参数预览更改
2. 结构化数据应该准确反映页面内容，避免误导搜索引擎和用户
3. 关键词应该自然融入内容，避免关键词堆砌
4. 定期更新内容和修改日期，保持网站的新鲜度
5. 使用 GPT-4o 增强器需要有效的 API 密钥，可以通过环境变量 `GPT4O_API_KEY` 设置或通过 `--api-key` 参数传入
