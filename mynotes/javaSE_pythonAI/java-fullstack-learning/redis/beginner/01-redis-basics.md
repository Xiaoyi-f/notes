# Redis 缓存技术

## 一、Redis 概述

Redis（Remote Dictionary Server）是一个开源的内存数据结构存储，可以用作数据库、缓存和消息中间件。

### Redis 数据结构

```
String（字符串）      - 最基本的数据类型
Hash（哈希）         - 键值对集合
List（列表）         - 有序集合，可重复
Set（集合）          - 无序集合，不重复
ZSet（有序集合）     - 带分数的集合
Bitmap（位图）        - 位操作
HyperLogLog         - 基数统计
Geo                 - 地理位置
Stream              - 流数据
```

## 二、Spring Data Redis

### 1. 基础配置

```xml
<!-- 依赖 -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>

<!-- Lettuce 连接池 -->
<dependency>
    <groupId>org.apache.commons</groupId>
    <artifactId>commons-pool2</artifactId>
</dependency>

<!-- Redisson 分布式锁 -->
<dependency>
    <groupId>org.redisson</groupId>
    <artifactId>redisson-spring-boot-starter</artifactId>
    <version>3.24.3</version>
</dependency>
```

```yaml
# application.yml
spring:
  data:
    redis:
      host: localhost
      port: 6379
      password:
      database: 0
      timeout: 5000ms
      lettuce:
        pool:
          max-active: 20
          max-idle: 10
          min-idle: 5
          max-wait: 1000ms

# Redisson 配置
spring:
  redis:
    redisson:
      file: classpath:redisson.yaml
      config: |
        singleServerConfig:
          address: redis://localhost:6379
          database: 0
          password: null
          connectionPoolSize: 20
          connectionMinimumIdleSize: 5
          idleConnectionTimeout: 10000
          connectTimeout: 10000
          timeout: 3000
          retryAttempts: 3
          retryInterval: 1500
        threads: 16
        nettyThreads: 32
```

### 2. RedisTemplate 配置

```java
@Configuration
@EnableCaching
public class RedisConfig {

    @Bean
    public RedisConnectionFactory redisConnectionFactory(RedisProperties properties) {
        LettuceConnectionFactory factory = new LettuceConnectionFactory(
            new RedisStandaloneConfiguration(
                properties.getHost(),
                properties.getPort()
            )
        );

        // 配置连接池
        LettuceClientConfiguration config = LettuceClientConfiguration.builder()
            .commandTimeout(Duration.ofMillis(properties.getTimeout().toMillis()))
            .shutdownTimeout(Duration.ZERO)
            .poolConfig(new GenericObjectPoolConfig<>() {{
                setMaxTotal(properties.getLettuce().getPool().getMaxActive());
                setMaxIdle(properties.getLettuce().getPool().getMaxIdle());
                setMinIdle(properties.getLettuce().getPool().getMinIdle());
                setMaxWaitMillis(properties.getLettuce().getPool().getMaxWait().toMillis());
            }})
            .build();

        factory.setClientConfiguration(config);
        return factory;
    }

    @Bean
    public RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory factory) {
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(factory);

        // 使用 Jackson2JsonRedisSerializer 序列化值
        Jackson2JsonRedisSerializer<Object> serializer = new Jackson2JsonRedisSerializer<>(Object.class);

        ObjectMapper mapper = new ObjectMapper();
        mapper.registerModules(new JavaTimeModule());
        mapper.disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);
        mapper.setSerializationInclusion(JsonInclude.Include.NON_NULL);
        serializer.setObjectMapper(mapper);

        // String 序列化 Key
        StringRedisSerializer stringSerializer = new StringRedisSerializer();

        template.setKeySerializer(stringSerializer);
        template.setHashKeySerializer(stringSerializer);
        template.setValueSerializer(serializer);
        template.setHashValueSerializer(serializer);

        template.afterPropertiesSet();
        return template;
    }

    @Bean
    public StringRedisTemplate stringRedisTemplate(RedisConnectionFactory factory) {
        StringRedisTemplate template = new StringRedisTemplate();
        template.setConnectionFactory(factory);
        return template;
    }

    @Bean
    public CacheManager cacheManager(RedisConnectionFactory factory) {
        RedisCacheConfiguration config = RedisCacheConfiguration.defaultCacheConfig()
            .entryTtl(Duration.ofHours(1))
            .serializeKeysWith(RedisSerializationContext.SerializationPair.fromSerializer(
                new StringRedisSerializer()))
            .serializeValuesWith(RedisSerializationContext.SerializationPair.fromSerializer(
                new Jackson2JsonRedisSerializer<>(Object.class)))
            .disableCachingNullValues();

        // 不同缓存不同的过期时间
        Map<String, RedisCacheConfiguration> cacheConfigurations = new HashMap<>();
        cacheConfigurations.put("users", config.entryTtl(Duration.ofMinutes(30)));
        cacheConfigurations.put("products", config.entryTtl(Duration.ofHours(2)));
        cacheConfigurations.put("orders", config.entryTtl(Duration.ofMinutes(10)));

        return RedisCacheManager.builder(factory)
            .cacheDefaults(config)
            .withInitialCacheConfigurations(cacheConfigurations)
            .transactionAware()
            .build();
    }
}
```

