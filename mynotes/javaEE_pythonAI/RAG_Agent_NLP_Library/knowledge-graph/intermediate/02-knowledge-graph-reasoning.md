# 知识图谱推理

## 什么是知识图谱推理？

推理是从已知知识中推导出新知识的过程。

### 推理类型

```python
"""
1. 简单推理（一步推理）
   已知: A是B的朋友
        B是C的朋友
   推导: A认识C（传递性）

2. 多步推理
   已知: A工作于X公司
        X公司位于北京
   推导: A在北京工作

3. 不确定性推理
   已知: A可能是B的亲戚（置信度0.8）
   推导: B可能是A的亲戚（置信度0.8）

4. 归纳推理
   已知: 所有观察到的X都是Y
   推导: 所有X都是Y
"""
```

## 1. 基于规则的推理

### Horn Clause 推理

```python
from typing import List, Dict, Tuple

class RuleEngine:
    def __init__(self):
        self.facts = set()
        self.rules = []

    def add_fact(self, fact: Tuple):
        """添加事实"""
        self.facts.add(fact)

    def add_rule(self, conditions: List[Tuple], conclusion: Tuple):
        """
        添加规则
        conditions: 前提条件列表
        conclusion: 结论
        """
        self.rules.append({
            "conditions": conditions,
            "conclusion": conclusion
        })

    def forward_chaining(self):
        """前向推理（从已知事实推导新知识）"""
        changed = True

        while changed:
            changed = False
            new_facts = []

            for rule in self.rules:
                # 检查所有条件是否满足
                conditions_met = all(
                    self._match_condition(condition)
                    for condition in rule["conditions"]
                )

                if conditions_met and rule["conclusion"] not in self.facts:
                    new_facts.append(rule["conclusion"])
                    self.facts.add(rule["conclusion"])
                    changed = True

            if new_facts:
                print(f"推导出新事实: {new_facts}")

    def _match_condition(self, condition: Tuple) -> bool:
        """检查条件是否满足"""
        # 简化实现：直接检查事实
        return condition in self.facts

    def backward_chaining(self, goal: Tuple) -> bool:
        """后向推理（从目标反向推导）"""
        # 检查是否已经是事实
        if goal in self.facts:
            return True

        # 尝试找到可以推导出目标的规则
        for rule in self.rules:
            if rule["conclusion"] == goal:
                # 递归检查所有前提
                if all(self.backward_chaining(cond) for cond in rule["conditions"]):
                    return True

        return False

# 使用示例
engine = RuleEngine()

# 添加事实
engine.add_fact(("张三", "朋友", "李四"))
engine.add_fact(("李四", "朋友", "王五"))
engine.add_fact(("朋友", "传递性", True))

# 添加规则
engine.add_rule(
    conditions=[("A", "朋友", "B"), ("B", "朋友", "C"), ("朋友", "传递性", True)],
    conclusion=("A", "认识", "C")
)

# 前向推理
print("=== 前向推理 ===")
engine.forward_chaining()
print(f"所有事实: {engine.facts}")

# 后向推理
print("\\n=== 后向推理 ===")
goal = ("张三", "认识", "王五")
result = engine.backward_chaining(goal)
print(f"目标 {goal} 可以被推导: {result}")
```

### 传递性推理

```python
class TransitivityReasoner:
    def __init__(self, graph):
        self.graph = graph

    def infer_transitive_relations(self, relation: str, max_depth: int = 3):
        """
        推导传递性关系
        relation: 关系类型
        max_depth: 最大推导深度
        """
        inferred_relations = set()

        for source in self.graph.nodes():
            visited = {source}
            queue = [(source, 0)]

            while queue:
                current, depth = queue.pop(0)

                if depth >= max_depth:
                    continue

                for neighbor in self.graph.successors(current):
                    # 检查边的关系类型
                    edge_data = self.graph.get_edge_data(current, neighbor)
                    if edge_data and edge_data.get("relation") == relation:
                        if neighbor not in visited:
                            # 如果不是直接连接，则为推导出的关系
                            if depth > 0:
                                inferred_relations.add((source, neighbor, relation, depth + 1))
                            visited.add(neighbor)
                            queue.append((neighbor, depth + 1))

        return inferred_relations

# 使用
import networkx as nx

G = nx.DiGraph()
G.add_edge("A", "B", relation="朋友")
G.add_edge("B", "C", relation="朋友")
G.add_edge("C", "D", relation="朋友")

reasoner = TransitivityReasoner(G)
inferred = reasoner.infer_transitive_relations("朋友")

print("推导出的关系:")
for src, dst, rel, depth in inferred:
    print(f"{src} --{rel}({depth}步)--> {dst}")
```

