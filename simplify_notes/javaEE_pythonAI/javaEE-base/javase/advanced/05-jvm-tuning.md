# JVM 调优指南

## 一、JVM 架构概述

### 1. JVM 内存模型

```
┌─────────────────────────────────────────────────────┐
│                    运行时数据区                        │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌───────────────────────────────────────────────┐  │
│  │              方法区 (Method Area)              │  │
│  │  - 类信息、方法信息、常量池、静态变量          │  │
│  └───────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────┐  │
│  │               堆 (Heap)                        │  │
│  │  ┌──────────────┬──────────────┐              │  │
│  │  │  年轻代      │   老年代     │              │  │
│  │  │  Young Gen   │   Old Gen   │              │  │
│  │  │  ┌──────┐    │  ┌────────┐ │              │  │
│  │  │  │ Eden │    │  │ Tenured│ │              │  │
│  │  │  └──────┘    │  │  Space │ │              │  │
│  │  │  ┌────────┐   │  └────────┘ │              │  │
│  │  │  │Survivor│   │             │              │  │
│  │  │  │  S0/S1 │   │             │              │  │
│  │  │  └────────┘   │             │              │  │
│  │  └──────────────┴──────────────┘              │  │
│  └───────────────────────────────────────────────┘  │
│  ┌───────────────────┐  ┌───────────────────────┐  │
│  │    程序计数器       │  │    Java 虚拟机栈       │  │
│  │  Program Counter  │  │   JVM Stack           │  │
│  │   (线程私有)       │  │    (线程私有)         │  │
│  └───────────────────┘  └───────────────────────┘  │
│  ┌───────────────────┐  ┌───────────────────────┐  │
│  │   本地方法栈       │  │   直接内存            │  │
│  │  Native Method    │  │   Direct Memory      │  │
│  │   (线程私有)       │  │    (堆外内存)        │  │
│  └───────────────────┘  └───────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### 2. 各区域详细说明

```java
/**
 * 程序计数器 (Program Counter Register)
 * - 作用：记录当前线程执行的字节码指令地址
 * - 特点：线程私有，内存极小，唯一不会 OOM 的区域
 * - 用途：字节码解释器工作时通过改变计数器来选取下一条指令
 */

/**
 * Java 虚拟机栈 (JVM Stack)
 * - 作用：描述 Java 方法执行的内存模型
 * - 特点：线程私有，生命周期与线程相同
 * - 组成：栈帧（Stack Frame）
 *   - 局部变量表：存储方法参数和局部变量
 *   - 操作数栈：执行方法操作
 *   - 动态链接：运行时符号引用转换为直接引用
 *   - 返回地址：方法正常或异常退出后的返回位置
 */

public class StackFrameDemo {
    public static void main(String[] args) {
        int a = 10;        // 局部变量表
        int b = 20;
        int c = a + b;     // 操作数栈
        System.out.println(c);
    }
}

/**
 * 本地方法栈 (Native Method Stack)
 * - 作用：为 Native 方法服务
 * - 特点：线程私有
 * - 用途：执行本地方法（如 Thread.sleep()）
 */

/**
 * 方法区 (Method Area / 元空间)
 * - 作用：存储类信息、常量池、静态变量、即时编译器编译后的代码
 * - 特点：线程共享，可被 GC
 * - JDK 1.8+：使用元空间，直接内存
 * - JDK 1.8-：使用永久代
 */

/**
 * 堆 (Heap)
 * - 作用：存储对象实例，垃圾回收的主要区域
 * - 特点：线程共享，GC 管理区域
 * - 划分：
 *   - 年轻代：Eden + 2 个 Survivor (S0, S1)
 *   - 老年代：长期存活对象
 */
```

## 二、垃圾回收机制

### 1. 垃圾判断算法

```java
/**
 * 1. 引用计数法（Reference Counting）
 * - 原理：记录对象被引用的次数
 * - 优点：简单高效
 * - 缺点：无法解决循环引用问题
 * - 使用：JVM 未采用，但 Python、PHP 使用
 */
