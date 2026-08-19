# GraphRAG：知识图谱增强的 RAG

## 什么是 GraphRAG？

GraphRAG 将知识图谱与 RAG 结合，利用结构化的知识来增强检索和生成的质量。

### GraphRAG vs 传统 RAG

```python
"""
传统 RAG:
用户问题 → 向量检索 → LLM 生成

问题: 可能丢失实体间的关系

GraphRAG:
用户问题 → 实体识别 → 图检索 → LLM 生成
         ↓
    关系推理

优势:
1. 保留实体关系
2. 支持多跳推理
3. 提供结构化上下文
"""
```

## 1. 实体识别与链接

```python
from typing import List, Dict, Tuple
from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch

class EntityRecognizer:
    def __init__(self, model_name="ckiplab/bert-base-chinese-ner"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForTokenClassification.from_pretrained(model_name)

    def recognize(self, text: str) -> List[Dict]:
        """识别文本中的实体"""
        inputs = self.tokenizer(text, return_tensors="pt")

        with torch.no_grad():
            outputs = self.model(**inputs)

        predictions = torch.argmax(outputs.logits, dim=2)
        tokens = self.tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])

        entities = []
        current_entity = None

        for token, pred in zip(tokens, predictions[0]):
            if pred != 0:  # 非 O 标签
                label = self.model.config.id2label[pred.item()]

                if label.startswith("B-"):
                    if current_entity:
                        entities.append(current_entity)
                    current_entity = {
                        "text": token,
                        "type": label[2:],
                        "start": 0,  # 简化
                        "end": 0
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

    def link_to_kg(self, entities: List[Dict], knowledge_graph) -> List[Dict]:
        """将实体链接到知识图谱"""
        linked_entities = []

        for entity in entities:
            # 在知识图谱中查找匹配的实体
            matches = self._find_matches(entity["text"], knowledge_graph)

            if matches:
                linked_entities.append({
                    "text": entity["text"],
                    "type": entity["type"],
                    "kg_id": matches[0]["id"],
                    "kg_label": matches[0]["label"],
                    "properties": matches[0].get("properties", {})
                })
            else:
                linked_entities.append({
                    "text": entity["text"],
                    "type": entity["type"],
                    "kg_id": None
                })

        return linked_entities

    def _find_matches(self, entity_text: str, kg, threshold=0.8) -> List[Dict]:
        """在知识图谱中查找匹配"""
        # 简化实现：使用模糊匹配
        from fuzzywuzzy import fuzz

        matches = []
        for node_id, node_data in kg.nodes(data=True):
            similarity = fuzz.ratio(entity_text, node_data.get("label", ""))
            if similarity >= threshold:
                matches.append({
                    "id": node_id,
                    "label": node_data.get("label"),
                    "similarity": similarity,
                    "properties": node_data
                })

        # 按相似度排序
        matches.sort(key=lambda x: x["similarity"], reverse=True)

        return matches

# 使用
import networkx as nx

# 创建简单知识图谱
kg = nx.DiGraph()
kg.add_node(1, label="张三", type="人物")
kg.add_node(2, label="李四", type="人物")
kg.add_node(3, label="科技公司", type="组织")
kg.add_edge(1, 2, relation="同事")
kg.add_edge(1, 3, relation="工作于")

# 识别和链接实体
recognizer = EntityRecognizer()
text = "张三和李四在科技公司工作"
entities = recognizer.recognize(text)
linked_entities = recognizer.link_to_kg(entities, kg)

print("识别的实体:", entities)
print("链接的实体:", linked_entities)
```

## 2. 子图检索

