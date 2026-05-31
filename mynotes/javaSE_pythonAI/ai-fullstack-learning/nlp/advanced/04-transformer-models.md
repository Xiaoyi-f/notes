# Transformer 模型深入

## 一、Transformer 架构详解

### 1. Transformer 原理

```python
import torch
import torch.nn as nn
import math
import torch.nn.functional as F

class PositionalEncoding(nn.Module):
    """正弦位置编码器"""

    def __init__(self, d_model, max_len=512, dropout=0.1):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)

        # 创建位置编码矩阵 (max_len, d_model)
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        # 计算频率项: 1 / 10000^(2i/d_model)
        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model)
        )
        # 偶数维度用 sin，奇数维度用 cos
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)  # (1, max_len, d_model)
        self.register_buffer('pe', pe)

    def forward(self, x):
        """
        x: [batch_size, seq_len, d_model]
        """
        x = x + self.pe[:, :x.size(1), :]
        return self.dropout(x)

# 标准位置编码公式:
# PE(pos, 2i)   = sin(pos / 10000^(2i/d_model))
# PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
#
# 其中:
# pos = 0, 1, 2, ..., max_len-1  (序列中的位置)
# i   = 0, 1, 2, ..., d_model/2-1 (嵌入维度索引)
# d_model = 嵌入总维度
```

### 2. 自注意力机制

```python
class MultiHeadAttention(nn.Module):
    """多头注意力机制"""

    def __init__(self, d_model, num_heads=8, dropout=0.1):
        super().__init__()
        assert d_model % num_heads == 0

        self.d_model = d_model
        self.num_heads = num_heads
        self.head_dim = d_model // num_heads
        self.scale = math.sqrt(self.head_dim)

        self.wq = nn.Linear(d_model, d_model)
        self.wk = nn.Linear(d_model, d_model)
        self.wv = nn.Linear(d_model, d_model)
        self.wo = nn.Linear(d_model, d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, query, key, value, mask=None):
        batch_size = query.size(0)

        # 1. 线性变换并分割多头
        Q = self.wq(query).view(batch_size, -1, self.num_heads, self.head_dim).transpose(1, 2)
        K = self.wk(key).view(batch_size, -1, self.num_heads, self.head_dim).transpose(1, 2)
        V = self.wv(value).view(batch_size, -1, self.num_heads, self.head_dim).transpose(1, 2)

        # 2. 缩放点积注意力
        scores = torch.matmul(Q, K.transpose(-2, -1)) / self.scale

        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-inf'))

        attn_weights = F.softmax(scores, dim=-1)
        attn_weights = self.dropout(attn_weights)

        # 3. 加权求和
        attn_output = torch.matmul(attn_weights, V)

        # 4. 合并多头并通过输出投影
        attn_output = attn_output.transpose(1, 2).contiguous().view(batch_size, -1, self.d_model)
        output = self.wo(attn_output)

        return output, attn_weights
```

### 3. 编码器类型

```python
from transformers import AutoModel, AutoTokenizer

# 1. BERT 编码器（双向编码器）
bert_model = AutoModel.from_pretrained("bert-base-chinese")
bert_tokenizer = AutoTokenizer.from_pretrained("bert-base-chinese")

# 文本编码
text = "这是一段中文文本。"
encoded = bert_tokenizer(text, return_tensors="pt",
                                 padding=True, truncation=True)
with torch.no_grad():
    # [batch_size, seq_len, hidden_size]
    output = bert_model(**encoded)
    last_hidden_state = output.last_hidden_state  # [CLS] token 的表示

# 2. GPT 系列编码器
gpt_model = AutoModelForCausalLM.from_pretrained("gpt2")
gpt_tokenizer = AutoTokenizer.from_pretrained("gpt2")

text = "The quick brown fox jumps over the lazy dog."
inputs = gpt_tokenizer(text, return_tensors="pt")
with torch.no_grad():
    outputs = gpt_model.generate(
        **inputs,
        max_length=50,
        num_return_sequences=1
    )
    print(gpt_tokenizer.decode(outputs[0]))

# 3. T5 编码器（生成式编码器）
t5_model = AutoModel.from_pretrained("google/flan-t5-small")
t5_tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")

# 文本摘要
text = "机器学习是人工智能的子领域"
inputs = t5_tokenizer("summarize: " + text, return_tensors="pt",
                          max_length=512)
outputs = t5_model.generate(**inputs)
print(t5_tokenizer.decode(outputs[0]))
```

