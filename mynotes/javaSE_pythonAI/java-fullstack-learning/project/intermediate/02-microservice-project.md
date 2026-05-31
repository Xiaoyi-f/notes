# 微服务项目实战

## 一、项目概述

基于 Spring Cloud Alibaba 构建一个电商平台的后端微服务系统，涵盖商品、订单、支付、库存、用户等核心业务。

### 技术栈

| 组件 | 选型 | 用途 |
|------|------|------|
| 服务框架 | Spring Boot 3.2 + JDK 21 | 基础服务 |
| 注册配置 | Nacos | 服务发现 + 配置中心 |
| 远程调用 | OpenFeign + Sentinel | 服务调用 + 熔断 |
| 网关 | Spring Cloud Gateway | 统一入口 |
| 持久层 | MyBatis-Plus + MySQL | 数据存储 |
| 消息队列 | RocketMQ | 异步解耦 |
| 缓存 | Redis + Caffeine | 多级缓存 |
| 分布式事务 | Seata AT | 跨服务事务 |

## 二、服务划分

```
api-gateway          # 网关（端口 8080）
  ├── product-service    # 商品服务（端口 8081）
  ├── order-service      # 订单服务（端口 8082）
  ├── payment-service    # 支付服务（端口 8083）
  ├── inventory-service  # 库存服务（端口 8084）
  ├── user-service       # 用户服务（端口 8085）
  └── notification-service # 通知服务（端口 8086）
```

## 三、核心业务流程

### 商品服务

```java
@RestController
@RequestMapping("/api/products")
public class ProductController {
    @Autowired
    private ProductService productService;

    @GetMapping
    public ApiResult<PageResult<ProductVO>> list(ProductQuery query) {
        return ApiResult.success(productService.page(query));
    }

    @GetMapping("/{id}")
    public ApiResult<ProductVO> detail(@PathVariable Long id) {
        return ApiResult.success(productService.getDetail(id));
    }
}

@Service
public class ProductService {
    @Autowired
    private ProductMapper productMapper;
    @Autowired
    private CacheManager cacheManager;

    public ProductVO getDetail(Long id) {
        // 多级缓存查询
        Product product = cacheManager.get("product:" + id, 
            Product.class, () -> productMapper.selectById(id));
        return ProductVO.from(product);
    }
}
```

### 下单流程

```java
@Service
public class OrderService {
    @Autowired
    private InventoryClient inventoryClient;
    @Autowired
    private PaymentClient paymentClient;
    @Autowired
    private RocketMQTemplate mqTemplate;

    @GlobalTransactional(name = "create-order", rollbackFor = Exception.class)
    public OrderVO createOrder(CreateOrderRequest request) {
        // 1. 锁定库存
        Boolean locked = inventoryClient.lockStock(
            request.getProductId(), request.getQuantity());
        if (!locked) throw new BusinessException("库存不足");

        // 2. 创建订单
        Order order = Order.builder()
            .userId(request.getUserId())
            .productId(request.getProductId())
            .quantity(request.getQuantity())
            .totalAmount(calculateAmount(request))
            .status(OrderStatus.PENDING_PAYMENT)
            .build();
        orderMapper.insert(order);

        // 3. 发送延迟消息（30分钟后检查支付）
        mqTemplate.syncSend("order-check-topic", 
            MessageBuilder.withPayload(order.getId()).build(),
            1000, 4);  // 延迟等级 4 = 30s (demo用)
        
        return OrderVO.from(order);
    }
}
```

## 四、Order 服务表结构

```sql
CREATE TABLE `order` (
    `id` bigint NOT NULL AUTO_INCREMENT,
    `order_no` varchar(32) NOT NULL COMMENT '订单号',
    `user_id` bigint NOT NULL,
    `product_id` bigint NOT NULL,
    `quantity` int NOT NULL DEFAULT 1,
    `total_amount` decimal(10,2) NOT NULL,
    `status` tinyint NOT NULL DEFAULT 0 COMMENT '0-待支付 1-已支付 2-已发货 3-已完成 4-已取消',
    `version` int NOT NULL DEFAULT 0,
    `deleted` tinyint NOT NULL DEFAULT 0,
    `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_order_no` (`order_no`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单表';
```

## 五、API 网关配置

```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: product-service
          uri: lb://product-service
          predicates:
            - Path=/api/products/**
          filters:
            - name: RequestRateLimiter
              args:
                key-resolver: "#{@ipKeyResolver}"
                redis-rate-limiter.replenishRate: 100
                redis-rate-limiter.burstCapacity: 200

        - id: order-service
          uri: lb://order-service
          predicates:
            - Path=/api/orders/**
          filters:
            - StripPrefix=1
```

## 六、部署

```yaml
# docker-compose.yml
version: "3.8"
services:
  nacos:
    image: nacos/nacos-server:v2.2.3
    environment:
      MODE: standalone
    ports:
      - "8848:8848"

  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root123
    volumes:
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql

  order-service:
    build: ./order-service
    environment:
      SPRING_PROFILES_ACTIVE: docker
    depends_on:
      - nacos
      - mysql
```

## 课后练习

1. 实现优惠券服务的扣减 + 回滚（分布式事务）
2. 对接支付宝/微信支付沙箱，实现支付回调处理
3. 实现订单超时自动取消（RocketMQ 延迟消息）
4. 实现商品搜索（Elasticsearch 集成）

## 自测题

1. Seata AT 模式下全局事务 ID 如何传递？ A) HTTP Header B) 线程变量 C) 数据库 D) 消息体
2. 下单流程中锁定库存放在哪个环节？ A) 支付成功后 B) 创建订单时 C) 发货时 D) 退款时
3. 网关层限流常用的算法是？ A) 计数器 B) 令牌桶 C) 漏桶 D) 滑动窗口

**答案：** 1-A, 2-B, 3-B
