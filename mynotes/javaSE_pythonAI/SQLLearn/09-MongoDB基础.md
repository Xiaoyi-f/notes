# SQL 学习笔记 - MongoDB 基础

## 一、MongoDB 概述

### 1.1 什么是 MongoDB

MongoDB 是一个基于文档的 NoSQL 数据库，存储的是 BSON（Binary JSON）格式的文档。

**核心特性：**
- 文档型数据库（无固定表结构）
- 支持复杂嵌套结构
- 支持数组类型
- 原生支持 JavaScript
- 水平扩展能力强

**适用场景：**
- 内容管理系统
- 实时数据分析
- 日志存储
- 物联网数据
- 移动应用后端

---

### 1.2 MongoDB vs SQL 对比

| 特性 | SQL（关系型） | MongoDB（文档型） |
|------|--------------|-------------------|
| **数据模型** | 表、行、列 | 集合、文档、字段 |
| **Schema** | 固定结构 | 灵活，无需预定义 |
| **事务** | 强一致 | 4.0+ 支持多文档事务 |
| **查询语言** | SQL | MQL（MongoDB Query Language） |
| **扩展性** | 垂直扩展为主 | 水平扩展为主 |
| **连接方式** | JOIN | $lookup（聚合） |
| **索引** | B-tree | B-tree、2d、2dsphere |
| **JSON 支持** | 需特殊类型 | 原生支持 |

---

### 1.3 核心概念对应

| SQL 概念 | MongoDB 概念 | 说明 |
|----------|-------------|------|
| 数据库 | Database | 数据库 |
| 表 | Collection | 集合 |
| 行 | Document | 文档 |
| 列 | Field | 字段 |
| 主键 | _id | 主键（默认 ObjectId） |
| 索引 | Index | 索引 |

---

## 二、MongoDB 连接与基础操作

### 2.1 连接 MongoDB

```bash
# 命令行连接
mongod "mongodb://localhost:27017"

# 使用 MongoDB Shell (mongosh)
mongosh "mongodb://localhost:27017"

# 指定用户名密码
mongosh "mongodb://username:password@localhost:27017"

# 指定数据库
mongosh "mongodb://localhost:27017/mydb"

# 远程连接
mongosh "mongodb://user:password@host:port/database?authSource=admin"
```

---

### 2.2 基础操作

```javascript
// 显示所有数据库
show dbs;

// 切换数据库（不存在会自动创建）
use mydb;

// 显示当前数据库
db;

// 显示当前数据库所有集合
show collections;

// 创建集合
db.createCollection("users");

// 删除集合
db.users.drop();

// 删除数据库
db.dropDatabase();

// 查看集合统计信息
db.users.stats();
```

---

## 三、CRUD 操作

### 3.1 插入文档（Create）

```javascript
// 插入单个文档
db.users.insertOne({
    name: "张三",
    age: 25,
    email: "zhangsan@example.com",
    tags: ["developer", "mongodb"],
    address: {
        city: "北京",
        street: "长安街"
    }
});

// 插入多个文档
db.users.insertMany([
    {
        name: "李四",
        age: 30,
        email: "lisi@example.com",
        tags: ["admin"]
    },
    {
        name: "王五",
        age: 28,
        email: "wangwu@example.com",
        tags: ["developer", "postgresql"]
    }
]);

// 使用 save（存在则更新，不存在则插入）
db.users.save({
    _id: ObjectId("507f1f77bcf86cd799439011"),
    name: "张三",
    age: 26
});

// 自动生成 _id
db.users.insertOne({
    name: "赵六",
    age: 22
});
```

---

### 3.2 查询文档（Read）

```javascript
// 查询所有文档
db.users.find();

// 查询指定字段
db.users.find(
    {},                    // 查询条件
    { name: 1, age: 1, _id: 0 }  // 1显示，0不显示
);

// 单条件查询
db.users.find({ age: 25 });

// 多条件查询（AND）
db.users.find({ age: 25, name: "张三" });

// 多条件查询（OR）
db.users.find({
    $or: [
        { age: { $lt: 25 } },
        { age: { $gt: 30 } }
    ]
});

// 查询单个文档
db.users.findOne({ name: "张三" });

// 根据_id查询
db.users.findOne({ 
    _id: ObjectId("507f1f77bcf86cd799439011") 
});

// 查询数组字段
db.users.find({ tags: "developer" });      // 包含指定值
db.users.find({ tags: ["developer"] });     // 精确匹配
db.users.find({ tags: { $all: ["developer", "mongodb"] } });  // 包含所有值
db.users.find({ tags: { $size: 2 } });      // 数组长度
```

---

### 3.3 查询操作符

