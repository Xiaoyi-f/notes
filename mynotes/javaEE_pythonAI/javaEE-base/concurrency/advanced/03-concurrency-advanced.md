# Java 并发高级专题

## 一、概述

深入并发底层：JMM 内存模型、锁优化、无锁数据结构、Disruptor、协程（虚拟线程）、性能基准测试。

## 二、Java 内存模型 (JMM)

### 内存模型结构

```
Thread A                     Thread B
    |                            |
    V                            V
┌──────────┐              ┌──────────┐
│ 工作内存  │              │ 工作内存  │
│ (本地缓存)│              │ (本地缓存)│
└─────┬────┘              └────┬─────┘
      │                        │
      └──────────┬─────────────┘
                 │
          ┌──────▼──────┐
          │   主内存     │
          │ (堆)         │
          └─────────────┘
```

### Happens-Before 规则

| 规则 | 说明 |
|------|------|
| 程序次序规则 | 同一线程中，写在前面的操作 happens-before 后面的操作 |
| 管程锁定规则 | unlock happens-before 后续的 lock |
| volatile 规则 | volatile 写 happens-before 后续的读 |
| 线程启动规则 | Thread.start() happens-before 线程中的任何操作 |
| 线程终止规则 | 线程中的所有操作 happens-before 其他线程检测到该线程终止 |
| 中断规则 | 调用 interrupt happens-before 检测到中断事件 |
| 终结器规则 | 对象构造完成 happens-before finalize 开始 |
| 传递性 | A happens-before B, B happens-before C ⇒ A happens-before C |

### 内存屏障

```java
public class MemoryBarrierExample {
    private int x = 0;
    private volatile boolean flag = false;  // volatile 实现内存屏障

    public void writer() {
        x = 42;              // StoreStore 屏障
        flag = true;         // StoreLoad 屏障
    }

    public void reader() {
        if (flag) {          // LoadLoad 屏障
            int r = x;       // 保证看到 x = 42
        }
    }
}

// Unsafe 手动屏障
public class UnsafeBarrier {
    private static final Unsafe U = Unsafe.getUnsafe();

    public void fullFence() {
        U.fullFence();          // 全屏障
    }

    public void loadFence() {
        U.loadFence();          // LoadLoad + LoadStore
    }

    public void storeFence() {
        U.storeFence();         // StoreStore + StoreLoad
    }
}
```

## 三、锁优化技术

### 锁消除

```java
// JIT 编译时会消除没有竞争的锁
public String concatString(String s1, String s2, String s3) {
    // StringBuffer 是局部变量，不会被其他线程访问
    StringBuffer sb = new StringBuffer();
    sb.append(s1);  // 锁被 JIT 消除
    sb.append(s2);
    sb.append(s3);
    return sb.toString();
}
```

### 锁粗化

```java
// JIT 将多次加锁合并为一次
public void appendStrings(StringBuffer sb, List<String> list) {
    for (String s : list) {
        // JIT 会将循环内的锁粗化到循环外
        sb.append(s);
    }
}
```

### 读写锁

```java
public class Cache<K, V> {
    private final Map<K, V> map = new HashMap<>();
    private final ReentrantReadWriteLock rwLock = new ReentrantReadWriteLock();
    private final Lock rLock = rwLock.readLock();
    private final Lock wLock = rwLock.writeLock();

    public V get(K key) {
        rLock.lock();
        try {
            return map.get(key);
        } finally {
            rLock.unlock();
        }
    }

    public void put(K key, V value) {
        wLock.lock();
        try {
            map.put(key, value);
        } finally {
            wLock.unlock();
        }
    }
}
```

### StampedLock

```java
public class Point {
    private double x, y;
    private final StampedLock sl = new StampedLock();

    // 乐观读（无锁）
    public double distanceFromOrigin() {
        long stamp = sl.tryOptimisticRead();
        double currentX = x, currentY = y;
        if (!sl.validate(stamp)) {  // 被写线程修改过
            stamp = sl.readLock();   // 升级为悲观读锁
            try {
                currentX = x;
                currentY = y;
            } finally {
                sl.unlockRead(stamp);
            }
        }
        return Math.sqrt(currentX * currentX + currentY * currentY);
    }

    // 写操作
    public void move(double deltaX, double deltaY) {
        long stamp = sl.writeLock();
        try {
            x += deltaX;
            y += deltaY;
        } finally {
            sl.unlockWrite(stamp);
        }
    }
}
```

