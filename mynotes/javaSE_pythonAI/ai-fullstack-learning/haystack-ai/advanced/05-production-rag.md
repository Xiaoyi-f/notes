# 生产级 RAG 系统构建

本节介绍如何构建可扩展、可靠、可维护的生产级 RAG 系统。

## 1. 系统架构设计

### 分层架构

```
┌─────────────────────────────────────────────────────────┐
│                      API Layer                          │
│              (REST API / WebSocket / GraphQL)           │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                  Application Layer                      │
│          (RAG Pipeline / Query Processing)              │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   Service Layer                         │
│    (Retrieval / Generation / Caching / Monitoring)      │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                  Data Layer                             │
│   (Vector DB / Document Store / Cache / Queue)          │
└─────────────────────────────────────────────────────────┘
```

### 微服务架构

```python
# rag_service.py - RAG 服务
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from haystack import Pipeline
import logging

app = FastAPI(title="RAG API")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueryRequest(BaseModel):
    question: str
    top_k: int = 5
    filters: dict = None

class QueryResponse(BaseModel):
    answer: str
    sources: list
    metadata: dict

# 初始化 RAG pipeline
rag_pipeline = None

@app.on_event("startup")
async def startup():
    global rag_pipeline
    logger.info("Initializing RAG pipeline...")
    rag_pipeline = create_rag_pipeline()
    logger.info("RAG pipeline ready")

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    try:
        result = rag_pipeline.run({
            "retriever": {"query": request.question, "filters": request.filters},
            "prompt_builder": {"question": request.question}
        })

        return QueryResponse(
            answer=result["llm"]["replies"][0],
            sources=[
                {"content": doc.content, "score": doc.score}
                for doc in result["retriever"]["documents"]
            ],
            metadata={
                "model": "gpt-4",
                "latency": result.get("latency")
            }
        )
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 2. 数据库选择与配置

### Elasticsearch 配置

```python
from haystack.document_stores.elasticsearch import ElasticsearchDocumentStore

# 生产环境 Elasticsearch 配置
document_store = ElasticsearchDocumentStore(
    hosts=["http://elasticsearch-1:9200", "http://elasticsearch-2:9200"],
    index="documents",
    embedding_dim=384,
    similarity="cosine",
    verify_certs=True,
    ca_certs="/path/to/ca.crt",
    basic_auth=("username", "password"),
    http_compress=True,
    timeout=30,
    max_retries=3,
    retry_on_timeout=True
)

# 集群健康检查
document_store.client.cluster.health()
```

### PostgreSQL + pgvector 配置

```python
from haystack.document_stores.pgvector import PgvectorDocumentStore

import psycopg2
from psycopg2 import pool

# 连接池配置
connection_pool = psycopg2.pool.ThreadedConnectionPool(
    minconn=5,
    maxconn=20,
    host="postgres.cluster.internal",
    database="rag_db",
    user="rag_user",
    password="secure_password",
    port=5432
)

# Pgvector 文档存储
document_store = PgvectorDocumentStore(
    connection_string="postgresql://rag_user:password@postgres.cluster.internal:5432/rag_db",
    table_name="documents",
    embedding_dim=1536,
    vector_function="cosine_similarity",
    recreate_table=False,
    search_strategy="hnsw",           # 使用 HNSW 索引
    hnsw_recreate_index_if_exists=False,
    hnsw_index_params={
        "m": 16,                      # 连接数
        "ef_construction": 64         # 构建时搜索参数
    },
    hnsw_ef_search=50                 # 搜索时 ef 参数
)
```

### Milvus 配置（大规模生产环境）

```python
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType

# 连接 Milvus 集群
connections.connect(
    alias="default",
    host="milvus.cloud.internal",
    port=19530,
    user="admin",
    password="password",
    secure=True
)

# 定义 Collection Schema
fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1536),
    FieldSchema(name="metadata", dtype=DataType.JSON),
    FieldSchema(name="timestamp", dtype=DataType.INT64)
]

schema = CollectionSchema(
    fields=fields,
    description="RAG documents collection",
    enable_dynamic_field=True
)

