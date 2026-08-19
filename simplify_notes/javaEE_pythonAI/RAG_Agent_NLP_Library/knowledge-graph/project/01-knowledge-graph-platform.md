# 知识图谱平台实战

## 一、项目概述

构建一个企业级知识图谱平台，支持从非结构化文本中抽取实体关系、图存储与查询、图谱可视化展示。

### 技术栈

| 组件 | 选型 | 说明 |
|------|------|------|
| NLP 抽取 | spaCy + Gliner + LLM | NER + RE |
| 图数据库 | Neo4j | 原生图存储 |
| 知识推理 | OpenAI + GraphRAG | 基于图的问答 |
| 可视化 | D3.js / G6 | 前端展示 |
| 存储 | PostgreSQL | 元数据管理 |
| 接口 | FastAPI | RESTful API |

## 二、系统架构

```
┌──────────────┐    ┌─────────────────┐    ┌──────────────┐
│  文档输入     │───▶│  实体关系抽取    │───▶│  知识融合     │
│  PDF/网页/文本 │    │  NER + RE + LLM │    │  去重/对齐    │
└──────────────┘    └────────┬────────┘    └──────┬───────┘
                             │                    │
                             └────────┬───────────┘
                                      │
                               ┌──────▼──────┐
                               │   Neo4j      │
                               │  图数据库     │
                               └──────┬──────┘
                                      │
                    ┌─────────────────┼──────────────┐
                    │                 │              │
               ┌────▼────┐    ┌──────▼──────┐  ┌────▼────┐
               │ GraphRAG │    │  查询API    │  │  可视化  │
               │  问答    │    │  Cypher     │  │  D3.js   │
               └─────────┘    └─────────────┘  └─────────┘
```

## 三、实体关系抽取

### LLM 驱动的抽取

```python
from openai import OpenAI
from pydantic import BaseModel, Field
import json

class Entity(BaseModel):
    name: str = Field(description="实体名称")
    type: str = Field(description="实体类型: PERSON/ORG/LOC/DATE/PRODUCT/CONCEPT")
    attributes: dict = Field(default={}, description="实体属性")

class Relation(BaseModel):
    source: str = Field(description="源实体名称")
    target: str = Field(description="目标实体名称")
    type: str = Field(description="关系类型")

class KnowledgeGraph(BaseModel):
    entities: list[Entity]
    relations: list[Relation]

class KnowledgeExtractor:
    def __init__(self, model="gpt-4o-mini"):
        self.client = OpenAI()
        self.model = model

    def extract_from_text(self, text: str) -> KnowledgeGraph:
        prompt = f"""从以下文本中抽取实体和关系：

文本：{text}

要求：
1. 识别人名、组织、地点、时间、产品、概念等实体
2. 识别实体间的语义关系（工作于、位于、成立于、收购等）
3. 每个实体附带简要属性
4. 返回完整的知识图谱结构"""
        
        response = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format=KnowledgeGraph
        )
        return response.choices[0].message.parsed

    def extract_batch(self, texts: list[str], batch_size=5) -> list[KnowledgeGraph]:
        """批量抽取，合并相同实体"""
        graphs = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            combined = "\n---\n".join(batch)
            graph = self.extract_from_text(combined)
            graphs.append(graph)
        return self._merge_graphs(graphs)

    def _merge_graphs(self, graphs: list[KnowledgeGraph]) -> KnowledgeGraph:
        """合并多个图谱，去重"""
        entities_dict = {}
        relations_set = set()
        
        for graph in graphs:
            for entity in graph.entities:
                key = entity.name.lower()
                if key in entities_dict:
                    # 合并属性
                    entities_dict[key].attributes.update(entity.attributes)
                else:
                    entities_dict[key] = entity
            for rel in graph.relations:
                relations_set.add((rel.source.lower(), rel.type, rel.target.lower()))
        
        return KnowledgeGraph(
            entities=list(entities_dict.values()),
            relations=[Relation(source=s, type=t, target=o) for s, t, o in relations_set]
        )
```

### 规则辅助抽取

