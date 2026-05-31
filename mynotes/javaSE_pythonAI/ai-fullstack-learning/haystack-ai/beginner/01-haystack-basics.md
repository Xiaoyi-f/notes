# Haystack AI 入门指南

## 什么是 Haystack？

Haystack 是一个开源的 NLP 框架，由 deepset 公司开发，专门用于构建基于大语言模型(LLM)的搜索系统。它是目前最强大的 RAG(Retrieval-Augmented Generation)框架之一。

### 核心特点

1. **模块化设计** - 每个组件都可以独立使用或组合使用
2. **支持多种模型** - OpenAI, Cohere, Hugging Face, Llama等
3. **可扩展性强** - 易于自定义和扩展
4. **生产就绪** - 支持高并发、监控、日志等生产特性

## RAG 是什么？

**RAG (Retrieval-Augmented Generation)** 是一种结合了检索和生成的AI系统架构。

### 工作流程

```
用户问题 → 检索器搜索相关文档 → 将文档和问题一起输入LLM → 生成答案
```

### 为什么需要 RAG？

- **解决幻觉问题** - LLM可能会编造不存在的信息
- **知识更新** - 不需要重新训练模型就能获取新知识
- **透明性** - 可以展示答案来源，提高可信度
- **成本效益** - 相比训练大模型，成本更低

## 安装 Haystack

```bash
# 基础安装
pip install haystack-ai

# 安装额外组件
pip install haystack-ai[elasticsearch]     # Elasticsearch
pip install haystack-ai[weaviate]          # Weaviate
pip install haystack-ai[pgvector]          # PostgreSQL向量存储
pip install haystack-ai[cohere,openai]     # 各种LLM模型
```

## 快速开始

### 1. 第一个简单的 RAG 系统

```python
from haystack import Document, Pipeline
from haystack.components.converters import TextFileToDocument
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack.components.writers import DocumentWriter
from haystack.components.retrievers import InMemoryBM25Retriever
from haystack.components.generators import OpenAIGenerator
from haystack.components.builders import PromptBuilder

# 创建文档
documents = [
    Document(content="Python是一种高级编程语言，由Guido van Rossum于1991年创建。"),
    Document(content="JavaScript是一种脚本语言，主要用于网页开发。"),
    Document(content="Java是一种面向对象的编程语言，由Sun Microsystems开发。"),
]

# 创建索引器管道
indexing_pipeline = Pipeline()
indexing_pipeline.add_component("writer", DocumentWriter(document_store=InMemoryDocumentStore()))

# 索引文档
indexing_pipeline.run({"writer": {"documents": documents}})

# 创建查询管道
query_pipeline = Pipeline()
query_pipeline.add_component("retriever", InMemoryBM25Retriever(document_store=doc_store))
query_pipeline.add_component("prompt_builder", PromptBuilder(
    template="根据以下信息回答问题：\\n\\n{% for doc in documents %}{{ doc.content }}\\n{% endfor %}\\n\\n问题：{{ question }}"
))
query_pipeline.add_component("llm", OpenAIGenerator(model="gpt-4"))

query_pipeline.connect("retriever", "prompt_builder.documents")
query_pipeline.connect("prompt_builder", "llm")

# 执行查询
result = query_pipeline.run({
    "retriever": {"query": "Python是谁创建的？"},
    "prompt_builder": {"question": "Python是谁创建的？"}
})

print(result["llm"]["replies"][0])
```

### 2. 使用 SentenceTransformers 嵌入

