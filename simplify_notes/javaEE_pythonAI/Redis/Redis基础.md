# Redis 学习笔记

## 一、Redis 概述

### 1.1 什么是 Redis

**Redis**（Remote Dictionary Server）是一个开源的内存数据结构存储系统，常用作**缓存、数据库、消息中间件**。

| 特性 | 说明 |
|------|------|
| **类型** | NoSQL（键值存储） |
| **数据存储** | 内存（为主）+ 磁盘持久化 |
| **数据模型** | Key-Value，Value 支持多种数据结构 |
| **通信协议** | RESP（REdis Serialization Protocol） |
| **单机 QPS** | ~10万+（读）/ ~8万+（写） |
| **语言** | C 语言编写 |
| **官网** | https://redis.io |

### 1.2 核心特性

- **内存存储**：数据主要在内存中，读写速度极快
- **单线程模型**：核心命令执行是单线程的，避免并发竞争
- **IO 多路复用**：使用 epoll（Linux）处理大量客户端连接
- **丰富的数据类型**：String、Hash、List、Set、ZSet、Stream 等
- **持久化**：支持 RDB（快照）和 AOF（日志）两种方式
- **高可用**：主从复制 + Sentinel 自动故障转移 + Cluster 分片集群
- **发布/订阅**：支持消息的发布订阅模式
- **Lua 脚本**：支持在服务端执行 Lua 脚本实现原子操作

### 1.3 适用场景

| 场景 | 说明 | Redis 方案 |
|------|------|-----------|
| **缓存** | 缓解数据库压力，加速访问 | SET/GET + EXPIRE 过期策略 |
| **会话共享** | 分布式系统共享用户 Session | String/Hash 存储 Session |
| **分布式锁** | 多服务互斥访问共享资源 | SETNX + Lua + Redlock |
| **计数器** | 文章阅读量、点赞数 | INCR/DECR |
| **排行榜** | 实时排名 | ZSet（有序集合） |
| **消息队列** | 异步解耦 | List（BRPOP/LPUSH）或 Stream |
| **限流** | API 限流、登录频率限制 | INCR + EXPIRE + 滑动窗口 |
| **位图计算** | 签到、活跃用户统计 | Bitmap |
| **地理位置** | 附近的人、LBS 服务 | Geospatial（GEO） |

---

## 二、桌面端 Redis 软件 / 工具

### 2.1 GUI 管理工具

| 软件 | 类型 | 平台 | 说明 |
|------|------|------|------|
| **Redis Insight** | GUI | Win/Mac/Linux | Redis 官方出品，功能最全，支持集群、Sentinel 可视化 |
| **Another Redis Desktop Manager** | GUI | Win/Mac/Linux | 第三方开源，轻量好用，连接管理方便 |
| **Medis** | GUI | Mac | macOS 专用，界面优雅 |
| **Tiny RDM** | GUI | Win/Mac/Linux | 新锐开源，颜值高性能好 |

#### Redis Insight 安装（推荐）

```
# Windows - 下载安装包
https://redis.io/insight/

# 或通过 winget 安装
winget install Redis.RedisInsight
```

#### Another Redis Desktop Manager 安装

```
# GitHub Releases 下载
https://github.com/qishibo/AnotherRedisDesktopManager/releases

# Windows 免安装版：下载 .exe 直接运行
```

### 2.2 命令行工具

| 命令 | 说明 |
|------|------|
| `redis-cli` | Redis 自带命令行客户端 |
| `redis-cli -h host -p port -a password` | 指定连接参数 |
| `redis-cli --raw` | 返回原始格式（避免中文乱码） |
| `redis-cli --bigkeys` | 扫描大 Key |
| `redis-cli --latency` | 检测延迟 |
| `redis-cli --stat` | 实时统计 |

### 2.3 Windows 安装 Redis Server

**方式一：WSL（推荐）**

```bash
# 1. 安装 WSL（管理员 PowerShell）
wsl --install

# 2. WSL 中安装 Redis
sudo apt update
sudo apt install redis-server -y
sudo systemctl start redis
redis-cli ping
> PONG
```

**方式二：Redis for Windows（非官方，社区版）**

```
# 下载 Redis-x64-xxx.msi
https://github.com/microsoftarchive/redis/releases

# 安装后作为 Windows 服务运行
```

**方式三：Docker（最推荐）**

```bash
docker run -d --name redis -p 6379:6379 redis:7-alpine
docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack-server:latest
  # 8001 是 RedisInsight Web 管理端口
```

---

## 三、生产环境 Redis 软件 / 组件

### 3.1 核心组件一览

| 组件 | 说明 | 部署方式 |
|------|------|---------|
| **Redis Server** | 核心服务，提供数据读写 | 原生 / Docker / K8s |
| **Redis Sentinel** | 高可用守护进程，监控 + 自动故障转移 | 独立进程，至少 3 节点 |
| **Redis Cluster** | 分布式集群，数据自动分片 | 原生部署，最少 6 节点（3主3从） |
| **Redis Stack** | 集成扩展模块的 Redis 发行版 | Docker / 原生安装 |
| **Redis Exporter** | Prometheus 监控指标导出 | 独立进程，旁路部署 |
| **RedisInsight Server** | Web 远程管理界面 | Docker / 原生安装 |

### 3.2 Redis Stack（扩展模块）

Redis Stack 在标准 Redis 基础上集成了以下模块：

| 模块 | 功能 |
|------|------|
| **RediSearch** | 全文搜索、二级索引、向量搜索 |
| **RedisJSON** | 原生 JSON 数据类型支持（`JSON.SET/GET`） |
| **RedisTimeSeries** | 时序数据存储与聚合查询 |
| **RedisBloom** | 布隆过滤器、Top-K、Count-Min Sketch |

```bash
# 生产推荐使用 Docker 部署 Redis Stack
docker run -d \
  --name redis-stack \
  -p 6379:6379 \
  -p 8001:8001 \
  -v /data/redis:/data \
  redis/redis-stack-server:latest
```

### 3.3 生产部署方案对比

