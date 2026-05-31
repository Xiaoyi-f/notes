# NLP（自然语言处理）基础入门

## 什么是 NLP？

NLP（Natural Language Processing）是计算机科学、人工智能和语言学的交叉领域，研究计算机如何理解、处理和生成人类语言。

### NLP 任务分类

```python
"""
┌─────────────────────────────────────────┐
│            NLP 任务分类                  │
├─────────────────────────────────────────┤
│  1. 文本分类               │
│     - 情感分析                             │
│     - 垃圾邮件检测                         │
│     - 主题分类                             │
│                                         │
│  2. 序列标注               │
│     - 命名实体识别（NER）                   │
│     - 词性标注（POS）                      │
│     - 语义角色标注（SRL）                  │
│                                         │
│  3. 生成任务              │
│     - 机器翻译                             │
│     - 文本摘要                             │
│     - 问答系统                             │
│                                         │
│  4. 信息抽取              │
│     - 关系抽取                             │
│     - 事件抽取                             │
│     - 属性抽取                             │
└─────────────────────────────────────────┘
"""
```

## 1. 文本预处理

### 分词（Tokenization）

```python
# 中文分词
import jieba
import jieba.posseg as pseg

# 基础分词
text = "自然语言处理是人工智能的重要分支"
words = jieba.lcut(text)
print("分词结果:", words)  # ['自然语言处理', '是', '人工智能', '的', '重要', '分支']

# 带词性标注
words_pos = pseg.lcut(text)
print("词性标注:", [(w.word, w.flag) for w in words_pos])

# 加载自定义词典
jieba.load_userdict("userdict.txt")

# 英文分词
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize

nltk.download('punkt')

english_text = "Natural Language Processing is an important branch of AI."
words = word_tokenize(english_text)
print("英文分词:", words)

# 句子分割
sentences = sent_tokenize("This is sentence 1. This is sentence 2!")
print("句子分割:", sentences)
```

### 去除停用词

```python
# 中文停用词
import jieba

# 加载停用词表
def load_stopwords(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        stopwords = [line.strip() for line in f]
    return stopwords

# 或者使用内置停用词
def remove_stopwords(text, stopwords=None):
    if stopwords is None:
        stopwords = {'的', '了', '和', '是', '在', '我', '有', '就', '不', '人'}

    words = jieba.lcut(text)
    filtered = [word for word in words if word not in stopwords]
    return " ".join(filtered)

text = "这是一个关于自然语言处理的例子"
filtered = remove_stopwords(text)
print("去除停用词:", filtered)
```

### 词干化和词形还原

```python
from nltk.stem import PorterStemmer, WordNetLemmatizer
import nltk
nltk.download('wordnet')

stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()

words = ["running", "ran", "easily", "fairly"]

print("词干化:")
for word in words:
    print(f"  {word} -> {stemmer.stem(word)}")

print("\\n词形还原:")
for word in words:
    print(f"  {word} -> {lemmatizer.lemmatize(word)}")
```

## 2. 文本表示

### One-Hot 编码

```python
import numpy as np

def one_hot_encode(vocab, word):
    """One-Hot 编码"""
    vector = np.zeros(len(vocab))
    if word in vocab:
        idx = vocab.index(word)
        vector[idx] = 1
    return vector

# 示例
vocab = ["苹果", "香蕉", "橙子", "葡萄"]
word = "苹果"

encoded = one_hot_encode(vocab, word)
print(f"词汇表: {vocab}")
print(f"{word}的One-Hot编码: {encoded}")
```

### 词袋模型（Bag of Words）

```python
from sklearn.feature_extraction.text import CountVectorizer

# 创建词袋模型
corpus = [
    "我喜欢吃苹果",
    "苹果很好吃",
    "香蕉也很好吃"
]

vectorizer = CountVectorizer(tokenizer=jieba.lcut)
X = vectorizer.fit_transform(corpus)

print("词汇表:", vectorizer.get_feature_names_out())
print("词袋矩阵:")
print(X.toarray())
```

