# 生产级文档存储实现

文档存储（Document Store）是 RAG 系统的数据底座。原型阶段用内存存储即可，但生产环境必须选择持久化、可扩展、高可用的方案。本节深入讲解主流向量数据库的配置、调优与运维。

## 1. 核心概念

### 1.1 向量索引原理

向量数据库的核心是将高维向量快速检索，依赖近似最近邻（ANN）索引。主流算法有三种：

| 算法 | 原理 | 召回率 | 构建速度 | 适用场景 |
|------|------|--------|----------|----------|
| **FLAT** | 暴力扫描全量向量 | 100% | 无需构建 | 数据量 < 1万，精度要求极高 |
| **IVF** | 先聚类到 Voronoi 单元，再搜索邻近单元 | 90~95% | 快 | 中等规模，内存有限 |
| **HNSW** | 分层可导航小世界图，贪心搜索 | 95~99% | 较慢 | 大规模生产环境首选 |

**HNSW 关键参数：**

```python
# 以 Qdrant 为例
hnsw_config = {
    "m": 16,                    # 每个节点的最大连接数，越大图越密，召回越高，内存越大
    "ef_construct": 100,        # 构建时的搜索深度，越大图质量越高，构建越慢
    "ef": 64,                   # 查询时的搜索深度，越大召回越高，延迟越大
    "on_disk": False            # 是否将索引存磁盘（内存不够时开启）
}
```

**参数调优建议：**
- `m`: 数据量 10万以下用 8~16，百万级用 16~32，千万级以上用 32~64
- `ef_construct`: 通常是 `m` 的 3~10 倍，构建时间敏感时取小值
- `ef`: 查询时动态设置，精确度要求高设 128~256，要求低设 32~64

### 1.2 距离度量方式

| 度量方式 | 公式特点 | 适用场景 |
|----------|----------|----------|
| **Cosine** | 忽略向量模长，只比较方向 | 语义相似度（最常用） |
| **Dot Product** | 考虑模长，大向量得分高 | 归一化后的向量、推荐系统 |
| **Euclidean (L2)** | 空间直线距离 | 物理位置、图像特征 |

**重要：** 嵌入模型和距离度量必须匹配。比如 `sentence-transformers/all-MiniLM-L6-v2` 输出已归一化，cosine 和 dot_product 结果一致；但 `BAAI/bge-large-zh` 未归一化，用 cosine 更稳定。

```python
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore

# cosine 是 RAG 语义检索的默认选择
document_store = QdrantDocumentStore(
    url="http://localhost:6333",
    index="documents",
    embedding_dim=768,
    similarity="cosine"          # 可选: "cosine", "dot_product", "l2"
)
```

### 1.3 分片与副本

```
┌─────────────────────────────────────────────┐
│              Collection (逻辑集合)              │
├─────────────┬─────────────┬─────────────────┤
│   Shard 0   │   Shard 1   │     Shard 2     │  ← 分片：水平扩展
│  (0~33333)  │ (33334~66666)│  (66667~100000) │
├──────┬──────┼──────┬──────┼──────┬──────────┤
│ Rep 0│ Rep 1│ Rep 0│ Rep 1│ Rep 0│  Rep 1   │  ← 副本：高可用
└──────┴──────┴──────┴──────┴──────┴──────────┘
```

- **分片（Sharding）**：将数据分布到多个节点，解决单机容量和吞吐量瓶颈
- **副本（Replication）**：每个分片存多份，某节点故障时不丢数据、服务不中断

**生产环境建议：**
- 节点数 >= 2 时开启副本，副本因子设为 2（共 3 份数据）
- 分片数 ≈ 数据量（万）/ 10，比如 100 万数据用 10 个分片
- 避免分片数过多（< 50），每个分片都有固定内存开销

## 2. 主流 DocumentStore 实战

### 2.1 Qdrant（推荐：中小规模 + 快速上手）

Qdrant 是用 Rust 编写的开源向量数据库，单机性能优秀，部署简单，Haystack 官方集成完善。

**本地 Docker 部署：**

```yaml
# docker-compose.yml
version: "3.8"
services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"      # REST API
      - "6334:6334"      # gRPC
    volumes:
      - ./qdrant_storage:/qdrant/storage
    environment:
      - QDRANT__SERVICE__HTTP_PORT=6333
    # 生产环境加内存限制
    deploy:
      resources:
        limits:
          memory: 4G
```