public class ReferenceCountingDemo {
    private Object ref;

    public void setRef(Object ref) {
        this.ref = ref;
    }

    // 循环引用示例
    public static void circularReference() {
        ReferenceCountingDemo a = new ReferenceCountingDemo();
        ReferenceCountingDemo b = new ReferenceCountingDemo();
        a.setRef(b);
        b.setRef(a);
        // 如果使用引用计数，a 和 b 都无法被回收
    }
}

/**
 * 2. 可达性分析算法（Reachability Analysis）
 * - 原理：从 GC Roots 开始向下搜索，不可达的对象为垃圾
 * - GC Roots 包括：
 *   - 虚拟机栈中引用的对象
 *   - 方法区中静态属性引用的对象
 *   - 方法区中常量引用的对象
 *   - 本地方法栈中引用的对象
 *   - 被同步锁持有的对象
 */
public class ReachabilityAnalysisDemo {
    // GC Root: 静态变量
    private static Object staticObj = new Object();

    public static void main(String[] args) {
        // GC Root: 栈中引用
        Object localObj = new Object();

        // GC Root: 常量
        final Object constantObj = new Object();

        // 可达对象：staticObj, localObj, constantObj
        // 不可达对象：超出作用域的对象
    }
}
```

### 2. 引用类型

```java
import java.lang.ref.*;

public class ReferenceTypesDemo {
    public static void main(String[] args) {
        // 强引用：最常见，永不回收
        Object strongRef = new Object();

        // 软引用：内存不足时回收
        ReferenceQueue<Object> queue = new ReferenceQueue<>();
        SoftReference<Object> softRef = new SoftReference<>(new Object(), queue);

        // 弱引用：GC 时必定回收
        WeakReference<Object> weakRef = new WeakReference<>(new Object(), queue);

        // 虚引用：无法通过引用获取对象，用于跟踪对象回收
        PhantomReference<Object> phantomRef = new PhantomReference<>(new Object(), queue);

        // 终结器引用（FinalReference）：对象被回收前执行 finalize()
    }
}

// 软引用应用：缓存
public class CacheDemo {
    private static final Map<String, SoftReference<byte[]>> cache = new HashMap<>();

    public static void put(String key, byte[] data) {
        cache.put(key, new SoftReference<>(data));
    }

    public static byte[] get(String key) {
        SoftReference<byte[]> ref = cache.get(key);
        return ref != null ? ref.get() : null;
    }
}
```

### 3. 垃圾回收算法

```java
/**
 * 1. 标记-清除算法 (Mark-Sweep)
 * 过程：
 *   1. 标记：标记所有需要回收的对象
 *   2. 清除：回收被标记的对象
 * 优点：简单
 * 缺点：产生大量不连续的内存碎片
 */

/**
 * 2. 标记-整理算法 (Mark-Compact)
 * 过程：
 *   1. 标记：标记所有需要回收的对象
 *   2. 整理：将存活对象向一端移动，清理边界
 * 优点：无内存碎片
 * 缺点：效率较低
 */

/**
 * 3. 复制算法 (Copying)
 * 过程：
 *   1. 将存活对象复制到另一块内存
 *   2. 清理当前内存
 * 优点：效率高，无内存碎片
 * 缺点：内存利用率低
 * 应用：年轻代 Eden 区
 */

/**
 * 4. 分代收集算法
 * 思想：根据对象存活周期将内存划分为不同代，采用不同算法
 * - 新生代：复制算法（Eden → Survivor）
 * - 老年代：标记-整理或标记-清除
 */
```

### 4. 垃圾收集器

```java
/**
 * Serial 收集器
 * - 工作方式：单线程收集
 * - 适合：小内存、单核 CPU
 * - 特点：STW (Stop-The-World)，简单高效
 */

