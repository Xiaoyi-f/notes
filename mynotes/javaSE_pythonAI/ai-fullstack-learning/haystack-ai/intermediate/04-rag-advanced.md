# 高级 RAG 技术

本节介绍高级 RAG 技术和最佳实践。

## 1. RAG 优化策略

### 检索增强生成（RAG）与检索后生成

```python
from haystack import Pipeline
from haystack.components.retrievers import InMemoryEmbeddingRetriever
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator

# 标准 RAG Pipeline
template = """
使用以下信息回答问题：

{% for doc in documents %}
文档 {{ loop.index }}: {{ doc.content }}
{% endfor %}

问题：{{ question }}

答案：
"""

pipeline = Pipeline()
pipeline.add_component("retriever", InMemoryEmbeddingRetriever(document_store=doc_store, top_k=5))
pipeline.add_component("prompt_builder", PromptBuilder(template=template))
pipeline.add_component("llm", OpenAIGenerator(model="gpt-4"))

pipeline.connect("retriever.documents", "prompt_builder.documents")
pipeline.connect("prompt_builder", "llm")

result = pipeline.run({
    "retriever": {"query": "深度学习的应用"},
    "prompt_builder": {"question": "深度学习的应用"}
})
```

### CoT（Chain of Thought）RAG

```python
# 思维链增强的 RAG
cot_template = """
请按照以下步骤回答问题：

步骤1: 分析提供的文档内容
{% for doc in documents %}
- {{ doc.content }}
{% endfor %}

步骤2: 识别与问题相关的信息

步骤3: 思考如何利用这些信息回答问题

步骤4: 给出最终答案

问题：{{ question }}

答案：
"""

pipeline.add_component("prompt_builder", PromptBuilder(template=cot_template))
```

### ReAct RAG（推理 + 行动）

```python
from haystack import Pipeline, component

@component
class ReActAgent:
    def __init__(self, retriever, llm):
        self.retriever = retriever
        self.llm = llm

    def run(self, question: str, max_iterations: int = 3):
        thought = f"问题：{question}\\n让我思考一下..."

        for i in range(max_iterations):
            # 生成思考
            prompt = f"""
            当前思考：{thought}

            下一步行动应该是什么？
            选项：
            1. 检索相关信息
            2. 基于已有信息回答
            3. 继续思考

            回复选项编号：
            """

            action = self.llm.run(prompt=prompt)

            if "1" in action["replies"][0]:
                # 检索
                results = self.retriever.run(query=question)
                thought += f"\\n检索到：{len(results['documents'])}个相关文档"
            elif "2" in action["replies"][0]:
                # 回答
                break
            else:
                # 继续
                continue

        # 生成最终答案
        answer_prompt = f"""
        问题：{question}
        思考过程：{thought}

        基于以上信息，给出准确答案：
        """
        return self.llm.run(prompt=answer_prompt)
```

## 2. 多模态 RAG

### 图文混合检索

```python
from haystack import Document
from haystack.components.embedders import OpenAITextEmbedder, OpenAIDocumentEmbedder
from haystack.components.retrievers import InMemoryEmbeddingRetriever

# 创建多模态文档
multimodal_docs = [
    Document(
        content="这是一张机器学习架构图，展示了神经网络的结构",
        meta={
            "image_url": "https://example.com/ml-arch.png",
            "type": "image"
        }
    ),
    Document(
        content="深度学习模型训练过程示意图",
        meta={
            "image_url": "https://example.com/training-process.png",
            "type": "image"
        }
    )
]

# 使用支持多模态的嵌入器
from haystack.components.embedders import OpenAITextEmbedder

text_embedder = OpenAITextEmbedder(model="text-embedding-3-large")

# 检索时可以检索相关图片描述
query = "神经网络的结构图"
embedding = text_embedder.run(text=query)
results = retriever.run(query_embedding=embedding["embedding"])
```

### 表格数据检索