```python
from typing import Set

class SubgraphRetriever:
    def __init__(self, knowledge_graph: nx.DiGraph):
        self.kg = knowledge_graph

    def retrieve_by_entities(self, entity_ids: List[int], hops: int = 2) -> nx.DiGraph:
        """
        基于实体检索子图
        entity_ids: 起始实体ID列表
        hops: 跳数
        """
        subgraph = nx.DiGraph()
        visited = set(entity_ids)

        # BFS 遍历
        for hop in range(hops + 1):
            new_nodes = set()

            for node in visited:
                # 添加节点到子图
                if node in self.kg.nodes:
                    subgraph.add_node(node, **self.kg.nodes[node])

                # 获取邻居
                neighbors = list(self.kg.neighbors(node))
                for neighbor in neighbors:
                    if neighbor not in visited:
                        new_nodes.add(neighbor)

                        # 添加边
                        edge_data = self.kg.get_edge_data(node, neighbor)
                        subgraph.add_edge(node, neighbor, **edge_data)

            visited.update(new_nodes)

        return subgraph

    def retrieve_by_path(self, source: int, target: int, max_length: int = 3) -> nx.DiGraph:
        """基于路径检索子图"""
        try:
            # 查找所有简单路径
            paths = list(nx.all_simple_paths(
                self.kg, source, target, cutoff=max_length
            ))
        except nx.NetworkXNoPath:
            return nx.DiGraph()

        # 构建子图
        subgraph = nx.DiGraph()

        for path in paths:
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]

                # 添加节点和边
                subgraph.add_node(u, **self.kg.nodes[u])
                subgraph.add_node(v, **self.kg.nodes[v])

                edge_data = self.kg.get_edge_data(u, v)
                subgraph.add_edge(u, v, **edge_data)

        return subgraph

    def retrieve_by_relation(self, relation: str, entity_id: int) -> nx.DiGraph:
        """基于关系类型检索子图"""
        subgraph = nx.DiGraph()

        # 添加起始节点
        subgraph.add_node(entity_id, **self.kg.nodes[entity_id])

        # 添加所有指定类型的边
        for u, v, data in self.kg.out_edges(entity_id, data=True):
            if data.get("relation") == relation:
                subgraph.add_node(v, **self.kg.nodes[v])
                subgraph.add_edge(u, v, **data)

        return subgraph

# 使用
retriever = SubgraphRetriever(kg)

# 检索张三的2跳邻居
subgraph = retriever.retrieve_by_entities([1], hops=2)
print(f"子图节点: {list(subgraph.nodes())}")
print(f"子图边: {list(subgraph.edges(data=True))}")
```

## 3. GraphRAG Pipeline

