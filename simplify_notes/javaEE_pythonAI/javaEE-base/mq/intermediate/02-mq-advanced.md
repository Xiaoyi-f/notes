# 消息队列进阶

## 一、概述

深入消息队列核心技术：消息可靠性、幂等性、顺序消息、事务消息、死信队列、延时消息。以 RocketMQ 为核心展开。

## 二、消息可靠性

### 生产者可靠性

```java
@Component
public class ReliableProducer {
    // 同步发送 + 重试
    public SendResult sendSync(String topic, String tag, Message msg) {
        return producer.send(msg, new SendCallback() {
            @Override
            public void onSuccess(SendResult result) {
                log.info("Send success: {}", result);
            }

            @Override
            public void onException(Throwable e) {
                log.error("Send failed, retrying", e);
                // 重试 3 次
                retryTemplate.execute(ctx -> {
                    producer.send(msg);
                    return null;
                });
            }
        }, 3000);  // 超时 3s
    }

    // 事务消息
    @Transactional
    public void createOrderWithTransaction(OrderDTO dto) {
        // 1. 发送半消息（prepare）
        Message msg = new Message("order-topic", "order", 
            JSON.toJSONBytes(dto));
        TransactionSendResult result = producer.sendMessageInTransaction(msg, null);
        
        // 2. 本地事务
        orderDao.insert(dto);
        
        // 3. commit/rollback 由回调查执行
        if (result.getLocalTransactionState() == LocalTransactionState.COMMIT_MESSAGE) {
            log.info("Order created and message committed");
        }
    }
}

// 事务消息监听器
@Component
public class OrderTransactionListener implements TransactionListener {
    @Autowired
    private OrderDao orderDao;

    @Override
    public LocalTransactionState executeLocalTransaction(Message msg, Object arg) {
        try {
            // 执行本地事务
            OrderDTO dto = JSON.parseObject(msg.getBody(), OrderDTO.class);
            orderDao.insert(dto);
            return LocalTransactionState.COMMIT_MESSAGE;
        } catch (Exception e) {
            return LocalTransactionState.ROLLBACK_MESSAGE;
        }
    }

    @Override
    public LocalTransactionState checkLocalTransaction(MessageExt msg) {
        // 回查：检查本地事务是否成功
        OrderDTO dto = JSON.parseObject(msg.getBody(), OrderDTO.class);
        boolean exists = orderDao.exists(dto.getOrderId());
        return exists ? LocalTransactionState.COMMIT_MESSAGE 
                      : LocalTransactionState.ROLLBACK_MESSAGE;
    }
}
```

### 消费者可靠性

```java
@Component
@RocketMQMessageListener(
    topic = "order-topic",
    consumerGroup = "order-consumer",
    consumeMode = ConsumeMode.ORDERLY,      // 顺序消费
    consumeThreadMax = 10,
    maxReconsumeTimes = 16                   // 最大重试次数
)
public class OrderConsumer implements RocketMQListener<MessageExt> {

    @Override
    public ConsumeConcurrentlyStatus onMessage(MessageExt msg) {
        try {
            OrderDTO order = JSON.parseObject(msg.getBody(), OrderDTO.class);
            
            // 幂等校验
            if (idempotentService.hasProcessed(order.getOrderId())) {
                return ConsumeConcurrentlyStatus.CONSUME_SUCCESS;
            }
            
            processOrder(order);
            
            // 记录处理成功
            idempotentService.markProcessed(order.getOrderId());
            
            return ConsumeConcurrentlyStatus.CONSUME_SUCCESS;
        } catch (Exception e) {
            log.error("Consume failed, retry later", e);
            // 重试次数超限后进入死信队列
            if (msg.getReconsumeTimes() >= 16) {
                log.warn("Retry exhausted, send to DLQ");
                return ConsumeConcurrentlyStatus.CONSUME_SUCCESS;
            }
            return ConsumeConcurrentlyStatus.RECONSUME_LATER;
        }
    }
}
```

## 三、幂等性方案

```java
@Component
public class IdempotentService {
    @Autowired
    private StringRedisTemplate redisTemplate;
    @Autowired
    private JdbcTemplate jdbcTemplate;

    // 方案一：Redis SETNX + 本地记录
    public boolean hasProcessed(String businessId) {
        // 利用 Redis 原子性
        Boolean success = redisTemplate.opsForValue()
            .setIfAbsent("idempotent:" + businessId, "1", Duration.ofHours(24));
        return Boolean.FALSE.equals(success);
    }

    public void markProcessed(String businessId) {
        // 落库保存
        jdbcTemplate.update(
            "INSERT INTO idempotent_record (business_id, create_time) VALUES (?, NOW())",
            businessId);
    }

    // 方案二：数据库唯一索引
    @Transactional
    public void processWithUniqueKey(OrderDTO order) {
        try {
            // 唯一索引保证最多执行一次
            orderDao.insertWithUniqueKey(order);
            processOrder(order);
        } catch (DuplicateKeyException e) {
            log.info("Duplicate order: {}", order.getOrderId());
        }
    }

    // 方案三：业务状态机
    @Transactional
    public void processWithStateMachine(Long orderId, OrderStatus from, OrderStatus to) {
        // UPDATE order SET status = ? WHERE id = ? AND status = ?
        int updated = orderDao.updateStatus(orderId, from, to);
        if (updated == 0) {
            throw new BusinessException("Order status not match");
        }
        // 继续后续处理
    }
}
```

