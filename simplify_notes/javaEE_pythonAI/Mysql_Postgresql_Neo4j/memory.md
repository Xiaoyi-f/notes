# 基本术语

**DBMS 数据库管理系统 --> MySQL、PostgreSQL、Neo4j(NoSQL/图)**

**数据库 表 列 行 主键(唯一标识) 外键(关联其他表的字段)**

 **操作数据库的脚本文件后缀: .sql**

**对应代码由语句组成，语句由多个子句组成**

##  子句书写顺序

**SELECT -> FROM -> WHERE -> GROUP BY -> HAVING -> ORDER BY -> LIMIT**

### SELECT查询

```
SELECT 列 FROM 表;

SELECT 

	列, 

	列, 

	... 

	FROM 表;

SELECT * FROM 表;  

-- 不建议使用 SELECT * FROM 表; 性能差 不灵活 

```

### DISTINCT去重

```
SELECT DISTINCT ...;
```

### ORDER BY排序

```
SELECT 列 FROM 表 ORDER BY 列 ASC/DESC; 
-- 排序规则 
数值大小 字典序 日期先后 NULL排序于最前或最后(看数据库) 中文拼音或编码 
```





## 数据库引擎执行顺序

FROM -> WHERE -> GROUP BY -> HAVING -> SELECT -> ORDER BY -> LIMIT 