| 方案 | 节点数 | 数据分片 | 自动故障转移 | 适用场景 |
|------|--------|---------|-------------|---------|
| **单机** | 1 | 否 | 否 | 开发测试 |
| **主从复制** | 2+ | 否 | 手动 | 读写分离 |
| **Sentinel** | 3+ | 否 | 自动 | 高可用需求 |
| **Cluster** | 6+ | 是 | 自动 | 大数据量、高吞吐 |

### 3.4 生产环境配置建议

```bash
# /etc/redis/redis.conf 关键配置

# 绑定地址（生产用内网IP）
bind 0.0.0.0

# 端口
port 6379

# 密码
requirepass your-strong-password

# 后台运行
daemonize yes

# 日志
logfile /var/log/redis/redis.log
loglevel notice

# RDB 持久化
save 900 1
save 300 10
save 60 10000

# AOF 持久化
appendonly yes
appendfsync everysec

# 内存上限（根据物理内存设置）
maxmemory 4gb

# 内存淘汰策略
maxmemory-policy allkeys-lru

# 慢查询日志（超过 10ms 记录，记录 128 条）
slowlog-log-slower-than 10000
slowlog-max-len 128
```

---

## 四、核心概念与数据类型

### 4.1 Redis 线程模型

#### 4.1.1 经典单线程模型（Redis 6.0 之前）

Redis 核心命令的执行是**单线程**的，为什么还快？

1. **完全基于内存**：数据在内存中，读写纳秒级
2. **IO 多路复用**：epoll（Linux）管理大量客户端连接，非阻塞 IO
3. **单线程避免竞争**：没有锁和上下文切换开销
4. **数据结构高效**：SDS、跳表、压缩列表等精心设计

> ⚠️ **注意**：单线程是指命令执行是单线程，但持久化（bgsave、AOF rewrite）、异步删除（unlink）等由子进程或后台线程完成。

#### 4.1.2 Redis 6.0/7.0 多线程 IO 模型

| 版本 | 变化 |
|------|------|
| **6.0** | 引入**多线程 IO**，网络读写由多个 IO 线程处理，但命令执行仍然是单线程 |
| **7.0** | 进一步优化多线程 IO，引入 **TLS 多线程**、`FLUSHALL/FLUSHDB` 异步化等 |

**为什么引入多线程 IO**：
- 单线程模型下，网络读写（socket read/write）占了大量 CPU 时间
- 随着网络带宽提升（万兆网卡），单线程无法充分利用带宽
- 将网络 IO 分摊到多线程，命令执行仍保持单线程（避免并发问题）

**架构示意**：

```
                主线程（事件循环）
               /     |      \
         IO线程1  IO线程2  IO线程3
               \     |      /
            客户端连接（网络读写）
```

- 主线程负责 accept 新连接、命令解析和执行
- IO 线程负责从 socket 读取数据和写回响应（默认 3 个 IO 线程）

```redis
# redis.conf 配置
io-threads 4            # 主线程 + 3 个 IO 线程（默认 4）
io-threads-do-reads yes # IO 线程也负责读取（默认 no，只负责写）
```

> **面试重点**：记住"**IO 多线程 + 命令执行单线程**"这个设计——既提升了 IO 吞吐，又避免了多线程并发复杂度和死锁风险。

### 4.2 数据库与 Key 命名

- Redis 默认有 **16 个数据库**（0-15），通过 `SELECT index` 切换
- 生产环境通常**只用 db0**，不同业务通过 Key 前缀隔离

```
# Key 命名规范（推荐用冒号分隔）
业务名:对象名:ID:属性

# 示例
user:1001:name
user:1001:email
article:42:title
order:20260501:count
```

### 4.3 五种基本数据类型

#### String（字符串）

| 底层结构 | SDS（Simple Dynamic String） |
|----------|---------------------------|
| 最大长度 | 512 MB |
| 适用场景 | 缓存、计数器、分布式锁、Session 共享 |

```redis
SET key value              # 设置键值
SET key value NX           # 键不存在才设置（SETNX）
SET key value XX           # 键存在才设置
SET key value EX 10        # 设置过期时间（秒）
GET key                    # 获取值
MGET key1 key2             # 批量获取
INCR key                   # +1（可用于计数器）
INCRBY key 100             # +100
DECR key                   # -1
GETSET key new_value       # 获取旧值并设置新值
STRLEN key                 # 字符串长度
APPEND key value           # 追加
```

#### Hash（哈希）

| 底层结构 | dict（哈希表）或 ziplist（压缩列表） |
|----------|-----------------------------------|
| 适用场景 | 对象存储、用户信息、购物车 |

```redis
HSET user:1001 name "张三" age 25 city "北京"   # 设置多个字段
HGET user:1001 name                              # 获取单个字段
HMGET user:1001 name age                         # 获取多个字段
HGETALL user:1001                                # 获取所有字段和值
HKEYS user:1001                                  # 获取所有字段名
HVALS user:1001                                  # 获取所有值
HDEL user:1001 age                               # 删除字段
HEXISTS user:1001 name                           # 判断字段是否存在
HLEN user:1001                                   # 字段数量
HINCRBY user:1001 age 1                          # 字段值自增
```

#### List（列表）

| 底层结构 | quicklist（3.2+，是 ziplist 和 linkedlist 的结合） |
|----------|-----------------------------------------------|
| 适用场景 | 消息队列、时间线、最新文章 |

```redis
LPUSH list_key item1 item2      # 左侧插入
RPUSH list_key item1 item2      # 右侧插入
LPOP list_key                   # 左侧弹出
RPOP list_key                   # 右侧弹出
LLEN list_key                   # 列表长度
LRANGE list_key 0 -1            # 获取全部元素
LINDEX list_key 0               # 获取指定索引元素
LTRIM list_key 0 99             # 截断列表（只保留前100个）

# 阻塞操作（常用于消息队列）
BLPOP queue timeout             # 阻塞式左侧弹出，timeout=0 表示永远等待
BRPOP queue timeout             # 阻塞式右侧弹出
```

#### Set（集合）

| 底层结构 | intset（整数集合）或 dict（哈希表） |
|----------|----------------------------------|
| 适用场景 | 去重、标签、共同好友、随机抽奖 |

