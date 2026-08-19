# 性能优化

## 一、JVM 性能调优

### 1. JVM 内存模型

```
┌─────────────────────────────────────────────────────┐
│                    JVM 内存结构                       │
├─────────────────────────────────────────────────────┤
│  程序计数器 (PC Register)                           │
├─────────────────────────────────────────────────────┤
│  虚拟机栈 (VM Stack) - 线程私有，存储栈帧          │
│  - 局部变量、方法参数                               │
│  - StackOverflowError                               │
├─────────────────────────────────────────────────────┤
│  本地方法栈 (Native Method Stack)                     │
├─────────────────────────────────────────────────────┤
│  堆 (Heap) - 所有对象实例及数组                       │
│  - Young Generation (新生代)                       │
│    └── Eden、Survivor 0、Survivor 1                 │
│  - Old Generation (老年代)                          │
│    └── Tenured Generation、Old Gen                    │
│  - OutOfMemoryError                                 │
├─────────────────────────────────────────────────────┤
│  方法区 (Method Area)                                 │
│  - 类信息、常量池、静态变量                          │
│  - 元空间 + 方法区                                 │
├─────────────────────────────────────────────────────┤
│  直接内存 (Direct Memory) - NIO                       │
└─────────────────────────────────────────────────────┘
```

### 2. 垃圾回收算法

```java
// 示例：内存泄漏检测
public class MemoryLeakExample {

    // 模拟静态集合导致的内存泄漏
    private static final Map<Integer, Object> CACHE = new HashMap<>();

    public void addToCache(Integer key, Object value) {
        CACHE.put(key, value);
        // 缓存不会自动清理，导致内存泄漏
    }

    // 正确做法：使用 WeakHashMap 或手动清理
    private static final Map<Integer, Object> WEAK_CACHE = new WeakHashMap<>();
    private static final ReferenceQueue<Object> REFERENCE_QUEUE = new ReferenceQueue<>();

    // 线程池导致的内存泄漏
    public void threadPoolLeak() {
        ThreadPoolExecutor executor = new ThreadPoolExecutor(
            10, 20, 60, TimeUnit.SECONDS,
            new LinkedBlockingQueue<>(100),
            new ThreadFactory() {
                private AtomicInteger count = new AtomicInteger(0);
                @Override
                public Thread newThread(Runnable r) {
                    return new Thread(r, "pool-thread-" + count.incrementAndGet());
                }
            }
        );

        // 错误：线程池未关闭
        executor.submit(() -> System.out.println("Task"));

        // 正确：线程池使用完毕后关闭
        try {
            // 执行任务
        } finally {
            executor.shutdown();
        }
    }

    // 监听器导致的内存泄漏
    public class LeakyComponent {
        private List<EventListener> listeners = new ArrayList<>();

        public void addListener(EventListener listener) {
            listeners.add(listener);
        }

        public void removeListener(EventListener listener) {
            listeners.remove(listener);  // 需要正确实现
        }

        public void fire() {
            for (EventListener listener : listeners) {
                listener.onEvent();
            }
        }
    }

    // 正确做法：使用弱引用
    public class NonLeakyComponent {
        private final List<WeakReference<EventListener>> listeners = new ArrayList<>();

        public void addListener(EventListener listener) {
            listeners.add(new WeakReference<>(listener));
        }

        public void fire() {
            Iterator<WeakReference<EventListener>> iterator = listeners.iterator();
            while (iterator.hasNext()) {
                WeakReference<EventListener> ref = iterator.next();
                EventListener listener = ref.get();
                if (listener != null) {
                    listener.onEvent();
                } else {
                    iterator.remove();
                }
            }
        }
    }

    // 使用 LRU Cache 防止内存泄漏
    private static final Cache<Integer, Object> LRU_CACHE = CacheBuilder.newBuilder()
        .maximumSize(1000)
        .expireAfterWrite(10, TimeUnit.MINUTES)
        .removalListener(notification -> {
            System.out.println("缓存移除: " + notification.getKey());
        })
        .build();

    public void putToCache(Integer key, Object value) {
        LRU_CACHE.put(key, value);
    }
}
```

### 3. JVM 参数配置