### 4. 位置编码详解

```python
import torch
import torch.nn as nn
import math

class LearnedPositionalEncoding(nn.Module):
    """可学习的位置编码"""

    def __init__(self, max_len=512, d_model=512, dropout=0.1):
        super().__init__()
        self.dropout = nn.Dropout(dropout)

        # 可学习的位置嵌入
        self.pos_embedding = nn.Embedding(max_len, d_model)

    def forward(self, x):
        # x: [batch_size, seq_len, d_model]
        seq_len = x.size(1)
        positions = torch.arange(seq_len, device=x.device).unsqueeze(0)
        pos_emb = self.pos_embedding(positions)  # [1, seq_len, d_model]
        x = x + pos_emb
        return self.dropout(x)
```

## 二、高级嵌入技术

### 1. 向量数据库对比

```python
from sentence_transformers import SentenceTransformer, util
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import time

# 加载模型
models = {
    "all-MiniLM-L6-v2": "sentence-transformers/all-MiniLM-L6-v2",
    "paraphrase-multilingual": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    "all-mpnet-base": "sentence-transformers/all-mpnet-base-v2",
    "bge-small-zh": "BAAI/bge-small-zh-v1.5",
}

# 测试模型
results = {}
sentences = [
    "今天天气很好",
    "这个产品很不错",
    "系统性能优秀"
]

for model_name, model_path in models.items():
    print(f"\n测试模型: {model_name}")

    model = SentenceTransformer(model_path)

    # 编码句子
    embeddings = model.encode(sentences)

    # 计算相似度矩阵
    similarity_matrix = cosine_similarity(embeddings)
    print(f"相似度矩阵:\\n{np.round(similarity_matrix, 3)}")

    # 计算平均相似度
    avg_similarities = []
    for i in range(len(sentences)):
        for j in range(len(sentences)):
            if i != j:
                avg_similarities.append(similarity_matrix[i][j])

    print(f"平均相似度: {np.mean(avg_similarities):.3f}")
    results[model_name] = {
        "avg_similarity": np.mean(avg_similarities),
        "matrix": similarity_matrix.tolist()
    }

    # 性能测试
    import time
    start = time.time()
    for _ in range(100):
        model.encode(sentences)
    time_cost = time.time() - start
    print(f"编码100次耗时: {time_cost*1000:.2f}ms")
```

### 2. 向量数据库实现

```python
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Optional, Dict
import uuid

class VectorDatabase:
    """向量数据库封装（基于 ChromaDB）"""

    def __init__(self, collection_name: str, persist_dir: str = "./chroma_db"):
        self.collection_name = collection_name

        # 连接 ChromaDB
        self.client = chromadb.PersistentClient(path=persist_dir)

        # 获取或创建集合
        try:
            self.collection = self.client.get_collection(name=collection_name)
            print(f"使用已存在集合: {collection_name}, 文档数: {self.collection.count()}")
        except Exception:
            print(f"创建新集合: {collection_name}")
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": f"{collection_name} 集合"}
            )

    def add_documents(self, texts: List[str], metadatas: List[Dict] = None,
                      embeddings: List = None, ids: List[str] = None):
        """添加文档到向量数据库"""
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in texts]
        if metadatas is None:
            metadatas = [{} for _ in texts]

        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings,
            ids=ids
        )
        return ids

    def search(self, query: str, n_results: int = 5,
               where: Dict = None) -> List[Dict]:
        """搜索最相似的文档"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where
        )

        formatted = []
        for i in range(len(results["ids"][0])):
            formatted.append({
                "id": results["ids"][0][i],
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                "distance": results["distances"][0][i] if results["distances"] else None
            })
        return formatted

    def delete_document(self, doc_id: str):
        """删除文档"""
        self.collection.delete(ids=[doc_id])

    def count(self) -> int:
        """获取文档数量"""
        return self.collection.count()

# 使用示例
db = VectorDatabase("my_knowledge_base")
db.add_documents(
    texts=["Python 是一种编程语言", "机器学习是AI的一个分支"],
    metadatas=[{"source": "wiki"}, {"source": "textbook"}]
)
results = db.search("什么是Python")
print(f"找到 {len(results)} 个结果")
for r in results:
    print(f"  [{r['id']}] {r['content'][:50]}...")
```

### 3. Pinecone 高级用法