**Haystack 集成：**

```python
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack.components.writers import DocumentWriter
from haystack import Pipeline, Document

# 连接生产环境 Qdrant
document_store = QdrantDocumentStore(
    url="http://qdrant.cluster.internal:6333",
    index="haystack_docs",           # Collection 名称
    embedding_dim=768,               # 与嵌入模型维度一致
    similarity="cosine",
    return_embedding=True,           # 检索时返回向量
    wait_result_from_api=True,       # 写入后等待确认
    # HNSW 索引配置
    hnsw_config={
        "m": 16,
        "ef_construct": 100,
    },
    # 乐观并发控制
    on_disk_payload=True,            # payload 存磁盘，降低内存
    content_field="content",         # 文档内容字段
    name_field="name",               # 文档名称字段
    embedding_field="embedding",     # 向量字段
)

# 完整索引管道
indexing = Pipeline()
indexing.add_component("embedder", SentenceTransformersDocumentEmbedder(
    model="BAAI/bge-large-zh-v1.5"
))
indexing.add_component("writer", DocumentWriter(document_store=document_store))
indexing.connect("embedder.documents", "writer.documents")

# 带元数据的文档
docs = [
    Document(
        content="Haystack 是一个开源 NLP 框架",
        meta={
            "category": "框架介绍",
            "author": "deepset",
            "created_at": "2024-01-15",
            "source": "official_doc"
        }
    ),
    Document(
        content="Qdrant 是用 Rust 编写的高性能向量数据库",
        meta={
            "category": "基础设施",
            "author": "qdrant-team",
            "created_at": "2024-03-20",
            "source": "github"
        }
    ),
]

indexing.run({"embedder": {"documents": docs}})
```

**元数据过滤检索：**

```python
from haystack_integrations.components.retrievers.qdrant import QdrantEmbeddingRetriever
from haystack.components.embedders import SentenceTransformersTextEmbedder

query_pipeline = Pipeline()
query_pipeline.add_component("embedder", SentenceTransformersTextEmbedder(
    model="BAAI/bge-large-zh-v1.5"
))
query_pipeline.add_component("retriever", QdrantEmbeddingRetriever(
    document_store=document_store,
    top_k=5,
    filters={                          # 元数据过滤
        "operator": "AND",
        "conditions": [
            {"field": "meta.category", "operator": "==", "value": "框架介绍"},
            {"field": "meta.created_at", "operator": ">=", "value": "2024-01-01"}
        ]
    }
))
query_pipeline.connect("embedder.embedding", "retriever.query_embedding")

result = query_pipeline.run({"embedder": {"text": "Haystack 是什么？"}})
for doc in result["retriever"]["documents"]:
    print(f"Score: {doc.score:.4f} | {doc.content[:50]}...")
```

**Qdrant 集群模式：**

```yaml
# docker-compose.cluster.yml
version: "3.8"
services:
  qdrant-node1:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - ./qdrant-node1:/qdrant/storage
    environment:
      - QDRANT__CLUSTER__ENABLED=true
      - QDRANT__CLUSTER__P2P__PORT=6335
      - QDRANT__CLUSTER__CONSENSUS__MAX_MESSAGE_QUEUE_SIZE=1000

  qdrant-node2:
    image: qdrant/qdrant:latest
    ports:
      - "6336:6333"
    volumes:
      - ./qdrant-node2:/qdrant/storage
    environment:
      - QDRANT__CLUSTER__ENABLED=true
      - QDRANT__CLUSTER__P2P__PORT=6335
      - QDRANT__BOOTSTRAP=qdrant-node1:6335
```

### 2.2 PostgreSQL + pgvector（推荐：已有 PG 基础设施）

如果团队已有 PostgreSQL 技术栈，pgvector 是最平滑的扩展方案，无需引入新数据库。

**部署 pgvector：**

```bash
# Docker 快速启动
docker run -d \
  --name pgvector \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=rag_db \
  -p 5432:5432 \
  -v pgvector_data:/var/lib/postgresql/data \
  ankane/pgvector:latest

# 进入容器创建扩展
docker exec -it pgvector psql -U postgres -d rag_db -c "CREATE EXTENSION vector;"
```