```bash
# 启动参数示例
java -jar app.jar \
  -Xms512m \
  -Xmx512m \
  -XX:NewRatio=2 \
  -XX:SurvivorRatio=8 \
  -XX:+UseG1GC \
  -XX:MaxGCPauseMillis=200 \
  -XX:+HeapDumpOnOutOfMemoryError \
  -XX:HeapDumpPath=/logs/heap_dump.hprof \
  -XX:+PrintGCDetails \
  -XX:+PrintGCTimeStamps \
  -Xloggc:/logs/gc.log \
  -XX:+UseStringDeduplication \
  -XX:MetaspaceSize=256m \
  -XX:MaxMetaspaceSize=512m \
  -Dfile.encoding=UTF-8 \
  -Duser.timezone=Asia/Shanghai
```

### 4. 监控和分析工具

```java
import com.sun.management.HotSpotDiagnosticMXBean;
import java.lang.management.*;

public class JVMMonitoring {

    public static void monitorMemory() {
        MemoryMXBean memoryMxBean = ManagementFactory.getMemoryMXBean();
        MemoryUsage heapUsage = memoryMxBean.getHeapMemoryUsage();
        MemoryUsage nonHeapUsage = memoryMxBean.getNonHeapMemoryUsage();

        System.out.println("堆内存:");
        System.out.println("  已用: " + formatBytes(heapUsage.getUsed()));
        System.out.println("  最大: " + formatBytes(heapUsage.getMax()));
        System.out.println("  使用率: " + (heapUsage.getUsed() * 100.0 / heapUsage.getMax()) + "%");

        System.out.println("非堆内存:");
        System.out.println("  已用: " + formatBytes(nonHeapUsage.getUsed()));
        System.out.println("  最大: " + formatBytes(nonHeapUsage.getMax()));
    }

    public static void monitorGC() {
        List<GarbageCollectorMXBean> gcBeans = ManagementFactory.getGarbageCollectorMXBeans();

        for (GarbageCollectorMXBean gcBean : gcBeans) {
            long count = gcBean.getCollectionCount();
            long time = gcBean.getCollectionTime();

            System.out.println(gcBean.getName() + ":");
            System.out.println("  GC次数: " + count);
            System.out.println("  GC时间: " + time + "ms");
        }
    }

    public static void monitorThreads() {
        ThreadMXBean threadBean = ManagementFactory.getThreadMXBean();

        System.out.println("线程数:");
        System.out.println("  总数: " + threadBean.getThreadCount());
        System.out.println("  峰值: " + threadBean.getPeakThreadCount());
        System.out.println("  守护线程: " + threadBean.getDaemonThreadCount());

        // 检测死锁
        long[] deadlockedThreads = threadBean.findDeadlockedThreads();
        if (deadlockedThreads.length > 0) {
            System.out.println("检测到死锁线程:");
            for (long threadId : deadlockedThreads) {
                ThreadInfo threadInfo = threadBean.getThreadInfo(threadId);
                System.out.println("  " + threadInfo.getThreadName());
            }
        }
    }

    public static void monitorClasses() {
        ClassLoadingMXBean classLoadingBean = ManagementFactory.getClassLoadingMXBean();

        System.out.println("类加载:");
        System.out.println("  已加载类数: " + classLoadingBean.getTotalLoadedClassCount());
        System.out.println("  当前加载类数: " + classLoadingBean.getLoadedClassCount());
        System.out.println("  已卸载类数: " + classLoadingBean.getUnloadedClassCount());
    }

    public static void createHeapDump() {
        HotSpotDiagnosticMXBean diagnosticMxBean = ManagementFactory.getPlatformMXBean(
            HotSpotDiagnosticMXBean.class);

        try {
            diagnosticMxBean.dumpHeap("/tmp/heap_dump.hprof", true);
            System.out.println("Heap dump 已创建");
        } catch (IOException e) {
            System.err.println("创建 Heap dump 失败: " + e.getMessage());
        }
    }

    private static String formatBytes(long bytes) {
        if (bytes < 1024) {
            return bytes + " B";
        } else if (bytes < 1024 * 1024) {
            return String.format("%.2f KB", bytes / 1024.0);
        } else if (bytes < 1024 * 1024 * 1024) {
            return String.format("%.2f MB", bytes / (1024.0 * 1024));
        } else {
            return String.format("%.2f GB", bytes / (1024.0 * 1024 * 1024));
        }
    }

    public static void main(String[] args) {
        System.out.println("=== JVM 监控 ===");

        monitorMemory();
        System.out.println();

        monitorGC();
        System.out.println();

        monitorThreads();
        System.out.println();

        monitorClasses();

        // createHeapDump();
    }
}
```