```python
from langchain.schema import BaseRetriever, Document
from langchain_openai import ChatOpenAI
from typing import List

class GraphRAGRetriever(BaseRetriever):
    def __init__(self, kg: nx.DiGraph, llm: ChatOpenAI):
        self.kg = kg
        self.llm = llm
        self.entity_recognizer = EntityRecognizer()
        self.subgraph_retriever = SubgraphRetriever(kg)

    def _get_relevant_documents(self, query: str) -> List[Document]:
        """检索相关文档"""
        # 1. 识别查询中的实体
        entities = self.entity_recognizer.recognize(query)
        linked_entities = self.entity_recognizer.link_to_kg(entities, self.kg)

        # 2. 获取实体ID
        entity_ids = [e["kg_id"] for e in linked_entities if e["kg_id"] is not None]

        if not entity_ids:
            return []

        # 3. 检索子图
        subgraph = self.subgraph_retriever.retrieve_by_entities(entity_ids, hops=2)

        # 4. 将子图转换为文档
        documents = self._subgraph_to_documents(subgraph, query)

        return documents

    def _subgraph_to_documents(self, subgraph: nx.DiGraph, query: str) -> List[Document]:
        """将子图转换为文档"""
        documents = []

        # 实体文档
        for node_id, node_data in subgraph.nodes(data=True):
            content = f"实体：{node_data.get('label', node_id)}"
            if "type" in node_data:
                content += f"，类型：{node_data['type']}"
            if "properties" in node_data:
                content += f"，属性：{node_data['properties']}"

            documents.append(Document(
                content=content,
                metadata={
                    "type": "entity",
                    "id": node_id,
                    "data": node_data
                }
            ))

        # 关系文档
        for u, v, edge_data in subgraph.edges(data=True):
            u_label = subgraph.nodes[u].get("label", u)
            v_label = subgraph.nodes[v].get("label", v)
            relation = edge_data.get("relation", "unknown")

            content = f"{u_label} --{relation}--> {v_label}"

            documents.append(Document(
                content=content,
                metadata={
                    "type": "relation",
                    "source": u,
                    "target": v,
                    "relation": relation
                }
            ))

        # 路径文档（如果相关）
        paths = self._find_relevant_paths(subgraph, query)
        for path in paths:
            path_str = " -> ".join([subgraph.nodes[n].get("label", n) for n in path])
            documents.append(Document(
                content=f"路径：{path_str}",
                metadata={"type": "path", "nodes": path}
            ))

        return documents

    def _find_relevant_paths(self, subgraph: nx.DiGraph, query: str) -> List[List]:
        """查找相关路径"""
        # 使用 LLM 判断哪些路径相关
        all_paths = []
        nodes = list(subgraph.nodes())

        # 简化：只查找节点间的路径
        for i, source in enumerate(nodes):
            for target in nodes[i+1:]:
                try:
                    paths = list(nx.all_simple_paths(subgraph, source, target, cutoff=3))
                    all_paths.extend(paths)
                except:
                    continue

        # 使用 LLM 筛选
        path_descriptions = [
            " -> ".join([subgraph.nodes[n].get("label", n) for n in path])
            for path in all_paths
        ]

        prompt = f"""
        查询：{query}

        以下是一些知识图谱中的路径：
        {chr(10).join([f"{i+1}. {desc}" for i, desc in enumerate(path_descriptions)])}

        请返回与查询最相关的路径编号，用逗号分隔。
        """

        response = self.llm.invoke(prompt)
        selected_indices = [int(i) - 1 for i in response.content.split(",") if i.strip().isdigit()]

        return [all_paths[i] for i in selected_indices if 0 <= i < len(all_paths)]


# 创建 GraphRAG Pipeline
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

llm = ChatOpenAI(model="gpt-4")
graph_retriever = GraphRAGRetriever(kg, llm)

# 创建 Prompt
template = """
基于以下知识图谱信息回答问题：

知识图谱信息：
{context}

问题：{query}

答案：
"""

PROMPT = PromptTemplate(
    template=template,
    input_variables=["context", "query"]
)

# 创建 QA Chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=graph_retriever,
    chain_type_kwargs={"prompt": PROMPT},
    return_source_documents=True
)

# 使用
query = "张三和谁一起工作？"
result = qa_chain.invoke({"query": query})

print("答案:", result["result"])
print("来源:")
for doc in result["source_documents"]:
    print(f"  - {doc.content}")
```

## 4. 高级 GraphRAG 技术

### GraphRAG + 向量检索