# 创建 Collection
collection = Collection(
    name="rag_documents",
    schema=schema
)

# 创建索引
index_params = {
    "metric_type": "IP",          # 内积距离
    "index_type": "HNSW",
    "params": {
        "M": 16,
        "efConstruction": 256
    }
}

collection.create_index(
    field_name="embedding",
    index_params=index_params
)

collection.load()
```

## 3. 缓存策略

### Redis 缓存

```python
import redis
import json
import hashlib
from typing import Optional

class RAGCache:
    def __init__(self, redis_host="localhost", redis_port=6379):
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=0,
            decode_responses=True
        )
        self.ttl = 3600  # 1小时

    def _generate_key(self, query: str) -> str:
        """生成缓存键"""
        hash_obj = hashlib.md5(query.encode())
        return f"rag:query:{hash_obj.hexdigest()}"

    def get(self, query: str) -> Optional[dict]:
        """获取缓存结果"""
        key = self._generate_key(query)
        cached = self.redis_client.get(key)
        if cached:
            return json.loads(cached)
        return None

    def set(self, query: str, result: dict):
        """设置缓存"""
        key = self._generate_key(query)
        self.redis_client.setex(
            key,
            self.ttl,
            json.dumps(result)
        )

    def invalidate(self, query: str):
        """使缓存失效"""
        key = self._generate_key(query)
        self.redis_client.delete(key)

    def clear_all(self):
        """清空所有缓存"""
        keys = self.redis_client.keys("rag:query:*")
        if keys:
            self.redis_client.delete(*keys)

# 在 RAG pipeline 中使用
cache = RAGCache()

def cached_query(query: str):
    cached_result = cache.get(query)
    if cached_result:
        logger.info(f"Cache hit for query: {query}")
        return cached_result

    result = rag_pipeline.run({"query": query})
    cache.set(query, result)
    return result
```

### 多级缓存

```python
from functools import lru_cache
from cachetools import TTLCache

class MultiLevelCache:
    def __init__(self):
        # L1: 内存缓存
        self.l1_cache = TTLCache(maxsize=1000, ttl=300)  # 5分钟
        # L2: Redis 缓存
        self.l2_cache = RAGCache()

    def get(self, query: str) -> Optional[dict]:
        # 先查 L1
        if query in self.l1_cache:
            return self.l1_cache[query]

        # 再查 L2
        result = self.l2_cache.get(query)
        if result:
            self.l1_cache[query] = result
            return result

        return None

    def set(self, query: str, result: dict):
        # 写入 L1 和 L2
        self.l1_cache[query] = result
        self.l2_cache.set(query, result)
```

## 4. 监控与日志

### Prometheus 监控

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# 定义指标
query_counter = Counter(
    'rag_queries_total',
    'Total number of queries',
    ['status']
)

query_duration = Histogram(
    'rag_query_duration_seconds',
    'Query processing duration'
)

document_retrieved = Gauge(
    'rag_documents_retrieved',
    'Number of documents retrieved'
)

cache_hits = Counter(
    'rag_cache_hits_total',
    'Total cache hits'
)

cache_misses = Counter(
    'rag_cache_misses_total',
    'Total cache misses'
)

# 使用指标
@query_duration.time()
def process_query(query: str):
    try:
        result = rag_pipeline.run({"query": query})
        query_counter.labels(status='success').inc()
        document_retrieved.set(len(result['documents']))
        return result
    except Exception as e:
        query_counter.labels(status='error').inc()
        raise

# 启动 metrics 服务器
start_http_server(8001)
```

### 结构化日志

```python
import logging
import json
from pythonjsonlogger import jsonlogger

# 配置 JSON 日志
logger = logging.getLogger(__name__)
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(asctime)s %(name)s %(levelname)s %(message)s')
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# 结构化日志记录
def log_query(query, result, duration):
    logger.info(
        "query_processed",
        extra={
            "query": query,
            "answer_length": len(result['answer']),
            "num_documents": len(result['sources']),
            "duration_ms": duration * 1000,
            "model": result['metadata']['model']
        }
    )
```

