# Spring Cloud Alibaba 微服务平台架构

## 一、概述

构建生产级微服务平台：Nacos 集群、Sentinel 规则中心、Seata 分布式事务、SkyWalking 全链路监控。

## 二、Nacos 集群部署

### 生产集群架构

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Nacos Node 1 │────▶│ Nacos Node 2 │────▶│ Nacos Node 3 │
│ 192.168.1.1  │     │ 192.168.1.2  │     │ 192.168.1.3  │
└──────────────┘     └──────────────┘     └──────────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  MySQL Cluster  │
                    │  (持久化存储)    │
                    └─────────────────┘
```

### 集群配置

```properties
# cluster.conf
192.168.1.1:8848
192.168.1.2:8848
192.168.1.3:8848

# application.properties
server.port=8848
spring.datasource.platform=mysql
db.url.0=jdbc:mysql://mysql-cluster:3306/nacos?characterEncoding=utf8
db.user= nacos
db.password=${NACOS_DB_PASSWORD}
nacos.core.auth.enabled=true
nacos.core.auth.server.identity.key=myKey
nacos.core.auth.server.identity.value=myValue
```

### 命名空间与隔离

```yaml
spring:
  cloud:
    nacos:
      config:
        server-addr: ${NACOS_SERVER:localhost:8848}
        namespace: ${NACOS_NAMESPACE:prod}   # 环境隔离
        group: ${NACOS_GROUP:DEFAULT_GROUP}
        file-extension: yaml
        refresh-enabled: true
      discovery:
        server-addr: ${NACOS_SERVER:localhost:8848}
        namespace: ${NACOS_NAMESPACE:prod}
        metadata:
          version: ${APP_VERSION:v1}
          gray: ${GRAY_ENABLED:false}
```

## 三、Seata 分布式事务

### AT 模式架构

```
TM (事务管理器) ──→ TC (事务协调器) ←── RM (资源管理器)
     │                                    │
     │                            ┌───────┴──────┐
     │                            │ 数据库/Redis  │
     │                            │  undo_log    │
     │                            └──────────────┘
  begin global tx
    → 注册分支事务
    → 执行业务 SQL
    → 上报回滚镜像
    → commit/rollback
```

### Seata 配置

```yaml
seata:
  enabled: true
  application-id: ${spring.application.name}
  tx-service-group: my_test_tx_group
  config:
    type: nacos
    nacos:
      server-addr: ${NACOS_SERVER}
      group: SEATA_GROUP
  registry:
    type: nacos
    nacos:
      server-addr: ${NACOS_SERVER}
      group: SEATA_GROUP
```

### 分布式事务实战

```java
@Service
public class OrderBusinessService {
    @Autowired
    private OrderService orderService;
    @Autowired
    private AccountService accountService;
    @Autowired
    private InventoryService inventoryService;

    @GlobalTransactional(name = "create-order", rollbackFor = Exception.class)
    public Order createOrder(OrderDTO dto) {
        // 1. 扣减账户余额
        accountService.deduct(dto.getUserId(), dto.getAmount());
        
        // 2. 扣减库存
        inventoryService.deduct(dto.getProductId(), dto.getQuantity());
        
        // 3. 创建订单
        Order order = orderService.create(dto);
        
        return order;
    }
}

// AccountService 中的本地事务
@Transactional(rollbackFor = Exception.class)
public void deduct(Long userId, BigDecimal amount) {
    Account account = accountDao.selectByUserId(userId);
    if (account.getBalance().compareTo(amount) < 0) {
        throw new BusinessException("余额不足");
    }
    accountDao.updateBalance(userId, account.getBalance().subtract(amount));
}
```

### TCC 模式

```java
@LocalTCC
public class AccountTCCService {
    @TwoPhaseBusinessAction(
        name = "deduct",
        commitMethod = "confirm",
        rollbackMethod = "cancel"
    )
    public void deduct(BusinessActionContext ctx,
                       @BusinessActionContextParameter(paramName = "userId") Long userId,
                       @BusinessActionContextParameter(paramName = "amount") BigDecimal amount) {
        // Try: 冻结金额
        accountDao.freezeBalance(userId, amount);
    }

    public void confirm(BusinessActionContext ctx) {
        // Confirm: 扣除冻结金额
        accountDao.confirmDeduct(ctx.getActionContext("userId"),
            ctx.getActionContext("amount"));
    }

    public void cancel(BusinessActionContext ctx) {
        // Cancel: 解冻金额
        accountDao.unfreezeBalance(ctx.getActionContext("userId"),
            ctx.getActionContext("amount"));
    }
}
```

## 四、SkyWalking 全链路监控

### 架构

```
Agent (探针) → OAP Server → Storage (ES) → UI
```

### Agent 配置

```bash
# 添加 JVM 参数接入探针
-javaagent:/path/to/skywalking-agent.jar
-Dskywalking.agent.service_name=order-service
-Dskywalking.collector.backend_service=oap:11800
-Dskywalking.logging.level=WARN
```

### 自定义 Span

```java
@Trace
public void processOrder(Order order) {
    // 自动追踪
}

// 手动埋点追踪关键链路
public void handleRefund(RefundRequest request) {
    Span span = Span.tag("refund", request.getOrderId())
        .tag("amount", request.getAmount().toString())
        .start();
    try (AbstractTracingContext ignored = span.asActive()) {
        // 退款逻辑
    } finally {
        span.stop();
    }
}
```

### 告警规则

```yaml
# alarm-settings.yml
rules:
  service_resp_time_rule:
    match-name: order-service
    threshold: 2000
    period: 10
    count: 3
    silence-period: 5
    message: Response time of {name} is more than 2000ms in last 10 minutes.
  service_sla_rule:
    threshold: 80
    period: 5
    count: 2
    message: Success rate of {name} is lower than 80% in last 5 minutes.
  
webhooks:
  - http://alertmanager:9093/api/v1/alerts
```

## 课后练习

1. 搭建 3 节点 Nacos 集群 + MySQL 持久化
2. 使用 Seata AT 模式实现跨服务转账（扣发 + 收款 + 记录流水）
3. 部署 SkyWalking 并对微服务全链路追踪
4. 设计一套灰度发布方案：按 IP / 用户 Tag / 区域分流

## 自测题

1. Seata AT 模式中 undo_log 表的作用？ A) 记录操作日志 B) 存储回滚镜像 C) 缓存数据 D) 序列号生成
2. Nacos 中 Namespace 的主要用途？ A) 配置分组 B) 环境隔离 C) 权限控制 D) 数据分区
3. SkyWalking 探针使用什么技术实现无侵入？ A) AOP B) Java Agent + ByteBuddy C) 反射 D) 动态代理

**答案：** 1-B, 2-B, 3-B
