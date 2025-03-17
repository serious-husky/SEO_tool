/**
 * 结构化数据模板 - 用于SEO优化和大模型爬取
 * 
 * 这些模板可以添加到文档页面中，以提供更丰富的结构化数据，
 * 帮助搜索引擎和大型语言模型更好地理解内容。
 */

// 文章页面的结构化数据模板
const articleStructuredData = {
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "文章标题",
  "description": "文章描述",
  "image": "https://your-docusaurus-site.example.com/img/article-image.jpg",
  "author": {
    "@type": "Organization",
    "name": "Cantian AI",
    "url": "https://cantian.ai"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Cantian AI",
    "logo": {
      "@type": "ImageObject",
      "url": "https://your-docusaurus-site.example.com/img/logo_light.svg"
    }
  },
  "datePublished": "2023-01-01T00:00:00Z",
  "dateModified": "2023-01-01T00:00:00Z",
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://your-docusaurus-site.example.com/article-url"
  }
};

// 术语表/词汇表页面的结构化数据模板
const glossaryTermStructuredData = {
  "@context": "https://schema.org",
  "@type": "DefinedTerm",
  "name": "术语名称",
  "description": "术语定义",
  "inDefinedTermSet": {
    "@type": "DefinedTermSet",
    "name": "中国传统命理术语表"
  }
};

// FAQ页面的结构化数据模板
const faqStructuredData = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "问题1",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "回答1"
      }
    },
    {
      "@type": "Question",
      "name": "问题2",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "回答2"
      }
    }
  ]
};

// 如何在Docusaurus页面中使用结构化数据
/**
 * 在Docusaurus中添加结构化数据的方法：
 * 
 * 1. 在页面的frontmatter中添加自定义字段，例如：
 * ---
 * title: 页面标题
 * description: 页面描述
 * structuredData:
 *   type: Article
 *   datePublished: 2023-01-01
 *   dateModified: 2023-01-01
 *   image: /img/article-image.jpg
 * ---
 * 
 * 2. 创建一个自定义Docusaurus插件，读取frontmatter中的结构化数据字段，
 *    并在页面渲染时添加相应的JSON-LD脚本。
 * 
 * 3. 或者，在每个页面的MDX内容中直接添加结构化数据脚本：
 * 
 * ```jsx
 * export const StructuredData = () => (
 *   <script
 *     type="application/ld+json"
 *     dangerouslySetInnerHTML={{
 *       __html: JSON.stringify({
 *         "@context": "https://schema.org",
 *         "@type": "Article",
 *         "headline": "文章标题",
 *         // 其他字段...
 *       }),
 *     }}
 *   />
 * );
 * 
 * <StructuredData />
 * ```
 */

// 示例：如何为"十神介绍"页面添加结构化数据
const tenGodsIntroStructuredData = {
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "十神介绍 - 中国传统命理基础概念",
  "description": "十神是传统中国命理学中用于预测人生吉凶的术语，基于天干地支和五行相生相克理论，在八字命理分析中起核心作用。",
  "image": "https://your-docusaurus-site.example.com/img/ten-gods.jpg",
  "author": {
    "@type": "Organization",
    "name": "Cantian AI",
    "url": "https://cantian.ai"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Cantian AI",
    "logo": {
      "@type": "ImageObject",
      "url": "https://your-docusaurus-site.example.com/img/logo_light.svg"
    }
  },
  "datePublished": "2023-01-01T00:00:00Z",
  "dateModified": "2023-01-01T00:00:00Z",
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://your-docusaurus-site.example.com/十神/十神介绍"
  },
  "keywords": "十神,比肩,劫财,食神,伤官,偏财,正财,七杀,正官,偏印,正印,命理,八字",
  "inLanguage": ["en", "zh-Hans", "zh-Hant", "ja", "ko"]
};

module.exports = {
  articleStructuredData,
  glossaryTermStructuredData,
  faqStructuredData,
  tenGodsIntroStructuredData
};
