# 消息队列（MQ）

## 一、消息队列概述

消息队列是一种应用程序间的通信方式，用于解耦系统、异步处理、流量削峰。

### 常见消息队列对比

```
┌─────────────┬────────────┬───────────┬────────────┬──────────┐
│     特性     │   RabbitMQ │   Kafka   │ RocketMQ  │  Redis   │
├─────────────┼────────────┼───────────┼────────────┼──────────┤
│  可靠性     │    高      │    高     │    高     │   中     │
│  吞吐量     │    中      │   极高    │    高     │   高     │
│  延迟       │    低      │    中     │    低     │   极低    │
│  复杂度     │   中高     │    高     │    中     │   低     │
│  功能丰富度  │   最高     │   高      │    高     │   低     │
│  适用场景   │ 复杂业务   │ 大数据流  │ 普通业务  │ 简单队列  │
└─────────────┴────────────┴───────────┴────────────┴──────────┘
```

## 二、RocketMQ

### 1. 基础配置

```java
// 依赖
/*
<dependency>
    <groupId>org.apache.rocketmq</groupId>
    <artifactId>rocketmq-spring-boot-starter</artifactId>
    <version>2.2.3</version>
</dependency>
*/

// application.yml
/*
rocketmq:
  name-server: localhost:9876
  producer:
    group: my-producer-group
    send-message-timeout: 3000
    retry-times-when-send-failed: 2
    access-key: ${rocketmq.accessKey:}
    secret-key: ${rocketmq.secretKey:}
*/

// 生产者配置
@Configuration
public class RocketMQProducerConfig {

    @Value("${rocketmq.name-server}")
    private String nameServer;

    @Value("${rocketmq.producer.group}")
    private String producerGroup;

    @Bean
    public DefaultMQProducer defaultMQProducer() throws MQClientException {
        DefaultMQProducer producer = new DefaultMQProducer(producerGroup);
        producer.setNamesrvAddr(nameServer);
        producer.setRetryTimesWhenSendFailed(2);
        producer.setSendMsgTimeout(3000);

        // 开启消息轨迹
        producer.setUseTLS(false);  // 生产环境建议开启

        producer.start();
        return producer;
    }
}
```

### 2. 消息发送

