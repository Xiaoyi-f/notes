# Haystack 文档处理

在 RAG 系统中，文档处理是关键的第一步。本节详细介绍如何处理各种类型的文档。

## 文档转换器

Haystack 提供了多种文档转换器，可以将不同格式的文档转换为 Haystack Document 对象。

### 1. 文本文件转换

```python
from haystack.components.converters import TextFileToDocument

# 转换单个文件
converter = TextFileToDocument()
result = converter.run(sources=["example.txt"])
documents = result["documents"]

# 转换多个文件
converter = TextFileToDocument()
result = converter.run(sources=["file1.txt", "file2.txt", "file3.txt"])
documents = result["documents"]
```

### 2. Markdown 文件转换

```python
from haystack.components.converters import MarkdownToDocument

converter = MarkdownToDocument()
result = converter.run(sources=["README.md", "docs/api.md"])
documents = result["documents"]

# 保留 Markdown 结构
converter = MarkdownToDocument(
    remove_code_blocks=False,      # 保留代码块
    remove_substrings=None         # 自定义要移除的子字符串
)
```

### 3. PDF 文件转换

```python
from haystack.components.converters import PyPDFToDocument

converter = PyPDFToDocument()
result = converter.run(sources=["document.pdf"])
documents = result["documents"]

# 指定页面范围
result = converter.run(sources=["document.pdf", "document2.pdf"])

# 获取每页的元数据
for doc in documents:
    print(doc.meta)  # 包含页码、文件路径等信息
```

### 4. HTML 网页转换

```python
from haystack.components.converters import HTMLToDocument

converter = HTMLToDocument()
result = converter.run(sources=["https://example.com/page.html"])
documents = result["documents"]

# 配置提取内容
converter = HTMLToDocument(
    extract_links=True,           # 提取链接
    extract_tables=True,          # 提取表格
    remove_tags=["script", "style"]  # 移除的标签
)
```

### 5. CSV 文件转换

```python
from haystack.components.converters import CSVToDocument

converter = CSVToDocument()
result = converter.run(sources=["data.csv"])
documents = result["documents"]

# 每行成为一个文档
for doc in documents:
    print(doc.content)
    print(doc.meta)  # 包含CSV的列信息
```

### 6. 图片转文本（OCR -> Optical Character Recognition光学字符识别）

```python
from haystack.components.converters import TesseractConverter

converter = TesseractConverter(language="chi_sim+eng")
result = converter.run(sources=["image.png", "scan.jpg"])
documents = result["documents"]
```

### 7. Excel 文件转换

```python
from haystack.components.converters import XLSXToDocument

converter = XLSXToDocument()
result = converter.run(sources=["data.xlsx"])
documents = result["documents"]

# 每个工作表产生文档
for doc in documents:
    print(doc.meta["sheet_name"])  # 工作表名称
```

### 8. 音频转文本

```python
from haystack.components.converters import AzureAudioToDocument

converter = AzureAudioToDocument(api_key="your-key", region="eastus")
result = converter.run(sources=["audio.mp3"])
documents = result["documents"]
```

## 文档清洗

处理文档时，需要清洗噪声数据。

### 1. 基本文档清洗

```python
from haystack import Document

# 移除多余空白
def clean_whitespace(text):
    return ' '.join(text.split())

# 移除特殊字符
import re
def clean_special_chars(text):
    return re.sub(r'[^a-zA-Z0-9\\s\\u4e00-\\u9fff.,!?;:]', '', text)

# 移除HTML标签
from bs4 import BeautifulSoup
def remove_html_tags(text):
    return BeautifulSoup(text, 'html.parser').get_text()
```

### 2. 文档去重

```python
from haystack.components.duplicators import DocumentDeduplicator

# 基于内容去重
deduplicator = DocumentDeduplicator(mode="content")
result = deduplicator.run(documents=documents)

# 基于嵌入去重
from haystack.components.duplicators import DocumentDeduplicator
deduplicator = DocumentDeduplicator(mode="embedding")
```

