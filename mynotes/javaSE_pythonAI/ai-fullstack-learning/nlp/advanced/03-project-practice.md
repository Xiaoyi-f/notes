# NLP 项目实战

## 项目1：智能客服系统

### 系统架构

```python
"""
┌─────────────────────────────────────────┐
│           智能客服系统                    │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────┐    ┌──────────────┐  │
│  │  用户界面    │    │  管理后台    │  │
│  └──────┬───────┘    └──────┬───────┘  │
│         │                    │          │
│         ↓                    ↓          │
│  ┌──────────────────────────────┐     │
│  │        API Gateway           │     │
│  └──────────────┬───────────────┘     │
│                 ↓                      │
│  ┌──────────────────────────────┐     │
│  │      对话管理服务             │     │
│  └──────┬──────────┬─────────────┘     │
│         │          │                   │
│         ↓          ↓                   │
│  ┌──────────┐ ┌──────────┐            │
│  │ NLU引擎  │ │ NLG引擎  │            │
│  └────┬─────┘ └────┬─────┘            │
│       │           │                   │
│       ↓           ↓                   │
│  ┌──────────────────────────────┐     │
│  │      知识库（RAG）            │     │
│  └──────────────────────────────┘     │
│                                         │
└─────────────────────────────────────────┘
"""
```

### 完整实现

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid
from langchain_openai import ChatOpenAI
from haystack import Pipeline, Document
from haystack.components.retrievers import InMemoryEmbeddingRetriever
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack.document_stores.in_memory import InMemoryDocumentStore

app = FastAPI(title="智能客服系统")

# 数据模型
class Message(BaseModel):
    content: str
    role: str = "user"
    timestamp: datetime = None

class Conversation(BaseModel):
    conversation_id: str
    messages: List[Message]
    user_id: str
    status: str = "active"

class CustomerServiceRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    user_id: str

class CustomerServiceResponse(BaseModel):
    message: str
    conversation_id: str
    confidence: float
    suggestions: List[str]
    source_documents: List[dict]

# 全局变量
llm = ChatOpenAI(model="gpt-4")
document_store = InMemoryDocumentStore()
conversations: dict = {}

# 意图识别
class IntentRecognizer:
    def __init__(self, llm):
        self.llm = llm
        self.intents = [
            "咨询产品",
            "售后服务",
            "投诉建议",
            "订单查询",
            "技术支持",
            "其他问题"
        ]

    def recognize(self, message: str) -> tuple:
        """识别意图和槽位"""
        prompt = f"""
        分析以下用户消息，识别：
        1. 意图（必须是以下之一：{', '.join(self.intents)}）
        2. 关键实体（产品名称、订单号等）

        用户消息：{message}

        以JSON格式返回：
        {{
            "intent": "意图",
            "entities": ["实体1", "实体2"]
        }}
        """

        result = llm.invoke(prompt)
        # 解析 JSON 结果
        # 简化实现
        return "其他问题", []

# 情感分析
class SentimentAnalyzer:
    def __init__(self):
        from transformers import pipeline
        self.sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment-latest"
        )

    def analyze(self, text: str) -> dict:
        """分析情感"""
        result = self.sentiment_pipeline(text)[0]
        return {
            "label": result["label"],
            "score": result["score"]
        }