```python
from haystack.components.embedders import SentenceTransformersDocumentEmbedder, SentenceTransformersTextEmbedder
from haystack.components.retrievers import InMemoryEmbeddingRetriever
from haystack.document_stores.in_memory import InMemoryDocumentStore

# 创建文档存储
document_store = InMemoryDocumentStore()

# 文档嵌入器
doc_embedder = SentenceTransformersDocumentEmbedder(model="sentence-transformers/all-MiniLM-L6-v2")

# 索引文档
documents = [
    Document(content="机器学习是人工智能的一个分支。"),
    Document(content="深度学习使用神经网络进行学习。"),
    Document(content="NLP处理人类语言的计算机技术。"),
]
documents = doc_embedder.run(documents)
document_store.write_documents(documents["documents"])

# 查询
text_embedder = SentenceTransformersTextEmbedder(model="sentence-transformers/all-MiniLM-L6-v2")
retriever = InMemoryEmbeddingRetriever(document_store=document_store)

query = "什么是深度学习？"
query_embedding = text_embedder.run(text=query)
results = retriever.run(query_embedding=query_embedding["embedding"])

for doc in results["documents"]:
    print(doc.content, doc.score)
```

## 核心组件详解

### 1. Document（文档）

```python
from haystack import Document

# 基本文档
doc = Document(content="这是一份文档内容")

# 带元数据的文档
doc = Document(
    content="Python是一门编程语言",
    meta={
        "source": "维基百科",
        "category": "编程",
        "date": "2024-01-01"
    }
)

# 带嵌入的文档
doc = Document(
    content="文档内容",
    embedding=[0.1, 0.2, 0.3, ...]  # 384维向量
)
```

### 2. DocumentStore（文档存储）

```python
# 内存存储（适合开发和小规模数据）
from haystack.document_stores.in_memory import InMemoryDocumentStore
doc_store = InMemoryDocumentStore()

# Elasticsearch（生产环境推荐）
from haystack.document_stores.elasticsearch import ElasticsearchDocumentStore
doc_store = ElasticsearchDocumentStore(
    hosts="http://localhost:9200",
    index="documents"
)

# Weaviate（向量数据库）
from haystack.document_stores.weaviate import WeaviateDocumentStore
doc_store = WeaviateDocumentStore(
    url="http://localhost:8080",
    index="documents"
)

# PostgreSQL + pgvector（企业级方案）
from haystack.document_stores.pgvector import PgvectorDocumentStore
doc_store = PgvectorDocumentStore(
    connection_string="postgresql://user:password@localhost:5432/db",
    table_name="documents"
)
```

### 3. Retriever（检索器）

```python
# BM25 检索器（关键词检索）
from haystack.components.retrievers import InMemoryBM25Retriever
retriever = InMemoryBM25Retriever(document_store=doc_store, top_k=5)

# 嵌入检索器（语义检索）
from haystack.components.retrievers import InMemoryEmbeddingRetriever
retriever = InMemoryEmbeddingRetriever(document_store=doc_store, top_k=5)

# 混合检索器（结合关键词和语义）
from haystack.components.retrievers import InMemoryHybridRetriever
retriever = InMemoryHybridRetriever(document_store=doc_store, top_k=5)

# 多向量检索器
from haystack.components.retrievers import MultiVectorRetriever
retriever = MultiVectorRetriever(document_store=doc_store, top_k=5)
```

### 4. Embedder（嵌入器）

```python
# SentenceTransformers（本地模型，免费）
from haystack.components.embedders import SentenceTransformersTextEmbedder
embedder = SentenceTransformersTextEmbedder(
    model="sentence-transformers/all-MiniLM-L6-v2"
)

# OpenAI 嵌入
from haystack.components.embedders import OpenAITextEmbedder
embedder = OpenAITextEmbedder(model="text-embedding-3-small")

# Cohere 嵌入
from haystack.components.embedders import CohereTextEmbedder
embedder = CohereTextEmbedder(model="embed-english-v3.0")

# Hugging Face 嵌入
from haystack.components.embedders import HuggingFaceAPITextEmbedder
embedder = HuggingFaceAPITextEmbedder(model="BAAI/bge-small-en-v1.5")
```

### 5. Generator（生成器）

```python
# OpenAI
from haystack.components.generators import OpenAIGenerator
generator = OpenAIGenerator(
    model="gpt-4",
    api_key="your-api-key"
)

# Cohere
from haystack.components.generators import CohereGenerator
generator = CohereGenerator(model="command")

# Hugging Face
from haystack.components.generators import HuggingFaceAPIGenerator
generator = HuggingFaceAPIGenerator(
    model="meta-llama/Meta-Llama-3-8B-Instruct"
)

# Anthropic Claude
from haystack.components.generators import AnthropicGenerator
generator = AnthropicGenerator(
    model="claude-3-sonnet-20240229"
)
```

