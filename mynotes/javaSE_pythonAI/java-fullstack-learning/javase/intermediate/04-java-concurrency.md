# Java 并发编程

## 一、线程基础

### 1. 线程创建与启动

```java
public class ThreadBasics {
    public static void main(String[] args) {
        // 方式1: 继承 Thread 类
        MyThread thread1 = new MyThread();
        thread1.start();

        // 方式2: 实现 Runnable 接口（推荐）
        Thread thread2 = new Thread(new MyRunnable());
        thread2.start();

        // 方式3: 使用 Lambda 表达式（Java 8+）
        Thread thread3 = new Thread(() -> {
            for (int i = 0; i < 5; i++) {
                System.out.println("Lambda Thread: " + i);
                try {
                    Thread.sleep(500);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        });
        thread3.start();

        // 方式4: 实现 Callable 接口（可返回结果）
        ExecutorService executor = Executors.newSingleThreadExecutor();
        Future<Integer> future = executor.submit(new MyCallable());

        try {
            Integer result = future.get();
            System.out.println("Callable 结果: " + result);
        } catch (Exception e) {
            e.printStackTrace();
        }

        executor.shutdown();
    }
}

class MyThread extends Thread {
    @Override
    public void run() {
        for (int i = 0; i < 5; i++) {
            System.out.println("MyThread: " + i);
            try {
                Thread.sleep(500);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}

class MyRunnable implements Runnable {
    @Override
    public void run() {
        for (int i = 0; i < 5; i++) {
            System.out.println("MyRunnable: " + i);
            try {
                Thread.sleep(500);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}

class MyCallable implements Callable<Integer> {
    @Override
    public Integer call() throws Exception {
        int sum = 0;
        for (int i = 0; i <= 100; i++) {
            sum += i;
        }
        return sum;
    }
}
```

### 2. 线程状态

```java
public class ThreadStates {
    public static void main(String[] args) throws Exception {
        Thread thread = new Thread(() -> {
            try {
                // TIMED_WAITING
                Thread.sleep(2000);
                System.out.println("Thread running");

                // WAITING
                synchronized (ThreadStates.class) {
                    ThreadStates.class.wait();
                }

            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        });

        // NEW
        System.out.println("状态: " + thread.getState());

        thread.start();

        Thread.sleep(100);

        // RUNNABLE 或 TIMED_WAITING
        System.out.println("状态: " + thread.getState());

        Thread.sleep(2000);

        // 等待结束
        // thread.interrupt();

        // BLOCKED
        createBlockedThread();

        // TERMINATED
        Thread sleepThread = new Thread(() -> {
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {}
        });
        sleepThread.start();
        sleepThread.join();
        System.out.println("睡眠线程状态: " + sleepThread.getState());
    }

    public static void createBlockedThread() throws InterruptedException {
        Object lock = new Object();

        Thread t1 = new Thread(() -> {
            synchronized (lock) {
                try {
                    Thread.sleep(2000);
                } catch (InterruptedException e) {}
            }
        });

        Thread t2 = new Thread(() -> {
            synchronized (lock) {
                System.out.println("t2 获取锁");
            }
        });

        t1.start();
        Thread.sleep(100);
        t2.start();
        Thread.sleep(100);

        System.out.println("t2 状态: " + t2.getState());  // BLOCKED

        t1.join();
        t2.join();
    }
}
```

## 二、线程同步与锁

### 1. synchronized 关键字

```java
public class SynchronizedDemo {
    private static int counter = 0;
    private static final Object lock = new Object();

    // 同步实例方法
    public synchronized void synchronizedMethod() {
        System.out.println("同步方法: " + Thread.currentThread().getName());
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {}
    }

    // 同步静态方法
    public static synchronized void synchronizedStaticMethod() {
        System.out.println("同步静态方法: " + Thread.currentThread().getName());
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {}
    }

    // 同步代码块
    public void synchronizedBlock() {
        synchronized (this) {
            System.out.println("同步代码块: " + Thread.currentThread().getName());
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {}
        }
    }

    // 使用对象锁
    public static void increment() {
        synchronized (lock) {
            counter++;
        }
    }

    public static void main(String[] args) throws InterruptedException {
        SynchronizedDemo demo = new SynchronizedDemo();

        // 测试同步方法
        Thread t1 = new Thread(demo::synchronizedMethod, "Thread-1");
        Thread t2 = new Thread(demo::synchronizedMethod, "Thread-2");
        t1.start();
        t2.start();
        t1.join();
        t2.join();

        // 测试静态同步方法
        Thread t3 = new Thread(SynchronizedDemo::synchronizedStaticMethod, "Thread-3");
        Thread t4 = new Thread(SynchronizedDemo::synchronizedStaticMethod, "Thread-4");
        t3.start();
        t4.start();
        t3.join();
        t4.join();

        // 测试计数器
        testCounter();
    }

    // 测试线程安全的计数器
    public static void testCounter() throws InterruptedException {
        final int THREADS = 10;
        final int INCREMENTS = 1000;

        Thread[] threads = new Thread[THREADS];

        for (int i = 0; i < THREADS; i++) {
            threads[i] = new Thread(() -> {
                for (int j = 0; j < INCREMENTS; j++) {
                    increment();
                }
            });
            threads[i].start();
        }

        for (Thread thread : threads) {
            thread.join();
        }

        System.out.println("预期值: " + (THREADS * INCREMENTS));
        System.out.println("实际值: " + counter);
    }
}
```

