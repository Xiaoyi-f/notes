# NLP 高级技术

## 1. 大语言模型（LLM）

### Transformer 架构

```python
import torch
import torch.nn as nn
import math

class MultiHeadAttention(nn.Module):
    """多头注意力机制"""
    def __init__(self, d_model, num_heads):
        super().__init__()
        assert d_model % num_heads == 0

        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads

        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)

    def scaled_dot_product_attention(self, Q, K, V, mask=None):
        """缩放点积注意力"""
        attn_scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)

        if mask is not None:
            attn_scores = attn_scores.masked_fill(mask == 0, -1e9)

        attn_probs = torch.softmax(attn_scores, dim=-1)
        output = torch.matmul(attn_probs, V)

        return output, attn_probs

    def forward(self, query, key, value, mask=None):
        batch_size = query.size(0)

        # 线性变换
        Q = self.W_q(query)  # (batch_size, seq_len, d_model)
        K = self.W_k(key)
        V = self.W_v(value)

        # 分割多头
        Q = Q.view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        K = K.view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        V = V.view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)

        # 计算注意力
        attn_output, attn_weights = self.scaled_dot_product_attention(Q, K, V, mask)

        # 合并多头
        attn_output = attn_output.transpose(1, 2).contiguous().view(
            batch_size, -1, self.d_model
        )

        # 最终线性变换
        output = self.W_o(attn_output)

        return output, attn_weights


class PositionalEncoding(nn.Module):
    """位置编码"""
    def __init__(self, d_model, max_len=5000):
        super().__init__()

        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)

        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model)
        )

        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)

        self.register_buffer('pe', pe)

    def forward(self, x):
        return x + self.pe[:, :x.size(1)]


class TransformerBlock(nn.Module):
    """Transformer 块"""
    def __init__(self, d_model, num_heads, d_ff, dropout=0.1):
        super().__init__()

        self.attention = MultiHeadAttention(d_model, num_heads)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)

        self.feed_forward = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.ReLU(),
            nn.Linear(d_ff, d_model)
        )

        self.dropout = nn.Dropout(dropout)

    def forward(self, x, mask=None):
        # 自注意力 + 残差连接
        attn_output, _ = self.attention(x, x, x, mask)
        x = self.norm1(x + self.dropout(attn_output))

        # 前馈网络 + 残差连接
        ff_output = self.feed_forward(x)
        x = self.norm2(x + self.dropout(ff_output))

        return x


class Transformer(nn.Module):
    """完整的 Transformer"""
    def __init__(self, vocab_size, d_model=512, num_heads=8,
                 num_layers=6, d_ff=2048, max_len=512):
        super().__init__()

        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoding = PositionalEncoding(d_model, max_len)

        self.transformer_blocks = nn.ModuleList([
            TransformerBlock(d_model, num_heads, d_ff)
            for _ in range(num_layers)
        ])

        self.fc = nn.Linear(d_model, vocab_size)
        self.dropout = nn.Dropout(0.1)

    def forward(self, x, mask=None):
        # 嵌入和位置编码
        x = self.embedding(x)
        x = self.pos_encoding(x)
        x = self.dropout(x)

        # Transformer 层
        for block in self.transformer_blocks:
            x = block(x, mask)

        # 输出层
        output = self.fc(x)

        return output
```

### 使用 Hugging Face 模型

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# 加载模型和分词器
model_name = "THUDM/chatglm3-6b"
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    trust_remote_code=True,
    torch_dtype=torch.float16,
    device_map="auto"
)

# 文本生成
def generate_text(prompt, max_length=512):
    """生成文本"""
    inputs = tokenizer(prompt, return_tensors="pt")
    inputs = inputs.to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_length=max_length,
            temperature=0.7,
            top_p=0.9,
            do_sample=True
        )

    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return generated_text

# 使用
prompt = "请用Python写一个快速排序算法："
result = generate_text(prompt)
print(result)
```

## 2. 微调 LLM

### LoRA 微调

```python
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from datasets import Dataset
import torch

# 加载基础模型
model_name = "meta-llama/Meta-Llama-3-8B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name)
base_model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="auto"
)

