# NLP 生产系统实战

## 一、项目概述

构建一个多语言 NLP 处理平台，支持文本分类、情感分析、命名实体识别、文本摘要，提供统一的 RESTful API 和批处理能力。

### 技术栈

| 组件 | 选型 | 说明 |
|------|------|------|
| 推理引擎 | ONNX Runtime / Triton | 高性能推理 |
| 模型管理 | Hugging Face + S3 | 模型版本管理 |
| 批处理 | Celery + RabbitMQ | 异步任务 |
| 缓存 | Redis | 结果缓存 |
| 监控 | Prometheus + Grafana | 延迟/QPS 监控 |
| 部署 | Docker + K8s | 弹性扩缩 |

## 二、系统架构

```
┌──────────────┐    ┌──────────────┐    ┌─────────────────┐
│  REST API    │───▶│  任务分发     │───▶│  NLP Pipeline   │
│  FastAPI     │    │  Celery      │    │  ONNX Runtime   │
└──────────────┘    └──────────────┘    └────────┬────────┘
                                                 │
                          ┌──────────────────────┼──────────┐
                          │                      │          │
                    ┌─────▼─────┐     ┌──────────▼─────┐    │
                    │  分类模型   │     │  序列标注模型   │    │
                    │ BERT/XLMR │     │  BERT-CRF      │    │
                    └───────────┘     └────────────────┘    │
                          │                      │          │
                    ┌─────▼─────┐     ┌──────────▼─────┐    │
                    │  Redis    │     │  PostgreSQL     │    │
                    │  缓存      │     │  结果持久化    │    │
                    └───────────┘     └────────────────┘    │
                          └──────────────────────────────────┘
```

## 三、模型推理服务

### ONNX 模型部署

```python
import onnxruntime as ort
import numpy as np
from transformers import AutoTokenizer
from typing import Optional

class ONNXInference:
    """ONNX 模型推理服务"""

    def __init__(self, model_path: str, tokenizer_name: str, providers: Optional[list] = None):
        if providers is None:
            providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
        self.session = ort.InferenceSession(model_path, providers=providers)
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        self.input_names = [inp.name for inp in self.session.get_inputs()]
        self.output_names = [out.name for out in self.session.get_outputs()]

    def predict(self, texts: list[str], batch_size: int = 32) -> np.ndarray:
        """批量推理"""
        all_outputs = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            inputs = self.tokenizer(batch, padding=True, truncation=True,
                                    max_length=512, return_tensors="np")
            onnx_inputs = {
                "input_ids": inputs["input_ids"],
                "attention_mask": inputs["attention_mask"]
            }
            if "token_type_ids" in self.input_names:
                onnx_inputs["token_type_ids"] = inputs.get("token_type_ids",
                    np.zeros_like(inputs["input_ids"]))
            outputs = self.session.run(self.output_names, onnx_inputs)
            all_outputs.append(outputs[0])
        return np.concatenate(all_outputs, axis=0)

class NLPModelHub:
    """模型仓库管理"""

    def __init__(self, base_dir: str = "/models"):
        self.base_dir = base_dir
        self.models = {}

    def load_model(self, name: str, version: str = "latest"):
        model_path = f"{self.base_dir}/{name}/{version}/model.onnx"
        tokenizer_path = f"{self.base_dir}/{name}/{version}/tokenizer"
        self.models[name] = ONNXInference(model_path, tokenizer_path)
        return self.models[name]

    def list_models(self) -> list[dict]:
        import os
        models = []
        for name in os.listdir(self.base_dir):
            versions = os.listdir(f"{self.base_dir}/{name}")
            models.append({"name": name, "versions": sorted(versions)})
        return models
```

## 四、NLP Pipeline

