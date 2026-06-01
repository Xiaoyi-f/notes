# SQL 学习笔记 - Neo4j 基础

## 一、Neo4j 概述

### 1.1 什么是 Neo4j

Neo4j 是一个基于图模型的 NoSQL 数据库，使用图结构（节点和关系）来存储和查询数据。

**核心特性：**
- 属性图模型（节点、关系、属性、标签）
- 原生图存储与处理
- 声明式查询语言 Cypher
- ACID 事务支持
- 高可用集群
- 可视化 Web 界面（Neo4j Browser）

**适用场景：**
- 社交网络关系分析
- 推荐引擎
- 知识图谱
- 欺诈检测
- 权限与访问控制
- 主数据管理

---

### 1.2 Neo4j vs SQL 对比

| 特性 | SQL（关系型） | Neo4j（图型） |
|------|--------------|----------------|
| **数据模型** | 表、行、列 | 节点、关系、属性 |
| **Schema** | 固定结构 | 灵活，无需预定义 |
| **事务** | 强一致 | 完全 ACID |
| **查询语言** | SQL | Cypher |
| **扩展性** | 垂直扩展为主 | 读写分离、集群 |
| **连接方式** | JOIN | 关系遍历（指针跳转） |
| **索引** | B-tree | B-tree、全文索引 |
| **关联查询** | JOIN（计算型） | 遍历（导航型） |

---

### 1.3 核心概念对应

| SQL 概念 | Neo4j 概念 | 说明 |
|----------|-------------|------|
| 数据库 | Database | 数据库 |
| 表 | Label | 标签（节点分类） |
| 行 | Node | 节点 |
| 列 | Property | 属性（键值对） |
| 主键 | 唯一约束属性 | 由约束保证唯一性 |
| 外键/JOIN | Relationship | 关系（有向、有类型） |
| 索引 | Index | 索引 |

---

### 1.4 图模型基础

```
(person:User {name: "张三"})
    │
    │ [:FOLLOWS {since: 2024}]
    ▼
(person:User {name: "李四"})
```

**图模型三要素：**
- **节点（Node）**：表示实体，用 `(variable:Label)` 表示
- **关系（Relationship）**：表示实体间的联系，用 `[variable:TYPE]` 表示，必须有方向
- **属性（Property）**：节点和关系都可以拥有键值对属性

---

## 二、Neo4j 连接与基础操作

### 2.1 连接 Neo4j

```bash
# Neo4j 启动（本地）
neo4j start

# Neo4j 状态查看
neo4j status

# Neo4j 停止
neo4j stop

# Neo4j 控制台（交互式 Cypher Shell）
cypher-shell -u neo4j -p password

# 连接远程 Neo4j
cypher-shell -a bolt://localhost:7687 -u neo4j -p password

# Neo4j Browser Web 界面
# http://localhost:7474
```

### 2.2 基础 Cypher 操作

```cypher
// 查看当前数据库
:system SHOW DATABASES;

// 切换数据库
:use neo4j;

// 查看所有标签
CALL db.labels();

// 查看所有关系类型
CALL db.relationshipTypes();

// 查看所有属性键
CALL db.propertyKeys();

// 查看数据库信息
CALL db.schema();

// 清空数据库
MATCH (n) DETACH DELETE n;

// 查看节点数量
MATCH (n) RETURN count(n) AS totalNodes;
```

---

## 三、Cypher CRUD 操作

### 3.1 创建节点（Create）

```cypher
// 创建无标签节点
CREATE (n {name: "测试"});

// 创建带标签的节点
CREATE (u:User {name: "张三", age: 25, email: "zhangsan@example.com"});

// 创建带多个标签的节点
CREATE (u:User:Employee {name: "李四", age: 30});

// 创建多个节点
CREATE (u1:User {name: "王五", age: 28}),
       (u2:User {name: "赵六", age: 22});

// 使用参数创建（推荐）
// :params {user: {name: "张三", age: 25}}
CREATE (u:User $user);
```

---

### 3.2 创建关系（Create Relationship）

