# 生产级 RAG 系统实战

## 一、项目概述

构建一个生产可用的企业知识库问答系统，支持文档上传、智能检索、流式回答，包含完整的监控与评估体系。

### 技术栈

| 组件 | 选型 | 说明 |
|------|------|------|
| RAG 框架 | Haystack 2.x | Pipeline 编排 |
| 向量数据库 | Qdrant / Milvus | 高性能 ANN 检索 |
| LLM | OpenAI / 本地 vLLM | 兼容多种模型 |
| 文档解析 | Unstructured | PDF/Word/Excel 解析 |
| 监控 | Prometheus + Grafana | 延迟、召回率仪表盘 |
| 部署 | Docker Compose | 一键部署 |

## 二、系统架构

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  用户界面    │────▶│   API 网关   │────▶│  Haystack    │
│  (React)    │     │  (FastAPI)   │     │  Pipeline    │
└─────────────┘     └──────────────┘     └──────┬───────┘
                                                │
                    ┌───────────────────────────┼───────────┐
                    │                           │           │
               ┌────▼────┐              ┌──────▼──────┐    │
               │ Qdrant  │              │  LLM 服务   │    │
               │ 向量库   │              │ (vLLM/OpenAI)│    │
               └─────────┘              └─────────────┘    │
                    │                           │           │
               ┌────▼────┐                             │
               │ MongoDB │  ← 元数据存储                    │
               └─────────┘                              │
                    └──────────────────────────────────────┘
```

### Pipeline 设计

```python
from haystack import Pipeline
from haystack.components.converters import TextFileToDocument, PyPDFToDocument
from haystack.components.preprocessors import DocumentCleaner, DocumentSplitter
from haystack.components.writers import DocumentWriter
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack.components.retrievers import EmbeddingRetriever
from haystack.components.readers import ExtractiveReader
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore

# 索引 Pipeline
indexing = Pipeline()
indexing.add_component("converter", PyPDFToDocument())
indexing.add_component("cleaner", DocumentCleaner())
indexing.add_component("splitter", DocumentSplitter(split_by="sentence", split_length=200))
indexing.add_component("embedder", SentenceTransformersTextEmbedder(model="BAAI/bge-large-zh-v1.5"))
indexing.add_component("writer", DocumentWriter(document_store=QdrantDocumentStore()))
indexing.connect("converter", "cleaner")
indexing.connect("cleaner", "splitter")
indexing.connect("splitter", "embedder")
indexing.connect("embedder", "writer")

# 查询 Pipeline
query = Pipeline()
query.add_component("query_embedder", SentenceTransformersTextEmbedder(model="BAAI/bge-large-zh-v1.5"))
query.add_component("retriever", EmbeddingRetriever(document_store=QdrantDocumentStore(), top_k=5))
query.add_component("reader", ExtractiveReader())
query.connect("query_embedder", "retriever")
query.connect("retriever", "reader")
```

## 三、高级检索策略

### 混合检索 (Hybrid Search)

```python
from haystack.components.retrievers import BM25Retriever
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore
from sentence_transformers import CrossEncoder

class HybridRetriever:
    def __init__(self, document_store, embedder_model="BAAI/bge-large-zh-v1.5"):
        self.document_store = document_store
        self.dense_retriever = EmbeddingRetriever(
            document_store=document_store, top_k=10
        )
        self.sparse_retriever = BM25Retriever(
            document_store=document_store, top_k=10
        )
        self.reranker = CrossEncoder("BAAI/bge-reranker-large")

    def retrieve(self, query_text: str, top_k: int = 5):
        dense_results = self.dense_retriever.run(query_text)
        sparse_results = self.sparse_retriever.run(query_text)
        # 合并去重
        seen = set()
        candidates = []
        for doc in dense_results["documents"] + sparse_results["documents"]:
            if doc.id not in seen:
                seen.add(doc.id)
                candidates.append(doc)
        # Rerank 重排序
        pairs = [(query_text, doc.content) for doc in candidates]
        scores = self.reranker.predict(pairs)
        ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in ranked[:top_k]]
```

### Query 路由与改写

```python
from haystack.components.generators import OpenAIGenerator

class QueryRouter:
    """智能路由：根据问题类型选择不同的检索策略"""

    def __init__(self):
        self.llm = OpenAIGenerator(model="gpt-4o-mini")

    def classify(self, query: str) -> str:
        prompt = f"""分析问题类型，返回以下之一：
- factual: 事实型（"公司2024年营收是多少"）
- summary: 总结型（"总结这份报告的主要内容"）
- comparison: 对比型（"A方案和B方案的区别"）
- action: 操作型（"如何配置Nginx"）

问题：{query}
类型："""
        result = self.llm.run(prompt)
        return result.strip()

    def rewrite(self, query: str, history: list[str]) -> str:
        """多轮对话中重写query"""
        if not history:
            return query
        prompt = f"""基于对话历史，补全当前问题：
历史：{' '.join(history[-3:])}
当前：{query}
补全后的问题："""
        return self.llm.run(prompt).strip()
```

## 四、生产化部署

### FastAPI 服务

```python
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uuid

app = FastAPI(title="Enterprise RAG API")

class QueryRequest(BaseModel):
    query: str
    history: list[str] = []
    stream: bool = True

class DocumentIngestResponse(BaseModel):
    doc_id: str
    chunks: int
    status: str