```python
import pandas as pd
from haystack import Document

def convert_table_to_documents(df):
    """将表格转换为文档"""
    documents = []

    # 整体描述文档
    description = f"表格包含{len(df)}行，{len(df.columns)}列数据。列名：{', '.join(df.columns)}"
    documents.append(Document(content=description, meta={"type": "table_description"}))

    # 每行数据文档
    for idx, row in df.iterrows():
        content = " | ".join([f"{col}: {val}" for col, val in row.items()])
        documents.append(Document(
            content=content,
            meta={
                "type": "table_row",
                "row_index": idx
            }
        ))

    return documents

# 使用
df = pd.DataFrame({
    "产品": ["A", "B", "C"],
    "价格": [100, 200, 150],
    "库存": [50, 30, 100]
})

docs = convert_table_to_documents(df)
```

## 3. 实时 RAG

### 流式 RAG

```python
from haystack.components.generators import OpenAIGenerator

# 流式生成器
generator = OpenAIGenerator(
    model="gpt-4",
    streaming_callback=lambda chunk: print(chunk, end="", flush=True)
)

# 在 pipeline 中使用
pipeline.add_component("streaming_generator", generator)
```

### 实时更新文档存储

```python
from haystack import Pipeline
from haystack.components.writers import DocumentWriter

# 监听文件变化
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class DocumentUpdateHandler(FileSystemEventHandler):
    def __init__(self, indexing_pipeline):
        self.indexing_pipeline = indexing_pipeline

    def on_modified(self, event):
        if event.src_path.endswith('.txt'):
            print(f"检测到文件变化: {event.src_path}")
            self.indexing_pipeline.run({
                "converter": {"sources": [event.src_path]}
            })

# 设置监听
observer = Observer()
handler = DocumentUpdateHandler(indexing_pipeline)
observer.schedule(handler, path="documents/", recursive=True)
observer.start()
```

## 4. RAG 质量评估

### 答案相关性评估

```python
from haystack.components.evaluators import FaithfulnessEvaluator, SASEvaluator

# 忠实度评估器 - 检查答案是否基于检索的文档
faithfulness_evaluator = FaithfulnessEvaluator()

# SASEvaluator - 评估答案质量
sase_evaluator = SASEvaluator()

def evaluate_rag_answer(question, retrieved_docs, answer):
    """评估 RAG 答案质量"""
    # 评估忠实度
    faithfulness_result = faithfulness_evaluator.run(
        questions=[question],
        contexts=[retrieved_docs],
        answers=[answer]
    )

    # 评估答案质量
    sas_result = sase_evaluator.run(
        questions=[question],
        contexts=[retrieved_docs],
        answers=[answer]
    )

    return {
        "faithfulness": faithfulness_result,
        "answer_quality": sas_result
    }
```

### 检索准确率评估

```python
def calculate_metrics(retrieved_docs, relevant_doc_ids):
    """计算检索指标"""
    retrieved_ids = [doc.meta["id"] for doc in retrieved_docs]

    # Precision@K
    precision = len(set(retrieved_ids) & set(relevant_doc_ids)) / len(retrieved_ids)

    # Recall@K
    recall = len(set(retrieved_ids) & set(relevant_doc_ids)) / len(relevant_doc_ids)

    # MAP (Mean Average Precision)
    ap = 0
    hits = 0
    for i, doc_id in enumerate(retrieved_ids, 1):
        if doc_id in relevant_doc_ids:
            hits += 1
            ap += hits / i
    map_score = ap / len(relevant_doc_ids) if relevant_doc_ids else 0

    return {
        "precision": precision,
        "recall": recall,
        "map": map_score
    }
```

## 5. RAG 性能优化

### 缓存策略

```python
import hashlib
import json
from functools import lru_cache

class CachedRetriever:
    def __init__(self, retriever):
        self.retriever = retriever
        self.cache = {}

    def run(self, query):
        # 生成缓存键
        cache_key = hashlib.md5(query.encode()).hexdigest()

        # 检查缓存
        if cache_key in self.cache:
            print("使用缓存结果")
            return self.cache[cache_key]

        # 执行检索
        result = self.retriever.run(query=query)

        # 缓存结果
        self.cache[cache_key] = result

        return result

    def clear_cache(self):
        self.cache.clear()
```