# 配置 LoRA
lora_config = LoraConfig(
    r=16,                    # LoRA 秩
    lora_alpha=32,           # LoRA alpha
    target_modules=["q_proj", "v_proj"],  # 目标模块
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

# 应用 LoRA
model = get_peft_model(base_model, lora_config)
model.print_trainable_parameters()

# 准备训练数据
train_data = [
    {
        "input": "写一个Python函数计算斐波那契数列",
        "output": "def fibonacci(n):\\n    if n <= 1:\\n        return n\\n    return fibonacci(n-1) + fibonacci(n-2)"
    },
    # ... 更多数据
]

# 转换为 Dataset
def preprocess_function(examples):
    inputs = examples["input"]
    outputs = examples["output"]

    model_inputs = tokenizer(
        inputs,
        max_length=512,
        padding="max_length",
        truncation=True
    )

    labels = tokenizer(
        outputs,
        max_length=512,
        padding="max_length",
        truncation=True
    )

    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

dataset = Dataset.from_list(train_data)
tokenized_dataset = dataset.map(preprocess_function, batched=True)

# 训练参数
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    warmup_steps=100,
    logging_steps=10,
    save_steps=100,
    learning_rate=2e-4,
    fp16=True,
)

# 训练器
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
)

# 开始训练
trainer.train()

# 保存模型
model.save_pretrained("./fine_tuned_model")
tokenizer.save_pretrained("./fine_tuned_model")
```

### QLoRA 微调（4-bit 量化）

```python
from transformers import BitsAndBytesConfig

# 4-bit 量化配置
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4"
)

# 加载量化模型
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    device_map="auto"
)

# 配置 QLoRA
qlora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, qlora_config)

# 训练（与 LoRA 相同）
```

## 3. 提示工程

### Few-Shot Prompting

```python
def few_shot_prompting(query: str) -> str:
    """Few-Shot 提示工程"""
    examples = [
        {
            "input": "Python中的列表推导式是什么？",
            "output": """
            Python列表推导式是一种简洁的创建列表的方法。
            示例：squares = [x**2 for x in range(10)]
            这会创建一个包含0到9的平方数的列表。
            """
        },
        {
            "input": "如何读取文件内容？",
            "output": """
            在Python中，可以使用open()函数读取文件内容。
            示例：
            with open('file.txt', 'r') as f:
                content = f.read()
            """
        }
    ]

    prompt = "以下是一些编程问题的示例和答案：\\n\\n"

    for i, example in enumerate(examples, 1):
        prompt += f"示例{i}:\\n"
        prompt += f"问题：{example['input']}\\n"
        prompt += f"答案：{example['output']}\\n\\n"

    prompt += f"现在回答这个问题：\\n问题：{query}\\n答案："

    return prompt

# 使用
query = "Python中的装饰器是什么？"
prompt = few_shot_prompting(query)
# result = llm.invoke(prompt)
```

### Chain of Thought（思维链）

```python
def chain_of_thought_prompt(query: str) -> str:
    """思维链提示"""
    prompt = f"""
    请按照以下步骤回答问题：

    步骤1：理解问题的核心需求
    步骤2：分析问题的关键点
    步骤3：提出解决方案
    步骤4：验证方案的正确性
    步骤5：给出最终答案

    问题：{query}

    请按步骤展开你的思考过程并给出最终答案：
    """

    return prompt

# 使用示例
query = "如何优化一个O(n^2)的算法？"
prompt = chain_of_thought_prompt(query)
# result = llm.invoke(prompt)
```

### Self-Consistency（自洽性）

```python
import asyncio
from typing import List

async def self_consistency(query: str, num_samples: int = 5) -> str:
    """
    自洽性：生成多个答案并选择最一致的
    """
    # 生成多个样本
    samples = []
    for i in range(num_samples):
        prompt = f"""
        按照以下格式回答：
        思考：[你的思考过程]
        答案：[最终答案]

        问题：{query}
        """

        # result = await llm.ainvoke(prompt)
        # samples.append(result.content)

        # 模拟
        samples.append(f"思考{i}\\n答案: A")

    # 统计答案
    answers = [s.split("答案:")[-1].strip() for s in samples]
    from collections import Counter
    answer_counts = Counter(answers)

    # 返回最常见的答案
    most_common = answer_counts.most_common(1)[0][0]

    return most_common

