# SQL 面试速查表

## SQL 执行顺序（必背）
```
FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT
```
> 书写顺序和实际执行顺序不同！这是面试最高频考点。

## 查询语法速查

### JOIN 类型
| 类型 | 说明 | 结果 |
|------|------|------|
| INNER JOIN | 内连接 | 两边都匹配的行 |
| LEFT JOIN | 左连接 | 保留左表全部，右表不匹配为 NULL |
| RIGHT JOIN | 右连接 | 保留右表全部，左表不匹配为 NULL |
| FULL OUTER JOIN | 全连接 | 两边全部保留(MySQL 不支持，需 UNION) |
| CROSS JOIN | 交叉连接 | 笛卡尔积(A×B) |

### WHERE vs HAVING
| | WHERE | HAVING |
|------|-------|--------|
| 执行时机 | 分组前 | 分组后 |
| 聚合函数 | ❌ | ✅ |

### UNION vs UNION ALL
| | UNION | UNION ALL |
|------|-------|----------|
| 去重 | ✅ | ❌ |
| 性能 | 慢(需排序) | 快 |
| 使用场景 | 需要去重 | 明确不重复 |

## 窗口函数速查

```sql
function() OVER (
    PARTITION BY col    -- 分组
    ORDER BY col        -- 排序
    ROWS BETWEEN ...    -- 窗口范围
)
```

| 函数 | 说明 | 示例 |
|------|------|------|
| `ROW_NUMBER()` | 顺序排名：1,2,3,4 | 每组取前N |
| `RANK()` | 跳跃排名：1,2,2,4 | 有并列排名 |
| `DENSE_RANK()` | 密集排名：1,2,2,3 | 不跳号排名 |
| `LAG(col, n)` | 前第 n 行 | 环比计算 |
| `LEAD(col, n)` | 后第 n 行 | 趋势分析 |
| `SUM() OVER` | 累计求和 | 累计销售额 |

## 索引速查

### 索引类型
| 类型 | 语法 | 特点 |
|------|------|------|
| 普通索引 | `CREATE INDEX idx ON t(col)` | 基本查询加速 |
| 唯一索引 | `CREATE UNIQUE INDEX` | 值唯一 |
| 复合索引 | `CREATE INDEX idx ON t(a,b)` | 最左前缀原则 |
| 覆盖索引 | 查询列全部在索引中 | 无需回表，最快 |

### 索引失效 6 场景
```sql
-- ❌ 1. 对列使用函数
WHERE YEAR(create_time) = 2024
-- ✅ WHERE create_time >= '2024-01-01'

-- ❌ 2. 隐式类型转换
WHERE phone = 13800138000  -- phone 是 VARCHAR
-- ✅ WHERE phone = '13800138000'

-- ❌ 3. LIKE 以 % 开头
WHERE name LIKE '%张'
-- ✅ 使用全文索引

-- ❌ 4. OR 条件
-- ✅ 改用 UNION

-- ❌ 5. NOT IN / != / <>
-- ✅ 改用 NOT EXISTS

-- ❌ 6. 复合索引不满足最左前缀
```

## 事务速查

### ACID
| 特性 | 说明 |
|------|------|
| 原子性 (Atomicity) | 要么全成功，要么全失败 |
| 一致性 (Consistency) | 事务前后数据一致 |
| 隔离性 (Isolation) | 并发事务互不干扰 |
| 持久性 (Durability) | 提交后永久保存 |

### 隔离级别
| 级别 | 脏读 | 不可重复读 | 幻读 |
|------|------|-----------|------|
| READ UNCOMMITTED | ✅ | ✅ | ✅ |
| READ COMMITTED | ❌ | ✅ | ✅ |
| REPEATABLE READ | ❌ | ❌ | ✅ (MySQL 默认) |
| SERIALIZABLE | ❌ | ❌ | ❌ |

### 事务失效场景
1. 引擎不支持事务 (MyISAM)
2. DDL 语句不能回滚 (CREATE/DROP/ALTER)
3. TRUNCATE 不能回滚 (MySQL)
4. 未开启事务 (自动提交)
5. 异常被捕获但未 ROLLBACK

## MySQL vs PostgreSQL

