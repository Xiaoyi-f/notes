# SQL 学习笔记 - PostgreSQL 特有功能

## 一、PostgreSQL 数据类型

### 1.1 数组类型

```sql
-- 创建表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50),
    tags INT[],              -- 整数数组
    emails VARCHAR(100)[],   -- 字符串数组
    scores NUMERIC[]         -- 数值数组
);

-- 插入数组
INSERT INTO users (name, tags, emails, scores) VALUES 
('张三', ARRAY[1, 2, 3], ARRAY['a@example.com', 'b@example.com'], ARRAY[90, 85, 95]),
('李四', '{4, 5, 6}', '{c@example.com, d@example.com}', '{80, 75, 85}');

-- 查询数组
SELECT name, tags FROM users;
SELECT name, tags[1] FROM users;  -- 数组索引从1开始

-- 更新数组
UPDATE users SET tags[2] = 10 WHERE id = 1;
UPDATE users SET tags = ARRAY[1, 10, 3] WHERE id = 1;

-- 追加元素
UPDATE users SET tags = array_append(tags, 4) WHERE id = 1;
UPDATE users SET tags = tags || 5 WHERE id = 1;

-- 数组函数
SELECT array_length(tags, 1) FROM users;           -- 数组长度
SELECT array_lower(tags, 1), array_upper(tags, 1) FROM users;  -- 数组范围
SELECT array_cat(ARRAY[1,2], ARRAY[3,4]);          -- 连接数组
SELECT array_position(ARRAY[1,2,3], 2);           -- 查找位置
SELECT array_remove(ARRAY[1,2,3,2], 2);           -- 删除元素
SELECT array_replace(ARRAY[1,2,3], 2, 20);        -- 替换元素

-- ANY 和 ALL
SELECT * FROM users WHERE 2 = ANY(tags);          -- tags 包含2
SELECT * FROM users WHERE 10 < ALL(scores);       -- 所有分数大于10
SELECT * FROM users WHERE 90 = ANY(scores);       -- 有分数90

-- 数组展开
SELECT name, unnest(tags) AS tag FROM users;
SELECT name, unnest(scores) AS score FROM users;
```

---

### 1.2 JSON/JSONB 类型

```sql
-- 创建表
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    attributes JSON,        -- JSON 类型（存储原文本）
    metadata JSONB          -- JSONB 类型（二进制，支持索引）
);

-- 插入 JSON 数据
INSERT INTO products (name, attributes, metadata) VALUES 
('手机', 
 '{"brand": "Apple", "model": "iPhone 15", "price": 7999}'::JSON,
 '{"brand": "Apple", "model": "iPhone 15", "price": 7999, "in_stock": true}'::JSONB);

-- JSON vs JSONB
-- JSON: 存储原文本，插入快，查询慢
-- JSONB: 二进制存储，插入慢，查询快，支持索引

-- 查询 JSON
SELECT 
    name,
    attributes->>'brand' AS brand,
    metadata->>'price' AS price
FROM products;

-- JSONB 操作符
-- -> 返回 JSON 对象
-- ->> 返回文本
-- #> 按路径获取 JSON
-- #>> 按路径获取文本
-- @> 包含检查
-- <@ 被包含检查
-- ? 键存在检查
-- ?| 任意键存在
-- ?& 所有键存在

-- 示例
SELECT * FROM products WHERE metadata @> '{"brand": "Apple"}';
SELECT * FROM products WHERE metadata ? 'brand';
SELECT * FROM products WHERE metadata ?& ARRAY['brand', 'model'];

-- JSONB 函数
-- jsonb_pretty: 格式化输出
SELECT jsonb_pretty(metadata) FROM products;

-- jsonb_set: 设置值
UPDATE products 
SET metadata = jsonb_set(metadata, '{price}', '6999'::jsonb)
WHERE id = 1;

-- jsonb_insert: 插入值
UPDATE products 
SET metadata = jsonb_insert(metadata, '{color}', '"黑色"')
WHERE id = 1;

-- jsonb_delete: 删除值
UPDATE products 
SET metadata = jsonb_delete(metadata, '{color}')
WHERE id = 1;

-- jsonb_array_length: 数组长度
SELECT jsonb_array_length(metadata->'specs') FROM products;

-- 聚合函数
-- jsonb_agg: 聚合成数组
SELECT jsonb_agg(name) FROM products;

-- jsonb_object_agg: 聚合成对象
SELECT jsonb_object_agg(id, name) FROM products;
```