/**
 * ParNew 收集器
 * - 工作方式：多线程收集（新生代）
 * - 适合：多核 CPU
 * - 特点：与 CMS 配合使用
 */

/**
 * Parallel Scavenge 收集器
 * - 工作方式：多线程收集（新生代）
 * - 目标：达到可控制的吞吐量
 * - 参数：
 *   - -XX:MaxGCPauseMillis：最大 GC 停顿时间
 *   - -XX:GCTimeRatio：GC 时间占比
 */

/**
 * CMS (Concurrent Mark Sweep) 收集器
 * - 工作方式：并发收集（老年代）
 * - 目标：最短回收停顿时间
 * - 过程：
 *   1. 初始标记 (STW)
 *   2. 并发标记
 *   3. 重新标记 (STW)
 *   4. 并发清除
 * - 缺点：产生内存碎片，CPU 敏感
 */

/**
 * G1 (Garbage First) 收集器
 * - 工作方式：分代收集， Region 分区
 * - 目标：可预测停顿时间，高吞吐量
 * - 特点：
 *   - 堆划分为多个 Region
 *   - 按 Region 回收
 *   - 可设置最大停顿时间
 * - 参数：
 *   - -XX:MaxGCPauseMillis：最大停顿时间
 *   - -XX:G1HeapRegionSize：Region 大小
 */

/**
 * ZGC (Z Garbage Collector)
 * - 工作方式：并发整理，Region 分区
 * - 目标：低延迟（<10ms）
 * - 特点：可扩展大堆，支持 TB 级内存
 * - 适用：需要低延迟的应用
 */
```

## 三、JVM 参数配置

### 1. 内存参数

```bash
# 堆内存配置
-Xms4g                    # 初始堆大小（必须与 -Xmx 相同）
-Xmx4g                    # 最大堆大小

# 新生代配置
-Xmn2g                    # 新生代大小
-XX:NewRatio=2            # 新生代:老年代 = 1:2
-XX:SurvivorRatio=8       # Eden:Survivor = 8:1:1
-XX:MaxTenuringThreshold=15  # 晋升老年代年龄阈值

# 元空间配置
-XX:MetaspaceSize=256m   # 元空间初始大小
-XX:MaxMetaspaceSize=512m # 元空间最大大小

# 直接内存配置
-XX:MaxDirectMemorySize=1g  # 直接内存最大大小

# 栈内存配置
-Xss512k                  # 每个线程栈大小

# GC 日志配置
-Xlog:gc*                  # 开启 GC 日志
-Xlog:gc*:file=gc.log      # GC 日志输出到文件
-XX:+PrintGCDetails        # 打印 GC 详情
-XX:+PrintGCDateStamps     # 打印 GC 时间戳
-XX:+PrintHeapAtGC         # GC 时打印堆信息
-XX:+PrintTenuringDistribution  # 打印年龄分布
-XX:+UseGCLogFileRotation     # 启用日志轮转
-XX:NumberOfGCLogFiles=10    # 保留日志文件数
-XX:GCLogFileSize=10M         # 日志文件大小
```

### 2. GC 算法选择

```bash
# Serial GC
-XX:+UseSerialGC           # 新生代和老年代都用 Serial

# Parallel GC (JDK 8 默认)
-XX:+UseParallelGC         # 新生代用 Parallel Scavenge
-XX:ParallelGCThreads=4     # GC 线程数
-XX:+UseParallelOldGC      # 老年代用 Parallel Old

# CMS GC
-XX:+UseConcMarkSweepGC    # 启用 CMS
-XX:+UseParNewGC           # 新生代用 ParNew
-XX:+CMSParallelRemarkEnabled  # 并发标记
-XX:CMSInitiatingOccupancyFraction=70  # 触发阈值
-XX:+UseCMSCompactAtFullCollection  # Full GC 时压缩
-XX:CMSFullGCsBeforeCompaction=3      # 压缩前 Full GC 次数