```java
@Service
@Slf4j
public class MessageProducer {

    private final DefaultMQProducer producer;

    public MessageProducer(DefaultMQProducer producer) {
        this.producer = producer;
    }

    // 同步发送（可靠性高，适用于重要消息）
    public SendResult sendSync(String topic, String tag, String key, Object message) {
        try {
            Message mqMessage = new Message(
                topic,
                tag,
                key,
                JSON.toJSONString(message).getBytes(StandardCharsets.UTF_8)
            );

            SendResult result = producer.send(mqMessage);

            log.info("消息发送成功: topic={}, tag={}, key={}, msgId={}",
                topic, tag, key, result.getMsgId());

            return result;
        } catch (Exception e) {
            log.error("消息发送失败: topic={}, tag={}, key={}", topic, tag, key, e);
            throw new BusinessException("消息发送失败");
        }
    }

    // 异步发送（高性能，适用于一般消息）
    public void sendAsync(String topic, String tag, String key, Object message) {
        try {
            Message mqMessage = new Message(
                topic,
                tag,
                key,
                JSON.toJSONString(message).getBytes(StandardCharsets.UTF_8)
            );

            producer.send(mqMessage, new SendCallback() {
                @Override
                public void onSuccess(SendResult sendResult) {
                    log.info("异步消息发送成功: topic={}, tag={}, key={}, msgId={}",
                        topic, tag, key, sendResult.getMsgId());
                }

                @Override
                public void onException(Throwable e) {
                    log.error("异步消息发送失败: topic={}, tag={}, key={}", topic, tag, key, e);
                    // 失败重试或记录到数据库
                }
            });
        } catch (Exception e) {
            log.error("异步消息发送异常", e);
        }
    }

    // 单向发送（最高性能，不关心结果，适用于日志等）
    public void sendOneWay(String topic, String tag, String key, Object message) {
        try {
            Message mqMessage = new Message(
                topic,
                tag,
                key,
                JSON.toJSONString(message).getBytes(StandardCharsets.UTF_8)
            );

            producer.sendOneway(mqMessage);

            log.debug("单向消息发送: topic={}, tag={}, key={}", topic, tag, key);

        } catch (Exception e) {
            log.error("单向消息发送失败", e);
        }
    }

    // 发送顺序消息
    public void sendOrderedMessage(String topic, String tag, String key,
                                      Object message, String orderId) {
        try {
            Message mqMessage = new Message(
                topic,
                tag,
                key,
                JSON.toJSONString(message).getBytes(StandardCharsets.UTF_8)
            );

            producer.send(mqMessage, new MessageQueueSelector() {
                @Override
                public MessageQueue select(List<MessageQueue> mqs, Message msg, Object arg) {
                    // 根据订单ID选择队列，保证同一订单的消息进入同一队列
                    Long orderId = (Long) arg;
                    int index = (int) (orderId % mqs.size());
                    return mqs.get(index);
                }
            }, orderId);

            log.info("顺序消息发送: topic={}, orderId={}", topic, orderId);

        } catch (Exception e) {
            log.error("顺序消息发送失败: orderId={}", orderId, e);
        }
    }

    // 发送事务消息
    public void sendTransactionalMessage(String topic, String tag, String key,
                                          TransactionMessage message) {
        try {
            TransactionMQProducer transactionProducer = new TransactionMQProducer("transaction-producer");
            transactionProducer.setNamesrvAddr(producer.getNamesrvAddr());

            // 设置事务监听器
            transactionProducer.setTransactionListener(new TransactionListener() {
                @Override
                public LocalTransactionState executeLocalTransaction(Message msg, Object arg) {
                    // 执行本地事务
                    try {
                        // 调用本地服务执行业务逻辑
                        boolean success = localTransactionExecutor.execute(message);

                        return success ? LocalTransactionState.COMMIT_MESSAGE
                                         : LocalTransactionState.ROLLBACK_MESSAGE;

                    } catch (Exception e) {
                        log.error("本地事务执行失败", e);
                        return LocalTransactionState.ROLLBACK_MESSAGE;
                    }
                }

                @Override
                public LocalTransactionState checkLocalTransaction(MessageExt msg) {
                    // 检查本地事务状态
                    try {
                        TransactionStatus status = localTransactionExecutor.checkStatus(msg.getTransactionId());

                        return switch (status) {
                            case COMMITTED -> LocalTransactionState.COMMIT_MESSAGE;
                            case ROLLED_BACK -> LocalTransactionState.ROLLBACK_MESSAGE;
                            case UNKNOWN -> LocalTransactionState.UNKNOW;
                        };

                    } catch (Exception e) {
                        log.error("检查本地事务状态失败", e);
                        return LocalTransactionState.UNKNOW;
                    }
                }
            });

            // 开启事务消息的回查线程池
            ExecutorService executorService = new ThreadPoolExecutor(
                2, 5, 100, TimeUnit.SECONDS,
                new LinkedBlockingQueue<>(1000)
            );
            transactionProducer.setExecutorService(executorService);

            transactionProducer.start();

            Message mqMessage = new Message(
                topic,
                tag,
                key,
                JSON.toJSONString(message).getBytes(StandardCharsets.UTF_8)
            );

            transactionProducer.sendMessageInTransaction(mqMessage, null);

            log.info("事务消息发送: topic={}, transactionId={}", topic, message.getTransactionId());

        } catch (Exception e) {
            log.error("事务消息发送失败", e);
        }
    }

    // 发送延时消息
    public void sendDelayMessage(String topic, String tag, String key,
                                   Object message, int delayLevel) {
        try {
            Message mqMessage = new Message(
                topic,
                tag,
                key,
                JSON.toJSONString(message).getBytes(StandardCharsets.UTF_8)
            );

            // 延时级别: 1s 5s 10s 30s 1m 2m 3m 4m 5m 6m 7m 8m 9m 10m 20m 30m 1h 2h
            mqMessage.setDelayTimeLevel(delayLevel);

            producer.send(mqMessage);

            log.info("延时消息发送: topic={}, delayLevel={}", topic, delayLevel);

        } catch (Exception e) {
            log.error("延时消息发送失败", e);
        }
    }

    // 批量发送
    public void sendBatch(String topic, String tag, List<Object> messages) {
        try {
            List<Message> mqMessages = messages.stream()
                .map(msg -> new Message(
                    topic,
                    tag,
                    UUID.randomUUID().toString(),
                    JSON.toJSONString(msg).getBytes(StandardCharsets.UTF_8)
                ))
                .collect(Collectors.toList());

            producer.send(mqMessages);

            log.info("批量消息发送: topic={}, count={}", topic, messages.size());

        } catch (Exception e) {
            log.error("批量消息发送失败", e);
        }
    }
}
```

