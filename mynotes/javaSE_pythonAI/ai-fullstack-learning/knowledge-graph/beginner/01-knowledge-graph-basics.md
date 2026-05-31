# 知识图谱基础入门

## 什么是知识图谱？

知识图谱是一种用图结构来表示知识的系统，包含**实体**（节点）、**关系**（边）和**属性**。

### 核心概念

```
┌─────────┐     ┌─────────┐     ┌─────────┐
│  实体1   │────▶│  关系    │────▶│  实体2   │
│ (Node)  │     │ (Edge)  │     │ (Node)  │
└─────────┘     └─────────┘     └─────────┘
     │                               │
     ↓                               ↓
  ┌─────┐                         ┌─────┐
  │属性1│                         │属性2│
  └─────┘                         └─────┘
```

### 示例知识图谱

```python
# 人物关系图谱
"""
[张三] --朋友--> [李四]
  |                    |
  |同事                |同事
  ↓                    ↓
[王五] --同学--> [赵六]

[张三] --工作于--> [科技公司]
                       |
                       |位于
                       ↓
                    [北京]
"""
```

## 知识图谱的表示

### RDF（Resource Description Framework）

```python
# RDF 三元组表示
triples = [
    ("张三", "朋友", "李四"),
    ("张三", "同事", "王五"),
    ("李四", "同事", "赵六"),
    ("王五", "同学", "赵六"),
    ("张三", "工作于", "科技公司"),
    ("科技公司", "位于", "北京")
]

# 可视化
from graphviz import Digraph

dot = Digraph()

# 添加节点
entities = set()
for s, p, o in triples:
    entities.add(s)
    entities.add(o)

for entity in entities:
    dot.node(entity)

# 添加边
for s, p, o in triples:
    dot.edge(s, o, label=p)

dot.render('knowledge_graph', view=True)
```

### JSON-LD 格式

```python
# JSON-LD 格式示例
knowledge_graph = {
    "@context": {
        "name": "http://xmlns.com/foaf/0.1/name",
        "friend": "http://xmlns.com/foaf/0.1/knows",
        "worksAt": "http://schema.org/worksFor",
        "locatedIn": "http://schema.org/location"
    },
    "@graph": [
        {
            "@id": "person1",
            "name": "张三",
            "friend": {"@id": "person2"},
            "worksAt": {"@id": "company1"}
        },
        {
            "@id": "person2",
            "name": "李四",
            "friend": {"@id": "person3"}
        },
        {
            "@id": "company1",
            "name": "科技公司",
            "locatedIn": {"@id": "city1"}
        },
        {
            "@id": "city1",
            "name": "北京"
        }
    ]
}

import json
print(json.dumps(knowledge_graph, indent=2, ensure_ascii=False))
```

## Python 知识图谱库

### NetworkX（基础图操作）

```python
import networkx as nx
import matplotlib.pyplot as plt

# 创建图
G = nx.DiGraph()

# 添加节点和属性
G.add_node("张三", age=30, job="工程师")
G.add_node("李四", age=28, job="设计师")
G.add_node("王五", age=32, job="产品经理")
G.add_node("科技公司", type="organization")
G.add_node("北京", type="city")

# 添加边和属性
G.add_edge("张三", "李四", relation="朋友", since=2018)
G.add_edge("张三", "王五", relation="同事", since=2019)
G.add_edge("张三", "科技公司", relation="工作于", since=2020)
G.add_edge("科技公司", "北京", relation="位于")

# 查询
print("张三的朋友:")
friends = [n for n in G.successors("张三") if G.edges["张三", n]["relation"] == "朋友"]
print(friends)

# 最短路径
print("\\n从张三到北京的最短路径:")
path = nx.shortest_path(G, "张三", "北京")
print(" -> ".join(path))

# 可视化
plt.figure(figsize=(10, 6))
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_size=2000, node_color="lightblue",
        font_size=10, arrows=True)
edge_labels = nx.get_edge_attributes(G, "relation")
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
plt.show()
```

### Neo4j（专业图数据库）

