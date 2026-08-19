# SQL 学习笔记 - MySQL 特有功能

## 了解与安装

基本创建:
drop database if exists XxxDB;
create database XxxDB;
use XxxDB;

下载mysql --> 搜索mysql官网下载即可 
cd mysql对应的bin文件夹 
mysql --initialize-insecure 初始化命令(实现无密进入)
mysqld --install MySQL 安装对应的服务 
win+r services.msc 启动mysql对应的服务 
-->
登陆
mysql -P 3306 -u root -p 
输入密码 
ALTER USER USER() IDENTIFIED BY '新密码'; 修改当前登录的密码 

## 一、MySQL 数据引擎

### 1.1 常用引擎对比

| 引擎 | 事务 | 外键 | 全文索引 | 聚簇索引 | 使用场景 |
|------|------|------|----------|----------|----------|
| **InnoDB** | ✅ | ✅ | ❌ | ✅ | 事务系统（默认） |
| **MyISAM** | ❌ | ❌ | ✅ | ❌ | 只读/读多写少 |
| **Memory** | ❌ | ❌ | ❌ | ❌ | 临时表、缓存 |
| **CSV** | ❌ | ❌ | ❌ | ❌ | 数据交换 |
| **Archive** | ❌ | ❌ | ❌ | ❌ | 归档存储 |

---

### 1.2 引擎特性详解

#### InnoDB（推荐）

```sql
-- 创建 InnoDB 表
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE
) ENGINE=InnoDB;

-- 特点：
-- ✅ 支持事务
-- ✅ 支持外键
-- ✅ 支持行级锁
-- ✅ 支持崩溃恢复
-- ✅ 聚簇索引（数据按主键存储）
-- ❌ 不支持全文索引（MySQL 5.6+ 支持）
```

#### MyISAM

```sql
-- 创建 MyISAM 表
CREATE TABLE articles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100),
    content TEXT
) ENGINE=MyISAM;

-- 特点：
-- ✅ 查询性能高
-- ✅ 支持全文索引
-- ✅ 表级锁
-- ❌ 不支持事务
-- ❌ 不支持外键
-- ❌ 崩溃后可能损坏
```

#### Memory

```sql
-- 创建 Memory 表
CREATE TABLE cache (
    key VARCHAR(50) PRIMARY KEY,
    value TEXT,
    expire_at DATETIME
) ENGINE=Memory;

-- 特点：
-- ✅ 存储在内存，速度极快
-- ✅ 支持哈希索引
-- ❌ 重启后数据丢失
-- ❌ 不支持事务
-- ❌ 不支持 BLOB/TEXT
```

---

### 1.3 查看和修改引擎

```sql
-- 查看默认引擎
SHOW VARIABLES LIKE 'default_storage_engine';

-- 查看表引擎
SHOW TABLE STATUS WHERE Name = 'users';

-- 修改表引擎
ALTER TABLE users ENGINE=InnoDB;

-- 修改默认引擎（配置文件 my.cnf）
[mysqld]
default-storage-engine=InnoDB
```

---

## 二、MySQL 分区表

### 2.1 分区类型

| 类型 | 说明 |
|------|------|
| **RANGE** | 按值范围分区 |
| **LIST** | 按值列表分区 |
| **HASH** | 按哈希值分区 |
| **KEY** | 类似 HASH，使用 MySQL 内置哈希 |
| **COLUMNS** | 按多列分区 |

---

### 2.2 RANGE 分区

```sql
-- 按年份分区
CREATE TABLE orders (
    id INT AUTO_INCREMENT,
    order_date DATE NOT NULL,
    amount DECIMAL(10,2),
    PRIMARY KEY (id, order_date)
)
PARTITION BY RANGE (YEAR(order_date)) (
    PARTITION p2021 VALUES LESS THAN (2022),
    PARTITION p2022 VALUES LESS THAN (2023),
    PARTITION p2023 VALUES LESS THAN (2024),
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION pmax VALUES LESS THAN MAXVALUE
);

-- 查询特定分区（只扫描相关分区）
SELECT * FROM orders PARTITION(p2023) WHERE amount > 1000;

-- 添加分区
ALTER TABLE orders ADD PARTITION (
    PARTITION p2025 VALUES LESS THAN (2026)
);

-- 删除分区（数据也会被删除）
ALTER TABLE orders DROP PARTITION p2021;
```

---

