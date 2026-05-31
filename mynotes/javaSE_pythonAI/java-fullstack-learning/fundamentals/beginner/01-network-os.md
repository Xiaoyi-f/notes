# 计算机网络与操作系统

## 一、计算机网络

### 1. OSI 七层模型

```
┌─────────────────────────────────────────────┐
│              OSI 七层模型                        │
├─────────────────────────────────────────────┤
│                                                     │
│  7. 应用层 (Application)                          │
│     - HTTP, HTTPS, FTP, SMTP, DNS, SSH          │
│     - 提供应用程序接口                           │
│                                                     │
│  6. 表示层 (Presentation)                         │
│     - 数据格式化、加密、解密                       │
│     - SSL/TLS、JPEG、MPEG                          │
│                                                     │
│  5. 会话层 (Session)                              │
│     - 建立、管理、终止会话                         │
│     - TCP/UDP 端口、会话 ID                       │
│                                                     │
│  4. 传输层 (Transport)                             │
│     - 端到端的数据传输                           │
│     - TCP（可靠）、UDP（不可靠）                   │
│                                                     │
│  3. 网络层 (Network)                               │
│     - 数据包路由和转发                           │
│     - IP、ICMP、ARP、OSPF、BGP                     │
│                                                     │
│  2. 数据链路层 (Data Link)                         │
│     - 物理地址寻址、介质访问控制                   │
│     - Ethernet、MAC 地址、交换机                   │
│                                                     │
│  1. 物理层 (Physical)                              │
│     - 物理传输介质（光缆、网线、无线电）            │
│     - 比特流传输、信号编码                         │
│                                                     │
└─────────────────────────────────────────────┘
```

### 2. TCP/IP 四层模型

```
┌─────────────────────────────────────────────┐
│            TCP/IP 四层模型                        │
├─────────────────────────────────────────────┤
│                                                     │
│  应用层                          │
│     - 对应 OSI 的应用层、表示层、会话层         │
│     - HTTP, FTP, SMTP, DNS, Telnet                 │
│                                                     │
│  传输层                          │
│     - 对应 OSI 的传输层                           │
│     - TCP、UDP                                   │
│                                                     │
│  网络层                          │
│     - 对应 OSI 的网络层                           │
│     - IP、ICMP、ARP、RARP                          │
│                                                     │
│  网络接口层                        │
│     - 对应 OSI 的数据链路层、物理层                 │
│     - Ethernet、ARP、RARP、设备驱动程序             │
│                                                     │
└─────────────────────────────────────────────┘
```

### 3. HTTP 协议

```java
/**
 * HTTP 协议详解
 */

// HTTP 1.0
/*
- 每个请求都需要建立新的 TCP 连接
- 性能差，资源浪费
*/

// HTTP 1.1
/*
- 支持持久连接（Connection: keep-alive）
- 支持管道（Pipelining）
- 支持分块传输（Chunked）
- 新增状态码 100 Continue
- 新增缓存控制头
*/

// HTTP 2.0
/*
- 多路复用：一个 TCP 连接传输多个请求
- 二进制帧传输：性能更好
- 头部压缩：减少数据传输量
- 服务器推送（Server Push）：主动推送资源
*/

// HTTP 3.0
/*
- 基于 QUIC（UDP）协议
- 解决 TCP 队头阻塞问题
- 连接迁移：网络切换不断连
*/

// HTTP 状态码
/*
1xx 信息
- 100 Continue
- 101 Switching Protocols

2xx 成功
- 200 OK
- 201 Created
- 204 No Content

3xx 重定向
- 301 Moved Permanently（永久重定向）
- 302 Found（临时重定向）
- 304 Not Modified（缓存未修改）

4xx 客户端错误
- 400 Bad Request
- 401 Unauthorized
- 403 Forbidden
- 404 Not Found
- 429 Too Many Requests

5xx 服务器错误
- 500 Internal Server Error
- 502 Bad Gateway
- 503 Service Unavailable
- 504 Gateway Timeout
*/
```

### 4. TCP vs UDP