## 三、String 操作

```java
@Service
@Slf4j
public class RedisStringService {

    private final RedisTemplate<String, Object> redisTemplate;
    private final StringRedisTemplate stringRedisTemplate;

    // 设置值
    public void set(String key, String value) {
        stringRedisTemplate.opsForValue().set(key, value);
    }

    // 设置值并指定过期时间
    public void set(String key, String value, long timeout, TimeUnit unit) {
        stringRedisTemplate.opsForValue().set(key, value, timeout, unit);
    }

    // 获取值
    public String get(String key) {
        return stringRedisTemplate.opsForValue().get(key);
    }

    // 获取并设置新值（原子操作）
    public String getAndSet(String key, String value) {
        return stringRedisTemplate.opsForValue().getAndSet(key, value);
    }

    // 如果 key 不存在则设置（SETNX）
    public Boolean setIfAbsent(String key, String value) {
        return stringRedisTemplate.opsForValue().setIfAbsent(key, value);
    }

    // 如果 key 不存在则设置并指定过期时间（分布式锁的基础）
    public Boolean setIfAbsent(String key, String value, long timeout, TimeUnit unit) {
        return stringRedisTemplate.opsForValue().setIfAbsent(key, value, timeout, unit);
    }

    // 递增
    public Long increment(String key) {
        return stringRedisTemplate.opsForValue().increment(key);
    }

    // 递增指定步长
    public Long increment(String key, long delta) {
        return stringRedisTemplate.opsForValue().increment(key, delta);
    }

    // 递减
    public Long decrement(String key) {
        return stringRedisTemplate.opsForValue().decrement(key);
    }

    // 递减指定步长
    public Long decrement(String key, long delta) {
        return stringRedisTemplate.opsForValue().decrement(key, delta);
    }

    // 追加字符串
    public Integer append(String key, String value) {
        return stringRedisTemplate.opsForValue().append(key, value);
    }

    // 获取字符串长度
    public Long size(String key) {
        return stringRedisTemplate.opsForValue().size(key);
    }

    // 设置多个值（MSET）
    public void multiSet(Map<String, String> map) {
        stringRedisTemplate.opsForValue().multiSet(map);
    }

    // 获取多个值（MGET）
    public List<String> multiGet(Collection<String> keys) {
        return stringRedisTemplate.opsForValue().multiGet(keys);
    }

    // 应用示例：限流
    public boolean rateLimit(String key, long limit, long timeout, TimeUnit unit) {
        Long count = redisTemplate.opsForValue().increment(key);
        if (count == 1) {
            redisTemplate.expire(key, timeout, unit);
        }
        return count <= limit;
    }

    // 应用示例：计数器
    public long increaseCounter(String key) {
        return redisTemplate.opsForValue().increment(key);
    }

    // 应用示例：分布式 Session
    public void saveSession(String sessionId, UserSession session, long timeout) {
        String key = "session:" + sessionId;
        redisTemplate.opsForValue().set(key, session, timeout, TimeUnit.SECONDS);
    }

    public UserSession getSession(String sessionId) {
        String key = "session:" + sessionId;
        return (UserSession) redisTemplate.opsForValue().get(key);
    }
}
```

## 四、Hash 操作