```python
from pinecone import Pinecone, ServerlessSpec
import os

# 初始化 Pinecone
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

# 创建 Serverless 索引
index_name = "docs-index"
if index_name not in [idx["name"] for idx in pc.list_indexes()]:
    pc.create_index(
        name=index_name,
        dimension=1536,  # OpenAI ada-002
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )

# 连接索引
index = pc.Index(index_name)

# 添加向量
vectors = [
    {
        "id": "doc-1",
        "values": [0.1] * 1536,  # 实际的 embedding 向量
        "metadata": {"title": "文档1", "category": "tech"}
    },
    {
        "id": "doc-2",
        "values": [0.2] * 1536,
        "metadata": {"title": "文档2", "category": "science"}
    }
]
index.upsert(vectors=vectors)

# 查询
query_vector = [0.15] * 1536  # 实际应使用 embedding 模型生成
results = index.query(
    vector=query_vector,
    top_k=5,
    include_metadata=True
)

# 处理结果
formatted = [{
    "id": match["id"],
    "score": match["score"],
    "metadata": match.get("metadata", {})
} for match in results["matches"]]

for r in formatted:
    print(f"ID: {r['id']}, Score: {r['score']:.4f}")
```

### 4. Weaviate 向量数据库

```python
import weaviate
from weaviate.classes.config import Configure, Property, DataType

# 连接 Weaviate
client = weaviate.connect_to_local()

# 创建 Collection
try:
    client.collections.delete("Documents")
except Exception:
    pass

collection = client.collections.create(
    name="Documents",
    properties=[
        Property(name="content", data_type=DataType.TEXT),
        Property(name="source", data_type=DataType.TEXT),
    ],
    vectorizer_config=Configure.Vectorizer.none()
)

# 添加文档（先使用外部模型生成 embedding）
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("BAAI/bge-small-zh-v1.5")

documents = [
    {"content": "Python 是一种高级编程语言", "source": "wiki"},
    {"content": "机器学习是人工智能的重要分支", "source": "textbook"},
]

with collection.batch.dynamic() as batch:
    for doc in documents:
        embedding = model.encode(doc["content"]).tolist()
        batch.add_object(
            properties=doc,
            vector=embedding
        )

# 语义搜索
query = "什么是编程语言"
query_vector = model.encode(query).tolist()
results = collection.query.near_vector(
    near_vector=query_vector,
    limit=3
)

for obj in results.objects:
    print(f"内容: {obj.properties['content']}")
    print(f"来源: {obj.properties.get('source', 'unknown')}")
    print(f"距离: {obj.metadata.distance:.4f}\n")

client.close()
```

## 三、高级 Agent 技术

### 1. 记忆管理

```python
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import Any, Dict

class ConversationMemory:
    """对话记忆管理"""

    def __init__(self, max_turns: int = 10):
        self.max_turns = max_turns
        self.memories = defaultdict(list)
        self.current_session_id = None

    def save_message(self, session_id: str, message: Tuple[str, str]):
        """保存消息到记忆"""
        self.memories[session_id].append(message)

        # 限制记忆数量
        if len(self.memories[session_id]) > self.max_turns:
            self.memories[session_id].pop(0)

    def get_recent_messages(self, session_id: str, n: int = 5) -> List[Tuple[str, str]]:
        """获取最近的对话"""
        return self.memories[session_id][-n:]

    def get_conversation_summary(self, session_id: str) -> str:
        """生成对话摘要"""
        messages = self.memories.get(session_id, [])
        if not messages:
            return ""

        summary_prompt = f"""
        总结以下对话：
        {chr(10).join([f"{user}: {response}" for user, response in messages])}

        对话摘要：
        """

        # 使用 LLM 生成摘要
        summary = llm.invoke(summary_prompt)
        return summary.content

    def clear_memory(self, session_id: str):
        """清空记忆"""
        if session_id in self.memories:
            del self.memories[session_id]
```

### 2. 长期记忆