```redis
SADD set_key member1 member2    # 添加元素
SMEMBERS set_key                # 获取所有元素
SCARD set_key                   # 元素数量
SISMEMBER set_key member        # 判断是否存在
SREM set_key member             # 删除元素
SPOP set_key count              # 随机弹出（抽奖）
SRANDMEMBER set_key count       # 随机获取（不删除）

# 集合运算
SINTER set1 set2                # 交集（共同好友）
SUNION set1 set2                # 并集
SDIFF set1 set2                 # 差集
SINTERSTORE dest set1 set2      # 交集结果存入 dest
```

#### ZSet（有序集合）

| 底层结构 | skiplist（跳表）+ dict（哈希表） |
|----------|-----------------------------|
| 适用场景 | 排行榜、延迟队列、限流 |

```redis
ZADD zset_key score member       # 添加元素
ZRANGE zset_key 0 -1             # 按分数升序获取
ZREVRANGE zset_key 0 -1          # 按分数降序获取（排行榜）
ZRANGEBYSCORE zset_key min max   # 按分数范围获取
ZRANK zset_key member            # 获取排名（升序）
ZREVRANK zset_key member         # 获取排名（降序）
ZSCORE zset_key member           # 获取分数
ZCARD zset_key                   # 元素数量
ZREM zset_key member             # 删除元素
ZINCRBY zset_key 1 member        # 增加分数
ZCOUNT zset_key min max          # 统计分数区间内元素数

# 带分页的排行榜
ZREVRANGE ranking 0 9 WITHSCORES   # 第1-10名及分数
ZREVRANGE ranking 10 19 WITHSCORES # 第11-20名
```

### 4.4 扩展数据类型

| 类型 | 用途 | 典型命令 |
|------|------|---------|
| **HyperLogLog** | 基数统计（UV、独立访客），占用 12KB 固定内存 | `PFADD/PFCOUNT/PFMERGE` |
| **Bitmap** | 位图，签到、设备状态、布隆过滤 | `SETBIT/GETBIT/BITCOUNT/BITOP` |
| **Geospatial** | 地理位置，附近的人、距离计算 | `GEOADD/GEORADIUS/GEODIST/GEOPOS` |
| **Stream**（5.0+） | 消息队列，支持消费组、消息持久化 | `XADD/XREAD/XREADGROUP/XDEL` |

```redis
# HyperLogLog（UV 统计）
PFADD uv:20260501 user1 user2 user3
PFCOUNT uv:20260501

# Bitmap（签到）
SETBIT sign:1001:202605 1 1    # 第1天签到
BITCOUNT sign:1001:202605     # 当月签到天数

# Geospatial
GEOADD locations 116.397 39.908 "天安门"
GEORADIUS locations 116.4 39.9 10 km    # 附近10公里

# Stream（消息队列）
XADD mystream * name "Alice" msg "hello"   # 生产消息
XREAD COUNT 10 BLOCK 0 STREAMS mystream $   # 消费消息
XGROUP CREATE mystream mygroup $            # 创建消费组
XREADGROUP GROUP mygroup consumer1 COUNT 1 STREAMS mystream >   # 消费组读取
```

### 4.5 底层数据结构详解

> 大厂面试高频：面试官通常不满足于知道"ZSet 用跳表实现"，而是要你讲清楚跳表是怎么查的、层高怎么生成、和平衡树比有什么优劣。

#### SDS（Simple Dynamic String）

String 类型的底层实现，取代 C 原生字符串。

| 对比维度 | C 字符串 | SDS |
|---------|---------|-----|
| **长度获取** | O(n)，遍历到 `\0` | O(1)，结构体存 len |
| **二进制安全** | 否（`\0` 截断） | 是 |
| **缓冲区溢出** | 会 | 不会（自动扩容） |
| **内存重分配** | 每次修改都要 | 预分配 + 惰性释放 |

```c
// SDS 结构（简化）
struct sdshdr {
    int len;      // 已用长度
    int free;     // 剩余空间
    char buf[];   // 字节数组
};
```

**空间预分配策略**：
- 修改后 `len < 1MB`：预分配 `len` 同样大小的 `free`（即翻倍）
- 修改后 `len >= 1MB`：预分配 `1MB` 的 `free`

#### dict（哈希表 / 字典）

Hash 类型和全局键空间的底层实现。

**渐进式 rehash**（重点）：

```
rehash 过程：
  dict.h[0]（旧表）→ dict.h[1]（新表，大小为 2 倍）

  不是一次性迁移，而是分多次：
  1. 为 h[1] 分配空间
  2. 设置 rehashidx = 0（标记正在 rehash）
  3. 每次增删改查时，顺便迁移 h[0] 一个 bucket 到 h[1]
  4. 迁移完 h[1] 变为 h[0]，释放旧表
```

**rehash 触发条件**：
- 负载因子 = `used / size`
- 扩容：负载因子 > 1（或 > 5 正在 BGSAVE）
- 缩容：负载因子 < 0.1

> **rehash 期间的操作规则**：新增只写入 h[1]，查改删先在 h[0] 查，没找到再去 h[1]。

#### ziplist（压缩列表）

Hash 和 ZSet 在元素较少时的底层编码，**内存连续**，节省空间。

```
ziplist 内存布局：
[zlbytes][zltail][zllen][entry1][entry2]...[entryN][zlend]

每个 entry 结构：
[prevlen][encoding][data]
  prevlen: 前一个 entry 的长度（用于反向遍历）
  encoding: 编码类型（整型/字符串、长度）
  data: 实际数据
```

**连锁更新问题**：当插入/删除一个 entry 导致后续 entry 的 `prevlen` 增大（1 字节 → 5 字节），可能引发多米诺骨牌效应。**这是 ziplist 的缺陷**，也是 Redis 7.0 引入 listpack 替代 ziplist 的原因之一。

#### quicklist（快速列表）

List 类型的底层实现（3.2+），是 **ziplist + 双向链表** 的结合体。

```
quicklist:
  [node1] <-> [node2] <-> [node3]
    ↓           ↓           ↓
  ziplist     ziplist     ziplist
```