```cypher
// 先创建节点，再创建关系
CREATE (a:User {name: "张三", age: 25}),
       (b:User {name: "李四", age: 30});

// 创建关系（需先有节点）
MATCH (a:User {name: "张三"})
MATCH (b:User {name: "李四"})
CREATE (a)-[r:FOLLOWS {since: 2024}]->(b)
RETURN r;

// 一次性创建节点和关系
CREATE (a:User {name: "王五"})-[:FRIENDS {since: 2023}]->(b:User {name: "赵六"});

// 创建双向关系
MATCH (a:User {name: "张三"})
MATCH (b:User {name: "李四"})
CREATE (a)-[:KNOWS]->(b),
       (b)-[:KNOWS]->(a);

// 复杂关系示例
CREATE (a:User {name: "张三"})
CREATE (b:User {name: "李四"})
CREATE (p:Post {title: "图数据库入门", content: "内容..."})
CREATE (a)-[:WRITE]->(p)
CREATE (b)-[:LIKE {createdAt: datetime()}]->(p)
CREATE (a)-[:MENTION]->(b);
```

---

### 3.3 查询节点（Read）

```cypher
// 查询所有 User 标签的节点
MATCH (u:User)
RETURN u;

// 查询指定属性
MATCH (u:User)
RETURN u.name, u.age;

// 单条件查询
MATCH (u:User {name: "张三"})
RETURN u;

// 多条件查询（AND）
MATCH (u:User {name: "张三", age: 25})
RETURN u;

// WHERE 子句（复杂条件）
MATCH (u:User)
WHERE u.age > 25
RETURN u.name, u.age;

// 多条件组合
MATCH (u:User)
WHERE u.age >= 25 AND u.age <= 30
RETURN u.name, u.age;

// OR 条件
MATCH (u:User)
WHERE u.age < 25 OR u.age > 30
RETURN u;

// 属性存在判断
MATCH (u:User)
WHERE u.email IS NOT NULL
RETURN u;

// 字符串匹配
MATCH (u:User)
WHERE u.name STARTS WITH "张"
RETURN u;

MATCH (u:User)
WHERE u.name CONTAINS "三"
RETURN u;

MATCH (u:User)
WHERE u.name ENDS WITH "三"
RETURN u;

// 正则匹配
MATCH (u:User)
WHERE u.name =~ "张.*"
RETURN u;

// IN 操作符
MATCH (u:User)
WHERE u.age IN [25, 30]
RETURN u;
```

---

### 3.4 查询关系（Read Relationships）

```cypher
// 查询某人的朋友
MATCH (u:User {name: "张三"})-[:FRIENDS]->(friend)
RETURN friend;

// 查询某人写过的文章
MATCH (u:User {name: "张三"})-[:WRITE]->(post:Post)
RETURN post.title, post.content;

// 查询关系属性
MATCH (u:User {name: "张三"})-[r:FOLLOWS]->(b)
RETURN r.since;

// 变长路径查询
MATCH (u:User {name: "张三"})-[:FRIENDS*2]->(fof)
RETURN DISTINCT fof;
// 注：*2 表示两层关系，*1..3 表示1到3层

// 最短路径查询
MATCH (a:User {name: "张三"}),
      (b:User {name: "赵六"}),
      p = shortestPath((a)-[*..6]->(b))
RETURN p;

// 查询所有关系类型
MATCH (u:User {name: "张三"})-[r]->()
RETURN type(r), r;

// 无关系查询（孤立节点）
MATCH (n)
WHERE NOT (n)--()
RETURN n;
```

---

### 3.5 更新节点和关系（Update）

```cypher
// 更新节点属性
MATCH (u:User {name: "张三"})
SET u.age = 26
RETURN u;

// 更新多个属性
MATCH (u:User {name: "张三"})
SET u.age = 26, u.email = "new@example.com";

// 增加属性（节点原来没有）
MATCH (u:User {name: "张三"})
SET u.phone = "13800138000";

// 数值增减
MATCH (u:User {name: "张三"})
SET u.age = u.age + 1;

// 替换所有属性
MATCH (u:User {name: "张三"})
SET u = {name: "张三", age: 30, city: "北京"};

// 移除属性
MATCH (u:User {name: "张三"})
REMOVE u.phone;

// 等价写法
MATCH (u:User {name: "张三"})
SET u.phone = null;

// 添加标签
MATCH (u:User {name: "张三"})
SET u:VIP;

// 移除标签
MATCH (u:User {name: "张三"})
REMOVE u:VIP;

// 更新关系属性
MATCH (u:User {name: "张三"})-[r:FOLLOWS]->(b)
SET r.since = 2023;
```

