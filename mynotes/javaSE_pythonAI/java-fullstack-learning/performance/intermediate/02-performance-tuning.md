# 性能调优实战

## 一、概述

系统性能调优方法论：从发现瓶颈到解决问题的完整流程。涵盖 JVM 调优、SQL 优化、缓存策略、异步化改造。

## 二、性能调优流程

```
发现瓶颈（监控/告警）
    → 定位问题（Profiling/线程栈/慢查询）
    → 分析根因（代码审查/数据对比）
    → 制定方案（权衡成本与效果）
    → 实施优化（小步迭代）
    → 验证效果（A/B Test / 指标对比）
```

## 三、JVM 调优

### GC 日志分析

```bash
# JVM 参数
-Xms4g -Xmx4g
-XX:+UseG1GC
-XX:MaxGCPauseMillis=200
-verbose:gc -Xloggc:/data/logs/gc.log
-XX:+PrintGCDetails
-XX:+PrintGCDateStamps
-XX:+UseGCLogFileRotation
-XX:NumberOfGCLogFiles=10
-XX:GCLogFileSize=100M

# GC 日志分析命令
grep "Full GC" gc.log | head -20
grep "GC pause" gc.log | awk '{print $NF}' | sort -n | tail -5
```

### G1 调优

```bash
# G1 关键参数
-XX:+UseG1GC
-XX:MaxGCPauseMillis=200          # 目标暂停时间
-XX:G1HeapRegionSize=4m           # Region 大小（1-32MB）
-XX:InitiatingHeapOccupancyPercent=45  # 触发并发标记的堆占用
-XX:G1ReservePercent=10           # 预留空间
-XX:+ParallelRefProcEnabled       # 并行处理引用
-XX:-ResizePLAB                   # 禁用 PLAB 大小调整
-XX:+UnlockExperimentalVMOptions
-XX:G1MixedGCLiveThresholdPercent=85  # 混合回收存活阈值

# 大对象阈值
-XX:+PrintAdaptiveSizePolicy
-XX:G1HeapWastePercent=5
```

### 内存泄漏排查

```java
// 1. 开启 Heap Dump
// -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/data/dumps/
// 2. 使用 MAT 分析
//   - Dominator Tree 查看大对象
//   - Leak Suspects 自动分析泄漏点
//   - OQL 查询特定对象

// 3. 常见泄漏场景
public class LeakExample {
    // ❌ 静态集合导致类加载器无法回收
    private static final List<byte[]> cache = new ArrayList<>();

    public void leak() {
        cache.add(new byte[1024 * 1024]);  // 不断增长
    }

    // ✅ 使用 WeakHashMap 或设置最大容量
    private static final Map<String, byte[]> safeCache =
        new WeakHashMap<>();
}
```

## 四、数据库优化

### 慢 SQL 优化

```sql
-- 慢查询日志配置
SET long_query_time = 0.1;     -- 慢查询阈值 100ms
SET slow_query_log = ON;
SET slow_query_log_file = '/data/mysql/slow.log';

-- 分析慢查询
EXPLAIN ANALYZE
SELECT u.name, COUNT(o.id) as order_count
FROM user u
LEFT JOIN order o ON u.id = o.user_id
WHERE u.created_at > '2024-01-01'
GROUP BY u.id
ORDER BY order_count DESC
LIMIT 100;

-- 优化方案
-- 1. 为 WHERE 和 JOIN 字段建索引
ALTER TABLE user ADD INDEX idx_created_at(created_at);
ALTER TABLE order ADD INDEX idx_user_id(user_id);

-- 2. 覆盖索引避免回表
ALTER TABLE user ADD INDEX idx_created_at_name(created_at, name, id);

-- 3. 大分页优化
-- 原查询（深度分页）
SELECT * FROM order LIMIT 1000000, 20;
-- 优化后（子查询 + 索引覆盖）
SELECT * FROM order 
WHERE id > (SELECT id FROM order ORDER BY id LIMIT 1000000, 1)
LIMIT 20;
```

### 数据库连接池调优

```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      connection-timeout: 3000
      idle-timeout: 600000
      max-lifetime: 1800000
      connection-test-query: SELECT 1
      validation-timeout: 1000
```

## 五、缓存优化

### 缓存策略选择

```java
@Service
public class CacheStrategyService {
    // 多级缓存
    @Autowired
    private CacheManager caffeineCache;  // 本地缓存
    @Autowired
    private RedisTemplate<String, Object> redisCache;  // 分布式缓存

    public Object getWithMultiLevel(String key) {
        // 1. 本地缓存（毫秒级）
        Object local = caffeineCache.getCache("local").get(key);
        if (local != null) return local;

        // 2. Redis 缓存（毫秒级）
        Object redis = redisCache.opsForValue().get(key);
        if (redis != null) {
            caffeineCache.getCache("local").put(key, redis);
            return redis;
        }

        // 3. 数据库查询
        Object dbData = queryFromDB(key);
        if (dbData != null) {
            redisCache.opsForValue().set(key, dbData, 1, TimeUnit.HOURS);
            caffeineCache.getCache("local").put(key, dbData);
        }
        return dbData;
    }
}
```

## 六、异步化改造

```java
// 同步转异步
@Service
public class AsyncOrderService {
    // 耗时操作异步化
    @Async("orderExecutor")
    public void sendNotification(Long orderId) {
        // 短信、邮件、推送等
    }

    // 线程池隔离
    @Bean("orderExecutor")
    public ThreadPoolTaskExecutor orderExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(4);
        executor.setMaxPoolSize(10);
        executor.setQueueCapacity(500);
        executor.setThreadNamePrefix("order-async-");
        executor.setRejectedExecutionHandler(
            new ThreadPoolExecutor.CallerRunsPolicy());
        executor.initialize();
        return executor;
    }
}
```

## 七、优化 Checklist

- [ ] JVM 参数调优（堆大小、GC 选型）
- [ ] 数据库慢查询优化（索引、SQL 改写）
- [ ] 多级缓存策略（本地缓存 + 分布式缓存）
- [ ] 异步化改造（非核心逻辑异步执行）
- [ ] 连接池调优（数据库、HTTP、Redis）
- [ ] 批量处理（批量写入、批量查询）
- [ ] 压缩传输（Gzip、Protobuf）
- [ ] 静态资源 CDN 加速

## 课后练习

1. 对系统的 TOP 5 慢查询进行优化，对比执行计划
2. 使用 JMH 对比 synchronized、ReentrantLock、StampedLock 的性能
3. 使用 AsyncProfiler 生成本地 CPU 火焰图并分析热点
4. 模拟内存泄漏，使用 MAT 分析并修复

## 自测题

1. G1 GC 的 Region 大小范围是？ A) 1-32MB B) 1-64MB C) 512KB-16MB D) 固定 4MB
2. 深度分页优化常用的方案是？ A) JOIN B) 子查询 + 覆盖索引 C) 临时表 D) 分区表
3. 多级缓存中本地缓存的优势是？ A) 容量大 B) 访问延迟最低 C) 支持集群 D) 持久化

**答案：** 1-A, 2-B, 3-B