### 2. Lock 接口

```java
import java.util.concurrent.locks.*;
import java.util.concurrent.*;

public class LockDemo {
    private static final Lock lock = new ReentrantLock();
    private static final ReadWriteLock rwLock = new ReentrantReadWriteLock();
    private static final Lock readLock = rwLock.readLock();
    private static final Lock writeLock = rwLock.writeLock();

    private static int counter = 0;
    private static String sharedData = "Hello";

    public static void main(String[] args) throws InterruptedException {
        // ReentrantLock 测试
        testReentrantLock();

        // 读写锁测试
        testReadWriteLock();

        // 尝试锁
        testTryLock();

        // 锁降级
        testLockDowngrade();
    }

    // ReentrantLock 使用
    public static void testReentrantLock() throws InterruptedException {
        System.out.println("=== ReentrantLock 测试 ===");

        final int THREADS = 5;
        CountDownLatch latch = new CountDownLatch(THREADS);

        for (int i = 0; i < THREADS; i++) {
            new Thread(() -> {
                lock.lock();
                try {
                    System.out.println(Thread.currentThread().getName() + " 获取锁");
                    counter++;
                    Thread.sleep(500);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                } finally {
                    lock.unlock();
                    System.out.println(Thread.currentThread().getName() + " 释放锁");
                    latch.countDown();
                }
            }, "Thread-" + i).start();
        }

        latch.await();
        System.out.println("Counter: " + counter + "\\n");
    }

    // 读写锁测试
    public static void testReadWriteLock() throws InterruptedException {
        System.out.println("=== 读写锁测试 ===");

        // 写线程
        new Thread(() -> {
            writeLock.lock();
            try {
                System.out.println("写线程获取锁");
                sharedData = "Updated by writer";
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            } finally {
                writeLock.unlock();
                System.out.println("写线程释放锁");
            }
        }, "Writer").start();

        Thread.sleep(100);

        // 读线程（可以并发）
        for (int i = 0; i < 3; i++) {
            new Thread(() -> {
                readLock.lock();
                try {
                    System.out.println("读线程获取锁: " + sharedData);
                    Thread.sleep(500);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                } finally {
                    readLock.unlock();
                    System.out.println("读线程释放锁");
                }
            }, "Reader-" + i).start();
        }

        Thread.sleep(2000);
        System.out.println();
    }

    // 尝试锁
    public static void testTryLock() throws InterruptedException {
        System.out.println("=== 尝试锁测试 ===");

        Thread t1 = new Thread(() -> {
            lock.lock();
            try {
                System.out.println("Thread-1 获取锁");
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            } finally {
                lock.unlock();
                System.out.println("Thread-1 释放锁");
            }
        });

        Thread t2 = new Thread(() -> {
            boolean acquired = false;
            try {
                // 尝试获取锁，最多等待500ms
                acquired = lock.tryLock(500, TimeUnit.MILLISECONDS);
                if (acquired) {
                    System.out.println("Thread-2 获取锁成功");
                    Thread.sleep(500);
                } else {
                    System.out.println("Thread-2 获取锁失败");
                }
            } catch (InterruptedException e) {
                e.printStackTrace();
            } finally {
                if (acquired) {
                    lock.unlock();
                    System.out.println("Thread-2 释放锁");
                }
            }
        });

        t1.start();
        t2.start();

        t1.join();
        t2.join();
        System.out.println();
    }

    // 锁降级（写锁 -> 读锁）
    public static void testLockDowngrade() {
        System.out.println("=== 锁降级测试 ===");

        writeLock.lock();
        try {
            System.out.println("获取写锁");

            // 降级为读锁
            readLock.lock();
            System.out.println("降级为读锁");

            // 释放写锁
            writeLock.unlock();
            System.out.println("释放写锁");

            // 使用读锁
            System.out.println("使用读锁: " + sharedData);

        } finally {
            readLock.unlock();
            System.out.println("释放读锁");
        }
    }
}
```