```python
import re
from collections import defaultdict

def extract_with_regex(text: str) -> tuple[list, list]:
    """基于正则的辅助抽取"""
    entities = []
    
    # 邮箱
    emails = re.findall(r'\b[\w.+-]+@[\w-]+\.[\w.-]+\b', text)
    for e in emails:
        entities.append(Entity(name=e, type="EMAIL"))
    
    # URL
    urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', text)
    for u in urls:
        entities.append(Entity(name=u, type="URL"))
    
    # 金额
    amounts = re.findall(r'[¥$€]\s*\d+(?:,\d{3})*(?:\.\d+)?', text)
    for a in amounts:
        entities.append(Entity(name=a, type="AMOUNT"))
    
    return entities, []
```

## 四、图数据库操作

### Neo4j 集成

```python
from neo4j import GraphDatabase, Driver

class Neo4jClient:
    def __init__(self, uri: str, user: str, password: str):
        self.driver: Driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_graph(self, graph: KnowledgeGraph):
        with self.driver.session() as session:
            # 创建实体
            for entity in graph.entities:
                session.run(
                    f"MERGE (e:{entity.type} {{name: $name}}) "
                    "SET e += $attributes",
                    name=entity.name,
                    attributes=entity.attributes
                )
            # 创建关系
            for rel in graph.relations:
                session.run(
                    f"MATCH (s {{name: $source}}) "
                    f"MATCH (t {{name: $target}}) "
                    f"MERGE (s)-[r:{rel.type}]->(t) "
                    "SET r.weight = COALESCE(r.weight, 0) + 1",
                    source=rel.source, target=rel.target
                )

    def query_entity_relations(self, entity_name: str, depth: int = 2) -> list:
        with self.driver.session() as session:
            result = session.run(
                f"MATCH (s {{name: $name}})-[r*1..{depth}]-(t) "
                "RETURN s, r, t LIMIT 100",
                name=entity_name
            )
            return [record.data() for record in result]

    def search_by_type(self, entity_type: str, limit: int = 50) -> list:
        with self.driver.session() as session:
            result = session.run(
                f"MATCH (e:{entity_type}) RETURN e.name AS name, "
                "labels(e) AS type, e LIMIT $limit",
                limit=limit
            )
            return [record.data() for record in result]
```

### 图算法应用

```python
from neo4j import GraphDatabase

class GraphAlgorithms:
    def __init__(self, client: Neo4jClient):
        self.driver = client.driver

    def pagerank(self) -> dict:
        """PageRank 计算节点重要性"""
        with self.driver.session() as session:
            result = session.run(
                "CALL gds.pageRank.stream('kg-graph') "
                "YIELD nodeId, score "
                "RETURN gds.util.asNode(nodeId).name AS name, score "
                "ORDER BY score DESC LIMIT 20"
            )
            return {record["name"]: record["score"] for record in result}

    def community_detection(self) -> dict:
        """Louvain 社区发现"""
        with self.driver.session() as session:
            result = session.run(
                "CALL gds.louvain.stream('kg-graph') "
                "YIELD nodeId, communityId "
                "RETURN communityId, COLLECT(gds.util.asNode(nodeId).name) AS members"
            )
            return {record["communityId"]: record["members"] for record in result}

    def shortest_path(self, source: str, target: str) -> list:
        """最短路径分析"""
        with self.driver.session() as session:
            result = session.run(
                "MATCH (s {name: $source}), (t {name: $target}) "
                "CALL gds.shortestPath.dijkstra.stream('kg-graph', {"
                "  sourceNode: s, targetNode: t, "
                "  relationshipWeightProperty: 'weight'"
                "}) "
                "YIELD nodeIds, costs "
                "RETURN [nodeId IN nodeIds | gds.util.asNode(nodeId).name] AS path, costs",
                source=source, target=target
            )
            return result.single()["path"]
```

## 五、GraphRAG 问答