```java
/**
 * TCP vs UDP 对比
 */

// TCP (Transmission Control Protocol) - 传输控制协议
/*
特点：
1. 面向连接：需要三次握手建立连接
2. 可靠传输：确认机制、重传机制
3. 有序传输：保证数据顺序
4. 流量控制：滑动窗口
5. 拥塞控制：慢启动、拥塞避免

应用场景：
- HTTP/HTTPS
- FTP
- SMTP
- SSH
*/

// UDP (User Datagram Protocol) - 用户数据报协议
/*
特点：
1. 无连接：不需要建立连接
2. 不可靠：不保证数据到达、不保证数据顺序
3. 无序传输：数据可能乱序到达
4. 无流量控制、无拥塞控制

应用场景：
- DNS
- 视频会议（对实时性要求高）
- 直播
- 游戏通信（对延迟敏感）
*/

// TCP 三次握手
/*
1. 客户端发送 SYN 包（SYN=1, seq=x）
2. 服务端收到 SYN，发送 SYN+ACK 包（SYN=1, ACK=1, seq=y, ack=x+1）
3. 客户端收到 SYN+ACK，发送 ACK 包（ACK=1, ack=y+1）
4. 连接建立完成

三次握手的原因：
- 防止已失效的连接请求突然又传到服务端，造成错误
*/

// TCP 四次挥手
/*
1. 客户端发送 FIN 包（FIN=1, seq=u）
2. 服务端收到 FIN，发送 ACK 包（ACK=1, ack=u+1）
3. 服务端数据发送完毕，发送 FIN 包（FIN=1, seq=v）
4. 客户端收到 FIN，发送 ACK 包（ACK=1, ack=v+1）
5. 连接关闭

四次挥手的原因：
- TCP 是全双工协议，双方都可以发送和接收数据
- 服务端发送完数据后，还需要接收客户端的数据
*/
```

## 二、操作系统

### 1. 进程与线程

```java
/**
 * 进程与线程
 */

// 进程（Process）
/*
- 程序的一次执行过程
- 资源分配的基本单位
- 独立的内存空间
- 进程间通信（IPC）：管道、消息队列、共享内存、信号量、套接字
*/

// 线程（Thread）
/*
- 进程内的执行单元
- CPU 调度的基本单位
- 共享进程的内存空间
- 线程间通信：共享内存、变量、锁
*/

// Java 中的线程
public class ThreadDemo {
    public static void main(String[] args) {
        // 1. 创建线程方式一：继承 Thread 类
        MyThread thread1 = new MyThread();
        thread1.start();

        // 2. 创建线程方式二：实现 Runnable 接口
        Thread thread2 = new Thread(new MyRunnable());
        thread2.start();

        // 3. 创建线程方式三：使用 Lambda 表达式
        Thread thread3 = new Thread(() -> {
            System.out.println("Lambda 线程");
        });
        thread3.start();

        // 4. 创建线程方式四：使用线程池
        ExecutorService executor = Executors.newFixedThreadPool(4);
        executor.submit(() -> {
            System.out.println("线程池线程");
        });
        executor.shutdown();
    }

    static class MyThread extends Thread {
        @Override
        public void run() {
            System.out.println("继承 Thread 类");
        }
    }

    static class MyRunnable implements Runnable {
        @Override
        public void run() {
            System.out.println("实现 Runnable 接口");
        }
    }
}

// 进程状态转换
/*
创建 → 就绪 → 运行 → 阻塞 → 终止
  ↑           ↓
  └─────────┘
*/
```

### 2. 进程调度算法

```java
/**
 * 进程调度算法
 */

// 1. 先来先服务 (FCFS)
/*
优点：公平、简单
缺点：可能导致"护航效应"（长任务阻塞短任务）
*/

// 2. 短作业优先 (SJF)
/*
优点：平均等待时间最短
缺点：可能导致"饥饿"（长任务永远得不到执行）
*/

// 3. 时间片轮转 (RR)
/*
优点：公平、响应时间好
缺点：上下文切换开销大
*/

// 4. 优先级调度
/*
优点：可以根据重要程度调度
缺点：可能导致"饥饿"
*/

// 5. 多级反馈队列 (MLFQ)
/*
优点：兼顾短任务和长任务
实现：
  - 多个队列，优先级不同
  - 时间片不同
  - 新任务进入高优先级队列
  - 用完时间片后降级
*/
```

### 3. 死锁

