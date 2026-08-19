# Redis 高级应用

## 一、概述

深入 Redis 高级特性：分布式锁、限流器、延迟队列、布隆过滤器、Lua 脚本、Redis 事务、管道技术。

## 二、分布式锁

### Redis 分布式锁演进

```java
// V1: SETNX + expire（❌ 非原子）
public boolean lockV1(String key, String value, long ttl) {
    Long result = jedis.setnx(key, value);
    if (result == 1) {
        jedis.expire(key, (int) ttl);
        return true;
    }
    return false;
    // 问题：setnx 和 expire 非原子，宕机导致死锁
}

// V2: SET NX EX（✅ 原子）
public boolean lockV2(String key, String value, long ttl) {
    String result = jedis.set(key, value, SetParams.setParams().nx().ex(ttl));
    return "OK".equals(result);
}

// V3: Redisson（✅ 生产级）
@Service
public class RedisLockService {
    @Autowired
    private RedissonClient redisson;

    public void processWithLock(String orderId) {
        RLock lock = redisson.getLock("lock:order:" + orderId);
        try {
            // 看门狗机制：默认 30s，自动续期
            if (lock.tryLock(5, 30, TimeUnit.SECONDS)) {
                processOrder(orderId);
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } finally {
            // 释放锁
            if (lock.isHeldByCurrentThread()) {
                lock.unlock();
            }
        }
    }
}

// V4: Redlock（多节点容错）
public boolean redlock(String resource, String value, long ttl) {
    int successCount = 0;
    long start = System.currentTimeMillis();
    
    for (RedisClient client : redisNodes) {
        try {
            String result = client.set(resource, value,
                SetParams.setParams().nx().ex(ttl / redisNodes.length));
            if ("OK".equals(result)) successCount++;
        } catch (Exception e) {
            // 忽略
        }
    }
    // 超过半数 + 总耗时 < TTL
    long cost = System.currentTimeMillis() - start;
    return successCount >= redisNodes.length / 2 + 1 && cost < ttl;
}
```

## 三、限流器

### 滑动窗口限流

```java
@Component
public class SlidingWindowRateLimiter {
    @Autowired
    private StringRedisTemplate redisTemplate;

    public boolean tryAcquire(String key, int maxCount, long windowSeconds) {
        String windowKey = "ratelimit:" + key;
        long now = System.currentTimeMillis();
        long windowStart = now - windowSeconds * 1000;
        
        // Lua 脚本实现原子操作
        String script = """
            redis.call('ZREMRANGEBYSCORE', KEYS[1], 0, ARGV[1])
            local count = redis.call('ZCARD', KEYS[1])
            if count < tonumber(ARGV[2]) then
                redis.call('ZADD', KEYS[1], ARGV[3], ARGV[3])
                redis.call('EXPIRE', KEYS[1], ARGV[4])
                return 1
            end
            return 0
            """;
        
        Long result = redisTemplate.execute(
            new DefaultRedisScript<>(script, Long.class),
            List.of(windowKey),
            String.valueOf(windowStart),      // ARGV[1]: 窗口起始
            String.valueOf(maxCount),          // ARGV[2]: 最大阈值
            String.valueOf(now),               // ARGV[3]: 当前时间戳
            String.valueOf(windowSeconds)      // ARGV[4]: TTL
        );
        return result != null && result == 1;
    }
}

// 令牌桶限流
@Component
public class TokenBucketRateLimiter {
    private final RedisTemplate<String, String> redisTemplate;
    private static final String BUCKET_KEY = "token_bucket:";
    private static final String SCRIPT = """
        local key = KEYS[1]
        local rate = tonumber(ARGV[1])       -- 速率（每秒）
        local capacity = tonumber(ARGV[2])    -- 桶容量
        local now = tonumber(ARGV[3])
        local requested = tonumber(ARGV[4])
        
        local last = redis.call('HGETALL', key)
        local lastTokens = capacity
        local lastRefreshed = now
        
        if #last > 0 then
            lastTokens = tonumber(last[2])
            lastRefreshed = tonumber(last[4])
        end
        
        local delta = math.max(0, now - lastRefreshed)
        local tokens = math.min(capacity, lastTokens + delta * rate)
        
        if tokens >= requested then
            redis.call('HSET', key, 'tokens', tokens - requested, 'timestamp', now)
            redis.call('EXPIRE', key, 5)
            return 1
        end
        return 0
        """;
}
```