### 2.3 LIST 分区

```sql
-- 按地区分区
CREATE TABLE customers (
    id INT AUTO_INCREMENT,
    name VARCHAR(50),
    region VARCHAR(20),
    PRIMARY KEY (id, region)
)
PARTITION BY LIST COLUMNS(region) (
    PARTITION p_east VALUES IN ('北京', '上海', '江苏'),
    PARTITION p_south VALUES IN ('广东', '广西', '海南'),
    PARTITION p_west VALUES IN ('四川', '云南', '贵州'),
    PARTITION p_other VALUES IN (DEFAULT)
);
```

---

### 2.4 HASH 分区

```sql
-- 按 ID 哈希分区
CREATE TABLE logs (
    id INT AUTO_INCREMENT,
    log_time DATETIME,
    message TEXT,
    PRIMARY KEY (id)
)
PARTITION BY HASH(id) 
PARTITIONS 4;

-- 按 USER_ID 哈希分区
CREATE TABLE user_actions (
    id INT AUTO_INCREMENT,
    user_id INT,
    action VARCHAR(20),
    created_at DATETIME,
    PRIMARY KEY (id, user_id)
)
PARTITION BY HASH(user_id) 
PARTITIONS 8;
```

---

### 2.5 分区查询

```sql
-- 查看分区信息
SELECT 
    PARTITION_NAME,
    PARTITION_METHOD,
    PARTITION_EXPRESSION,
    PARTITION_DESCRIPTION,
    TABLE_ROWS
FROM information_schema.PARTITIONS
WHERE TABLE_NAME = 'orders';

-- 查看分区数据
SELECT COUNT(*) FROM orders PARTITION(p2023);

-- 优化查询（指定分区）
EXPLAIN PARTITIONS SELECT * FROM orders WHERE YEAR(order_date) = 2023;
```

---

## 三、MySQL 全文索引

### 3.1 创建全文索引

```sql
-- 创建表时添加全文索引
CREATE TABLE articles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100),
    content TEXT,
    FULLTEXT INDEX ft_title_content (title, content)
) ENGINE=MyISAM;  -- MyISAM 或 InnoDB (MySQL 5.6+)

-- 为现有表添加全文索引
ALTER TABLE articles ADD FULLTEXT INDEX ft_content (content);

-- 使用 ngram 分词器（中文全文索引）
CREATE TABLE articles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100),
    content TEXT,
    FULLTEXT INDEX ft_content (content) 
    WITH PARSER ngram
) ENGINE=InnoDB;
```

---

### 3.2 全文搜索语法

```sql
-- 基本全文搜索
SELECT * FROM articles 
WHERE MATCH(title, content) AGAINST('MySQL 数据库');

-- 自然语言模式（默认）
SELECT * FROM articles 
WHERE MATCH(content) AGAINST('MySQL' IN NATURAL LANGUAGE MODE);

-- 布尔模式
SELECT * FROM articles 
WHERE MATCH(content) AGAINST('+MySQL -PostgreSQL' IN BOOLEAN MODE);
-- +表示必须包含，-表示必须不包含

-- 查询扩展模式
SELECT * FROM articles 
WHERE MATCH(content) AGAINST('MySQL' WITH QUERY EXPANSION);

-- 返回相关度
SELECT 
    id, 
    title,
    MATCH(title, content) AGAINST('MySQL 数据库') AS score
FROM articles
WHERE MATCH(title, content) AGAINST('MySQL 数据库')
ORDER BY score DESC;
```

---

### 3.3 全文搜索布尔操作符

| 操作符 | 说明 | 示例 |
|--------|------|------|
| `+` | 必须包含 | `'+MySQL +数据库'` |
| `-` | 必须不包含 | `'+MySQL -PostgreSQL'` |
| `>` | 提高权重 | `'+MySQL >数据库'` |
| `<` | 降低权重 | `'+MySQL <数据库'` |
| `()` | 分组 | `'+(MySQL 数据库)'` |
| `~` | 负相关 | `'MySQL ~PostgreSQL'` |
| `*` | 通配符 | `'MySQL*'` |
| `""` | 精确匹配 | `'"MySQL 数据库"'` |

```sql
-- 复杂布尔查询
SELECT * FROM articles 
WHERE MATCH(content) AGAINST(
    '+MySQL +数据库 >优化 <问题 *(存储* +性能)' 
    IN BOOLEAN MODE
);
```