# 答案生成器
class AnswerGenerator:
    def __init__(self, llm, retriever):
        self.llm = llm
        self.retriever = retriever

    def generate(self, question: str, conversation_history: List[dict] = None) -> dict:
        """生成答案"""
        # 检索相关文档
        results = self.retriever.run(query=question)
        documents = results["documents"]

        # 构建上下文
        context = "\\n".join([
            f"- {doc.content} (相似度: {doc.score:.2f})"
            for doc in documents
        ])

        # 构建历史上下文
        history_context = ""
        if conversation_history:
            history_context = "\\n对话历史：\\n"
            for msg in conversation_history[-5:]:  # 只保留最近5轮
                history_context += f"{msg['role']}: {msg['content']}\\n"

        # 生成答案
        prompt = f"""
        你是一个专业的客服助手。请根据以下信息回答用户问题。

        知识库信息：
        {context}

        {history_context}

        用户问题：{question}

        要求：
        1. 准确、专业
        2. 有礼貌
        3. 如果知识库中没有答案，说"抱歉，我需要更多信息来回答您的问题"
        4. 提供2-3个相关问题建议

        以JSON格式返回：
        {{
            "answer": "答案内容",
            "confidence": 0.95,
            "suggestions": ["相关问题1", "相关问题2", "相关问题3"]
        }}
        """

        result = llm.invoke(prompt)

        # 解析 JSON
        # 简化实现
        return {
            "answer": result.content,
            "confidence": 0.9,
            "suggestions": [
                "还有其他问题吗？",
                "需要更多帮助吗？"
            ],
            "source_documents": [
                {
                    "content": doc.content,
                    "score": doc.score
                }
                for doc in documents[:3]
            ]
        }

# 初始化组件
intent_recognizer = IntentRecognizer(llm)
sentiment_analyzer = SentimentAnalyzer()

# 检索管道
text_embedder = SentenceTransformersTextEmbedder(
    model="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
retriever = InMemoryEmbeddingRetriever(document_store=document_store, top_k=5)
answer_generator = AnswerGenerator(llm, retriever)

# API 端点
@app.post("/chat", response_model=CustomerServiceResponse)
async def chat(request: CustomerServiceRequest):
    """对话接口"""
    # 获取或创建会话
    if request.conversation_id and request.conversation_id in conversations:
        conversation = conversations[request.conversation_id]
    else:
        conversation_id = str(uuid.uuid4())
        conversation = {
            "conversation_id": conversation_id,
            "messages": [],
            "user_id": request.user_id,
            "status": "active",
            "created_at": datetime.now()
        }
        conversations[conversation_id] = conversation

    # 识别意图
    intent, entities = intent_recognizer.recognize(request.message)

    # 情感分析
    sentiment = sentiment_analyzer.analyze(request.message)

    # 如果是负面情绪，升级处理
    if sentiment["label"] == "NEGATIVE" and sentiment["score"] > 0.8:
        # 升级到人工客服
        return CustomerServiceResponse(
            message="我理解您的不满。请允许我将您转接到人工客服，他们会更好地帮助您。",
            conversation_id=conversation["conversation_id"],
            confidence=1.0,
            suggestions=[],
            source_documents=[]
        )

    # 生成答案
    history = conversation["messages"]
    result = answer_generator.generate(request.message, history)

    # 保存消息
    conversation["messages"].append({
        "role": "user",
        "content": request.message,
        "timestamp": datetime.now(),
        "intent": intent,
        "entities": entities,
        "sentiment": sentiment
    })

    conversation["messages"].append({
        "role": "assistant",
        "content": result["answer"],
        "timestamp": datetime.now(),
        "confidence": result["confidence"]
    })

    return CustomerServiceResponse(
        message=result["answer"],
        conversation_id=conversation["conversation_id"],
        confidence=result["confidence"],
        suggestions=result["suggestions"],
        source_documents=result["source_documents"]
    )

@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """获取会话历史"""
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="会话不存在")
    return conversations[conversation_id]