### 反关系推理

```python
class InverseRelationReasoner:
    def __init__(self, inverse_relations: Dict[str, str]):
        """
        inverse_relations: 反关系映射
        {"朋友": "朋友", "父": "子", "工作于": "雇主"}
        """
        self.inverse_relations = inverse_relations

    def infer_inverse(self, graph: nx.DiGraph) -> nx.DiGraph:
        """推导反关系"""
        new_graph = graph.copy()

        for u, v, data in graph.edges(data=True):
            relation = data.get("relation")

            if relation in self.inverse_relations:
                inverse_rel = self.inverse_relations[relation]

                # 添加反关系边
                if not new_graph.has_edge(v, u):
                    new_graph.add_edge(v, u, relation=inverse_rel, inferred=True)

        return new_graph

# 使用
G = nx.DiGraph()
G.add_edge("张三", "李四", relation="朋友")
G.add_edge("王五", "赵六", relation="父")

reasoner = InverseRelationReasoner({
    "朋友": "朋友",
    "父": "子",
    "工作于": "雇主"
})

inferred_graph = reasoner.infer_inverse(G)

print("原始图边:", list(G.edges()))
print("推导后图边:", list(inferred_graph.edges()))
```

## 2. 路径推理

### 多跳推理

```python
class PathReasoner:
    def __init__(self, graph: nx.DiGraph):
        self.graph = graph

    def find_all_paths(self, source: str, target: str, max_length: int = 5):
        """查找所有路径"""
        paths = []

        def dfs(current, target, path, visited):
            if len(path) > max_length:
                return

            if current == target:
                paths.append(path.copy())
                return

            for neighbor in self.graph.successors(current):
                if neighbor not in visited:
                    edge_data = self.graph.get_edge_data(current, neighbor)
                    visited.add(neighbor)
                    path.append((current, neighbor, edge_data.get("relation")))
                    dfs(neighbor, target, path, visited)
                    path.pop()
                    visited.remove(neighbor)

        dfs(source, target, [], {source})
        return paths

    def find_shortest_path(self, source: str, target: str):
        """查找最短路径"""
        try:
            path = nx.shortest_path(self.graph, source, target)
            edges = []
            for i in range(len(path) - 1):
                edge_data = self.graph.get_edge_data(path[i], path[i + 1])
                edges.append((path[i], path[i + 1], edge_data.get("relation")))
            return edges
        except nx.NetworkXNoPath:
            return None

    def semantic_path(self, source: str, target: str, relation_type: str):
        """查找特定关系类型的路径"""
        # 创建只包含特定关系类型的子图
        subgraph = nx.DiGraph()

        for u, v, data in self.graph.edges(data=True):
            if data.get("relation") == relation_type:
                subgraph.add_edge(u, v, **data)

        # 在子图中查找路径
        if source not in subgraph or target not in subgraph:
            return None

        try:
            path = nx.shortest_path(subgraph, source, target)
            return path
        except nx.NetworkXNoPath:
            return None

# 使用
G = nx.DiGraph()
G.add_edge("张三", "李四", relation="朋友")
G.add_edge("李四", "王五", relation="同事")
G.add_edge("王五", "赵六", relation="同学")
G.add_edge("张三", "赵六", relation="朋友")

reasoner = PathReasoner(G)

# 查找所有路径
paths = reasoner.find_all_paths("张三", "赵六")
print("\\n所有路径:")
for i, path in enumerate(paths, 1):
    print(f"路径{i}: {' -> '.join([f'{u}[{rel}]{v}' for u, v, rel in path])}")

# 查找最短路径
shortest = reasoner.find_shortest_path("张三", "赵六")
print("\\n最短路径:", shortest)
```

