# 全栈开发学习工作空间

本工作空间包含 4 个完整的学习系列，共 55+ 篇笔记，覆盖从 AI 到 Java 全栈的核心技术栈。

## 快速导航

| 系列 | 目录 | 内容 | 文件数 |
|------|------|------|--------|
| AI 全栈学习 | [ai-fullstack-learning](./ai-fullstack-learning/) | Haystack RAG、LangChain Agent、知识图谱、NLP | 16 |
| Java 全栈学习 | [java-fullstack-learning](./java-fullstack-learning/) | JavaSE、Spring Boot、微服务、Redis、MQ、项目实战 | 20 |
| Spring 学习 | [SpringLearn](./SpringLearn/) | IoC/DI、AOP、Spring Boot、MVC、JPA、Security | 8 |
| SQL 学习 | [SQLLearn](./SQLLearn/) | MySQL、PostgreSQL、MongoDB、索引、事务、面试题 | 11 |

## 目录结构

```
claudeworkspace/
├── README.md                         ← 本文件
│
├── ai-fullstack-learning/            ← AI 全栈学习
│   ├── README.md                     # AI 学习路径总览
│   ├── QUICKSTART.md                 # 15 分钟快速体验
│   ├── haystack-ai/                  # Haystack RAG（5篇）
│   ├── langchain-agent/              # LangChain Agent（4篇）
│   ├── knowledge-graph/              # 知识图谱（3篇）
│   └── nlp/                          # NLP 自然语言处理（4篇）
│
├── java-fullstack-learning/          ← Java 全栈学习
│   ├── README.md                     # 部署与监控笔记
│   ├── javase/                       # Java SE（6篇）
│   ├── javaweb/                      # Java Web（1篇）
│   ├── spring/                       # Spring Framework（2篇）
│   ├── spring-boot/                  # Spring Boot（1篇）
│   ├── spring-cloud-alibaba/         # 微服务（1篇）
│   ├── redis/                        # Redis（1篇）
│   ├── mq/                           # 消息队列（1篇）
│   ├── mybatis/                      # MyBatis Plus（1篇）
│   ├── performance/                  # 性能优化（1篇）
│   ├── project/                      # 项目实战（1篇）
│   ├── system-design/                # 系统设计（1篇）
│   ├── fundamentals/                 # 网络与操作系统（1篇）
│   └── interview/                    # 面试指南（1篇）
│
├── SpringLearn/                      ← Spring 面试学习
│   ├── 第一课-Spring核心.md          # IoC、DI、Bean
│   ├── 第二课-AOP面向切面编程.md      # AOP 原理与实践
│   ├── 第三课-SpringBoot快速入门.md   # Spring Boot 基础
│   ├── 第四课-SpringBoot自动配置原理.md # 自动配置深度解析
│   ├── 第五课-SpringMVC.md           # Spring MVC 详解
│   ├── 第六课-SpringDataJPA.md       # JPA 数据访问
│   ├── 第七课-SpringSecurity.md      # 安全认证与 JWT
│   └── 第八课-面试高频考点.md         # 50+ 面试题汇总
│
└── SQLLearn/                         ← SQL 数据库学习
    ├── 01-基础查询与数据操作.md        # SELECT、WHERE、INSERT、UPDATE
    ├── 02-高级查询与连接.md           # JOIN、子查询、窗口函数
    ├── 03-聚合与分组.md              # GROUP BY、HAVING、聚合函数
    ├── 04-视图与存储过程.md           # View、Procedure、Function
    ├── 05-事务与游标.md              # ACID、隔离级别、Cursor
    ├── 06-索引与触发器.md            # Index、Trigger、性能优化
    ├── 07-MySQL特有功能.md           # 引擎、分区、JSON、MySQL 8.0
    ├── 08-PostgreSQL特有功能.md       # 数组、JSONB、UPSERT、CTE
    ├── 09-MongoDB基础.md             # NoSQL、文档操作、聚合管道
    └── 10-面试高频考点.md             # SQL 面试题汇总
```

## 建议学习路径

### 路线 A：Java 后端工程师
```
Java SE 基础 → Spring 核心 → Spring Boot → Spring MVC
    → JPA/MyBatis → Redis → MQ → Spring Cloud → 项目实战 → 系统设计
```
配合：[SpringLearn](./SpringLearn/) + [java-fullstack-learning](./java-fullstack-learning/)

### 路线 B：AI 开发工程师
```
Python NLP 基础 → Haystack RAG → LangChain Agent
    → 知识图谱 → GraphRAG → Transformer 模型 → 项目实战
```
配合：[ai-fullstack-learning](./ai-fullstack-learning/)

### 路线 C：数据库工程师/DBA
```
SQL 基础 → 高级查询 → 聚合分组 → 视图存储过程
    → 索引触发器 → MySQL 深入 → PostgreSQL 深入 → MongoDB 基础
```
配合：[SQLLearn](./SQLLearn/)

### 路线 D：全栈 AI 工程师（推荐）
```
1. SQL 基础（1-2 周）→ SQLLearn 01-03
2. Java/Spring 基础（3-4 周）→ SpringLearn 全 8 课
3. Python AI 基础（2 周）→ ai-fullstack-learning NLP
4. RAG + Agent 实战（3 周）→ Haystack + LangChain
5. 全栈项目实战（4 周）→ java-fullstack-learning + AI 项目
6. 面试冲刺（2 周）→ 各系列面试篇
```

## 每篇笔记结构

每篇笔记均包含以下板块：

| 板块 | 说明 |
|------|------|
| 概念讲解 | 核心概念对比表、原理流程图 |
| 代码示例 | 可运行的完整代码（Java/Python/SQL） |
| 面试考点 | 高频面试问题与关键答案要点 |
| 课后练习 | 编程练习题（2-4 题） |
| 自测题 | 选择题 + 答案，快速检验理解 |
| 下一课 | 明确的课程间交叉引用 |

## 学习建议

1. **循序渐进**：按照推荐顺序学习，不要跳过基础篇
2. **动手实践**：每篇笔记的课后练习必须实际编码完成
3. **笔记整理**：用自己的话重新组织知识，而不是照抄
4. **面试导向**：重点掌握各篇的"面试考点"和"自测题"
5. **项目驱动**：学完一个模块后，用项目实战巩固

## 更新记录

- 2026-05-29：完成全部 55+ 篇笔记的完善工作
  - 修复代码错误（Transformer 模型、位置编码等）
  - 为所有笔记添加实践练习和自测题
  - 添加模块间交叉引用
  - 修复错别字
  - 创建主 README 索引