```python
from typing import List, Dict
import json
import hashlib
from datetime import datetime

class LongTermMemory:
    """长期记忆 - 持久化到数据库"""

    def __init__(self, db_connection_string: str):
        self.db_connection_string = db_connection_string
        self._init_db()

    def _init_db(self):
        import sqlite3
        self.conn = sqlite3.connect(self.db_connection_string)
        self.cursor = self.conn.cursor()

        # 创建记忆表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS long_term_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                category TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                relevance REAL DEFAULT 1.0,
                accessed_count INTEGER DEFAULT 0
            )

            CREATE INDEX IF NOT EXISTS idx_lt_memory_session_category ON long_term_memory(session_id, category);
            CREATE INDEX IF NOT EXISTS idx_lt_memory_question ON long_term_memory(question);
            CREATE INDEX IF NOT EXISTS idx_lt_memory_relevance ON long_term_memory(relevance);
            CREATE INDEX IF NOT EXISTS idx_lt_memory_accessed_count ON long_term_memory(accessed_count);
        """)

        self.conn.commit()

    def add_memory(self, session_id: str, question: str, answer: str,
                     category: str = None, tags: List[str] = None):
        """添加长期记忆"""
        tags_str = json.dumps(tags or [], ensure_ascii=False)

        self.cursor.execute("""
            INSERT INTO long_term_memory
            (session_id, question, answer, category, tags)
            VALUES (?, ?, ?, ?, ?)
        """, (session_id, question, answer, category, tags_str))

        self.conn.commit()

    def search_memory(self, session_id: str, query: str, top_k: int = 5) -> List[Dict]:
        """搜索相关记忆"""
        # 使用全文检索
        self.cursor.execute("""
            SELECT id, question, answer, category, tags, created_at, relevance
            FROM long_term_memory
            WHERE session_id = ?
            AND question LIKE ?
            OR answer LIKE ?
            OR tags LIKE ?
            ORDER BY relevance DESC, created_at DESC
            LIMIT ?
        """, (session_id, f"%{query}%", f"%{query}%", f"%{query}%"))

        rows = self.cursor.fetchall()

        return [{
            "id": row[0],
            "question": row[1],
            "answer": row[2],
            "category": row[3],
            "tags": json.loads(row[4]) if row[4] else [],
            "created_at": row[5],
            "relevance": row[6],
            "accessed_count": row[7]
        } for row in rows]

    def get_statistics(self, session_id: str) -> Dict:
        """获取记忆统计"""
        self.cursor.execute("""
            SELECT
                COUNT(*) as total,
                COUNT(DISTINCT category) as categories,
                COUNT(DISTINCT tags) as tag_count,
                AVG(relevance) as avg_relevance,
                MAX(accessed_count) as max_accessed
            FROM long_term_memory
            WHERE session_id = ?
        """, (session_id,))

        row = self.cursor.fetchone()
        if row:
            return {
                "total": row[0],
                "categories": row[1],
                "tag_count": row[2],
                "avg_relevance": float(row[3]) if row[3] else 0,
                "max_accessed": row[4]
            }
        return {"total": 0}
```

### 3. Agent 协作模式

```python
from typing import List, Dict
import asyncio

class MultiAgent:
    """多 Agent 协作"""

    def __init__(self, agents: Dict[str, Callable], llm):
        self.agents = agents
        self.llm = llm
        self.agent_history = {}

    async def run(self, query: str) -> Dict:
        """运行多 Agent 协作"""
        current_query = query
        agent_trail = []

        for attempt in range(3):  # 最多3次尝试
            print(f"=== 第 {attempt + 1} 次尝试 ===")

            # 让每个 Agent 处理查询
            tasks = []
            for name, agent in self.agents.items():
                task = agent(current_query)
                tasks.append((name, task))

            # 并行执行
            results = await asyncio.gather(
                *[task[1] for task in tasks]
            )

            # 分析结果
            result = self._analyze_results(results, current_query, tasks)
            print(f"\n分析结果: {result}")

            if result["complete"]:
                return result["answer"]

            # 如果不完整，生成下一个查询
            next_query = result["next_query"]
            if next_query == current_query:
                print("Agent 无法解决问题，结束")
                return {"answer": "抱歉，我无法回答这个问题。"}
            current_query = next_query

        return {"answer": "抱歉，我无法回答这个问题。"}

    def _analyze_results(self, results: List, current_query: str,
                          tasks: List) -> Dict:
        """分析多个 Agent 的结果"""
        # 检查是否有 Agent 认为完成
        complete_count = sum(1 for _, result in results if result.get("status") == "complete")

        if complete_count > 0:
            return results[0][1]

        # 如果没有完成，合并所有结果并生成新查询
        combined_results = []
        for name, result in results:
            if result.get("status") != "failed":
                combined_results.append(result.get("partial_answer", ""))

        return {
            "complete": False,
            "partial_answer": "；".join(combined_results),
            "next_query": self._generate_next_query(current_query, results, tasks)
        }

    def _generate_next_query(self, query: str, results: List, tasks: List) -> str:
        """生成下一个查询"""
        # 根据前一轮结果和原始问题生成下一个更具体的问题
        agent_summaries = "\n".join([
            f"{name} 结果: {result}"
            for (name, _), result in zip(tasks, results)
        ])
        prompt = f"""
        前面几个助手都没有解决以下问题：
        问题：{query}
        {agent_summaries}

        请基于以上信息，生成一个更具体的问题，帮助助手们更好地理解你的需求：
        """

        result = self.llm.invoke(prompt)
        return result.content.strip()
```