### 概率路径推理

```python
import numpy as np

class ProbabilisticPathReasoner:
    def __init__(self, graph: nx.DiGraph):
        self.graph = graph

    def find_most_likely_path(self, source: str, target: str):
        """
        查找最可能的路径
        假设每条边有概率属性
        """
        # 动态规划
        best_prob = {node: 0 for node in self.graph.nodes()}
        best_path = {node: None for node in self.graph.nodes()}

        best_prob[source] = 1.0

        # BFS 遍历
        for node in nx.topological_sort(self.graph):
            for neighbor in self.graph.successors(node):
                edge_data = self.graph.get_edge_data(node, neighbor)
                edge_prob = edge_data.get("probability", 0.5)

                new_prob = best_prob[node] * edge_prob
                if new_prob > best_prob[neighbor]:
                    best_prob[neighbor] = new_prob
                    best_path[neighbor] = node

        # 重建路径
        if best_prob[target] > 0:
            path = []
            current = target
            while current != source:
                path.append(current)
                current = best_path[current]
            path.append(source)
            path.reverse()
            return path, best_prob[target]
        else:
            return None, 0

    def monte_carlo_path_sampling(self, source: str, target: str, num_samples: int = 1000):
        """
        蒙特卡洛路径采样
        估计从源到目标的概率
        """
        success_count = 0

        for _ in range(num_samples):
            current = source
            visited = {source}

            while current != target:
                neighbors = [n for n in self.graph.successors(current) if n not in visited]

                if not neighbors:
                    break

                # 根据概率选择下一个节点
                probs = []
                for neighbor in neighbors:
                    edge_data = self.graph.get_edge_data(current, neighbor)
                    probs.append(edge_data.get("probability", 0.5))

                # 归一化
                total = sum(probs)
                probs = [p / total for p in probs]

                # 随机选择
                chosen = np.random.choice(neighbors, p=probs)
                visited.add(chosen)
                current = chosen

            if current == target:
                success_count += 1

        return success_count / num_samples

# 使用
G = nx.DiGraph()
G.add_edge("A", "B", relation="connects", probability=0.9)
G.add_edge("A", "C", relation="connects", probability=0.1)
G.add_edge("B", "D", relation="connects", probability=0.8)
G.add_edge("C", "D", relation="connects", probability=0.2)
G.add_edge("D", "E", relation="connects", probability=0.7)

reasoner = ProbabilisticPathReasoner(G)

# 最可能路径
path, prob = reasoner.find_most_likely_path("A", "E")
print(f"最可能路径: {path}, 概率: {prob:.4f}")

# 蒙特卡洛估计
mc_prob = reasoner.monte_carlo_path_sampling("A", "E", num_samples=10000)
print(f"蒙特卡洛估计概率: {mc_prob:.4f}")
```

## 3. 基于嵌入的推理

### TransE 模型

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class TransE(nn.Module):
    """
    TransE: 嵌入翻译模型
    h + r ≈ t (头实体 + 关系 ≈ 尾实体)
    """
    def __init__(self, num_entities, num_relations, embedding_dim):
        super().__init__()
        self.entity_embeddings = nn.Embedding(num_entities, embedding_dim)
        self.relation_embeddings = nn.Embedding(num_relations, embedding_dim)

        # 归一化嵌入
        nn.init.uniform_(self.entity_embeddings.weight.data, -6/(embedding_dim**0.5), 6/(embedding_dim**0.5))
        nn.init.uniform_(self.relation_embeddings.weight.data, -6/(embedding_dim**0.5), 6/(embedding_dim**0.5))

    def forward(self, heads, relations, tails):
        head_emb = self.entity_embeddings(heads)
        rel_emb = self.relation_embeddings(relations)
        tail_emb = self.entity_embeddings(tails)

        # L2 距离
        score = torch.norm(head_emb + rel_emb - tail_emb, p=2, dim=1)
        return score

    def predict_triple(self, head_idx, rel_idx, tail_idx):
        """预测三元组的得分"""
        with torch.no_grad():
            head = torch.tensor([head_idx])
            rel = torch.tensor([rel_idx])
            tail = torch.tensor([tail_idx])
            score = self.forward(head, rel, tail)
            return -score.item()  # 返回负距离，得分越高越好

    def find_missing_tail(self, head_idx, rel_idx, top_k=5):
        """查找最可能的尾实体"""
        with torch.no_grad():
            head = torch.tensor([head_idx])
            rel = torch.tensor([rel_idx])

            head_emb = self.entity_embeddings(head)
            rel_emb = self.relation_embeddings(rel)
            all_tail_emb = self.entity_embeddings.weight

            # 计算所有可能的尾实体得分
            scores = torch.norm(head_emb + rel_emb - all_tail_emb, p=2, dim=1)

            # 返回 top_k
            top_scores, top_indices = torch.topk(-scores, top_k)
            return top_indices.tolist(), (-top_scores).tolist()