### 3. 消息消费

```java
@Service
@Slf4j
public class MessageConsumer {

    // 普通消息消费
    @RocketMQMessageListener(
        topic = "user-topic",
        consumerGroup = "user-consumer-group",
        selectorExpression = "*",
        messageModel = MessageModel.CLUSTERING  // 集群模式
    )
    public class UserMessageConsumer implements RocketMQListener<UserMessage> {

        @Override
        public void onMessage(UserMessage message) {
            log.info("收到用户消息: {}", message);

            try {
                // 处理业务逻辑
                processUserMessage(message);

                // 确认消息（默认自动确认）
                // 如果处理失败，可以抛出异常触发重试

            } catch (BusinessException e) {
                log.error("业务处理失败: {}", message, e);
                // 不重试
            } catch (Exception e) {
                log.error("系统异常，将重试: {}", message, e);
                throw e;  // 触发重试
            }
        }

        private void processUserMessage(UserMessage message) {
            // 具体业务逻辑
        }
    }

    // 顺序消息消费
    @RocketMQMessageListener(
        topic = "order-topic",
        consumerGroup = "order-consumer-group",
        consumeMode = ConsumeMode.ORDERLY,  // 顺序消费
        maxReconsumeTimes = 3
    )
    public class OrderMessageConsumer implements RocketMQListener<OrderMessage> {

        @Override
        public void onMessage(OrderMessage message) {
            log.info("收到订单消息: {}", message);

            try {
                processOrderMessage(message);

            } catch (Exception e) {
                log.error("订单消息处理失败: {}", message, e);
                throw e;
            }
        }

        private void processOrderMessage(OrderMessage message) {
            // 按订单ID处理
        }
    }

    // 事务消息消费
    @RocketMQMessageListener(
        topic = "payment-topic",
        consumerGroup = "payment-consumer-group",
        consumeThreadNumber = 4,
        consumeThreadMax = 8
    )
    public class PaymentMessageConsumer implements RocketMQListener<PaymentMessage> {

        @Override
        public void onMessage(PaymentMessage message) {
            log.info("收到支付消息: {}", message);

            try {
                processPaymentMessage(message);

            } catch (Exception e) {
                log.error("支付消息处理失败: {}", message, e);

                // 处理失败，发送到死信队列
                sendToDeadQueue(message);
            }
        }

        private void processPaymentMessage(PaymentMessage message) {
            // 支付处理逻辑
        }

        private void sendToDeadQueue(PaymentMessage message) {
            // 发送到死信队列
        }
    }

    // 广播消息消费
    @RocketMQMessageListener(
        topic = "broadcast-topic",
        consumerGroup = "broadcast-consumer-group",
        messageModel = MessageModel.BROADCASTING  // 广播模式
    )
    public class BroadcastMessageConsumer implements RocketMQListener<String> {

        @Override
        public void onMessage(String message) {
            log.info("收到广播消息: {}", message);
            // 广播消息处理
        }
    }

    // Tag 过滤消费
    @RocketMQMessageListener(
        topic = "product-topic",
        consumerGroup = "product-consumer-group",
        selectorExpression = "tagA || tagB",  // SQL92 表达式
        selectorType = SelectorType.SQL92
    )
    public class TagFilterMessageConsumer implements RocketMQListener<ProductMessage> {

        @Override
        public void onMessage(ProductMessage message) {
            log.info("收到产品消息: {}", message);
        }
    }

    // 消费者配置
    @Bean
    public DefaultRocketMQListenerContainerFactory rocketMQListenerContainerFactory(
            RocketMQProperties properties) {

        DefaultRocketMQListenerContainerFactory factory =
            new DefaultRocketMQListenerContainerFactory();

        factory.setConsumerGroup("default-consumer-group");
        factory.setNameServer(properties.getNameServer());

        // 消费端配置
        factory.setMaxReconsumeTimes(3);  // 最大重试次数
        factory.setSuspendCurrentQueueTimeMillis(10000);  // 挂起当前队列时间
        factory.setConsumeTimeout(15 * 60 * 1000);  // 消费超时时间

        // 线程配置
        factory.setConsumeThreadMin(4);
        factory.setConsumeThreadMax(8);

        // 消息模式
        factory.setMessageModel(MessageModel.CLUSTERING);

        // 顺序消费
        factory.setConsumeMode(ConsumeMode.CONCURRENTLY);

        // 消息失败处理策略
        factory.setAckMode(AckMode.ACK_MANUALLY);

        return factory;
    }
}
```