## 二、数据库性能优化

### 1. SQL 优化

```java
// 使用 MyBatis Plus 批量操作
@Service
public class ProductBatchService {

    private final ProductMapper productMapper;

    // 批量插入
    @Transactional
    public void batchInsert(List<Product> products) {
        // 分批插入，每批 100 条
        int batchSize = 100;
        for (int i = 0; i < products.size(); i += batchSize) {
            int end = Math.min(i + batchSize, products.size());
            List<Product> batch = products.subList(i, end);
            productMapper.insertBatch(batch);
        }
    }

    // 批量更新
    @Transactional
    public void batchUpdateStock(Map<Long, Integer> stockChanges) {
        // 方式1: 单条更新（性能差）
        // stockChanges.forEach((productId, quantity) -> {
        //     productMapper.updateStock(productId, quantity);
        // });

        // 方式2: 使用 CASE WHEN（性能好）
        productMapper.batchUpdateStock(stockChanges);
    }

    // 使用 SQL 优化查询
    public Page<Product> searchOptimized(ProductSearchQuery query) {
        Pageable pageable = PageRequest.of(query.getPage() - 1, query.getSize());

        // 使用 QueryWrapper 优化
        LambdaQueryWrapper<Product> wrapper = new LambdaQueryWrapper<>();
        wrapper.select(
            Product::getId,
            Product::getProductNo,
            Product::getName,
            Product::getPrice,
            Product::getStock
        );

        // 只查询必要的字段
        if (StringUtils.hasText(query.getKeyword())) {
            wrapper.like(Product::getName, query.getKeyword(), SqlLike.LEFT)
                .or()
                .like(Product::getProductNo, query.getKeyword(), SqlLike.LEFT);
        }

        if (query.getMinPrice() != null) {
            wrapper.ge(Product::getPrice, query.getMinPrice());
        }
        if (query.getMaxPrice() != null) {
            wrapper.le(Product::getPrice, query.getMaxPrice());
        }

        if (query.getOnSale() != null) {
            wrapper.eq(Product::getOnSale, query.getOnSale());
        }

        wrapper.orderByDesc(Product::getSales);

        return productMapper.selectPage(wrapper, pageable);
    }
}

// Mapper XML 优化
/*
<mapper namespace="com.example.mapper.ProductMapper">

    <select id="selectListOptimized" resultType="com.example.entity.Product">
        SELECT
            id, product_no, name, price, stock, sales
        FROM t_product
        WHERE 1=1
        <if test="keyword != null and keyword != ''">
            AND (name LIKE CONCAT('%', #{keyword}, '%')
                 OR product_no LIKE CONCAT('%', #{keyword}, '%'))
        </if>
        <if test="minPrice != null">
            AND price >= #{minPrice}
        </if>
        <if test="maxPrice != null">
            AND price <= #{maxPrice}
        </if>
        <if test="onSale != null">
            AND on_sale = #{onSale}
        </if>
        ORDER BY sales DESC
        LIMIT #{size} OFFSET #{offset}
    </select>

    <update id="batchUpdateStock">
        UPDATE t_product
        SET stock = stock +
        <trim prefix="CASE " suffix=" ELSE 0 END">
            <foreach collection="stockChanges" item="productId">
                WHEN id = #{item.productId} THEN -#{item.quantity}
            </foreach>
        </trim>
        WHERE id IN
        <foreach collection="stockChanges" item="productId" separator=",">
            #{item.productId}
        </foreach>
    </update>

</mapper>
*/
```

### 2. 索引优化