### TF-IDF

```python
from sklearn.feature_extraction.text import TfidfVectorizer

# 创建 TF-IDF 向量化器
tfidf_vectorizer = TfidfVectorizer(tokenizer=jieba.lcut)
tfidf_matrix = tfidf_vectorizer.fit_transform(corpus)

print("\\nTF-IDF 矩阵:")
print(tfidf_matrix.toarray())

# 获取每个词的 IDF 值
print("\\nIDF 值:")
for word, idf in zip(tfidf_vectorizer.get_feature_names_out(),
                     tfidf_vectorizer.idf_):
    print(f"  {word}: {idf:.4f}")
```

### Word Embeddings（词嵌入）

```python
# 使用预训练词向量
from gensim.models import KeyedVectors

# 加载预训练模型（需要先下载）
# model = KeyedVectors.load_word2vec_format("path/to/model.bin", binary=True)

# 简化示例：手动创建小规模嵌入
import numpy as np

word_embeddings = {
    "苹果": np.array([0.1, 0.2, 0.3]),
    "香蕉": np.array([0.2, 0.1, 0.4]),
    "橙子": np.array([0.15, 0.25, 0.35]),
    "葡萄": np.array([0.05, 0.15, 0.25])
}

def get_word_embedding(word):
    return word_embeddings.get(word, np.zeros(3))

def cosine_similarity(vec1, vec2):
    """计算余弦相似度"""
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    return dot_product / (norm1 * norm2)

# 计算词相似度
apple_emb = get_word_embedding("苹果")
banana_emb = get_word_embedding("香蕉")

similarity = cosine_similarity(apple_emb, banana_emb)
print(f"苹果和香蕉的相似度: {similarity:.4f}")
```

### Sentence Embeddings（句子嵌入）

```python
from sentence_transformers import SentenceTransformer

# 加载预训练模型
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# 编码句子
sentences = [
    "我喜欢吃苹果",
    "苹果很好吃",
    "香蕉也很好吃"
]

embeddings = model.encode(sentences)

print("句子嵌入形状:", embeddings.shape)  # (3, 384)

# 计算句子相似度
from sklearn.metrics.pairwise import cosine_similarity

similarities = cosine_similarity(embeddings)
print("\\n句子相似度矩阵:")
for i, sent in enumerate(sentences):
    print(f"{sent}: {similarities[i]}")
```

## 3. 文本分类

### 传统方法：朴素贝叶斯

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# 准备数据
corpus = [
    "这个产品很好，我很喜欢",
    "质量不错，推荐购买",
    "服务态度很好",
    "产品质量太差了",
    "不推荐，很失望",
    "服务太差，态度不好"
]

labels = ["正面", "正面", "正面", "负面", "负面", "负面"]

# 分割数据
X_train, X_test, y_train, y_test = train_test_split(
    corpus, labels, test_size=0.3, random_state=42
)

# 特征提取
vectorizer = TfidfVectorizer(tokenizer=jieba.lcut)
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# 训练模型
model = MultinomialNB()
model.fit(X_train_tfidf, y_train)

# 预测
y_pred = model.predict(X_test_tfidf)

# 评估
print("分类报告:")
print(classification_report(y_test, y_pred))

# 预测新文本
new_text = ["这个产品非常好，我很满意"]
new_tfidf = vectorizer.transform(new_text)
prediction = model.predict(new_tfidf)
print(f"\\n新文本 '{new_text[0]}' 的预测: {prediction[0]}")
```

### 深度学习方法：BERT

```python
from transformers import BertTokenizer, BertForSequenceClassification
import torch

# 加载预训练模型
tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')
model = BertForSequenceClassification.from_pretrained('bert-base-chinese', num_labels=2)

# 准备数据
texts = ["这个产品很好", "质量太差了"]
labels = [1, 0]  # 1: 正面, 0: 负面

# 编码
inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")

# 前向传播
outputs = model(**inputs, labels=torch.tensor(labels))