## 三、RabbitMQ

### 1. 基础配置

```java
// 依赖
/*
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-amqp</artifactId>
</dependency>
*/

// application.yml
/*
spring:
  rabbitmq:
    host: localhost
    port: 5672
    username: guest
    password: guest
    virtual-host: /
    listener:
      simple:
        acknowledge-mode: manual  # 手动确认
        retry:
          enabled: true
          max-attempts: 3
          initial-interval: 1000
          multiplier: 2
    publisher-confirm-type: correlated  # 发布确认
    publisher-returns: true
*/

// 配置类
@Configuration
public class RabbitMQConfig {

    @Bean
    public Queue orderQueue() {
        return QueueBuilder.durable("order.queue")
            .withArgument("x-dead-letter-exchange", "dlx.exchange")
            .withArgument("x-dead-letter-routing-key", "dlx.routing.key")
            .build();
    }

    @Bean
    public Queue directQueue() {
        return QueueBuilder.durable("direct.queue").build();
    }

    @Bean
    public TopicExchange topicExchange() {
        return ExchangeBuilder.topicExchange("topic.exchange").durable(true).build();
    }

    @Bean
    public DirectExchange directExchange() {
        return ExchangeBuilder.directExchange("direct.exchange").durable(true).build();
    }

    @Bean
    public Binding orderBinding(Queue orderQueue, TopicExchange topicExchange) {
        return BindingBuilder.bind(orderQueue)
            .to(topicExchange)
            .with("order.*");
    }

    @Bean
    public Binding directBinding(Queue directQueue, DirectExchange directExchange) {
        return BindingBuilder.bind(directQueue)
            .to(directExchange)
            .with("direct.routing.key");
    }

    // 死信队列配置
    @Bean
    public Queue deadLetterQueue() {
        return QueueBuilder.durable("dlx.queue").build();
    }

    @Bean
    public DirectExchange deadLetterExchange() {
        return ExchangeBuilder.directExchange("dlx.exchange").durable(true).build();
    }

    @Bean
    public Binding deadLetterBinding(Queue deadLetterQueue, DirectExchange deadLetterExchange) {
        return BindingBuilder.bind(deadLetterQueue)
            .to(deadLetterExchange)
            .with("dlx.routing.key");
    }

    // 延时队列（使用插件）
    @Bean
    public Queue delayedQueue() {
        return QueueBuilder.durable("delayed.queue").build();
    }

    @Bean
    public CustomExchange delayedExchange() {
        Map<String, Object> args = new HashMap<>();
        args.put("x-delayed-type", "direct");
        return new CustomExchange("delayed.exchange", "x-delayed-message", true, false, args);
    }

    @Bean
    public Binding delayedBinding(Queue delayedQueue, CustomExchange delayedExchange) {
        return BindingBuilder.bind(delayedQueue)
            .to(delayedExchange)
            .with("delayed.routing.key");
    }
}
```

### 2. 消息发送