---

### 1.3 JSONB 索引

```sql
-- GIN 索引（推荐）
CREATE INDEX idx_metadata_gin ON products USING GIN (metadata);

-- GIN 索引支持的操作符
-- @> 包含检查
-- ? 键存在
-- ?| 任意键
-- ?& 所有键

-- 特定路径的 GIN 索引
CREATE INDEX idx_metadata_brand ON products USING GIN ((metadata->>'brand') gin_trgm_ops);

-- B-tree 索引（特定字段）
CREATE INDEX idx_metadata_price ON products ((metadata->>'price'));

-- 查询示例（使用索引）
EXPLAIN ANALYZE SELECT * FROM products WHERE metadata @> '{"brand": "Apple"}';
```

---

### 1.4 几何类型

```sql
-- 创建表
CREATE TABLE places (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    location POINT,        -- 点
    area POLYGON,          -- 多边形
    path LINE              -- 线
);

-- 插入几何数据
INSERT INTO places (name, location, area) VALUES 
('中心公园', POINT(0, 0), 
 POLYGON((0,0), (100,0), (100,100), (0,100), (0,0)));

-- 几何函数
-- 距离计算
SELECT name, location, 
       location <-> POINT(50, 50) AS distance
FROM places;

-- 面积
SELECT name, ST_Area(area) FROM places;

-- 点是否在多边形内
SELECT name, 
       ST_Contains(area, POINT(10, 10)) AS inside
FROM places;
```

---

### 1.5 范围类型

```sql
-- 创建表
CREATE TABLE schedules (
    id SERIAL PRIMARY KEY,
    task VARCHAR(100),
    time_range TSRANGE,        -- 时间范围
    date_range DATERANGE,      -- 日期范围
    num_range INT4RANGE,       -- 整数范围
    decimal_range NUMRANGE     -- 小数范围
);

-- 插入范围数据
INSERT INTO schedules (task, time_range, num_range) VALUES 
('会议', 
 '[2024-01-01 09:00:00, 2024-01-01 10:00:00]',
 '[1, 10]');

-- 范围操作符
-- @> 包含
-- <@ 被包含
-- && 重叠
-- << 在...之前
-- >> 在...之后
-- -|- 相邻

-- 查询示例
SELECT * FROM schedules WHERE time_range @> '2024-01-01 09:30:00'::timestamp;
SELECT * FROM schedules WHERE time_range && '[2024-01-01, 2024-01-02]'::tsrange;
SELECT * FROM schedules WHERE num_range @> 5;

-- 范围函数
SELECT lower(time_range), upper(time_range) FROM schedules;
SELECT isempty(time_range) FROM schedules;
SELECT length(num_range) FROM schedules;
```

---

## 二、PostgreSQL 函数

### 2.1 字符串函数

```sql
-- 字符串拼接（推荐使用 ||）
SELECT 'Hello' || ' ' || 'World';  -- Hello World

-- 字符串重复
SELECT REPEAT('abc', 3);  -- abcabcabc

-- 字符串替换
SELECT REPLACE('hello world', 'world', 'PostgreSQL');  -- hello PostgreSQL

-- 字符串截取
SELECT SUBSTRING('hello world', 1, 5);  -- hello
SELECT SUBSTRING('hello world' FROM 1 FOR 5);  -- hello

-- 字符串长度
SELECT LENGTH('hello');  -- 5

-- 字符串位置
SELECT POSITION('world' IN 'hello world');  -- 7

-- 字符串反转
SELECT REVERSE('hello');  -- olleh

-- 大小写转换
SELECT UPPER('hello');  -- HELLO
SELECT LOWER('HELLO');  -- hello

-- 去除空格
SELECT TRIM('  hello  ');     -- hello
SELECT LTRIM('  hello  ');    -- hello  
SELECT RTRIM('  hello  ');    --   hello

-- 分割字符串
SELECT string_to_array('a,b,c,d', ',');  -- {a,b,c,d}

-- 合并数组
SELECT array_to_string(ARRAY[1,2,3], ',');  -- 1,2,3
```

---

### 2.2 日期函数

