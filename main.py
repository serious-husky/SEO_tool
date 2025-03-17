#!/usr/bin/env python3
"""
SEO 优化工具主程序

这个程序集成了所有 SEO 优化功能，提供完整的自动化 SEO 优化流程。
根据配置和环境，自动决定是否使用 GPT-4o 增强功能。
默认对整个 Docusaurus 项目中所有文档更新前置元数据。
"""

import os
import sys
import argparse
import time
import logging
import yaml
import json
from pathlib import Path
from dotenv import load_dotenv

# 导入各个模块
from config import SITE_INFO, PATHS, SITEMAP, ROBOTS
from analyze_seo import SEOAnalyzer
from update_frontmatter import update_frontmatter, process_directory as update_frontmatter_directory

# 尝试导入 GPT-4o 增强器，如果不可用则忽略
try:
    from gpt4o_enhancer import GPT4OEnhancer
    gpt4o_available = True
except (ImportError, ModuleNotFoundError):
    gpt4o_available = False

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("seo_optimization.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SEO_Optimizer")

class SEOOptimizer:
    """SEO 优化器类，集成所有 SEO 优化功能"""
    
    def __init__(self, config=None):
        """初始化 SEO 优化器"""
        # 加载环境变量
        load_dotenv()
        
        # 加载配置
        self.config = config or {}
        self.docs_dir = self.config.get('docs_dir', PATHS.get('docs_dir', '../cantian-ai-wiki/docs'))
        self.i18n_dir = self.config.get('i18n_dir', os.path.join(os.path.dirname(self.docs_dir), 'i18n'))
        self.static_dir = self.config.get('static_dir', PATHS.get('static_dir', '../cantian-ai-wiki/static'))
        self.output_dir = self.config.get('output_dir', PATHS.get('output_dir', 'seo_reports'))
        self.site_url = self.config.get('site_url', SITE_INFO.get('url', 'https://your-docusaurus-site.example.com'))
        
        # 检查 GPT-4o API 密钥
        self.api_key = os.environ.get("GPT4O_API_KEY")
        self.use_gpt4o = gpt4o_available and self.api_key and self.config.get('use_gpt4o', True)
        
        if self.use_gpt4o:
            try:
                self.gpt4o_enhancer = GPT4OEnhancer(api_key=self.api_key)
                logger.info("GPT-4o 增强功能已启用")
            except Exception as e:
                logger.warning(f"GPT-4o 增强功能初始化失败: {e}")
                self.use_gpt4o = False
        
        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 初始化 SEO 分析器
        self.analyzer = SEOAnalyzer()
    
    def create_robots_txt(self):
        """创建或更新 robots.txt 文件"""
        robots_path = os.path.join(self.static_dir, 'robots.txt')
        
        # 构建 robots.txt 内容
        content = []
        content.append("User-agent: *")
        
        if ROBOTS.get('allow_all', True):
            content.append("Allow: /")
        
        # 添加禁止访问的路径
        for path in ROBOTS.get('disallow_paths', []):
            content.append(f"Disallow: {path}")
        
        # 添加站点地图路径
        sitemap_path = ROBOTS.get('sitemap_path', 'sitemap.xml')
        content.append(f"\n# 指定网站地图的位置")
        content.append(f"Sitemap: {self.site_url}/{sitemap_path}")
        
        # 写入文件
        with open(robots_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(content))
        
        logger.info(f"robots.txt 文件已创建: {robots_path}")
        return robots_path
    
    def generate_sitemap_index(self):
        """生成站点地图索引文件"""
        from generate_sitemap_index import generate_sitemap_index
        
        output_path = os.path.join(self.static_dir, 'sitemap-index.xml')
        locales = SITE_INFO.get('locales', ['en', 'zh-Hans', 'zh-Hant', 'ja', 'ko'])
        
        generate_sitemap_index(self.site_url, locales, output_path)
        logger.info(f"站点地图索引文件已生成: {output_path}")
        return output_path
    
    def analyze_seo(self):
        """分析 SEO 状况并生成报告"""
        logger.info(f"开始分析 SEO 状况: {self.docs_dir}")
        self.analyzer.analyze_directory(self.docs_dir)
        self.analyzer.generate_report(self.output_dir)
        logger.info(f"SEO 分析报告已生成到目录: {self.output_dir}")
        return self.output_dir
    
    def update_frontmatter_basic(self, directory, preview=False):
        """使用基本方法更新前置元数据"""
        logger.info(f"开始更新前置元数据 (基本方法): {directory}")
        
        class Args:
            def __init__(self, preview):
                self.preview = preview
        
        args = Args(preview)
        
        if os.path.isfile(directory):
            update_frontmatter(directory, args)
        else:
            update_frontmatter_directory(directory, args)
        
        logger.info(f"前置元数据更新完成 (基本方法): {directory}")
    
    def update_frontmatter_enhanced(self, directory, preview=False):
        """使用 GPT-4o 增强方法更新前置元数据"""
        logger.info(f"开始更新前置元数据 (GPT-4o 增强): {directory}")
        
        if os.path.isfile(directory):
            if preview:
                with open(directory, 'r', encoding='utf-8') as f:
                    content = f.read()
                analysis = self.gpt4o_enhancer.analyze_content_for_seo(content, directory)
                logger.info(f"SEO 分析:\n{analysis}")
            else:
                self.gpt4o_enhancer.enhance_frontmatter(directory)
        else:
            self.gpt4o_enhancer.batch_enhance_directory(directory, preview=preview)
        
        logger.info(f"前置元数据更新完成 (GPT-4o 增强): {directory}")
    
    def run_full_optimization(self, target_dir=None, preview=False):
        """运行完整的 SEO 优化流程"""
        start_time = time.time()
        logger.info("开始完整 SEO 优化流程")
        
        # 1. 创建 robots.txt
        self.create_robots_txt()
        
        # 2. 生成站点地图索引
        self.generate_sitemap_index()
        
        # 3. 分析 SEO 状况
        self.analyze_seo()
        
        # 4. 更新前置元数据
        target = target_dir or self.docs_dir
        
        # 处理主文档目录
        if self.use_gpt4o:
            self.update_frontmatter_enhanced(target, preview=preview)
        else:
            self.update_frontmatter_basic(target, preview=preview)
        
        # 处理 i18n 目录下的翻译文件
        if not target_dir and os.path.exists(self.i18n_dir):  # 只在未指定目标目录时处理 i18n
            logger.info(f"开始处理 i18n 目录: {self.i18n_dir}")
            for lang_dir in os.listdir(self.i18n_dir):
                i18n_docs_dir = os.path.join(self.i18n_dir, lang_dir, 'docusaurus-plugin-content-docs')
                if os.path.exists(i18n_docs_dir):
                    logger.info(f"处理语言目录: {lang_dir}")
                    if self.use_gpt4o:
                        self.update_frontmatter_enhanced(i18n_docs_dir, preview=preview)
                    else:
                        self.update_frontmatter_basic(i18n_docs_dir, preview=preview)
        
        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"SEO 优化流程完成，耗时: {duration:.2f} 秒")
        
        # 生成优化报告
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "duration": f"{duration:.2f} 秒",
            "target": target,
            "use_gpt4o": self.use_gpt4o,
            "preview_mode": preview,
            "seo_issues": sum(self.analyzer.stats.values()),
            "files_processed": len(self.analyzer.issues),
            "output_dir": self.output_dir
        }
        
        report_path = os.path.join(self.output_dir, 'optimization_report.json')
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"优化报告已生成: {report_path}")
        return report

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='SEO 优化工具')
    parser.add_argument('--target', help='要处理的文件或目录路径，默认为配置中的 docs_dir')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--preview', action='store_true', help='预览模式，不实际修改文件')
    parser.add_argument('--no-gpt4o', action='store_true', help='禁用 GPT-4o 增强功能')
    parser.add_argument('--analyze-only', action='store_true', help='仅分析 SEO 状况，不进行优化')
    parser.add_argument('--update-only', action='store_true', help='仅更新前置元数据，不进行其他优化')
    parser.add_argument('--robots-only', action='store_true', help='仅创建 robots.txt 文件')
    parser.add_argument('--sitemap-only', action='store_true', help='仅生成站点地图索引')
    parser.add_argument('--api-key', help='GPT-4o API 密钥，如果不提供则使用环境变量 GPT4O_API_KEY')
    args = parser.parse_args()
    
    # 加载配置
    config = {}
    if args.config:
        try:
            with open(args.config, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return 1
    
    # 设置 API 密钥
    if args.api_key:
        os.environ["GPT4O_API_KEY"] = args.api_key
    
    # 禁用 GPT-4o
    if args.no_gpt4o:
        config['use_gpt4o'] = False
    
    try:
        optimizer = SEOOptimizer(config)
        
        if args.analyze_only:
            # 仅分析 SEO 状况
            optimizer.analyze_seo()
        elif args.update_only:
            # 仅更新前置元数据
            target = args.target or optimizer.docs_dir
            if optimizer.use_gpt4o:
                optimizer.update_frontmatter_enhanced(target, preview=args.preview)
            else:
                optimizer.update_frontmatter_basic(target, preview=args.preview)
        elif args.robots_only:
            # 仅创建 robots.txt 文件
            optimizer.create_robots_txt()
        elif args.sitemap_only:
            # 仅生成站点地图索引
            optimizer.generate_sitemap_index()
        else:
            # 运行完整的 SEO 优化流程
            optimizer.run_full_optimization(
                target_dir=args.target,
                preview=args.preview
            )
        
        return 0
    except Exception as e:
        logger.error(f"SEO 优化过程中出错: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())
