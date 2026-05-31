# Spring Cloud Alibaba 微服务架构

## 一、微服务架构概述

```
┌─────────────────────────────────────────────────────────┐
│                   客户端 (Browser/Mobile)                  │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│                 API Gateway (网关)                        │
│  - 路由转发  - 负载均衡  - 认证鉴权  - 限流熔断            │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│                服务注册中心 (Nacos)                        │
│     服务注册  服务发现  配置中心  命名服务                  │
└─────────────────────────────────────────────────────────┘
                     ↓
        ┌────────────┼────────────┐
        ↓            ↓            ↓
┌───────────┐ ┌───────────┐ ┌───────────┐
│  用户服务  │ │  订单服务  │ │  商品服务  │
│           │ │           │ │           │
├───────────┤ ├───────────┤ ├───────────┤
│ Nacos     │ │ Nacos     │ │ Nacos     │
│ Sentinel  │ │ Sentinel  │ │ Sentinel  │
│ OpenFeign │ │ OpenFeign │ │ OpenFeign │
└───────────┘ └───────────┘ └───────────┘
        ↓            ↓            ↓
┌─────────────────────────────────────────────────────────┐
│                 中间件层                                  │
│  - Redis    - MySQL    - RocketMQ/Kafka                 │
│  - Elasticsearch - MongoDB                              │
└─────────────────────────────────────────────────────────┘
```

## 二、Spring Cloud Alibaba 核心组件

### 1. Nacos（服务注册与配置中心）

```java
// 依赖
/*
<dependency>
    <groupId>com.alibaba.cloud</groupId>
    <artifactId>spring-cloud-starter-alibaba-nacos-discovery</artifactId>
</dependency>
<dependency>
    <groupId>com.alibaba.cloud</groupId>
    <artifactId>spring-cloud-starter-alibaba-nacos-config</artifactId>
</dependency>
*/

// 启动类
@SpringBootApplication
@EnableDiscoveryClient
public class UserServiceApplication {
    public static void main(String[] args) {
        SpringApplication.run(UserServiceApplication.class, args);
    }
}

// bootstrap.yml
/*
spring:
  application:
    name: user-service
  cloud:
    nacos:
      discovery:
        server-addr: localhost:8848
        namespace: dev
        group: DEFAULT_GROUP
        metadata:
          version: 1.0.0
          region: beijing
      config:
        server-addr: localhost:8848
        namespace: dev
        group: DEFAULT_GROUP
        file-extension: yaml
        refresh-enabled: true
        shared-configs:
          - data-id: common-config.yaml
            group: DEFAULT_GROUP
            refresh: true
*/

// 配置中心使用
@RestController
@RefreshScope  // 支持配置动态刷新
public class ConfigController {

    @Value("${app.title}")
    private String appTitle;

    @Value("${app.version}")
    private String appVersion;

    @GetMapping("/config")
    public Map<String, Object> getConfig() {
        return Map.of(
            "title", appTitle,
            "version", appVersion,
            "timestamp", System.currentTimeMillis()
        );
    }

    @GetMapping("/config/refresh")
    public String refreshConfig() {
        // 手动刷新
        return "配置已刷新";
    }
}

// 服务调用
@Service
public class OrderService {
    private final DiscoveryClient discoveryClient;
    private final RestTemplate restTemplate;
    private final UserServiceClient userServiceClient;

    public OrderService(DiscoveryClient discoveryClient,
                        RestTemplate restTemplate,
                        UserServiceClient userServiceClient) {
        this.discoveryClient = discoveryClient;
        this.restTemplate = restTemplate;
        this.userServiceClient = userServiceClient;
    }

    // 方式1: 使用 DiscoveryClient
    public User getUserById1(Long userId) {
        List<ServiceInstance> instances = discoveryClient.getInstances("user-service");
        if (instances.isEmpty()) {
            throw new BusinessException("用户服务不可用");
        }

        ServiceInstance instance = instances.get(0);
        String url = instance.getUri() + "/api/users/" + userId;
        return restTemplate.getForObject(url, User.class);
    }

    // 方式2: 使用 LoadBalancer (推荐)
    public User getUserById2(Long userId) {
        String url = "http://user-service/api/users/" + userId;
        return restTemplate.getForObject(url, User.class);
    }

    // 方式3: 使用 OpenFeign (推荐)
    public User getUserById3(Long userId) {
        return userServiceClient.getUserById(userId);
    }
}

// LoadBalancer 配置
@Configuration
public class LoadBalancerConfig {
    @Bean
    @LoadBalanced
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
}
```