### 批量检索优化

```python
from haystack import Pipeline
import asyncio

class BatchRetriever:
    def __init__(self, retriever, batch_size=10):
        self.retriever = retriever
        self.batch_size = batch_size

    async def batch_retrieve(self, queries):
        """批量检索"""
        results = []

        for i in range(0, len(queries), self.batch_size):
            batch = queries[i:i + self.batch_size]

            # 并发检索
            tasks = [self._retrieve_single(query) for query in batch]
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)

        return results

    async def _retrieve_single(self, query):
        # 在实际应用中，这里可以调用异步 API
        return self.retriever.run(query=query)
```

## 6. 高级 RAG 模式

### GraphRAG（知识图谱增强 RAG）

```python
from haystack import Pipeline, component

@component
class GraphRetriever:
    def __init__(self, graph_store):
        self.graph_store = graph_store

    def run(self, query: str, top_k: int = 5):
        # 从查询中提取实体
        entities = self._extract_entities(query)

        # 在知识图谱中检索相关节点和边
        related_nodes = []
        for entity in entities:
            nodes = self.graph_store.get_related_nodes(entity)
            related_nodes.extend(nodes)

        return {"documents": related_nodes}

    def _extract_entities(self, text):
        # 使用 NER 提取实体
        # 简化实现
        return [word for word in text.split() if word.isupper()]
```

### HyDE（Hypothetical Document Embeddings）

```python
@component
class HypotheticalDocGenerator:
    def __init__(self, llm):
        self.llm = llm

    def run(self, query: str):
        prompt = f"""
        为以下问题生成一个理想的答案文档。答案应该详细且准确。

        问题：{query}

        理想答案：
        """

        result = self.llm.run(prompt=prompt)
        hypothetical_doc = Document(content=result["replies"][0])

        return {"documents": [hypothetical_doc]}

# 在 pipeline 中使用
pipeline = Pipeline()
pipeline.add_component("hyde_generator", HypotheticalDocGenerator(llm))
pipeline.add_component("doc_embedder", SentenceTransformersDocumentEmbedder(model=model_name))
pipeline.add_component("retriever", InMemoryEmbeddingRetriever(document_store=doc_store))

pipeline.connect("hyde_generator.documents", "doc_embedder.documents")
pipeline.connect("doc_embedder.documents", "retriever.documents")
```

### 查询理解增强

```python
@component
class QueryUnderstanding:
    def __init__(self, llm):
        self.llm = llm

    def run(self, query: str):
        prompt = f"""
        分析以下查询并提取：
        1. 主要意图
        2. 关键实体
        3. 需求类型（定义、比较、步骤、示例等）

        查询：{query}

        以JSON格式返回结果：
        """

        result = self.llm.run(prompt=prompt)

        return {"query_analysis": result["replies"][0]}
```

## 小结

本节介绍了高级 RAG 技术：

- **优化策略** - CoT、ReAct
- **多模态** - 图文、表格
- **实时 RAG** - 流式、实时更新
- **质量评估** - 忠实度、准确性
- **性能优化** - 缓存、批量
- **高级模式** - GraphRAG、HyDE

## 实践练习

### 编程题
1. 实现一个带有 HyDE（Hypothetical Document Embeddings）的检索管道，对比直接使用原始查询的检索效果。
2. 编写一个 CoT RAG 管道，让 LLM 按步骤分析文档后回答问题。

### 思考题
1. ReAct RAG 和标准 RAG 的区别是什么？什么场景适合用 ReAct？
2. 多模态 RAG 系统设计时，如何处理文本和图片的不对称检索问题？

### 自测题
1. HyDE 的核心思想是什么？
2. RAG 质量评估中，"忠实度（Faithfulness）"指的是什么？
3. GraphRAG 相比传统 RAG 的主要优势是什么？

下一步将学习生产级 RAG 系统构建（→ `05-production-rag.md`）。