```sql
-- 当前日期时间
SELECT CURRENT_DATE;      -- 2024-01-15
SELECT CURRENT_TIME;      -- 14:30:00
SELECT CURRENT_TIMESTAMP; -- 2024-01-15 14:30:00
SELECT NOW();             -- 2024-01-15 14:30:00

-- 日期计算
SELECT NOW() + INTERVAL '7 days';           -- 加7天
SELECT NOW() - INTERVAL '1 month';          -- 减1个月
SELECT NOW() + INTERVAL '1-2' YEAR TO MONTH; -- 加1年2个月
SELECT NOW() + INTERVAL '1 year 2 months 3 days 4 hours 5 minutes 6 seconds';

-- 日期差
SELECT AGE(CURRENT_DATE, '2020-01-01');     -- 4 years...
SELECT DATE_PART('year', AGE('2020-01-01')); -- 4

-- 日期提取
SELECT EXTRACT(YEAR FROM NOW());    -- 2024
SELECT EXTRACT(MONTH FROM NOW());   -- 1
SELECT EXTRACT(DAY FROM NOW());     -- 15
SELECT EXTRACT(HOUR FROM NOW());    -- 14

-- 日期转换
SELECT TO_CHAR(NOW(), 'YYYY-MM-DD HH24:MI:SS');  -- 2024-01-15 14:30:00
SELECT TO_DATE('2024-01-15', 'YYYY-MM-DD');
SELECT TO_TIMESTAMP('2024-01-15 14:30:00', 'YYYY-MM-DD HH24:MI:SS');

-- 时间戳转换
SELECT EXTRACT(EPOCH FROM NOW());  -- Unix 时间戳
SELECT TO_TIMESTAMP(1705318200);  -- 从 Unix 时间戳转换
```

---

### 2.3 数学函数

```sql
-- 四舍五入
SELECT ROUND(3.14159, 2);  -- 3.14

-- 向上取整
SELECT CEILING(3.1);      -- 4
SELECT CEIL(3.1);         -- 4

-- 向下取整
SELECT FLOOR(3.9);        -- 3

-- 绝对值
SELECT ABS(-5);           -- 5

-- 平方根
SELECT SQRT(16);          -- 4

-- 幂运算
SELECT POWER(2, 3);       -- 8
SELECT 2^3;               -- 8

-- 取模
SELECT MOD(10, 3);        -- 1

-- 随机数
SELECT RANDOM();         -- 0-1 之间的随机数
SELECT RANDOM() * 100;   -- 0-100 之间的随机数
SELECT FLOOR(RANDOM() * 100) + 1;  -- 1-100 之间的随机整数

-- 数学常数
SELECT PI();              -- 3.14159...
SELECT DEGREES(PI());     -- 180
SELECT RADIANS(180);      -- 3.14159...
```

---

### 2.4 条件函数

```sql
-- CASE 表达式
SELECT 
    name,
    CASE 
        WHEN score >= 90 THEN '优秀'
        WHEN score >= 80 THEN '良好'
        WHEN score >= 60 THEN '及格'
        ELSE '不及格'
    END AS grade
FROM students;

-- COALESCE（返回第一个非NULL值）
SELECT COALESCE(phone, email, '无联系方式') FROM users;

-- NULLIF（相等返回NULL）
SELECT NULLIF(a, b);  -- 如果 a=b 返回 NULL

-- GREATEST（最大值）
SELECT GREATEST(10, 20, 30);  -- 30

-- LEAST（最小值）
SELECT LEAST(10, 20, 30);    -- 10
```

---

## 三、PostgreSQL 高级功能

### 3.1 CTE（公用表表达式）

```sql
-- 简单 CTE
WITH high_salary AS (
    SELECT * FROM employees WHERE salary > 10000
)
SELECT * FROM high_salary;

-- 递归 CTE
WITH RECURSIVE employee_tree AS (
    -- 初始查询
    SELECT id, name, manager_id, 1 AS level
    FROM employees
    WHERE id = 1
    
    UNION ALL
    
    -- 递归查询
    SELECT e.id, e.name, e.manager_id, et.level + 1
    FROM employees e
    JOIN employee_tree et ON e.manager_id = et.id
)
SELECT * FROM employee_tree;

-- 多个 CTE
WITH 
    dept_avg AS (
        SELECT department_id, AVG(salary) AS avg_salary
        FROM employees
        GROUP BY department_id
    ),
    high_salary AS (
        SELECT e.id, e.name, e.salary, da.avg_salary
        FROM employees e
        JOIN dept_avg da ON e.department_id = da.department_id
        WHERE e.salary > da.avg_salary * 1.5
    )
SELECT * FROM high_salary;

-- CTE 数据修改
WITH updated AS (
    UPDATE employees SET salary = salary * 1.1 
    WHERE department_id = 1
    RETURNING *
)
SELECT * FROM updated;
```