---

### 3.6 删除（Delete）

```cypher
// 删除节点（需先删除关系）
MATCH (u:User {name: "张三"})
DETACH DELETE u;
// DETACH DELETE 会自动删除该节点的所有关系

// 只删除关系
MATCH (u:User {name: "张三"})-[r:FOLLOWS]->()
DELETE r;

// 删除节点和所有关系
MATCH (u:User {name: "张三"})
DETACH DELETE u;

// 删除指定标签的所有节点
MATCH (u:User)
DETACH DELETE u;

// 删除满足条件的节点
MATCH (u:User)
WHERE u.age < 18
DETACH DELETE u;

// 删除属性
MATCH (u:User {name: "张三"})
REMOVE u.phone;

// 清空数据库
MATCH (n)
DETACH DELETE n;
```

---

## 四、高级查询

### 4.1 Aggregation 聚合

```cypher
// 计数
MATCH (u:User)
RETURN count(u) AS totalUsers;

// 分组计数
MATCH (u:User)
RETURN u.age AS age, count(u) AS count
ORDER BY count DESC;

// 常用聚合函数
MATCH (u:User)
RETURN count(u) AS total,
       avg(u.age) AS avgAge,
       sum(u.age) AS totalAge,
       min(u.age) AS minAge,
       max(u.age) AS maxAge;

// 按条件分组
MATCH (u:User)
RETURN CASE
         WHEN u.age < 25 THEN "young"
         WHEN u.age < 40 THEN "middle"
         ELSE "old"
       END AS category,
       count(u) AS count;
```

---

### 4.2 排序与分页

```cypher
// 排序
MATCH (u:User)
RETURN u.name, u.age
ORDER BY u.age DESC, u.name ASC;

// 分页
MATCH (u:User)
RETURN u.name, u.age
ORDER BY u.age DESC
SKIP 10 LIMIT 10;  // 第11-20条
```

---

### 4.3 路径查询

```cypher
// 查询朋友的朋友
MATCH (u:User {name: "张三"})-[:FRIENDS]->()-[:FRIENDS]->(fof)
RETURN DISTINCT fof;

// 变长路径
MATCH (u:User {name: "张三"})-[:FRIENDS*2..4]->(far)
RETURN DISTINCT far;

// 命名路径
MATCH p = (u:User {name: "张三"})-[:FRIENDS*1..3]->(friend)
RETURN p, length(p) AS pathLength;

// 最短路径
MATCH (a:User {name: "张三"}),
      (b:User {name: "赵六"}),
      p = shortestPath((a)-[*..6]->(b))
RETURN p;

// 所有最短路径
MATCH (a:User {name: "张三"}),
      (b:User {name: "赵六"}),
      p = allShortestPaths((a)-[*..6]->(b))
RETURN p;
```

---

### 4.4 模式匹配

```cypher
// 查询关注者超过100的用户
MATCH (u:User)
WHERE size((u)<-[:FOLLOWS]-()) > 100
RETURN u.name, size((u)<-[:FOLLOWS]-()) AS followers;

// 查询发布过文章的用户
MATCH (u:User)
WHERE (u)-[:WRITE]->(:Post)
RETURN u;

// 查询与张三有共同好友的用户
MATCH (u:User {name: "张三"})-[:FRIENDS]->(common)-[:FRIENDS]->(other)
WHERE other <> u
RETURN DISTINCT other;

// NOT 模式
MATCH (u:User)
WHERE NOT (u)-[:WRITE]->(:Post)
RETURN u.name AS usersWithoutPosts;

// OPTIONAL MATCH（类似 LEFT JOIN）
MATCH (u:User)
OPTIONAL MATCH (u)-[:WRITE]->(p:Post)
RETURN u.name, p.title;
```

---

### 4.5 WITH 子句与管道

```cypher
// WITH 用于管道传递（类似 SQL CTE）
MATCH (u:User)
WITH u, u.age * 2 AS doubleAge
WHERE doubleAge > 50
RETURN u.name, doubleAge;

// 聚合后过滤
MATCH (u:User)-[:WRITE]->(p:Post)
WITH u, count(p) AS postCount
WHERE postCount >= 2
RETURN u.name, postCount;

// 去重
MATCH (u:User)-[:FRIENDS]->(friend)
WITH DISTINCT friend
RETURN friend.name;

// 排序后取前N
MATCH (u:User)
WITH u
ORDER BY u.age DESC
LIMIT 5
RETURN u.name, u.age;

// 收集（类似 GROUP_CONCAT）
MATCH (u:User)-[:WRITE]->(p:Post)
RETURN u.name, collect(p.title) AS postTitles;
```