# G1 GC (JDK 9+ 默认)
-XX:+UseG1GC               # 启用 G1
-XX:MaxGCPauseMillis=200    # 最大停顿时间（ms）
-XX:G1HeapRegionSize=16m   # Region 大小
-XX:G1ReservePercent=10    # 保留空间百分比

# ZGC (JDK 11+)
-XX:+UnlockExperimentalVMOptions -XX:+UseZGC
-XX:ConcGCThreads=2        # 并发 GC 线程数

# Shenandoah GC (JDK 12+)
-XX:+UnlockExperimentalVMOptions -XX:+UseShenandoahGC
```

### 3. 性能调优参数

```bash
# JIT 编译
-XX:CompileThreshold=10000  # 方法调用多少次后编译
-XX:+TieredCompilation      # 分层编译
-XX:+PrintCompilation       # 打印编译信息

# 类加载
-XX:+TraceClassLoading      # 跟踪类加载
-XX:+TraceClassUnloading    # 跟踪类卸载

# 异常处理
-XX:+PrintCommandLineFlags  # 打印命令行参数
-XX:+PrintFlagsFinal        # 打印最终参数
-XX:+ErrorFile=hs_err_pid%p.log  # 错误日志文件

# 其他
-XX:+UseCompressedOops     # 压缩普通对象指针（<32GB 时启用）
-XX:+UseCompressedClassPointers  # 压缩类指针
-XX:+AlwaysPreTouch         # 预分配内存（启动慢但运行稳）
-XX:+UseStringDeduplication  # 字符串去重
```

## 四、JVM 监控工具

### 1. 命令行工具

```bash
# jps - JVM 进程状态
jps -l -v    # 显示完整类名和 JVM 参数

# jstat - JVM 统计信息
jstat -gcutil <pid> 1000 10    # 每秒输出 GC 情况，共 10 次
jstat -gc <pid>                  # GC 详情
jstat -gcnewcapacity <pid>       # 新生代容量

# jinfo - JVM 配置信息
jinfo -flags <pid>      # 查看 JVM 参数
jinfo -flag PrintGCDetails <pid>  # 查看特定参数

# jmap - 内存映射
jmap -heap <pid>                  # 查看堆信息
jmap -histo:live <pid>            # 查看堆中对象统计
jmap -dump:format=b,file=heap.hprof <pid>  # 导出堆转储

# jstack - 线程堆栈
jstack <pid>                       # 查看线程堆栈
jstack -l <pid>                    # 包含锁信息
```

### 2. 可视化工具

```java
/**
 * JConsole
 * - JDK 自带的监控工具
 * - 监控：内存、线程、类、MBean
 * - 启动：jconsole <pid>
 */

/**
 * JVisualVM
 * - JDK 自带的性能分析工具
 * - 功能：线程分析、内存分析、堆转储、GC 分析
 * - 启动：jvisualvm
 */

/**
 * Arthas（阿里开源）
 * - 功能丰富的 Java 诊断工具
 * - 安装：curl -O https://arthas.aliyun.com/arthas-boot.jar
 * - 启动：java -jar arthas-boot.jar <pid>
 * - 常用命令：
 *   - dashboard：查看系统信息
 *   - thread：查看线程信息
 *   - classloader：查看类加载器
 *   - sc：查看类
 *   - sm：查看方法
 *   - watch：观察方法调用
 *   - trace：跟踪方法调用链
 */

/**
 * MAT (Memory Analyzer Tool)
 * - Eclipse 基金会的内存分析工具
 * - 功能：分析堆转储，查找内存泄漏
 * - 下载：https://www.eclipse.org/mat/
 */

/**
 * JProfiler
 * - 商业性能分析工具
 * - 功能：CPU 分析、内存分析、线程分析
 */

/**
 * Prometheus + Grafana
 * - 生产环境监控方案
 * - 使用 Micrometer 暴露 JVM 指标
 */