---

### 3.2 窗口函数

```sql
-- 排名函数
SELECT 
    id,
    name,
    salary,
    ROW_NUMBER() OVER (ORDER BY salary DESC) AS row_num,
    RANK() OVER (ORDER BY salary DESC) AS rank,
    DENSE_RANK() OVER (ORDER BY salary DESC) AS dense_rank
FROM employees;

-- 分组排名
SELECT 
    department_id,
    name,
    salary,
    RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) AS dept_rank
FROM employees;

-- 偏移函数
SELECT 
    id,
    name,
    salary,
    LAG(salary) OVER (ORDER BY id) AS prev_salary,
    LEAD(salary) OVER (ORDER BY id) AS next_salary
FROM employees;

-- 聚合窗口函数
SELECT 
    order_date,
    amount,
    SUM(amount) OVER (ORDER BY order_date) AS cumulative_sum,
    AVG(amount) OVER (
        ORDER BY order_date
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS moving_avg,
    FIRST_VALUE(amount) OVER (
        ORDER BY order_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS first_amount,
    LAST_VALUE(amount) OVER (
        ORDER BY order_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS last_amount
FROM orders;

-- 窗口子句
SELECT 
    department_id,
    name,
    salary,
    AVG(salary) OVER (
        PARTITION BY department_id
        ORDER BY salary DESC
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS avg_so_far
FROM employees;
```

---

### 3.3 全文搜索

```sql
-- 创建表
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    tsv TSVECTOR
);

-- 创建全文搜索索引
CREATE INDEX idx_tsv ON articles USING GIN (tsv);

-- 插入数据（自动生成 TSVECTOR）
INSERT INTO articles (title, content) VALUES 
('PostgreSQL 教程', 'PostgreSQL 是一个强大的开源数据库');
UPDATE articles SET tsv = to_tsvector('english', coalesce(title, '') || ' ' || coalesce(content, ''));

-- 全文搜索
SELECT * FROM articles WHERE tsv @@ to_tsquery('english', 'PostgreSQL');

-- 复杂查询
SELECT * FROM articles WHERE tsv @@ to_tsquery('english', 'PostgreSQL & 数据库');
SELECT * FROM articles WHERE tsv @@ to_tsquery('english', 'PostgreSQL | MySQL');
SELECT * FROM articles WHERE tsv @@ to_tsquery('english', 'PostgreSQL & !MySQL');

-- 自动更新触发器
CREATE OR REPLACE FUNCTION article_tsv_trigger() RETURNS TRIGGER AS $$
BEGIN
    NEW.tsv := to_tsvector('english', coalesce(NEW.title, '') || ' ' || coalesce(NEW.content, ''));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER article_tsv_update
BEFORE INSERT OR UPDATE ON articles
FOR EACH ROW
EXECUTE FUNCTION article_tsv_trigger();

-- 排序结果
SELECT *, ts_rank(tsv, to_tsquery('english', 'PostgreSQL')) AS rank
FROM articles
WHERE tsv @@ to_tsquery('english', 'PostgreSQL')
ORDER BY rank DESC;

-- 高亮关键词
SELECT title, ts_headline('english', content, to_tsquery('english', 'PostgreSQL'))
FROM articles
WHERE tsv @@ to_tsquery('english', 'PostgreSQL');
```

---

### 3.4 RETURNING 子句

```sql
-- INSERT RETURNING
INSERT INTO users (name, email) 
VALUES ('张三', 'zhangsan@example.com')
RETURNING id, name, created_at;

-- UPDATE RETURNING
UPDATE users SET email = 'new@example.com' WHERE id = 1
RETURNING id, email, updated_at;

-- DELETE RETURNING
DELETE FROM users WHERE id = 1
RETURNING *;

-- 批量插入并返回结果
INSERT INTO users (name, email) 
VALUES 
    ('张三', 'a@example.com'),
    ('李四', 'b@example.com')
RETURNING id, name;
```

---

### 3.5 UPSERT（INSERT ... ON CONFLICT）