## 四、项目实战扩展

### 1. 智能客服系统

```python
from typing import List, Dict, Optional
import json

class IntelligentCustomerService:

    def __init__(self):
        self.knowledge_base = self._load_knowledge_base()
        self.conversation_memory = ConversationMemory()
        self.order_service = OrderService()

    def _load_knowledge_base(self) -> Dict:
        """加载知识库"""
        return {
            "faq": [
            {
                "question": "如何重置密码？",
                "answer": "在设置页面点击'重置密码'，按照提示操作即可。"
            },
            {
                "question": "如何退款？",
                "answer": "在订单详情页面点击'申请退款'，填写原因后提交，客服会在1-3个工作日处理。"
            },
            {
                "question": "如何联系客服？",
                "answer": "点击页面底部的'在线客服'或拨打400-12345678。"
            },
            {
                "question": "支持哪些支付方式？",
                "answer": "支持支付宝、微信、银行卡、花呗、京东支付。"
            }
        ],
            "products": [
            {"id": "p001", "name": "产品A", "price": 99.00},
            {"id": "p002", "name": "产品B", "price": 199.00},
            {"id": "p003", "name": "产品C", "price": 299.00}
        ],
            "policies": {
                "return_policy": "7天无理由退货",
                "shipping_policy": "满99元包邮",
                "customization_time": "1-3天"
            }
        }

    async def handle_query(self, user_message: str, user_id: str) -> str:
        """处理用户查询"""
        print(f"\n用户: {user_id}")
        print(f"查询: {user_message}")

        # 1. 意图理解
        intent = self._classify_intent(user_message)
        print(f"\n意图: {intent}")

        # 2. 知识库检索
        kb_answers = self._search_knowledge_base(intent, user_message)

        if kb_answers:
            return self._format_kb_response(kb_answers)

        # 3. 使用 RAG 检索
        rag_result = await self._rag_search(user_message)
        if rag_result:
            return rag_result

        # 4. LLM 生成
        return await self._llm_generate(user_message, kb_answers, rag_result)

    def _classify_intent(self, message: str) -> str:
        """意图分类"""
        prompt = f"""
        将以下用户问题分类为以下类别之一：

        类别：
        - 订单相关（查询、创建、修改、取消、退款等）
        - 产品相关（查询、比较、推荐等）
        - 账户相关（登录、密码、个人信息等）
        - 其他

用户问题：{message}

只返回类别，不要其他内容。
        """

        result = llm.invoke(prompt)
        return result.content.strip()

    def _search_knowledge_base(self, intent: str, message: str) -> Optional[str]:
        """搜索知识库"""
        intent_keywords = {
            "订单相关": ["订单", "退款", "发货", "查询"],
            "产品相关": ["产品", "推荐", "价格", "功能"],
            "客户相关": ["登录", "密码", "账号", "信息"]
        }

        for intent_type, keywords in intent_keywords.items():
            if any(keyword in message for keyword in keywords):
                faq_answers = [q["answer"] for q in self.knowledge_base["faq"] if keyword in q["question"]]
                return faq_answers[0] if faq_answers else None

        return None

    async def _rag_search(self, message: str) -> str:
        """RAG 搜索"""
        # 构建查询管道
        pipeline = Pipeline()

        pipeline.add_component("retriever", rag_retriever)
        pipeline.add_component("prompt_builder", PromptBuilder(template=RAG_TEMPLATE))
        pipeline.add_component("llm", OpenAIGenerator(model="gpt-4"))

        # 执行 RAG 查询
        rag_result = pipeline.run({"retriever": {"query": message}})

        return rag_result["llm"]["replies"][0]

    def _format_kb_response(self, answers: List[str]) -> str:
        """格式化知识库响应"""
        if not answers:
            return "抱歉，没有找到相关信息。"

        if len(answers) == 1:
            return answers[0]
        else:
            return "\\n".join([f"{i+1}. {ans}" for i, ans in enumerate(answers)])

    async def _llm_generate(self, user_message: str, kb_answers: List[str],
                           rag_result: str = "") -> str:
        """使用 LLM 生成回答"""
        template = f"""
用户问题：{user_message}

参考信息：
{kb_str}

{rag_str}

请基于以上信息提供准确、有帮助的回答。如果不确定信息，就说"抱歉，我需要更多信息"。
"""

        # 组合参考信息
        kb_str = "\\n\\n".join([
            f"参考1: {kb_answers[0] if kb_answers else '无'}",
            f"参考2: {rag_result if rag_result else '无'}"
        ])

        result = llm.invoke(template.format(kb_str=kb_str, rag_str=rag_str))
        return result.content
```