## 5. 错误处理与重试

### 指数退避重试

```python
import time
from functools import wraps

def retry_on_failure(max_retries=3, base_delay=1, max_delay=32):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = base_delay
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(
                        f"Attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {delay}s..."
                    )
                    time.sleep(delay)
                    delay = min(delay * 2, max_delay)

            raise last_exception
        return wrapper
    return decorator

# 使用
@retry_on_failure(max_retries=5)
def call_llm(prompt: str):
    return llm_client.generate(prompt)
```

### 断路器模式

```python
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=60)
def external_api_call(endpoint: str):
    response = requests.get(endpoint)
    response.raise_for_status()
    return response.json()

# 当失败次数达到阈值时，断路器会打开，阻止更多请求
# 一段时间后会自动尝试恢复
```

## 6. 批量处理

### 批量索引

```python
import concurrent.futures
from tqdm import tqdm

def batch_index_documents(documents, batch_size=100, max_workers=4):
    """批量索引文档"""
    total_docs = len(documents)
    indexed_count = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []

        with tqdm(total=total_docs, desc="Indexing") as pbar:
            for i in range(0, total_docs, batch_size):
                batch = documents[i:i + batch_size]

                future = executor.submit(index_batch, batch)
                futures.append(future)

            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    indexed_count += result
                    pbar.update(result)
                except Exception as e:
                    logger.error(f"Batch indexing failed: {e}")

    logger.info(f"Indexed {indexed_count}/{total_docs} documents")
    return indexed_count

def index_batch(batch):
    """索引一批文档"""
    embedding_result = embedder.run(documents=batch)
    document_store.write_documents(embedding_result["documents"])
    return len(batch)
```

## 7. 数据备份与恢复

### Elasticsearch 备份

```python
from elasticsearch.client import SnapshotClient

class ElasticsearchBackup:
    def __init__(self, es_client):
        self.snapshot_client = SnapshotClient(es_client)

    def create_repository(self, repo_name, s3_bucket):
        """创建快照仓库"""
        body = {
            "type": "s3",
            "settings": {
                "bucket": s3_bucket,
                "region": "us-east-1"
            }
        }
        self.snapshot_client.create_repository(
            repository=repo_name,
            body=body
        )

    def create_snapshot(self, repo_name, snapshot_name, indices):
        """创建快照"""
        body = {
            "indices": indices,
            "ignore_unavailable": True,
            "include_global_state": False
        }
        self.snapshot_client.create(
            repository=repo_name,
            snapshot=snapshot_name,
            body=body,
            wait_for_completion=True
        )

    def restore_snapshot(self, repo_name, snapshot_name):
        """恢复快照"""
        self.snapshot_client.restore(
            repository=repo_name,
            snapshot=snapshot_name,
            wait_for_completion=True
        )
```

## 小结

本节介绍了生产级 RAG 系统的关键要素：

- **架构设计** - 分层、微服务
- **数据库** - ES、PostgreSQL、Milvus
- **缓存** - Redis、多级缓存
- **监控** - Prometheus、结构化日志
- **可靠性** - 重试、断路器
- **性能** - 批量处理
- **数据安全** - 备份恢复

## 实践练习

### 编程题
1. 基于 FastAPI 封装一个 RAG 服务，包含 `/query`（查询）和 `/health`（健康检查）端点，并添加 Prometheus 监控指标。
2. 实现一个带 Redis 缓存和重试机制的 RAG 查询函数，相同问题 1 小时内直接返回缓存。

### 思考题
1. 生产环境的 RAG 系统需要考虑哪些非功能性需求？
2. Elasticsearch、PostgreSQL+pgvector、Milvus 分别适合什么规模和场景？

### 自测题
1. 多级缓存（L1+L2）的好处是什么？
2. 断路器模式（Circuit Breaker）解决什么问题？
3. HNSW 索引参数 `m` 和 `ef_construction` 分别影响什么？

下一步将学习 LangChain Agent 开发（→ `langchain-agent/beginner/01-langchain-basics.md`）。