## 三、线程池

### 1. 线程池基础

```java
import java.util.concurrent.*;
import java.util.*;

public class ThreadPoolDemo {
    public static void main(String[] args) throws InterruptedException {
        // 固定大小线程池
        testFixedThreadPool();

        // 缓存线程池
        testCachedThreadPool();

        // 单线程池
        testSingleThreadExecutor();

        // 定时任务线程池
        testScheduledThreadPool();

        // 自定义线程池
        testCustomThreadPool();

        // Fork/Join 框架
        testForkJoin();
    }

    // 固定大小线程池
    public static void testFixedThreadPool() throws InterruptedException {
        System.out.println("=== 固定大小线程池 ===");

        ExecutorService executor = Executors.newFixedThreadPool(3);

        for (int i = 0; i < 5; i++) {
            final int taskId = i;
            executor.submit(() -> {
                System.out.println("Task " + taskId + " 开始执行: " + Thread.currentThread().getName());
                try {
                    Thread.sleep(1000);
                } catch (InterruptedException e) {}
                System.out.println("Task " + taskId + " 执行完成");
            });
        }

        executor.shutdown();
        executor.awaitTermination(5, TimeUnit.SECONDS);
        System.out.println();
    }

    // 缓存线程池
    public static void testCachedThreadPool() throws InterruptedException {
        System.out.println("=== 缓存线程池 ===");

        ExecutorService executor = Executors.newCachedThreadPool();

        for (int i = 0; i < 5; i++) {
            final int taskId = i;
            executor.submit(() -> {
                System.out.println("Task " + taskId + ": " + Thread.currentThread().getName());
            });
        }

        executor.shutdown();
        executor.awaitTermination(2, TimeUnit.SECONDS);
        System.out.println();
    }

    // 单线程池
    public static void testSingleThreadExecutor() throws InterruptedException {
        System.out.println("=== 单线程池 ===");

        ExecutorService executor = Executors.newSingleThreadExecutor();

        for (int i = 0; i < 3; i++) {
            final int taskId = i;
            executor.submit(() -> {
                System.out.println("Task " + taskId);
            });
        }

        executor.shutdown();
        executor.awaitTermination(2, TimeUnit.SECONDS);
        System.out.println();
    }

    // 定时任务线程池
    public static void testScheduledThreadPool() throws InterruptedException {
        System.out.println("=== 定时任务线程池 ===");

        ScheduledExecutorService executor = Executors.newScheduledThreadPool(2);

        // 延迟执行
        executor.schedule(() -> {
            System.out.println("延迟3秒执行");
        }, 3, TimeUnit.SECONDS);

        // 固定延迟执行
        executor.scheduleWithFixedDelay(() -> {
            System.out.println("固定延迟执行: " + LocalDateTime.now());
        }, 0, 2, TimeUnit.SECONDS);

        // 固定频率执行
        executor.scheduleAtFixedRate(() -> {
            System.out.println("固定频率执行: " + LocalDateTime.now());
        }, 0, 3, TimeUnit.SECONDS);

        Thread.sleep(10000);
        executor.shutdown();
        System.out.println();
    }

    // 自定义线程池（推荐方式）
    public static void testCustomThreadPool() throws InterruptedException {
        System.out.println("=== 自定义线程池 ===");

        // 使用 ThreadPoolExecutor 创建
        ThreadPoolExecutor executor = new ThreadPoolExecutor(
            2,                              // 核心线程数
            5,                              // 最大线程数
            60L, TimeUnit.SECONDS,          // 空闲线程存活时间
            new ArrayBlockingQueue<>(10),   // 任务队列
            Executors.defaultThreadFactory(),  // 线程工厂
            new ThreadPoolExecutor.AbortPolicy()  // 拒绝策略
        );

        // 监控线程池
        new Thread(() -> {
            while (!executor.isShutdown()) {
                System.out.printf(
                    "核心线程: %d, 最大线程: %d, 当前线程: %d, " +
                    "队列大小: %d, 已完成任务: %d\\n",
                    executor.getCorePoolSize(),
                    executor.getMaximumPoolSize(),
                    executor.getPoolSize(),
                    executor.getQueue().size(),
                    executor.getCompletedTaskCount()
                );
                try {
                    Thread.sleep(1000);
                } catch (InterruptedException e) {}
            }
        }).start();

        // 提交任务
        for (int i = 0; i < 20; i++) {
            final int taskId = i;
            try {
                executor.execute(() -> {
                    try {
                        Thread.sleep(1000);
                        System.out.println("Task " + taskId + " 完成");
                    } catch (InterruptedException e) {}
                });
            } catch (RejectedExecutionException e) {
                System.out.println("Task " + taskId + " 被拒绝");
            }
        }

        Thread.sleep(8000);
        executor.shutdown();
        System.out.println();
    }

    // Fork/Join 框架
    public static void testForkJoin() throws InterruptedException, ExecutionException {
        System.out.println("=== Fork/Join 框架 ===");

        ForkJoinPool pool = new ForkJoinPool();

        // 计算斐波那契数列
        FibonacciTask task = new FibonacciTask(20);
        Integer result = pool.invoke(task);

        System.out.println("Fibonacci(20) = " + result);

        pool.shutdown();
    }

    // Fork/Join 任务
    static class FibonacciTask extends RecursiveTask<Integer> {
        private final int n;

        public FibonacciTask(int n) {
            this.n = n;
        }

        @Override
        protected Integer compute() {
            if (n <= 1) {
                return n;
            }

            FibonacciTask f1 = new FibonacciTask(n - 1);
            FibonacciTask f2 = new FibonacciTask(n - 2);

            f1.fork();
            f2.fork();

            return f1.join() + f2.join();
        }
    }
}
```

