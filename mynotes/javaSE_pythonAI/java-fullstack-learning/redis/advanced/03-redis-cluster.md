# Redis 集群与运维

## 一、概述

Redis 生产级部署方案：主从复制、Sentinel 高可用、Cluster 集群、持久化策略、缓存淘汰、大 key 治理。

## 二、主从复制

### 复制原理

```
Master                  Slave
  │                        │
  │──── PSYNC ────────────▶│
  │◀── FULLRESYNC ────────│
  │──── RDB + buffer ─────▶│  全量同步
  │                        │
  │──── 增量 replication ──▶│  增量同步
  │    (命令传播)           │
```

### 配置

```bash
# slave 配置
replicaof 192.168.1.1 6379
replica-read-only yes
replica-priority 100
min-replicas-to-write 1    # 至少一个从节点在线才可写
min-replicas-max-lag 10    # 从节点延迟不超过 10s

# master 配置
masterauth yourpassword
repl-backlog-size 64mb     # 复制积压缓冲区
repl-backlog-ttl 3600
```

### 读写分离

```java
@Configuration
public class RedisReadWriteConfig {
    @Bean
    public RedisTemplate<String, Object> redisTemplate() {
        // 使用 Lettuce 的读写分离
        LettuceClientConfiguration config = LettuceClientConfiguration.builder()
            .readFrom(ReadFrom.REPLICA_PREFERRED)  // 优先读从节点
            .build();
        LettuceConnectionFactory factory = new LettuceConnectionFactory(
            new RedisStandaloneConfiguration("master", 6379), config);
        // ...
    }
}
```

## 三、Sentinel 高可用

### 架构

```
┌──────────┐    ┌──────────┐    ┌──────────┐
│ Sentinel1 │    │ Sentinel2 │    │ Sentinel3 │
└─────┬────┘    └─────┬────┘    └─────┬────┘
      │               │               │
      └───────────────┼───────────────┘
                      │
             ┌────────▼────────┐
             │   Redis 节点     │
             │ Master: 6379    │
             │ Slave1: 6380    │
             │ Slave2: 6381    │
             └─────────────────┘
```

### Sentinel 配置

```properties
# sentinel.conf
port 26379
sentinel monitor mymaster 192.168.1.1 6379 2
sentinel down-after-milliseconds mymaster 5000
sentinel failover-timeout mymaster 60000
sentinel parallel-syncs mymaster 1
sentinel auth-pass mymaster yourpassword
```

### Java 集成

```java
@Bean
public RedisConnectionFactory sentinelConnectionFactory() {
    RedisSentinelConfiguration sentinelConfig = new RedisSentinelConfiguration()
        .master("mymaster")
        .sentinel("192.168.1.1", 26379)
        .sentinel("192.168.1.2", 26379)
        .sentinel("192.168.1.3", 26379);
    sentinelConfig.setPassword("yourpassword");
    
    return new LettuceConnectionFactory(sentinelConfig);
}
```

## 四、Cluster 集群

### 集群架构

```
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│ Node 1   │  │ Node 2   │  │ Node 3   │  │ Node 4   │  │ Node 5   │  │ Node 6   │
│ 7000     │  │ 7001     │  │ 7002     │  │ 7003     │  │ 7004     │  │ 7005     │
│ Slot     │  │ Slot     │  │ Slot     │  │ Slot     │  │ Slot     │  │ Slot     │
│ 0-5460   │  │ 5461-10922│  │10923-16383│  │(replica) │  │(replica) │  │(replica) │
└────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
     │              │              │              │              │              │
     └──────────────┴──────────────┴──────────────┴──────────────┴──────────────┘
                          Gossip 通信
```

```bash
# 创建集群
redis-cli --cluster create \
    192.168.1.1:7000 192.168.1.1:7001 192.168.1.1:7002 \
    192.168.1.2:7003 192.168.1.2:7004 192.168.1.2:7005 \
    --cluster-replicas 1

# 集群管理
redis-cli --cluster check 192.168.1.1:7000
redis-cli --cluster rebalance 192.168.1.1:7000
redis-cli --cluster add-node new:7006 existing:7000 --cluster-slave
```

### 集群客户端