| 特性 | MySQL | PostgreSQL |
|------|-------|------------|
| 默认引擎 | InnoDB | (统称 PostgreSQL) |
| 自增列 | AUTO_INCREMENT | SERIAL |
| 字符串拼接 | CONCAT() | \|\| |
| JSON 类型 | JSON | JSON / JSONB |
| UPSERT | REPLACE / ON DUPLICATE KEY | INSERT ON CONFLICT |
| 全文搜索 | MATCH...AGAINST | to_tsvector / to_tsquery |
| 窗口函数 | 8.0+ | 9.0+ |
| 数组类型 | ❌ | ✅ |
| 范围类型 | ❌ | ✅ |
| RETURNING | ❌ | ✅ |

## MongoDB 速查

| SQL 概念 | MongoDB 概念 |
|----------|-------------|
| Database | Database |
| Table | Collection |
| Row | Document |
| Column | Field |
| WHERE | `$match` |
| JOIN | `$lookup` |
| GROUP BY | `$group` |
| ORDER BY | `$sort` |
| INSERT | `insertOne()` / `insertMany()` |

## 常用函数速查

### 字符串
| MySQL | PostgreSQL | 功能 |
|-------|------------|------|
| `CONCAT(a,b)` | `a \|\| b` | 拼接 |
| `SUBSTRING(s,1,5)` | `SUBSTRING(s,1,5)` | 截取 |
| `LENGTH(s)` | `LENGTH(s)` | 长度 |
| `REPLACE(s,a,b)` | `REPLACE(s,a,b)` | 替换 |
| `UPPER(s)` / `LOWER(s)` | 同 | 大小写 |
| `GROUP_CONCAT(col)` | `STRING_AGG(col,',')` | 字符串聚合 |

### 日期
| MySQL | PostgreSQL | 功能 |
|-------|------------|------|
| `NOW()` | `NOW()` | 当前日期时间 |
| `CURDATE()` | `CURRENT_DATE` | 当前日期 |
| `DATE_ADD(d, INTERVAL 7 DAY)` | `d + INTERVAL '7 days'` | 日期加 |
| `DATEDIFF(d1,d2)` | `AGE(d1,d2)` | 日期差 |
| `DATE_FORMAT(d,f)` | `TO_CHAR(d,f)` | 格式化 |
| `YEAR(d)` / `MONTH(d)` | `EXTRACT(YEAR FROM d)` | 提取 |

## 存储过程 vs 视图 vs 触发器

| | 视图(VIEW) | 存储过程(SP) | 触发器(TRIGGER) |
|------|-----------|-------------|----------------|
| 本质 | 虚拟表 | 预编译代码块 | 事件自动执行 |
| 存数据 | ❌ | ❌ | ❌ |
| 更新 | 简单视图可 | 通过逻辑 | 事件驱动 |
| 参数 | ❌ | IN/OUT/INOUT | NEW/OLD |
| 用途 | 简化查询、安全 | 复杂业务、复用 | 审计、验证 |

## 面试高频 15 问

1. **SQL 执行顺序？** FROM→WHERE→GROUP BY→HAVING→SELECT→ORDER BY→LIMIT
2. **WHERE vs HAVING？** WHERE 分组前、不能用聚合；HAVING 分组后、可用聚合
3. **LEFT JOIN 原理？** 保留左表全部记录，右表不匹配为 NULL
4. **UNION vs UNION ALL？** UNION 去重(慢)，UNION ALL 不去重(快)
5. **索引失效场景？** 函数、隐式转换、LIKE %开头、OR、NOT IN、最左不匹配
6. **最左前缀原则？** 复合索引从最左列开始匹配，跳过左列无法使用索引
7. **ACID 是什么？** 原子性、一致性、隔离性、持久性
8. **隔离级别有哪些？** READ UNCOMMITTED/READ COMMITTED/REPEATABLE READ/SERIALIZABLE
9. **MySQL 默认隔离级别？** REPEATABLE READ
10. **InnoDB vs MyISAM？** InnoDB 支持事务/外键/行锁；MyISAM 不支持事务/表锁/全文索引
11. **慢查询如何优化？** EXPLAIN 分析 → 加索引 → 优化 SQL → 读写分离 → 分库分表
12. **聚集索引和非聚集索引？** 聚集索引数据与索引存一起(主键)，非聚集索引存指针
13. **覆盖索引？** 查询所需列全部在索引中，不需要回表查询
14. **乐观锁 vs 悲观锁？** 乐观锁(版本号/CAS)，悲观锁(SELECT FOR UPDATE)
15. **分库分表策略？** 垂直拆分(按业务)，水平拆分(按 ID 哈希/范围)
