# Spring Boot 微服务架构

## 一、概述

从单体到微服务的演进：服务拆分原则、Spring Boot 微服务架构模式、分布式链路追踪、弹性设计、容器化部署。

## 二、微服务拆分原则

### 拆分策略

| 维度 | 原则 | 反例 |
|------|------|------|
| 业务域 | 按 DDD 限界上下文拆分 | 按层拆分（controller/service/dao） |
| 数据 | 每个服务独享数据库 | 多个服务直连同一数据库 |
| 团队 | 每个服务由 2-5 人团队维护 | 单人维护 10+ 服务 |
| 通信 | REST/ gRPC 同步 + MQ 异步 | 共享内存/文件 |

### 典型服务划分

```
order-service      # 订单服务（独立数据库 order_db）
user-service       # 用户服务（独立数据库 user_db）
payment-service    # 支付服务（独立数据库 payment_db）
notification-service # 通知服务（无状态）
gateway-service    # API 网关
```

## 三、服务间通信

### Feign 声明式调用

```java
// API 定义接口
@FeignClient(name = "user-service", path = "/api/users",
             fallbackFactory = UserClientFallback.class)
public interface UserClient {
    @GetMapping("/{id}")
    ApiResult<UserVO> getUser(@PathVariable Long id);

    @PostMapping("/batch")
    ApiResult<List<UserVO>> getUsers(@RequestBody List<Long> ids);
}

// 熔断降级
@Component
public class UserClientFallback implements FallbackFactory<UserClient> {
    @Override
    public UserClient create(Throwable cause) {
        return new UserClient() {
            @Override
            public ApiResult<UserVO> getUser(Long id) {
                log.warn("User service unavailable, fallback", cause);
                return ApiResult.error(503, "User service unavailable");
            }

            @Override
            public ApiResult<List<UserVO>> getUsers(List<Long> ids) {
                return ApiResult.success(Collections.emptyList());
            }
        };
    }
}
```

### 异步解耦（MQ）

```java
// 订单服务发布事件
@Service
public class OrderService {
    @Autowired
    private StreamBridge streamBridge;

    @Transactional
    public Order createOrder(OrderDTO dto) {
        Order order = saveOrder(dto);
        // 发送"订单已创建"事件
        OrderCreatedEvent event = new OrderCreatedEvent(order.getId(), order.getUserId());
        streamBridge.send("order-event-output", event);
        return order;
    }
}

// 通知服务消费事件
@Component
public class OrderEventConsumer {
    @Bean
    public Consumer<OrderCreatedEvent> orderCreated() {
        return event -> {
            UserVO user = userClient.getUser(event.getUserId());
            smsSender.send(user.getPhone(), "您的订单已创建 #" + event.getOrderId());
        };
    }
}
```

## 四、分布式链路追踪

### Micrometer Tracing

```xml
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-tracing-bridge-brave</artifactId>
</dependency>
<dependency>
    <groupId>io.zipkin.reporter2</groupId>
    <artifactId>zipkin-reporter-brave</artifactId>
</dependency>
```

```yaml
spring:
  application:
    name: order-service
  sleuth:
    trace-id128: true
    sampler:
      probability: 1.0  # 生产环境建议 0.1-0.5
management:
  tracing:
    sampling:
      probability: 1.0
  zipkin:
    tracing:
      endpoint: http://zipkin:9411/api/v2/spans
```

```java
// 手动埋点
@Service
public class OrderService {
    @Autowired
    private Tracer tracer;

    public void processOrder(Long orderId) {
        Span span = tracer.nextSpan().name("processOrder").start();
        try (Tracer.SpanInScope ws = tracer.withSpan(span)) {
            span.tag("orderId", String.valueOf(orderId));
            // 业务逻辑
        } finally {
            span.end();
        }
    }
}
```

## 五、弹性设计模式

### 熔断器 (Resilience4j)