### 2. 生产者消费者模型

```java
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import java.util.*;

public class ProducerConsumer {
    public static void main(String[] args) {
        // 使用 BlockingQueue 实现
        producerConsumerWithBlockingQueue();

        // 使用 Condition 实现
        producerConsumerWithCondition();
    }

    // 使用 BlockingQueue
    public static void producerConsumerWithBlockingQueue() {
        System.out.println("=== BlockingQueue 实现 ===");

        BlockingQueue<Integer> queue = new ArrayBlockingQueue<>(5);

        // 生产者
        Runnable producer = () -> {
            try {
                for (int i = 0; i < 10; i++) {
                    System.out.println("生产: " + i);
                    queue.put(i);  // 阻塞直到队列有空间
                    Thread.sleep(100);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        };

        // 消费者
        Runnable consumer = () -> {
            try {
                for (int i = 0; i < 10; i++) {
                    Integer item = queue.take();  // 阻塞直到队列有元素
                    System.out.println("消费: " + item);
                    Thread.sleep(200);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        };

        new Thread(producer, "Producer").start();
        new Thread(consumer, "Consumer").start();

        try {
            Thread.sleep(3000);
        } catch (InterruptedException e) {}
        System.out.println();
    }

    // 使用 Condition 实现
    public static void producerConsumerWithCondition() {
        System.out.println("=== Condition 实现 ===");

        SharedBuffer buffer = new SharedBuffer();

        // 生产者
        Runnable producer = () -> {
            try {
                for (int i = 0; i < 10; i++) {
                    buffer.put(i);
                    Thread.sleep(100);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        };

        // 消费者
        Runnable consumer = () -> {
            try {
                for (int i = 0; i < 10; i++) {
                    buffer.take();
                    Thread.sleep(200);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        };

        new Thread(producer, "Producer").start();
        new Thread(consumer, "Consumer").start();

        try {
            Thread.sleep(3000);
        } catch (InterruptedException e) {}
    }

    // 共享缓冲区
    static class SharedBuffer {
        private final Queue<Integer> queue = new LinkedList<>();
        private final int capacity = 5;
        private final Lock lock = new ReentrantLock();
        private final Condition notFull = lock.newCondition();
        private final Condition notEmpty = lock.newCondition();

        public void put(int item) throws InterruptedException {
            lock.lock();
            try {
                while (queue.size() >= capacity) {
                    System.out.println("队列满，生产者等待");
                    notFull.await();
                }

                queue.offer(item);
                System.out.println("生产: " + item + ", 队列大小: " + queue.size());
                notEmpty.signal();
            } finally {
                lock.unlock();
            }
        }

        public void take() throws InterruptedException {
            lock.lock();
            try {
                while (queue.isEmpty()) {
                    System.out.println("队列空，消费者等待");
                    notEmpty.await();
                }

                int item = queue.poll();
                System.out.println("消费: " + item + ", 队列大小: " + queue.size());
                notFull.signal();
            } finally {
                lock.unlock();
            }
        }
    }
}
```

## 四、并发工具类

### 1. CountDownLatch、CyclicBarrier、Semaphore