**Haystack 集成：**

```python
from haystack_integrations.document_stores.pgvector import PgvectorDocumentStore

# 方式1: 连接字符串
document_store = PgvectorDocumentStore(
    connection_string="postgresql://postgres:secret@localhost:5432/rag_db",
    table_name="haystack_documents",
    embedding_dim=768,
    vector_function="cosine_similarity",   # 或 "inner_product", "l2_distance"
    search_strategy="hnsw",                 # 或 "exact_nn"
    # HNSW 索引参数
    hnsw_recreate_index_if_exists=False,
    hnsw_index_params={
        "m": 16,
        "ef_construction": 64
    },
    hnsw_ef_search=50,
    recreate_table=False,                   # 生产环境设为 False
    schema_name="public",
    language="simple",                      # 全文检索语言
)

# 方式2: 使用现有连接池（生产环境推荐）
import psycopg2.pool

connection_pool = psycopg2.pool.ThreadedConnectionPool(
    minconn=5,
    maxconn=50,
    host="postgres.cluster.internal",
    port=5432,
    database="rag_db",
    user="rag_user",
    password="secure_password"
)

document_store = PgvectorDocumentStore(
    connection_string="postgresql://rag_user:secure_password@postgres.cluster.internal:5432/rag_db",
    table_name="documents",
    embedding_dim=768,
    search_strategy="hnsw",
    hnsw_index_params={"m": 16, "ef_construction": 64},
)
```

**pgvector 性能优化：**

```sql
-- 查看 HNSW 索引大小
SELECT pg_size_pretty(pg_relation_size('documents_hnsw_idx'));

-- 查看表统计信息（用于查询计划优化）
ANALYZE haystack_documents;

-- 为常用过滤字段创建 B-tree 索引
CREATE INDEX idx_documents_category ON haystack_documents((meta->>'category'));
CREATE INDEX idx_documents_source ON haystack_documents((meta->>'source'));

-- 分区表（数据量 > 1000万时）
CREATE TABLE haystack_documents_y2024m01 PARTITION OF haystack_documents
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

**批量写入优化：**

```python
from haystack import Document
import time

def batch_write_optimized(documents, batch_size=500):
    """优化的批量写入，避免单条插入开销"""
    total = len(documents)
    written = 0

    for i in range(0, total, batch_size):
        batch = documents[i:i + batch_size]
        document_store.write_documents(batch)
        written += len(batch)
        print(f"Progress: {written}/{total}")
        # 给数据库喘息时间，避免锁竞争
        time.sleep(0.1)

# 使用 COPY 协议极速导入（绕过 ORM）
def fast_import_with_copy(documents, connection_string):
    """使用 PostgreSQL COPY 协议批量导入"""
    import psycopg2
    import json
    import numpy as np

    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()

    # 准备数据
    rows = []
    for doc in documents:
        embedding_str = f"[{','.join(map(str, doc.embedding))}]"
        rows.append((
            doc.id,
            doc.content,
            json.dumps(doc.meta),
            embedding_str
        ))

    # 使用 COPY
    from io import StringIO
    buffer = StringIO()
    for row in rows:
        buffer.write("\t".join(map(str, row)) + "\n")
    buffer.seek(0)

    cursor.copy_from(buffer, 'haystack_documents', columns=('id', 'content', 'meta', 'embedding'))
    conn.commit()
    cursor.close()
    conn.close()
```

### 2.3 Elasticsearch（推荐：需要全文检索 + 向量混合）

ES 的优势在于成熟的分布式架构、强大的全文检索能力、以及与现有日志/搜索基础设施的整合。

**部署与配置：**

```yaml
# docker-compose.es.yml
version: "3.8"
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms2g -Xmx2g"
    ports:
      - "9200:9200"
    volumes:
      - es_data:/usr/share/elasticsearch/data

volumes:
  es_data:
```

**Haystack 集成：**

```python
from haystack_integrations.document_stores.elasticsearch import ElasticsearchDocumentStore