### 2. Sentinel（流量控制与熔断降级）

```java
// 依赖
/*
<dependency>
    <groupId>com.alibaba.cloud</groupId>
    <artifactId>spring-cloud-starter-alibaba-sentinel</artifactId>
</dependency>
*/

// application.yml
/*
spring:
  cloud:
    sentinel:
      transport:
        dashboard: localhost:8080
        port: 8719
      eager: true
      datasource:
        flow:
          nacos:
            server-addr: localhost:8848
            data-id: ${spring.application.name}-flow-rules
            group-id: DEFAULT_GROUP
            rule-type: flow
*/

// 资源定义
@RestController
@RequestMapping("/api/users")
public class UserController {
    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    // 方式1: 使用 @SentinelResource 注解
    @GetMapping("/{id}")
    @SentinelResource(
        value = "getUserById",
        blockHandler = "handleBlock",           // 限流/熔断处理
        fallback = "handleFallback",           // 降级处理
        exceptionsToTrace = {Exception.class}
    )
    public User getUserById(@PathVariable Long id) {
        return userService.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("用户不存在"));
    }

    // 限流/熔断处理方法（参数必须一致，额外添加 BlockException）
    public User handleBlock(Long id, BlockException ex) {
        // 记录日志
        log.warn("用户查询被限流，用户ID: {}, 异常: {}", id, ex.getClass().getSimpleName());

        // 返回降级数据
        return User.builder()
            .id(-1L)
            .username("系统繁忙")
            .build();
    }

    // 降级处理方法（参数必须一致）
    public User handleFallback(Long id, Exception ex) {
        log.error("用户查询异常，用户ID: {}", id, ex);

        return User.builder()
            .id(-2L)
            .username("服务异常")
            .build();
    }

    // 方式2: 编程式定义规则
    @PostConstruct
    public void initFlowRules() {
        List<FlowRule> rules = new ArrayList<>();

        // 流量控制规则
        FlowRule rule = new FlowRule();
        rule.setResource("getUserById");
        rule.setGrade(RuleConstant.FLOW_GRADE_QPS);  // QPS 限流
        rule.setCount(10);                          // 阈值
        rule.setLimitApp("default");
        rule.setStrategy(RuleConstant.STRATEGY_DIRECT);  // 直接拒绝
        rule.setControlBehavior(RuleConstant.CONTROL_BEHAVIOR_DEFAULT);

        rules.add(rule);
        FlowRuleManager.loadRules(rules);
    }
}

// 熔断规则
@PostConstruct
public void initDegradeRules() {
    List<DegradeRule> rules = new ArrayList<>();

    DegradeRule rule = new DegradeRule();
    rule.setResource("getUserById");
    rule.setGrade(RuleConstant.DEGRADE_GRADE_RT);  // 响应时间
    rule.setCount(100);                              // 响应时间阈值 (ms)
    rule.setTimeWindow(10);                          // 熔断时长 (s)

    rules.add(rule);
    DegradeRuleManager.loadRules(rules);
}

// 系统规则
@PostConstruct
public void initSystemRules() {
    List<SystemRule> rules = new ArrayList<>();

    SystemRule rule = new SystemRule();
    rule.setHighestSystemLoad(0.8);                  // 系统最大负载
    rule.setAvgRt(1000);                             // 平均响应时间
    rule.setMaxThread(200);                          // 最大线程数
    rule.setQps(1000);                               // QPS 阈值

    rules.add(rule);
    SystemRuleManager.loadRules(rules);
}

// 授权规则（黑名单/白名单）
@PostConstruct
public void initAuthorityRules() {
    List<AuthorityRule> rules = new ArrayList<>();

    AuthorityRule rule = new AuthorityRule();
    rule.setResource("getUserById");
    rule.setStrategy(RuleConstant.AUTHORITY_WHITE);  // 白名单
    rule.setLimitApp("app1,app2");                   // 允许的应用

    rules.add(rule);
    AuthorityRuleManager.loadRules(rules);
}
```