```python
# Neo4j Python 驱动
from neo4j import GraphDatabase

class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_person(self, name, age, job):
        with self.driver.session() as session:
            session.run("""
                CREATE (p:Person {name: $name, age: $age, job: $job})
            """, name=name, age=age, job=job)

    def create_relationship(self, person1, person2, relation_type):
        with self.driver.session() as session:
            session.run(f"""
                MATCH (p1:Person {{name: $person1}})
                MATCH (p2:Person {{name: $person2}})
                CREATE (p1)-[:{relation_type}]->(p2)
            """, person1=person1, person2=person2)

    def find_friends(self, name):
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Person {name: $name})-[:朋友]->(friend:Person)
                RETURN friend.name, friend.age
            """, name=name)
            return [record for record in result]

    def find_shortest_path(self, person1, person2):
        with self.driver.session() as session:
            result = session.run("""
                MATCH path = shortestPath(
                    (p1:Person {name: $person1})-[*]-(p2:Person {name: $person2})
                )
                RETURN [node in nodes(path) | node.name] as path
            """, person1=person1, person2=person2)
            return result.single()[0]

# 使用
conn = Neo4jConnection("bolt://localhost:7687", "neo4j", "password")

# 创建数据
conn.create_person("张三", 30, "工程师")
conn.create_person("李四", 28, "设计师")

# 创建关系
conn.create_relationship("张三", "李四", "朋友")

# 查询
friends = conn.find_friends("张三")
print(f"张三的朋友: {friends}")

path = conn.find_shortest_path("张三", "李四")
print(f"最短路径: {' -> '.join(path)}")

conn.close()
```

### PyTorch Geometric（图神经网络）

```python
import torch
from torch_geometric.data import Data
from torch_geometric.nn import GCNConv
import torch.nn.functional as F

# 创建图数据
# 节点特征矩阵
x = torch.tensor([
    [1, 0],  # 节点0
    [0, 1],  # 节点1
    [1, 1],  # 节点2
], dtype=torch.float)

# 边索引 (每列是一条边)
edge_index = torch.tensor([
    [0, 1, 1, 2],  # 源节点
    [1, 0, 2, 1],  # 目标节点
], dtype=torch.long)

# 创建图数据对象
data = Data(x=x, edge_index=edge_index)

# 定义 GCN 模型
class GCN(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = GCNConv(2, 4)
        self.conv2 = GCNConv(4, 2)

    def forward(self, data):
        x, edge_index = data.x, data.edge_index
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = self.conv2(x, edge_index)
        return x

# 使用模型
model = GCN()
output = model(data)
print("节点嵌入:")
print(output)
```

## 知识图谱构建流程

### 1. 数据收集

```python
import requests
from bs4 import BeautifulSoup
import pandas as pd

# 从网络收集数据
def scrape_wikipedia_topic(topic: str):
    """抓取 Wikipedia 主题"""
    url = f"https://zh.wikipedia.org/wiki/{topic}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # 提取标题
    title = soup.find('h1').text

    # 提取链接
    links = []
    for a in soup.find_all('a', href=True):
        if a['href'].startswith('/wiki/'):
            links.append(a.text)

    return {
        "title": title,
        "links": links[:10]  # 取前10个链接
    }

# 使用
data = scrape_wikipedia_topic("人工智能")
print(data)
```

### 2. 实体抽取（NER）

```python
from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch

# 加载中文 NER 模型
tokenizer = AutoTokenizer.from_pretrained("ckiplab/bert-base-chinese-ner")
model = AutoModelForTokenClassification.from_pretrained("ckiplab/bert-base-chinese-ner")

def extract_entities(text: str):
    """抽取实体"""
    # 标记化
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
            if label.startswith("B-"):  # 实体开始
                if current_entity:
                    entities.append(current_entity)
                current_entity = {"text": token, "type": label[2:]}
            elif label.startswith("I-") and current_entity:  # 实体继续
                current_entity["text"] += token
        else:
            if current_entity:
                entities.append(current_entity)
                current_entity = None

    if current_entity:
        entities.append(current_entity)

    return entities

# 使用
text = "张三和李四在北京的科技公司工作，他们是同事。"
entities = extract_entities(text)
for entity in entities:
    print(f"{entity['type']}: {entity['text']}")
```