```sql
-- 1. 分析查询，创建合适的索引

-- 单列索引
CREATE INDEX idx_username ON t_user(username);
CREATE INDEX idx_email ON t_user(email);

-- 复合索引（注意最左前缀原则）
CREATE INDEX idx_user_age_status ON t_user(age, status);
CREATE INDEX idx_order_user_status ON t_order(user_id, status);

-- 覆盖索引（包含查询所需的所有字段）
CREATE INDEX idx_order_cover ON t_order(user_id, status, total_amount, paid_at);

-- 唯一索引
CREATE UNIQUE INDEX uk_product_no ON t_product(product_no);

-- 全文索引
CREATE FULLTEXT INDEX idx_content ON t_article(content);

-- 2. 索引优化技巧

-- 避免索引失效
-- 不要在索引列上使用函数
-- 错误：WHERE DATE(created_at) = '2024-01-01'
-- 正确：WHERE created_at >= '2024-01-01' AND created_at < '2024-01-02'

-- 避免隐式转换
-- 错误：WHERE user_id = '1'  -- user_id 是 bigint 类型
-- 正确：WHERE user_id = 1

-- 使用前缀索引
CREATE INDEX idx_name_prefix ON t_user(name(10));

-- 哈希索引（解决 LIKE 左模糊查询）
CREATE INDEX idx_name_hash ON t_user(HASH(name));

-- 3. 分析慢查询

-- 开启慢查询日志
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;  -- 超过2秒的查询
SET GLOBAL slow_query_log_file = '/var/log/mysql/slow.log';

-- 分析慢查询
EXPLAIN SELECT * FROM t_order WHERE user_id = 12345;
EXPLAIN ANALYZE SELECT * FROM t_order WHERE user_id = 12345;

-- 查看索引使用情况
SHOW INDEX FROM t_user;
SHOW INDEX FROM t_product;

-- 查看表的统计信息
SHOW TABLE STATUS LIKE 't_user';

-- 更新统计信息
ANALYZE TABLE t_user;
OPTIMIZE TABLE t_user;
```

### 3. 连接池配置

```java
@Configuration
public class DataSourceConfig {

    @Bean
    @ConfigurationProperties(prefix = "spring.datasource.hikari")
    public DataSource dataSource() {
        HikariDataSource ds = new HikariDataSource();

        // 连接池配置
        ds.setPoolName("app-pool");
        ds.setMinimumIdle(5);
        ds.setMaximumPoolSize(20);
        ds.setIdleTimeout(60000);  // 空闲超时（毫秒）
        ds.setConnectionTimeout(30000);  // 连接超时
        ds.setMaxLifetime(1800000);  // 连接最大生命周期（30分钟）
        ds.setConnectionTestQuery("SELECT 1");  // 连接测试查询
        ds.setValidationTimeout(5000);  // 验证超时

        // 性能优化
        ds.setAutoCommit(false);  // 手动提交
        ds.setReadOnly(false);  // 非只读
        ds.setRegisterMbeans(true);  // 注册 JMX

        return ds;
    }

    @Bean
    public JdbcTemplate jdbcTemplate(DataSource dataSource) {
        return new JdbcTemplate(dataSource);
    }
}

// application.yml 配置
/*
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/mydb?useSSL=false&serverTimezone=UTC
    username: root
    password: password
    driver-class-name: com.mysql.cj.jdbc.Driver
    hikari:
      pool-name: app-pool
      minimum-idle: 5
      maximum-pool-size: 20
      idle-timeout: 60000
      max-lifetime: 1800000
      connection-timeout: 30000
      validation-timeout: 5000
      connection-test-query: SELECT 1
      leak-detection-threshold: 30000
*/
```

## 三、缓存优化

### 1. 多级缓存