- 每个节点是一个 ziplist，存储多个元素
- 通过控制 `list-max-ziplist-size` 平衡内存和性能
- 两端操作快（直接操作头尾节点）
- 相对于纯链表，减少了指针开销，内存更紧凑

#### skiplist（跳表）

ZSet 的有序部分实现，支持 O(log N) 的查找、插入、删除。

```
skiplist 结构示意（层高4）：

level 3:  head ------------------------------> tail
level 2:  head ------> node2 ----------------> tail
level 1:  head ------> node2 ------> node3 --> tail
level 0:  head -> n1 -> node2 -> n3 -> node3 -> tail
```

**核心机制**：
- **层高**：每个节点层高随机生成（1~32），幂次分布（P=0.25）。平均每个节点 1.33 层
- **查询过程**：从最高层开始向右走，遇到尾部或大于目标则降一层继续
- **为什么用跳表不用平衡树**：跳表实现简单，范围查询方便（ZRANGE），调整结构只需修改指针

**跳表 vs 平衡树 vs B+ 树**：

| 维度 | 跳表 | 平衡树 | B+ 树 |
|------|------|--------|-------|
| 实现复杂度 | 低 | 高 | 高 |
| 范围查询 | O(log N + M) | O(log N + M) 需中序遍历 | O(log N + M) 链表 |
| 内存占用 | 稍高（冗余指针） | 低 | 中 |
| 并发控制 | 容易 | 复杂 | 复杂 |
| 适用 | 内存场景 | 文件系统 | 磁盘数据库 |

#### intset（整数集合）

Set 类型当所有元素都是整数时的底层编码。

```c
struct intset {
    uint32_t encoding;  // 编码方式（16/32/64 位）
    uint32_t length;    // 元素个数
    int8_t contents[];  // 整数数组（有序排列）
};
```

**升级机制**：当插入一个更大范围的整数（如 32 位 → 64 位），整个集合会升级编码。**升级是单向的，不能降级**。

---

## 五、常用命令分类

### 5.1 通用命令

```redis
KEYS pattern         # 查找键（生产禁用，会阻塞！用 SCAN 替代）
SCAN cursor          # 渐进式遍历缓存
TYPE key             # 返回数据类型
EXISTS key           # 键是否存在
DEL key1 key2        # 删除键
UNLINK key           # 异步删除（非阻塞）
EXPIRE key seconds   # 设置过期时间
TTL key              # 查看剩余过期时间（秒）
PTTL key             # 查看剩余过期时间（毫秒）
PERSIST key          # 移除过期时间
RENAME key newkey    # 重命名
RANDOMKEY            # 随机返回一个键
DBSIZE               # 当前数据库键数量
FLUSHDB              # 清空当前数据库
FLUSHALL             # 清空所有数据库
```

### 5.2 发布订阅

```redis
# 订阅者
SUBSCRIBE channel1 channel2        # 订阅一个或多个频道
PSUBSCRIBE news:*                  # 按模式订阅（通配符）

# 发布者
PUBLISH channel1 "hello"           # 向频道发送消息

# 管理
PUBSUB CHANNELS                    # 查看活跃频道
PUBSUB NUMSUB channel1             # 查看频道订阅者数量
```

### 5.3 事务

```redis
# 基本事务
MULTI                              # 开启事务
SET key1 value1                    # 命令入队
SET key2 value2
EXEC                               # 执行事务
DISCARD                            # 取消事务

# 乐观锁（CAS）
WATCH key1                         # 监视 key1
MULTI
SET key1 new_value
EXEC                               # 如果 key1 被其他客户端修改，执行返回 nil
```

> **注意**：Redis 事务保证隔离性和原子性（所有命令顺序执行），但不支持回滚——如果队列中有命令语法错误，事务会拒绝执行；如果运行时错误（如类型不匹配），正确命令仍会执行。

### 5.4 Pipeline（管道）

Pipeline 将多个命令一次性发送到服务端，减少网络往返（RTT），**不是事务**（不保证原子性）。

```java
// Java Jedis Pipeline
Pipeline pipeline = jedis.pipelined();
pipeline.set("key1", "value1");
pipeline.set("key2", "value2");
pipeline.incr("counter");
pipeline.sync();
```

```python
# Python redis-py Pipeline
pipe = r.pipeline()
pipe.set('key1', 'value1')
pipe.set('key2', 'value2')
pipe.incr('counter')
pipe.execute()
```

---

## 六、持久化

### 6.1 RDB（快照持久化）

RDB 将内存数据生成**二进制快照**保存到磁盘。

| 项目 | 说明 |
|------|------|
| **触发方式** | 手动 `SAVE`（阻塞） / `BGSAVE`（后台） / 自动配置 |
| **文件** | `dump.rdb` |
| **优点** | 文件紧凑，恢复快，适合备份 |
| **缺点** | 可能丢失最后一次快照后的数据 |

```redis
# 自动触发配置（ save <秒内> <变更次数> ）
save 900 1          # 900秒（15分钟）内至少1次变更
save 300 10         # 300秒（5分钟）内至少10次变更
save 60 10000       # 60秒内至少10000次变更
```

**BGSAVE 流程**：
1. 父进程 fork 子进程
2. 子进程将数据写入临时 RDB 文件
3. 写入完毕后替换旧 RDB 文件
4. 子进程退出

### 6.2 AOF（追加日志）

AOF 以**日志追加**的方式记录每条写命令。

| 项目 | 说明 |
|------|------|
| **触发方式** | 每次写入、每秒、由操作系统决定 |
| **文件** | `appendonly.aof` |
| **优点** | 数据完整性高，最多丢失 1 秒数据 |
| **缺点** | 文件体积大，恢复速度比 RDB 慢 |

```redis
# 配置
appendonly yes
appendfilename "appendonly.aof"

# 刷盘策略
appendfsync always      # 每次写入都 fsync（最安全，最慢）
appendfsync everysec    # 每秒 fsync（推荐）
appendfsync no          # 由操作系统决定（最快，最不安全）
```

**AOF 重写（BGREWRITEAOF）**：合并冗余命令，压缩 AOF 文件体积