```java
@Configuration
public class Resilience4jConfig {
    @Bean
    public Customizer<Resilience4JCircuitBreakerFactory> defaultCustomizer() {
        return factory -> factory.configureDefault(id -> new Resilience4JConfigBuilder(id)
            .circuitBreakerConfig(CircuitBreakerConfig.custom()
                .slidingWindowSize(10)           // 10个请求的滑动窗口
                .minimumNumberOfCalls(5)         // 最少5个请求开始计算
                .failureRateThreshold(50)        // 50%失败率开启熔断
                .waitDurationInOpenState(Duration.ofSeconds(30))  // 半开等待30s
                .permittedNumberOfCallsInHalfOpenState(3)          // 半开时允许3个请求
                .build())
            .timeLimiterConfig(TimeLimiterConfig.custom()
                .timeoutDuration(Duration.ofSeconds(3))
                .build())
            .build());
    }
}

@Service
public class PaymentService {
    @CircuitBreaker(name = "paymentService", fallbackMethod = "paymentFallback")
    @Bulkhead(name = "paymentService", type = Bulkhead.Type.THREADPOOL)
    public PaymentResult processPayment(PaymentRequest request) {
        return restTemplate.postForObject("http://payment-service/pay", request, PaymentResult.class);
    }

    public PaymentResult paymentFallback(PaymentRequest request, Throwable t) {
        log.error("Payment failed, use fallback", t);
        return PaymentResult.failed("Payment system busy, please retry later");
    }
}
```

### 重试与限流

```java
@Retry(name = "inventoryService", fallbackMethod = "inventoryFallback")
public InventoryResult checkInventory(Long productId, int quantity) {
    return inventoryClient.check(productId, quantity);
}

// 限流（基于令牌桶）
@RateLimiter(name = "apiLimiter", fallbackMethod = "rateLimitFallback")
@GetMapping("/api/orders")
public ApiResult<List<Order>> listOrders() {
    return ApiResult.success(orderService.findAll());
}
```

## 六、容器化部署

```dockerfile
# 多阶段构建
FROM eclipse-temurin:21-jdk-alpine AS builder
WORKDIR /build
COPY pom.xml .
RUN mvn dependency:go-offline
COPY src ./src
RUN mvn package -DskipTests

FROM eclipse-temurin:21-jre-alpine
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
WORKDIR /app
COPY --from=builder /build/target/*.jar app.jar
EXPOSE 8080
USER appuser
ENTRYPOINT ["java", "-jar", "app.jar"]
# 生产 JVM 参数: -Xms512m -Xmx2g -XX:+UseZGC -XX:MaxMetaspaceSize=256m
```

```yaml
# docker-compose.yml（单机演示）
version: "3.8"
services:
  gateway:
    image: gateway-service:latest
    ports:
      - "8080:8080"
    environment:
      - SPRING_PROFILES_ACTIVE=docker
    depends_on:
      - user-service
      - order-service

  user-service:
    image: user-service:latest
    environment:
      - SPRING_PROFILES_ACTIVE=docker
      - DB_URL=jdbc:postgresql://postgres:5432/user_db

  order-service:
    image: order-service:latest
    # ...类似配置
```

## 课后练习

1. 实现基于 Resilience4j 的重试 + 熔断 + 限流三件套集成
2. 搭建 Zipkin + Micrometer Tracing 全链路追踪
3. 实现一个 Sidecar 模式的服务网格代理（Spring Cloud Gateway）
4. 设计一个灰度发布方案（基于 Header/Cookie 的路由规则）

## 自测题

1. Feign 默认集成的负载均衡组件？ A) Ribbon (已弃用) B) Spring Cloud LoadBalancer C) Nginx D) HAProxy
2. 熔断器的三个状态是？ A) 开启/关闭/半开 B) 运行/停止/等待 C) 健康/危险/恢复 D) 正常/异常/超时
3. 微服务拆分中数据库应如何设计？ A) 所有服务共享一个库 B) 每个服务独享数据库 C) 按读写分离 D) 全部用 NoSQL

**答案：** 1-B, 2-A, 3-B