```java
@Service
@Slf4j
public class RabbitMQProducer {

    private final RabbitTemplate rabbitTemplate;
    private final ConfirmCallback confirmCallback;
    private final ReturnsCallback returnsCallback;

    public RabbitMQProducer(RabbitTemplate rabbitTemplate,
                               ConfirmCallback confirmCallback,
                               ReturnsCallback returnsCallback) {
        this.rabbitTemplate = rabbitTemplate;
        this.confirmCallback = confirmCallback;
        this.returnsCallback = returnsCallback;

        // 设置回调
        rabbitTemplate.setConfirmCallback(confirmCallback);
        rabbitTemplate.setReturnsCallback(returnsCallback);

        // 开启强制确认
        rabbitTemplate.setMandatory(true);
    }

    // 发送消息
    public void send(String exchange, String routingKey, Object message) {
        log.info("发送消息: exchange={}, routingKey={}, message={}", exchange, routingKey, message);

        rabbitTemplate.convertAndSend(exchange, routingKey, message);
    }

    // 发送消息并设置属性
    public void sendWithProperties(String exchange, String routingKey, Object message,
                                     Map<String, Object> headers) {
        MessageHeaders messageHeaders = new MessageHeaders(headers);
        Message<?> msg = MessageBuilder.createMessage(message, messageHeaders);

        rabbitTemplate.convertAndSend(exchange, routingKey, msg);
    }

    // 发送延时消息
    public void sendDelayMessage(String routingKey, Object message, long delayMillis) {
        log.info("发送延时消息: routingKey={}, delay={}, message={}", routingKey, delayMillis, message);

        rabbitTemplate.convertAndSend(
            "delayed.exchange",
            "delayed.routing.key",
            message,
            msg -> {
                msg.getMessageProperties().setDelay((int) delayMillis);
                return msg;
            }
        );
    }

    // 发送对象消息
    public void sendObject(String exchange, String routingKey, Object object) {
        rabbitTemplate.convertAndSend(
            exchange,
            routingKey,
            object,
            new CorrelationData(UUID.randomUUID().toString())
        );
    }

    // 发布确认回调
    @Component
    public static class RabbitConfirmCallback implements ConfirmCallback {

        @Override
        public void confirm(CorrelationData correlationData, boolean ack, String cause) {
            if (ack) {
                log.info("消息发送成功: id={}", correlationData.getId());
            } else {
                log.error("消息发送失败: id={}, cause={}", correlationData.getId(), cause);
                // 发送失败处理
            }
        }
    }

    // 消息退回回调
    @Component
    public static class RabbitReturnsCallback implements ReturnsCallback {

        @Override
        public void returnedMessage(Message message, int replyCode, String replyText,
                                     String exchange, String routingKey) {
            log.error("消息被退回: exchange={}, routingKey={}, replyCode={}, replyText={}",
                exchange, routingKey, replyCode, replyText);

            // 退回消息处理
        }
    }
}
```

### 3. 消息消费

```java
@Service
@Slf4j
public class RabbitMQConsumer {

    // 普通消息消费
    @RabbitListener(queues = "order.queue")
    public void handleOrderMessage(OrderMessage message, Channel channel, Message amqpMessage) {
        try {
            log.info("收到订单消息: {}", message);

            // 处理消息
            processOrderMessage(message);

            // 手动确认
            channel.basicAck(amqpMessage.getMessageProperties().getDeliveryTag(), false);

        } catch (BusinessException e) {
            log.error("业务处理失败", e);

            // 拒绝消息（不重试）
            channel.basicNack(
                amqpMessage.getMessageProperties().getDeliveryTag(),
                false,
                false
            );

        } catch (Exception e) {
            log.error("系统异常", e);

            // 拒绝消息并重新入队
            channel.basicNack(
                amqpMessage.getMessageProperties().getDeliveryTag(),
                false,
                true
            );
        }
    }

    // 批量消费
    @RabbitListener(
        queues = "batch.queue",
        containerFactory = "batchRabbitListenerContainerFactory"
    )
    public void handleBatchMessages(List<OrderMessage> messages) {
        log.info("批量收到 {} 条订单消息", messages.size());

        try {
            // 批量处理
            processBatchMessages(messages);

        } catch (Exception e) {
            log.error("批量处理失败", e);
            throw e;  // 整批失败
        }
    }

    // 死信队列消费
    @RabbitListener(queues = "dlx.queue")
    public void handleDeadLetterMessage(Message message, Channel channel) {
        long deliveryTag = message.getMessageProperties().getDeliveryTag();

        try {
            log.info("收到死信消息: {}", new String(message.getBody()));

            // 处理死信消息
            processDeadLetter(message);

            // 确认
            channel.basicAck(deliveryTag, false);

        } catch (Exception e) {
            log.error("死信消息处理失败", e);

            // 拒绝
            channel.basicNack(deliveryTag, false, false);
        }
    }

    // 消费者配置
    @Bean
    public SimpleRabbitListenerContainerFactory batchRabbitListenerContainerFactory(
            ConnectionFactory connectionFactory,
            Jackson2JsonMessageConverter messageConverter) {

        SimpleRabbitListenerContainerFactory factory = new SimpleRabbitListenerContainerFactory();
        factory.setConnectionFactory(connectionFactory);
        factory.setMessageConverter(messageConverter);

        // 批量消费配置
        factory.setBatchListener(true);
        factory.setBatchSize(20);
        factory.setReceiveTimeout(30000L);

        // 预取数量
        factory.setPrefetch(50);

        // 并发消费者
        factory.setConcurrentConsumers(5);
        factory.setMaxConcurrentConsumers(10);

        return factory;
    }

    @Bean
    public Jackson2JsonMessageConverter messageConverter() {
        ObjectMapper mapper = new ObjectMapper();
        mapper.registerModules(new JavaTimeModule());
        mapper.disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);

        return new Jackson2JsonMessageConverter(mapper);
    }
}
```