### 6.3 RDB vs AOF 对比

| 对比维度 | RDB | AOF |
|---------|-----|-----|
| 恢复速度 | 快 | 慢 |
| 数据安全 | 可能丢数据 | everysec 最多丢 1s |
| 文件大小 | 小（压缩二进制） | 大（文本命令） |
| 对性能影响 | fork 子进程，大实例可能卡顿 | everysec 影响极小 |
| 适用场景 | 备份、灾难恢复 | 数据完整要求高 |

> **生产建议**：两者同时开启 —— RDB 用于快速恢复和备份，AOF 用于保障数据安全。

### 6.4 混合持久化（Redis 4.0+）

将 RDB 和 AOF 结合起来：AOF 重写时，先将当前内存数据以 RDB 格式写入 AOF 文件，再追加增量命令。

```redis
# 开启混合持久化
aof-use-rdb-preamble yes
```

**AOF 文件结构**：
```
[AOF 文件]
[RDB 数据（全量快照）] [增量命令日志（AOF 格式）]
```

**优势**：
- 重启恢复速度接近 RDB（加载 RDB 部分即可）
- 数据安全性接近 AOF（增量命令不会丢）
- 文件体积比纯 AOF 小

> **生产推荐**：Redis 4.0+ 建议开启混合持久化，兼具 RDB 恢复快和 AOF 数据安全双重优势。

---

## 七、过期策略与内存淘汰

### 7.1 过期策略

Redis 使用 **定期删除 + 惰性删除** 组合策略：

| 策略 | 工作机制 |
|------|---------|
| **定期删除** | 每秒 10 次随机抽样 20 个过期 key，删除其中过期的，如果过期比例 >25% 则重复 |
| **惰性删除** | 访问 key 时检查是否过期，过期则删除 |

> 为什么不用定时删除？每创建一个 key 就开定时器，CPU 开销过高。

### 7.2 内存淘汰策略

当内存达到 `maxmemory` 上限时，Redis 根据配置策略淘汰 key：

| 策略 | 说明 |
|------|------|
| `noeviction` | 不淘汰，写入返回错误（**默认**） |
| `allkeys-lru` | 淘汰最近最少使用的 key（**最常用**） |
| `allkeys-lfu` | 淘汰最不经常使用的 key（4.0+） |
| `volatile-lru` | 从设置了过期时间的 key 中淘汰最近最少使用的 |
| `volatile-lfu` | 从设置了过期时间的 key 中淘汰最不经常使用的 |
| `volatile-ttl` | 从设置了过期时间的 key 中淘汰即将过期的 |
| `volatile-random` | 从设置了过期时间的 key 中随机淘汰 |
| `allkeys-random` | 随机淘汰 |

```redis
# 配置推荐（生产通用场景）
maxmemory 4gb
maxmemory-policy allkeys-lru
```

---

## 八、高可用方案

### 8.1 主从复制

主节点（master）写入，从节点（replica）只读并同步数据。

```bash
# 从节点配置
replicaof master-ip 6379
replica-read-only yes
```

#### 同步流程（psync2，Redis 2.8 / 4.0）

**两个核心标识**：
- **replication ID（replid）**：主节点的唯一标识，从节点同步后继承 replid
- **offset**：复制偏移量，记录从节点已同步到主节点数据的哪个位置

**首次同步——全量同步**：
1. 从节点发送 `PSYNC ? -1`（表示不知道 replid 和 offset）
2. 主节点返回 `+FULLRESYNC <replid> <offset>`
3. 主节点执行 `BGSAVE` 生成 RDB
4. 同时将新写入命令缓冲在 **replication backlog**（环形缓冲区，默认 1MB）
5. RDB 生成完毕，发送给从节点
6. 从节点清空自身数据，加载 RDB
7. 主节点将 backlog 中的增量命令发给从节点

**断线重连——部分同步（增量同步）**：
1. 从节点发送 `PSYNC <replid> <offset>`（带上之前同步的 replid 和 offset）
2. 主节点检查 `replid` 是否匹配、`offset` 是否仍在 backlog 中
3. ✅ 匹配 → 执行**部分同步**，只发送 backlog 中的缺失数据
4. ❌ 不匹配 → 执行**全量同步**

**psync2 改进（Redis 4.0）**：
- 主从切换后，新主节点继承旧主节点的 replid
- 从节点重启后仍能触发部分同步（避免重复全量同步）

#### 主从复制常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| **复制延迟** | 网络带宽不足、主节点写入量大 | 读写分离只读从库，或升级带宽 |
| **数据不一致** | 异步复制，主从存在短暂延迟 | 用 `WAIT` 命令等待从节点确认（会阻塞） |
| **主节点宕机** | 单点故障 | 搭配 Sentinel 自动故障转移 |

### 8.2 Sentinel（哨兵）

Sentinel 是一个独立进程，监控 Redis 主从状态，自动执行故障转移。

| 功能 | 说明 |
|------|------|
| **监控** | 定期 PING 检查主从节点健康状态 |
| **通知** | 节点故障时通知管理员或其他程序 |
| **自动故障转移** | 主节点宕机时，选举一个从节点提升为主 |
| **配置提供** | 客户端通过 Sentinel 获取当前主节点地址 |

```bash
# sentinel.conf 配置
sentinel monitor mymaster 127.0.0.1 6379 2   # 2 为 quorum（判定主节点故障的投票数）
sentinel down-after-milliseconds mymaster 5000
sentinel failover-timeout mymaster 60000
sentinel parallel-syncs mymaster 1

# 启动 Sentinel
redis-sentinel /path/to/sentinel.conf
```

#### 故障转移流程

1. **主观下线**：单个 Sentinel 发现主节点 PING 超时（`down-after-milliseconds`）
2. **客观下线**：该 Sentinel 向其他 Sentinel 询问，收到 ≥quorum 个确认后标记为主观下线
3. **Leader 选举**：Sentinel 之间通过 **Raft 算法** 选举一个 Leader 执行故障转移
4. **选新主节点**：从从节点中选一个（优先级高 → 复制偏移量大 → runid 小）
5. **切换主节点**：Leader 向选中的从节点发送 `SLAVEOF NO ONE`，使其成为新主节点
6. **通知客户端**：Sentinel 通知客户端新主节点地址