# 获取预测
logits = outputs.logits
predictions = torch.argmax(logits, dim=1)

print("预测结果:", predictions.tolist())

# 获取损失
loss = outputs.loss
print(f"损失: {loss.item():.4f}")
```

## 4. 命名实体识别（NER）

### 规则方法

```python
import re

def rule_based_ner(text):
    """基于规则的 NER"""
    entities = []

    # 识别电话号码
    phone_pattern = r'1[3-9]\d{9}'
    phones = re.findall(phone_pattern, text)
    for phone in phones:
        entities.append({
            "text": phone,
            "type": "PHONE",
            "start": text.index(phone),
            "end": text.index(phone) + len(phone)
        })

    # 识别邮箱
    email_pattern = r'\w+@\w+\.\w+'
    emails = re.findall(email_pattern, text)
    for email in emails:
        entities.append({
            "text": email,
            "type": "EMAIL",
            "start": text.index(email),
            "end": text.index(email) + len(email)
        })

    # 识别日期
    date_pattern = r'\d{4}年\d{1,2}月\d{1,2}日'
    dates = re.findall(date_pattern, text)
    for date in dates:
        entities.append({
            "text": date,
            "type": "DATE",
            "start": text.index(date),
            "end": text.index(date) + len(date)
        })

    return entities

text = "我的电话是13812345678，邮箱是test@example.com，今天日期是2024年1月1日"
entities = rule_based_ner(text)

print("识别的实体:")
for entity in entities:
    print(f"  {entity['type']}: {entity['text']}")
```

### 深度学习方法

```python
from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch

# 加载中文 NER 模型
tokenizer = AutoTokenizer.from_pretrained("ckiplab/bert-base-chinese-ner")
model = AutoModelForTokenClassification.from_pretrained("ckiplab/bert-base-chinese-ner")

def extract_entities(text):
    """抽取实体"""
    # 编码
    inputs = tokenizer(text, return_tensors="pt")

    # 预测
    with torch.no_grad():
        outputs = model(**inputs)

    # 解析结果
    predictions = torch.argmax(outputs.logits, dim=2)
    tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])

    entities = []
    current_entity = None

    for token, pred in zip(tokens, predictions[0]):
        if pred != 0:  # 非 O 标签
            label = model.config.id2label[pred.item()]

            if label.startswith("B-"):
                if current_entity:
                    entities.append(current_entity)
                current_entity = {
                    "text": token,
                    "type": label[2:]
                }
            elif label.startswith("I-") and current_entity:
                current_entity["text"] += token
        else:
            if current_entity:
                entities.append(current_entity)
                current_entity = None

    if current_entity:
        entities.append(current_entity)

    return entities

# 使用
text = "张三和李四在北京的科技公司工作"
entities = extract_entities(text)

print("识别的实体:")
for entity in entities:
    print(f"  {entity['type']}: {entity['text']}")
```

## 小结

本节介绍了 NLP 的基础知识：

- **文本预处理** - 分词、停用词
- **文本表示** - One-Hot、BoW、TF-IDF、Embeddings
- **文本分类** - 朴素贝叶斯、BERT
- **命名实体识别** - 规则、深度学习

## 实践练习

### 编程题
1. 使用 jieba 分词 + TF-IDF + 朴素贝叶斯，构建一个中文情感分类器，在测试集上达到 80% 以上的准确率。
2. 用 SentenceTransformer 将 10 个句子编码为向量，计算两两之间的余弦相似度，找出最相似和最不相似的句子对。

### 思考题
1. 中文分词相比英文分词有哪些额外的挑战？
2. TF-IDF 和词嵌入（Word Embedding）在文本表示上的本质区别是什么？

### 自测题
1. NLP 的四大任务分类是什么？
2. 词干化（Stemming）和词形还原（Lemmatization）的区别是什么？
3. One-Hot 编码的主要缺点是什么？

下一步将学习 NLP 高级技术（→ `02-nlp-advanced.md`）。