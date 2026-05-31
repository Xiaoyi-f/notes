# 性能测试基础

## 一、概述

性能测试是保障系统质量的关键环节。掌握性能测试方法论、常用工具、指标分析、瓶颈定位。

## 二、性能测试类型

| 类型 | 目的 | 方法 |
|------|------|------|
| 负载测试 | 验证系统在预期负载下的表现 | 逐步增加并发到目标值 |
| 压力测试 | 找到系统的极限和瓶颈 | 持续增加负载直到崩溃 |
| 稳定性测试 | 验证长期运行的可靠性 | 70-80% 负载运行 24-72h |
| 峰值测试 | 验证突发流量的处理能力 | 瞬间加载 2-5 倍正常流量 |
| 容量规划 | 确定资源与吞吐量的关系 | 不同配置下的基准对比 |

## 三、核心指标

| 指标 | 说明 | 健康值 |
|------|------|--------|
| TPS/QPS | 每秒事务数/查询数 | 越高越好 |
| RT (Response Time) | 响应时间 | P99 < 500ms |
| 并发数 | 同时处理的请求数 | 与 TPS 成正比 |
| 错误率 | 失败请求占比 | < 0.1% |
| CPU 使用率 | 处理器占用 | < 80% |
| GC 暂停 | JVM GC 暂停时间 | P99 < 200ms |

## 四、JMeter 实战

### 测试计划结构

```xml
Test Plan
├── Thread Group (100 threads, 10s ramp-up)
│   ├── HTTP Request Defaults
│   ├── CSV Data Set Config (参数化)
│   ├── HTTP Request (/api/users)
│   │   ├── HTTP Header Manager
│   │   └── JSON Extractor (提取响应)
│   ├── Transaction Controller
│   └── Listeners
│       ├── Summary Report
│       ├── Aggregate Report
│       └── Graph Results
├── JDBC Connection Configuration
├── JDBC Request (数据库直接验证)
└── Backend Listener (InfluxDB + Grafana)
```

### 分布式压测

```bash
# Master 节点
jmeter -n -t test-plan.jmx -l results.jtl -e -o report/ \
  -R slave1:1099,slave2:1099 \
  -Gthreads=500 -Gduration=600

# Slave 节点（启动代理）
jmeter-server -Djava.rmi.server.hostname=192.168.1.10
```

## 五、关键指标采集

### Java 应用侧

```java
@Component
public class PerformanceMetrics {
    private final MeterRegistry registry;

    public PerformanceMetrics(MeterRegistry registry) {
        this.registry = registry;
        // JVM 指标
        registry.gauge("jvm.memory.used", getUsedMemory());
        registry.gauge("jvm.threads.live", Thread.activeCount());
        registry.gauge("jvm.gc.pause", getGcPauseTime());
    }

    @Timed(value = "api.latency", percentiles = {0.5, 0.95, 0.99})
    @GetMapping("/api/users")
    public List<User> getUsers() {
        return userService.list();
    }

    private double getGcPauseTime() {
        for (GarbageCollectorMXBean gc : ManagementFactory
            .getGarbageCollectorMXBeans()) {
            return gc.getCollectionTime();
        }
        return 0;
    }
}
```

### 系统侧

```bash
# CPU
top -bn1 | grep "Cpu(s)"
mpstat -P ALL 1 5

# 内存
free -h
vmstat 1 5

# 磁盘 IO
iostat -x 1 5

# 网络
netstat -s
sar -n DEV 1 5

# 进程级
pidstat -u -r -d -p $PID 1 5
```

## 六、常见瓶颈定位

```java
// 使用 Arthas 定位问题
// dashboard          - 实时监控面板
// thread             - 查看线程栈
// stack com.example.UserService - 查看方法调用栈
// trace com.example.UserService getUser - 链路追踪
// monitor com.example.UserService getUser - 方法调用统计
// profiler start/stop - CPU 热点采样

// 火焰图分析
// profiler start --event cpu
// 执行测试
// profiler stop --format html
```

## 课后练习

1. 使用 JMeter 对 HTTP API 进行 100/500/1000 并发压测
2. 编写性能脚本监控 JVM GC 情况（GCeasy 分析 GC 日志）
3. 使用 Arthas 定位一个 CPU 100% 的线程问题
4. 通过压力测试确定系统的最大 TPS 和最佳并发数

## 自测题

1. 以下哪个指标最适合衡量系统吞吐量？ A) 响应时间 B) TPS C) CPU 使用率 D) GC 频率
2. 压力测试的目的是？ A) 验证预期负载 B) 找到系统极限 C) 验证稳定性 D) 测试功能
3. JMeter 中用来模拟多用户并发的是？ A) Sampler B) Thread Group C) Listener D) Assertion

**答案：** 1-B, 2-B, 3-B