#### 脑裂问题

**场景**：主节点实际存活但 Sentinel 误判，选举了新主节点。旧主节点恢复后继续写入，导致数据不一致。

**解决方案**（redis.conf）：

```redis
# 最少从节点数量（主节点写入前检查至少有 N 个从节点连接）
min-replicas-to-write 1
# 从节点最大延迟（秒）
min-replicas-max-lag 10
```

配合这两个配置：主节点检测不到足够从节点时拒绝写入，避免脑裂期间写入的数据丢失。

> **生产建议**：部署 3 个或 5 个 Sentinel 节点（奇数），quorum 设为 N/2+1。

### 8.3 Cluster（集群）

Redis Cluster 将数据自动分片到多个节点，提供线性扩展能力。

| 特性 | 说明 |
|------|------|
| **数据分片** | 16384 个 hash slot，通过 CRC16(key) % 16384 分配 |
| **节点通信** | Gossip 协议，节点间互相交换状态 |
| **高可用** | 每个主节点可以有多个从节点，主节点宕机时从节点自动晋升 |
| **最小节点** | 至少 3 个主节点 |
| **客户端** | 需要支持 Cluster 的客户端（JedisCluster、lettuce） |

```bash
# 创建集群（6 个节点：3主3从）
redis-cli --cluster create \
  192.168.1.1:6379 192.168.1.2:6379 192.168.1.3:6379 \
  192.168.1.4:6379 192.168.1.5:6379 192.168.1.6:6379 \
  --cluster-replicas 1
```

#### Cluster 重定向机制

##### MOVED 重定向

客户端请求的 key 不在当前节点时，返回 `MOVED` 错误和目标节点地址：

```redis
# 客户端连接到节点A，但 key 在节点B
> GET mykey
-MOVED 1234 192.168.1.2:6379
# 客户端需要重发请求到 192.168.1.2:6379
```

- Smart 客户端（如 JedisCluster、lettuce）会缓存 slot→节点映射表，直接跳转，不经过重定向
- `MOVED` 是**永久的**——slot 已经迁移到目标节点，下次直接发过去

##### ASK 重定向（迁移中）

当 Cluster 正在做 **resharding**（slot 迁移）时：

```redis
> GET mykey
-ASK 1234 192.168.1.2:6379   # slot 1234 正在迁移中
```

- 客户端先发 `ASKING` 命令到目标节点（临时授权），再发请求
- `ASK` 是**临时的**——slot 迁移完成后，后续请求变为 `MOVED`

##### 对比

| 重定向 | 含义 | 客户端缓存 | 场景 |
|--------|------|-----------|------|
| **MOVED** | slot 已迁移到其他节点 | 更新本地 slot 映射 | slot 迁移完成 |
| **ASK** | slot 正在迁移，仅当前请求去目标节点 | 不更新映射 | resharding 进行中 |

```bash
# 集群管理命令
CLUSTER INFO                    # 集群状态
CLUSTER NODES                   # 节点列表
CLUSTER KEYSLOT key             # 查看 key 的 slot
CLUSTER COUNTKEYSINSLOT slot    # 查看 slot 中 key 数

# 重新分片
redis-cli --cluster reshard 192.168.1.1:6379
```

### 8.4 方案选型对比

| 维度 | 主从复制 | Sentinel | Cluster |
|------|---------|----------|---------|
| 部署复杂度 | 低 | 中 | 高 |
| 自动故障转移 | 否 | 是 | 是 |
| 数据分片 | 否 | 否 | 是 |
| 在线扩缩容 | 否 | 否 | 是 |
| 总数据量 | <内存上限 | <内存上限 | TB 级 |
| 客户端支持 | 标准 | 标准 | 需 Cluster 兼容 |
| 适用规模 | 单机数 GB | 单机数十 GB | 多机数百 GB+ |

---

## 九、生产最佳实践

### 9.1 Big Key（大键）危害与处理

**Big Key** 是指单个键包含大量数据，如大 String（>10MB）、大 Hash/Set/ZSet（>5000 元素）。

**危害**：
- 删除慢：`DEL` 大 key 会阻塞 Redis 数十秒
- 迁移慢：Cluster 中迁移大 key 耗时极长
- 内存不均：Cluster 中某些节点内存暴涨

```bash
# 扫描 big key
redis-cli --bigkeys
```

**处理方案**：
- 拆分：大 Hash 拆分成多个小 Hash（分段存储）
- 异步删除：用 `UNLINK` 替代 `DEL`
- 分批操作：`SSCAN`/`HSCAN`/`ZSCAN` 分批遍历

### 9.2 缓存一致性（数据库与 Redis 双写一致性）

> 大厂面试必问：更新数据库后，是先更新缓存还是先删缓存？

| 策略 | 操作顺序 | 问题 | 推荐？ |
|------|---------|------|--------|
| **先更新缓存，再写 DB** | 更新 Redis → 更新 MySQL | Redis 成功但 MySQL 失败，数据不一致 | ❌ |
| **先写 DB，再更新缓存** | 更新 MySQL → 更新 Redis | 并发写导致缓存和 DB 不一致 | ❌ |
| **先删缓存，再写 DB** | 删除 Redis → 更新 MySQL | 删除缓存后、写 DB 前有并发读，读到旧数据缓存 | ⚠️ |
| **先写 DB，再删缓存**（Cache Aside） | 更新 MySQL → 删除 Redis | 删除可能失败，需要兜底 | ✅ **推荐** |

**推荐方案：Cache Aside Pattern + 延迟双删**

```
更新流程：
  1. 更新 MySQL
  2. 删除 Redis 缓存
  3. （延迟几百毫秒）再次删除 Redis 缓存 → 解决并发读请求写入旧数据的问题
```

**兜底方案**：
- 设置缓存过期时间（最终一致性兜底）
- 异步队列重试删除失败的操作
- 监听 MySQL binlog（Canal）同步触发缓存更新

### 9.3 缓存穿透 / 击穿 / 雪崩