```

## 五、常见问题分析

### 1. 内存泄漏

```java
/**
 * 常见内存泄漏场景
 */

// 1. 静态集合持有对象引用
public class StaticCollectionLeak {
    private static final List<Object> cache = new ArrayList<>();

    public void addObject(Object obj) {
        cache.add(obj);  // 对象永远不会被回收
    }
}

// 解决：使用 WeakHashMap 或定期清理
public class FixedStaticCollection {
    private static final Map<String, Object> cache = new WeakHashMap<>();

    public void put(String key, Object value) {
        cache.put(key, value);
    }
}

// 2. 未关闭的资源
public class ResourceLeak {
    public void readFile() throws IOException {
        FileInputStream fis = new FileInputStream("file.txt");
        // 忘记关闭 fis
    }
}

// 解决：使用 try-with-resources
public class ResourceFixed {
    public void readFile() throws IOException {
        try (FileInputStream fis = new FileInputStream("file.txt")) {
            // 自动关闭
        }
    }
}

// 3. ThreadLocal 未清理
public class ThreadLocalLeak {
    private static final ThreadLocal<byte[]> threadLocal = new ThreadLocal<>();

    public void setValue(byte[] data) {
        threadLocal.set(data);  // 线程不结束时不会被回收
    }
}

// 解决：使用后及时清理
public class ThreadLocalFixed {
    private static final ThreadLocal<byte[]> threadLocal = new ThreadLocal<>();

    public void setValue(byte[] data) {
        threadLocal.set(data);
    }

    public void clear() {
        threadLocal.remove();  // 清理引用
    }
}

// 4. 监听器和回调未移除
public class ListenerLeak {
    private final List<Listener> listeners = new ArrayList<>();

    public void addListener(Listener listener) {
        listeners.add(listener);
    }

    // 没有 removeListener，导致 listener 无法被回收
}
```

### 2. CPU 飙高

```bash
# 分析 CPU 飙高步骤：

# 1. 找到高 CPU 的 Java 进程
top

# 2. 找到高 CPU 的线程
top -H -p <pid>

# 3. 将线程 ID 转换为十六进制
printf "%x" <thread_id>

# 4. 查看线程堆栈
jstack <pid> | grep <hex_thread_id>

# 5. 使用 Arthas 分析
# 启动 Arthas
java -jar arthas-boot.jar <pid>

# 查看线程
thread

# 查看最忙的线程
thread -n 3

# 反编译类
jad <class_name>
```

### 3. 死锁

```java
/**
 * 死锁示例
 */
public class DeadlockDemo {
    private static final Object lock1 = new Object();
    private static final Object lock2 = new Object();

    public static void main(String[] args) {
        Thread t1 = new Thread(() -> {
            synchronized (lock1) {
                System.out.println("Thread 1: 获取 lock1");
                try {
                    Thread.sleep(100);
                } catch (InterruptedException e) {}

                synchronized (lock2) {
                    System.out.println("Thread 1: 获取 lock2");
                }
            }
        });

        Thread t2 = new Thread(() -> {
            synchronized (lock2) {
                System.out.println("Thread 2: 获取 lock2");
                try {
                    Thread.sleep(100);
                } catch (InterruptedException e) {}

                synchronized (lock1) {
                    System.out.println("Thread 2: 获取 lock1");
                }
            }
        });

        t1.start();
        t2.start();
    }

    /**
     * 解决死锁的方法：
     * 1. 固定锁顺序：所有线程按相同顺序获取锁
     * 2. 超时尝试：使用 tryLock()
     * 3. 死锁检测：使用 jstack 或工具检测
     */
}

// 使用 tryLock 解决死锁
public class DeadlockFixed {
    private static final Object lock1 = new Object();
    private static final Object lock2 = new Object();

