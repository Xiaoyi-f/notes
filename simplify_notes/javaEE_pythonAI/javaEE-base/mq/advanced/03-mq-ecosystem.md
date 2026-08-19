# 消息队列生态与架构

## 一、概述

对比主流消息队列（RocketMQ / Kafka / RabbitMQ / Pulsar）的架构差异，掌握消息中间件选型、性能调优、集群部署与监控。

## 二、MQ 对比

### 功能对比

| 特性 | RocketMQ | Kafka | RabbitMQ | Pulsar |
|------|----------|-------|----------|--------|
| 消息模型 | Queue + Topic | Partition | Exchange + Queue | Topic + Partition |
| 顺序消息 | 支持 | 分区内有序 | 单队列 | 分区内有序 |
| 事务消息 | 支持 | 支持(简单) | 支持 | 支持 |
| 延时消息 | 内置18级 | 不支持 | 插件 | 支持 |
| 死信队列 | 内置 | 支持 | 支持 | 支持 |
| 堆积能力 | 强 | 最强 | 弱 | 最强 |
| 吞吐量 | 10万+/s | 百万+/s | 万级/s | 百万+/s |
| 语言 | Java | Scala/Java | Erlang | Java |
| 运维复杂度 | 中 | 高 | 低 | 中 |

### 选型建议

| 场景 | 推荐 | 原因 |
|------|------|------|
| 业务消息（订单、支付） | RocketMQ | 事务消息、顺序消息 |
| 日志采集 / 大数据 | Kafka | 高吞吐、长期存储 |
| 企业总线 / 路由复杂 | RabbitMQ | 灵活的路由策略 |
| 云原生 / 多租户 | Pulsar | 存算分离、弹性扩缩 |

## 三、RocketMQ 集群架构

### DLedger 模式

```properties
# broker.conf (3 节点)
brokerClusterName=DefaultCluster
brokerName=broker-a
brokerId=0
listenPort=10911
namesrvAddr=ns1:9876;ns2:9876;ns3:9876
storePathRootDir=/data/rocketmq/store
commitLogLevel=INFO

# DLedger 配置
enableDLegerCommitLog=true
dLegerGroup=broker-a
dLegerPeers=n1:40911;n2:40911;n3:40911
dLegerSelfId=n1
```

### 生产部署建议

```yaml
# docker-compose.yml RocketMQ 4 节点
services:
  namesrv1:
    image: apache/rocketmq:5.1.4
    container_name: rmqnamesrv1
    ports:
      - "9876:9876"

  broker-a-master:
    image: apache/rocketmq:5.1.4
    environment:
      - "NAMESRV_ADDR=namesrv1:9876"
    volumes:
      - ./conf/broker-a.properties:/home/rocketmq/rocketmq-5.1.4/conf/broker.conf
      - ./data/broker-a:/home/rocketmq/store
    command: sh mqbroker -c /home/rocketmq/conf/broker.conf
    ports:
      - "10911:10911"

  broker-a-slave:
    # 从节点配置
    ...

  broker-b-master:
    # 另一个主节点
    ...
```

### 性能调优

```properties
# 系统调优
# /etc/sysctl.conf
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
vm.overcommit_memory = 1

# Broker 配置
# 刷盘策略
flushDiskType=ASYNC_FLUSH          # 异步刷盘
# 线程池
sendMessageThreadPoolNums=16
pullMessageThreadPoolNums=16
# 文件
mappedFileSizeCommitLog=1073741824  # CommitLog 1GB
mappedFileSizeConsumeQueue=300000
# 预热
warmMapedFileEnable=true
```

## 四、Kafka 深度

### 分区分配策略

```java
public class KafkaRebalanceListener implements ConsumerRebalanceListener {
    @Override
    public void onPartitionsRevoked(Collection<TopicPartition> partitions) {
        // 在 Rebalance 前提交偏移量
        consumer.commitSync();
    }

    @Override
    public void onPartitionsAssigned(Collection<TopicPartition> partitions) {
        // 重新分配后，从上次提交的位置继续消费
        log.info("Assigned partitions: {}", partitions);
    }
}

// 三种分区策略
// 1. RangeAssignor: 按分区范围分配（默认）
// 2. RoundRobinAssignor: 轮询分配
// 3. StickyAssignor: 粘性分配（尽量保持原有分配）
properties.put(ConsumerConfig.PARTITION_ASSIGNMENT_STRATEGY_CONFIG,
    StickyAssignor.class.getName());
```