### 3. 文档筛选

```python
# 基于元数据筛选
filtered_docs = [
    doc for doc in documents
    if doc.meta.get("category") == "技术"
]

# 基于内容长度筛选
filtered_docs = [
    doc for doc in documents
    if len(doc.content) > 50
]

# 自定义筛选函数
def filter_docs(documents, condition):
    return [doc for doc in documents if condition(doc)]

filtered = filter_docs(
    documents,
    lambda doc: "python" in doc.content.lower()
)
```

## 文档分块

长文档需要分成小块，以便更好地检索和生成。

### 1. 基于字符数分块

```python
from haystack.components.preprocessors import DocumentSplitter

# 按固定字符数分块
splitter = DocumentSplitter(
    split_by="character",      # 字符数
    split_length=200,          # 每块200字符
    split_overlap=20,          # 重叠20字符
    remove_empty_docs=True
)

result = splitter.run(documents=long_documents)
chunked_docs = result["documents"]
```

### 2. 基于词语分块

```python
# 按词数分块
splitter = DocumentSplitter(
    split_by="word",           # 词数
    split_length=50,           # 每块50词
    split_overlap=5
)
```

### 3. 基于句子分块

```python
# 按句子分块
splitter = DocumentSplitter(
    split_by="sentence",
    split_length=5,            # 每块5句
    split_overlap=1
)
```

### 4. 基于段落分块

```python
# 按段落分块
splitter = DocumentSplitter(
    split_by="paragraph",
    split_length=3,            # 每块3段
    split_overlap=0
)
```

### 5. 智能语义分块

```python
from haystack.components.preprocessors import SemanticDocumentSplitter
from haystack.components.embedders import SentenceTransformersTextEmbedder

embedder = SentenceTransformersTextEmbedder(
    model="sentence-transformers/all-MiniLM-L6-v2"
)

# 基于语义相似度分块
splitter = SemanticDocumentSplitter(
    embedder=embedder,
    max_split_length=500,
    split_overlap=50
)

result = splitter.run(documents=long_documents)
```

### 6. 递归分块

```python
from haystack.components.preprocessors import RecursiveDocumentSplitter

# 优先按段落分割，其次按句子
splitter = RecursiveDocumentSplitter(
    separators=["\\n\\n", "\\n", "。", "！", "？", ".", "!", "?"],
    max_split_length=500,
    split_overlap=50
)

result = splitter.run(documents=long_documents)
```

## 文档预处理管道

### 完整的文档处理流程

```python
from haystack import Pipeline
from haystack.components.converters import TextFileToDocument
from haystack.components.preprocessors import DocumentSplitter
from haystack.components.cleaners import DocumentCleaner
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack.components.writers import DocumentWriter
from haystack.document_stores.in_memory import InMemoryDocumentStore

# 创建文档存储
document_store = InMemoryDocumentStore()

# 创建处理管道
pipeline = Pipeline()

# 添加组件
pipeline.add_component("converter", TextFileToDocument())
pipeline.add_component("cleaner", DocumentCleaner(
    remove_empty_lines=True,
    remove_extra_whitespaces=True,
    remove_repeated_substrings=False
))
pipeline.add_component("splitter", DocumentSplitter(
    split_by="character",
    split_length=300,
    split_overlap=30
))
pipeline.add_component("embedder", SentenceTransformersDocumentEmbedder(
    model="sentence-transformers/all-MiniLM-L6-v2"
))
pipeline.add_component("writer", DocumentWriter(document_store=document_store))

# 连接组件
pipeline.connect("converter.documents", "cleaner.documents")
pipeline.connect("cleaner.documents", "splitter.documents")
pipeline.connect("splitter.documents", "embedder.documents")
pipeline.connect("embedder.documents", "writer.documents")

# 执行处理
pipeline.run({"converter": {"sources": ["example.txt"]}})
```

## 爬虫集成

### 使用 Haystack 爬取网页