# 使用
# result = asyncio.run(self_consistency("1+1等于多少？"))
```

## 4. RAG 优化

### 查询优化

```python
class QueryOptimizer:
    """查询优化器"""

    def __init__(self, llm):
        self.llm = llm

    def expand_query(self, query: str) -> List[str]:
        """查询扩展"""
        prompt = f"""
        为以下查询生成3个相关的查询变体，用于提高检索效果。
        每行一个查询。

        原始查询：{query}

        相关查询：
        """

        # result = self.llm.invoke(prompt)
        # return result.content.strip().split("\\n")

        # 模拟返回
        return [query, f"关于{query}", f"{query}的相关信息"]

    def rewrite_query(self, query: str) -> str:
        """查询重写"""
        prompt = f"""
        将以下自然语言查询重写为更适合文档检索的形式。
        简短、关键词化。

        原始查询：{query}

        重写后的查询：
        """

        # result = self.llm.invoke(prompt)
        # return result.content.strip()

        # 简化实现
        return " ".join(query.split()[:5])

    def decompose_query(self, query: str) -> List[str]:
        """查询分解"""
        prompt = f"""
        将复杂查询分解为多个简单的子查询。

        复杂查询：{query}

        子查询（每行一个）：
        """

        # result = self.llm.invoke(prompt)
        # return result.content.strip().split("\\n")

        # 简化实现
        return [query]
```

### 检索优化

```python
class HybridRetriever:
    """混合检索器"""

    def __init__(self, vector_store, keyword_store, llm):
        self.vector_store = vector_store
        self.keyword_store = keyword_store
        self.llm = llm

    def retrieve(self, query: str, top_k: int = 10) -> List[Document]:
        """混合检索"""
        # 1. 向量检索
        vector_results = self.vector_store.search(query, top_k=top_k)

        # 2. 关键词检索
        keyword_results = self.keyword_store.search(query, top_k=top_k)

        # 3. 合并和去重
        all_results = self._merge_results(vector_results, keyword_results)

        # 4. 重排序
        reranked = self._rerank(query, all_results, top_k)

        return reranked

    def _merge_results(self, results1, results2):
        """合并检索结果"""
        seen = set()
        merged = []

        for doc in results1 + results2:
            doc_id = doc.metadata.get("id", doc.content)
            if doc_id not in seen:
                seen.add(doc_id)
                merged.append(doc)

        return merged

    def _rerank(self, query: str, documents: List[Document], top_k: int) -> List[Document]:
        """重排序"""
        # 使用交叉编码器重排序
        # 这里简化实现

        # 计算相似度分数
        scores = []
        for doc in documents:
            score = self._compute_similarity(query, doc)
            scores.append(score)

        # 按分数排序
        sorted_docs = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
        return [doc for doc, score in sorted_docs[:top_k]]

    def _compute_similarity(self, query: str, document: Document) -> float:
        """计算查询和文档的相似度"""
        # 简化实现：使用关键词重叠
        query_words = set(query.lower().split())
        doc_words = set(document.content.lower().split())

        overlap = len(query_words & doc_words)
        return overlap / len(query_words) if query_words else 0
```

## 小结

本节介绍了 NLP 高级技术：

- **LLM** - Transformer 架构、使用方法
- **微调** - LoRA、QLoRA
- **提示工程** - Few-Shot、CoT、Self-Consistency
- **RAG 优化** - 查询优化、混合检索

## 实践练习

### 编程题
1. 使用 LoRA 对一个开源小模型（如 Qwen2-0.5B）进行微调，让它学会回答特定领域的问题。
2. 实现一个完整的混合检索器：结合向量检索和关键词检索，对结果进行去重和重排序。

### 思考题
1. LoRA 微调中，`r`（秩）参数的大小对训练效果和效率有什么影响？
2. Chain of Thought 和 Self-Consistency 各适合什么类型的问题？

### 自测题
1. Transformer 架构的核心组件是什么？
2. LoRA 和 QLoRA 的主要区别是什么？
3. 查询优化的三种主要方法是什么？

下一步将学习项目实战（→ `03-project-practice.md`）。