```javascript
// 比较操作符
db.users.find({ age: { $gt: 25 } });        // 大于
db.users.find({ age: { $gte: 25 } });       // 大于等于
db.users.find({ age: { $lt: 30 } });        // 小于
db.users.find({ age: { $lte: 30 } });       // 小于等于
db.users.find({ age: { $ne: 25 } });        // 不等于
db.users.find({ age: { $in: [25, 30] } });   // 在数组中
db.users.find({ age: { $nin: [25, 30] } });  // 不在数组中

// 逻辑操作符
db.users.find({
    $and: [
        { age: { $gte: 25 } },
        { age: { $lte: 30 } }
    ]
});

db.users.find({
    $or: [
        { age: { $lt: 25 } },
        { age: { $gt: 30 } }
    ]
});

db.users.find({
    age: { $not: { $gte: 25 } }
});

db.users.find({
    $nor: [
        { age: { $lt: 25 } },
        { age: { $gt: 30 } }
    ]
});

// 元素操作符
db.users.find({ tags: { $exists: true } });   // 字段存在
db.users.find({ age: { $type: "number" } });  // 指定类型
db.users.find({ tags: { $mod: [2, 0] } });    // 取模
db.users.find({ name: { $regex: /^张/ } });   // 正则匹配

// 数组操作符
db.users.find({ tags: "developer" });                        // 包含
db.users.find({ tags: { $all: ["developer", "mongodb"] } }); // 包含所有
db.users.find({ tags: { $elemMatch: { $regex: /dev/ } } }); // 元素匹配
db.users.find({ tags: { $size: 2 } });                        // 数组长度

// 嵌套文档查询
db.users.find({ "address.city": "北京" });
db.users.find({ address: { city: "北京", street: "长安街" } });  // 精确匹配
```

---

### 3.4 更新文档（Update）

```javascript
// 更新单个文档
db.users.updateOne(
    { name: "张三" },
    { $set: { age: 26 } }
);

// 更新多个文档
db.users.updateMany(
    { age: { $lt: 25 } },
    { $set: { status: "young" } }
);

// 替换文档
db.users.replaceOne(
    { name: "张三" },
    { name: "张三", age: 30, email: "new@example.com" }
);

// 更新操作符
db.users.updateOne(
    { name: "张三" },
    {
        $set: { age: 26, "address.city": "上海" },           // 设置值
        $unset: { phone: 1 },                                // 删除字段
        $inc: { age: 1 },                                    // 增加数值
        $mul: { salary: 1.1 },                               // 乘以数值
        $rename: { name: "username" },                       // 重命名字段
        $min: { age: 18 },                                   // 取较小值
        $max: { age: 65 },                                   // 取较大值
        $currentDate: { updatedAt: true }                    // 设置当前日期
    }
);

// 数组操作符
db.users.updateOne(
    { name: "张三" },
    {
        $push: { tags: "java" },                             // 添加元素
        $addToSet: { tags: "python" },                       // 添加（去重）
        $pop: { tags: 1 },                                    // 删除最后一个元素
        $pull: { tags: "mongodb" },                          // 删除指定元素
        $pullAll: { tags: ["java", "python"] },              // 删除多个元素
        $push: { tags: { $each: ["a", "b", "c"] } },        // 批量添加
        $push: { tags: { $each: [1, 2, 3], $sort: -1, $slice: 5 } }  // 添加并排序限制
    }
);

// findAndModify（原子操作）
db.users.findAndModify({
    query: { name: "张三" },
    update: { $set: { age: 27 } },
    new: true,    // 返回更新后的文档
    upsert: false // 不存在则不插入
});
```

---

### 3.5 删除文档（Delete）

```javascript
// 删除单个文档
db.users.deleteOne({ name: "张三" });

// 删除多个文档
db.users.deleteMany({ age: { $lt: 18 } });

// 删除集合所有文档
db.users.deleteMany({});

// findOneAndDelete（原子操作）
db.users.findOneAndDelete({ name: "张三" });

// 注意：不要使用 remove（已废弃）
// db.users.remove({ name: "张三" });  // 不推荐
```

---

## 四、聚合管道

### 4.1 聚合管道基础

```javascript
// 基本语法
db.collection.aggregate([
    { $match: { ... } },      // 过滤
    { $group: { ... } },     // 分组
    { $sort: { ... } },      // 排序
    { $limit: ... },         // 限制
    { $skip: ... },          // 跳过
    { $project: { ... } },   // 投影
    // ...
]);
```

---

### 4.2 常用聚合操作符