### 2. 图知识问答系统

```python
from typing import List, Tuple, Optional
from langchain.chains import GraphCypherChain
from langchain_community.graphs import Neo4jGraph
from langchain_experimental.graphs import Neo4jGraphQuery

class GraphQA:
    """图知识问答"""

    def __init__(self):
        # 创建图数据库
        self.graph = Neo4jGraph()

        # 添加节点
        self._add_graph_nodes()

    def _add_graph_nodes(self):
        # 人物节点
        entities = [
            ("张三", "人物", "软件工程师", "TechCorp", 2020-01"),
            ("李四", "人物", "产品经理", "TechCorp", "2018-03"),
            ("王五", "人物", "前端开发", "TechCorp", "2021-06"),
            ("TechCorp", "组织", "科技公司", "北京", "2015-01"),
            ("北京", "地点", "中国首都", "", ""),
            ("上海", "地点", "中国城市", ""),
        ]

        # 添加节点到图
        for entity in entities:
            self.graph.add_node(entity[0], {"name": entity[0], "type": entity[1]})
            if len(entity) > 4:
                self.graph.add_node(entity[4], {"name": entity[4], "type": entity[5]})

        # 添加关系
        self._add_graph_edges()

    def _add_graph_edges(self):
        # 添加边
        edges = [
            ("张三", "工作于", "TechCorp"),
            ("李四", "工作于", "TechCorp"),
            ("王五", "工作于", "TechCorp"),
            ("TechCorp", "位于", "北京"),
            ("张三", "同事", "李四"),
            ("李四", "同事", "王五"),
            ("王五", "同学", "赵六"),
            ("赵六", "同学", "张三"),
        ]

        for src, rel, dst in edges:
            # 查找节点ID
            src_id = self._find_node_id(src)
            dst_id = self._find_node_id(dst)
            if src_id and dst_id:
                self.graph.add_edge(src_id, dst_id, relation=rel)

    def _find_node_id(self, name: str) -> Optional[int]:
        """根据名称查找节点ID"""
        for node in self.graph.nodes(data=True):
            if node.get("name") == name:
                return node.id
        return None

    def query_graph(self, question: str) -> str:
        """图知识问答"""
        # 使用 Cypher 查询
        query_chain = GraphCypherChain(llm=ChatOpenAI(model="gpt-4"), graph=self.graph)

        result = query_chain.invoke({"query": question})
        return result["result"]
```

## 小结

本节补充了重要的高级内容：

- **Transformer** - 架构原理、位置编码、自注意力、编码器类型
- **向量数据库** - Pinecone、Weaviate 实战
- **Agent 高级** - 记忆管理、多Agent 协作、长程记忆
- **图问答系统** - 知识图谱问答、Neo4j 实战
- **智能客服** - 完整的客服系统实现

## 实践练习

### 编程题
1. 使用 ChromaDB 搭建一个本地的向量检索系统：包含文档添加、语义搜索、基于元数据的过滤搜索功能。
2. 实现一个带有长期记忆的对话 Agent：能将重要信息持久化到 SQLite，下次对话时自动检索相关记忆。

### 思考题
1. 向量数据库选择时，ChromaDB、Pinecone、Weaviate 各适合什么场景？
2. 长期记忆和短期记忆在 Agent 系统中的分工是什么？如何判断哪些信息应该进入长期记忆？

### 自测题
1. 正弦位置编码和可学习位置编码各有什么优缺点？
2. 多头注意力中，不同"头"学习到的是什么？
3. 多 Agent 协作中，如何解决 Agent 之间的信息冲突？

下一步回顾整个 AI 全栈学习路径，开始项目实战练习。