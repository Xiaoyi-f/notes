# Spring Cloud Alibaba 微服务网关

## 一、概述

微服务网关作为系统的统一入口，负责请求路由、认证鉴权、限流熔断、协议转换。基于 Spring Cloud Gateway + Nacos 实现动态路由。

## 二、网关核心能力

| 能力 | 实现 | 说明 |
|------|------|------|
| 动态路由 | Nacos + Gateway | 配置中心动态更新路由规则 |
| 认证鉴权 | JWT + GlobalFilter | 统一 Token 校验 |
| 限流熔断 | Sentinel | 按 API/参数/来源限流 |
| 灰度发布 | Nacos Metadata | 基于权重/Header 分流 |
| 日志审计 | 自定义 Filter | 全量请求日志 |

## 三、动态路由实现

### 基础配置

```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: user-service
          uri: lb://user-service
          predicates:
            - Path=/api/users/**
          filters:
            - StripPrefix=1
            - name: RequestRateLimiter
              args:
                redis-rate-limiter:
                  replenishRate: 100
                  burstCapacity: 200
        - id: order-service
          uri: lb://order-service
          predicates:
            - Path=/api/orders/**
          filters:
            - StripPrefix=1
```

### Nacos 动态路由

```java
@Component
public class NacosDynamicRouteService {
    @Autowired
    private RouteDefinitionWriter routeDefinitionWriter;
    @Autowired
    private NacosConfigManager nacosConfigManager;

    @PostConstruct
    public void init() {
        // 监听 Nacos 配置变化
        nacosConfigManager.getConfigService().addListener(
            "gateway-routes.json", "DEFAULT_GROUP", new Listener() {
                @Override
                public Executor getExecutor() {
                    return Executors.newSingleThreadExecutor();
                }

                @Override
                public void receiveConfigInfo(String configInfo) {
                    // 解析 JSON 配置并刷新路由
                    List<RouteDefinition> routes = JSON.parseArray(
                        configInfo, RouteDefinition.class);
                    for (RouteDefinition route : routes) {
                        routeDefinitionWriter.save(
                            Mono.just(route)).subscribe();
                    }
                }
            }
        );
    }
}
```

## 四、GlobalFilter 实战

### 认证过滤器

```java
@Component
@Order(-1)
public class AuthGlobalFilter implements GlobalFilter {
    private static final Set<String> WHITE_LIST = Set.of(
        "/api/auth/login", "/api/auth/register",
        "/api/public/", "/actuator/"
    );

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        String path = exchange.getRequest().getURI().getPath();
        
        // 白名单放行
        if (WHITE_LIST.stream().anyMatch(path::startsWith)) {
            return chain.filter(exchange);
        }

        // 校验 Token
        String token = exchange.getRequest().getHeaders()
            .getFirst("Authorization");
        if (token == null || !token.startsWith("Bearer ")) {
            return unauthorized(exchange, "Missing token");
        }

        try {
            Jwt jwt = JwtUtil.parse(token.substring(7));
            // 将用户信息传递到下游服务
            ServerWebExchange mutated = exchange.mutate()
                .request(r -> r.header("X-User-Id", jwt.getSubject())
                               .header("X-User-Role", jwt.getClaim("role")))
                .build();
            return chain.filter(mutated);
        } catch (Exception e) {
            return unauthorized(exchange, "Invalid token");
        }
    }

    private Mono<Void> unauthorized(ServerWebExchange exchange, String msg) {
        exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
        return exchange.getResponse()
            .writeWith(Mono.just(exchange.getResponse().bufferFactory()
                .wrap(("{\"code\":401,\"message\":\"" + msg + "\"}").getBytes())));
    }
}
```

### 灰度发布过滤器

```java
@Component
public class GrayPublishingFilter implements GlobalFilter {
    @Autowired
    private LoadBalancerClient loadBalancerClient;

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        String version = exchange.getRequest().getHeaders()
            .getFirst("X-Version");
        if (version != null) {
            // 使用自定义负载均衡策略
            exchange.getAttributes().put("version", version);
        }
        return chain.filter(exchange);
    }
}

// 自定义负载均衡策略
public class GrayLoadBalancer implements ReactorServiceInstanceLoadBalancer {
    @Override
    public Mono<Response<ServiceInstance>> choose(Request request) {
        // 从 Request 获取 version
        String version = request.getContext() != null ?
            (String) request.getContext().get("version") : null;
        
        List<ServiceInstance> instances = ...;  // 从 Nacos 获取
        // 过滤出版本匹配的实例
        List<ServiceInstance> matched = instances.stream()
            .filter(i -> version == null || 
                version.equals(i.getMetadata().get("version")))
            .collect(Collectors.toList());
        
        if (matched.isEmpty()) {
            matched = instances;  // 降级到所有实例
        }
        return Mono.just(new DefaultResponse(
            matched.get(ThreadLocalRandom.current().nextInt(matched.size()))));
    }
}
```

## 五、Sentinel 网关限流

```yaml
spring:
  cloud:
    sentinel:
      transport:
        dashboard: localhost:8080
      datasource:
        ds1:
          nacos:
            server-addr: localhost:8848
            data-id: sentinel-gateway-rules
            rule-type: gw_flow
```

```java
@Configuration
public class GatewaySentinelConfig {
    @PostConstruct
    public void initGatewayRules() {
        Set<GatewayFlowRule> rules = new HashSet<>();
        // 按 API 限流
        rules.add(new GatewayFlowRule("user-service")
            .setCount(1000)           // 每秒 1000 次
            .setIntervalSec(1)
            .setBurst(200)            // 突发 200
            .setParamItem(new GatewayParamFlowItem()
                .setParseStrategy(SentinelGatewayConstants.PARAM_PARSE_STRATEGY_URL_PARAM)
                .setFieldName("userId")));
        // 按来源限流
        rules.add(new GatewayFlowRule("order-service")
            .setCount(500)
            .setResourceMode(SentinelGatewayConstants.RESOURCE_MODE_ROUTE_ID)
            .setParamItem(new GatewayParamFlowItem()
                .setParseStrategy(SentinelGatewayConstants
                    .PARAM_PARSE_STRATEGY_HEADER)
                .setFieldName("X-Source")));
        
        GatewayRuleManager.loadRules(rules);
    }
}
```

## 课后练习

1. 实现基于 Nacos 配置的动态路由刷新，支持实时生效
2. 编写一个请求日志审计 Filter，记录请求参数、响应时间
3. 集成 Sentinel 网关限流并配置 Nacos 动态规则
4. 实现基于用户 ID 哈希的一致性路由（同一用户路由到同一实例）

## 自测题

1. Spring Cloud Gateway 底层通信模型基于？ A) Servlet B) Netty C) Tomcat D) Undertow
2. Gateway 的 Filter 执行顺序由什么决定？ A) @Order B) filter 名称 C) 配置顺序 D) 随机
3. Sentinel 网关限流的粒度可以到？ A) 路由级别 B) API 级别 C) 参数级别 D) 以上都是

**答案：** 1-B, 2-A, 3-D