```javascript
// $match：过滤文档
db.users.aggregate([
    { $match: { age: { $gte: 25 } } }
]);

// $group：分组
db.users.aggregate([
    {
        $group: {
            _id: "$age",              // 按年龄分组
            count: { $sum: 1 },       // 计数
            avgAge: { $avg: "$age" }  // 平均值
        }
    }
]);

// 统计每个部门的员工
db.users.aggregate([
    {
        $group: {
            _id: "$department",
            count: { $sum: 1 },
            avgSalary: { $avg: "$salary" },
            totalSalary: { $sum: "$salary" },
            minSalary: { $min: "$salary" },
            maxSalary: { $max: "$salary" }
        }
    }
]);

// $project：投影（选择字段）
db.users.aggregate([
    {
        $project: {
            name: 1,
            age: 1,
            _id: 0,                    // 不显示 _id
            ageCategory: {
                $cond: [
                    { $lt: ["$age", 25] },
                    "young",
                    { $cond: [{ $lt: ["$age", 40] }, "middle", "old"] }
                ]
            }
        }
    }
]);

// $sort：排序
db.users.aggregate([
    { $sort: { age: -1, name: 1 } }    // age 降序，name 升序
]);

// $limit 和 $skip
db.users.aggregate([
    { $skip: 10 },
    { $limit: 10 }
]);

// $unwind：展开数组
db.users.aggregate([
    { $unwind: "$tags" }
]);

// 统计每个 tag 的出现次数
db.users.aggregate([
    { $unwind: "$tags" },
    {
        $group: {
            _id: "$tags",
            count: { $sum: 1 }
        }
    },
    { $sort: { count: -1 } }
]);

// $lookup：关联查询（相当于 JOIN）
db.orders.aggregate([
    {
        $lookup: {
            from: "users",           // 要关联的集合
            localField: "userId",    // 当前集合的字段
            foreignField: "_id",     // 目标集合的字段
            as: "userInfo"           // 结果字段名
        }
    }
]);

// 复杂聚合示例
db.orders.aggregate([
    // 1. 关联用户
    {
        $lookup: {
            from: "users",
            localField: "userId",
            foreignField: "_id",
            as: "userInfo"
        }
    },
    // 2. 展开用户信息
    { $unwind: "$userInfo" },
    // 3. 关联产品
    {
        $lookup: {
            from: "products",
            localField: "productId",
            foreignField: "_id",
            as: "productInfo"
        }
    },
    // 4. 展开产品信息
    { $unwind: "$productInfo" },
    // 5. 计算总金额
    {
        $project: {
            orderId: "$_id",
            orderDate: "$createdAt",
            userName: "$userInfo.name",
            productName: "$productInfo.name",
            quantity: 1,
            amount: "$productInfo.price"
        }
    },
    // 6. 分组统计
    {
        $group: {
            _id: "$userName",
            orderCount: { $sum: 1 },
            totalAmount: { $sum: "$amount" }
        }
    },
    // 7. 排序
    { $sort: { totalAmount: -1 } }
]);
```

---

## 五、索引

### 5.1 创建索引

```javascript
// 创建单字段索引
db.users.createIndex({ name: 1 });       // 升序
db.users.createIndex({ age: -1 });       // 降序

// 创建复合索引
db.users.createIndex({ name: 1, age: 1 });

// 创建唯一索引
db.users.createIndex({ email: 1 }, { unique: true });

// 创建稀疏索引（只索引存在的字段）
db.users.createIndex({ phone: 1 }, { sparse: true });

// 创建 TTL 索引（自动过期）
db.sessions.createIndex({ createdAt: 1 }, { expireAfterSeconds: 3600 });

// 查看索引
db.users.getIndexes();

// 删除索引
db.users.dropIndex("name_1");
db.users.dropIndex({ name: 1 });  // 也可以直接指定键
db.users.dropIndexes();  // 删除所有索引（保留 _id）
```

---

### 5.2 索引类型

```javascript
// 文本索引（全文搜索）
db.articles.createIndex({ title: "text", content: "text" });

// 全文搜索
db.articles.find({
    $text: { $search: "MongoDB 教程" }
});

// 地理位置索引
db.places.createIndex({ location: "2dsphere" });

// 地理位置查询
db.places.find({
    location: {
        $nearSphere: {
            $geometry: {
                type: "Point",
                coordinates: [116.404, 39.915]  // [经度, 纬度]
            },
            $maxDistance: 1000  // 1000米内
        }
    }
});

// 地理位置范围查询
db.places.find({
    location: {
        $geoWithin: {
            $geometry: {
                type: "Polygon",
                coordinates: [
                    [ [0,0], [0,10], [10,10], [10,0], [0,0] ]  // 多边形坐标
                ]
            }
        }
    }
});
```

---

### 5.3 查看执行计划

