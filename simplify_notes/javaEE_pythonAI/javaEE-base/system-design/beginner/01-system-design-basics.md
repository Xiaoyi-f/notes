# 系统设计基础

## 一、系统设计原则

### 1. 设计原则

```
┌─────────────────────────────────────────────────────┐
│              系统设计核心原则                          │
├─────────────────────────────────────────────────────┤
│                                                     │
│  1. 可用性 (Availability)                            │
│     - 服务正常时间占比                               │
│     - 目标：99.99% (4个9)                            │
│                                                     │
│  2. 可扩展性 (Scalability)                           │
│     - 垂直扩展：增加硬件资源                           │
│     - 水平扩展：增加服务实例                           │
│                                                     │
│  3. 可靠性 (Reliability)                             │
│     - 系统在各种条件下正常运行                         │
│     - 容错和自恢复能力                               │
│                                                     │
│  4. 性能 (Performance)                              │
│     - 响应时间、吞吐量、并发数                         │
│     - 低延迟、高吞吐                                 │
│                                                     │
│  5. 可维护性 (Maintainability)                     │
│     - 代码清晰、模块化、文档完善                     │
│     - 易于调试和升级                                 │
│                                                     │
│  6. 安全性 (Security)                               │
│     - 数据保护、访问控制、加密存储                     │
│     - 防止攻击和漏洞                                 │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 2. CAP 定理

```java
/**
 * CAP 定理：分布式系统不能同时满足以下三个保证
 *
 * C (Consistency) - 一致性
 *     - 所有节点同时看到相同的数据
 *     - 强一致性：写操作完成后，所有后续读取都能看到最新值
 *
 * A (Availability) - 可用性
 *     - 每个请求都能收到非错的响应
 *     - 不保证响应是最新的
 *
 * P (Partition Tolerance) - 分区容错
 *     - 系统在网络分区的情况下仍能继续运行
 *
 * 只能同时满足其中两个：
 * - CP：保证一致性和分区容错（牺牲可用性）
 *   - 例如：ZooKeeper、Redis Sentinel、HBase
 *
 * - AP：保证可用性和分区容错（牺牲一致性）
 *   - 例如：Cassandra、DynamoDB、DNS
 *
 * - CA：保证一致性和可用性（牺牲分区容错）
 *   - 例如：RDBMS、单机系统
 *
 * 注意：在分布式系统中，分区容错是必须的，所以只能在 CP 和 AP 之间选择
 */
```

### 3. BASE 理论

```java
/**
 * BASE 理论：CAP 中 AP 的延伸
 *
 * BA (Basically Available) - 基本可用
 *     - 系统在出现故障时，允许损失部分可用性
 *
 * S (Soft State) - 软状态
 *     - 系统中的数据可以随时间变化
 *     - 不要求强一致性
 *
 * E (Eventually Consistent) - 最终一致性
 *     - 系统保证在没有新的更新后，最终所有副本都会一致
 *     - 不同的业务场景有不同的最终一致性要求
 *
 * 最终一致性模型：
 * 1. 因果一致性：如果进程 A 看到了更新，进程 B 也能看到
 * 2. 读己之所写：进程 A 总能读到自己写的数据
 * 3. 会话一致性：用户会话期间的读一致
 * 4. 单调读：如果进程读到了某个值，后续读取不会读到更旧的值
 * 5. 单调写：系统保证写操作是串行的
 */
```

## 二、负载均衡

### 1. 负载均衡策略

```java
/**
 * 负载均衡算法
 */

public interface LoadBalancer {
    Server select(List<Server> servers);
}

// 1. 轮询 (Round Robin)
class RoundRobinBalancer implements LoadBalancer {
    private final AtomicInteger counter = new AtomicInteger(0);

    @Override
    public Server select(List<Server> servers) {
        int index = counter.getAndIncrement() % servers.size();
        return servers.get(index);
    }
}

// 2. 加权轮询 (Weighted Round Robin)
class WeightedRoundRobinBalancer implements LoadBalancer {
    private final AtomicInteger counter = new AtomicInteger(0);
    private final int totalWeight;

    public WeightedRoundRobinBalancer(int totalWeight) {
        this.totalWeight = totalWeight;
    }

