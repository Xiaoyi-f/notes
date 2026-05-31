# Java 全栈速查表

## Java 基础速查

| 知识点 | 要点 |
|--------|------|
| 八大基本类型 | byte(1) short(2) int(4) long(8) float(4) double(8) char(2) boolean |
| OOP 四大特性 | 封装、继承、多态、抽象 |
| 接口 vs 抽象类 | 接口：多实现、默认方法(Java8+)；抽象类：单继承、可有构造器 |
| 重载 vs 重写 | 重载：同名不同参(编译期)；重写：子类覆盖父类方法(运行期) |
| String vs StringBuilder | String 不可变(常量池)；StringBuilder 可变(非线程安全)；StringBuffer 线程安全 |
| == vs equals() | == 比较引用地址；equals() 比较内容(需重写) |

## 集合框架速查

| 类型 | 实现 | 特点 | 线程安全版 |
|------|------|------|-----------|
| List | ArrayList | 数组实现，O(1)查询，O(n)增删 | CopyOnWriteArrayList |
| List | LinkedList | 链表实现，O(n)查询，O(1)增删 | - |
| Set | HashSet | 哈希表，O(1)操作，无序 | Collections.synchronizedSet |
| Set | TreeSet | 红黑树，O(log n)，有序 | - |
| Map | HashMap | 哈希表，O(1)，允许 null | ConcurrentHashMap |
| Map | TreeMap | 红黑树，有序 | - |

## 并发编程速查

### 线程创建
```java
new Thread(() -> { ... }).start();                          // Runnable + Lambda
ExecutorService pool = Executors.newFixedThreadPool(10);    // 线程池
CompletableFuture.supplyAsync(() -> result);                // 异步
```

### 锁与同步
| 机制 | 特点 |
|------|------|
| synchronized | JVM 内置，自动释放，非公平锁 |
| ReentrantLock | API 级别，手动释放，可公平、可中断、可超时 |
| ReadWriteLock | 读读共享，读写互斥 |
| CountDownLatch | 一个线程等多个线程完成 |
| CyclicBarrier | 多个线程互相等待 |
| Semaphore | 控制并发访问数量 |

### 线程池参数
```java
new ThreadPoolExecutor(
    corePoolSize,      // 核心线程数
    maxPoolSize,       // 最大线程数
    keepAliveTime,     // 空闲线程存活时间
    unit,              // 时间单位
    workQueue,         // 任务队列
    handler            // 拒绝策略(Abort/CallerRuns/Discard/DiscardOldest)
);
```

## JVM 速查

### 内存区域
| 区域 | 共享 | 内容 | OOM |
|------|------|------|-----|
| 堆(Heap) | 线程共享 | 对象实例 | ✅ |
| 方法区(Metaspace) | 线程共享 | 类信息、常量池 | ✅ |
| 虚拟机栈 | 线程私有 | 栈帧(局部变量/操作数栈) | ✅ StackOverflow |
| 程序计数器 | 线程私有 | 指令地址 | ❌ |
| 本地方法栈 | 线程私有 | Native 方法 | ✅ |

### GC 算法
| 算法 | 过程 | 优缺点 |
|------|------|--------|
| 标记-清除 | 标记→清除 | 简单，有碎片 |
| 标记-整理 | 标记→移动到一端 | 无碎片，效率低 |
| 复制 | 复制到另一块 | 快，浪费空间 |
| 分代收集 | 新生代用复制，老年代用标记-整理 | 综合最优 |

### GC 收集器
| 收集器 | 特点 | 推荐场景 |
|--------|------|----------|
| Serial | 单线程 | 小内存/单核 |
| Parallel | 多线程，高吞吐 | 批处理 |
| CMS | 低停顿，并发 | 响应时间敏感 |
| G1 | 可预测停顿，分 Region | JDK 9+ 默认 |
| ZGC | 超低延迟(<10ms)，TB级堆 | 大内存低延迟 |

## Spring 全家桶速查

### 核心注解
| 注解 | 作用 |
|------|------|
| `@SpringBootApplication` | @Configuration + @EnableAutoConfiguration + @ComponentScan |
| `@Autowired` | 自动装配(byType→byName) |
| `@Transactional` | 事务管理(propagation/isolation/rollbackFor) |
| `@Aspect` | 声明切面 |
| `@Value` vs `@ConfigurationProperties` | 单个 vs 批量属性绑定 |

### Bean 生命周期
```
实例化 → 属性注入(@Autowired) → 初始化(@PostConstruct) → 使用 → 销毁(@PreDestroy)
```

### AOP 通知类型
```
@Around(环绕) → @Before(前置) → 方法执行 → @Around(后) → @AfterReturning/@AfterThrowing → @After(后置)
```

## 中间件速查

| 组件 | 核心用途 | 关键配置 |
|------|----------|----------|
| Redis | 缓存/分布式锁/排行榜 | 持久化(RDB/AOF)、淘汰策略 |
| RocketMQ | 异步解耦/削峰 | NameServer、Producer Group、Consumer Group |
| Nacos | 注册中心+配置中心 | 服务注册、配置刷新(@RefreshScope) |
| Sentinel | 流量控制/熔断降级 | QPS 限流、热点参数、系统规则 |
| MyBatis Plus | ORM | CRUD 自动生成、分页插件、逻辑删除 |

## 系统设计速查

| 场景 | 核心技术方案 |
|------|------------|
| 秒杀系统 | Redis 预减库存 + MQ 异步下单 + 限流 |
| 短链接 | 发号器 + Base62 + 301 重定向 + 布隆过滤器 |
| 分布式 ID | 雪花算法(Snowflake)、号段模式 |
| 分布式锁 | Redis SET NX + Lua 解锁、Redisson |
| 分布式事务 | Seata(AT/TCC/Saga)、MQ 最终一致性 |
| API 网关 | 路由、限流、认证、日志 |

## 面试高频 15 问

1. HashMap 原理？数组+链表+红黑树，扩容因子 0.75
2. ConcurrentHashMap 如何保证线程安全？CAS + synchronized 锁链表头
3. synchronized 和 Lock 区别？synchronized 自动释放，Lock 更灵活
4. 线程池工作原理？核心线程→队列→最大线程→拒绝策略
5. JVM 内存模型？堆、方法区、虚拟机栈、程序计数器、本地方法栈
6. CMS 和 G1 区别？CMS 标记清除有碎片，G1 分区可预测停顿
7. Spring IoC/AOP 原理？IoC 控制反转(DI 实现)，AOP 动态代理
8. Spring Boot 自动配置原理？@EnableAutoConfiguration → spring.factories → @Conditional
9. @Transactional 失效场景？非 public、内部调用、异常被捕获
10. Redis 缓存穿透/击穿/雪崩？穿透:布隆过滤器，击穿:互斥锁，雪崩:随机过期
11. MQ 如何保证消息不丢？生产确认+持久化+消费 Ack
12. 分布式事务方案？2PC、TCC、Saga、可靠消息最终一致性
13. MySQL 索引优化？最左前缀、覆盖索引、避免函数和隐式转换
14. CAP 理论？一致性、可用性、分区容错，最多同时满足两个
15. 微服务优缺点？独立部署扩展，但分布式复杂、运维成本高