```java
@Service
@Slf4j
public class RedisHashService {

    private final RedisTemplate<String, Object> redisTemplate;

    // 设置字段值
    public void hSet(String key, String field, Object value) {
        redisTemplate.opsForHash().put(key, field, value);
    }

    // 获取字段值
    public Object hGet(String key, String field) {
        return redisTemplate.opsForHash().get(key, field);
    }

    // 删除字段
    public Long hDel(String key, Object... fields) {
        return redisTemplate.opsForHash().delete(key, fields);
    }

    // 检查字段是否存在
    public Boolean hExists(String key, String field) {
        return redisTemplate.opsForHash().hasKey(key, field);
    }

    // 获取所有字段
    public Map<Object, Object> hGetAll(String key) {
        return redisTemplate.opsForHash().entries(key);
    }

    // 获取所有字段名
    public Set<Object> hKeys(String key) {
        return redisTemplate.opsForHash().keys(key);
    }

    // 获取所有值
    public List<Object> hValues(String key) {
        return redisTemplate.opsForHash().values(key);
    }

    // 递增字段值
    public Long hIncrBy(String key, String field, long delta) {
        return redisTemplate.opsForHash().increment(key, field, delta);
    }

    // 应用示例：用户信息缓存
    public void cacheUserInfo(Long userId, UserInfo userInfo) {
        String key = "user:" + userId;
        hSet(key, "id", userInfo.getId());
        hSet(key, "username", userInfo.getUsername());
        hSet(key, "email", userInfo.getEmail());
        hSet(key, "avatar", userInfo.getAvatar());
        redisTemplate.expire(key, 1, TimeUnit.HOURS);
    }

    // 应用示例：购物车
    public void addToCart(String userId, Long productId, int quantity) {
        String key = "cart:" + userId;
        hIncrBy(key, productId.toString(), quantity);
        redisTemplate.expire(key, 7, TimeUnit.DAYS);
    }

    // 应用示例：商品库存
    public boolean deductStock(Long productId, int quantity) {
        String key = "stock:" + productId;
        Long stock = (Long) hGet(key, "quantity");

        if (stock == null || stock < quantity) {
            return false;
        }

        hIncrBy(key, "quantity", -quantity);
        hIncrBy(key, "sales", quantity);
        return true;
    }
}
```

## 五、List 操作

```java
@Service
@Slf4j
public class RedisListService {

    private final RedisTemplate<String, Object> redisTemplate;

    // 左侧添加（LPUSH）
    public Long leftPush(String key, Object value) {
        return redisTemplate.opsForList().leftPush(key, value);
    }

    // 右侧添加（RPUSH）
    public Long rightPush(String key, Object value) {
        return redisTemplate.opsForList().rightPush(key, value);
    }

    // 左侧弹出（LPOP）
    public Object leftPop(String key) {
        return redisTemplate.opsForList().leftPop(key);
    }

    // 右侧弹出（RPOP）
    public Object rightPop(String key) {
        return redisTemplate.opsForList().rightPop(key);
    }

    // 获取列表长度
    public Long size(String key) {
        return redisTemplate.opsForList().size(key);
    }

    // 获取列表元素（范围）
    public List<Object> range(String key, long start, long end) {
        return redisTemplate.opsForList().range(key, start, end);
    }

    // 获取所有元素
    public List<Object> all(String key) {
        return range(key, 0, -1);
    }

    // 索引获取元素
    public Object index(String key, long index) {
        return redisTemplate.opsForList().index(key, index);
    }

    // 设置指定位置的值
    public void set(String key, long index, Object value) {
        redisTemplate.opsForList().set(key, index, value);
    }

    // 移除指定值的元素
    public Long remove(String key, long count, Object value) {
        return redisTemplate.opsForList().remove(key, count, value);
    }

    // 裁剪列表
    public void trim(String key, long start, long end) {
        redisTemplate.opsForList().trim(key, start, end);
    }

    // 应用示例：消息队列
    public void pushMessage(String queue, Message message) {
        rightPush("queue:" + queue, message);
    }

    public Message popMessage(String queue) {
        return (Message) leftPop("queue:" + queue);
    }

    // 阻塞获取消息
    public Message blockingPop(String queue, long timeout, TimeUnit unit) {
        return (Message) redisTemplate.opsForList().leftPop("queue:" + queue, timeout, unit);
    }

    // 应用示例：排行榜（最新排行）
    public void addToRanking(String ranking, Long userId, String username) {
        rightPush("ranking:" + ranking, Map.of("userId", userId, "username", username));

        // 保持只有前100名
        trim("ranking:" + ranking, -100, -1);
    }

    public List<Map<String, Object>> getRanking(String ranking) {
        List<Object> list = all("ranking:" + ranking);
        // 反转列表，最新的在前
        Collections.reverse(list);

        return list.stream()
            .map(obj -> (Map<String, Object>) obj)
            .collect(Collectors.toList());
    }
}
```

## 六、Set 操作