## Pipeline（管道）

Pipeline 是 Haystack 的核心概念，用于连接各个组件。

```python
from haystack import Pipeline
from haystack.components.retrievers import InMemoryBM25Retriever
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator

# 创建管道
pipeline = Pipeline()

# 添加组件
pipeline.add_component("retriever", InMemoryBM25Retriever(document_store=doc_store))
pipeline.add_component("prompt_builder", PromptBuilder(template=template))
pipeline.add_component("llm", OpenAIGenerator(model="gpt-4"))

# 连接组件
pipeline.connect("retriever.documents", "prompt_builder.documents")
pipeline.connect("prompt_builder", "llm")

# 可视化管道
pipeline.draw("pipeline.png")

# 运行管道
result = pipeline.run({
    "retriever": {"query": "用户问题"},
    "prompt_builder": {"question": "用户问题"}
})
```

## 常见应用场景

### 1. 问答系统

```python
# 文档问答系统
from haystack import Pipeline
from haystack.components.retrievers import InMemoryEmbeddingRetriever
from haystack.components.generators import OpenAIGenerator
from haystack.components.builders import PromptBuilder

template = """
使用以下文档回答问题。如果文档中没有答案，就说"我不知道"。

文档：
{% for doc in documents %}
- {{ doc.content }}
{% endfor %}

问题：{{ question }}
答案：
"""

pipeline = Pipeline()
pipeline.add_component("retriever", InMemoryEmbeddingRetriever(document_store=doc_store, top_k=3))
pipeline.add_component("prompt_builder", PromptBuilder(template=template))
pipeline.add_component("llm", OpenAIGenerator(model="gpt-4"))

pipeline.connect("retriever.documents", "prompt_builder.documents")
pipeline.connect("prompt_builder", "llm")

result = pipeline.run({
    "retriever": {"query": "什么是机器学习？"},
    "prompt_builder": {"question": "什么是机器学习？"}
})
```

### 2. 文档摘要

```python
from haystack import Pipeline
from haystack.components.summarizers import OpenAISummarizer

pipeline = Pipeline()
pipeline.add_component("summarizer", OpenAISummarizer(model="gpt-4"))

document = Document(content="很长的文档内容...")
result = pipeline.run({"summarizer": {"documents": [document]}})
print(result["summarizer"]["documents"][0].content)
```

### 3. 文档分类

```python
from haystack import Pipeline
from haystack.components.classifiers import DocumentClassifier

pipeline = Pipeline()
pipeline.add_component("classifier", DocumentClassifier(
    model="deepset/roberta-base-squad2",
    labels=["技术", "商业", "体育", "娱乐"]
))

documents = [Document(content="Python编程教程")]
result = pipeline.run({"classifier": {"documents": documents}})
```

## 小结

本节介绍了 Haystack 的基础概念和核心组件：

- **Document** - 文档数据结构
- **DocumentStore** - 文档存储
- **Retriever** - 检索器
- **Embedder** - 嵌入器
- **Generator** - 生成器
- **Pipeline** - 管道

## 实践练习

### 编程题
1. 创建一个包含 5 个文档的 DocumentStore，分别用 BM25 和嵌入检索器检索同一个问题，比较两种检索结果的区别。
2. 基于 `PromptBuilder` 创建自己的 RAG 提示模板，要求 LLM 在回答时标注信息来源编号。

### 思考题
1. RAG 相比直接让 LLM 回答问题，有哪些优势和劣势？
2. 什么场景下应该用 BM25 检索，什么场景下用嵌入检索？为什么？

### 自测题
1. Haystack 的核心组件有哪些？
2. Pipeline 的 `connect()` 方法有什么作用？
3. Document 对象的 `meta` 字段有什么用？

下一步将学习文档处理技术（→ `02-document-processing.md`）。