# 生产集群配置
document_store = ElasticsearchDocumentStore(
    hosts=[
        "https://es-node1.internal:9200",
        "https://es-node2.internal:9200",
        "https://es-node3.internal:9200"
    ],
    index="rag_documents",
    embedding_dim=768,
    similarity="cosine",
    # 安全认证
    basic_auth=("rag_user", "secure_password"),
    verify_certs=True,
    ca_certs="/etc/ssl/certs/ca.crt",
    # 性能调优
    timeout=30,
    max_retries=3,
    retry_on_timeout=True,
    http_compress=True,              # 启用压缩
    # 返回 embedding（用于调试，生产可关闭节省带宽）
    return_embedding=False,
)

# 验证集群健康
health = document_store.client.cluster.health()
print(f"Cluster status: {health['status']}")  # green / yellow / red
print(f"Active shards: {health['active_primary_shards']}")
```

**混合检索（全文 + 向量）：**

```python
from haystack_integrations.components.retrievers.elasticsearch import ElasticsearchBM25Retriever, ElasticsearchEmbeddingRetriever
from haystack.components.joiners import DocumentJoiner
from haystack.components.rankers import TransformersSimilarityRanker
from haystack import Pipeline

# 创建混合检索管道
hybrid_pipeline = Pipeline()

# BM25 全文检索
hybrid_pipeline.add_component("bm25_retriever", ElasticsearchBM25Retriever(
    document_store=document_store,
    top_k=10
))

# 向量检索
hybrid_pipeline.add_component("embedding_retriever", ElasticsearchEmbeddingRetriever(
    document_store=document_store,
    top_k=10
))

# 结果合并（RRF 算法）
hybrid_pipeline.add_component("joiner", DocumentJoiner(
    join_mode="reciprocal_rank_fusion",
    top_k=10,
    rank_constant=60
))

# 重排序
hybrid_pipeline.add_component("ranker", TransformersSimilarityRanker(
    model="BAAI/bge-reranker-large",
    top_k=5
))

# 连接
hybrid_pipeline.connect("bm25_retriever.documents", "joiner.documents")
hybrid_pipeline.connect("embedding_retriever.documents", "joiner.documents")
hybrid_pipeline.connect("joiner.documents", "ranker.documents")

# 执行混合检索
from haystack.components.embedders import SentenceTransformersTextEmbedder

embedder = SentenceTransformersTextEmbedder(model="BAAI/bge-large-zh-v1.5")
query_embedding = embedder.run(text="RAG 系统的文档存储选型")

result = hybrid_pipeline.run({
    "bm25_retriever": {"query": "RAG 文档存储选型"},
    "embedding_retriever": {"query_embedding": query_embedding["embedding"]},
    "ranker": {"query": "RAG 系统的文档存储选型"}
})
```

### 2.4 Milvus / Zilliz（推荐：超大规模场景）

Milvus 专为大规模向量检索设计，支持十亿级向量，适合有专门向量检索团队的企业。

```python
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility

# 连接 Milvus 集群
connections.connect(
    alias="default",
    host="milvus.cluster.internal",
    port="19530",
    user="root",
    password="Milvus",
)

# 定义 Schema
fields = [
    FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=100),
    FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768),
    FieldSchema(name="meta", dtype=DataType.JSON),
    FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=100),
]

schema = CollectionSchema(fields=fields, description="RAG document collection")

# 创建 Collection
collection_name = "rag_documents"
if utility.has_collection(collection_name):
    utility.drop_collection(collection_name)

collection = Collection(name=collection_name, schema=schema)

# 创建 HNSW 索引
index_params = {
    "metric_type": "COSINE",
    "index_type": "HNSW",
    "params": {"M": 16, "efConstruction": 200}
}
collection.create_index(field_name="embedding", index_params=index_params)

# 创建标量索引（加速过滤）
collection.create_index(field_name="category", index_name="category_idx")

# 加载到内存
collection.load()

# 插入数据
import random
entities = [
    [f"doc_{i}" for i in range(1000)],           # id
    [f"Content of document {i}" for i in range(1000)],  # content
    [[random.random() for _ in range(768)] for _ in range(1000)],  # embedding
    [{"source": "test", "author": "system"} for _ in range(1000)],  # meta
    ["tech" if i % 2 == 0 else "business" for i in range(1000)]    # category
]
collection.insert(entities)

# 搜索
search_params = {"metric_type": "COSINE", "params": {"ef": 64}}
results = collection.search(
    data=[[random.random() for _ in range(768)]],
    anns_field="embedding",
    param=search_params,
    limit=10,
    expr='category == "tech"',  # 标量过滤
    output_fields=["content", "meta"]
)
```

**Milvus 分区和分片：**

```python
# 按类别分区，查询时只扫描相关分区（大幅减少数据量）
from pymilvus import Partition