```java
@Service
@Slf4j
public class RedisSetService {

    private final RedisTemplate<String, Object> redisTemplate;

    // 添加元素
    public Long add(String key, Object... values) {
        return redisTemplate.opsForSet().add(key, values);
    }

    // 获取所有元素
    public Set<Object> members(String key) {
        return redisTemplate.opsForSet().members(key);
    }

    // 移除元素
    public Long remove(String key, Object... values) {
        return redisTemplate.opsForSet().remove(key, values);
    }

    // 判断元素是否存在
    public Boolean isMember(String key, Object value) {
        return redisTemplate.opsForSet().isMember(key, value);
    }

    // 获取集合大小
    public Long size(String key) {
        return redisTemplate.opsForSet().size(key);
    }

    // 随机获取元素
    public Object randomMember(String key) {
        return redisTemplate.opsForSet().randomMember(key);
    }

    // 随机获取多个元素
    public List<Object> randomMembers(String key, long count) {
        return redisTemplate.opsForSet().randomMembers(key, count);
    }

    // 并集
    public Set<Object> union(String key1, String key2) {
        return redisTemplate.opsForSet().union(key1, key2);
    }

    public Set<Object> union(String key, Collection<String> otherKeys) {
        return redisTemplate.opsForSet().union(key, otherKeys);
    }

    // 交集
    public Set<Object> intersect(String key1, String key2) {
        return redisTemplate.opsForSet().intersect(key1, key2);
    }

    public Set<Object> intersect(String key, Collection<String> otherKeys) {
        return redisTemplate.opsForSet().intersect(key, otherKeys);
    }

    // 差集
    public Set<Object> difference(String key1, String key2) {
        return redisTemplate.opsForSet().difference(key1, key2);
    }

    public Set<Object> difference(String key, Collection<String> otherKeys) {
        return redisTemplate.opsForSet().difference(key, otherKeys);
    }

    // 应用示例：共同好友
    public Set<Long> getCommonFriends(Long userId1, Long userId2) {
        Set<Object> friends1 = members("friends:" + userId1);
        Set<Object> friends2 = members("friends:" + userId2);

        return intersect("friends:" + userId1, Collections.singletonList("friends:" + userId2))
            .stream()
            .map(id -> (Long) id)
            .collect(Collectors.toSet());
    }

    // 应用示例：标签推荐
    public Set<String> recommendTags(Long userId) {
        // 获取用户关注的标签
        Set<Object> userTags = members("user_tags:" + userId);

        // 获取每个标签的相似标签
        Set<String> recommended = new HashSet<>();
        for (Object tagObj : userTags) {
            String tag = (String) tagObj;
            Set<Object> similarTags = members("tag_similar:" + tag);
            recommended.addAll(similarTags.stream()
                .map(String::valueOf)
                .collect(Collectors.toSet()));
        }

        // 排除已关注的标签
        recommended.removeAll(userTags.stream()
            .map(String::valueOf)
            .collect(Collectors.toSet()));

        return recommended;
    }

    // 应用示例：抽奖系统
    public boolean participateInLottery(String lotteryId, Long userId) {
        String key = "lottery:" + lotteryId;

        // 检查是否已参与
        if (isMember("lottery_participants:" + lotteryId, userId)) {
            return false;
        }

        // 添加到参与者列表
        add("lottery_participants:" + lotteryId, userId);

        // 记录用户参与的抽奖
        add("user_lotteries:" + userId, lotteryId);

        return true;
    }

    public Set<Long> getLotteryParticipants(String lotteryId) {
        Set<Object> members = members("lottery_participants:" + lotteryId);
        return members.stream()
            .map(id -> (Long) id)
            .collect(Collectors.toSet());
    }

    public Long drawWinner(String lotteryId) {
        // 随机抽取一个中奖者
        Object winner = randomMember("lottery_participants:" + lotteryId);

        if (winner == null) {
            return null;
        }

        // 从参与者列表中移除
        remove("lottery_participants:" + lotteryId, winner);

        // 添加到中奖名单
        add("lottery_winners:" + lotteryId, winner);

        return (Long) winner;
    }
}
```

## 七、ZSet 操作

