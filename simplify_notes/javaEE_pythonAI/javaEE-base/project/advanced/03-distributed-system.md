# 高并发分布式项目实战

## 一、项目概述

设计一个支持百万并发的分布式系统，涵盖秒杀系统、分布式 ID 生成、弹性伸缩设计、多级缓存、降级熔断、全链路压测。

### 技术栈

| 组件 | 选型 | 说明 |
|------|------|------|
| 流量入口 | Nginx + LVS | 四层 + 七层负载均衡 |
| 网关 | Spring Cloud Gateway | 限流 + 路由 |
| 业务层 | Spring Boot + K8s | 弹性伸缩 |
| 缓存 | Redis Cluster + Caffeine | 多级缓存 |
| 消息队列 | RocketMQ | 削峰填谷 |
| 数据库 | ShardingSphere + MySQL | 分库分表 |
| 监控 | Prometheus + Grafana + SkyWalking | 全链路监控 |

## 二、秒杀系统设计

### 系统架构

```
负载均衡层          ┌──────────────────────┐
(LVS + Nginx)       │  1. 客户端请求到达     │
                    └──────────┬───────────┘
                               │
限流层              ┌──────────▼───────────┐
(网关 + Sentinel)   │  2. 全局限流           │
                    │  3. 用户级限流         │
                    └──────────┬───────────┘
                               │
预扣减层            ┌──────────▼───────────┐
(Redis Lua)         │  4. Redis 预扣减库存  │
                    └──────────┬───────────┘
                               │
MQ 削峰             ┌──────────▼───────────┐
(RocketMQ)          │  5. 秒杀请求入队      │
                    └──────────┬───────────┘
                               │
异步落单             ┌──────────▼───────────┐
(消费者)             │  6. 异步创建订单      │
                    └──────────┬───────────┘
                               │
数据库              ┌──────────▼───────────┐
(MySQL)             │  7. 最终一致性写库    │
                    └────────────────────────
```

### 核心代码

```java
@Service
public class FlashSaleService {
    @Autowired
    private StringRedisTemplate redisTemplate;
    @Autowired
    private RocketMQTemplate mqTemplate;
    private static final String STOCK_KEY = "seckill:stock:";

    // Redis Lua 原子扣减
    public boolean tryAcquire(Long activityId, Long userId) {
        String script = """
            local stock_key = KEYS[1]
            local user_key = KEYS[2]
            local stock = redis.call('GET', stock_key)
            if not stock or tonumber(stock) <= 0 then
                return 0
            end
            if redis.call('SISMEMBER', user_key, ARGV[1]) == 1 then
                return -1  -- 重复购买
            end
            redis.call('DECR', stock_key)
            redis.call('SADD', user_key, ARGV[1])
            redis.call('EXPIRE', user_key, 86400)
            return 1
            """;

        Long result = redisTemplate.execute(
            new DefaultRedisScript<>(script, Long.class),
            List.of(STOCK_KEY + activityId, "seckill:users:" + activityId),
            String.valueOf(userId)
        );
        return result != null && result == 1;
    }

    // 发送秒杀消息
    public void sendFlashSaleMessage(FlashSaleRequest request) {
        FlashSaleMessage msg = new FlashSaleMessage(
            request.getActivityId(), request.getUserId(),
            request.getProductId(), LocalDateTime.now());
        mqTemplate.syncSend("flash-sale-topic", msg, 2000);
    }

    // 消费端异步落单
    @RocketMQMessageListener(topic = "flash-sale-topic", 
        consumerGroup = "flash-sale-consumer",
        consumeThreadMax = 32)
    public class FlashSaleConsumer implements RocketMQListener<FlashSaleMessage> {
        @Override
        public ConsumeConcurrentlyStatus onMessage(FlashSaleMessage msg) {
            // 1. 幂等校验（去重表）
            if (idempotentService.hasProcessed(msg.getMessageId())) {
                return ConsumeConcurrentlyStatus.CONSUME_SUCCESS;
            }
            // 2. 创建订单
            orderService.createFlashSaleOrder(msg);
            // 3. 标记已处理
            idempotentService.markProcessed(msg.getMessageId());
            return ConsumeConcurrentlyStatus.CONSUME_SUCCESS;
        }
    }
}
```