### 3. OpenFeign（声明式服务调用）

```java
// 依赖
/*
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-openfeign</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-loadbalancer</artifactId>
</dependency>
*/

// 启用 Feign
@SpringBootApplication
@EnableFeignClients
public class OrderServiceApplication {}

// Feign 客户端
@FeignClient(
    name = "user-service",           // 服务名称
    path = "/api/users",              // 基础路径
    fallback = UserServiceFallback.class,  // 降级实现
    configuration = FeignConfig.class  // 配置类
)
public interface UserServiceClient {

    @GetMapping("/{id}")
    User getUserById(@PathVariable("id") Long id);

    @GetMapping
    Page<User> getUsers(
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "10") int size
    );

    @PostMapping
    User createUser(@RequestBody UserCreateDto dto);

    @PutMapping("/{id}")
    User updateUser(@PathVariable("id") Long id, @RequestBody UserUpdateDto dto);

    @DeleteMapping("/{id}")
    void deleteUser(@PathVariable("id") Long id);
}

// Feign 配置
@Configuration
public class FeignConfig {
    @Bean
    public RequestInterceptor requestInterceptor() {
        return template -> {
            // 添加认证头
            String token = SecurityContextHolder.getContext()
                .getAuthentication()
                .getCredentials()
                .toString();
            template.header("Authorization", "Bearer " + token);

            // 添加追踪ID
            String traceId = MDC.get("traceId");
            if (traceId != null) {
                template.header("X-Trace-Id", traceId);
            }

            // 添加请求时间
            template.header("X-Request-Time", String.valueOf(System.currentTimeMillis()));
        };
    }

    @Bean
    public Logger.Level feignLoggerLevel() {
        return Logger.Level.FULL;  // 记录完整的请求和响应
    }

    @Bean
    public Contract feignContract() {
        return new SpringMvcContract();  // 支持 Spring MVC 注解
    }

    @Bean
    public Encoder feignEncoder() {
        return new SpringFormEncoder(new JacksonEncoder());  // 支持 JSON
    }

    @Bean
    public Decoder feignDecoder() {
        return new JacksonDecoder();
    }

    @Bean
    public Feign.Builder feignBuilder() {
        return Feign.builder()
            .options(new Request.Options(
                10000,  // 连接超时
                60000   // 读取超时
            ))
            .retryer(new Retryer.Default(
                5000,      // 初始间隔
                60000,     // 最大间隔
                3         // 最大重试次数
            ));
    }
}

// 降级实现
@Component
public class UserServiceFallback implements UserServiceClient {
    @Override
    public User getUserById(Long id) {
        return User.builder()
            .id(-1L)
            .username("服务降级")
            .build();
    }

    @Override
    public Page<User> getUsers(int page, int size) {
        return Page.empty();
    }

    @Override
    public User createUser(UserCreateDto dto) {
        throw new BusinessException("服务不可用");
    }

    @Override
    public User updateUser(Long id, UserUpdateDto dto) {
        throw new BusinessException("服务不可用");
    }

    @Override
    public void deleteUser(Long id) {
        log.warn("删除用户失败，服务降级: userId={}", id);
    }
}

// 在 Service 中使用
@Service
public class OrderService {
    private final UserServiceClient userServiceClient;

    @GetMapping("/orders/{orderId}/user")
    public User getOrderUser(@PathVariable Long orderId) {
        Order order = orderRepository.findById(orderId)
            .orElseThrow(() -> new ResourceNotFoundException("订单不存在"));

        // 调用用户服务
        return userServiceClient.getUserById(order.getUserId());
    }
}
```

### 4. Seata（分布式事务）