```java
@Service
@Slf4j
public class RedisZSetService {

    private final RedisTemplate<String, Object> redisTemplate;

    // 添加元素
    public Boolean add(String key, Object value, double score) {
        return redisTemplate.opsForZSet().add(key, value, score);
    }

    // 批量添加
    public Long add(String key, Set<ZSetOperations.TypedTuple<Object>> tuples) {
        return redisTemplate.opsForZSet().add(key, tuples);
    }

    // 获取元素的分数
    public Double score(String key, Object value) {
        return redisTemplate.opsForZSet().score(key, value);
    }

    // 增加元素的分数
    public Double incrementScore(String key, Object value, double delta) {
        return redisTemplate.opsForZSet().incrementScore(key, value, delta);
    }

    // 获取排名（从低到高）
    public Long rank(String key, Object value) {
        return redisTemplate.opsForZSet().rank(key, value);
    }

    // 获取排名（从高到低）
    public Long reverseRank(String key, Object value) {
        return redisTemplate.opsForZSet().reverseRank(key, value);
    }

    // 获取指定范围的元素（从低到高）
    public Set<Object> range(String key, long start, long end) {
        return redisTemplate.opsForZSet().range(key, start, end);
    }

    // 获取指定范围的元素（从高到低）
    public Set<Object> reverseRange(String key, long start, long end) {
        return redisTemplate.opsForZSet().reverseRange(key, start, end);
    }

    // 获取指定范围的元素及分数
    public Set<ZSetOperations.TypedTuple<Object>> rangeWithScores(String key, long start, long end) {
        return redisTemplate.opsForZSet().rangeWithScores(key, start, end);
    }

    // 获取集合大小
    public Long size(String key) {
        return redisTemplate.opsForZSet().size(key);
    }

    // 获取指定分数范围的元素
    public Set<Object> rangeByScore(String key, double min, double max) {
        return redisTemplate.opsForZSet().rangeByScore(key, min, max);
    }

    // 移除元素
    public Long remove(String key, Object... values) {
        return redisTemplate.opsForZSet().remove(key, values);
    }

    // 应用示例：排行榜
    public void addScore(String leaderboard, Long userId, double score) {
        add(leaderboard, userId, score);
        redisTemplate.expire(leaderboard, 30, TimeUnit.DAYS);
    }

    public List<Map<String, Object>> getLeaderboard(String leaderboard, int top) {
        Set<ZSetOperations.TypedTuple<Object>> tuples = reverseRangeWithScores(
            leaderboard, 0, top - 1
        );

        return tuples.stream()
            .map(tuple -> Map.of(
                "userId", tuple.getValue(),
                "score", tuple.getScore(),
                "rank", (long) tuples.stream().toList().indexOf(tuple) + 1
            ))
            .collect(Collectors.toList());
    }

    public Long getUserRank(String leaderboard, Long userId) {
        Long rank = reverseRank(leaderboard, userId);
        return rank != null ? rank + 1 : null;
    }

    // 应用示例：延时队列
    public void addToDelayQueue(String queue, String taskId, long delay, TimeUnit unit) {
        double score = System.currentTimeMillis() + unit.toMillis(delay);
        add("delay_queue:" + queue, taskId, score);
    }

    public String pollFromDelayQueue(String queue) {
        // 获取当前时间之前的任务
        double now = System.currentTimeMillis();
        Set<Object> tasks = rangeByScore("delay_queue:" + queue, 0, now);

        if (tasks.isEmpty()) {
            return null;
        }

        // 获取第一个任务
        String taskId = (String) tasks.iterator().next();

        // 移除任务
        remove("delay_queue:" + queue, taskId);

        return taskId;
    }

    // 应用示例：热点内容推荐
    public void recordView(String content, Long userId) {
        String key = "content_views:" + content;
        // 记录用户浏览
        add("user_viewed:" + userId, content, System.currentTimeMillis());

        // 更新内容浏览量
        incrementScore(key, content, 1);
        redisTemplate.expire(key, 7, TimeUnit.DAYS);
    }

    public List<String> getHotContent(int limit) {
        Set<Object> hotContents = reverseRange("content_views:", 0, limit - 1);
        return hotContents.stream()
            .map(String::valueOf)
            .collect(Collectors.toList());
    }
}
```

## 八、分布式锁