@app.post("/v1/ingest", response_model=DocumentIngestResponse)
async def ingest_document(file: UploadFile = File(...)):
    """上传并索引文档"""
    doc_id = str(uuid.uuid4())
    content = await file.read()
    # 保存临时文件
    with open(f"/tmp/{doc_id}.pdf", "wb") as f:
        f.write(content)
    # 执行索引 Pipeline
    result = indexing.run({"converter": {"sources": [f"/tmp/{doc_id}.pdf"]}})
    return DocumentIngestResponse(
        doc_id=doc_id,
        chunks=len(result["writer"]["documents"]),
        status="indexed"
    )

@app.post("/v1/query")
async def query(request: QueryRequest):
    """检索并生成答案"""
    if request.stream:
        return StreamingResponse(
            stream_answer(request.query, request.history),
            media_type="text/event-stream"
        )
    # 非流式
    context = hybrid_retriever.retrieve(request.query)
    answer = llm.generate(context, request.query)
    return {"answer": answer, "sources": [d.meta for d in context]}

async def stream_answer(query: str, history: list[str]):
    """流式生成 SSE 响应"""
    context = hybrid_retriever.retrieve(query)
    yield f"data: {json.dumps({'type': 'sources', 'data': [d.meta for d in context]})}\n\n"
    async for chunk in llm.astream(context, query):
        yield f"data: {json.dumps({'type': 'token', 'data': chunk})}\n\n"
```

### Docker Compose

```yaml
version: "3.8"
services:
  qdrant:
    image: qdrant/qdrant:latest
    volumes:
      - ./data/qdrant:/qdrant/storage
    ports:
      - "6333:6333"

  api:
    build: .
    environment:
      - QDRANT_HOST=qdrant
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - EMBEDDER_MODEL=BAAI/bge-large-zh-v1.5
    ports:
      - "8000:8000"
    depends_on:
      - qdrant

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    ports:
      - "80:80"
    depends_on:
      - api
```

## 五、评估体系

### RAGAS 评估

```python
from ragas import evaluate
from ragas.metrics import (
    faithfulness, answer_relevancy, context_precision, context_recall
)

def evaluate_pipeline(test_set: list[dict]) -> dict:
    """评估 RAG 系统的各项指标"""
    result = evaluate(
        dataset=test_set,  # 包含 question, answer, contexts, ground_truth
        metrics=[
            faithfulness,          # 答案忠实于上下文
            answer_relevancy,      # 答案与问题相关性
            context_precision,     # 检索到的上下文精确率
            context_recall,        # 检索到的上下文召回率
        ]
    )
    return {
        "faithfulness": result["faithfulness"],
        "answer_relevancy": result["answer_relevancy"],
        "context_precision": result["context_precision"],
        "context_recall": result["context_recall"],
    }
```

### 监控指标埋点

```python
from prometheus_client import Counter, Histogram, Gauge
import time

rag_query_total = Counter("rag_query_total", "Total RAG queries", ["status"])
rag_latency = Histogram("rag_latency_seconds", "RAG query latency", buckets=[0.1, 0.5, 1, 2, 5])
retrieval_hit_rate = Gauge("retrieval_hit_rate", "Retrieval relevance rate")

@rag_latency.time()
def monitored_query(query: str):
    try:
        result = query_pipeline.run(query)
        rag_query_total.labels(status="success").inc()
        return result
    except Exception as e:
        rag_query_total.labels(status="error").inc()
        raise
```

## 六、性能优化 Checklist

- [ ] 使用 ONNX 加速 Embedding 推理
- [ ] 开启 Qdrant 内存映射模式
- [ ] Embedding 结果缓存 (LRU Cache)
- [ ] 批量索引/异步写入
- [ ] 分片策略：按文档类型分 Collection
- [ ] LLM 推理使用 vLLM + PagedAttention
- [ ] 开启 Response Cache（相同 query 命中缓存）
- [ ] 连接池调优：max_connections=100

## 七、面试考点

1. **RAG 系统的瓶颈在哪里？** 检索召回率和 LLM 推理延迟。解决方案：混合检索 + Rerank，vLLM 流式推理
2. **如何评估 RAG 质量？** RAGAS 四维指标（faithfulness, relevancy, precision, recall）+ 人工 A/B Test
3. **长文档如何处理？** 递归分割 + 滑动窗口，检索时用 Summary Window 策略
4. **如何保证数据安全？** 文档级权限控制、Query 过滤、敏感信息脱敏

## 八、课后练习

1. 实现一个 Query 改写组件，支持同义词扩展和多轮对话上下文补全
2. 在 Qdrant 中实现全文检索 + 向量检索的混合检索 Pipeline
3. 搭建 Prometheus + Grafana 监控仪表盘，监控 P99 延迟和召回率
4. 使用 RAGAS 构建 50 条测试集并评估当前系统，写出改进方案

## 自测题

1. Haystack 中 `Pipeline` 与 `Pipeline.run()` 的关系是？ A) 继承 B) 组合 C) 工厂 D) 代理
2. 以下哪种检索方式不适用于 RAG？ A) Dense Retrieval B) BM25 C) 顺序扫描 D) Hybrid Search
3. Rerank 的作用是？ A) 减少检索量 B) 重新排序提升精度 C) 压缩文档 D) 改写问题

**答案：** 1-B, 2-C, 3-B