```java
import java.util.concurrent.*;
import java.util.*;

public class ConcurrentUtilsDemo {
    public static void main(String[] args) throws InterruptedException {
        // CountDownLatch 倒计时门闩
        testCountDownLatch();

        // CyclicBarrier 循环栅栏
        testCyclicBarrier();

        // Semaphore 信号量
        testSemaphore();
    }

    // CountDownLatch - 一个或多个线程等待其他线程完成
    public static void testCountDownLatch() throws InterruptedException {
        System.out.println("=== CountDownLatch 测试 ===");

        final int THREADS = 3;
        CountDownLatch startLatch = new CountDownLatch(1);  // 发令枪
        CountDownLatch doneLatch = new CountDownLatch(THREADS);  // 完成计数

        for (int i = 0; i < THREADS; i++) {
            final int workerId = i;
            new Thread(() -> {
                try {
                    // 等待开始信号
                    System.out.println("Worker " + workerId + " 准备就绪");
                    startLatch.await();

                    // 执行任务
                    System.out.println("Worker " + workerId + " 开始工作");
                    Thread.sleep(1000);
                    System.out.println("Worker " + workerId + " 完成工作");

                    // 计数减1
                    doneLatch.countDown();
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }, "Worker-" + i).start();
        }

        // 发令枪
        Thread.sleep(100);
        System.out.println("开始！所有线程启动");
        startLatch.countDown();

        // 等待所有线程完成
        doneLatch.await();
        System.out.println("所有线程已完成！\\n");
    }

    // CyclicBarrier - 多个线程互相等待
    public static void testCyclicBarrier() throws InterruptedException {
        System.out.println("=== CyclicBarrier 测试 ===");

        final int PARTIES = 3;

        // 创建栅栏，到达后执行回调
        CyclicBarrier barrier = new CyclicBarrier(PARTIES, () -> {
            System.out.println("=== 所有线程已到达，开始下一阶段 ===");
        });

        for (int i = 0; i < PARTIES; i++) {
            final int threadId = i;
            new Thread(() -> {
                try {
                    for (int phase = 1; phase <= 2; phase++) {
                        System.out.println("Thread " + threadId + " 阶段 " + phase + " 开始");
                        Thread.sleep(500);
                        System.out.println("Thread " + threadId + " 到达栅栏");
                        barrier.await();  // 等待其他线程
                    }
                } catch (BrokenBarrierException | InterruptedException e) {
                    e.printStackTrace();
                }
            }, "Thread-" + i).start();
        }

        Thread.sleep(3000);
        System.out.println();
    }

    // Semaphore - 控制并发访问数量
    public static void testSemaphore() throws InterruptedException {
        System.out.println("=== Semaphore 测试 ===");

        final int PERMITS = 2;  // 只允许2个线程同时访问
        Semaphore semaphore = new Semaphore(PERMITS);

        for (int i = 0; i < 5; i++) {
            final int threadId = i;
            new Thread(() -> {
                try {
                    // 获取许可
                    System.out.println("Thread " + threadId + " 尝试获取许可");
                    semaphore.acquire();
                    System.out.println("Thread " + threadId + " 获取许可成功，开始工作");

                    Thread.sleep(1000);

                    // 释放许可
                    System.out.println("Thread " + threadId + " 完成工作，释放许可");
                    semaphore.release();
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }, "Thread-" + i).start();
        }

        Thread.sleep(6000);
        System.out.println();
    }
}
```

### 2. 并发集合