## 四、消息队列应用场景

### 1. 订单系统

```java
@Service
@Slf4j
public class OrderMessageService {

    private final MessageProducer messageProducer;

    // 创建订单（发送消息到多个系统）
    @Transactional
    public Order createOrder(OrderCreateDto dto) {
        // 1. 创建订单
        Order order = orderRepository.save(Order.builder()
            .userId(dto.getUserId())
            .productId(dto.getProductId())
            .quantity(dto.getQuantity())
            .totalAmount(calculateTotal(dto))
            .status(OrderStatus.CREATED)
            .build());

        // 2. 发送订单创建消息
        OrderCreatedMessage message = OrderCreatedMessage.builder()
            .orderId(order.getId())
            .userId(order.getUserId())
            .productId(order.getProductId())
            .quantity(order.getQuantity())
            .totalAmount(order.getTotalAmount())
            .createdAt(LocalDateTime.now())
            .build();

        // 3. 发送到不同系统
        // 库存系统
        messageProducer.send("order-topic", "inventory", "order-" + order.getId(), message);

        // 支付系统
        messageProducer.send("order-topic", "payment", "order-" + order.getId(), message);

        // 用户通知系统
        messageProducer.send("order-topic", "notification", "order-" + order.getId(), message);

        // 数据统计系统
        messageProducer.sendAsync("order-topic", "analytics", "order-" + order.getId(), message);

        return order;
    }

    // 支付成功
    public void paymentSucceeded(Long orderId, Long transactionId) {
        PaymentSucceededMessage message = PaymentSucceededMessage.builder()
            .orderId(orderId)
            .transactionId(transactionId)
            .paidAt(LocalDateTime.now())
            .build();

        // 更新订单状态
        orderRepository.updateStatus(orderId, OrderStatus.PAID);

        // 发送消息
        messageProducer.send("order-topic", "payment-success", "payment-" + orderId, message);

        // 发送延时消息（自动收货）
        messageProducer.sendDelayMessage("order-topic", "auto-confirm",
            AutoConfirmMessage.builder()
                .orderId(orderId)
                .autoConfirmDays(7)
                .build(),
            7 * 24 * 60 * 60 * 1000L
        );
    }

    // 自动收货
    public void autoConfirmOrder(Long orderId) {
        orderRepository.updateStatus(orderId, OrderStatus.COMPLETED);

        // 发送通知
        messageProducer.send("order-topic", "order-completed",
            "complete-" + orderId, orderId);
    }
}
```

### 2. 秒杀系统