```python
from haystack.components.retrievers import InMemoryEmbeddingRetriever
from haystack.document_stores.in_memory import InMemoryDocumentStore

class HybridGraphRAGRetriever:
    def __init__(self, kg: nx.DiGraph, doc_store: InMemoryDocumentStore, llm):
        self.kg = kg
        self.doc_store = doc_store
        self.llm = llm
        self.entity_recognizer = EntityRecognizer()
        self.graph_retriever = SubgraphRetriever(kg)
        self.vector_retriever = InMemoryEmbeddingRetriever(doc_store=doc_store)

    def retrieve(self, query: str, top_k: int = 5) -> List[Document]:
        """混合检索"""
        # 1. 图检索
        entities = self.entity_recognizer.recognize(query)
        linked_entities = self.entity_recognizer.link_to_kg(entities, self.kg)
        entity_ids = [e["kg_id"] for e in linked_entities if e["kg_id"] is not None]

        graph_docs = []
        if entity_ids:
            subgraph = self.graph_retriever.retrieve_by_entities(entity_ids)
            graph_docs = self._subgraph_to_documents(subgraph, query)

        # 2. 向量检索
        # 假设已经计算了查询的嵌入
        # vector_docs = self.vector_retriever.run(query_embedding=...)

        # 3. 合并和重排序
        all_docs = graph_docs  # + vector_docs

        # 使用知识图谱信息增强文档
        enhanced_docs = []
        for doc in all_docs:
            if doc.metadata.get("type") == "relation":
                # 从知识图谱中获取更多信息
                source = doc.metadata["source"]
                target = doc.metadata["target"]
                relation = doc.metadata["relation"]

                # 查找相关属性
                source_data = self.kg.nodes.get(source, {})
                target_data = self.kg.nodes.get(target, {})

                enhanced_content = doc.content
                if source_data:
                    enhanced_content += f"\\n来源实体属性：{source_data}"
                if target_data:
                    enhanced_content += f"\\n目标实体属性：{target_data}"

                enhanced_docs.append(Document(
                    content=enhanced_content,
                    metadata=doc.metadata
                ))
            else:
                enhanced_docs.append(doc)

        return enhanced_docs[:top_k]

    def _subgraph_to_documents(self, subgraph, query):
        # ... 与之前相同
        pass
```

### 多模态 GraphRAG

```python
class MultiModalGraphRAG:
    def __init__(self, kg: nx.DiGraph, image_retriever, text_retriever, llm):
        self.kg = kg
        self.image_retriever = image_retriever
        self.text_retriever = text_retriever
        self.llm = llm

    def retrieve(self, query: str) -> dict:
        """检索多模态信息"""
        result = {
            "text": [],
            "image": [],
            "graph": []
        }

        # 1. 文本检索
        text_docs = self.text_retriever.retrieve(query)
        result["text"] = text_docs

        # 2. 图像检索
        image_docs = self.image_retriever.retrieve(query)
        result["image"] = image_docs

        # 3. 图谱检索
        entities = self._extract_entities(query)
        linked_entities = self._link_to_kg(entities)

        if linked_entities:
            subgraph = self._retrieve_subgraph(linked_entities)
            result["graph"] = self._format_subgraph(subgraph)

        # 4. 多模态融合
        answer = self._fuse_multimodal(result, query)

        return {
            "answer": answer,
            "sources": result
        }

    def _fuse_multimodal(self, retrieved: dict, query: str) -> str:
        """融合多模态信息"""
        # 构建 prompt
        prompt = f"""
        问题：{query}

        文本信息：
        {self._format_text_sources(retrieved["text"])}

        知识图谱信息：
        {self._format_graph_sources(retrieved["graph"])}

        图像信息：
        有{len(retrieved["image"])}张相关图像

        请综合以上信息回答问题。
        """

        return self.llm.invoke(prompt).content
```

## 小结

本节介绍了 GraphRAG 技术：

- **实体识别链接** - NER + 知识图谱链接
- **子图检索** - 多跳、路径、关系检索
- **GraphRAG Pipeline** - 完整实现
- **高级技术** - 混合检索、多模态

## 实践练习

### 编程题
1. 基于 NetworkX 构建的知识图谱，实现一个简单的 GraphRAG 检索器：给定查询文本，识别实体，检索 2 跳子图，将子图信息转换为文本上下文。
2. 结合 LangChain 的 `RetrievalQA` 和自己实现的 `GraphRAGRetriever`，构建一个完整的图增强问答系统。

### 思考题
1. GraphRAG 在处理多跳推理问题时，相比传统向量检索有什么优势？
2. 混合检索（向量检索 + 图检索）中，如何确定两种检索结果的权重？

### 自测题
1. GraphRAG 的核心流程分为哪几步？
2. 子图检索的"跳数（hops）"设置过大或过小各有什么影响？
3. 实体链接（Entity Linking）为什么是 GraphRAG 的关键步骤？

下一步将学习 NLP 技术（→ `nlp/beginner/01-nlp-basics.md`）。