```java
// 依赖
/*
<dependency>
    <groupId>com.alibaba.cloud</groupId>
    <artifactId>spring-cloud-starter-alibaba-seata</artifactId>
</dependency>
*/

// file.conf
/*
transport {
  type = "TCP"
  server = "Nacos"
}
service {
  vgroupMapping.my_tx_group = "default"
  default.grouplist = "127.0.0.1:8091"
  enableDegrade = false
  disable = false
}
*/

// registry.conf
/*
registry {
  type = "nacos"
  nacos {
    application = "seata-server"
    serverAddr = "localhost:8848"
    group = "SEATA_GROUP"
    namespace = ""
    cluster = "default"
  }
}
config {
  type = "nacos"
  nacos {
    serverAddr = "localhost:8848"
    group = "SEATA_GROUP"
    namespace = ""
  }
}
*/

// 全局事务注解
@Service
public class OrderService {

    // AT 模式
    @GlobalTransactional(name = "create-order", rollbackFor = Exception.class)
    public Order createOrder(OrderCreateDto dto) {
        // 1. 创建订单（本地事务）
        Order order = createOrderInternal(dto);

        // 2. 调用库存服务扣减库存（远程服务）
        inventoryClient.deductStock(dto.getProductId(), dto.getQuantity());

        // 3. 调用用户服务扣除余额（远程服务）
        userClient.deductBalance(dto.getUserId(), order.getTotalAmount());

        return order;
    }

    // TCC 模式
    @GlobalTransactional(name = "create-order-tcc", rollbackFor = Exception.class)
    public Order createOrderTCC(OrderCreateDto dto) {
        // 1. Prepare 阶段
        tccOrderService.prepare(dto);

        // 2. 调用其他服务 Prepare
        tccInventoryService.prepare(dto);
        tccUserService.prepare(dto);

        // 3. Commit 阶段（Seata 自动调用）
        // 或 Rollback 阶段（异常时自动调用）

        return order;
    }

    // SAGA 模式
    @GlobalTransactional(name = "create-order-saga", rollbackFor = Exception.class)
    public Order createOrderSaga(OrderCreateDto dto) {
        // 1. 创建订单
        Order order = createOrderInternal(dto);

        // 2. 预扣库存
        inventoryService.reserveStock(dto.getProductId(), dto.getQuantity());

        // 3. 锁定余额
        userService.freezeBalance(dto.getUserId(), order.getTotalAmount());

        // 4. 完成订单
        completeOrder(order);

        return order;
    }
}

// TCC 服务接口
@LocalTCC
public interface TccOrderService {
    // Prepare 阶段
    @TwoPhaseBusinessAction(
        name = "prepareOrder",
        commitMethod = "commit",
        rollbackMethod = "rollback"
    )
    boolean prepare(@BusinessActionContextParameter(paramName = "dto") OrderCreateDto dto);

    // Commit 阶段
    boolean commit(BusinessActionContext context);

    // Rollback 阶段
    boolean rollback(BusinessActionContext context);
}

@Service
public class TccOrderServiceImpl implements TccOrderService {

    @Override
    public boolean prepare(OrderCreateDto dto) {
        // 创建预留订单（状态为 PENDING）
        PendingOrder pendingOrder = PendingOrder.builder()
            .userId(dto.getUserId())
            .productId(dto.getProductId())
            .quantity(dto.getQuantity())
            .status(OrderStatus.PENDING)
            .build();

        pendingOrderRepository.save(pendingOrder);
        return true;
    }

    @Override
    public boolean commit(BusinessActionContext context) {
        // 将订单状态改为已确认
        String orderId = context.getActionContext("orderId");
        orderRepository.updateStatus(orderId, OrderStatus.CONFIRMED);
        return true;
    }

    @Override
    public boolean rollback(BusinessActionContext context) {
        // 取消订单
        String orderId = context.getActionContext("orderId");
        orderRepository.delete(orderId);
        return true;
    }
}
```

## 三、网关实现

### Gateway 路由配置

