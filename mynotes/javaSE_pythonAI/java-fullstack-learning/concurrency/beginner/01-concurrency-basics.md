# Java 并发编程基础

## 一、概述

并发编程是 Java 后端开发的核心能力。掌握线程基础、锁机制、volatile 语义、synchronized 原理、CAS 无锁编程。

## 二、线程基础

### 创建线程三种方式

```java
// 1. 继承 Thread
class MyThread extends Thread {
    @Override
    public void run() {
        System.out.println("Thread: " + Thread.currentThread().getName());
    }
}
new MyThread().start();

// 2. 实现 Runnable（推荐）
class MyTask implements Runnable {
    @Override
    public void run() {
        System.out.println("Runnable: " + Thread.currentThread().getName());
    }
}
new Thread(new MyTask()).start();

// 3. FutureTask + Callable（带返回值）
class MyCallable implements Callable<String> {
    @Override
    public String call() throws Exception {
        return "Result from " + Thread.currentThread().getName();
    }
}
FutureTask<String> task = new FutureTask<>(new MyCallable());
new Thread(task).start();
String result = task.get();  // 阻塞获取结果
```

### 线程状态

```
NEW → RUNNABLE ←→ BLOCKED
                   ←→ WAITING
                   ←→ TIMED_WAITING
     → TERMINATED
```

```java
// 线程状态转换演示
Thread t = new Thread(() -> {
    try {
        Thread.sleep(1000);           // RUNNABLE → TIMED_WAITING
        synchronized (lock) {
            lock.wait();              // RUNNABLE → WAITING
        }
    } catch (InterruptedException e) {
        Thread.currentThread().interrupt();
    }
});
System.out.println(t.getState());     // NEW
t.start();
System.out.println(t.getState());     // RUNNABLE
```

## 三、synchronized 原理

### 三种用法

```java
public class SynchronizedDemo {
    // 1. 实例方法锁（锁 this）
    public synchronized void instanceMethod() { }

    // 2. 静态方法锁（锁 Class 对象）
    public static synchronized void staticMethod() { }

    // 3. 同步代码块（锁指定对象）
    public void block() {
        synchronized (this) { }
    }
}
```

### 锁升级过程 (JDK 6+)

```
无锁 → 偏向锁 → 轻量级锁 → 重量级锁 (不可逆)
```

| 锁状态 | 开销 | 适用场景 |
|--------|------|----------|
| 偏向锁 | 最低 | 单线程访问 |
| 轻量级锁 | 较低 | 线程交替执行 |
| 重量级锁 | 较高 | 多线程竞争激烈 |

## 四、volatile 关键字

### 可见性保证

```java
public class VolatileExample {
    private volatile boolean running = true;

    public void run() {
        while (running) {
            // 无 volatile 则此线程可能永远看不到其他线程对 running 的修改
        }
    }

    public void stop() {
        running = false;
    }
}
```

### volatile 不保证原子性

```java
private volatile int count = 0;

// ❌ 不保证原子性：count++ 是读-改-写三步操作
public void increment() {
    count++;
}

// ✅ 使用 synchronized 或 AtomicInteger
private AtomicInteger count2 = new AtomicInteger(0);
public void safeIncrement() {
    count2.incrementAndGet();
}
```

## 五、CAS 无锁编程

```java
import java.util.concurrent.atomic.*;

public class CASDemo {
    private AtomicInteger count = new AtomicInteger(0);
    private AtomicReference<Node> head = new AtomicReference<>();
    private AtomicIntegerArray array = new AtomicIntegerArray(10);
    private AtomicLongFieldUpdater<Order> updater = 
        AtomicLongFieldUpdater.newUpdater(Order.class, "version");

    public void increment() {
        // CAS 自增
        count.incrementAndGet();
    }

    public boolean tryUpdate(int expected, int newValue) {
        // 手动 CAS
        return count.compareAndSet(expected, newValue);
    }
}

// CAS 实现简易锁
class CASLock {
    private AtomicInteger state = new AtomicInteger(0);

    public void lock() {
        while (!state.compareAndSet(0, 1)) {
            // 自旋等待
            Thread.onSpinWait();
        }
    }

    public void unlock() {
        state.set(0);
    }
}
```

### CAS 三大问题

| 问题 | 说明 | 解决方案 |
|------|------|----------|
| ABA 问题 | 值被改回原值 | AtomicStampedReference（版本号） |
| 自旋开销 | 长时间不成功浪费 CPU | 自适应自旋 + 指定次数后挂起 |
| 仅单变量 | 无法同时对多个变量 CAS | AtomicReference 包装对象 |

## 六、线程通信

```java
public class WaitNotifyDemo {
    private final Object lock = new Object();
    private boolean ready = false;

    public void waitForReady() throws InterruptedException {
        synchronized (lock) {
            while (!ready) {            // 防止虚假唤醒
                lock.wait();
            }
        }
    }

    public void setReady() {
        synchronized (lock) {
            ready = true;
            lock.notifyAll();           // 唤醒所有等待线程
        }
    }
}
```

## 面试考点

1. **synchronized 和 ReentrantLock 的区别？** synchronized 自动释放，ReentrantLock 支持可中断、公平锁、Condition
2. **线程池核心参数及其作用？** corePoolSize, maxPoolSize, keepAliveTime, workQueue, threadFactory, handler
3. **volatile 能替代 synchronized 吗？** 不能，volatile 只保证可见性和有序性，不保证原子性
4. **CAS 的 ABA 问题怎么解决？** 添加版本号，如 AtomicStampedReference

## 课后练习

1. 使用 wait/notify 实现生产者-消费者模型
2. 使用 CAS 实现一个简单的计数器，对比 synchronized 的性能差异
3. 分析 volatile 和 synchronized 的内存语义差异
4. 实现自定义 ReentrantLock 的简单版本（基于 AQS）

## 自测题

1. 以下哪种方式不能创建线程？ A) new Thread() B) new Thread(new Runnable()) C) Executors.newCachedThreadPool() D) Thread.run()
2. synchronized 是可重入锁吗？ A) 是 B) 否 C) 取决于版本 D) 取决于配置
3. CAS 操作的全称是？ A) Compare-And-Swap B) Create-And-Set C) Check-And-Store D) Compare-Add-Spin

**答案：** 1-D, 2-A, 3-A