```sql
-- ON CONFLICT DO UPDATE
INSERT INTO users (id, name, email)
VALUES (1, '张三', 'zhangsan@example.com')
ON CONFLICT (id) 
DO UPDATE SET 
    name = EXCLUDED.name,
    email = EXCLUDED.email,
    updated_at = NOW()
WHERE users.id = EXCLUDED.id;

-- ON CONFLICT DO NOTHING
INSERT INTO users (id, name, email)
VALUES (1, '张三', 'zhangsan@example.com')
ON CONFLICT (id) 
DO NOTHING;

-- 复杂的 UPSERT
INSERT INTO orders (user_id, product_id, quantity, amount)
VALUES (1, 100, 2, 199.99)
ON CONFLICT (user_id, product_id)
DO UPDATE SET
    quantity = orders.quantity + EXCLUDED.quantity,
    amount = orders.amount + EXCLUDED.amount,
    updated_at = NOW()
WHERE orders.user_id = EXCLUDED.user_id
  AND orders.product_id = EXCLUDED.product_id;
```

---

### 3.6 LATERAL JOIN

```sql
-- LATERAL 允许引用左侧表的数据
SELECT 
    u.name,
    t.last_order_date,
    t.total_amount
FROM users u
LEFT JOIN LATERAL (
    SELECT 
        MAX(order_date) AS last_order_date,
        SUM(amount) AS total_amount
    FROM orders o
    WHERE o.user_id = u.id
) t ON TRUE;

-- 计算每个用户最近的3个订单
SELECT 
    u.name,
    t.order_date,
    t.amount
FROM users u
LEFT JOIN LATERAL (
    SELECT order_date, amount
    FROM orders o
    WHERE o.user_id = u.id
    ORDER BY order_date DESC
    LIMIT 3
) t ON TRUE
ORDER BY u.name, t.order_date DESC;
```

---

## 四、PostgreSQL 存储过程

### 4.1 PL/pgSQL 基本语法

```sql
-- 创建函数
CREATE OR REPLACE FUNCTION 函数名(参数)
RETURNS 返回类型 AS $$
DECLARE
    -- 变量声明
    变量名 类型;
BEGIN
    -- 函数体
    RETURN 返回值;
END;
$$ LANGUAGE plpgsql;

-- 示例：简单函数
CREATE OR REPLACE FUNCTION get_user_count()
RETURNS INT AS $$
DECLARE
    count INT;
BEGIN
    SELECT COUNT(*) INTO count FROM users;
    RETURN count;
END;
$$ LANGUAGE plpgsql;

-- 调用
SELECT get_user_count();
```

---

### 4.2 参数类型

```sql
-- IN 参数（默认）
CREATE OR REPLACE FUNCTION get_user_by_id(user_id INT)
RETURNS TABLE(id INT, name VARCHAR, email VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT id, name, email FROM users WHERE id = user_id;
END;
$$ LANGUAGE plpgsql;

-- OUT 参数
CREATE OR REPLACE FUNCTION get_user_info(
    IN user_id INT,
    OUT user_name VARCHAR,
    OUT user_email VARCHAR
) AS $$
BEGIN
    SELECT name, email INTO user_name, user_email 
    FROM users WHERE id = user_id;
END;
$$ LANGUAGE plpgsql;

-- 调用
SELECT * FROM get_user_info(1);

-- INOUT 参数
CREATE OR REPLACE FUNCTION increment_value(INOUT value INT)
AS $$
BEGIN
    value := value + 1;
END;
$$ LANGUAGE plpgsql;

-- 调用
DO $$
DECLARE
    val INT := 10;
BEGIN
    PERFORM increment_value(val);
    RAISE NOTICE 'Value: %', val;
END $$;
```

---

### 4.3 控制语句

```sql
-- IF 语句
CREATE OR REPLACE FUNCTION categorize_age(age INT)
RETURNS VARCHAR AS $$
BEGIN
    IF age < 18 THEN
        RETURN '未成年';
    ELSIF age < 60 THEN
        RETURN '成年';
    ELSE
        RETURN '老年';
    END IF;
END;
$$ LANGUAGE plpgsql;

-- 循环
CREATE OR REPLACE FUNCTION generate_numbers(n INT)
RETURNS SETOF INT AS $$
DECLARE
    i INT := 1;
BEGIN
    WHILE i <= n LOOP
        RETURN NEXT i;
        i := i + 1;
    END LOOP;
    RETURN;
END;
$$ LANGUAGE plpgsql;

-- FOR 循环
CREATE OR REPLACE FUNCTION process_employees()
RETURNS VOID AS $$
DECLARE
    emp_record RECORD;
BEGIN
    FOR emp_record IN SELECT id, name, salary FROM employees
    LOOP
        UPDATE employees 
        SET salary = emp_record.salary * 1.1 
        WHERE id = emp_record.id;
        
        RAISE NOTICE 'Processed: %, %', emp_record.id, emp_record.name;
    END LOOP;
END;
$$ LANGUAGE plpgsql;
```