```java
@Configuration
@EnableCaching
public class CacheConfig {

    @Bean
    public CacheManager cacheManager(RedisConnectionFactory redisConnectionFactory) {
        RedisCacheConfiguration redisConfig = RedisCacheConfiguration.defaultCacheConfig()
            .entryTtl(Duration.ofMinutes(30))
            .serializeKeysWith(RedisSerializationContext.SerializationPair.fromSerializer(
                new StringRedisSerializer()))
            .serializeValuesWith(RedisSerializationContext.SerializationPair.fromSerializer(
                new Jackson2JsonRedisSerializer<>(Object.class)
            ))
            .disableCachingNullValues();

        // L1: Caffeine（本地缓存）
        CaffeineCacheManager caffeineCacheManager = new CaffeineCacheManager();
        CaffeineCache<Object, Object> caffeineCache = Caffeine.newBuilder()
            .expireAfterWrite(5, TimeUnit.MINUTES)
            .maximumSize(1000)
            .recordStats()
            .build();

        // L2: Redis（分布式缓存）
        RedisCacheManager redisCacheManager = RedisCacheManager.builder(redisConnectionFactory)
            .cacheDefaults(redisConfig)
            .transactionAware()
            .build();

        // 组合缓存
        CompositeCacheManager compositeCacheManager = new CompositeCacheManager(
            caffeineCacheManager,
            redisCacheManager
        );

        return compositeCacheManager;
    }

    @Bean
    public KeyGenerator customKeyGenerator() {
        return (target, method, params) -> {
            String className = target.getClass().getSimpleName();
            String methodName = method.getName();
            String key = className + ":" + methodName + ":";

            // 根据方法参数生成 Key
            if (params.length == 0) {
                return key + "0";
            }

            key += DigestUtils.md5Hex(Arrays.toString(params));
            return key;
        };
    }
}

// 多级缓存使用
@Service
@Slf4j
public class MultiCacheService {

    @Autowired
    private CacheManager cacheManager;

    @Cacheable(
        value = {"products", "product-detail"},
        cacheResolver = "multiCacheResolver",
        keyGenerator = "customKeyGenerator"
    )
    public Product getProduct(Long productId) {
        log.info("从数据库查询产品: {}", productId);
        return productRepository.findById(productId).orElse(null);
    }

    @CacheEvict(value = {"products", "product-detail"}, allEntries = true)
    public void clearAllProductCache() {
        log.info("清除所有产品缓存");
    }
}
```

### 2. 缓存穿透、击穿、雪崩

```java
@Service
public class CacheProtectionService {

    private final ProductRepository productRepository;
    private final StringRedisTemplate stringRedisTemplate;

    // 缓存穿透（布隆过滤器 + 空值缓存）
    public Product getProductWithBloomFilter(Long productId) {
        // 1. 布隆过滤器检查
        if (!bloomFilter.mightContain(productId)) {
            // 不存在，直接返回
            return null;
        }

        // 2. 查询缓存
        String cacheKey = "product:" + productId;
        Object cached = stringRedisTemplate.opsForValue().get(cacheKey);
        if (cached != null) {
            if ("NULL".equals(cached)) {
                // 空值缓存，说明数据不存在
                return null;
            }
            return (Product) cached;
        }

        // 3. 查询数据库
        Product product = productRepository.findById(productId).orElse(null);

        // 4. 写入缓存
        if (product != null) {
            stringRedisTemplate.opsForValue().set(cacheKey, product, 1, TimeUnit.HOURS);
        } else {
            // 缓存空值（防止穿透）
            stringRedisTemplate.opsForValue().set(cacheKey, "NULL", 5, TimeUnit.MINUTES);
        }

        // 5. 更新布隆过滤器
        bloomFilter.put(productId);

        return product;
    }

    // 缓存击穿（加锁）
    public Product getProductWithLock(Long productId) {
        String cacheKey = "product:" + productId;

        // 1. 查询缓存
        Object cached = stringRedisTemplate.opsForValue().get(cacheKey);
        if (cached != null) {
            return (Product) cached;
        }

        // 2. 使用分布式锁
        String lockKey = "lock:product:" + productId;
        RLock lock = redissonClient.getLock(lockKey);

        try {
            // 获取锁
            boolean acquired = lock.tryLock(10, 30, TimeUnit.SECONDS);
            if (!acquired) {
                throw new BusinessException("系统繁忙，请稍后重试");
            }

            // 双重检查
            cached = stringRedisTemplate.opsForValue().get(cacheKey);
            if (cached != null) {
                return (Product) cached;
            }

            // 3. 查询数据库
            Product product = productRepository.findById(productId).orElse(null);

            // 4. 写入缓存
            if (product != null) {
                stringRedisTemplate.opsForValue().set(cacheKey, product, 1, TimeUnit.HOURS);
            }

            return product;

        } finally {
            lock.unlock();
        }
    }

    // 缓存雪崩（互斥锁 + 熔断降级）
    @Cacheable(value = "products", key = "#productId")
    public Product getProductWithCircuitBreaker(Long productId) {
        // 正常逻辑
        return productRepository.findById(productId).orElse(null);
    }

    // 缓存降级
    public Product getProductWithFallback(Long productId) {
        String cacheKey = "product:" + productId;

        try {
            // 1. 尝试从 Redis 获取
            Product cached = (Product) stringRedisTemplate.opsForValue().get(cacheKey);
            if (cached != null) {
                return cached;
            }

            // 2. 使用互斥锁防止雪崩
            String lockKey = "lock:cache:" + productId;
            RLock lock = redissonClient.getLock(lockKey);

            if (lock.tryLock(100, 10, TimeUnit.MILLISECONDS)) {
                try {
                    // 3. 从数据库查询
                    Product product = productRepository.findById(productId).orElse(null);

                    if (product != null) {
                        // 4. 写入缓存，设置随机过期时间
                        long randomExpire = ThreadLocalRandom.current().nextLong(3000, 10000);
                        stringRedisTemplate.opsForValue().set(cacheKey, product,
                            randomExpire, TimeUnit.MILLISECONDS);
                    }

                    return product;

                } finally {
                    lock.unlock();
                }
            }

            // 5. 降级：返回默认商品或从另一个数据源获取
            return getFromBackup(productId);

        } catch (Exception e) {
            log.error("查询商品异常: productId={}", productId, e);
            return getDefaultProduct();
        }
    }

    private Product getFromBackup(Long productId) {
        // 从备份数据源查询
        // ...
        return null;
    }

    private Product getDefaultProduct() {
        // 返回默认商品
        return Product.builder()
            .id(-1L)
            .name("商品暂时无法显示")
            .build();
    }
}
```