# 创建分区
collection.create_partition("partition_tech")
collection.create_partition("partition_business")
collection.create_partition("partition_legal")

# 插入到指定分区
collection.insert(entities, partition_name="partition_tech")

# 只在 tech 分区搜索
results = collection.search(
    data=[query_vector],
    anns_field="embedding",
    param=search_params,
    limit=10,
    partition_names=["partition_tech"],
    output_fields=["content"]
)
```

## 3. 生产级运维

### 3.1 从内存存储迁移到持久化存储

```python
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore
from haystack.components.embedders import SentenceTransformersDocumentEmbedder

def migrate_inmemory_to_qdrant(
    in_memory_store: InMemoryDocumentStore,
    qdrant_url: str,
    batch_size: int = 100
):
    """将内存存储中的数据迁移到 Qdrant"""

    # 创建目标存储
    target_store = QdrantDocumentStore(
        url=qdrant_url,
        index="migrated_documents",
        embedding_dim=768,
        similarity="cosine",
        recreate_collection=True,
    )

    # 获取所有文档（包括 embedding）
    all_docs = in_memory_store.filter_documents()
    total = len(all_docs)
    print(f"Migrating {total} documents...")

    # 分批写入
    for i in range(0, total, batch_size):
        batch = all_docs[i:i + batch_size]
        target_store.write_documents(batch)
        print(f"Migrated {min(i + batch_size, total)}/{total}")

    print("Migration complete!")
    return target_store
```

### 3.2 文档增量更新

生产环境中文档经常变更，需要支持增量更新而非全量重建。

```python
from haystack import Document
from datetime import datetime

class IncrementalDocumentManager:
    """支持增量更新的文档管理器"""

    def __init__(self, document_store):
        self.document_store = document_store

    def upsert_document(self, doc: Document):
        """插入或更新文档（基于 source_id 去重）"""
        source_id = doc.meta.get("source_id")
        if not source_id:
            raise ValueError("Document must have meta.source_id for upsert")

        # 查找已存在的文档
        existing = self.document_store.filter_documents({
            "field": "meta.source_id", "operator": "==", "value": source_id
        })

        if existing:
            # 更新：先删除旧版本，再写入新版本
            old_doc = existing[0]
            self.document_store.delete_documents([old_doc.id])
            doc.meta["version"] = old_doc.meta.get("version", 1) + 1
            doc.meta["updated_at"] = datetime.now().isoformat()
        else:
            doc.meta["version"] = 1
            doc.meta["created_at"] = datetime.now().isoformat()

        self.document_store.write_documents([doc])
        return doc

    def delete_by_source(self, source_id: str):
        """根据业务 ID 删除文档"""
        docs = self.document_store.filter_documents({
            "field": "meta.source_id", "operator": "==", "value": source_id
        })
        if docs:
            self.document_store.delete_documents([d.id for d in docs])
            return len(docs)
        return 0

    def get_document_history(self, source_id: str):
        """获取文档变更历史（需要配合外部数据库）"""
        # 实际生产中会配合 MongoDB/PostgreSQL 记录变更日志
        pass
```

### 3.3 批量写入与并发控制

```python
import concurrent.futures
from queue import Queue
import threading

class BulkDocumentIndexer:
    """并发批量索引器，带背压控制"""

    def __init__(self, document_store, max_workers=4, batch_size=200):
        self.document_store = document_store
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.error_queue = Queue()
        self.success_count = 0
        self.failed_count = 0
        self._lock = threading.Lock()

    def index(self, documents: list[Document]):
        """并发批量索引文档"""
        total = len(documents)
        batches = [
            documents[i:i + self.batch_size]
            for i in range(0, total, self.batch_size)
        ]

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers
        ) as executor:
            futures = {
                executor.submit(self._write_batch, batch): i
                for i, batch in enumerate(batches)
            }

            for future in concurrent.futures.as_completed(futures):
                batch_idx = futures[future]
                try:
                    count = future.result()
                    with self._lock:
                        self.success_count += count
                    print(f"Batch {batch_idx + 1}/{len(batches)}: {count} docs indexed")
                except Exception as e:
                    with self._lock:
                        self.failed_count += self.batch_size
                    self.error_queue.put((batch_idx, str(e)))
                    print(f"Batch {batch_idx + 1} failed: {e}")

        print(f"\nIndexing complete: {self.success_count} success, {self.failed_count} failed")
        return self.success_count, self.failed_count

    def _write_batch(self, batch: list[Document]) -> int:
        """写入一批文档"""
        self.document_store.write_documents(batch)
        return len(batch)