```python
from dataclasses import dataclass, field
from typing import Optional
import spacy

@dataclass
class NLPResult:
    text: str
    language: str
    sentiment: Optional[dict] = None
    entities: list = field(default_factory=list)
    categories: list = field(default_factory=list)
    summary: Optional[str] = None
    keywords: list = field(default_factory=list)
    confidence: float = 0.0

class NLPPipeline:
    """统一的 NLP 处理管线"""

    def __init__(self, models: NLPModelHub):
        self.models = models
        self.classifier = models.load_model("xlmr-classifier")
        self.ner_model = models.load_model("bert-ner")
        self.nlp_zh = spacy.load("zh_core_web_sm")
        self.nlp_en = spacy.load("en_core_web_trf")

    def process(self, text: str, tasks: list[str] = None) -> NLPResult:
        if tasks is None:
            tasks = ["language", "sentiment", "entities", "categories", "keywords"]
        
        result = NLPResult(text=text)
        for task in tasks:
            if task == "language":
                result.language = self._detect_language(text)
            elif task == "sentiment":
                result.sentiment = self._analyze_sentiment(text)
            elif task == "entities":
                result.entities = self._extract_entities(text)
            elif task == "categories":
                result.categories = self._classify(text)
            elif task == "keywords":
                result.keywords = self._extract_keywords(text)
        return result

    def _detect_language(self, text: str) -> str:
        """语言检测"""
        import langdetect
        try:
            return langdetect.detect(text)
        except:
            return "unknown"

    def _analyze_sentiment(self, text: str) -> dict:
        """情感分析"""
        inputs = self.models.models["xlmr-classifier"].tokenizer(
            text, return_tensors="np", truncation=True, max_length=512)
        outputs = self.models.models["xlmr-classifier"].session.run(
            None, {"input_ids": inputs["input_ids"],
                   "attention_mask": inputs["attention_mask"]})
        probs = np.exp(outputs[0]) / np.exp(outputs[0]).sum(-1, keepdims=True)
        labels = ["negative", "neutral", "positive"]
        return {
            "label": labels[probs[0].argmax()],
            "score": float(probs[0].max()),
            "distribution": {l: float(p) for l, p in zip(labels, probs[0])}
        }

    def _extract_entities(self, text: str, lang: str = "zh") -> list[dict]:
        """命名实体识别"""
        nlp = self.nlp_zh if lang == "zh" else self.nlp_en
        doc = nlp(text)
        entities = []
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            })
        # 合并重叠实体
        return self._dedup_entities(entities)

    def _classify(self, text: str) -> list[dict]:
        """文本分类"""
        outputs = self.classifier.predict([text])[0]
        labels = ["technology", "finance", "health", "education", "news", "other"]
        probs = np.exp(outputs) / np.exp(outputs).sum()
        categories = [{"label": l, "score": float(p)} for l, p in zip(labels, probs)]
        return sorted(categories, key=lambda x: x["score"], reverse=True)[:3]

    def _extract_keywords(self, text: str, top_k: int = 10) -> list[str]:
        """TF-IDF 关键词提取"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        import jieba
        if len(text) < 50:
            return []
        words = " ".join(jieba.cut(text))
        vectorizer = TfidfVectorizer(max_features=100)
        tfidf = vectorizer.fit_transform([words])
        scores = zip(vectorizer.get_feature_names_out(), tfidf.toarray()[0])
        return [w for w, s in sorted(scores, key=lambda x: x[1], reverse=True)[:top_k]]

    def _dedup_entities(self, entities: list[dict]) -> list[dict]:
        """去重重叠实体"""
        if not entities:
            return []
        entities.sort(key=lambda x: (x["start"], -x["end"]))
        result = [entities[0]]
        for e in entities[1:]:
            if e["start"] >= result[-1]["end"]:
                result.append(e)
        return result
```

## 五、API 服务