# 训练 TransE
def train_transe(triples, num_entities, num_relations, embedding_dim=100, epochs=100):
    model = TransE(num_entities, num_relations, embedding_dim)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    # 负采样函数
    def negative_sampling(triple, num_entities):
        head, rel, tail = triple
        # 随机替换头实体或尾实体
        if torch.rand(1).item() > 0.5:
            new_head = torch.randint(0, num_entities, (1,)).item()
            while new_head == head:
                new_head = torch.randint(0, num_entities, (1,)).item()
            return (new_head, rel, tail)
        else:
            new_tail = torch.randint(0, num_entities, (1,)).item()
            while new_tail == tail:
                new_tail = torch.randint(0, num_entities, (1,)).item()
            return (head, rel, new_tail)

    # 训练循环
    for epoch in range(epochs):
        total_loss = 0

        for triple in triples:
            head, rel, tail = triple

            # 负采样
            neg_head, neg_rel, neg_tail = negative_sampling(triple, num_entities)

            # 正例和负例
            pos_head = torch.tensor([head])
            pos_rel = torch.tensor([rel])
            pos_tail = torch.tensor([tail])

            neg_head_tensor = torch.tensor([neg_head])
            neg_tail_tensor = torch.tensor([neg_tail])

            # 计算损失
            pos_score = model(pos_head, pos_rel, pos_tail)
            neg_score = model(neg_head_tensor, pos_rel, neg_tail_tensor)

            # Hinge Loss
            loss = F.relu(pos_score - neg_score + 1.0).mean()

            # 反向传播
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch + 1}, Loss: {total_loss / len(triples):.4f}")

    return model

# 使用
# 假设我们有以下三元组 (head, relation, tail)
triples = [
    (0, 0, 1),  # 0(张三) -朋友-> 1(李四)
    (1, 0, 2),  # 1(李四) -朋友-> 2(王五)
    (0, 1, 2),  # 0(张三) -同事-> 2(王五)
]

num_entities = 3  # 张三, 李四, 王五
num_relations = 2  # 朋友, 同事

model = train_transe(triples, num_entities, num_relations, embedding_dim=50, epochs=50)

# 预测：张三的朋友是谁？
top_indices, top_scores = model.find_missing_tail(0, 0, top_k=3)
print(f"张三的可能朋友: {top_indices}, 得分: {top_scores}")
```

## 小结

本节介绍了知识图谱推理技术：

- **规则推理** - Horn Clause、传递性
- **路径推理** - 多跳、概率路径
- **嵌入推理** - TransE 模型

## 实践练习

### 编程题
1. 实现一个前向推理引擎，给定事实"A是B的父亲""B是C的父亲"和规则"父亲关系具有传递性"，推导出"A是C的祖父"。
2. 用 TransE 模型训练一个小型知识图谱（10个实体，3种关系），然后用训练好的模型预测缺失的尾实体。

### 思考题
1. 前向推理和后向推理分别适用于什么场景？
2. 基于嵌入的推理（如 TransE）相比基于规则的推理有什么优势和局限？

### 自测题
1. 知识图谱推理的四种主要类型是什么？
2. TransE 的核心假设（h + r ≈ t）是什么意思？
3. 蒙特卡洛路径采样在概率推理中的作用是什么？

下一步将学习 GraphRAG 技术（→ `03-graph-rag.md`）。