```java
/**
 * 死锁及其解决
 */

// 死锁条件
/*
1. 互斥：资源不能同时使用
2. 请求与保持：持有资源的同时请求其他资源
3. 不剥夺：资源不能被强制剥夺
4. 循环等待：多个进程形成等待环
*/

// 死锁预防
public class DeadlockPrevention {
    // 1. 资源有序分配（破坏循环等待）
    private static final Object lock1 = new Object();
    private static final Object lock2 = new Object();

    public void method1() {
        synchronized (lock1) {
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {}
            synchronized (lock2) {
                // 业务逻辑
            }
        }
    }

    public void method2() {
        synchronized (lock1) {  // 与 method1 顺序一致
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {}
            synchronized (lock2) {
                // 业务逻辑
            }
        }
    }

    // 2. 使用 tryLock（破坏不剥夺）
    public void tryLockMethod() {
        try {
            if (lock1.tryLock(1, TimeUnit.SECONDS)) {
                if (lock2.tryLock(1, TimeUnit.SECONDS)) {
                    // 获取锁成功
                    // 业务逻辑
                } else {
                    // 获取 lock2 失败，释放 lock1
                    lock1.unlock();
                }
            } else {
                // 获取 lock1 夳败
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } finally {
            if (Thread.holdsLock(lock1)) {
                lock1.unlock();
            }
        }
    }
}

// 死锁避免
public class DeadlockAvoidance {
    private static final Lock lock = new ReentrantLock();

    public void transfer(Account from, Account to, int amount) {
        // 总是先锁 ID 小的账户，破坏循环等待
        Account first = from.getId() < to.getId() ? from : to;
        Account second = from.getId() < to.getId() ? to : from;

        lock.lock();
        try {
            first.debit(amount);
            second.credit(amount);
        } finally {
            lock.unlock();
        }
    }
}

// 死锁检测
public class DeadlockDetection {
    public static boolean detectDeadlock() {
        // 使用 JMX 或死锁检测工具
        ThreadMXBean threadMXBean = ManagementFactory.getThreadMXBean();
        long[] deadlockedThreads = threadMXBean.findDeadlockedThreads();

        return deadlockedThreads != null && deadlockedThreads.length > 0;
    }
}
```

### 4. 内存管理

```java
/**
 * 内存管理
 */

// 内存分配方式
/*
1. 连续分配（连续内存区域）
   - 优点：简单高效
   - 缺点：外部碎片

2. 分页分配（固定大小页）
   - 优点：无外部碎片，内存利用率高
   - 缺点：内部碎片，页表开销

3. 分段分配（按逻辑分段）
   - 优点：逻辑清晰，易于共享和保护
   - 缺点：外部碎片

4. 段页式（结合分段和分页）
   - 优点：兼具两者优点
   - 缺点：管理复杂
*/

// 虚拟内存
/*
原理：
- 将物理内存和外存（磁盘）统一编址
- 程序看到的虚拟地址空间大于物理内存
- 需要时将数据在物理内存和磁盘间交换

优势：
- 程序可以使用比物理内存更大的空间
- 多个程序可以同时运行
- 内存保护：每个进程有独立的地址空间
*/

// 页面置换算法
// 1. 先进先出 (FIFO)
// 2. 最近最久未使用 (LRU)
// 3. 最不常用 (LFU)
// 4. 时钟算法 (Clock)
```

### 5. 文件系统

```java
/**
 * 文件系统
 */

// 文件系统结构
/*
┌─────────────────────────────────────────────┐
│              文件系统结构                        │
├─────────────────────────────────────────────┤
│                                                     │
│  超级块 (Superblock)                             │
│  - 文件系统信息、空闲块列表                         │
│                                                     │
│  I 节点表 (Inode Table)                           │
│  - I 节点：文件的元数据                           │
│  - I 节点表：存储所有 I 节点                     │
│                                                     │
│  数据块 (Data Blocks)                             │
│  - 文件的实际数据                                 │
│                                                     │
└─────────────────────────────────────────────┘
*/

// 文件类型
/*
1. 普通文件
2. 目录文件
3. 设备文件
4. 符号文件
5. 套接文件（软链接、硬链接）
*/

// Linux 文件权限
/*
权限位：rwxrwxrwxrwx
- 9 位，3 组：
  - 前 3 位：所有者权限
  - 中 3 位：组用户权限
  - 后 3 位：其他用户权限

权限含义：
- r（读）：可以读取文件内容，列出目录
- w（写）：可以修改文件内容，在目录中创建/删除文件
- x（执行）：可以执行文件，进入目录

权限修改：
chmod 755 file  // rwxr-xr-x
chmod u+x file   // 所有者添加执行权限
chmod g+w file   // 组用户添加写权限
*/
```

## 三、Linux 常用命令

### 1. 文件操作