```python
from haystack.components.crawlers import Crawler

# 爬取单个网站
crawler = Crawler(
    urls=["https://example.com"],
    output_dir="crawled_data",
    depth=1,                      # 爬取深度
    overwrite=True,
    crawler_version="haystack-crawler"
)

crawler.run()

# 爬取多个网站
crawler = Crawler(
    urls=[
        "https://docs.python.org",
        "https://stackoverflow.com"
    ],
    output_dir="crawled_data",
    depth=2
)
```

### 自定义爬虫

```python
from haystack.components.converters import HTMLToDocument
import requests
from bs4 import BeautifulSoup

class CustomWebCrawler:
    def __init__(self):
        self.converter = HTMLToDocument()

    def crawl(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 提取文本内容
        text = soup.get_text()

        # 创建文档
        doc = Document(
            content=text,
            meta={
                "url": url,
                "title": soup.title.string if soup.title else "",
                "crawled_at": datetime.now().isoformat()
            }
        )

        return [doc]

    def crawl_multiple(self, urls):
        all_documents = []
        for url in urls:
            docs = self.crawl(url)
            all_documents.extend(docs)
        return all_documents
```

## 高级文档处理技巧

### 1. 保留文档结构

```python
from haystack import Document

# 保存文档层级信息
doc = Document(
    content="文档内容",
    meta={
        "chapter": "第一章",
        "section": "1.1 介绍",
        "subsection": "1.1.1 背景",
        "page": 1
    }
)
```

### 2. 代码文档处理

```python
import re

def extract_code_blocks(markdown_text):
    pattern = r'```(\\w+)?\\n(.*?)```'
    matches = re.findall(pattern, markdown_text, re.DOTALL)

    documents = []
    for lang, code in matches:
        doc = Document(
            content=code,
            meta={
                "type": "code",
                "language": lang if lang else "text"
            }
        )
        documents.append(doc)

    return documents
```

### 3. 表格数据处理

```python
import pandas as pd

def process_table_data(csv_path):
    df = pd.read_csv(csv_path)

    documents = []
    for index, row in df.iterrows():
        content = " | ".join([f"{col}: {val}" for col, val in row.items()])
        doc = Document(
            content=content,
            meta={
                "type": "table_row",
                "row_number": index
            }
        )
        documents.append(doc)

    return documents
```

### 4. 多模态文档处理

```python
# 处理包含文本和图片的文档
def process_multimodal_document(pdf_path):
    # 转换 PDF
    pdf_converter = PyPDFToDocument()
    docs = pdf_converter.run(sources=[pdf_path])

    # 提取图片
    from pdf2image import convert_from_path
    images = convert_from_path(pdf_path)

    # OCR 提取图片文字
    tesseract_converter = TesseractConverter(language="chi_sim+eng")
    for i, image in enumerate(images):
        image.save(f"temp_image_{i}.png")
        image_docs = tesseract_converter.run(sources=[f"temp_image_{i}.png"])
        docs.extend(image_docs["documents"])

    return docs
```

## 小结

本节介绍了文档处理的关键技术：

- **文档转换器** - 支持多种格式
- **文档清洗** - 去除噪声
- **文档分块** - 切分长文档
- **爬虫集成** - 自动收集数据
- **高级技巧** - 结构化、代码、表格、多模态处理

## 实践练习

### 编程题
1. 编写一个完整的文档处理管道，实现：PDF/Markdown 读取 → 清洗 → 语义分块 → 嵌入 → 写入文档存储。用至少 3 个不同格式的文件测试。
2. 实现一个自定义的 `DocumentCleaner`，能够移除文本中的特殊字符、多余空格和 HTML 标签。

### 思考题
1. 文档分块的 `split_overlap` 参数设置多大比较合适？为什么需要重叠？
2. 语义分块和固定长度分块各有什么适用场景？

### 自测题
1. Haystack 支持哪些文档格式的转换？
2. `DocumentSplitter` 支持哪几种分块方式？
3. 文档去重有哪两种模式？它们的区别是什么？

下一步将学习高级检索技术（→ `03-retrieval-techniques.md`）。