---

## 四、MySQL JSON 类型

### 4.1 创建 JSON 列

```sql
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    attributes JSON,  -- JSON 类型
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

### 4.2 插入 JSON 数据

```sql
-- 插入 JSON 对象
INSERT INTO products (name, attributes) VALUES 
('手机', 
 JSON_OBJECT(
     'brand', 'Apple',
     'model', 'iPhone 15',
     'price', 7999,
     'specs', JSON_ARRAY('128GB', '6.1英寸', 'A17芯片')
 )
);

-- 插入 JSON 数组
INSERT INTO products (name, attributes) VALUES 
('配件', 
 JSON_ARRAY(
     JSON_OBJECT('name', '充电器', 'price', 199),
     JSON_OBJECT('name', '耳机', 'price', 599)
 )
);
```

---

### 4.3 查询 JSON 数据

```sql
-- 提取 JSON 值
SELECT 
    name,
    JSON_EXTRACT(attributes, '$.brand') AS brand,
    JSON_EXTRACT(attributes, '$.price') AS price
FROM products;

-- 使用 -> 操作符（MySQL 5.7.9+）
SELECT 
    name,
    attributes->'$.brand' AS brand,
    attributes->'$.price' AS price
FROM products;

-- 使用 ->> 操作符（自动转字符串）
SELECT 
    name,
    attributes->>'$.brand' AS brand
FROM products;

-- 查询 JSON 数组
SELECT 
    name,
    attributes->>'$.specs[0]' AS spec
FROM products;

-- JSON 路径通配符
SELECT 
    name,
    attributes->>'$.specs[*]' AS all_specs
FROM products;
```

---

### 4.4 JSON 修改函数

```sql
-- JSON_SET：设置值（不存在则添加，存在则修改）
UPDATE products 
SET attributes = JSON_SET(attributes, '$.price', 6999)
WHERE id = 1;

-- JSON_INSERT：插入值（不存在才插入）
UPDATE products 
SET attributes = JSON_INSERT(attributes, '$.color', '黑色')
WHERE id = 1;

-- JSON_REPLACE：替换值（存在才替换）
UPDATE products 
SET attributes = JSON_REPLACE(attributes, '$.price', 6999)
WHERE id = 1;

-- JSON_REMOVE：删除值
UPDATE products 
SET attributes = JSON_REMOVE(attributes, '$.specs[0]')
WHERE id = 1;

-- JSON_ARRAY_APPEND：追加到数组
UPDATE products 
SET attributes = JSON_ARRAY_APPEND(attributes, '$.specs', '5G')
WHERE id = 1;
```

---

### 4.5 JSON 函数

```sql
-- JSON_KEYS：获取所有键
SELECT JSON_KEYS(attributes) AS keys FROM products;

-- JSON_LENGTH：获取长度
SELECT JSON_LENGTH(attributes) AS length FROM products;

-- JSON_VALID：验证 JSON 格式
SELECT 
    id,
    name,
    CASE 
        WHEN JSON_VALID(attributes) THEN '有效'
        ELSE '无效'
    END AS json_status
FROM products;

-- JSON_PRETTY：格式化输出
SELECT JSON_PRETTY(attributes) AS formatted_json FROM products;

-- JSON_SEARCH：搜索值
SELECT * FROM products 
WHERE JSON_SEARCH(attributes, 'one', 'Apple') IS NOT NULL;

-- JSON_CONTAINS：包含检查
SELECT * FROM products 
WHERE JSON_CONTAINS(attributes->'$.specs', '"128GB"');
```

---

### 4.6 JSON 索引

```sql
-- 为 JSON 列创建虚拟列并添加索引
ALTER TABLE products 
ADD COLUMN brand VARCHAR(50) 
    GENERATED ALWAYS AS (attributes->>'$.brand') STORED,
ADD INDEX idx_brand (brand);

-- 查询时可以使用索引
SELECT * FROM products WHERE brand = 'Apple';

-- MySQL 8.0.17+ 支持多值索引
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_data JSON,
    INDEX idx_order_data ((CAST(order_data->'$.items[*].product_id' AS UNSIGNED ARRAY)))
);
```

---

## 五、MySQL 8.0 新特性

### 5.1 CTE（公用表表达式）

```sql
-- 简单 CTE
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
```

---

### 5.2 窗口函数（MySQL 8.0+）

```sql
-- 行号
SELECT 
    id,
    name,
    salary,
    ROW_NUMBER() OVER (ORDER BY salary DESC) AS rank