### 3. 缓存预热

```java
@Component
@Slf4j
public class CacheWarmupService implements ApplicationRunner {

    private final ProductService productService;
    private final RedisTemplate<String, Object> redisTemplate;

    @Override
    public void run(ApplicationArguments args) {
        log.info("开始缓存预热...");

        // 预热热门商品
        warmUpHotProducts();

        // 预热用户信息
        warmUpUsers();

        // 预热商品分类
        warmUpCategories();

        log.info("缓存预热完成");
    }

    private void warmUpHotProducts() {
        try {
            List<Long> hotProductIds = productService.getHotProductIds(100);

            for (Long productId : hotProductIds) {
                Product product = productService.getProduct(productId);
                if (product != null) {
                    String cacheKey = "product:" + productId;
                    redisTemplate.opsForValue().set(cacheKey, product, 24, TimeUnit.HOURS);
                }
            }

            log.info("热门商品预热完成，数量: {}", hotProductIds.size());

        } catch (Exception e) {
            log.error("热门商品预热失败", e);
        }
    }

    private void warmUpUsers() {
        // 预热用户信息
        // ...
    }

    private void warmUpCategories() {
        // 预热商品分类
        // ...
    }
}
```

## 四、并发优化

### 1. 异步处理

```java
@Service
@Slf4j
public class AsyncOrderService {

    private final OrderRepository orderRepository;
    private final NotificationService notificationService;
    private final AnalyticsService analyticsService;

    @Async("orderExecutor")
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public CompletableFuture<Void> processOrderAsync(Order order) {
        return CompletableFuture.runAsync(() -> {
            log.info("异步处理订单: {}", order.getId());

            try {
                // 发送通知
                notificationService.sendOrderNotification(order);

                // 更新统计
                analyticsService.updateOrderStats(order);

            } catch (Exception e) {
                log.error("订单异步处理失败: {}", order.getId(), e);
                throw e;
            }
        });
    }

    @Async("orderExecutor")
    public CompletableFuture<Void> sendNotificationsAsync(Long orderId, List<Long> userIds) {
        return CompletableFuture.runAsync(() -> {
            log.info("异步发送通知: orderId={}, 用户数={}", orderId, userIds.size());

            userIds.forEach(userId -> {
                notificationService.sendOrderNotification(userId, orderId);
            });
        });
    }

    // 并行处理多个任务
    public CompletableFuture<OrderProcessResult> processOrder(Order order) {
        CompletableFuture<Boolean> inventoryCheck = CompletableFuture.supplyAsync(() ->
            inventoryService.checkStock(order.getProductId(), order.getQuantity())
        );

        CompletableFuture<Boolean> paymentCheck = CompletableFuture.supplyAsync(() ->
            paymentService.validatePayment(order.getTotalAmount())
        );

        CompletableFuture<Boolean> userCheck = CompletableFuture.supplyAsync(() ->
            userService.validateUser(order.getUserId())
        );

        // 等待所有检查完成
        CompletableFuture.allOf(inventoryCheck, paymentCheck, userCheck).join();

        boolean allPassed = inventoryCheck.get() && paymentCheck.get() && userCheck.get();

        if (allPassed) {
            return OrderProcessResult.success();
        } else {
            return OrderProcessResult.failure("前置条件不满足");
        }
    }

    @Bean
    public Executor orderExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(5);
        executor.setMaxPoolSize(20);
        executor.setQueueCapacity(100);
        executor.setThreadNamePrefix("order-");
        executor.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
        executor.initialize();
        return executor;
    }
}
```