```java
@Service
@Slf4j
public class RedisDistributedLock {

    private final RedisTemplate<String, String> redisTemplate;
    private final RedissonClient redissonClient;

    // 简单分布式锁
    public boolean tryLock(String lockKey, String requestId, long expireTime) {
        return Boolean.TRUE.equals(
            redisTemplate.opsForValue().setIfAbsent(
                lockKey,
                requestId,
                expireTime,
                TimeUnit.SECONDS
            )
        );
    }

    public boolean tryLock(String lockKey, String requestId, long expireTime, TimeUnit unit) {
        return Boolean.TRUE.equals(
            redisTemplate.opsForValue().setIfAbsent(
                lockKey,
                requestId,
                expireTime,
                unit
            )
        );
    }

    public void unlock(String lockKey, String requestId) {
        // 使用 Lua 脚本保证原子性
        String script = "if redis.call('get', KEYS[1]) == ARGV[1] then " +
                       "return redis.call('del', KEYS[1]) " +
                       "else " +
                       "return 0 " +
                       "end";

        DefaultRedisScript<Long> redisScript = new DefaultRedisScript<>(script, Long.class);
        Long result = redisTemplate.execute(redisScript, Collections.singletonList(lockKey), requestId);

        if (result == 0) {
            log.warn("释放分布式锁失败，锁可能已过期或被其他线程释放");
        }
    }

    // Redisson 可重入锁
    public <T> T executeWithLock(String lockName, LockCallback<T> callback) {
        RLock lock = redissonClient.getLock(lockName);

        try {
            // 获取锁
            boolean acquired = lock.tryLock(10, 30, TimeUnit.SECONDS);

            if (!acquired) {
                throw new BusinessException("获取锁失败");
            }

            // 执行业务逻辑
            return callback.execute();

        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new BusinessException("获取锁被中断");
        } finally {
            // 释放锁
            if (lock.isHeldByCurrentThread()) {
                lock.unlock();
            }
        }
    }

    // 读写锁
    public <T> T executeWithReadLock(String lockName, LockCallback<T> callback) {
        RReadWriteLock rwLock = redissonClient.getReadWriteLock(lockName);
        RLock readLock = rwLock.readLock();

        try {
            readLock.lock();
            return callback.execute();
        } finally {
            readLock.unlock();
        }
    }

    public <T> T executeWithWriteLock(String lockName, LockCallback<T> callback) {
        RReadWriteLock rwLock = redissonClient.getReadWriteLock(lockName);
        RLock writeLock = rwLock.writeLock();

        try {
            writeLock.lock();
            return callback.execute();
        } finally {
            writeLock.unlock();
        }
    }

    // 公平锁
    public <T> T executeWithFairLock(String lockName, LockCallback<T> callback) {
        RLock fairLock = redissonClient.getFairLock(lockName);

        try {
            fairLock.lock();
            return callback.execute();
        } finally {
            fairLock.unlock();
        }
    }

    // 红锁（跨多个 Redis 实例）
    public <T> T executeWithRedLock(List<String> lockNames, LockCallback<T> callback) {
        RLock redLock = redissonClient.getRedLock(lockNames.toArray(new String[0]));

        try {
            redLock.lock();
            return callback.execute();
        } finally {
            redLock.unlock();
        }
    }

    // 闭锁（所有线程到达后执行）
    public boolean awaitForAll(String lockName, long threads, long timeout, TimeUnit unit) {
        RCountDownLatch latch = redissonClient.getCountDownLatch(lockName);
        try {
            latch.trySetCount(threads);
            latch.await(timeout, unit);
            return true;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return false;
        }
    }

    public void countDown(String lockName) {
        RCountDownLatch latch = redissonClient.getCountDownLatch(lockName);
        latch.countDown();
    }

    // 信号量
    public <T> T executeWithSemaphore(String semaphoreName, int permits, LockCallback<T> callback) {
        RSemaphore semaphore = redissonClient.getSemaphore(semaphoreName);

        try {
            semaphore.acquire(permits);
            return callback.execute();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new BusinessException("获取信号量被中断");
        } finally {
            semaphore.release(permits);
        }
    }

    @FunctionalInterface
    public interface LockCallback<T> {
        T execute();
    }

    // 应用示例：防止重复提交
    public boolean preventDuplicateSubmit(String key, long timeout, TimeUnit unit) {
        String lockKey = "submit:" + key;
        String requestId = UUID.randomUUID().toString();

        if (tryLock(lockKey, requestId, timeout, unit)) {
            try {
                // 执行业务逻辑
                doSubmit(key);
                return true;
            } finally {
                unlock(lockKey, requestId);
            }
        }

        return false;
    }

    // 应用示例：库存扣减
    public boolean deductStock(Long productId, int quantity) {
        String lockKey = "stock:lock:" + productId;

        return executeWithLock(lockKey, () -> {
            // 检查库存
            Integer stock = (Integer) redisTemplate.opsForValue().get("stock:" + productId);

            if (stock == null || stock < quantity) {
                return false;
            }

            // 扣减库存
            redisTemplate.opsForValue().set("stock:" + productId, stock - quantity);

            return true;
        });
    }
}
```

## 九、Redis 持久化

```java
/**
 * Redis 提供两种持久化方式：RDB 和 AOF
 */

// RDB（Redis Database）
/*
机制：定时快照，将内存数据保存到磁盘
配置：
  save 900 1      # 900秒内至少1个key变化则保存
  save 300 10     # 300秒内至少10个key变化则保存
  save 60 10000   # 60秒内至少10000个key变化则保存

优点：
  - 文件紧凑，适合备份
  - 恢复速度快
  - 对性能影响小（fork子进程）

缺点：
  - 可能丢失最后一次快照后的数据
  - 大数据量时fork耗时
*/

// AOF（Append Only File）
/*
机制：记录每个写操作命令
配置：
  appendonly yes
  appendfsync everysec  # 每秒同步（推荐）

优点：
  - 数据安全性高
  - 可以实时备份

缺点：
  - 文件体积大
  - 恢复速度慢
  - 性能开销较大
*/

// 混合持久化（Redis 4.0+）
/*
机制：AOF重写时，先写入RDB格式的全量数据，再写入AOF格式的增量数据
配置：
  aof-use-rdb-preamble yes

优点：
  - 结合RDB和AOF的优点
  - 恢复速度快
  - 数据安全性高
*/
```