```javascript
// 查看查询计划
db.users.find({ age: 25 }).explain();

// 详细执行计划
db.users.find({ age: 25 }).explain("executionStats");

// 关键指标
// winningPlan: 使用的执行计划
// stage: 执行阶段（COLLSCAN、IXSCAN）
// executionTimeMillis: 执行时间
// totalDocsExamined: 扫描的文档数
// indexUsed: 使用的索引
```

---

## 六、事务

### 6.1 多文档事务（MongoDB 4.0+）

```javascript
// 开启会话
const session = db.getMongo().startSession();

try {
    // 开启事务
    session.startTransaction();

    // 执行操作
    db.accounts.updateOne(
        { _id: 1 },
        { $inc: { balance: -100 } },
        { session }
    );

    db.accounts.updateOne(
        { _id: 2 },
        { $inc: { balance: 100 } },
        { session }
    );

    // 提交事务
    session.commitTransaction();
    print("事务成功");
} catch (error) {
    // 回滚事务
    session.abortTransaction();
    print("事务失败: " + error);
} finally {
    // 结束会话
    session.endSession();
}
```

---

### 6.2 注意事项

- 事务需要在副本集或分片集群上使用
- 事务会锁定文档，影响性能
- 事务有超时限制（默认60秒）
- 事务大小有限制（16MB）

---

## 七、备份与恢复

### 7.1 使用 mongodump

```bash
# 备份整个数据库
mongodump --db mydb --out /backup/

# 备份指定集合
mongodump --db mydb --collection users --out /backup/

# 备份到压缩文件
mongodump --db mydb --archive=/backup/mydb.gz --gzip

# 远程备份
mongodump --host mongodb.example.com --port 27017 --db mydb --out /backup/
```

---

### 7.2 使用 mongorestore

```bash
# 恢复整个数据库
mongorestore --db mydb /backup/mydb/

# 恢复指定集合
mongorestore --db mydb --collection users /backup/mydb/users.bson

# 从压缩文件恢复
mongorestore --archive=/backup/mydb.gz --gzip

# 远程恢复
mongorestore --host mongodb.example.com --port 27017 --db mydb /backup/mydb/
```

---

## 八、常用 Shell 命令

```javascript
// 查看数据库状态
db.stats();

// 查看集合状态
db.users.stats();

// 查看集合大小
db.users.dataSize();
db.users.totalSize();

// 查看索引大小
db.users.totalIndexSize();

// 分析查询性能
db.users.find({ age: 25 }).explain("executionStats");

// 重建索引
db.users.reIndex();

// 验证集合
db.users.validate();

// 获取集合信息
db.users.getCollectionInfos();

// 重命名集合
db.users.renameCollection("people");

// 计算集合中文档数
db.users.countDocuments();
db.users.estimatedDocumentCount();  // 估算值，更快
```

---

## 九、本节面试考点

| 考点 | 答案要点 |
|------|----------|
| MongoDB 特点 | 文档型、灵活Schema、水平扩展 |
| 核心概念对应 | Database、Collection、Document、Field |
| _id 类型 | 默认 ObjectId，可自定义 |
| CRUD 操作 | insertOne、find、updateOne、deleteOne |
| 查询操作符 | $gt、$lt、$in、$or、$and、$regex |
| 数组查询 | $all、$size、$elemMatch |
| 聚合管道 | $match、$group、$project、$lookup |
| $lookup | 类似 JOIN，关联集合 |
| 索引类型 | 单字段、复合、唯一、稀疏、TTL |
| 全文索引 | text 索引，$text、$search |
| 地理索引 | 2dsphere，$nearSphere |
| 事务 | MongoDB 4.0+，多文档事务 |
| 备份工具 | mongodump、mongorestore |
| BSON vs JSON | BSON 二进制，支持更多类型 |

---

## 课后练习

1. 创建一个用户集合，包含姓名、年龄、邮箱、标签、地址
2. 插入10条测试数据
3. 查询年龄在25-30之间的用户
4. 使用聚合管道统计每个标签的用户数
5. 为邮箱字段创建唯一索引

---

## 📝 自测题

1. MongoDB 中存储数据的基本单位是？\
   A. 表  B. 集合  C. 文档  D. 行
2. MongoDB 中类似 SQL JOIN 的操作是？\
   A. $join  B. $lookup  C. $merge  D. $connect
3. MongoDB 默认主键 `_id` 的类型是？\
   A. INT  B. UUID  C. ObjectId  D. STRING
4. MongoDB 4.0+ 支持多文档事务，说法正确的是？\
   A. 完全不支持事务  B. 仅支持单文档事务  C. 支持多文档 ACID 事务  D. 事务性能优于 MySQL

**答案：1-C, 2-B, 3-C, 4-C**

---

下一课：面试高频考点汇总（→ `10-面试高频考点.md`）
6. 实现一个转账事务