```java
@Bean
public RedisConnectionFactory clusterConnectionFactory() {
    RedisClusterConfiguration clusterConfig = new RedisClusterConfiguration()
        .clusterNode("192.168.1.1", 7000)
        .clusterNode("192.168.1.1", 7001)
        .clusterNode("192.168.1.2", 7003);
    clusterConfig.setMaxRedirects(3)
        .setPassword("yourpassword");
    
    return new LettuceConnectionFactory(clusterConfig);
}

// 集群环境下使用 hash tags 确保相关 key 在同一 slot
// user:{123}:profile
// user:{123}:orders
```

## 五、持久化策略

### RDB vs AOF

| 特性 | RDB | AOF |
|------|-----|-----|
| 文件格式 | 二进制快照 | 协议追加 |
| 恢复速度 | 快 | 慢 |
| 数据安全性 | 可能丢失最后一次备份后的数据 | 最多丢失 1s 数据 |
| 文件大小 | 小 | 大（需 rewrite） |
| 对性能影响 | fork 子进程，大实例有延迟 | 写时追加，影响较小 |

### 混合持久化 (Redis 4.0+)

```bash
# 推荐配置：AOF + RDB 混合
appendonly yes
appendfsync everysec
aof-use-rdb-preamble yes   # AOF 文件头部用 RDB 格式
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
```

## 六、缓存淘汰策略

```bash
# 配置
maxmemory 4gb
maxmemory-policy allkeys-lru
```

| 策略 | 说明 | 适用场景 |
|------|------|----------|
| allkeys-lru | 淘汰最近最少使用的 key | 通用缓存 |
| allkeys-lfu | 淘汰最不经常使用的 key | 访问频率差异大的场景 |
| volatile-lru | 仅淘汰设置了 TTL 的 key | 混合存储 |
| volatile-ttl | 淘汰 TTL 最小的 key | 时效性数据 |
| noeviction | 不淘汰，写操作报错 | 禁止丢失数据的场景 |

## 七、大 Key 治理

### 大 Key 发现问题

```bash
# 扫描大 key
redis-cli --bigkeys -i 0.1

# 手动分析
redis-cli MEMORY USAGE key_name
redis-cli DEBUG OBJECT key_name

# 内存分析工具
redis-rdb-tools
```

### 大 Key 处理方案

```java
// 大 String：拆分为小 key
// ❌ 一个 key 存 10MB JSON
// ✅ 按业务拆分
redisTemplate.opsForValue().set("user:1001:profile", profileJson);
redisTemplate.opsForValue().set("user:1001:orders", ordersJson);

// 大 Hash：分批读取
public Map<String, String> scanHash(String key, int count) {
    Map<String, String> result = new HashMap<>();
    Cursor<Map.Entry<String, String>> cursor = redisTemplate.opsForHash()
        .scan(key, ScanOptions.scanOptions().count(count).build());
    while (cursor.hasNext()) {
        Map.Entry<String, String> entry = cursor.next();
        result.put(entry.getKey(), entry.getValue());
    }
    return result;
}

// 大 List：限定长度
redisTemplate.opsForList().trim("logs", 0, 999);  // 保留最近 1000 条
```

## 面试考点

1. **Redis Cluster 的哈希槽数量？** 16384 个，通过 CRC16(key) % 16384 计算槽位
2. **缓存穿透、击穿、雪崩的区别与解决方案？** 穿透（布隆过滤器）、击穿（互斥锁）、雪崩（过期时间加随机值）
3. **Redis 集群为什么是 16384 个槽？** 心跳包大小控制、槽位信息可压缩
4. **AOF rewrite 会阻塞吗？** fork 子进程处理，但 fork 本身在主线程会短暂阻塞

## 课后练习

1. 搭建 3 主 3 从的 Redis Cluster 集群
2. 使用 Redis Sentinel 实现 Java 客户端自动故障转移
3. 实现大 Key 自动发现和拆分机制
4. 压测对比 RDB 和 AOF 的恢复时间和数据安全性

## 自测题

1. Redis Sentinel 的选举仲裁数是什么？ A) 所有 sentinel 节点 B) quorum 配置值 C) 所有数据节点 D) 客户端
2. Redis Cluster 中 MOVED 重定向的含义？ A) 节点故障 B) 槽位迁移到其他节点 C) 主从切换 D) 集群分裂
3. 以下哪个不是 Redis 的持久化方式？ A) RDB B) AOF C) RDB+AOF 混合 D) Binlog

**答案：** 1-B, 2-B, 3-D
