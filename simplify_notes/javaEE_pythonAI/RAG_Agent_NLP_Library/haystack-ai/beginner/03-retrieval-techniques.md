# Haystack 检索技术详解

检索是 RAG 系统的核心，本文详细介绍各种检索技术和策略。

## 1. 基础检索方法

### BM25 检索（关键词检索）

BM25 是一种经典的关键词检索算法，适合精确匹配关键词的场景。

```python
from haystack.components.retrievers import InMemoryBM25Retriever
from haystack.document_stores.in_memory import InMemoryDocumentStore

# 创建文档存储
document_store = InMemoryDocumentStore()

# BM25 检索器
retriever = InMemoryBM25Retriever(
    document_store=document_store,
    top_k=5,                    # 返回前5个结果
    scale_score=False           # 是否归一化分数
)

# 使用不同参数的 BM25
retriever = InMemoryBM25Retriever(
    document_store=document_store,
    top_k=10,
    k1=1.5,                     # 词频饱和参数
    b=0.75,                     # 长度归一化参数
    scale_score=True
)

# 检索
results = retriever.run(query="Python编程教程")
for doc in results["documents"]:
    print(f"内容: {doc.content[:50]}...")
    print(f"分数: {doc.score}\\n")
```

**参数说明：**
- `k1`: 控制词频饱和度，通常 1.2-2.0
- `b`: 控制文档长度归一化，通常 0.75
- `top_k`: 返回的文档数量

### 向量检索（语义检索）

基于向量相似度的检索，能够理解语义相似性。

```python
from haystack.components.retrievers import InMemoryEmbeddingRetriever
from haystack.components.embedders import SentenceTransformersTextEmbedder

# 创建文本嵌入器
text_embedder = SentenceTransformersTextEmbedder(
    model="sentence-transformers/all-MiniLM-L6-v2"
)

# 创建检索器
retriever = InMemoryEmbeddingRetriever(
    document_store=document_store,
    top_k=5,
    filters=None               # 可添加过滤条件
)

# 检索
query = "机器学习的基础知识"
query_embedding = text_embedder.run(text=query)
results = retriever.run(query_embedding=query_embedding["embedding"])

for doc in results["documents"]:
    print(f"内容: {doc.content[:50]}...")
    print(f"相似度: {doc.score:.4f}\\n")
```

**推荐的嵌入模型：**
- 英文: `all-MiniLM-L6-v2`, `all-mpnet-base-v2`
- 中文: `paraphrase-multilingual-MiniLM-L12-v2`
- 多语言: `sentence-t5-large`, `sentence-t5-xl`

## 2. 高级检索方法

### 混合检索（Hybrid Search）

结合关键词和语义检索的优势。

```python
from haystack.components.retrievers import InMemoryHybridRetriever
from haystack.components.rankers import TransformersSimilarityRanker
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack import Pipeline

# 创建混合检索管道
pipeline = Pipeline()

# 添加组件
pipeline.add_component("retriever", InMemoryHybridRetriever(
    document_store=document_store,
    top_k=20                     # 先检索更多
))
pipeline.add_component("embedder", SentenceTransformersTextEmbedder(
    model="sentence-transformers/all-MiniLM-L6-v2"
))
pipeline.add_component("ranker", TransformersSimilarityRanker(
    model="cross-encoder/ms-marco-MiniLM-L-6-v2"
))

# 连接组件
pipeline.connect("retriever.documents", "ranker.documents")

# 执行检索
query = "深度学习与机器学习的区别"
query_embedding = pipeline.get_component("embedder").run(text=query)

results = pipeline.run({
    "retriever": {"query": query},
    "ranker": {"query_embedding": query_embedding["embedding"]}
})
```

### 重新排序（Reranking）

对初步检索结果进行更精确的排序。

```python
from haystack.components.rankers import TransformersSimilarityRanker
from haystack.components.embedders import SentenceTransformersTextEmbedder

# 创建重排序器
ranker = TransformersSimilarityRanker(
    model="BAAI/bge-reranker-base",
    top_k=5,                    # 最终保留的结果数
    score_threshold=None        # 分数阈值
)

# 使用流程
embedder = SentenceTransformersTextEmbedder(model="BAAI/bge-small-en-v1.5")

query = "什么是Transformer模型？"
query_embedding = embedder.run(text=query)

# 假设有初步检索结果
initial_docs = [...]  # 来自初步检索

results = ranker.run(
    documents=initial_docs,
    query_embedding=query_embedding["embedding"]
)

for doc in results["documents"]:
    print(f"分数: {doc.score:.4f}")
    print(f"内容: {doc.content}\\n")
```