```bash
# 文件查看
ls -la           # 列出所有文件（包括隐藏文件）
ls -lh           # 人类可读格式显示

# 文件操作
touch file.txt   # 创建文件
cp file1 file2   # 复制文件
mv file1 file2   # 重命名/移动文件
rm file.txt       # 删除文件
rm -rf dir       # 递归删除目录

# 文件内容查看
cat file.txt      # 查看全部内容
more file.txt     # 分页查看
less file.txt     # 分页查看（可上下翻页）
head -n 10 file.txt # 查看前 10 行
tail -n 10 file.txt # 查看后 10 行
tail -f file.txt   # 实时查看文件内容

# 文件搜索
find . -name "*.java"            # 按名称查找
find . -type f -name "*.java"     # 查找文件
find . -type d -name "test"       # 查找目录
grep "keyword" file.txt          # 在文件中搜索关键词
grep -r "keyword" .               # 递归搜索目录
```

### 2. 进程管理

```bash
# 进程查看
ps aux                    # 查看所有进程
ps -ef                    # 查看所有进程（完整格式）
top                       # 实时查看进程状态

# 进程控制
kill PID                  # 终止进程
kill -9 PID               # 强制终止进程
kill -15 PID              # 正常终止进程

# 后台任务
command &                 # 后台运行
nohup command &            # 关闭终端后继续运行
jobs                      # 查看后台任务
fg %1                     # 将任务 1 调到前台
bg %1                     # 将任务 1 调到后台
```

### 3. 网络命令

```bash
# 网络状态
netstat -an               # 查看所有网络连接
netstat -tuln              # 查看 TCP 监听端口
netstat -s                 # 查看网络统计

# 网络测试
ping host                  # 测试网络连通性
curl http://example.com   # 测试 HTTP 请求
telnet host port          # 测试端口连通性

# 网络配置
ifconfig                   # 查看网络接口配置
ip addr                    # 查看网络接口配置
route -n                   # 查看路由表
```

### 4. 系统监控

```bash
# 系统信息
uname -a                  # 查看系统信息
df -h                     # 查看磁盘使用情况
du -sh .                  # 查看目录大小
free -h                    # 查看内存使用情况
uptime                    # 查看系统负载

# 系统日志
dmesg                     # 查看系统日志
tail -f /var/log/syslog  # 实时查看系统日志
tail -f /var/log/auth.log  # 查看认证日志

# 性能监控
iostat                    # 查看磁盘 I/O 状态
vmstat                    # 查看虚拟内存统计
sar                        # 系统活动报告
```

### 5. Shell 脚本

```bash
#!/bin/bash

# 变量定义
NAME="John"
AGE=30

# 条件判断
if [ $AGE -gt 18 ]; then
    echo "$NAME 是成年人"
else
    echo "$NAME 是未成年人"
fi

# 循环
for i in {1..10}; do
    echo "数字: $i"
done

# 函数
function greet() {
    echo "Hello, $1!"
}

greet "World"

# 函数调用
result=$(greet "World")
echo "结果: $result"

# 命令替换
current_date=$(date +%Y-%m-%d)
echo "当前日期: $current_date"

# 管道操作
ls | grep ".java" | wc -l  # 统计 Java 文件数量

# 重定向
ls > output.txt           # 输出到文件
ls >> output.txt          # 追加到文件
ls 2> error.log            # 错误输出到文件
command &> /dev/null        # 忽略所有输出
```

## 小结

本节学习了计算机网络与操作系统：

- **网络模型** - OSI 七层模型、TCP/IP 四层模型
- **HTTP 协议** - HTTP 1.0/1.1/2.0/3.0、状态码
- **传输协议** - TCP vs UDP、三次握手、四次挥手
- **进程线程** - 进程状态、线程创建、线程通信
- **调度算法** - FCFS、SJF、RR、优先级、MLFQ
- **死锁** - 死锁条件、预防、避免、检测
- **内存管理** - 分配方式、虚拟内存、页面置换
- **文件系统** - 文件系统结构、文件类型、权限
- **Linux 命令** - 文件操作、进程管理、网络、监控、Shell

## 实践练习

### 编程题
1. 用 Java NIO 实现一个简单的 HTTP 服务器，支持静态文件访问和基本的 GET/POST 请求处理。
2. 编写程序模拟 TCP 的三次握手和四次挥手过程，打印每个阶段的状态转换。

### 思考题
1. TCP 和 UDP 的根本区别是什么？为什么游戏和视频通话通常用 UDP？
2. 进程和线程的本质区别？协程相比线程有什么优势？

### 自测题
1. OSI 七层模型和 TCP/IP 四层模型的对应关系？
2. HTTP 1.1、HTTP 2、HTTP 3 的主要区别？
3. 死锁的四个必要条件？

下一步将学习面试指南（→ `interview/beginner/01-interview-guide.md`）。