@app.post("/conversations/{conversation_id}/feedback")
async def submit_feedback(conversation_id: str, rating: int, comment: str = None):
    """提交反馈"""
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="会话不存在")

    # 保存反馈
    conversations[conversation_id]["feedback"] = {
        "rating": rating,
        "comment": comment,
        "timestamp": datetime.now()
    }

    return {"status": "success", "message": "反馈已保存"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 项目2：文档智能分析系统

```python
from haystack import Pipeline, Document
from haystack.components.converters import PyPDFToDocument
from haystack.components.preprocessors import DocumentSplitter
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack.components.writers import DocumentWriter
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.routers import ConditionalRouter
from haystack.components.generators import OpenAIGenerator
from haystack.components.builders import PromptBuilder

class DocumentAnalyzer:
    """文档智能分析系统"""

    def __init__(self):
        self.document_store = InMemoryDocumentStore()
        self.llm = OpenAIGenerator(model="gpt-4")

        # 创建索引管道
        self.indexing_pipeline = self._create_indexing_pipeline()

        # 创建分析管道
        self.analysis_pipeline = self._create_analysis_pipeline()

    def _create_indexing_pipeline(self):
        """创建文档索引管道"""
        pipeline = Pipeline()

        pipeline.add_component("converter", PyPDFToDocument())
        pipeline.add_component("splitter", DocumentSplitter(
            split_by="word",
            split_length=200,
            split_overlap=20
        ))
        pipeline.add_component("embedder", SentenceTransformersDocumentEmbedder(
            model="sentence-transformers/all-MiniLM-L6-v2"
        ))
        pipeline.add_component("writer", DocumentWriter(
            document_store=self.document_store
        ))

        pipeline.connect("converter.documents", "splitter.documents")
        pipeline.connect("splitter.documents", "embedder.documents")
        pipeline.connect("embedder.documents", "writer.documents")

        return pipeline

    def _create_analysis_pipeline(self):
        """创建文档分析管道"""
        pipeline = Pipeline()

        # 摘要生成
        summary_prompt = PromptBuilder(
            template="为以下文档生成简洁的摘要：\\n\\n{% for doc in documents %}{{ doc.content }}\\n{% endfor %}\\n\\n摘要："
        )
        pipeline.add_component("summary_builder", summary_prompt)
        pipeline.add_component("summary_generator", self.llm)

        # 关键信息抽取
        extraction_prompt = PromptBuilder(
            template="从以下文档中提取关键信息（日期、金额、人名、公司名等）：\\n\\n{% for doc in documents %}{{ doc.content }}\\n{% endfor %}\\n\\n以JSON格式返回："
        )
        pipeline.add_component("extraction_builder", extraction_prompt)
        pipeline.add_component("extraction_generator", self.llm)

        return pipeline

    def index_document(self, file_path: str):
        """索引文档"""
        result = self.indexing_pipeline.run({
            "converter": {"sources": [file_path]}
        })
        return result

    def summarize_document(self, query: str):
        """生成文档摘要"""
        # 检索相关文档
        retriever = InMemoryEmbeddingRetriever(
            document_store=self.document_store,
            top_k=5
        )
        results = retriever.run(query=query)

        # 生成摘要
        summary_result = self.analysis_pipeline.run({
            "summary_builder": {"documents": results["documents"]},
            "extraction_builder": {"documents": results["documents"]}
        })

        return {
            "summary": summary_result["summary_generator"]["replies"][0],
            "key_info": summary_result["extraction_generator"]["replies"][0],
            "source_documents": results["documents"]
        }

    def compare_documents(self, doc_ids: List[str]):
        """比较文档"""
        documents = [self.document_store.get_documents_by_id([doc_id]) for doc_id in doc_ids]

        prompt = f"""
        比较以下文档的内容，找出它们的主要异同点：

        文档1：
        {documents[0][0].content}

        文档2：
        {documents[1][0].content}

        分析结果：
        """

        result = self.llm.run(prompt=prompt)
        return result["replies"][0]

# 使用
analyzer = DocumentAnalyzer()

# 索引文档
# analyzer.index_document("contract.pdf")
# analyzer.index_document("report.pdf")

# 分析
# result = analyzer.summarize_document("合同条款")
# print(result["summary"])

# 比较
# comparison = analyzer.compare_documents(["doc1_id", "doc2_id"])
# print(comparison)
```

## 项目3：多模态问答系统

```python
from typing import List, Union
from PIL import Image
import base64
import io

class MultimodalQA:
    """多模态问答系统"""

    def __init__(self):
        from transformers import BlipProcessor, BlipForQuestionAnswering
        from sentence_transformers import SentenceTransformer

        # 图像问答模型
        self.image_processor = BlipProcessor.from_pretrained(
            "Salesforce/blip-vqa-base"
        )
        self.image_qa_model = BlipForQuestionAnswering.from_pretrained(
            "Salesforce/blip-vqa-base"
        )

        # 文本检索模型
        self.text_model = SentenceTransformer('all-MiniLM-L6-v2')

        # 文本问答 LLM
        from langchain_openai import ChatOpenAI
        self.text_llm = ChatOpenAI(model="gpt-4-vision-preview")

    def encode_image(self, image: Union[str, Image.Image]) -> str:
        """编码图像为 base64"""
        if isinstance(image, str):
            image = Image.open(image)

        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str

    def image_qa(self, image: Union[str, Image.Image], question: str) -> str:
        """图像问答"""
        # 处理图像和问题
        inputs = self.image_processor(image, question, return_tensors="pt")

        # 生成答案
        with torch.no_grad():
            outputs = self.image_qa_model.generate(**inputs)

        answer = self.image_processor.decode(outputs[0], skip_special_tokens=True)
        return answer

    def text_qa(self, question: str, context: List[str] = None) -> str:
        """文本问答"""
        if context:
            # 使用 RAG
            context_str = "\\n".join(context)
            prompt = f"""
            根据以下上下文回答问题：

            上下文：
            {context_str}

            问题：{question}

            答案：
            """
        else:
            prompt = f"回答以下问题：{question}"

        result = self.text_llm.invoke(prompt)
        return result.content

    def multimodal_qa(
        self,
        question: str,
        image: Union[str, Image.Image] = None,
        context: List[str] = None
    ) -> str:
        """多模态问答"""
        responses = []

        # 图像问答
        if image:
            image_answer = self.image_qa(image, question)
            responses.append(f"图像分析：{image_answer}")

        # 文本问答
        if context:
            text_answer = self.text_qa(question, context)
            responses.append(f"文本分析：{text_answer}")

        # 综合答案
        if len(responses) > 1:
            combined_prompt = f"""
            用户问题：{question}

            来自不同模态的回答：
            {chr(10).join(responses)}

            请综合以上信息，给出最终的准确答案：
            """
            final_answer = self.text_llm.invoke(combined_prompt).content
        else:
            final_answer = responses[0] if responses else "无法回答"

        return final_answer

# 使用
qa = MultimodalQA()

# 图像问答
# answer = qa.image_qa("image.jpg", "图片中是什么？")
# print(answer)

# 文本问答
# answer = qa.text_qa("什么是机器学习？")
# print(answer)

# 多模态问答
# answer = qa.multimodal_qa(
#     question="这张图片中的物体是什么？它与机器学习有什么关系？",
#     image="image.jpg",
#     context=["机器学习是AI的分支", "图像识别是机器学习的重要应用"]
# )
# print(answer)
```

## 小结

本节介绍了三个完整的 NLP 项目：

- **智能客服系统** - 对话管理、意图识别、RAG
- **文档分析系统** - 文档索引、摘要、比较
- **多模态问答** - 图像+文本综合分析

## 实践练习

### 编程题
1. 完善智能客服系统：添加 FAQ 知识库的自动匹配、用户满意度评分记录、以及客服对话的统计分析功能。
2. 为文档分析系统添加"文档对比"功能：输入两篇文档，自动生成差异分析报告。

### 思考题
1. 智能客服系统中，什么情况下应该从 AI 自动转接到人工客服？
2. 多模态问答系统设计时，如何处理文本信息和图像信息的不对称情况？

### 自测题
1. 智能客服系统包含哪些核心模块？
2. 文档分析系统中，如何高效处理大文件（超过100MB的PDF）？
3. 多模态 QA 和单模态 QA 在架构上有什么关键区别？

下一步将学习 Transformer 模型深入（→ `04-transformer-models.md`）。