**推荐的重排序模型：**
- 英文: `cross-encoder/ms-marco-MiniLM-L-6-v2`, `BAAI/bge-reranker-base`
- 中文: `BAAI/bge-reranker-large`, `BAAI/bge-reranker-v2-m3`

### 递归检索

对于分层结构的文档，使用递归检索策略。

```python
from haystack import Pipeline
from haystack.components.retrievers import InMemoryEmbeddingRetriever
from haystack.components.builders import PromptBuilder

template = """
上下文信息：
{% for doc in documents %}
- {{ doc.content }}
{% endfor %}

基于以上信息回答问题。如果需要更多信息，请说明需要查看哪个章节。

问题：{{ question }}
"""

# 检索父级文档
pipeline = Pipeline()
pipeline.add_component("parent_retriever", InMemoryEmbeddingRetriever(
    document_store=parent_doc_store,
    top_k=3
))
pipeline.add_component("prompt_builder", PromptBuilder(template=template))
pipeline.add_component("llm", OpenAIGenerator(model="gpt-4"))

pipeline.connect("parent_retriever.documents", "prompt_builder.documents")
pipeline.connect("prompt_builder", "llm")

# 如果LLM建议查看特定章节，再检索子文档
```

### 多跳检索

通过多次检索获得更全面的信息。

```python
class MultiHopRetriever:
    def __init__(self, retriever, max_hops=2):
        self.retriever = retriever
        self.max_hops = max_hops

    def retrieve(self, query, documents_so_far=None):
        if documents_so_far is None:
            documents_so_far = []

        # 当前检索
        results = self.retriever.run(query=query)
        current_docs = results["documents"]

        # 合并结果
        all_docs = documents_so_far + current_docs

        # 是否继续检索
        if len(all_docs) >= self.max_hops * 5:
            return all_docs

        # 生成下一个查询
        next_query = self._generate_next_query(current_docs, query)
        if next_query:
            return self.retrieve(next_query, all_docs)

        return all_docs

    def _generate_next_query(self, documents, original_query):
        # 使用LLM生成相关查询
        # 这里简化处理
        if len(documents) > 0:
            return documents[0].content[:50]
        return None
```

## 3. 检索优化策略

### 查询扩展

扩展原始查询以提高召回率。

```python
from haystack.components.generators import OpenAIGenerator
from haystack import Pipeline

query_expansion_template = """
原始查询：{{ query }}

生成3个相关的查询变体，用于提高检索效果。每行一个查询。
"""

# 查询扩展管道
expansion_pipeline = Pipeline()
expansion_pipeline.add_component("expander", OpenAIGenerator(model="gpt-4"))
expansion_pipeline.add_component("prompt_builder", PromptBuilder(
    template=query_expansion_template
))
expansion_pipeline.connect("prompt_builder", "expander")

# 扩展查询
original_query = "机器学习算法"
expanded_queries = expansion_pipeline.run({
    "prompt_builder": {"query": original_query}
})

# 对每个扩展查询进行检索
all_results = []
for query in [original_query] + expanded_queries["expander"]["replies"]:
    results = retriever.run(query=query)
    all_results.extend(results["documents"])
```

### 查询改写

将用户的自然语言查询改写为更适合检索的形式。

```python
query_rewrite_template = """
用户问题：{{ user_question }}

将这个问题改写为简短的关键词查询，用于文档检索。只返回改写后的查询，不要其他内容。
"""

rewrite_pipeline = Pipeline()
rewrite_pipeline.add_component("rewriter", OpenAIGenerator(model="gpt-4"))
rewrite_pipeline.add_component("prompt_builder", PromptBuilder(
    template=query_rewrite_template
))
rewrite_pipeline.connect("prompt_builder", "rewriter")

user_question = "请问你能告诉我深度学习和传统机器学习有什么区别吗？"
rewritten = rewrite_pipeline.run({
    "prompt_builder": {"user_question": user_question}
})
```

### 检索结果去重

```python
def deduplicate_results(documents, threshold=0.9):
    """基于相似度去重"""
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np

    # 提取嵌入
    embeddings = [doc.embedding for doc in documents if doc.embedding]
    if not embeddings:
        return documents

    embeddings = np.array(embeddings)

    # 计算相似度矩阵
    similarities = cosine_similarity(embeddings)

    # 去重
    to_keep = []
    for i, doc in enumerate(documents):
        if i not in to_keep:
            to_keep.append(i)
            # 移除相似文档
            for j in range(i + 1, len(documents)):
                if similarities[i][j] > threshold:
                    if j not in to_keep:
                        to_keep.append(j)

    return [documents[i] for i in to_keep]

# 使用
deduplicated = deduplicate_results(results["documents"])
```