```yaml
# application.yml
spring:
  cloud:
    gateway:
      discovery:
        locator:
          enabled: true
          lower-case-service-id: true

      routes:
        # 用户服务路由
        - id: user-service
          uri: lb://user-service
          predicates:
            - Path=/api/users/**
          filters:
            - StripPrefix=1
            - name: RequestRateLimiter
              args:
                redis-rate-limiter.replenishRate: 10
                redis-rate-limiter.burstCapacity: 20
            - name: Retry
              args:
                retries: 3
                statuses: BAD_GATEWAY, SERVICE_UNAVAILABLE

        # 订单服务路由
        - id: order-service
          uri: lb://order-service
          predicates:
            - Path=/api/orders/**
          filters:
            - StripPrefix=1
            - AddRequestHeader=X-Gateway-Request-Id, ${uuid}
            - AddResponseHeader=X-Gateway-Response-Time, ${responseTime}

        # 商品服务路由（灰度发布）
        - id: product-service-v1
          uri: lb://product-service
          predicates:
            - Path=/api/products/**
            - Header=X-Version, v1

        - id: product-service-v2
          uri: lb://product-service-v2
          predicates:
            - Path=/api/products/**
            - Header=X-Version, v2

      # 全局配置
      default-filters:
        - name: GlobalFilter
        - name: LoggingFilter

    # 跨域配置
      globalcors:
        cors-configurations:
          '[/**]':
            allowed-origins: "*"
            allowed-methods:
              - GET
              - POST
              - PUT
              - DELETE
            allowed-headers: "*"
            allow-credentials: true
            max-age: 3600

# 服务配置
server:
  port: 8080

# 日志配置
logging:
  level:
    org.springframework.cloud.gateway: DEBUG
```

### 自定义过滤器