    @Override
    public Server select(List<Server> servers) {
        int count = counter.getAndIncrement() % totalWeight;
        int sum = 0;
        for (Server server : servers) {
            sum += server.getWeight();
            if (count < sum) {
                return server;
            }
        }
        return servers.get(0);
    }
}

// 3. 随机 (Random)
class RandomBalancer implements LoadBalancer {
    private final Random random = new Random();

    @Override
    public Server select(List<Server> servers) {
        return servers.get(random.nextInt(servers.size()));
    }
}

// 4. 最少连接 (Least Connections)
class LeastConnectionsBalancer implements LoadBalancer {
    @Override
    public Server select(List<Server> servers) {
        Server selected = null;
        int minConnections = Integer.MAX_VALUE;

        for (Server server : servers) {
            if (server.getActiveConnections() < minConnections) {
                minConnections = server.getActiveConnections();
                selected = server;
            }
        }
        return selected;
    }
}

// 5. 一致性哈希 (Consistent Hash)
class ConsistentHashBalancer implements LoadBalancer {
    private final TreeMap<Integer, Server> ring = new TreeMap<>();

    public ConsistentHashBalancer(List<Server> servers, int virtualNodes) {
        for (Server server : servers) {
            for (int i = 0; i < virtualNodes; i++) {
                int hash = hash(server.getHost() + "#" + i);
                ring.put(hash, server);
            }
        }
    }

    @Override
    public Server select(List<Server> servers) {
        String key = Thread.currentThread().getName();
        int hash = hash(key);

        // 找到第一个大于等于 hash 的节点
        Map.Entry<Integer, Server> entry = ring.ceilingEntry(hash);
        if (entry == null) {
            entry = ring.firstEntry();  // 环形
        }
        return entry.getValue();
    }

    private int hash(String key) {
        return key.hashCode() & Integer.MAX_VALUE;
    }
}
```

### 2. 四层与七层负载均衡

```
┌─────────────────────────────────────────────────────┐
│              四层负载均衡 (L4)                         │
│  - 基于 IP 和端口                                   │
│  - 协议：TCP/UDP                                    │
│  - 性能高，功能有限                                 │
│  - 工具：LVS、HAProxy (mode tcp)、Nginx (stream)     │
├─────────────────────────────────────────────────────┤
│              七层负载均衡 (L7)                         │
│  - 基于 HTTP 协议内容                               │
│  - 协议：HTTP/HTTPS                                 │
│  - 功能丰富，性能相对较低                           │
│  - 工具：Nginx、HAProxy (mode http)、Envoy          │
└─────────────────────────────────────────────────────┘

选择建议：
- 需要高性能：使用 L4
- 需要 HTTP 级控制：使用 L7
- 一般场景：L4 + L7 组合使用
```

## 三、缓存策略

### 1. 缓存位置

```java
/**
 * 缓存层次结构
 */

// 1. 浏览器缓存
//    - HTTP Cache-Control, ETag
//    - 适用于静态资源

// 2. CDN 缓存
//    - 分布式内容分发网络
//    - 靠近用户的边缘节点
//    - 适用于静态资源和部分动态资源

// 3. 应用缓存（本地缓存）
//    - Guava Cache、Caffeine
//    - 速度快，容量有限
//    - 适用于热点数据

// 4. 分布式缓存
//    - Redis、Memcached
//    - 容量大，可共享
//    - 适用于共享数据

// 5. 数据库缓存
//    - MySQL Query Cache（已弃用）
//    - PostgreSQL、Oracle 内部缓存
```

### 2. 缓存更新策略

```java
/**
 * Cache Aside Pattern（旁路缓存）
 * 应用最广泛的缓存策略
 */

@Service
public class CacheAsideService {
    private final UserRepository userRepository;
    private final CacheManager cacheManager;

    public User getUser(Long userId) {
        // 1. 先查缓存
        String cacheKey = "user:" + userId;
        Cache cache = cacheManager.getCache("users");
        User cached = cache.get(cacheKey, User.class);

        if (cached != null) {
            return cached;
        }

        // 2. 缓存未命中，查数据库
        User user = userRepository.findById(userId)
            .orElseThrow(() -> new ResourceNotFoundException("用户不存在"));

        // 3. 写入缓存
        cache.put(cacheKey, user);

        return user;
    }

