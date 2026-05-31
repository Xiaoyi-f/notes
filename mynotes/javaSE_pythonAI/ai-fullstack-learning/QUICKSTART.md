# 快速开始指南

## 🚀 15分钟快速体验

### Python AI - 快速体验 RAG

```python
# 安装
pip install haystack-ai sentence-transformers openai langchain-community

# 第一行代码 RAG
from haystack import Pipeline, Document
from haystack.components.retrievers import InMemoryEmbeddingRetriever
from haystack.components.generators import OpenAIGenerator
from haystack.document_stores.in_memory import InMemoryDocumentStore

# 1. 创建文档
documents = [
    Document(content="Python是一种高级编程语言，由Guido van Rossum创建于1991年。"),
    Document(content="JavaScript是一种脚本语言，主要用于网页开发。"),
    Document(content="Java是一种面向对象的编程语言，由Sun Microsystems开发。"),
]

# 2. 创建索引
doc_store = InMemoryDocumentStore()
for doc in documents:
    doc_store.write_documents([doc])

# 3. 创建 RAG pipeline
pipeline = Pipeline()

pipeline.add_component("embedder", SentenceTransformersDocumentEmbedder(model="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"))
pipeline.add_component("writer", DocumentWriter(document_store=doc_store))

pipeline.run({"embedder": {"documents": documents}})

# 4. 查询
retriever = InMemoryEmbeddingRetriever(document_store=doc_store, top_k=2)
llm = OpenAIGenerator(model="gpt-4")

question = "Python是由谁创建的？"
embedding = SentenceTransformersTextEmbedder(model="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2").run(text=question)

results = retriever.run(query_embedding=embedding["embedding"])
context = "\\n".join([doc.content for doc in results["documents"]])

response = llm.invoke(f"基于以下信息回答问题：\\n{context}\\n\\n问题：{question}")

print(response.content)
```

### LangChain Agent - 快速体验

```python
# 安装
pip install langchain langchain-openai

from langchain.agents import initialize_agent, Tool
from langchain.tools import Tool
import os

# 设置 API Key
os.environ["OPENAI_API_KEY"] = "your-api-key"

# 定义工具
def search_web(query: str) -> str:
    """搜索网络信息"""
    # 实际应用中调用搜索 API
    return f"搜索 '{query}' 的结果..."

def calculate(expression: str) -> str:
    """计算数学表达式"""
    try:
        result = eval(expression)
        return f"{expression} = {result}"
    except:
        return f"无法计算 {expression}"

# 创建工具列表
tools = [
    Tool(
        name="搜索",
        func=search_web,
        description="搜索网络信息，输入查询词"
    ),
    Tool(
        name="计算器",
        func=calculate,
        description="计算数学表达式，输入数学表达式"
    )
]

# 创建 Agent
agent = initialize_agent(
    tools=tools,
    llm=ChatOpenAI(model="gpt-4"),
    agent="zero-shot-react-description",
    verbose=True
)

# 使用 Agent
result = agent.run("Python + 10 的结果是多少？并且搜索 Python 最新的版本")
print(result["output"])
```

## 📚 完整学习路径

我已经为你创建了完整的学习文件，包含以下内容：

### Python AI 技术栈 (ai-fullstack-learning/)

```
ai-fullstack-learning/
├── haystack-ai/          # Haystack RAG
│   ├── beginner/
│   │   ├── 01-haystack-basics.md
│   │   ├── 02-document-processing.md
│   │   └── 03-retrieval-techniques.md
│   ├── intermediate/
│   │   └── 04-rag-advanced.md
│   └── advanced/
│       └── 05-production-rag.md
│
├── langchain-agent/       # LangChain Agent
│   ├── beginner/
│   │   ├── 01-langchain-basics.md
│   │   └── 02-langchain-tools.md
│   ├── intermediate/
│   │   └── 03-langchain-agents.md
│   └── advanced/
│       └── 04-langchain-production.md
│
├── knowledge-graph/      # 知识图谱
│   ├── beginner/
│   │   └── 01-knowledge-graph-basics.md
│   ├── intermediate/
│   │   └── 02-knowledge-graph-reasoning.md
│   └── advanced/
│       └── 03-graph-rag.md
│
└── nlp/                 # NLP
    ├── beginner/
    │   └── 01-nlp-basics.md
    ├── intermediate/
    │   └── 02-nlp-advanced.md
    └── advanced/
        └── 03-project-practice.md
```

### Java 全栈技术栈 (java-fullstack-learning/)

```
java-fullstack-learning/
├── javase/              # Java SE
│   ├── beginner/
│   │   └── 01-java-se-basics.md
│   ├── intermediate/
│   │   ├── 02-java-se-collections.md
│   │   ├── 03-java-se-advanced.md
│   │   └── 04-java-concurrency.md
│   └── advanced/
│       └── 05-jvm.md
│
├── javaweb/             # Java Web
│   └── beginner/
│       └── 01-servlet-jsp.md
│
├── spring/              # Spring Framework
│   └── beginner/
│       └── 01-spring-framework.md
│
├── spring-boot/          # Spring Boot
│   └── beginner/
│       └── 01-spring-boot-basics.md
│
├── spring-cloud-alibaba/ # Spring Cloud Alibaba
│   └── beginner/
│       └── 01-spring-cloud-alibaba.md
│
├── redis/               # Redis 缓存
│   └── beginner/
│       └── 01-redis-basics.md
│
├── mq/                  # 消息队列
│   └── beginner/
│       └── 01-message-queue.md
│
├── performance/          # 性能优化
│   └── advanced/
│       └── 02-optimization.md
│
└── project/             # 项目实战
    └── beginner/
        └── 01-ecommerce-project.md
```

### 总览文件

- `ai-fullstack-learning/README.md` - AI 技术栈学习路径总览
- `java-fullstack-learning/README.md` - Java 全栈学习路径总览

## 🎯 学习重点

### Python AI 核心

1. **Haystack RAG** - 文档检索与生成
2. **LangChain Agent** - 智能代理开发
3. **知识图谱** - 图数据库构建与推理
4. **NLP 高级** - LLM 微调、提示工程

### Java 全栈核心

1. **Java SE** - 基础、集合、多线程、JVM
2. **Spring 全家桶** - 框架、Boot、Cloud
3. **中间件** - Redis、消息队列、监控
4. **系统设计** - 微服务、分布式、性能

## 🚀 现在就开始

1. 查看对应目录的学习笔记
2. 按照学习路径循序渐进
3. 每个技术点都要动手实践
4. 完成实战项目巩固知识

## 📞 获取帮助

学习过程中遇到问题可以：

1. 查看官方文档
2. 搜索 Stack Overflow
3. 查看项目 Issue
4. 在技术社区提问

祝你学习顺利！🎉