```java
@Service
@Slf4j
public class SeckillMessageService {

    private final MessageProducer messageProducer;
    private final RedisTemplate<String, Object> redisTemplate;

    // 秒杀请求
    public void seckill(Long userId, Long productId) {
        // 1. 检查用户是否已购买
        String purchasedKey = "seckill:purchased:" + productId + ":" + userId;
        if (redisTemplate.hasKey(purchasedKey)) {
            throw new BusinessException("每人限购一件");
        }

        // 2. 检查库存（Redis 预减）
        String stockKey = "seckill:stock:" + productId;
        Long stock = redisTemplate.opsForValue().decrement(stockKey);

        if (stock == null || stock < 0) {
            // 库存不足，恢复计数
            redisTemplate.opsForValue().increment(stockKey);
            throw new BusinessException("商品已售罄");
        }

        // 3. 发送秒杀订单消息
        SeckillOrderMessage message = SeckillOrderMessage.builder()
            .userId(userId)
            .productId(productId)
            .timestamp(System.currentTimeMillis())
            .build();

        messageProducer.sendAsync("seckill-topic", "order", "seckill-" + userId, message);

        // 4. 设置用户购买记录（有效期24小时）
        redisTemplate.opsForValue().set(purchasedKey, "1", 24, TimeUnit.HOURS);
    }

    // 处理秒杀订单
    @RocketMQMessageListener(
        topic = "seckill-topic",
        consumerGroup = "seckill-consumer-group",
        maxReconsumeTimes = 1  // 只重试一次，快速失败
    )
    public class SeckillOrderConsumer implements RocketMQListener<SeckillOrderMessage> {

        @Override
        public void onMessage(SeckillOrderMessage message) {
            log.info("处理秒杀订单: {}", message);

            try {
                // 创建订单
                createSeckillOrder(message);

                // 扣减数据库库存
                deductDatabaseStock(message.getProductId());

                // 发送订单创建通知
                sendNotification(message);

            } catch (BusinessException e) {
                log.error("秒杀订单处理失败: {}", message, e);

                // 失败则退还 Redis 库存
                String stockKey = "seckill:stock:" + message.getProductId();
                redisTemplate.opsForValue().increment(stockKey);

                // 清除用户购买记录
                String purchasedKey = "seckill:purchased:" + message.getProductId() + ":" + message.getUserId();
                redisTemplate.delete(purchasedKey);

            } catch (Exception e) {
                log.error("秒杀订单系统异常: {}", message, e);

                // 系统异常，先记录，后续补偿
                recordFailedOrder(message);
            }
        }

        private void createSeckillOrder(SeckillOrderMessage message) {
            // 创建订单逻辑
        }

        private void deductDatabaseStock(Long productId) {
            // 扣减数据库库存
        }

        private void sendNotification(SeckillOrderMessage message) {
            // 发送通知
        }

        private void recordFailedOrder(SeckillOrderMessage message) {
            // 记录失败订单，用于后续补偿
            String failedKey = "seckill:failed:" + message.getUserId() + ":" + message.getProductId();
            redisTemplate.opsForValue().set(failedKey, message, 24, TimeUnit.HOURS);
        }
    }
}
```

## 五、消息队列面试高频考点