## 四、顺序消息

### RocketMQ 顺序消息

```java
// 生产者：相同 orderId 发送到同一个 MessageQueue
public void sendOrderMessage(OrderEvent event) {
    Message msg = new Message("order-topic", "order",
        JSON.toJSONBytes(event));
    // 使用 orderId 作为选择 key，确保同一订单的消息在同一个队列
    SendResult result = producer.send(msg, 
        (mqs, ms) -> {
            int index = Math.abs(event.getOrderId().hashCode()) % mqs.size();
            return mqs.get(index);
        },
        event.getOrderId()  // 队列选择参数
    );
}

// 消费者：顺序消费
@Component
@RocketMQMessageListener(
    topic = "order-topic",
    consumerGroup = "order-consumer",
    consumeMode = ConsumeMode.ORDERLY  // 单线程消费每个队列
)
public class OrderEventConsumer implements RocketMQListener<MessageExt> {
    // 同一个订单的事件会被顺序消费
    // create → pay → deliver → confirm
}
```

### Kafka 顺序消息

```java
// Kafka 中分区内有序
ProducerRecord<String, String> record = new ProducerRecord<>(
    "order-events",
    orderId,          // 相同 key 进入同一分区
    JSON.toJSONString(event)
);
producer.send(record);

// 消费者单分区消费
@KafkaListener(topicPartitions = {
    @TopicPartition(topic = "order-events", partitions = {"0"})
})
public void consumeOrderEvent(String message) {
    // 单分区内是顺序的
}
```

## 五、死信队列与延时消息

### 死信队列

```java
// 消费者重试超过阈值后进入 %DLQ% 队列
// 需要单独消费死信队列做人工处理
@Component
@RocketMQMessageListener(
    topic = "%DLQ%order-consumer",   // 死信队列
    consumerGroup = "dlq-handler"
)
public class DeadLetterConsumer implements RocketMQListener<MessageExt> {
    @Override
    public ConsumeConcurrentlyStatus onMessage(MessageExt msg) {
        log.warn("Dead letter message: topic={}, keys={}, body={}",
            msg.getTopic(), msg.getKeys(), new String(msg.getBody()));
        // 记录到数据库，触发人工处理
        deadLetterDao.insert(msg);
        // 通知运维
        alertService.sendAlert("死信消息告警", msg.getKeys());
        return ConsumeConcurrentlyStatus.CONSUME_SUCCESS;
    }
}
```

### 延时消息

```java
// RocketMQ 延时等级 (messageDelayLevel)
// 1s 5s 10s 30s 1m 2m 3m 4m 5m 6m 7m 8m 9m 10m 20m 30m 1h 2h

// 发送延时消息
Message msg = new Message("order-topic", "order-cancel",
    JSON.toJSONBytes(orderDTO));
msg.setDelayTimeLevel(5);  // 1 分钟后检查支付状态
producer.send(msg);

// 自定义延时时间（RocketMQ 5.0+ 支持任意时间）
Message msg2 = new Message();
msg2.setStartDeliverTime(System.currentTimeMillis() + 3600000);  // 1h后
producer.send(msg2);
```

## 面试考点

1. **如何保证消息不丢失？** 生产者（同步发送 + 重试 + 事务消息）、Broker（持久化 + 同步刷盘）、消费者（手动 ACK + 重试）
2. **如何保证消息不重复消费？** 幂等性设计：唯一键、状态机、去重表
3. **RocketMQ 如何保证顺序消息？** 生产者选择队列 + 消费者单线程顺序消费
4. **事务消息的实现原理？** 半消息 → 执行本地事务 → commit/rollback → 回查

## 课后练习

1. 实现一个基于 RocketMQ 的事务消息的订单支付流程
2. 设计消息幂等处理的通用组件（注解 + AOP）
3. 实现延时消息的手动 ACK 和重试机制
4. 搭建 RocketMQ 双主双从集群并测试故障转移

## 自测题

1. RocketMQ 事务消息的回查机制基于？ A) 定时任务 B) 客户端触发 C) Broker 主动回查 D) A + C
2. 顺序消费模式下 ConsumeMode.ORDERLY 的作用？ A) 按发送顺序消费 B) 单线程消费队列 C) 全局有序 D) 批量消费
3. RocketMQ 默认最大重试次数是？ A) 3 B) 8 C) 16 D) 无限

**答案：** 1-D, 2-B, 3-C