    public static void main(String[] args) {
        Thread t1 = new Thread(() -> {
            try {
                if (tryLock(lock1, lock2)) {
                    // 执行业务逻辑
                }
            } finally {
                unlock(lock1, lock2);
            }
        });

        Thread t2 = new Thread(() -> {
            try {
                // 注意顺序要一致
                if (tryLock(lock1, lock2)) {
                    // 执行业务逻辑
                }
            } finally {
                unlock(lock1, lock2);
            }
        });

        t1.start();
        t2.start();
    }

    private static boolean tryLock(Object lock1, Object lock2) {
        try {
            if (lock1.tryLock(1, TimeUnit.SECONDS)) {
                if (lock2.tryLock(1, TimeUnit.SECONDS)) {
                    return true;
                }
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return false;
    }

    private static void unlock(Object... locks) {
        for (Object lock : locks) {
            if (Thread.holdsLock(lock)) {
                synchronized (lock) {
                    lock.notifyAll();
                }
            }
        }
    }
}
```

### 4. OOM (Out Of Memory)

```java
/**
 * OOM 场景分析
 */

// 1. 堆溢出（HeapOOM）
public class HeapOOM {
    static class OOMObject {}

    public static void main(String[] args) {
        List<OOMObject> list = new ArrayList<>();
        while (true) {
            list.add(new OOMObject());  // 不断创建对象，堆溢出
        }
    }
}

// 解决：增大堆内存或分析内存泄漏
// -Xms10m -Xmx10m

// 2. 栈溢出（StackOverflowError）
public class StackOverflow {
    private int stackLength = 1;

    public void stackLeak() {
        stackLength++;
        stackLeak();  // 递归过深
    }

    public static void main(String[] args) {
        StackOverflow sof = new StackOverflow();
        try {
            sof.stackLeak();
        } catch (Throwable e) {
            System.out.println("stack length: " + sof.stackLength);
            throw e;
        }
    }
}

// 解决：增大栈内存或优化递归深度
// -Xss512k

// 3. 方法区溢出（CGLib 反射）
public class MethodAreaOOM {
    static class OOMClass {}

    public static void main(String[] args) {
        while (true) {
            Enhancer enhancer = new Enhancer();
            enhancer.setSuperclass(OOMClass.class);
            enhancer.setUseCache(false);
            enhancer.setCallback(new MethodInterceptor() {
                @Override
                public Object intercept(Object obj, Method method,
                        Object[] args, MethodProxy proxy) throws Throwable {
                    return proxy.invokeSuper(obj, args);
                }
            });
            enhancer.create();
        }
    }
}

// 解决：增大元空间
// -XX:MaxMetaspaceSize=512m

// 4. 直接内存溢出
public class DirectMemoryOOM {
    private static final int _1MB = 1024 * 1024;

    public static void main(String[] args) throws Exception {
        Field unsafeField = Unsafe.class.getDeclaredFields()[0];
        unsafeField.setAccessible(true);
        Unsafe unsafe = (Unsafe) unsafeField.get(null);

        while (true) {
            unsafe.allocateMemory(_1MB);  // 直接内存溢出
        }
    }
}

// 解决：限制直接内存大小
// -XX:MaxDirectMemorySize=512m
```

## 六、调优实战案例

### 案例 1：大对象分配优化

```java
/**
 * 问题：频繁创建大对象导致频繁 Full GC
 */

// 不好的做法
public class BigObjectBad {
    public void process() {
        byte[] data = new byte[10 * 1024 * 1024];  // 10MB
        // 处理数据
    }
}

// 好的做法：使用对象池或复用
public class BigObjectGood {
    private byte[] buffer;

    public BigObjectGood() {
        this.buffer = new byte[10 * 1024 * 1024];
    }

    public void process(byte[] input) {
        // 复用 buffer
        System.arraycopy(input, 0, buffer, 0, input.length);
        // 处理数据
        // 清空 buffer
        Arrays.fill(buffer, (byte) 0);
    }
}

// 使用对象池
public class BigObjectPool {
    private final Queue<BigObjectGood> pool = new ConcurrentLinkedQueue<>();
    private final int maxSize = 10;

    public BigObjectGood borrow() {
        BigObjectGood obj = pool.poll();
        if (obj == null) {
            obj = new BigObjectGood();
        }
        return obj;
    }

    public void returnObject(BigObjectGood obj) {
        if (pool.size() < maxSize) {
            pool.offer(obj);
        }
    }
}
```

### 案例 2：集合优化

```java
/**
 * 问题：集合初始容量不当导致频繁扩容
 */

// 不好的做法
public class CollectionBad {
    public void addElements(List<String> list) {
        for (int i = 0; i < 10000; i++) {
            list.add("item" + i);  // 默认容量 10，扩容多次
        }
    }
}

// 好的做法：预估大小
public class CollectionGood {
    public void addElements(List<String> list) {
        // 预估大小，避免扩容
        List<String> optimizedList = new ArrayList<>(10000);
        for (int i = 0; i < 10000; i++) {
            optimizedList.add("item" + i);
        }
    }
}

// HashMap 优化
public class HashMapOptimization {
    // 默认初始容量 16，负载因子 0.75
    // 当元素超过 12 时扩容到 32
    // 扩容是昂贵的操作

    // 好的做法：预估容量
    public Map<String, String> createHashMap(int expectedSize) {
        // 避免扩容，容量设为 expectedSize / 0.75 + 1
        int capacity = (int) (expectedSize / 0.75) + 1;
        return new HashMap<>(capacity);
    }
}
```

### 案例 3：字符串优化

```java
/**
 * 字符串常量和 intern()
 */

public class StringOptimization {
    public static void main(String[] args) {
        // 字符串常量池
        String s1 = "hello";        // 常量池
        String s2 = "hello";        // 复用
        String s3 = new String("hello");  // 堆内存
        String s4 = s3.intern();    // 放入常量池

        System.out.println(s1 == s2);   // true
        System.out.println(s1 == s3);   // false
        System.out.println(s1 == s4);   // true

        // 字符串拼接优化
        // 编译器优化为 String s5 = "helloworld";
        String s5 = "hello" + "world";

        // 使用 StringBuilder（循环拼接）
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < 1000; i++) {
            sb.append(i);
        }

        // intern() 注意事项
        // 不要随意使用 intern()，可能造成永久代/元空间溢出
        // 只对确认为常量的字符串使用 intern()
    }
}
```

### 案例 4：生产环境 JVM 配置

```bash
# 8G 内存服务器，Java 应用配置
# 预留系统 2G，应用 6G

java -jar app.jar \
  -Xms4g \
  -Xmx4g \
  -Xmn2g \
  -Xss512k \
  -XX:MetaspaceSize=256m \
  -XX:MaxMetaspaceSize=512m \
  -XX:+UseG1GC \
  -XX:MaxGCPauseMillis=200 \
  -XX:G1HeapRegionSize=16m \
  -XX:InitiatingHeapOccupancyPercent=45 \
  -XX:+UseStringDeduplication \
  -XX:+PrintGCDetails \
  -XX:+PrintGCDateStamps \
  -XX:+PrintTenuringDistribution \
  -Xlog:gc*:file=/var/log/app/gc.log:time,tags:filecount=10,filesize=10m \
  -XX:+UseGCLogFileRotation \
  -XX:NumberOfGCLogFiles=10 \
  -XX:GCLogFileSize=10M \
  -XX:+HeapDumpOnOutOfMemoryError \
  -XX:HeapDumpPath=/var/log/app/heapdump.hprof \
  -XX:ErrorFile=/var/log/app/hs_err_pid%p.log \
  -XX:+ExitOnOutOfMemoryError

# 参数说明：
# -Xms4g -Xmx4g：固定堆大小，避免运行时扩容
# -Xmn2g：新生代 2G（50%）
# -Xss512k：线程栈 512K（支持约 4000 线程）
# -XX:MetaspaceSize=256m：元空间初始 256M
# -XX:+UseG1GC：使用 G1 收集器
# -XX:MaxGCPauseMillis=200：最大停顿 200ms
# -XX:InitiatingHeapOccupancyPercent=45：堆占用 45% 时开始 GC
# -XX:+UseStringDeduplication：启用字符串去重
# -XX:+HeapDumpOnOutOfMemoryError：OOM 时自动 dump
# -XX:+ExitOnOutOfMemoryError：OOM 时退出
```

## 七、性能监控

### Spring Boot Actuator 集成

```java
// pom.xml 依赖
/*
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-registry-prometheus</artifactId>
</dependency>
*/

// application.yml 配置
/*
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus,heapdump,threaddump
  endpoint:
    health:
      show-details: always
    metrics:
      enabled-by-default: true
      export:
        prometheus:
          enabled: true
  metrics:
    export:
      prometheus:
        enabled: true
    distribution:
      percentiles-histogram:
        http.server.requests: true
      percentiles:
        http.server.requests: 0.5,0.95,0.99
    tags:
      application: ${spring.application.name}
*/

// 自定义健康检查
@Component
public class DatabaseHealthIndicator implements HealthIndicator {