### 2. 批量处理

```java
@Service
@Slf4j
public class BatchProcessingService {

    private final UserRepository userRepository;

    // 并发处理用户
    @Async
    public CompletableFuture<List<User>> processUsersInParallel(List<Long> userIds) {
        return CompletableFuture.supplyAsync(() -> {
            List<User> results = Collections.synchronizedList(new ArrayList<>());

            // 创建线程池
            ExecutorService executor = Executors.newFixedThreadPool(10);

            List<CompletableFuture<Void>> futures = new ArrayList<>();

            for (Long userId : userIds) {
                CompletableFuture<Void> future = CompletableFuture.runAsync(() -> {
                    try {
                        User user = userRepository.findById(userId).orElse(null);
                        if (user != null) {
                            // 处理用户
                            processUser(user);
                            results.add(user);
                        }
                    } catch (Exception e) {
                        log.error("处理用户失败: userId={}", userId, e);
                    }
                }, executor);
                futures.add(future);
            }

            // 等待所有任务完成
            CompletableFuture.allOf(futures.toArray(new CompletableFuture[0])).join();

            executor.shutdown();

            return results;
        });
    }

    // 批量插入优化
    @Transactional
    public void batchInsertOptimized(List<User> users) {
        if (users.isEmpty()) {
            return;
        }

        // 方式1: MyBatis 批量插入
        userRepository.insertBatch(users);

        // 方式2: 使用 INSERT VALUES ON DUPLICATE KEY UPDATE
        userRepository.batchInsertWithIgnore(users);

        // 方式3: 使用 LOAD DATA INFILE（最快）
        // userRepository.batchImport(users);
    }

    // 分片处理
    public void processInBatches(List<Long> ids, int batchSize) {
        List<List<Long>> batches = Lists.partition(ids, batchSize);

        for (List<Long> batch : batches) {
            processBatch(batch);
        }
    }

    private void processBatch(List<Long> batch) {
        // 处理一批数据
        batch.forEach(id -> {
            // 处理逻辑
        });
    }
}
```

## 小结

本节学习了性能优化：

- **JVM 调优** - 内存模型、GC 算法、参数配置、监控工具
- **数据库优化** - SQL 优化、索引设计、连接池
- **缓存优化** - 多级缓存、穿透/击穿/雪崩、预热
- **并发优化** - 异步处理、批量处理、线程池

## 实践练习

### 编程题
1. 对一个慢查询 SQL 进行优化：使用 EXPLAIN 分析执行计划，添加合适的索引，将查询时间从 5 秒降到 50ms 以内。
2. 使用 JMeter 对一个 Spring Boot 接口进行压测，分别测试不同并发量下的响应时间，找出性能瓶颈并优化。

### 思考题
1. 数据库读写分离后，如何解决主从延迟导致的数据不一致问题？
2. 单表数据量过亿后，有哪些分库分表策略？垂直拆分和水平拆分各适合什么场景？

### 自测题
1. EXPLAIN 执行计划中，type 字段的访问类型从好到差如何排序？
2. 常见 SQL 优化策略有哪些（至少 5 条）？
3. 缓存和数据库双写一致性的解决方案？

下一步将学习部署和监控（→ `README.md`）。