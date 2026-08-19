# Java 并发工具与线程池

## 一、概述

深入 JUC 工具类：线程池原理与调优、AQS 框架、ReentrantLock、CountDownLatch、CyclicBarrier、Semaphore、CompletableFuture。

## 二、线程池

### 核心参数

```java
ThreadPoolExecutor executor = new ThreadPoolExecutor(
    5,                      // corePoolSize: 核心线程数
    10,                     // maximumPoolSize: 最大线程数
    60L,                    // keepAliveTime: 空闲存活时间
    TimeUnit.SECONDS,       // 时间单位
    new ArrayBlockingQueue<>(100),  // workQueue: 阻塞队列
    Executors.defaultThreadFactory(), // threadFactory: 线程工厂
    new ThreadPoolExecutor.CallerRunsPolicy() // handler: 拒绝策略
);
```

### 处理流程

```
提交任务
  → 运行线程数 < corePoolSize → 创建新线程
  → 运行线程数 >= corePoolSize → 放入队列
  → 队列满 → 创建新线程（直到 maxPoolSize）
  → 线程数 >= maxPoolSize + 队列满 → 执行拒绝策略
```

### 拒绝策略

| 策略 | 行为 | 适用场景 |
|------|------|----------|
| AbortPolicy (默认) | 抛 RejectedExecutionException | 必须处理的场景 |
| CallerRunsPolicy | 调用者线程执行 | 降级，减缓提交速度 |
| DiscardPolicy | 直接丢弃 | 不重要的任务 |
| DiscardOldestPolicy | 丢弃队列中最旧的任务 | 消息推送等 |

### 线程池监控

```java
public class MonitorThreadPool extends ThreadPoolExecutor {
    private final AtomicInteger submittedTasks = new AtomicInteger(0);
    private final AtomicInteger completedTasks = new AtomicInteger(0);

    @Override
    protected void beforeExecute(Thread t, Runnable r) {
        super.beforeExecute(t, r);
        submittedTasks.incrementAndGet();
    }

    @Override
    protected void afterExecute(Runnable r, Throwable t) {
        super.afterExecute(r, t);
        completedTasks.incrementAndGet();
    }

    public String getMetrics() {
        return String.format(
            "PoolSize=%d, Active=%d, Queued=%d, Completed=%d, Submitted=%d",
            this.getPoolSize(), this.getActiveCount(),
            this.getQueue().size(), this.getCompletedTaskCount(),
            completedTasks.get()
        );
    }

    // 定时输出监控指标
    public void startMonitor(long period, TimeUnit unit) {
        Executors.newSingleThreadScheduledExecutor()
            .scheduleAtFixedRate(() -> log.info(getMetrics()),
               0, period, unit);
    }
}
```

### 线程池大小估算

```java
public class ThreadPoolSizing {
    // CPU 密集型: Ncpu + 1
    public static int cpuIntensive() {
        return Runtime.getRuntime().availableProcessors() + 1;
    }

    // IO 密集型: 2 * Ncpu
    public static int ioIntensive() {
        return 2 * Runtime.getRuntime().availableProcessors();
    }

    // 通用公式
    public static int optimalPoolSize(double targetUtilization, 
                                       double waitRatio, int ncpu) {
        // waitRatio = waitTime / computeTime
        return (int) (ncpu * targetUtilization * (1 + waitRatio));
    }
}
```

## 三、AQS (AbstractQueuedSynchronizer)

### AQS 原理

```
状态变量 state (volatile int)
    ↓
CLH 队列 (双向链表)
    ├── head (当前持有锁的线程)
    └── tail (等待线程)
        ↓
独占模式 (ReentrantLock)
共享模式 (Semaphore, CountDownLatch)
```

### 自定义 AQS 锁

```java
class SharedLock {
    private static class Sync extends AbstractQueuedSynchronizer {
        @Override
        protected boolean tryAcquire(int acquires) {
            if (compareAndSetState(0, acquires)) {
                setExclusiveOwnerThread(Thread.currentThread());
                return true;
            }
            return false;
        }

        @Override
        protected boolean tryRelease(int releases) {
            if (getState() == 0) throw new IllegalMonitorStateException();
            setExclusiveOwnerThread(null);
            setState(0);
            return true;
        }

        @Override
        protected int tryAcquireShared(int acquires) {
            for (;;) {
                int available = getState();
                int remaining = available - acquires;
                if (remaining < 0 || compareAndSetState(available, remaining)) {
                    return remaining;
                }
            }
        }

        @Override
        protected boolean tryReleaseShared(int releases) {
            for (;;) {
                int current = getState();
                int next = current + releases;
                if (compareAndSetState(current, next)) {
                    return true;
                }
            }
        }
    }

    private final Sync sync = new Sync();
    
    public void lock() { sync.acquire(1); }
    public void unlock() { sync.release(1); }
    public boolean tryLock() { return sync.tryAcquire(1); }
}
```