```java
/**
 * MQ 面试高频问题
 */

// 1. 消息队列的作用？
/*
- 解耦：系统间通过消息通信，降低耦合度
- 异步：提高系统响应速度
- 削峰：平滑处理突发流量
- 数据分发：一对多消息分发
*/

// 2. 消息队列如何保证消息不丢失？
/*
生产者端：
  - 同步发送 + 失败重试
  - 发送确认机制（Confirm）
  - 事务消息

MQ 服务端：
  - 消息持久化（RDB/AOF、刷盘策略）
  - 主从复制
  - 集群模式

消费者端：
  - 手动确认（ACK）
  - 消费失败重试
  - 死信队列
*/

// 3. 消息队列如何保证消息顺序性？
/*
RocketMQ：
  - 全局顺序：单队列
  - 局部顺序：按业务ID分片到同一队列

Kafka：
  - 单分区保证顺序
  - 同一Key的消息进入同一分区

RabbitMQ：
  - 单队列单消费者
  - 或使用优先级队列
*/

// 4. 消息队列如何处理消息重复消费？
/*
原因：
  - 网络抖动导致确认失败，消息重新投递
  - 消费者处理超时，消息重新投递

解决：
  - 幂等性设计（数据库唯一索引、状态机）
  - 消息去重（Redis 去重表）
  - 业务逻辑天然幂等（如 SQL UPDATE）
*/

@Component
public class IdempotentMessageHandler {
    private final StringRedisTemplate redisTemplate;

    public void handleMessage(String messageId, Runnable handler) {
        String key = "msg:handled:" + messageId;

        // 使用 SETNX 实现幂等
        Boolean success = redisTemplate.opsForValue()
            .setIfAbsent(key, "1", Duration.ofHours(24));

        if (Boolean.TRUE.equals(success)) {
            try {
                handler.run();
            } catch (Exception e) {
                // 处理失败，删除标记，允许重试
                redisTemplate.delete(key);
                throw e;
            }
        } else {
            // 消息已处理，忽略
            log.info("消息已处理，跳过: {}", messageId);
        }
    }
}

// 5. 消息积压如何处理？
/*
原因：
  - 消费者处理能力不足
  - 消费者异常导致消息堆积

解决：
  - 增加消费者数量
  - 优化消费者处理逻辑
  - 批量消费
  - 临时扩容
  - 跳过非关键消息
*/

// 6. 消息队列如何实现延时消息？
/*
方案一：RocketMQ 延时消息
  - 内置延时级别（1s, 5s, 10s, 30s, 1m, ...）
  - 使用 SCHEDULE_TOPIC_XXXX 队列

方案二：RabbitMQ 延时队列
  - TTL + 死信队列
  - 或使用延时插件

方案三：Redis ZSet
  - 使用 ZSet 存储消息，分数为执行时间
  - 定时轮询获取到期消息

方案四：时间轮（TimeWheel）
  - Netty 中的 HashedWheelTimer
  - 分层时间轮
*/

// 7. Kafka 和 RocketMQ 的区别？
/*
Kafka：
  - 吞吐量极高（百万级）
  - 基于日志的存储（顺序写）
  - 适合大数据流处理
  - 延迟相对较高
  - 消费模型：pull

RocketMQ：
  - 吞吐量高（十万级）
  - 支持多种消息类型（顺序、事务、延时）
  - 适合业务消息
  - 延迟低
  - 消费模型：push（长轮询）
  - 功能更丰富
*/

// 8. 消息队列选型建议？
/*
- 高吞吐量 + 大数据：Kafka
- 复杂业务 + 事务消息：RocketMQ
- 功能丰富 + 路由灵活：RabbitMQ
- 简单场景 + 快速接入：Redis List/ZSet

一般组合方案：
- 业务消息：RocketMQ
- 日志收集：Kafka
- 延时任务：Redis ZSet
*/
```

## 六、消息队列常见问题排查

```bash
# RocketMQ 常用命令

# 查看集群信息
mqadmin clusterList -n localhost:9876

# 查看 Topic 列表
mqadmin topicList -n localhost:9876

# 查看 Topic 路由信息
mqadmin topicRoute -n localhost:9876 -t order-topic

# 查看消费者组
mqadmin consumerProgress -n localhost:9876 -g order-consumer-group

# 查看消息
mqadmin queryMsgById -n localhost:9876 -i msgId

# 重置消费位点
mqadmin resetOffsetByTime -n localhost:9876 -g order-consumer-group -t order-topic -s "2024-01-01 00:00:00"

# 查看 Broker 状态
mqadmin brokerStatus -n localhost:9876 -b broker-a:10911
```

## 小结

本节学习了消息队列：

- **RocketMQ** - 同步/异步/单向/顺序/事务/延时消息
- **RabbitMQ** - 基础配置、消息发送、消息消费
- **应用场景** - 订单系统、秒杀系统
- **面试考点** - 消息不丢失、顺序性、幂等性、延时消息
- **问题排查** - 常用命令和排查思路

## 实践练习

### 编程题
1. 使用 RocketMQ 实现一个订单异步处理系统：订单服务发送"下单"消息，库存服务消费消息扣减库存，通知服务消费消息发送通知。确保消息不丢失、不重复消费。
2. 实现一个延时消息场景：用户下单后 30 分钟未支付自动取消订单。

### 思考题
1. 如何保证消息的可靠性投递？生产者确认、持久化和消费者 Ack 分别解决了什么问题？
2. RocketMQ、Kafka、RabbitMQ 各自的设计哲学和最佳场景？

### 自测题
1. 消息队列的三大核心作用是什么？
2. 消息重复消费的原因和解决方案？
3. RocketMQ 的消息模型包含哪些角色？

下一步将学习 MyBatis（→ `mybatis/beginner/01-mybatis-basics.md`）。