# 使用示例
indexer = BulkDocumentIndexer(document_store, max_workers=4, batch_size=200)
indexer.index(large_document_set)
```

### 3.4 数据备份与恢复

```python
import json
import gzip
from datetime import datetime

class DocumentStoreBackup:
    """文档存储备份工具"""

    def __init__(self, document_store):
        self.document_store = document_store

    def backup_to_file(self, filepath: str, compress: bool = True):
        """备份所有文档到文件"""
        docs = self.document_store.filter_documents()

        backup_data = {
            "timestamp": datetime.now().isoformat(),
            "count": len(docs),
            "documents": []
        }

        for doc in docs:
            backup_data["documents"].append({
                "id": doc.id,
                "content": doc.content,
                "meta": doc.meta,
                "embedding": doc.embedding.tolist() if hasattr(doc.embedding, 'tolist') else doc.embedding
            })

        if compress:
            with gzip.open(filepath, 'wt', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False)
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False)

        print(f"Backed up {len(docs)} documents to {filepath}")
        return len(docs)

    def restore_from_file(self, filepath: str, compress: bool = True):
        """从文件恢复文档"""
        if compress:
            with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                backup_data = json.load(f)
        else:
            with open(filepath, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)

        from haystack import Document
        import numpy as np

        documents = []
        for doc_data in backup_data["documents"]:
            doc = Document(
                id=doc_data["id"],
                content=doc_data["content"],
                meta=doc_data["meta"],
                embedding=np.array(doc_data["embedding"]) if doc_data.get("embedding") else None
            )
            documents.append(doc)

        # 清空并重建
        # 注意：生产环境应使用更安全的策略
        self.document_store.write_documents(documents)
        print(f"Restored {len(documents)} documents from {filepath}")
        return len(documents)
```

### 3.5 多租户隔离方案

```python
class MultiTenantDocumentStore:
    """基于元数据过滤的多租户隔离"""

    def __init__(self, document_store):
        self.document_store = document_store

    def get_tenant_filter(self, tenant_id: str):
        """生成租户过滤条件"""
        return {
            "field": "meta.tenant_id",
            "operator": "==",
            "value": tenant_id
        }

    def write_for_tenant(self, tenant_id: str, documents: list[Document]):
        """为指定租户写入文档"""
        for doc in documents:
            if "tenant_id" not in doc.meta:
                doc.meta["tenant_id"] = tenant_id
            elif doc.meta["tenant_id"] != tenant_id:
                raise ValueError(f"Document tenant mismatch")
        self.document_store.write_documents(documents)

    def query_for_tenant(self, tenant_id: str, query_embedding, top_k: int = 5):
        """为指定租户执行检索"""
        from haystack_integrations.components.retrievers.qdrant import QdrantEmbeddingRetriever

        retriever = QdrantEmbeddingRetriever(
            document_store=self.document_store,
            top_k=top_k,
            filters=self.get_tenant_filter(tenant_id)
        )
        return retriever.run(query_embedding=query_embedding)

    def delete_tenant_data(self, tenant_id: str):
        """删除某个租户的所有数据（GDPR 合规）"""
        docs = self.document_store.filter_documents(
            filters=self.get_tenant_filter(tenant_id)
        )
        if docs:
            self.document_store.delete_documents([d.id for d in docs])
        return len(docs)