```python
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from celery import Celery
import uuid

app = FastAPI(title="NLP Platform API")
celery_app = Celery("nlp", broker="redis://localhost:6379/1")

class ProcessRequest(BaseModel):
    text: str
    tasks: list[str] = ["language", "sentiment", "entities"]
    sync: bool = True

class BatchProcessRequest(BaseModel):
    texts: list[str]
    tasks: list[str] = ["language", "sentiment", "entities"]

@celery_app.task(bind=True, max_retries=3)
def process_async(self, text: str, tasks: list[str]):
    try:
        return nlp_pipeline.process(text, tasks).__dict__
    except Exception as e:
        self.retry(countdown=60)

@app.post("/v1/process")
async def process_text(request: ProcessRequest):
    """处理文本"""
    if not request.text.strip():
        raise HTTPException(400, "text cannot be empty")
    
    if request.sync:
        result = nlp_pipeline.process(request.text, request.tasks)
        return {"status": "ok", "data": result.__dict__}
    else:
        task = process_async.delay(request.text, request.tasks)
        return {"status": "accepted", "task_id": task.id}

@app.post("/v1/batch")
async def batch_process(request: BatchProcessRequest):
    """批量处理"""
    if len(request.texts) > 1000:
        raise HTTPException(400, "batch size max 1000")
    
    # 批量推理（同步）
    results = []
    for i in range(0, len(request.texts), 32):
        batch = request.texts[i:i+32]
        batch_results = nlp_pipeline.classifier.predict(batch)
        for text, result in zip(batch, batch_results):
            results.append({"text": text[:50], "category": int(result.argmax())})
    return {"status": "ok", "count": len(results), "data": results}

@app.get("/v1/tasks/{task_id}")
async def get_task(task_id: str):
    """异步任务查询"""
    task = celery_app.AsyncResult(task_id)
    if task.failed():
        return {"status": "failed", "error": str(task.info)}
    elif task.ready():
        return {"status": "completed", "data": task.result}
    return {"status": "processing"}
```

## 六、性能优化

### 模型量化

```python
from onnxruntime.quantization import quantize_dynamic, QuantType

def optimize_model(input_path: str, output_path: str):
    """模型量化和导出"""
    # 动态量化（INT8）
    quantize_dynamic(
        model_input=input_path,
        model_output=output_path,
        per_channel=True,
        weight_type=QuantType.QUInt8
    )
    # 量化后体积减小 4x，推理速度提升 2-3x

# Triton Server 配置
triton_config = """
name: "nlp_pipeline"
backend: "ensemble"
max_batch_size: 64
input [
  { name: "TEXT", data_type: TYPE_STRING, dims: [1] }
]
output [
  { name: "CATEGORY", data_type: TYPE_INT64, dims: [1] },
  { name: "SENTIMENT", data_type: TYPE_STRING, dims: [1] }
]
"""
```

### 缓存策略

```python
import hashlib
import redis.asyncio as aioredis
from functools import lru_cache

class NLPCache:
    def __init__(self, redis_url="redis://localhost:6379"):
        self.redis = None  # lazy init

    async def get_or_compute(self, text: str, compute_func):
        text_hash = hashlib.md5(text.encode()).hexdigest()
        # 尝试从缓存获取
        cached = await self._get(text_hash)
        if cached:
            return cached
        # 计算并缓存
        result = await compute_func(text)
        await self._set(text_hash, result, ttl=3600)
        return result

    async def _get(self, key: str):
        if not self.redis:
            self.redis = await aioredis.from_url(self.redis_url)
        data = await self.redis.get(f"nlp:{key}")
        return json.loads(data) if data else None

    async def _set(self, key: str, value, ttl: int):
        await self.redis.setex(f"nlp:{key}", ttl, json.dumps(value))
```

## 七、面试考点

1. **ONNX Runtime 相比原始 PyTorch 推理的优势？** 跨平台、量化支持、CUDA/CPU 统一接口、无 Python GIL
2. **如何处理长文本（超过 512 tokens）？** 滑动窗口 + 集成投票 / Longformer / 分块处理
3. **批量推理的注意事项？** Padding 策略（dynamic padding）、max_tokens 对齐、OOM 处理
4. **多语言模型如何选型？** XLM-R 适合跨语言场景，mBERT 适合中英文

## 八、课后练习

1. 将模型转为 ONNX 格式并对比量化前后的推理速度和精度差异
2. 实现一个流式文本处理 Pipeline，支持 1000+ QPS
3. 为情感分析添加细粒度维度（如：anger, joy, sadness）
4. 集成飞书/钉钉机器人，实时处理用户消息

## 自测题

1. ONNX Runtime 不支持的优化方式是？ A) 动态量化 B) 静态量化 C) 知识蒸馏 D) 算子融合
2. Transformer 模型中 self-attention 的计算复杂度是？ A) O(n) B) O(n log n) C) O(n²) D) O(2^n)
3. 以下哪个不是常用的序列标注解码方式？ A) Softmax B) CRF C) Viterbi D) Beam Search

**答案：** 1-C, 2-C, 3-A