## 十、Redis 集群

```java
/**
 * Redis 三种集群模式
 */

// 1. 主从复制
/*
架构：一主多从
特点：
  - 主节点负责写，从节点负责读
  - 从节点复制主节点数据
  - 无法实现自动故障转移

配置：
  replicaof 127.0.0.1 6379  # 从节点配置
*/

// 2. 哨兵模式（Sentinel）
/*
架构：主从复制 + 哨兵监控
特点：
  - 监控主从节点状态
  - 自动故障转移
  - 客户端从哨兵获取主节点地址

配置：
  sentinel monitor mymaster 127.0.0.1 6379 2
  sentinel down-after-milliseconds mymaster 5000
*/

// 3. Cluster 模式
/*
架构：多主多从，数据分片
特点：
  - 16384个槽位分配到不同节点
  - 无中心架构
  - 自动故障转移
  - 在线扩容

命令：
  redis-cli --cluster create 127.0.0.1:6379 127.0.0.1:6380 ... --cluster-replicas 1
*/
```

## 十一、缓存问题与解决

```java
/**
 * 1. 缓存穿透
 * 问题：查询不存在的数据，缓存和数据库都没有
 * 解决：
 *   - 缓存空值（设置较短过期时间）
 *   - 布隆过滤器（Bloom Filter）
 */

@Component
public class CachePenetrationSolution {
    private final StringRedisTemplate redisTemplate;
    private final BloomFilter<String> bloomFilter;

    public String getData(String key) {
        // 布隆过滤器判断
        if (!bloomFilter.mightContain(key)) {
            return null;  // 一定不存在
        }

        String value = redisTemplate.opsForValue().get(key);
        if (value != null) {
            return value;
        }

        // 查询数据库
        value = queryDatabase(key);

        if (value != null) {
            redisTemplate.opsForValue().set(key, value, Duration.ofMinutes(30));
        } else {
            // 缓存空值，防止穿透
            redisTemplate.opsForValue().set(key, "NULL", Duration.ofMinutes(5));
        }

        return value;
    }
}

/**
 * 2. 缓存雪崩
 * 问题：大量缓存同时失效，请求全部打到数据库
 * 解决：
 *   - 设置不同的过期时间（随机偏移）
 *   - 使用互斥锁（只有一个线程去加载数据）
 *   - 缓存预热
 *   - 多级缓存
 */

@Component
public class CacheAvalancheSolution {
    private final StringRedisTemplate redisTemplate;

    public String getData(String key) {
        String value = redisTemplate.opsForValue().get(key);
        if (value != null) {
            return value;
        }

        // 互斥锁，只有一个线程去加载数据
        synchronized (this) {
            // 双重检查
            value = redisTemplate.opsForValue().get(key);
            if (value != null) {
                return value;
            }

            value = queryDatabase(key);
            if (value != null) {
                // 设置随机过期时间，避免同时失效
                long expireTime = 30 + (long) (Math.random() * 10);
                redisTemplate.opsForValue().set(key, value, Duration.ofMinutes(expireTime));
            }
        }

        return value;
    }
}

/**
 * 3. 缓存击穿
 * 问题：热点数据过期，大量并发请求同时查询数据库
 * 解决：
 *   - 互斥锁
 *   - 逻辑过期（不设置物理过期，通过逻辑判断）
 *   - 热点数据永不过期
 */

@Component
public class CacheBreakdownSolution {
    private final StringRedisTemplate redisTemplate;
    private final Map<String, Lock> locks = new ConcurrentHashMap<>();

    public String getHotData(String key) {
        String value = redisTemplate.opsForValue().get(key);
        if (value != null) {
            return value;
        }

        Lock lock = locks.computeIfAbsent(key, k -> new ReentrantLock());
        lock.lock();
        try {
            // 双重检查
            value = redisTemplate.opsForValue().get(key);
            if (value != null) {
                return value;
            }

            value = queryDatabase(key);
            if (value != null) {
                // 热点数据设置较长过期时间或永不过期
                redisTemplate.opsForValue().set(key, value, Duration.ofHours(1));
            }
            return value;
        } finally {
            lock.unlock();
        }
    }
}
```

## 十二、Redis 面试高频考点