```python
from openai import OpenAI
from neo4j import GraphDatabase

class GraphRAG:
    """基于知识图谱的 RAG 系统"""

    def __init__(self, neo4j_client: Neo4jClient):
        self.neo4j = neo4j_client
        self.llm = OpenAI()

    def answer(self, question: str) -> dict:
        # 1. 识别问题中的实体
        entities = self._extract_query_entities(question)
        
        # 2. 从图数据库检索子图
        subgraph = self._retrieve_subgraph(entities, depth=2)
        
        # 3. 生成结构化上下文
        context = self._subgraph_to_text(subgraph)
        
        # 4. LLM 生成答案
        answer = self._generate(question, context)
        
        return {
            "answer": answer,
            "evidence": subgraph[:10]  # top-10 证据子图
        }

    def _extract_query_entities(self, question: str) -> list[str]:
        response = self.llm.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"从问题中提取关键实体名称（中文名、英文名）：\n{question}"}]
        )
        return [e.strip() for e in response.choices[0].message.content.split("\n") if e.strip()]

    def _retrieve_subgraph(self, entities: list[str], depth: int) -> list:
        with self.neo4j.driver.session() as session:
            results = []
            for entity in entities:
                result = session.run(
                    f"MATCH (s)-[r*1..{depth}]-(t) "
                    "WHERE s.name CONTAINS $entity "
                    "RETURN s, r, t LIMIT 50",
                    entity=entity
                )
                results.extend([r.data() for r in result])
            return results

    def _subgraph_to_text(self, subgraph: list) -> str:
        contexts = set()
        for record in subgraph:
            nodes = []
            for key in record:
                if isinstance(record[key], dict) and "name" in record[key]:
                    nodes.append(record[key]["name"])
            if len(nodes) >= 2:
                contexts.add(f"{nodes[0]} --相关--> {nodes[1]}")
        return "\n".join(list(contexts)[:20])
```

## 六、可视化

### 前端展示 (G6)

```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://unpkg.com/@antv/g6@5"></script>
</head>
<body>
  <div id="graph-container" style="width: 100%; height: 600px;"></div>
  <script>
    fetch('/api/graph/query?name=Apple')
      .then(res => res.json())
      .then(data => {
        const graph = new G6.Graph({
          container: 'graph-container',
          width: 1200,
          height: 600,
          layout: { type: 'force', preventOverlap: true },
          defaultNode: { style: { fill: '#91d5ff', stroke: '#1890ff' } },
          defaultEdge: { style: { stroke: '#e8e8e8' } }
        });
        graph.data(transformToG6(data));
        graph.render();
      });

    function transformToG6(data) {
      const nodes = data.entities.map(e => ({
        id: e.name, label: e.name, group: e.type
      }));
      const edges = data.relations.map(r => ({
        source: r.source, target: r.target, label: r.type
      }));
      return { nodes, edges };
    }
  </script>
</body>
</html>
```

## 七、面试考点

1. **知识图谱与向量数据库的区别？** 图谱擅长多跳推理和关系查询，向量库擅长语义相似度搜索
2. **实体对齐怎么做？** 编辑距离 + 向量相似度 + 同义词映射，结合规则和模型
3. **大规模图谱如何优化查询？** 索引（Composites indexes）+ 分区 + 缓存热节点
4. **GraphRAG 比传统 RAG 强在哪？** 利用关系路径进行多跳推理，答案更准确

## 八、课后练习

1. 实现一个实体对齐模块，合并 "Apple Inc." 和 "Apple" 等别名
2. 开发一个 Cypher Query Builder，将自然语言转换为图查询
3. 为图谱添加时间维度，支持 "2024年之前的事件" 查询
4. 使用 GDS 库实现知识图谱上的社区发现

## 自测题

1. Neo4j 的 Cypher 查询中 `MATCH (a)-[r*1..3]->(b)` 的含义？ A) 精确匹配 B) 1到3跳关系 C) 正则匹配 D) 模糊匹配
2. 知识图谱中 NER 的任务是？ A) 关系抽取 B) 实体识别 C) 文本分类 D) 情感分析
3. GraphRAG 相比向量 RAG 的主要优势？ A) 速度快 B) 支持多跳推理 C) 存储成本低 D) 不需要 Embedding

**答案：** 1-B, 2-B, 3-B