### 3. 关系抽取

```python
from transformers import pipeline

# 使用关系抽取模型
relation_extractor = pipeline("zero-shot-classification",
    model="facebook/bart-large-mnli")

def extract_relation(subject, object_, context):
    """抽取关系"""
    # 定义可能的关系类型
    relation_labels = [
        "朋友", "同事", "家人",
        "工作于", "居住在", "位于",
        "创立", "拥有", "使用"
    ]

    # 构造输入
    input_text = f"{subject} 和 {object_} 的关系：{context}"

    # 预测关系
    result = relation_extractor(
        input_text,
        relation_labels
    )

    return result["labels"][0], result["scores"][0]

# 使用
relation, confidence = extract_relation(
    "张三", "李四", "张三和李四经常一起工作"
)
print(f"关系: {relation}, 置信度: {confidence:.2f}")
```

### 4. 知识融合

```python
from fuzzywuzzy import fuzz

def merge_entities(entities1, entities2, threshold=80):
    """合并相似的实体"""
    merged = entities1.copy()

    for entity2 in entities2:
        found = False
        for entity1 in merged:
            # 计算相似度
            similarity = fuzz.ratio(entity1["text"], entity2["text"])

            if similarity >= threshold:
                # 合并属性
                entity1["aliases"] = entity1.get("aliases", []) + [entity2["text"]]
                entity1["types"] = list(set(entity1.get("types", []) + entity2.get("types", [])))
                found = True
                break

        if not found:
            merged.append(entity2)

    return merged

# 使用
entities1 = [
    {"text": "张三", "type": "人物"},
    {"text": "北京", "type": "地点"}
]

entities2 = [
    {"text": "张三", "type": "人物"},
    {"text": "北京市", "type": "地点"}
]

merged = merge_entities(entities1, entities2)
print(merged)
```

## 知识图谱查询

### SPARQL 查询

```python
from rdflib import Graph, Namespace, Literal, RDF, RDFS

# 创建 RDF 图
g = Graph()

# 定义命名空间
ex = Namespace("http://example.org/")
g.bind("ex", ex)

# 添加三元组
g.add((ex.ZhangSan, RDF.type, ex.Person))
g.add((ex.ZhangSan, ex.name, Literal("张三")))
g.add((ex.ZhangSan, ex.age, Literal(30)))
g.add((ex.ZhangSan, ex.friend, ex.LiSi))
g.add((ex.LiSi, RDF.type, ex.Person))
g.add((ex.LiSi, ex.name, Literal("李四")))

# SPARQL 查询
query = """
SELECT ?name ?age
WHERE {
    ?person ex:friend ex:LiSi .
    ?person ex:name ?name .
    ?person ex:age ?age .
}
"""

results = g.query(query)
for row in results:
    print(f"姓名: {row.name}, 年龄: {row.age}")
```

## 小结

本节介绍了知识图谱的基础：

- **概念** - 实体、关系、属性
- **表示** - RDF, JSON-LD
- **工具** - NetworkX, Neo4j, PyG
- **构建** - 抽取、融合
- **查询** - SPARQL

## 实践练习

### 编程题
1. 使用 NetworkX 构建一个公司员工关系图（至少 5 个节点），包括"同事""上下级""朋友"三种关系，可视化并查询所有直接关系。
2. 连接 Neo4j 数据库，用 Cypher 查询实现：查找某人所有朋友的同事。

### 思考题
1. 知识图谱和传统关系型数据库在存储实体关系上有什么本质区别？
2. 实体消歧（Entity Disambiguation）在知识图谱构建中的重要性体现在哪里？

### 自测题
1. RDF 三元组由哪三部分组成？
2. NetworkX 和 Neo4j 的适用场景有什么不同？
3. SPARQL 和 Cypher 分别用于查询什么类型的图数据库？

下一步将学习知识图谱推理技术（→ `02-knowledge-graph-reasoning.md`）。