```java
import java.util.concurrent.*;
import java.util.*;
import java.util.concurrent.atomic.*;

public class ConcurrentCollectionsDemo {
    public static void main(String[] args) throws InterruptedException {
        // ConcurrentHashMap
        testConcurrentHashMap();

        // CopyOnWriteArrayList
        testCopyOnWriteArrayList();

        // ConcurrentLinkedQueue
        testConcurrentLinkedQueue();

        // BlockingQueue
        testBlockingQueue();

        // 原子类
        testAtomic();
    }

    // ConcurrentHashMap
    public static void testConcurrentHashMap() throws InterruptedException {
        System.out.println("=== ConcurrentHashMap 测试 ===");

        ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();

        // 并发写入
        int threads = 10;
        CountDownLatch latch = new CountDownLatch(threads);

        for (int i = 0; i < threads; i++) {
            final int threadId = i;
            new Thread(() -> {
                for (int j = 0; j < 100; j++) {
                    String key = "key-" + (threadId * 100 + j);
                    map.put(key, j);
                }
                latch.countDown();
            }).start();
        }

        latch.await();
        System.out.println("Map 大小: " + map.size());

        // 原子操作
        map.putIfAbsent("test", 100);
        map.computeIfAbsent("test", k -> 200);
        map.compute("test", (k, v) -> v + 100);
        map.merge("test", 50, Integer::sum);

        System.out.println("test 值: " + map.get("test"));
        System.out.println();
    }

    // CopyOnWriteArrayList
    public static void testCopyOnWriteArrayList() throws InterruptedException {
        System.out.println("=== CopyOnWriteArrayList 测试 ===");

        CopyOnWriteArrayList<String> list = new CopyOnWriteArrayList<>();

        // 添加元素
        list.add("A");
        list.add("B");
        list.add("C");

        // 遍历时修改
        new Thread(() -> {
            System.out.println("迭代线程开始遍历");
            for (String item : list) {
                System.out.println("迭代: " + item);
                try {
                    Thread.sleep(500);
                } catch (InterruptedException e) {}
            }
            System.out.println("迭代线程完成");
        }).start();

        // 修改线程
        new Thread(() -> {
            try {
                Thread.sleep(300);
                System.out.println("添加元素 D");
                list.add("D");
                System.out.println("添加元素 E");
                list.add("E");
            } catch (InterruptedException e) {}
        }).start();

        Thread.sleep(2000);
        System.out.println("最终列表: " + list);
        System.out.println();
    }

    // ConcurrentLinkedQueue
    public static void testConcurrentLinkedQueue() throws InterruptedException {
        System.out.println("=== ConcurrentLinkedQueue 测试 ===");

        ConcurrentLinkedQueue<Integer> queue = new ConcurrentLinkedQueue<>();

        // 生产者
        Thread producer = new Thread(() -> {
            for (int i = 0; i < 10; i++) {
                queue.offer(i);
                System.out.println("生产: " + i);
                try {
                    Thread.sleep(200);
                } catch (InterruptedException e) {}
            }
        });

        // 消费者
        Thread consumer = new Thread(() -> {
            while (!Thread.currentThread().isInterrupted()) {
                Integer item = queue.poll();
                if (item != null) {
                    System.out.println("消费: " + item);
                } else if (producer.getState() == Thread.State.TERMINATED && queue.isEmpty()) {
                    break;
                }
                try {
                    Thread.sleep(300);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
        });

        producer.start();
        consumer.start();

        producer.join();
        consumer.interrupt();
        consumer.join();

        System.out.println();
    }

    // BlockingQueue
    public static void testBlockingQueue() throws InterruptedException {
        System.out.println("=== BlockingQueue 测试 ===");

        // ArrayBlockingQueue - 有界队列
        BlockingQueue<String> boundedQueue = new ArrayBlockingQueue<>(3);

        // LinkedBlockingQueue - 无界队列
        BlockingQueue<String> unboundedQueue = new LinkedBlockingQueue<>();

        // PriorityBlockingQueue - 优先级队列
        PriorityBlockingQueue<Integer> priorityQueue = new PriorityBlockingQueue<>();

        // DelayQueue - 延迟队列
        DelayQueue<DelayedTask> delayQueue = new DelayQueue<>();

        // 测试有界队列
        Thread producer = new Thread(() -> {
            for (int i = 0; i < 5; i++) {
                try {
                    boundedQueue.put("Item-" + i);
                    System.out.println("生产: Item-" + i + ", 队列大小: " + boundedQueue.size());
                } catch (InterruptedException e) {}
            }
        });

        Thread consumer = new Thread(() -> {
            for (int i = 0; i < 5; i++) {
                try {
                    String item = boundedQueue.take();
                    System.out.println("消费: " + item + ", 队列大小: " + boundedQueue.size());
                    Thread.sleep(500);
                } catch (InterruptedException e) {}
            }
        });

        producer.start();
        consumer.start();

        producer.join();
        consumer.join();

        System.out.println();
    }

    // 原子类
    public static void testAtomic() throws InterruptedException {
        System.out.println("=== 原子类测试 ===");

        AtomicInteger atomicInt = new AtomicInteger(0);
        AtomicLong atomicLong = new AtomicLong(0);
        AtomicReference<String> atomicRef = new AtomicReference<>("Initial");
        AtomicBoolean atomicBool = new AtomicBoolean(false);

        // 并发增加
        int threads = 10;
        int increments = 1000;
        CountDownLatch latch = new CountDownLatch(threads);

        for (int i = 0; i < threads; i++) {
            new Thread(() -> {
                for (int j = 0; j < increments; j++) {
                    // 原子增加
                    atomicInt.incrementAndGet();
                    atomicLong.incrementAndGet();

                    // 原子更新
                    atomicInt.updateAndGet(x -> x + 2);

                    // 原子比较交换
                    atomicRef.compareAndSet(
                        atomicRef.get(),
                        atomicRef.get() + "-modified"
                    );
                }
                latch.countDown();
            }).start();
        }

        latch.await();

        System.out.println("AtomicInt: " + atomicInt.get());
        System.out.println("AtomicLong: " + atomicLong.get());
        System.out.println("AtomicRef: " + atomicRef.get());

        // 原子数组
        AtomicIntegerArray atomicArray = new AtomicIntegerArray(5);
        atomicArray.set(0, 10);
        atomicArray.incrementAndGet(0);
        System.out.println("AtomicArray[0]: " + atomicArray.get(0));
    }
}

// 延迟任务
class DelayedTask implements Delayed {
    private final long executeTime;
    private final String name;

    public DelayedTask(long delay, String name) {
        this.executeTime = System.currentTimeMillis() + delay;
        this.name = name;
    }

    @Override
    public long getDelay(TimeUnit unit) {
        return unit.convert(executeTime - System.currentTimeMillis(), TimeUnit.MILLISECONDS);
    }

    @Override
    public int compareTo(Delayed other) {
        return Long.compare(this.executeTime, ((DelayedTask) other).executeTime);
    }

    @Override
    public String toString() {
        return name;
    }
}
```