## 四、延迟队列

```java
@Component
public class RedisDelayQueue {
    @Autowired
    private StringRedisTemplate redisTemplate;

    // 添加延迟任务
    public void add(String queue, String task, long delayMs) {
        long executeTime = System.currentTimeMillis() + delayMs;
        redisTemplate.opsForZSet().add("delay:" + queue, task, executeTime);
    }

    // 消费延迟任务
    @Scheduled(fixedDelay = 1000)
    public void consume() {
        long now = System.currentTimeMillis();
        // 获取到期的任务（score <= now）
        Set<String> tasks = redisTemplate.opsForZSet()
            .rangeByScore("delay:order_cancel", 0, now, 0, 100);
        if (tasks == null || tasks.isEmpty()) return;

        for (String task : tasks) {
            // 原子移除并处理
            Long removed = redisTemplate.opsForZSet()
                .remove("delay:order_cancel", task);
            if (removed != null && removed > 0) {
                processTask(task);
            }
        }
    }

    private void processTask(String task) {
        // 取消超时未支付订单
        String orderId = task.split(":")[1];
        orderService.cancelOrder(orderId);
    }
}
```

## 五、布隆过滤器

```java
@Component
public class BloomFilterService {
    @Autowired
    private RedissonClient redisson;

    // 防止缓存穿透
    public RBloomFilter<String> createUserBloomFilter() {
        RBloomFilter<String> filter = redisson.getBloomFilter("bloom:users");
        filter.tryInit(1000000L, 0.01);  // 100万数据，1%误判率
        
        return filter;
    }

    // 使用布隆过滤器判断用户是否存在（一定不存在，可能存在）
    public boolean mightContain(String username) {
        RBloomFilter<String> filter = redisson.getBloomFilter("bloom:users");
        if (!filter.contains(username)) {
            return false;  // 一定不存在
        }
        // 可能存在，查缓存或数据库
        return true;
    }
}
```

## 六、管道与批量操作

```java
@Component
public class RedisBatchService {
    @Autowired
    private RedisTemplate<String, String> redisTemplate;

    // Pipeline 批量写入
    public void batchWrite(Map<String, String> data) {
        redisTemplate.executePipelined((RedisCallback<Object>) connection -> {
            data.forEach((key, value) -> {
                byte[] rawKey = redisTemplate.getStringSerializer().serialize(key);
                byte[] rawValue = redisTemplate.getStringSerializer().serialize(value);
                connection.set(rawKey, rawValue);
            });
            return null;
        });
    }

    // Pipeline 批量读取
    public List<String> batchRead(List<String> keys) {
        List<Object> results = redisTemplate.executePipelined(
            (RedisCallback<String>) connection -> {
                keys.forEach(key -> {
                    byte[] rawKey = redisTemplate.getStringSerializer().serialize(key);
                    connection.get(rawKey);
                });
                return null;
            }
        );
        return results.stream()
            .map(r -> r instanceof String ? (String) r : null)
            .collect(Collectors.toList());
    }
}
```

## 课后练习

1. 实现基于 Redisson 的公平锁，支持排队等待
2. 使用 ZSet 实现一个简单排行榜（按分数排序，分页查询）
3. 实现布隆过滤器 + 缓存双检防止缓存穿透
4. 用 Lua 脚本实现原子性的库存扣减操作

## 自测题

1. Redisson 看门狗续期默认时间？ A) 10s B) 30s C) 60s D) 永不超时
2. 布隆过滤器的特点是？ A) 精确判断存在 B) 精确判断不存在 C) 不存在误判 D) 支持删除
3. Redis Pipeline 的主要优势？ A) 减少网络往返 B) 原子性 C) 持久化 D) 主从同步

**答案：** 1-B, 2-B, 3-A