FROM employees;

-- 分组排名
SELECT 
    department_id,
    name,
    salary,
    RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) AS dept_rank
FROM employees;

-- 累计求和
SELECT 
    order_date,
    amount,
    SUM(amount) OVER (ORDER BY order_date) AS cumulative_sum
FROM orders;

-- 移动平均
SELECT 
    order_date,
    amount,
    AVG(amount) OVER (
        ORDER BY order_date
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS moving_avg
FROM orders;
```

---

### 5.3 索引隐藏

```sql
-- 隐藏索引（用于测试）
ALTER TABLE users ALTER INDEX idx_email INVISIBLE;

-- 恢复索引
ALTER TABLE users ALTER INDEX idx_email VISIBLE;

-- 查看索引状态
SELECT 
    INDEX_NAME,
    COLUMN_NAME,
    IS_VISIBLE
FROM information_schema.STATISTICS
WHERE TABLE_NAME = 'users';
```

---

### 5.4 降序索引

```sql
-- MySQL 8.0+ 支持降序索引
CREATE INDEX idx_salary_desc ON employees(salary DESC);

-- 查询可以使用降序索引
SELECT * FROM employees ORDER BY salary DESC;
```

---

### 5.5 函数索引

```sql
-- MySQL 8.0+ 支持函数索引
CREATE INDEX idx_name_upper ON users((UPPER(name)));

-- 查询可以使用索引
SELECT * FROM users WHERE UPPER(name) = 'ZHANGSAN';
```

---

## 六、MySQL 性能优化

### 6.1 EXPLAIN 分析查询

```sql
-- 基本用法
EXPLAIN SELECT * FROM users WHERE email = 'test@example.com';

-- 格式化输出（MySQL 8.0+）
EXPLAIN FORMAT=JSON SELECT * FROM users WHERE email = 'test@example.com';

-- EXPLAIN 列说明
-- id: 查询序列号
-- select_type: 查询类型（SIMPLE、PRIMARY、SUBQUERY、DERIVED、UNION）
-- table: 访问的表
-- partitions: 匹配的分区
-- type: 访问类型（ALL < index < range < ref < eq_ref < const < system）
-- possible_keys: 可能使用的索引
-- key: 实际使用的索引
-- key_len: 使用索引的长度
-- ref: 索引比较的列
-- rows: 估算扫描的行数
-- filtered: 过滤后剩余的百分比
-- Extra: 额外信息
```

---

### 6.2 慢查询日志

```sql
-- 查看慢查询配置
SHOW VARIABLES LIKE 'slow_query%';

-- 开启慢查询日志
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;  -- 超过2秒的查询

-- 查看慢查询日志文件路径
SHOW VARIABLES LIKE 'slow_query_log_file';
```

---

### 6.3 查询缓存（MySQL 5.7及以下）

```sql
-- MySQL 5.7 查看查询缓存
SHOW VARIABLES LIKE 'query_cache%';

-- MySQL 8.0 已移除查询缓存
```

---

### 6.4 性能分析

```sql
-- 使用 Profiler 分析查询
SET profiling = 1;

-- 执行查询
SELECT * FROM users WHERE email = 'test@example.com';

-- 查看性能分析
SHOW PROFILES;

-- 查看详细分析
SHOW PROFILE FOR QUERY 1;

-- 查看所有分析
SHOW PROFILE;
```

---

## 七、MySQL 常用函数

### 7.1 字符串函数

```sql
-- 字符串拼接
SELECT CONCAT(name, '(', email, ')') FROM users;

-- 字符串重复
SELECT REPEAT('abc', 3);  -- abcabcabc

-- 字符串替换
SELECT REPLACE('hello world', 'world', 'MySQL');  -- hello MySQL

-- 字符串截取
SELECT SUBSTRING('hello world', 1, 5);  -- hello
SELECT SUBSTRING('hello world', 7);     -- world

-- 字符串长度
SELECT LENGTH('hello');        -- 5（字节长度）
SELECT CHAR_LENGTH('hello');   -- 5（字符长度）

-- 字符串位置
SELECT LOCATE('world', 'hello world');  -- 7

-- 字符串反转
SELECT REVERSE('hello');  -- olleh

-- 格式化
SELECT FORMAT(12345.6789, 2);  -- 12,345.68
```

---

### 7.2 日期函数

```sql
-- 当前日期时间
SELECT NOW();           -- 2024-01-15 14:30:00
SELECT CURRENT_DATE();  -- 2024-01-15
SELECT CURRENT_TIME();  -- 14:30:00

-- 日期计算
SELECT DATE_ADD(NOW(), INTERVAL 7 DAY);      -- 加7天
SELECT DATE_SUB(NOW(), INTERVAL 1 MONTH);    -- 减1个月
SELECT DATE_ADD(NOW(), INTERVAL '1-2' YEAR_MONTH);  -- 加1年2个月

-- 日期差
SELECT DATEDIFF('2024-12-31', '2024-01-01');  -- 365天

-- 日期格式化
SELECT DATE_FORMAT(NOW(), '%Y-%m-%d %H:%i:%s');
SELECT TIME_FORMAT(NOW(), '%H:%i:%s');

-- 日期部分提取
SELECT YEAR(NOW());           -- 2024
SELECT MONTH(NOW());          -- 1
SELECT DAY(NOW());            -- 15
SELECT HOUR(NOW());           -- 14
SELECT MINUTE(NOW());         -- 30
SELECT SECOND(NOW());         -- 0

-- 日期转换
SELECT STR_TO_DATE('2024-01-15', '%Y-%m-%d');
```

---

### 7.3 数学函数

```sql
-- 四舍五入
SELECT ROUND(3.14159, 2);  -- 3.14
SELECT ROUND(3.5);        -- 4
SELECT ROUND(3.4);        -- 3

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
SELECT POW(2, 3);         -- 8
SELECT POWER(2, 3);       -- 8

-- 取模
SELECT MOD(10, 3);        -- 1
SELECT 10 % 3;            -- 1

-- 随机数
SELECT RAND();            -- 0-1 之间的随机数
SELECT RAND() * 100;      -- 0-100 之间的随机数
SELECT FLOOR(RAND() * 100) + 1;  -- 1-100 之间的随机整数
```

---

### 7.4 条件函数

```sql
-- IF 函数
SELECT IF(score >= 60, '及格', '不及格') FROM students;

-- IFNULL 函数
SELECT IFNULL(phone, '无电话') FROM users;

-- NULLIF 函数
SELECT NULLIF(a, b);  -- 如果 a=b 返回 NULL，否则返回 a

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
```

---

## 八、本节面试考点

| 考点 | 答案要点 |
|------|----------|
| MySQL 引擎 | InnoDB（默认）、MyISAM、Memory |
| InnoDB 特点 | 支持事务、外键、行级锁、聚簇索引 |
| MyISAM 特点 | 查询性能高、支持全文索引、表级锁 |
| 分区类型 | RANGE、LIST、HASH、KEY、COLUMNS |
| 全文索引 | MATCH ... AGAINST，支持布尔模式 |
| JSON 类型 | JSON_OBJECT、JSON_ARRAY、JSON_EXTRACT |
| JSON 索引 | 虚拟列 + STORED 索引 |
| CTE | WITH 子句，支持递归 |
| 窗口函数 | MySQL 8.0+，ROW_NUMBER、RANK 等 |
| 慢查询 | slow_query_log、long_query_time |
| EXPLAIN | 查看执行计划，type 列是关键 |
| 聚簇索引 | 数据按主键存储，一张表只能有一个 |

---

## 课后练习

1. 创建一个按日期分区的订单表
2. 为文章表添加全文索引，实现搜索功能
3. 使用 JSON 类型存储商品属性
4. 使用 CTE 查询员工层级关系
5. 分析一个慢查询并优化

---

## 📝 自测题

1. MySQL 默认的存储引擎是？\
   A. MyISAM  B. Memory  C. InnoDB  D. CSV
2. EXPLAIN 执行计划中最重要的字段是？\
   A. id  B. table  C. type  D. rows
3. MySQL 8.0 支持的窗口函数包括？\
   A. ROW_NUMBER  B. RANK  C. DENSE_RANK  D. 以上全部
4. JSON 列添加索引的正确方式是？\
   A. 直接创建 B-tree 索引  B. 使用虚拟列 + STORED 索引  C. JSON 不支持索引  D. 使用 HASH 索引

**答案：1-C, 2-C, 3-D, 4-B**

---

下一课：PostgreSQL 特有功能（→ `08-PostgreSQL特有功能.md`）