| 问题 | 描述 | 解决方法 |
|------|------|---------|
| **穿透** | 查不到的数据（如 ID=-1），每次直接打到 DB | 布隆过滤器（Bloom Filter） / 缓存空值 |
| **击穿** | 热点 key 过期瞬间，高并发打到 DB | 互斥锁 / 热点 key 永不过期 + 异步更新 |
| **雪崩** | 大量 key 同时过期，或 Redis 宕机 | 过期时间加随机值 / 多级缓存 / 限流降级 |

```redis
# 缓存穿透：缓存空值（较简单方案）
SET user:notexist "null" EX 60
```

```java
// 缓存击穿：互斥锁（Java 示例）
public String getData(String key) {
    String value = redis.get(key);
    if (value != null) return value;

    // 分布式锁
    if (redis.setnx("lock:" + key, "1", 10)) {
        value = db.query(key);
        redis.set(key, value, 3600);
        redis.del("lock:" + key);
    } else {
        Thread.sleep(100);
        return redis.get(key);  // 重试
    }
    return value;
}
```

### 9.4 热点 Key 问题

**热点 Key** 是指被大量并发请求同时访问的 key（如双十一大促的爆款商品、微博热搜）。

**危害**：
- 单个 Redis 节点 CPU 飙高，响应变慢
- 网卡带宽打满，影响其他业务
- 流量打到后端数据库（如果缓存过期）

**解决方案**：

| 方案 | 原理 | 适用场景 |
|------|------|---------|
| **本地缓存 + Redis** | 热点数据在 JVM/进程内也缓存一份（Caffeine） | 读多，可接受短暂不一致 |
| **热点 Key 副本** | 将热点 key 复制 N 份（如 `key_1` ~ `key_N`），分散到不同节点 | 读多写少 |
| **读写分离** | 从节点分担读流量 | 集群部署时 |
| **限流熔断** | 对热点 key 的访问做限流，保护 Redis 和后端 | 所有场景兜底 |

```java
// 热点 key 副本策略（读请求随机选一个副本）
String hotKey = "product:123";
int replicaCount = 10;
int index = ThreadLocalRandom.current().nextInt(replicaCount);
String replicaKey = hotKey + "_" + index;
String value = redis.get(replicaKey);
// 写入时需要写所有副本
```

### 9.5 内存优化

```redis
# 配置优化
hash-max-ziplist-entries 512    # Hash 压缩列表编码阈值
hash-max-ziplist-value 64       # 字段值超过此值用 dict 编码
set-max-intset-entries 512      # Set 整数集合编码阈值
zset-max-ziplist-entries 128    # ZSet 压缩列表编码阈值
zset-max-ziplist-value 64

# 内存统计
INFO memory                     # 查看内存使用详情
MEMORY USAGE key                # 查看单个 key 内存占用
MEMORY STATS                    # 内存统计报告
MEMORY PURGE                    # 尝试释放内存碎片
```

### 9.6 安全配置

```redis
# /etc/redis/redis.conf

# 密码认证
requirepass 强密码

# 危险命令重命名或禁用
rename-command FLUSHALL ""
rename-command FLUSHDB ""
rename-command CONFIG "ADMIN_CONFIG"
rename-command KEYS "ADMIN_KEYS"

# 绑定内网 IP（不暴露到公网）
bind 内网IP

# 禁用外部访问（仅本地）
protected-mode yes
```

### 9.7 慢查询与延迟

```redis
# 配置慢查询
slowlog-log-slower-than 10000    # 超过 10ms 的记录（微秒单位）
slowlog-max-len 128              # 最多保留 128 条

# 查看慢查询
SLOWLOG GET 10                   # 获取最近 10 条慢查询
SLOWLOG LEN                      # 慢查询总数
SLOWLOG RESET                    # 清空慢查询
```

**常见延迟原因**：
- `KEYS *`、`SMEMBERS`、`HGETALL` 等全量遍历命令
- `DEL` 大 key（用 `UNLINK` 替代）
- AOF 配置 `always` 刷盘
- fork 子进程（大实例持久化时，4GB 实例 fork 耗时 ~ms 级）
- 内存碎片（`MEMORY PURGE`）
- 操作系统内存 Swap（禁用！）

### 9.8 Redis 变慢排查思路

```
现象：业务发现 Redis 响应变慢（P99 延迟升高）

排查步骤：

1. 确认网络
   ping 检查延迟，排除网络抖动
   redis-cli --latency -h host -p port   # 检测网络延迟

2. 检查慢查询
   SLOWLOG GET 50                        # 查看最近慢命令

3. 检查 big key
   redis-cli --bigkeys
   MEMORY USAGE key                      # 逐个排查可疑 key

4. 检查 CPU
   INFO CPU                              # 看 used_cpu_sys 是否过高
   top 查看 redis-server 进程 CPU 是否跑满

5. 检查内存
   INFO memory
  关注：used_memory_rss / used_memory ≈ 1.5+ 说明内存碎片严重

6. 检查持久化影响
   INFO persistence                      # 看 rdb_last_bgsave_status、aof_last_rewrite_status
  查看最近是否有 fork（latest_fork_usec）

7. 检查连接数
   INFO clients                          # connected_clients 是否过高
   CLIENT LIST                           # 查看客户端连接详情

8. 操作系统层面
   free -h                               # 检查是否使用了 Swap
   /proc/redis_pid/smaps | grep Swap     # 查看 Redis 进程是否有换页
```

### 9.9 Redlock 分布式锁原理

> 大厂面试高频：Redis 单机锁和 Redlock 各有什么问题？为什么很多场景不用 Redlock？

**单机锁的问题**（SETNX on a single master）：
- 主节点写入锁成功，但还没同步到从节点就宕机
- 从节点晋升为主，锁信息丢失
- 另一个客户端可以获取同一把锁 → **锁失效**

**Redlock 算法**（Redis 官方分布式锁算法）：