## 五、CompletableFuture（异步编程）

```java
import java.util.concurrent.*;
import java.util.*;

public class CompletableFutureDemo {
    public static void main(String[] args) throws Exception {
        // 基础使用
        basicUsage();

        // 组合多个 Future
        combineFutures();

        // 异常处理
        exceptionHandling();

        // 实际应用场景
        practicalExample();
    }

    // 基础使用
    public static void basicUsage() throws Exception {
        System.out.println("=== CompletableFuture 基础使用 ===");

        // 创建并执行异步任务
        CompletableFuture<String> future1 = CompletableFuture.supplyAsync(() -> {
            System.out.println("任务1 开始");
            sleep(500);
            return "Result 1";
        });

        // 添加回调
        CompletableFuture<String> future2 = future1.thenApply(result -> {
            System.out.println("任务2 处理: " + result);
            sleep(500);
            return result + " -> Processed";
        });

        // 添加消费回调（无返回值）
        CompletableFuture<Void> future3 = future2.thenAccept(result -> {
            System.out.println("任务3 消费: " + result);
        });

        // 添加运行回调
        CompletableFuture<Void> future4 = future3.thenRun(() -> {
            System.out.println("任务4 完成");
        });

        // 等待完成
        future4.get();
        System.out.println();
    }

    // 组合多个 Future
    public static void combineFutures() throws Exception {
        System.out.println("=== 组合多个 Future ===");

        CompletableFuture<String> future1 = CompletableFuture.supplyAsync(() -> {
            sleep(500);
            return "Hello";
        });

        CompletableFuture<String> future2 = CompletableFuture.supplyAsync(() -> {
            sleep(300);
            return "World";
        });

        // 组合两个 Future（等两个都完成）
        CompletableFuture<String> combinedFuture = future1.thenCombine(future2, (r1, r2) -> {
            return r1 + " " + r2;
        });

        System.out.println("组合结果: " + combinedFuture.get());

        // 组合多个 Future（allOf）
        CompletableFuture<Void> allFutures = CompletableFuture.allOf(
            CompletableFuture.runAsync(() -> { sleep(300); System.out.println("Task A"); }),
            CompletableFuture.runAsync(() -> { sleep(200); System.out.println("Task B"); }),
            CompletableFuture.runAsync(() -> { sleep(100); System.out.println("Task C"); })
        );

        allFutures.get();
        System.out.println("所有任务完成");

        // 组合多个 Future（anyOf）
        CompletableFuture<Object> anyFuture = CompletableFuture.anyOf(
            CompletableFuture.supplyAsync(() -> { sleep(500); return "Task 1"; }),
            CompletableFuture.supplyAsync(() -> { sleep(200); return "Task 2"; }),
            CompletableFuture.supplyAsync(() -> { sleep(300); return "Task 3"; })
        );

        System.out.println("最先完成: " + anyFuture.get());
        System.out.println();
    }

    // 异常处理
    public static void exceptionHandling() throws Exception {
        System.out.println("=== 异常处理 ===");

        // 处理异常
        CompletableFuture<String> future = CompletableFuture.supplyAsync(() -> {
            if (Math.random() > 0.5) {
                throw new RuntimeException("模拟异常");
            }
            return "Success";
        });

        future
            .exceptionally(ex -> {
                System.out.println("异常: " + ex.getMessage());
                return "Default Value";
            })
            .thenAccept(result -> {
                System.out.println("最终结果: " + result);
            })
            .get();

        // 组合异常处理
        CompletableFuture<String> future2 = CompletableFuture.supplyAsync(() -> {
            sleep(500);
            return "正常结果";
        });

        future2
            .handle((result, ex) -> {
                if (ex != null) {
                    return "异常: " + ex.getMessage();
                }
                return "正常: " + result;
            })
            .thenAccept(System.out::println)
            .get();

        System.out.println();
    }

    // 实际应用场景：电商订单处理
    public static void practicalExample() throws Exception {
        System.out.println("=== 电商订单处理 ===");

        long startTime = System.currentTimeMillis();

        // 获取用户信息
        CompletableFuture<User> userFuture = CompletableFuture.supplyAsync(() -> {
            sleep(200);
            return new User("张三", "VIP");
        });

        // 获取商品信息
        CompletableFuture<Product> productFuture = CompletableFuture.supplyAsync(() -> {
            sleep(300);
            return new Product("iPhone 15", 5999.00);
        });

        // 获取优惠券
        CompletableFuture<Coupon> couponFuture = CompletableFuture.supplyAsync(() -> {
            sleep(150);
            return new Coupon("NEWUSER", 100.00);
        });

        // 获取库存
        CompletableFuture<Integer> stockFuture = CompletableFuture.supplyAsync(() -> {
            sleep(100);
            return 50;
        });

        // 组合所有操作
        CompletableFuture<OrderResult> orderFuture = CompletableFuture.allOf(
            userFuture, productFuture, couponFuture, stockFuture
        ).thenApply(v -> {
            try {
                User user = userFuture.get();
                Product product = productFuture.get();
                Coupon coupon = couponFuture.get();
                int stock = stockFuture.get();

                // 计算价格
                double finalPrice = product.getPrice() - coupon.getDiscount();

                return new OrderResult(
                    user.getName(),
                    product.getName(),
                    coupon.getCode(),
                    finalPrice,
                    stock
                );
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        });

        OrderResult result = orderFuture.get();
        System.out.println("订单处理结果:");
        System.out.println("  用户: " + result.userName);
        System.out.println("  商品: " + result.productName);
        System.out.println("  优惠券: " + result.couponCode);
        System.out.println("  最终价格: ¥" + result.finalPrice);
        System.out.println("  库存: " + result.stock);

        long endTime = System.currentTimeMillis();
        System.out.printf("总耗时: %dms\\n", endTime - startTime);
    }

    private static void sleep(long millis) {
        try {
            Thread.sleep(millis);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    // 测试类
    static class User {
        private String name;
        private String level;

        public User(String name, String level) {
            this.name = name;
            this.level = level;
        }

        public String getName() { return name; }
    }

    static class Product {
        private String name;
        private double price;

        public Product(String name, double price) {
            this.name = name;
            this.price = price;
        }

        public String getName() { return name; }
        public double getPrice() { return price; }
    }

    static class Coupon {
        private String code;
        private double discount;

        public Coupon(String code, double discount) {
            this.code = code;
            this.discount = discount;
        }

        public String getCode() { return code; }
        public double getDiscount() { return discount; }
    }

    static class OrderResult {
        String userName;
        String productName;
        String couponCode;
        double finalPrice;
        int stock;

        public OrderResult(String userName, String productName, String couponCode, double finalPrice, int stock) {
            this.userName = userName;
            this.productName = productName;
            this.couponCode = couponCode;
            this.finalPrice = finalPrice;
            this.stock = stock;
        }
    }
}
```