    public void updateUser(User user) {
        // 1. 更新数据库
        userRepository.save(user);

        // 2. 删除缓存（延迟双删）
        String cacheKey = "user:" + user.getId();
        cacheManager.getCache("users").evict(cacheKey);

        // 延迟删除，防止并发问题
        CompletableFuture.runAsync(() -> {
            try {
                Thread.sleep(500);
                cacheManager.getCache("users").evict(cacheKey);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
    }
}

/**
 * Read Through Pattern（穿透缓存）
 * 应用负责从数据库加载并写入缓存
 */

@Service
public class ReadThroughService {
    private final CacheLoader<String, User> cacheLoader;
    private final LoadingCache<String, User> loadingCache;

    public ReadThroughService(UserRepository userRepository) {
        this.cacheLoader = new CacheLoader<>() {
            @Override
            public User load(String key) {
                Long userId = Long.parseLong(key.split(":")[1]);
                return userRepository.findById(userId)
                    .orElseThrow(() -> new ResourceNotFoundException("用户不存在"));
            }
        };

        this.loadingCache = Caffeine.newBuilder()
            .expireAfterWrite(1, TimeUnit.HOURS)
            .maximumSize(1000)
            .build(cacheLoader);
    }

    public User getUser(Long userId) {
        return loadingCache.get("user:" + userId);
    }
}

/**
 * Write Through Pattern（直写缓存）
 * 写入时同时更新缓存和数据库
 */

@Service
public class WriteThroughService {
    private final UserRepository userRepository;
    private final Cache<String, User> cache;

    public void updateUser(User user) {
        // 同时更新缓存和数据库
        userRepository.save(user);
        String cacheKey = "user:" + user.getId();
        cache.put(cacheKey, user);
    }
}

/**
 * Write Behind Pattern（异步写回）
 * 先更新缓存，异步更新数据库
 * 注意：可能数据丢失
 */

@Service
public class WriteBehindService {
    private final UserRepository userRepository;
    private final Cache<String, User> cache;
    private final ExecutorService executorService;

    public void updateUser(User user) {
        // 先更新缓存
        String cacheKey = "user:" + user.getId();
        cache.put(cacheKey, user);

        // 异步更新数据库
        executorService.submit(() -> {
            try {
                userRepository.save(user);
            } catch (Exception e) {
                log.error("数据库更新失败", e);
                // 可以重试或记录到队列
            }
        });
    }
}
```

### 3. 缓存问题与解决

```java
/**
 * 1. 缓存穿透
 * 问题：查询不存在的数据，缓存和数据库都没有，每次都查数据库
 * 解决：
 *   - 缓存空值
 *   - 布隆过滤器
 */

@Service
public class CachePenetrationService {
    private final UserRepository userRepository;
    private final Cache<String, User> cache;
    private final BloomFilter<Long> bloomFilter;

    public User getUser(Long userId) {
        // 布隆过滤器判断
        if (!bloomFilter.mightContain(userId)) {
            return null;
        }

        String cacheKey = "user:" + userId;
        User cached = cache.get(cacheKey);

        if (cached != null) {
            return cached.equals(NULL_VALUE) ? null : cached;
        }

        User user = userRepository.findById(userId).orElse(null);

        if (user != null) {
            cache.put(cacheKey, user);
        } else {
            // 缓存空值，防止穿透
            cache.put(cacheKey, NULL_VALUE, Duration.ofMinutes(5));
        }
        return user;
    }

    private static final User NULL_VALUE = new User();  // 标记对象
}

/**
 * 2. 缓存雪崩
 * 问题：大量缓存同时失效，导致请求全部打到数据库
 * 解决：
 *   - 设置不同的过期时间
 *   - 使用互斥锁
 *   - 缓存预热
 */

@Service
public class CacheAvalancheService {
    private final UserRepository userRepository;
    private final Cache<String, User> cache;

    public User getUser(Long userId) {
        String cacheKey = "user:" + userId;
        User cached = cache.get(cacheKey);

        if (cached != null) {
            return cached;
        }

        // 使用互斥锁
        synchronized (this) {
            // 双重检查
            cached = cache.get(cacheKey);
            if (cached != null) {
                return cached;
            }

            User user = userRepository.findById(userId)
                .orElseThrow(() -> new ResourceNotFoundException("用户不存在"));

            // 设置随机过期时间，避免同时失效
            long expireTime = 30 + (long) (Math.random() * 10);
            cache.put(cacheKey, user, Duration.ofMinutes(expireTime));

            return user;
        }
    }
}

/**
 * 3. 缓存击穿
 * 问题：热点数据过期，大量并发请求同时查询数据库
 * 解决：
 *   - 互斥锁
 *   - 永不过期
 */

@Service
public class CacheBreakdownService {
    private final UserRepository userRepository;
    private final Cache<String, User> cache;
    private final Map<String, Lock> locks = new ConcurrentHashMap<>();

    public User getUser(Long userId) {
        String cacheKey = "user:" + userId;
        User cached = cache.get(cacheKey);

        if (cached != null) {
            return cached;
        }

        // 获取锁
        Lock lock = locks.computeIfAbsent(cacheKey, k -> new ReentrantLock());
        lock.lock();
        try {
            // 双重检查
            cached = cache.get(cacheKey);
            if (cached != null) {
                return cached;
            }

            User user = userRepository.findById(userId)
                .orElseThrow(() -> new ResourceNotFoundException("用户不存在"));

            cache.put(cacheKey, user, Duration.ofHours(1));
            return user;
        } finally {
            lock.unlock();
        }
    }
}
```

## 四、数据库扩展

### 1. 读写分离

```java
/**
 * 读写分离架构
 */

// 1. 主从数据源配置
@Configuration
public class DataSourceConfig {

    @Bean
    @Primary
    public DataSource masterDataSource(
            @Value("${spring.datasource.master.url}") String url,
            @Value("${spring.datasource.master.username}") String username,
            @Value("${spring.datasource.master.password}") String password
    ) {
        HikariDataSource dataSource = new HikariDataSource();
        dataSource.setJdbcUrl(url);
        dataSource.setUsername(username);
        dataSource.setPassword(password);
        return dataSource;
    }

    @Bean
    public DataSource slaveDataSource(
            @Value("${spring.datasource.slave.url}") String url,
            @Value("${spring.datasource.slave.username}") String username,
            @Value("${spring.datasource.slave.password}") String password
    ) {
        HikariDataSource dataSource = new HikariDataSource();
        dataSource.setJdbcUrl(url);
        dataSource.setUsername(username);
        dataSource.setPassword(password);
        return dataSource;
    }

    @Bean
    public DynamicDataSource dynamicDataSource(
            DataSource masterDataSource,
            DataSource slaveDataSource
    ) {
        Map<Object, Object> targetDataSources = new HashMap<>();
        targetDataSources.put("master", masterDataSource);
        targetDataSources.put("slave", slaveDataSource);

        DynamicDataSource dataSource = new DynamicDataSource();
        dataSource.setDefaultTargetDataSource(masterDataSource);
        dataSource.setTargetDataSources(targetDataSources);
        return dataSource;
    }
}

// 2. 动态数据源
public class DynamicDataSource extends AbstractRoutingDataSource {
    @Override
    protected Object determineCurrentLookupKey() {
        return DataSourceContextHolder.getDataSourceType();
    }
}

public class DataSourceContextHolder {
    private static final ThreadLocal<String> contextHolder = new ThreadLocal<>();

    public static void setDataSourceType(String dataSourceType) {
        contextHolder.set(dataSourceType);
    }

    public static String getDataSourceType() {
        return contextHolder.get();
    }

    public static void clearDataSourceType() {
        contextHolder.remove();
    }
}

// 3. 自定义注解
@Target({ElementType.METHOD})
@Retention(RetentionPolicy.RUNTIME)
public @interface ReadOnly {
}

// 4. AOP 切面
@Aspect
@Component
public class ReadOnlyAspect {
    @Around("@annotation(ReadOnly)")
    public Object around(ProceedingJoinPoint joinPoint) throws Throwable {
        try {
            DataSourceContextHolder.setDataSourceType("slave");
            return joinPoint.proceed();
        } finally {
            DataSourceContextHolder.clearDataSourceType();
        }
    }
}

// 5. 使用示例
@Service
public class UserService {
    private final UserRepository userRepository;

    public User findById(Long id) {
        // 查询操作，使用从库
        return userRepository.findById(id).orElse(null);
    }

    @Transactional
    public User save(User user) {
        // 写操作，使用主库
        return userRepository.save(user);
    }

    @ReadOnly  // 使用 AOP 自动切换到从库
    public User findByUsername(String username) {
        return userRepository.findByUsername(username);
    }
}
```

### 2. 分库分表

```java
/**
 * 分库分表策略
 */

// 1. 分片算法
public class ShardingStrategy {
    private static final int DB_COUNT = 4;
    private static final int TABLE_COUNT = 10;

    // 根据 user_id 分库分表
    public static String getShardTable(Long userId) {
        int dbIndex = (int) (userId % DB_COUNT);
        int tableIndex = (int) (userId / DB_COUNT % TABLE_COUNT);

        return String.format("db%d.user_%d", dbIndex, tableIndex);
    }

    // 哈希分片（更均匀）
    public static String getHashShardTable(Long userId) {
        int hash = userId.hashCode();
        int dbIndex = Math.abs(hash) % DB_COUNT;
        int tableIndex = Math.abs(hash / DB_COUNT) % TABLE_COUNT;

        return String.format("db%d.user_%d", dbIndex, tableIndex);
    }

    // 范围分片（按时间）
    public static String getRangeShardTable(LocalDateTime createTime) {
        int year = createTime.getYear();
        int month = createTime.getMonthValue();

        return String.format("user_%d_%02d", year, month);
    }
}

// 2. 动态 SQL
@Repository
public class DynamicQueryRepository {
    private final JdbcTemplate jdbcTemplate;

    public List<User> findByUserId(Long userId) {
        String table = ShardingStrategy.getShardTable(userId);
        String sql = String.format("SELECT * FROM %s WHERE id = ?", table);

        return jdbcTemplate.query(sql, new UserRowMapper(), userId);
    }

    public List<User> findByUsername(String username) {
        // 需要查询所有分片
        List<User> results = new ArrayList<>();

        for (int dbIndex = 0; dbIndex < 4; dbIndex++) {
            for (int tableIndex = 0; tableIndex < 10; tableIndex++) {
                String table = String.format("db%d.user_%d", dbIndex, tableIndex);
                String sql = String.format("SELECT * FROM %s WHERE username = ?", table);

                try {
                    List<User> users = jdbcTemplate.query(sql,
                        new UserRowMapper(), username);
                    results.addAll(users);
                } catch (Exception e) {
                    log.error("查询失败: {}", table, e);
                }
            }
        }
        return results;
    }
}

// 3. 分布式 ID 生成
@Component
public class DistributedIdGenerator {
    // 雪花算法实现
    private final long workerId;
    private final long datacenterId;
    private long sequence = 0L;
    private long lastTimestamp = -1L;

    // 时间戳位数、机器ID位数、序列号位数
    private static final long WORKER_ID_BITS = 5L;
    private static final long DATACENTER_ID_BITS = 5L;
    private static final long SEQUENCE_BITS = 12L;

    private static final long MAX_WORKER_ID = ~(-1L << WORKER_ID_BITS);
    private static final long MAX_DATACENTER_ID = ~(-1L << DATACENTER_ID_BITS);

    public DistributedIdGenerator(long workerId, long datacenterId) {
        if (workerId > MAX_WORKER_ID || workerId < 0) {
            throw new IllegalArgumentException("workerId 超出范围");
        }
        if (datacenterId > MAX_DATACENTER_ID || datacenterId < 0) {
            throw new IllegalArgumentException("datacenterId 超出范围");
        }
        this.workerId = workerId;
        this.datacenterId = datacenterId;
    }

    public synchronized long nextId() {
        long timestamp = System.currentTimeMillis();

        if (timestamp < lastTimestamp) {
            throw new RuntimeException("时钟回拨");
        }

        if (timestamp == lastTimestamp) {
            sequence = (sequence + 1) & (-1L << SEQUENCE_BITS);
            if (sequence == 0) {
                timestamp = tilNextMillis(lastTimestamp);
            }
        } else {
            sequence = 0L;
        }

        lastTimestamp = timestamp;

        return ((timestamp - 1288834974657L) << (WORKER_ID_BITS + DATACENTER_ID_BITS + SEQUENCE_BITS))
                | (datacenterId << (WORKER_ID_BITS + SEQUENCE_BITS))
                | (workerId << SEQUENCE_BITS)
                | sequence;
    }

    private long tilNextMillis(long lastTimestamp) {
        long timestamp = System.currentTimeMillis();
        while (timestamp <= lastTimestamp) {
            timestamp = System.currentTimeMillis();
        }
        return timestamp;
    }
}
```

## 五、消息队列

### 1. 使用场景

```java
/**
 * 消息队列应用场景
 */

// 1. 异步处理
@Service
public class EmailService {
    private final MessageProducer messageProducer;

    public void sendEmail(String to, String subject, String content) {
        // 直接发送邮件耗时，改为异步
        EmailMessage message = new EmailMessage(to, subject, content);
        messageProducer.send("email-queue", message);
    }
}

@RabbitListener(queues = "email-queue")
public class EmailConsumer {
    private final JavaMailSender mailSender;

    @RabbitHandler
    public void handle(EmailMessage message) {
        try {
            MimeMessage mimeMessage = createMimeMessage(message);
            mailSender.send(mimeMessage);
        } catch (Exception e) {
            log.error("发送邮件失败", e);
            throw new RuntimeException(e);  // 重试
        }
    }
}

// 2. 解耦
@Service
public class OrderService {
    private final OrderRepository orderRepository;
    private final MessageProducer messageProducer;

    @Transactional
    public Order createOrder(OrderCreateDto dto) {
        Order order = new Order(dto);
        order = orderRepository.save(order);

        // 发送订单创建事件，解耦后续处理
        OrderCreatedEvent event = new OrderCreatedEvent(order);
        messageProducer.send("order-created", event);

        return order;
    }
}

// 订单服务只需要创建订单，不需要关心后续的库存、支付等
@RabbitListener(queues = "order-created")
public class InventoryConsumer {
    public void handle(OrderCreatedEvent event) {
        // 扣减库存
    }
}

@RabbitListener(queues = "order-created")
public class PaymentConsumer {
    public void handle(OrderCreatedEvent event) {
        // 处理支付
    }
}

// 3. 削峰填谷
@Service
public class SeckillService {
    private final MessageProducer messageProducer;
    private final RedisTemplate<String, Object> redisTemplate;

    public void seckill(Long userId, Long productId) {
        // 快速扣减 Redis 库存
        String key = "seckill:stock:" + productId;
        Long stock = redisTemplate.opsForValue().decrement(key);

        if (stock >= 0) {
            // 请求放入队列，异步处理
            SeckillRequest request = new SeckillRequest(userId, productId);
            messageProducer.send("seckill-queue", request);

            return true;
        }
        return false;
    }
}

@RabbitListener(queues = "seckill-queue", containerFactory = "batchFactory")
public void SeckillConsumer {
    private final OrderService orderService;

    public void handle(List<SeckillRequest> requests) {
        // 批量处理订单
        for (SeckillRequest request : requests) {
            orderService.createOrder(request.getUserId(), request.getProductId());
        }
    }
}
```

### 2. 消息可靠性

```java
/**
 * 消息可靠性保证
 */

// 1. 生产者确认
@Configuration
public class RabbitMQConfig {

    @Bean
    public RabbitTemplate rabbitTemplate(ConnectionFactory connectionFactory) {
        RabbitTemplate template = new RabbitTemplate(connectionFactory);

        // 开启确认模式
        template.setConfirmCallback((correlationData, ack, cause) -> {
            if (ack) {
                log.info("消息发送成功: {}", correlationData);
            } else {
                log.error("消息发送失败: {}, 原因: {}", correlationData, cause);
                // 重试或记录到数据库
            }
        });

        // 开启返回模式
        template.setReturnCallback((message, replyCode, replyText, exchange, routingKey) -> {
            log.error("消息路由失败: {}, 交换机: {}, 路由键: {}, 回复码: {}, 回复文本: {}",
                new String(message.getBody()), exchange, routingKey, replyCode, replyText);
        });

        return template;
    }

    // 2. 消息持久化
    @Bean
    public Queue durableQueue() {
        return QueueBuilder.durable("order-queue")
            .build();
    }

    // 3. 消费者手动确认
    @Bean
    public SimpleRabbitListenerContainerFactory batchFactory(
            ConnectionFactory connectionFactory
    ) {
        SimpleRabbitListenerContainerFactory factory =
            new SimpleRabbitListenerContainerFactory(connectionFactory);
        factory.setAcknowledgeMode(AcknowledgeMode.MANUAL);
        factory.setBatchSize(20);  // 批量确认
        return factory;
    }
}

@Service
public class OrderConsumer {

    @RabbitListener(queues = "order-queue")
    public void handle(
            Order order,
            Channel channel,
            @Header(AmqpHeaders.DELIVERY_TAG) long deliveryTag
    ) {
        try {
            // 处理消息
            processOrder(order);

            // 手动确认
            channel.basicAck(deliveryTag, false);  // false = 不批量确认
        } catch (Exception e) {
            log.error("处理订单失败: {}", order, e);

            try {
                // 拒绝消息，重新入队
                channel.basicNack(deliveryTag, false, true);
            } catch (IOException ioException) {
                log.error("消息重新入队失败", ioException);
            }
        }
    }
}

// 4. 死信队列
@Configuration
public class DeadLetterConfig {

    @Bean
    public Queue deadLetterQueue() {
        return QueueBuilder.durable("order-dlq").build();
    }

    @Bean
    public DirectExchange deadLetterExchange() {
        return new DirectExchange("order-dlx");
    }

    @Bean
    public Binding deadLetterBinding() {
        return BindingBuilder.bind(deadLetterQueue())
            .to(deadLetterExchange())
            .with("order-dlq");
    }

    @Bean
    public Queue orderQueue() {
        return QueueBuilder.durable("order-queue")
            .withArgument("x-dead-letter-exchange", "order-dlx")
            .withArgument("x-dead-letter-routing-key", "order-dlq")
            .build();
    }
}
```

## 六、分布式事务

### 1. Seata AT 模式

```java
/**
 * Seata 分布式事务
 */

// 1. 启动类添加注解
@SpringBootApplication
@EnableAutoDataSourceProxy  // Seata 数据源代理
public class Application {}

// 2. 全局事务注解
@Service
public class OrderService {
    private final OrderRepository orderRepository;
    private final InventoryService inventoryService;
    private final AccountService accountService;

    // AT 模式：自动补偿
    @GlobalTransactional(name = "create-order", rollbackFor = Exception.class)
    public Order createOrder(OrderCreateDto dto) {
        // 1. 创建订单
        Order order = new Order(dto);
        order = orderRepository.save(order);

        // 2. 扣减库存（远程服务）
        inventoryService.deductStock(dto.getProductId(), dto.getQuantity());

        // 3. 扣减余额（远程服务）
        accountService.deductBalance(dto.getUserId(), order.getTotalAmount());

        return order;
    }
}

// 3. TCC 模式
@Service
public class TccOrderService {

    // Prepare 阶段：锁定库存和余额
    @GlobalTransactional(name = "create-order-tcc", rollbackFor = Exception.class)
    public Order createOrder(OrderCreateDto dto) {
        // Prepare 阶段
        tccInventoryService.prepare(dto.getProductId(), dto.getQuantity());
        tccAccountService.prepare(dto.getUserId(), dto.getTotalAmount());

        // 创建订单（预留状态）
        Order order = new Order(dto, OrderStatus.PENDING);
        order = orderRepository.save(order);

        return order;
    }

    // Confirm 阶段：确认扣减
    @Transactional
    public void confirmOrder(Long orderId) {
        Order order = orderRepository.findById(orderId)
            .orElseThrow(() -> new ResourceNotFoundException("订单不存在"));

        if (order.getStatus() != OrderStatus.PENDING) {
            throw new BusinessException("订单状态不正确");
        }

        // Confirm 阶段
        tccInventoryService.confirm(order.getProductId(), order.getQuantity());
        tccAccountService.confirm(order.getUserId(), order.getTotalAmount());

        // 更新订单状态
        order.setStatus(OrderStatus.CONFIRMED);
        orderRepository.save(order);
    }

    // Cancel 阶段：取消扣减
    @Transactional
    public void cancelOrder(Long orderId) {
        Order order = orderRepository.findById(orderId)
            .orElseThrow(() -> new ResourceNotFoundException("订单不存在"));

        // Cancel 阶段
        tccInventoryService.cancel(order.getProductId(), order.getQuantity());
        tccAccountService.cancel(order.getUserId(), order.getTotalAmount());

        // 更新订单状态
        order.setStatus(OrderStatus.CANCELLED);
        orderRepository.save(order);
    }
}

// TCC 服务接口
@LocalTCC
public interface TccInventoryService {
    // Prepare 阶段
    @TwoPhaseBusinessAction(
        name = "prepareInventory",
        commitMethod = "commit",
        rollbackMethod = "rollback"
    )
    boolean prepare(@BusinessActionContextParameter(paramName = "dto") PrepareInventoryDto dto);

    // Confirm 阶段
    boolean commit(BusinessActionContext context);

    // Rollback 阶段
    boolean rollback(BusinessActionContext context);
}

// TCC 服务实现
@Service
public class TccInventoryServiceImpl implements TccInventoryService {

    @Override
    public boolean prepare(PrepareInventoryDto dto) {
        // 预留库存（创建预留记录）
        InventoryReservation reservation = new InventoryReservation(
            dto.getProductId(),
            dto.getQuantity(),
            ReservationStatus.PENDING
        );
        reservationRepository.save(reservation);

        // 检查可用库存
        int available = inventoryService.getAvailableStock(dto.getProductId());
        if (available < dto.getQuantity()) {
            throw new BusinessException("库存不足");
        }

        // 冻结库存
        inventoryService.freezeStock(dto.getProductId(), dto.getQuantity());

        return true;
    }

    @Override
    public boolean commit(BusinessActionContext context) {
        PrepareInventoryDto dto = (PrepareInventoryDto) context.getActionContext("dto");

        // 扣减库存（真正扣减）
        inventoryService.deductStock(dto.getProductId(), dto.getQuantity());

        // 更新预留状态
        updateReservationStatus(context, ReservationStatus.COMMITTED);

        return true;
    }

    @Override
    public boolean rollback(BusinessActionContext context) {
        PrepareInventoryDto dto = (PrepareInventoryDto) context.getActionContext("dto");

        // 释放冻结的库存
        inventoryService.unfreezeStock(dto.getProductId(), dto.getQuantity());

        // 更新预留状态
        updateReservationStatus(context, ReservationStatus.CANCELLED);

        return true;
    }
}
```

## 小结

本节学习了系统设计基础：

- **设计原则** - 可用性、可扩展性、可靠性、性能、安全性
- **CAP 理论** - 一致性、可用性、分区容错
- **BASE 理论** - 基本可用、软状态、最终一致性
- **负载均衡** - 策略算法、L4/L7 区别
- **缓存策略** - 位置、更新策略、问题解决
- **数据库扩展** - 读写分离、分库分表
- **消息队列** - 使用场景、可靠性保证
- **分布式事务** - Seata AT、TCC 模式

## 实践练习

### 编程题
1. 设计一个短链接系统：生成 7 位短码、支持 301 重定向、统计点击数据、处理高并发读写（100万 QPS）。
2. 基于 Redis 实现一个简单的限流器：支持滑动窗口算法，对每个用户每分钟最多请求 100 次。

### 思考题
1. 设计一个微博 Feed 流系统，如何处理大 V 粉丝的推送延迟问题？
2. CAP 理论在分布式系统设计中如何权衡？给出具体场景的例子。

### 自测题
1. 负载均衡的常见算法有哪些？最少连接数和加权轮询的区别？
2. 分布式 ID 生成方案中，UUID 和 Snowflake 的优缺点？
3. 什么是缓存穿透/击穿/雪崩？如何解决？

下一步将学习网络与操作系统基础（→ `fundamentals/beginner/01-network-os.md`）。