### 数据库层防超卖

```sql
-- 乐观锁扣减库存（CAS）
UPDATE product 
SET stock = stock - 1, version = version + 1 
WHERE id = ? AND stock > 0 AND version = ?;
```

## 三、分布式 ID 生成

```java
@Component
public class DistributedIdGenerator {
    // Snowflake 算法（Twitter）
    // 1位符号位 + 41位时间戳 + 10位工作节点 + 12位序列号
    private long workerId;
    private long sequence = 0L;
    private long lastTimestamp = -1L;

    public synchronized long nextId() {
        long timestamp = System.currentTimeMillis();
        if (timestamp < lastTimestamp) {
            throw new RuntimeException("Clock moved backwards");
        }
        if (timestamp == lastTimestamp) {
            sequence = (sequence + 1) & 4095;
            if (sequence == 0) {
                timestamp = tilNextMillis(lastTimestamp);
            }
        } else {
            sequence = 0L;
        }
        lastTimestamp = timestamp;
        return ((timestamp - 1288834974657L) << 22)
             | (workerId << 12)
             | sequence;
    }

    // 优化版：使用 Redis INCR 生成分段号
    public long nextRedisId(String key) {
        return redisTemplate.opsForValue().increment("id:" + key);
    }
}
```

## 四、全链路压测

### 压测数据隔离

```yaml
# 压测标记传递
spring:
  cloud:
    gateway:
      default-filters:
        - name: RequestHeaderToRequestUri
          args:
            headerName: X-Stress-Test

# 压测数据写入影子表
@Component
public class StressTestFilter extends AbstractRequestFilter {
    @Override
    protected boolean isStressTest(HttpServletRequest request) {
        return "true".equals(request.getHeader("X-Stress-Test"));
    }

    @Override
    protected void routeToShadowTable(DataSource dataSource) {
        // 路由到 shadow_t_order 影子表
    }
}
```

### K8s 弹性伸缩

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: flash-sale-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: flash-sale-service
  minReplicas: 10
  maxReplicas: 200
  metrics:
  - type: Pods
    pods:
      metric:
        name: request_per_second
      target:
        type: AverageValue
        averageValue: 500
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
    scaleDown:
      stabilizationWindowSeconds: 300
```

## 五、容量规划

| 资源 | 预估容量 | 实际配置 |
|------|----------|----------|
| QPS 峰值 | 500,000 | Nginx 1000+ 连接 |
| Redis 读 | 300,000 QPS | Redis Cluster 12 分片 |
| Redis 写 | 50,000 QPS | 批处理合并写 |
| MQ 吞吐 | 100,000 TPS | RocketMQ 8 队列 |
| DB 写入 | 5,000 TPS | ShardingSphere 16 表 |

## 课后练习

1. 实现秒杀系统的静态化 + CDN 加速
2. 实现滑动窗口限流 + Sentinel 网关限流
3. 使用 Locust 模拟百万并发压测
4. 设计多级降级方案（功能降级、流量降级、数据降级）

## 自测题

1. 秒杀系统 Redis 预扣减库存失败应？ A) 重试 B) 直接返回失败 C) 排队等待 D) 降级到数据库
2. Snowflake 算法中 10 位工作节点支持的最大节点数？ A) 256 B) 512 C) 1024 D) 2048
3. K8s HPA 的扩容冷却时间配置参数是？ A) cooldownSeconds B) stabilizationWindowSeconds C) scaleDownDelay D) coolDownPeriod

**答案：** 1-B, 2-C, 3-B