```java
/**
 * Redis 面试高频问题
 */

// 1. Redis 为什么快？
/*
- 纯内存操作
- 单线程避免上下文切换
- IO多路复用（epoll）
- 高效的数据结构
- 避免了锁竞争
*/

// 2. Redis 是单线程还是多线程？
/*
- Redis 6.0 之前：单线程（网络IO和命令执行都是单线程）
- Redis 6.0 之后：多线程（网络IO使用多线程，命令执行仍是单线程）
- 为什么命令执行保持单线程？
  - 避免锁竞争
  - 避免上下文切换
  - 简化实现
*/

// 3. Redis 内存淘汰策略？
/*
- noeviction：不淘汰，直接返回错误（默认）
- allkeys-lru：所有键中使用LRU算法淘汰
- volatile-lru：只淘汰设置了过期时间的键（LRU）
- allkeys-random：所有键中随机淘汰
- volatile-random：只淘汰设置了过期时间的键（随机）
- volatile-ttl：淘汰即将过期的键
- allkeys-lfu：所有键中使用LFU算法淘汰（Redis 4.0+）
- volatile-lfu：只淘汰设置了过期时间的键（LFU）
*/

// 4. Redis 事务支持回滚吗？
/*
- Redis 事务不支持回滚
- 原因：
  - 简化实现，提高性能
  - 命令错误通常是编程错误，应该在开发阶段发现
  - 不支持回滚可以避免复杂的事务管理
- 但是可以使用 Lua 脚本实现原子操作
*/

// 5. Redis 和 Memcached 的区别？
/*
Redis：
- 支持多种数据结构
- 支持持久化
- 支持集群
- 支持事务和 Lua 脚本
- 单线程

Memcached：
- 只支持简单的 key-value
- 不支持持久化
- 不支持集群（需要客户端分片）
- 不支持事务
- 多线程
*/

// 6. 如何保证缓存和数据库的一致性？
/*
方案一：Cache Aside Pattern
  读：先读缓存，未命中则读数据库并写入缓存
  写：先更新数据库，再删除缓存

方案二：Read/Write Through
  读写都通过缓存，缓存负责同步数据库

方案三：Write Behind
  先更新缓存，异步更新数据库

最常用的是 Cache Aside Pattern，配合延时双删策略
*/

// 7. Redis 如何实现分布式锁？
/*
基本方案：
  SET key value NX EX 30  # 原子性设置锁和过期时间

问题与解决：
  - 锁误删：使用唯一标识（UUID），释放时验证
  - 锁续期：使用看门狗机制（Redisson）
  - 可重入：使用 Hash 结构记录重入次数
  - 高可用：使用 RedLock 算法
*/

// 8. Redis 热key问题？
/*
问题：某个 key 被大量访问，导致单个 Redis 节点压力过大

解决：
  - 本地缓存：在应用层加本地缓存
  - key拆分：将热key拆分为多个子key
  - 读写分离：增加从节点
  - 限流：对热key访问进行限流
*/

// 9. Redis 大key问题？
/*
问题：单个 key 的 value 过大，影响性能

危害：
  - 内存分配不均
  - 阻塞 Redis 主线程
  - 网络拥塞
  - 主从同步延迟

解决：
  - 拆分：将大key拆分为多个小key
  - 压缩：使用压缩算法
  - 监控：定期扫描大key
  - 清理：删除或迁移大key
*/

// 10. Redis 脑裂问题？
/*
问题：主从节点网络分区，导致多个节点认为自己是主节点

解决：
  - 配置 min-slaves-to-write 和 min-slaves-max-lag
  - 使用哨兵模式或 Cluster 模式
  - 配置合理的 down-after-milliseconds
*/
```

## 小结

本节学习了 Redis 缓存技术：

- **配置** - RedisTemplate、CacheManager
- **String** - 基础缓存、计数器、限流
- **Hash** - 对象缓存、购物车、库存
- **List** - 消息队列、排行榜
- **Set** - 共同好友、标签推荐、抽奖
- **ZSet** - 排行榜、延时队列、热点内容
- **分布式锁** - 可重入锁、读写锁、公平锁、红锁
- **持久化** - RDB、AOF、混合持久化
- **集群** - 主从复制、哨兵、Cluster
- **缓存问题** - 穿透、雪崩、击穿及解决方案
- **面试考点** - 高频面试题及答案

## 实践练习

### 编程题
1. 使用 Redis 实现一个分布式锁，确保在分布式环境下同一时刻只有一个服务实例执行定时任务。需要包含锁超时和自动续期机制。
2. 用 Redis 的 ZSet 实现一个实时排行榜，支持"积分更新"和"查询 Top N"功能，并处理并列排名。

### 思考题
1. 缓存穿透、缓存击穿、缓存雪崩分别是什么？各自的解决方案？
2. Redis 集群方案（主从、哨兵、Cluster）如何选择？CAP 理论在 Redis 中如何体现？

### 自测题
1. Redis 有哪五种基本数据类型？各自的常用命令？
2. Redis 的持久化方式 RDB 和 AOF 有什么区别？
3. Redisson 分布式锁的原理？

下一步将学习消息队列（→ `mq/beginner/01-message-queue.md`）。