```
前提：部署 N 个独立的 Redis 节点（通常 N=5，完全独立，不是 Cluster）

加锁流程：
  1. 获取当前时间（毫秒）
  2. 依次向 N 个节点发送 SET key value NX PX 10000（锁超时 10s）
  3. 计算获取锁消耗的时间（当前时间 - 步骤1时间）
  4. 成功获取锁的条件：
     - 从超过半数节点（N/2+1）获取到锁
     - 总耗时 < 锁超时时间
  5. 满足条件 → 锁获取成功
  6. 不满足条件 → 向所有节点发送解锁请求
```

**Redlock 存在的问题（争论）**：

| 问题 | 说明 |
|------|------|
| **性能开销** | 需要和 5 个节点交互，延迟较高 |
| **时钟漂移** | 依赖服务器时间，时钟跳跃可能导致锁失效 |
| **复杂性** | 部署 5 个独立节点增加运维成本 |
| **必要性争议** | 很多场景单机锁 + 适度降级已足够 |

> **业界共识**：Redlock 适用于对锁可靠性要求极高的场景（如金融交易）。大多数业务场景用单机 SETNX + 主从同步 + 降级兜底即可。Martin Kleppmann 和 Antirez（Redis 作者）曾为此有过著名辩论。

```java
// 单机锁（大多数场景推荐，足够使用）
// 加锁
String result = jedis.set("lock:order", "value", SetParams.setParams().nx().ex(10));
// 解锁（Lua 保证原子性）
String script = "if redis.call('get',KEYS[1])==ARGV[1] then return redis.call('del',KEYS[1]) else return 0 end";
jedis.eval(script, Collections.singletonList("lock:order"), Collections.singletonList(value));
```

---

## 十、客户端使用

### 10.1 Java 客户端

#### Jedis（最经典）

```xml
<dependency>
    <groupId>redis.clients</groupId>
    <artifactId>jedis</artifactId>
    <version>5.2.0</version>
</dependency>
```

```java
// Jedis 基础使用
JedisPool pool = new JedisPool("localhost", 6379);
try (Jedis jedis = pool.getResource()) {
    jedis.auth("password");

    // String
    jedis.set("key", "value");
    String value = jedis.get("key");

    // Hash
    jedis.hset("user:1", "name", "张三");
    Map<String, String> user = jedis.hgetAll("user:1");

    // 过期时间
    jedis.setex("session:token", 3600, "user_data");

    // 分布式锁
    String lockKey = "lock:order:123";
    String lockValue = UUID.randomUUID().toString();
    String result = jedis.set(lockKey, lockValue, SetParams.setParams().nx().ex(10));
    if ("OK".equals(result)) {
        // 执行业务逻辑
        // 释放锁（Lua 脚本保证原子性）
        String luaScript = "if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('del', KEYS[1]) else return 0 end";
        jedis.eval(luaScript, Collections.singletonList(lockKey), Collections.singletonList(lockValue));
    }
}
pool.close();
```

#### Lettuce（响应式，Spring Boot 默认）

```xml
<dependency>
    <groupId>io.lettuce</groupId>
    <artifactId>lettuce-core</artifactId>
    <version>6.4.0</version>
</dependency>
```

```java
// Lettuce 基础使用
RedisClient client = RedisClient.create("redis://password@localhost:6379");
StatefulRedisConnection<String, String> conn = client.connect();
RedisCommands<String, String> cmd = conn.sync();

cmd.set("key", "value");
String value = cmd.get("key");

conn.close();
client.close();
```

#### Spring Data Redis

```yaml
# application.yml
spring:
  data:
    redis:
      host: localhost
      port: 6379
      password: password
      lettuce:
        pool:
          max-active: 16
          max-idle: 8
          min-idle: 4
```

```java
@Autowired
private StringRedisTemplate redisTemplate;

// String
redisTemplate.opsForValue().set("key", "value", 1, TimeUnit.HOURS);
String value = redisTemplate.opsForValue().get("key");

// Hash
redisTemplate.opsForHash().put("user:1", "name", "张三");
String name = (String) redisTemplate.opsForHash().get("user:1", "name");

// List
redisTemplate.opsForList().rightPush("queue", "task1");

// Set
redisTemplate.opsForSet().add("tags", "java", "redis");

// ZSet
redisTemplate.opsForZSet().add("ranking", "user1", 100);

// 过期时间
redisTemplate.expire("key", 30, TimeUnit.MINUTES);

// 分布式锁（Spring Data Redis 自带）
RedisLock lock = new RedisLock(redisTemplate, "lock:order:123", Duration.ofSeconds(10));
if (lock.tryLock()) {
    try {
        // 执行业务
    } finally {
        lock.unlock();
    }
}
```

### 10.2 Python 客户端

```bash
pip install redis
```

```python
import redis

# 连接 Redis
r = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    password='your-password',
    decode_responses=True,    # 自动解码为字符串
)

# 验证连接
try:
    r.ping()
    print("Redis 连接成功!")
except redis.ConnectionError:
    print("Redis 连接失败!")

# String
r.set('key', 'value', ex=3600)    # ex=过期秒数
val = r.get('key')
r.incr('counter')                   # +1
r.incrby('counter', 10)            # +10

# Hash
r.hset('user:1', mapping={'name': '张三', 'age': 25})
user = r.hgetall('user:1')

# List
r.lpush('queue', 'task1', 'task2')
task = r.brpop('queue', timeout=0)   # 阻塞式获取

# Set
r.sadd('tags', 'java', 'redis', 'python')
members = r.smembers('tags')

# ZSet
r.zadd('ranking', {'user1': 100, 'user2': 85})
top10 = r.zrevrange('ranking', 0, 9, withscores=True)

# Pipeline
pipe = r.pipeline()
pipe.set('key1', 'val1')
pipe.set('key2', 'val2')
pipe.incr('counter')
pipe.execute()
```

---

## 附：Redis 学习路线图

```
初学者 → 数据类型 + 常用命令（熟悉 String/Hash/List/Set/ZSet）
  ↓
进阶   → 持久化(RDB/AOF) + 过期策略 + 事务
  ↓
高级   → 主从复制 + Sentinel + Cluster 高可用集群
  ↓
生产   → 监控 + 安全 + 性能优化 + 分布式锁 + 缓存策略
  ↓
扩展   → Redis Stack(Search/JSON/TimeSeries) + Stream 消息队列
```