### Kafka 生产者参数调优

```java
properties.put(ProducerConfig.BATCH_SIZE_CONFIG, 65536);           // 64KB 批量
properties.put(ProducerConfig.LINGER_MS_CONFIG, 10);              // 10ms 等待
properties.put(ProducerConfig.COMPRESSION_TYPE_CONFIG, "lz4");   // 压缩
properties.put(ProducerConfig.ACKS_CONFIG, "1");                  // 1 个副本确认
properties.put(ProducerConfig.BUFFER_MEMORY_CONFIG, 67108864);    // 64MB 缓冲区
properties.put(ProducerConfig.RETRIES_CONFIG, 3);
```

## 五、消息轨迹与监控

### RocketMQ 消息轨迹

```java
@Component
public class MessageTraceService {
    @Autowired
    private RocketMQTemplate rocketMqTemplate;

    // 开启消息轨迹
    // application.yml
    // rocketmq:
    //   producer:
    //     enable-msg-trace: true
    //   consumer:
    //     enable-msg-trace: true

    // 自定义追踪
    @EventListener
    public void onMessageEvent(TraceContext context) {
        MessageTrace trace = MessageTrace.builder()
            .messageId(context.getMessageId())
            .topic(context.getTopic())
            .producerHost(context.getProducerHost())
            .consumerGroup(context.getConsumerGroup())
            .costTime(context.getCostTime())
            .status(context.getStatus())
            .build();
        traceDao.insert(trace);
    }
}
```

### 监控指标

```java
@RestController
@RequestMapping("/admin/mq")
public class MQMonitorController {
    // 使用 Micrometer 监控 Broker 指标
    private final MeterRegistry meterRegistry;

    // 核心监控指标
    @GetMapping("/metrics")
    public Map<String, Object> metrics() {
        Map<String, Object> metrics = new HashMap<>();
        
        // 生产端
        metrics.put("producer.send.success", meterRegistry
            .counter("rocketmq.send.success").count());
        metrics.put("producer.send.failure", meterRegistry
            .counter("rocketmq.send.failure").count());
        
        // 消费端
        metrics.put("consumer.consume.rate", meterRegistry
            .gauge("rocketmq.consume.rate", new AtomicDouble(0)));
        metrics.put("consumer.accumulation", meterRegistry
            .gauge("rocketmq.accumulation", new AtomicLong(0)));
        
        // Broker
        metrics.put("broker.put.tps", getBrokerMetric("putTps"));
        metrics.put("broker.get.tps", getBrokerMetric("getTps"));
        
        return metrics;
    }
}
```

## 面试考点

1. **RocketMQ 和 Kafka 的存储模型差异？** RocketMQ 用 CommitLog + ConsumeQueue，Kafka 用 Partition Segment + Index
2. **消息堆积如何排查？** 消费者线程数不足、消费逻辑慢、死锁、网络问题
3. **RocketMQ DLedger 模式原理？** Raft 协议选主 + 自动故障转移
4. **Kafka 为什么快？** 顺序写磁盘、PageCache、零拷贝（sendfile）、批量压缩

## 课后练习

1. 搭建 RocketMQ 5.x DLedger 多副本集群
2. 实现基于 Kafka Streams 的实时计算（订单金额统计）
3. 实现 MQ 监控大盘：消息积压、消费延迟、生产 TPS
4. 对比压测 RocketMQ 和 Kafka 的吞吐量

## 自测题

1. Kafka 实现高吞吐的核心机制不包括？ A) 顺序写 B) 零拷贝 C) 内存映射 D) 每消息 ACK
2. RocketMQ CommitLog 文件默认多大？ A) 512MB B) 1GB C) 2GB D) 不限
3. Pulsar 相比 Kafka 的核心优势是？ A) 更高吞吐 B) 存算分离 C) 更低延迟 D) 更简单

**答案：** 1-D, 2-B, 3-B