---

### 4.4 异常处理

```sql
CREATE OR REPLACE FUNCTION safe_transfer(
    from_id INT,
    to_id INT,
    amount NUMERIC
) RETURNS VARCHAR AS $$
DECLARE
    from_balance NUMERIC;
BEGIN
    -- 检查余额
    SELECT balance INTO from_balance FROM accounts WHERE id = from_id;
    
    IF from_balance < amount THEN
        RAISE EXCEPTION '余额不足';
    END IF;
    
    -- 开始事务
    BEGIN
        -- 扣款
        UPDATE accounts SET balance = balance - amount WHERE id = from_id;
        
        -- 加钱
        UPDATE accounts SET balance = balance + amount WHERE id = to_id;
        
        RETURN '转账成功';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE '转账失败: %', SQLERRM;
            RETURN '转账失败';
    END;
END;
$$ LANGUAGE plpgsql;
```

---

## 五、PostgreSQL 性能优化

### 5.1 EXPLAIN ANALYZE

```sql
-- 基本用法
EXPLAIN SELECT * FROM users WHERE email = 'test@example.com';

-- 执行分析
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';

-- 格式化输出
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) 
SELECT * FROM users WHERE email = 'test@example.com';

-- EXPLAIN 关键信息
-- Scan Type: 扫描类型（Seq Scan、Index Scan、Bitmap Scan）
-- Rows: 估算行数
-- Actual Rows: 实际行数
-- Total Runtime: 总执行时间
-- Planning Time: 规划时间
-- Execution Time: 执行时间
-- Buffers: 缓冲区使用情况
```

---

### 5.2 慢查询日志

```sql
-- 查看慢查询配置
SHOW log_min_duration_statement;  -- 慢查询阈值（毫秒）
SHOW log_statement;                -- 记录的语句类型

-- 开启慢查询日志（需要修改配置文件）
# postgresql.conf
log_min_duration_statement = 1000  -- 超过1秒的查询
log_statement = 'all'
```

---

### 5.3 VACUUM 和 ANALYZE

```sql
-- VACUUM：回收空间
VACUUM users;

-- VACUUM FULL：完全回收（需要锁定表）
VACUUM FULL users;

-- ANALYZE：更新统计信息
ANALYZE users;

-- VACUUM ANALYZE：回收并更新统计信息
VACUUM ANALYZE users;

-- 查看表大小
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## 六、本节面试考点

| 考点 | 答案要点 |
|------|----------|
| 数组类型 | INT[]、VARCHAR[]，索引从1开始 |
| JSON vs JSONB | JSON 存原文本，JSONB 二进制支持索引 |
| JSONB 操作符 | @> 包含、? 键存在、|| 追加 |
| JSONB 索引 | GIN 索引，支持 @>、?、?|、?& |
| 范围类型 | INT4RANGE、TSRANGE、DATERANGE |
| 范围操作符 | @> 包含、&& 重叠、<< 在之前 |
| 字符串拼接 | 使用 || |
| UPSERT | INSERT ... ON CONFLICT |
| RETURNING | 返回操作的结果 |
| LATERAL JOIN | 引用左侧表数据 |
| 全文搜索 | to_tsvector、to_tsquery、@@ 操作符 |
| PL/pgSQL | PostgreSQL 存储过程语言 |

---

## 课后练习

1. 创建一个包含数组字段的表
2. 使用 JSONB 存储产品属性，并添加 GIN 索引
3. 实现一个递归 CTE 查询员工层级
4. 使用 UPSERT 实现订单数量累加
5. 创建一个存储过程，使用异常处理

---

## 📝 自测题

1. PostgreSQL 中 JSON 和 JSONB 的主要区别是？\
   A. 完全相同  B. JSONB 支持索引，JSON 不支持  C. JSON 更快  D. JSONB 不推荐使用
2. PostgreSQL 中字符串拼接推荐的运算符是？\
   A. +  B. CONCAT  C. ||  D. &
3. UPSERT 对应的语法是？\
   A. REPLACE INTO  B. INSERT ... ON CONFLICT  C. MERGE  D. INSERT OR UPDATE
4. PostgreSQL 数组索引从几开始？\
   A. 0  B. 1  C. -1  D. 可以自定义

**答案：1-B, 2-C, 3-B, 4-B**

---

下一课：Neo4j 基础（→ `09-Neo4j基础.md`）