## 四、无锁数据结构

### Lock-Free 栈

```java
public class LockFreeStack<T> {
    private final AtomicReference<Node<T>> top = new AtomicReference<>();

    static class Node<T> {
        final T value;
        Node<T> next;
        Node(T value) { this.value = value; }
    }

    public void push(T value) {
        Node<T> newNode = new Node<>(value);
        while (true) {
            Node<T> currentTop = top.get();
            newNode.next = currentTop;
            if (top.compareAndSet(currentTop, newNode)) return;
        }
    }

    public T pop() {
        while (true) {
            Node<T> currentTop = top.get();
            if (currentTop == null) return null;
            Node<T> newTop = currentTop.next;
            if (top.compareAndSet(currentTop, newTop)) {
                return currentTop.value;
            }
        }
    }
}
```

### 伪共享 (False Sharing)

```java
// 伪共享问题
class Counter {
    public volatile long value1;  // 与 value2 在同一缓存行
    public volatile long value2;  // 不同线程修改，导致缓存行无效
}

// @Contended 注解（JDK 8+）
@sun.misc.Contended
class PaddedCounter {
    public volatile long value1;
}

// 手动填充
class CacheLinePadding {
    public volatile long p1, p2, p3, p4, p5, p6, p7;  // 填充
    public volatile long value = 0;
    public volatile long q1, q2, q3, q4, q5, q6, q7;  // 填充
}
```

## 五、虚拟线程 (JDK 21+)

```java
public class VirtualThreadDemo {
    public static void main(String[] args) throws Exception {
        // 创建虚拟线程
        Thread vt = Thread.startVirtualThread(() -> {
            System.out.println("Virtual thread: " + Thread.currentThread());
        });
        vt.join();

        // 虚拟线程池
        try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
            List<Future<String>> futures = new ArrayList<>();
            for (int i = 0; i < 1000; i++) {
                int taskId = i;
                futures.add(executor.submit(() -> processTask(taskId)));
            }
            for (Future<String> f : futures) {
                f.get();
            }
        }
    }

    // 虚拟线程适合大量 IO 阻塞场景
    static String processTask(int id) {
        try {
            Thread.sleep(100);  // 虚拟线程挂起时释放底层 OS 线程
            return "Done: " + id;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return "Failed: " + id;
        }
    }
}
```

### 虚拟线程 vs 平台线程

| 特性 | 平台线程 | 虚拟线程 |
|------|----------|----------|
| 创建成本 | 高（1MB+ 栈） | 极低（几百字节） |
| 最大数量 | 数千 | 数百万 |
| 阻塞影响 | 阻塞 OS 线程 | 挂起不阻塞 OS |
| 适用场景 | CPU 密集型 | IO 密集型 |
| 池化需求 | 需要线程池 | 不需要池化 |

## 面试考点

1. **JMM 中 volatile 的语义？** 可见性 + 禁止指令重排序（内存屏障）
2. **StampedLock 比 ReadWriteLock 的优势？** 乐观读不阻塞写线程，读多写少场景性能更好
3. **伪共享的危害和解决方案？** 多线程修改同一缓存行的不同变量导致性能骤降；缓存行填充
4. **虚拟线程为什么启动快？** 由 JVM 管理，不映射 OS 线程，栈空间按需增长

## 课后练习

1. 使用 JMH 基准测试对比 synchronized、ReentrantLock、StampedLock 性能
2. 实现一个 Lock-Free 队列，分析其正确性
3. 模拟伪共享场景，用 @Contended 注解解决
4. 使用虚拟线程重写一个高并发 IO 服务，对比平台线程的吞吐量

## 自测题

1. JMM 中哪个规则保证了 volatile 变量写操作的可见性？ A) 程序次序规则 B) volatile 规则 C) 传递性 D) 管程锁定规则
2. StampedLock 的乐观读是什么？ A) 加读锁 B) 不加锁直接读 C) 写锁降级 D) 读锁升级
3. 虚拟线程在 JDK 哪个版本正式发布？ A) 17 B) 19 C) 21 D) 23

**答案：** 1-B, 2-B, 3-C
