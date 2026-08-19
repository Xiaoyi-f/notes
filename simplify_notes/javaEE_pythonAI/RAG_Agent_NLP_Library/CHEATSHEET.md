# AI 全栈速查表

## RAG 系统核心流程
```
文档加载 → 文档处理(分块/清洗) → 嵌入(Embedding) → 存储(VectorDB)
                                                          ↓
用户问题 → 嵌入 → 检索(Retriever) → 重排序(Reranker) → LLM 生成 → 答案
```

## Haystack 核心组件速查

| 组件 | 类 | 关键参数 |
|------|-----|----------|
| 文档存储 | `InMemoryDocumentStore` / `ElasticsearchDocumentStore` | `embedding_dim`, `similarity` |
| 嵌入器 | `SentenceTransformersDocumentEmbedder` | `model="all-MiniLM-L6-v2"` |
| 检索器 | `InMemoryEmbeddingRetriever` / `InMemoryBM25Retriever` | `top_k=5` |
| 生成器 | `OpenAIGenerator` / `AnthropicGenerator` | `model="gpt-4"` |
| 分块器 | `DocumentSplitter` | `split_length=200, split_overlap=20` |
| 排序器 | `TransformersSimilarityRanker` | `model="BAAI/bge-reranker-base"` |

## LangChain 核心组件

| 组件 | 说明 | 关键类/方法 |
|------|------|------------|
| LLM | 模型调用 | `ChatOpenAI(model="gpt-4")` |
| Prompt | 提示模板 | `PromptTemplate`, `ChatPromptTemplate` |
| Chain | 组件串联 | `LLMChain`, `SequentialChain`, `RouterChain` |
| Agent | 自主决策 | `initialize_agent()`, `AgentExecutor` |
| Memory | 对话记忆 | `ConversationBufferMemory`, `ConversationSummaryMemory` |
| Tool | 工具调用 | `Tool(name, func, description)` |
| Parser | 输出解析 | `PydanticOutputParser`, `StructuredOutputParser` |

## RAG 优化策略速查

| 策略 | 说明 | 适用场景 |
|------|------|----------|
| **HyDE** | 先生成假设答案再检索 | 查询与文档语义差距大 |
| **CoT RAG** | 逐步推理 + 检索 | 复杂多步推理问题 |
| **ReAct RAG** | 推理+行动循环 | 需要多轮检索的场景 |
| **GraphRAG** | 知识图谱增强检索 | 实体关系密集的领域 |
| **查询扩展** | 生成多个查询变体 | 召回率不足 |
| **混合检索** | BM25 + 向量检索 | 需要兼顾关键词和语义 |

## 推荐嵌入模型

| 模型 | 维度 | 语言 | 推荐场景 |
|------|------|------|----------|
| `all-MiniLM-L6-v2` | 384 | 英文 | 通用英文 |
| `all-mpnet-base-v2` | 768 | 英文 | 高质量英文 |
| `paraphrase-multilingual-MiniLM-L12-v2` | 384 | 多语言 | 中文/多语言 |
| `BAAI/bge-small-zh-v1.5` | 512 | 中文 | 中文场景首选 |
| `BAAI/bge-large-zh-v1.5` | 1024 | 中文 | 高精度中文 |
| `text-embedding-3-small` | 512 | 多语言 | OpenAI 嵌入 |

## 知识图谱速查

| 概念 | 说明 |
|------|------|
| RDF 三元组 | (主体, 谓词, 客体) → (张三, 朋友, 李四) |
| Neo4j | 图数据库，Cypher 查询语言 |
| NetworkX | Python 图算法库 |
| 推理类型 | 规则推理、路径推理、嵌入推理(TransE) |
| TransE | h + r ≈ t（头实体+关系≈尾实体） |

## NLP 核心任务速查

| 任务 | 方法 | 模型/工具 |
|------|------|----------|
| 分词 | 规则/统计 | jieba, nltk |
| 文本表示 | BoW/TF-IDF/Embedding | TfidfVectorizer, SentenceTransformer |
| 文本分类 | 传统ML/深度学习 | 朴素贝叶斯, BERT |
| NER | 规则/深度学习 | `ckiplab/bert-base-chinese-ner` |
| 文本生成 | Transformer | GPT, Llama, ChatGLM |
| 微调 | LoRA/QLoRA | PEFT, bitsandbytes |

## 常用 API 命令速查

```python
# Haystack Pipeline
pipeline = Pipeline()
pipeline.add_component("retriever", retriever)
pipeline.add_component("llm", generator)
pipeline.connect("retriever", "llm")
result = pipeline.run({"retriever": {"query": "问题"}})

# LangChain Chain
chain = prompt | llm | output_parser
result = chain.invoke({"input": "问题"})

# ChromaDB 查询
collection.query(query_texts=["问题"], n_results=5)

# Embedding
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(["文本1", "文本2"])
```

## 面试高频 10 问

1. **RAG 是什么？** 检索增强生成，先检索相关文档再交给 LLM 生成答案
2. **RAG vs 微调？** RAG 实时外挂知识、低成本；微调改变模型参数、高成本
3. **Haystack Pipeline 原理？** 组件化管道，通过 connect() 串联各组件
4. **BM25 vs 向量检索？** BM25 关键词匹配，向量检索语义匹配
5. **如何评估 RAG？** 忠实度(Faithfulness)、答案相关性、检索精度/召回
6. **Agent 工作原理？** 思考→行动→观察 循环，自主选择工具完成任务
7. **知识图谱 vs 向量DB？** KG 存结构化关系，VectorDB 存语义向量
8. **LoRA 原理？** 低秩分解，只训练少量参数，大幅降低微调成本
9. **ChromaDB vs Pinecone？** ChromaDB 本地免费；Pinecone 云端托管
10. **嵌入维度选择？** 精度越高维度越大，384d 够用，1536d 高精度