### 自定义过滤

```python
# 基于元数据过滤
filters = {
    "operator": "AND",
    "conditions": [
        {"field": "category", "operator": "==", "value": "技术"},
        {"field": "date", "operator": ">=", "value": "2024-01-01"}
    ]
}

results = retriever.run(
    query="Python",
    filters=filters
)

# 更复杂的过滤
from datetime import datetime, timedelta

def recent_filter(days=30):
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    return {
        "field": "created_at",
        "operator": ">=",
        "value": cutoff
    }

results = retriever.run(
    query="最新技术",
    filters={
        "operator": "AND",
        "conditions": [
            {"field": "published", "operator": "==", "value": True},
            recent_filter(days=7)
        ]
    }
)
```

## 4. 检索评估

### 检索质量评估

```python
def evaluate_retrieval(retriever, test_queries, relevant_docs):
    """评估检索质量"""
    results = {
        "precision": [],
        "recall": [],
        "mrr": []  # Mean Reciprocal Rank
    }

    for query, expected in zip(test_queries, relevant_docs):
        retrieved = retriever.run(query=query)["documents"]

        # Precision@K
        retrieved_ids = {doc.meta.get("id") for doc in retrieved[:5]}
        relevant_ids = set(expected)
        precision = len(retrieved_ids & relevant_ids) / len(retrieved_ids)

        # Recall@K
        recall = len(retrieved_ids & relevant_ids) / len(relevant_ids)

        # MRR
        mrr = 0
        for i, doc in enumerate(retrieved, 1):
            if doc.meta.get("id") in relevant_ids:
                mrr = 1 / i
                break

        results["precision"].append(precision)
        results["recall"].append(recall)
        results["mrr"].append(mrr)

    return {
        "precision": sum(results["precision"]) / len(results["precision"]),
        "recall": sum(results["recall"]) / len(results["recall"]),
        "mrr": sum(results["mrr"]) / len(results["mrr"])
    }
```

## 5. 完整检索管道示例

```python
from haystack import Pipeline
from haystack.components.retrievers import InMemoryEmbeddingRetriever
from haystack.components.rankers import TransformersSimilarityRanker
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack.document_stores.in_memory import InMemoryDocumentStore

# 创建文档存储
document_store = InMemoryDocumentStore()

# 创建完整的检索管道
retrieval_pipeline = Pipeline()

# 添加组件
retrieval_pipeline.add_component("embedder", SentenceTransformersTextEmbedder(
    model="sentence-transformers/all-MiniLM-L6-v2"
))
retrieval_pipeline.add_component("retriever", InMemoryEmbeddingRetriever(
    document_store=document_store,
    top_k=20
))
retrieval_pipeline.add_component("ranker", TransformersSimilarityRanker(
    model="BAAI/bge-reranker-base",
    top_k=5
))

# 连接组件
retrieval_pipeline.connect("embedder.embedding", "retriever.query_embedding")
retrieval_pipeline.connect("retriever.documents", "ranker.documents")

# 使用
query = "Python中的装饰器是什么？"
results = retrieval_pipeline.run({"embedder": {"text": query}})
```

## 小结

本节介绍了 Haystack 的各种检索技术：

- **基础检索** - BM25 和向量检索
- **高级检索** - 混合检索、重排序、递归检索
- **检索优化** - 查询扩展、改写、过滤
- **检索评估** - Precision、Recall、MRR

## 实践练习

### 编程题
1. 实现一个包含"检索 → 重排序 → 生成"三步的 RAG 管道，对比使用重排序和不使用重排序的回答质量差异。
2. 编写查询扩展的管道，对用户原始查询生成 3 个变体后分别检索，合并去重后输出结果。

### 思考题
1. 混合检索（Hybrid Search）的权重应该如何分配？什么情况下 BM25 的权重要高于向量检索？
2. 递归检索（Recursive Retrieval）适用于什么场景？它和单次检索相比有什么优势？

### 自测题
1. BM25 参数 `k1` 和 `b` 分别控制什么？
2. 重排序模型（Reranker）和检索模型有什么不同？
3. 查询扩展和查询改写的区别是什么？

下一步将学习高级 RAG 技术（→ `04-rag-advanced.md`）。