## 四、JUC 工具类

### CountDownLatch

```java
public class BatchProcessor {
    public void processBatch(List<Job> jobs) throws InterruptedException {
        int threadCount = Math.min(jobs.size(), 10);
        CountDownLatch latch = new CountDownLatch(jobs.size());

        for (Job job : jobs) {
            threadPool.submit(() -> {
                try {
                    processJob(job);
                } finally {
                    latch.countDown();  // 每个任务完成后减 1
                }
            });
        }

        latch.await(30, TimeUnit.SECONDS);  // 等待所有完成
        log.info("All jobs completed");
    }
}
```

### CyclicBarrier

```java
public class BatchImportService {
    private final CyclicBarrier barrier;
    private final List<String> batchResults = new ArrayList<>();

    public BatchImportService(int threadCount) {
        this.barrier = new CyclicBarrier(threadCount, () -> {
            // 所有线程到达屏障后执行合并
            mergeResults(batchResults);
            batchResults.clear();
        });
    }

    public void importData(List<String> data) throws Exception {
        for (int i = 0; i < data.size(); i += 100) {
            List<String> batch = data.subList(i, Math.min(i + 100, data.size()));
            threadPool.submit(() -> {
                String result = processBatch(batch);
                synchronized (batchResults) {
                    batchResults.add(result);
                }
                barrier.await();  // 等待所有线程完成当前批次
            });
        }
    }

    private String processBatch(List<String> batch) { /* ... */ return "ok"; }
    private void mergeResults(List<String> results) { /* ... */ }
}
```

### Semaphore

```java
@Service
public class RateLimitedService {
    private final Semaphore semaphore = new Semaphore(10, true);  // 公平

    public void processRequest(Request request) {
        if (!semaphore.tryAcquire(5, TimeUnit.SECONDS)) {
            throw new BusyException("Server busy, please retry");
        }
        try {
            handleRequest(request);
        } finally {
            semaphore.release();
        }
    }
}
```

## 五、CompletableFuture

```java
@Service
public class OrderQueryService {
    @Autowired
    private UserService userService;
    @Autowired
    private StockService stockService;
    @Autowired
    private PriceService priceService;

    public CompletableFuture<OrderDetail> getOrderDetail(Long orderId) {
        // 并行查询三个服务
        CompletableFuture<UserVO> userFuture = 
            CompletableFuture.supplyAsync(() -> userService.getUser(orderId));
        CompletableFuture<StockVO> stockFuture = 
            CompletableFuture.supplyAsync(() -> stockService.getStock(orderId));
        CompletableFuture<PriceVO> priceFuture = 
            CompletableFuture.supplyAsync(() -> priceService.getPrice(orderId));

        // 三个都完成后再聚合
        return CompletableFuture.allOf(userFuture, stockFuture, priceFuture)
            .thenApplyAsync(v -> {
                UserVO user = userFuture.join();
                StockVO stock = stockFuture.join();
                PriceVO price = priceFuture.join();
                return new OrderDetail(orderId, user, stock, price);
            })
            .exceptionally(ex -> {
                log.error("Failed to get order detail", ex);
                return OrderDetail.empty(orderId);
            })
            .orTimeout(5, TimeUnit.SECONDS)
            .exceptionally(ex -> {
                log.warn("Query timeout for order: {}", orderId);
                return OrderDetail.timeout(orderId);
            });
    }
}
```

## 面试考点

1. **线程池 submit() 和 execute() 的区别？** submit 返回 Future，execute 返回 void
2. **如何合理设置线程池大小？** CPU 密集型 N+1，IO 密集型 2N，通用公式 N * targetUtilization * (1 + wait/compute)
3. **CountDownLatch 和 CyclicBarrier 的区别？** Latch 一次性、await 等待计数归零；Barrier 可循环、await 等待所有线程到达
4. **CompletableFuture 的 thenApply 和 thenCompose 区别？** thenApply 展平为 CompletableFuture<U>，thenCompose 保持 CompletableFuture<CompletableFuture<U>>

## 课后练习

1. 实现一个可动态调整大小（resize）的线程池
2. 使用 CompletableFuture 实现多服务并行调用 + 超时 + 降级
3. 使用 CyclicBarrier 实现多阶段并行计算任务
4. 基于 AQS 实现一个独占锁和共享锁

## 自测题

1. ThreadPoolExecutor 中 CallerRunsPolicy 的执行者是？ A) 提交任务的线程 B) 线程池中的线程 C) 新创建的线程 D) 主线程
2. AQS 使用什么数据结构管理等待线程？ A) 数组 B) 链表 C) CLH 队列 D) 红黑树
3. CompletableFuture.allOf 返回的是什么？ A) 第一个完成的结果 B) 所有结果列表 C) CompletableFuture<Void> D) 最后一个完成的结果

**答案：** 1-A, 2-C, 3-C