    @Override
    public Health health() {
        // 检查数据库连接
        boolean isHealthy = checkDatabase();

        if (isHealthy) {
            return Health.up()
                .withDetail("database", "MySQL")
                .withDetail("status", "connected")
                .build();
        } else {
            return Health.down()
                .withDetail("error", "Cannot connect to database")
                .build();
        }
    }

    private boolean checkDatabase() {
        // 实现检查逻辑
        return true;
    }
}

// 自定义指标
@Component
public class CustomMetrics {

    private final Counter orderCounter;
    private final Gauge activeConnections;

    public CustomMetrics(MeterRegistry registry) {
        // 计数器
        this.orderCounter = Counter.builder("orders.total")
            .description("Total number of orders")
            .tag("type", "online")
            .register(registry);

        // 仪表
        this.activeConnections = Gauge.builder("connections.active",
                this, CustomMetrics::getActiveConnections)
            .description("Number of active connections")
            .register(registry);
    }

    public void recordOrder() {
        orderCounter.increment();
    }

    private int getActiveConnections() {
        // 返回活跃连接数
        return 10;
    }
}
```

## 小结

本节学习了 JVM 调优：

- **JVM 架构** - 运行时数据区、内存模型
- **垃圾回收** - GC 算法、垃圾收集器
- **JVM 参数** - 内存配置、GC 配置、性能参数
- **监控工具** - 命令行工具、可视化工具
- **问题分析** - 内存泄漏、CPU 飙高、死锁、OOM
- **调优实战** - 大对象优化、集合优化、字符串优化
- **生产配置** - 生产环境 JVM 参数推荐
- **性能监控** - Actuator、自定义指标

## 实践练习

### 编程题
1. 编写一个程序模拟内存泄漏，用 jmap 导出堆转储文件，然后用 MAT 分析定位泄漏点。
2. 配置两套不同的 JVM 参数（分别使用 G1 和 Parallel GC），用 JMeter 压测同一个 Spring Boot 应用，对比 GC 日志和响应时间。

### 思考题
1. 什么场景下应该选择 G1 而不是 CMS？ZGC 相比 G1 的优势是什么？
2. 如果线上服务频繁 Full GC，你的排查步骤是什么？

### 自测题
1. JVM 堆内存分为哪几个区域？各有什么特点？
2. 可达性分析算法中，哪些对象可以作为 GC Roots？
3. CMS 收集器的四个主要阶段是什么？

下一步将学习算法与数据结构（→ `06-algorithms-data-structures.md`）。