---

### 4.6 复杂查询示例

```cypher
// 建立示例数据
CREATE (a:User {name: "张三", age: 25})
CREATE (b:User {name: "李四", age: 30})
CREATE (c:User {name: "王五", age: 28})
CREATE (d:User {name: "赵六", age: 35})
CREATE (a)-[:FOLLOWS {since: 2023}]->(b)
CREATE (b)-[:FOLLOWS {since: 2022}]->(c)
CREATE (c)-[:FOLLOWS {since: 2024}]->(d)
CREATE (a)-[:FRIENDS {since: 2020}]->(c)
CREATE (b)-[:FRIENDS {since: 2021}]->(d);

// 查询关注链
MATCH path = (u:User {name: "张三"})-[:FOLLOWS*1..3]->(target)
RETURN [n IN nodes(path) | n.name] AS path,
       length(path) AS depth;

// 推荐好友（共同关注）
MATCH (u:User {name: "张三"})-[:FOLLOWS]->(following)-[:FOLLOWS]->(recommend)
WHERE NOT (u)-[:FOLLOWS]->(recommend) AND recommend <> u
RETURN recommend.name, count(*) AS commonFollowers
ORDER BY commonFollowers DESC;

// 社交圈分析
MATCH (u:User {name: "张三"})-[:FRIENDS|FOLLOWS*1..2]-(connected)
RETURN connected.name, 
       labels(connected) AS labels,
       count(*) AS connectionStrength
ORDER BY connectionStrength DESC;
```

---

## 五、索引与约束

### 5.1 索引

```cypher
// 创建单属性索引
CREATE INDEX user_name_index FOR (u:User) ON (u.name);

// 创建复合索引
CREATE INDEX user_age_name_index FOR (u:User) ON (u.age, u.name);

// 创建全文索引（需要 apoc）
// CALL db.index.fulltext.createNodeIndex("postSearch", ["Post"], ["title", "content"]);

// 查看索引
SHOW INDEXES;

// 删除索引
DROP INDEX user_name_index;
```

---

### 5.2 约束

```cypher
// 唯一约束（类似主键）
CREATE CONSTRAINT unique_user_email FOR (u:User) REQUIRE u.email IS UNIQUE;

// 节点属性存在约束
CREATE CONSTRAINT require_user_name FOR (u:User) REQUIRE u.name IS NOT NULL;

// 关系属性存在约束
CREATE CONSTRAINT require_follows_since FOR ()-[r:FOLLOWS]-() REQUIRE r.since IS NOT NULL;

// 复合唯一约束
CREATE CONSTRAINT unique_user_name_age FOR (u:User) REQUIRE (u.name, u.age) IS UNIQUE;

// 查看约束
SHOW CONSTRAINTS;

// 删除约束
DROP CONSTRAINT unique_user_email;
```

---

### 5.3 执行计划

```cypher
// 查看执行计划（不执行）
EXPLAIN MATCH (u:User {name: "张三"}) RETURN u;

// 查看执行计划（执行）
PROFILE MATCH (u:User {name: "张三"}) RETURN u;

// 关键指标
// NodeByLabelScan: 按标签扫描
// NodeIndexSeek: 使用索引查找
// Filter: 过滤节点
// Expand(All): 扩展关系
// CacheProperties: 加载属性
```

---

## 六、事务

### 6.1 Cypher 事务

```cypher
// Cypher 不支持显式 BEGIN/COMMIT
// 每个 Cypher 语句默认在独立事务中执行

// 通过驱动 API 管理事务（Java/Python/JS 示例）
```

### 6.2 事务示例（Java 驱动）

```java
try (Transaction tx = session.beginTransaction()) {
    tx.run("CREATE (u:User {name: $name, age: $age})",
        parameters("name", "张三", "age", 25));
    tx.run("MATCH (a:User {name: $from}), (b:User {name: $to}) " +
           "CREATE (a)-[:FOLLOWS]->(b)",
        parameters("from", "张三", "to", "李四"));
    tx.commit();
}
```