```

## 4. 选型对比与决策树

### 4.1 横向对比

| 维度 | Qdrant | PostgreSQL+pgvector | Elasticsearch | Milvus |
|------|--------|---------------------|---------------|--------|
| **部署复杂度** | 低 | 极低（已有PG时） | 中 | 高 |
| **向量性能** | 高 | 中 | 中 | 极高 |
| **全文检索** | 支持（有限） | 支持（PG全文检索） | 极强 | 弱 |
| **混合检索** | 支持 | 需手动实现 | 原生支持 | 需配合其他系统 |
| **扩展性** | 良好 | 垂直扩展为主 | 极强 | 极强 |
| **数据一致性** | 最终一致 | 强一致 | 最终一致 | 最终一致 |
| **团队学习成本** | 低 | 极低 | 中 | 高 |
| **社区/生态** | 活跃 | 极广 | 极广 | 活跃 |

### 4.2 决策树

```
是否需要全文检索？
├─ 是 → 已有 ES 集群？
│       ├─ 是 → Elasticsearch（一票否决，平滑集成）
│       └─ 否 → 数据量 > 1000万？
│               ├─ 是 → Milvus + 独立全文检索（如 Meilisearch）
│               └─ 否 → Qdrant（内置稀疏向量支持全文）
│
└─ 否 → 已有 PostgreSQL？
        ├─ 是 → pgvector（最平滑，运维团队熟悉）
        └─ 否 → 数据量 > 1亿？
                ├─ 是 → Milvus（专为超大规模设计）
                └─ 否 → Qdrant（性能优秀，部署简单）
```

### 4.3 混合架构参考

超大规模生产环境中，单一数据库往往无法满足所有需求，常用混合架构：

```
┌─────────────────────────────────────────────────────┐
│                    API Gateway                       │
└─────────────────────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌────────────┐  ┌────────────┐  ┌────────────┐
    │  Qdrant    │  │    ES      │  │ PostgreSQL │
    │ (向量检索)  │  │ (全文检索)  │  │ (元数据/业务)│
    └──────┬─────┘  └──────┬─────┘  └──────┬─────┘
           │               │               │
           └───────────────┼───────────────┘
                           ▼
                    ┌────────────┐
                    │  Reranker  │
                    │  (合并结果) │
                    └────────────┘
```

## 5. 性能调优 Checklist

- [ ] **索引预热**：首次查询前执行一批 warm-up query，避免冷启动延迟
- [ ] **批量写入**：单条插入改为批量（100~500条/批），吞吐量提升 10~100 倍
- [ ] **Embedding 缓存**：相同文档的 embedding 计算结果缓存到 Redis
- [ ] **查询超时**：设置合理的 query timeout，防止长尾请求拖垮服务
- [ ] **连接池**：数据库连接使用连接池，避免频繁创建/销毁连接
- [ ] **监控告警**：核心指标（P99 延迟、QPS、内存使用率、磁盘使用率）接入 Prometheus
- [ ] **定期分析**：执行 `ANALYZE`（PG）或 `forcemerge`（ES），保持查询计划最优
- [ ] **数据清理**：设置文档 TTL，自动清理过期数据，避免无限增长

## 小结

本节系统讲解了生产级文档存储的实现：

- **核心概念** — HNSW 索引原理、距离度量、分片与副本
- **主流方案** — Qdrant、pgvector、Elasticsearch、Milvus 的实战配置
- **生产运维** — 迁移、增量更新、批量写入、备份恢复、多租户隔离
- **选型决策** — 根据团队现状和数据规模选择最合适的方案

## 实践练习

### 编程题
1. 使用 Docker Compose 部署 Qdrant + pgvector 双节点，分别写入 1 万条测试数据，对比两者的检索延迟（P50/P99）。
2. 实现一个支持租户隔离的 `DocumentStore` 包装类，确保租户 A 的查询不会返回租户 B 的数据。
3. 编写一个增量同步脚本，从 PostgreSQL 业务表读取变更，同步更新到 Qdrant 向量库。

### 思考题
1. HNSW 的 `ef` 参数在查询时动态调大和固定调大各有什么优劣？
2. 为什么 pgvector 在数据量超过 1000 万后性能会下降？可以从哪些维度优化？
3. 多租户场景下，用分区（Partition）隔离和用元数据过滤隔离，各自的适用场景是什么？

### 自测题
1. Cosine 相似度和 Dot Product 的区别是什么？什么情况下结果相同？
2. HNSW 索引的三个核心参数 `m`、`ef_construct`、`ef` 分别控制什么？
3. 已有 PostgreSQL 基础设施时，引入新向量数据库（如 Qdrant）的 trade-off 有哪些？

下一步将学习 LangChain Agent 开发（→ `langchain-agent/beginner/01-langchain-basics.md`）。