```java
// 认证过滤器
@Component
public class AuthenticationFilter implements GlobalFilter, Ordered {

    private final JwtTokenProvider tokenProvider;
    private final RedisTemplate<String, String> redisTemplate;

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        String path = exchange.getRequest().getPath().value();

        // 跳过白名单路径
        if (isWhiteListPath(path)) {
            return chain.filter(exchange);
        }

        // 获取 Token
        String token = extractToken(exchange.getRequest());

        if (token == null) {
            return unauthorized(exchange, "缺少认证令牌");
        }

        // 验证 Token
        if (!tokenProvider.validateToken(token)) {
            return unauthorized(exchange, "认证令牌无效");
        }

        // 检查 Token 是否在黑名单
        if (isTokenBlacklisted(token)) {
            return unauthorized(exchange, "认证令牌已失效");
        }

        // 获取用户信息
        String username = tokenProvider.getUsernameFromToken(token);

        // 检查用户权限
        if (!hasPermission(username, path)) {
            return forbidden(exchange, "无访问权限");
        }

        // 添加用户信息到请求头
        ServerWebExchange modifiedExchange = exchange.mutate()
            .request(exchange.getRequest().mutate()
                .header("X-User-Id", getUserId(username))
                .header("X-Username", username)
                .header("X-Roles", getRoles(username))
                .build())
            .build();

        return chain.filter(modifiedExchange);
    }

    @Override
    public int getOrder() {
        return -100;  // 优先级最高
    }

    private boolean isWhiteListPath(String path) {
        return path.matches("(/api/auth/login|/api/auth/register|/health|/actuator/.*)");
    }

    private String extractToken(ServerHttpRequest request) {
        String bearerToken = request.getHeaders().getFirst("Authorization");
        if (bearerToken != null && bearerToken.startsWith("Bearer ")) {
            return bearerToken.substring(7);
        }
        return null;
    }

    private boolean isTokenBlacklisted(String token) {
        return Boolean.TRUE.equals(redisTemplate.hasKey("blacklist:" + token));
    }

    private Mono<Void> unauthorized(ServerWebExchange exchange, String message) {
        exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
        return writeResponse(exchange, ErrorResponse.of(401, message));
    }

    private Mono<Void> forbidden(ServerWebExchange exchange, String message) {
        exchange.getResponse().setStatusCode(HttpStatus.FORBIDDEN);
        return writeResponse(exchange, ErrorResponse.of(403, message));
    }

    private Mono<Void> writeResponse(ServerWebExchange exchange, ErrorResponse error) {
        exchange.getResponse().getHeaders().setContentType(MediaType.APPLICATION_JSON);
        DataBuffer buffer = exchange.getResponse().bufferFactory()
            .wrap(error.toString().getBytes());
        return exchange.getResponse().writeWith(Mono.just(buffer));
    }
}

// 日志过滤器
@Component
@Slf4j
public class LoggingFilter implements GlobalFilter, Ordered {

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        ServerHttpRequest request = exchange.getRequest();
        long startTime = System.currentTimeMillis();

        // 记录请求信息
        String requestId = MDC.get("traceId");
        if (requestId == null) {
            requestId = UUID.randomUUID().toString();
            MDC.put("traceId", requestId);
        }

        log.info("Gateway Request: {} {} | TraceId: {}",
            request.getMethod(), request.getURI(), requestId);

        return chain.filter(exchange).then(Mono.fromRunnable(() -> {
            long duration = System.currentTimeMillis() - startTime;
            ServerHttpResponse response = exchange.getResponse();

            log.info("Gateway Response: {} | Status: {} | Duration: {}ms | TraceId: {}",
                request.getURI(), response.getStatusCode(), duration, requestId);

            // 保存日志到数据库或日志系统
            saveLog(exchange, duration);
        }));
    }

    @Override
    public int getOrder() {
        return Ordered.LOWEST_PRECEDENCE;
    }

    private void saveLog(ServerWebExchange exchange, long duration) {
        // 保存网关日志
    }
}

// 限流过滤器
@Component
public class RateLimitFilter implements GlobalFilter, Ordered {

    private final RedisTemplate<String, String> redisTemplate;
    private final RateLimitProperties properties;

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        String clientId = getClientId(exchange.getRequest());

        // 从 Redis 获取当前请求数
        String key = "rate:limit:" + clientId;
        Long currentCount = redisTemplate.opsForValue().increment(key);
        redisTemplate.expire(key, 1, TimeUnit.SECONDS);

        if (currentCount > properties.getMaxRequests()) {
            // 超过限制
            exchange.getResponse().setStatusCode(HttpStatus.TOO_MANY_REQUESTS);
            exchange.getResponse().getHeaders().add("X-RateLimit-Limit",
                String.valueOf(properties.getMaxRequests()));
            exchange.getResponse().getHeaders().add("X-RateLimit-Remaining", "0");
            exchange.getResponse().getHeaders().add("X-RateLimit-Reset", "1");

            return writeResponse(exchange, ErrorResponse.of(429, "请求过于频繁"));
        }

        return chain.filter(exchange);
    }

    private String getClientId(ServerHttpRequest request) {
        // 优先使用用户ID，否则使用IP地址
        String userId = request.getHeaders().getFirst("X-User-Id");
        if (userId != null) {
            return userId;
        }

        return request.getRemoteAddress().getAddress().getHostAddress();
    }
}

// 动态路由配置
@RestController
@RequestMapping("/gateway/routes")
public class RouteController {

    private final RouteDefinitionLocator routeDefinitionLocator;
    private final RouteDefinitionWriter routeDefinitionWriter;

    @GetMapping
    public Flux<RouteDefinition> getRoutes() {
        return routeDefinitionLocator.getRouteDefinitions();
    }

    @PostMapping
    public Mono<Void> addRoute(@RequestBody RouteDefinition definition) {
        return routeDefinitionWriter.save(Mono.just(definition)).then();
    }

    @DeleteMapping("/{id}")
    public Mono<Void> deleteRoute(@PathVariable String id) {
        return routeDefinitionWriter.delete(Mono.just(id)).then();
    }
}
```

## 小结

本节学习了 Spring Cloud Alibaba 微服务：

- **Nacos** - 服务注册、配置中心
- **Sentinel** - 流量控制、熔断降级
- **OpenFeign** - 声明式服务调用
- **Seata** - 分布式事务
- **Gateway** - API 网关、路由配置、过滤器

## 实践练习

### 编程题
1. 搭建一个包含 3 个微服务（用户、订单、商品）+ Nacos + Gateway + Sentinel 的最小微服务系统，实现服务间的 Feign 调用和网关路由。
2. 配置 Sentinel 实现 QPS 限流和降级规则，模拟高并发场景，观察限流效果。

### 思考题
1. Nacos 作为配置中心，配置的动态刷新原理是什么？`@RefreshScope` 的作用机制？
2. 微服务架构中分布式事务如何处理？Seata 的 AT 模式和 Saga 模式各适合什么场景？

### 自测题
1. Spring Cloud Alibaba 包含哪些核心组件？
2. Nacos 同时支持哪两大功能？
3. Sentinel 的限流模式和降级策略有哪些？

下一步将学习 Redis 缓存（→ `redis/beginner/01-redis-basics.md`）。