### 6.3 Python 驱动事务

```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
with driver.session() as session:
    with session.begin_transaction() as tx:
        tx.run("CREATE (u:User {name: $name})", name="张三")
        tx.run("CREATE (u:User {name: $name})", name="李四")
        tx.commit()
```

### 6.4 注意事项

- Neo4j 是完全 ACID 的
- 单个 Cypher 语句自动在事务中执行
- 事务隔离级别为 READ COMMITTED
- 写操作会锁定受影响节点和关系
- 避免大事务（默认超时 60 秒）

---

## 七、备份与恢复

### 7.1 在线备份

```bash
# 创建备份
neo4j-admin database dump neo4j --to-path=/backup/

# 从备份恢复
neo4j-admin database load neo4j --from-path=/backup/neo4j.dump

# 创建压缩备份
neo4j-admin database dump neo4j --to-path=/backup/ --compress

# 备份指定数据库
neo4j-admin database dump mydb --to-path=/backup/
```

### 7.2 离线备份

```bash
# 停止 Neo4j
neo4j stop

# 复制数据目录
cp -r /var/lib/neo4j/data/databases/neo4j /backup/neo4j_backup

# 启动 Neo4j
neo4j start
```

---

## 八、常用命令

```cypher
// 查看数据库信息
CALL db.info();

// 查看数据库模式
CALL db.schema();

// 查看数据库统计信息
CALL db.stats();

// 查看数据库列表
SHOW DATABASES;

// 创建数据库
CREATE DATABASE mydb;

// 删除数据库
DROP DATABASE mydb;

// 属性索引建议
CALL db.index.fulltext.listAvailableAnalyzers();

// 等待索引上线
CALL db.awaitIndexes(300);

// 重建索引
CALL db.index.fulltext.createNodeIndex("postSearch", ["Post"], ["title", "content"]);

// 查询运行状态
CALL dbms.listActiveLocks();

// 查询等待事务
CALL dbms.listTransactions();
```

---

## 九、本节面试考点

| 考点 | 答案要点 |
|------|----------|
| Neo4j 特点 | 图数据库、节点关系属性、ACID、Cypher |
| 核心概念 | Node、Relationship、Property、Label |
| Cypher vs SQL | MATCH 替代 SELECT、() 替代表、[] 表示关系 |
| 创建节点 | CREATE (var:Label {props}) |
| 创建关系 | MATCH a, b CREATE (a)-[r:TYPE]->(b) |
| 查询语法 | MATCH、WHERE、RETURN、ORDER BY、SKIP、LIMIT |
| 关系查询 | [:TYPE]、[:TYPE*min..max]、shortestPath |
| 聚合 | count、sum、avg、min、max、collect |
| 索引 | CREATE INDEX FOR...ON (...) |
| 约束 | CREATE CONSTRAINT...REQUIRE...IS UNIQUE |
| 删除节点 | DETACH DELETE（先删关系再删节点） |
| SET/REMOVE | SET 更新属性，REMOVE 删除属性/标签 |

---

## 课后练习

1. 创建学生节点（Student），包含姓名、年龄、专业属性
2. 创建课程节点（Course），包含课程名、学分属性
3. 创建选课关系 [:ENROLL {score: 95}] 连接学生和课程
4. 查询选修了"图数据库"课程的学生姓名和成绩
5. 查询平均成绩大于80分的专业和学生人数
6. 为学生姓名创建索引，为学号创建唯一约束

---

## 📝 自测题

1. Neo4j 中存储数据的基本模型是？\
   A. 文档  B. 键值对  C. 图（节点和关系）  D. 宽表
2. Cypher 中创建关系使用什么语法？\
   A. `CREATE RELATION`  B. `MATCH...CREATE (a)-[r:TYPE]->(b)`  C. `LINK a TO b`  D. `ADD EDGE`
3. 在 Neo4j 中删除节点及其所有关系的正确命令是？\
   A. DELETE n  B. REMOVE n  C. DETACH DELETE n  D. DROP n
4. 以下哪个不是 Neo4j 的核心概念？\
   A. Node  B. Relationship  C. Collection  D. Property

**答案：1-C, 2-B, 3-C, 4-C**

---

下一课：面试高频考点汇总（→ `10-面试高频考点.md`）