## 小结

本节学习了 Java 并发编程：

- **线程基础** - 创建、状态、生命周期
- **线程同步** - synchronized、Lock、ReadWriteLock
- **线程池** - ThreadPoolExecutor、Fork/Join
- **并发工具** - CountDownLatch、CyclicBarrier、Semaphore
- **并发集合** - ConcurrentHashMap、CopyOnWriteArrayList
- **异步编程** - CompletableFuture

## 实践练习

### 编程题
1. 使用线程池实现一个并发的 Web 爬虫：从种子 URL 开始，并发送 HTTP 请求，提取页面链接后继续爬取，使用 ConcurrentHashMap 去重，控制最大并发数为 10。
2. 使用 CompletableFuture 实现一个旅行预订系统：并行查询航班、酒店、租车三个服务，三个服务全部返回后汇总结果，任何一个失败则整体回滚。

### 思考题
1. `synchronized` 和 `ReentrantLock` 的区别？什么场景下应该选择 Lock？
2. 线程池的核心参数（corePoolSize、maxPoolSize、queueCapacity）应该如何根据业务场景调整？

### 自测题
1. 线程有哪几种状态？状态之间如何转换？
2. CountDownLatch 和 CyclicBarrier 的区别是什么？
3. ThreadLocal 的作用和使用注意事项？

下一步将学习 Spring 框架基础（→ `spring/beginner/01-spring-framework.md`）。