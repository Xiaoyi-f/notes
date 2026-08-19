# Spring Boot 进阶开发

## 一、概述

深入 Spring Boot 核心机制：自动配置原理、Actuator 生产监控、自定义 Starter、配置加密、指标度量。

## 二、自动配置原理

### @SpringBootApplication 组合注解

```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Inherited
@SpringBootConfiguration    // 本质是 @Configuration
@EnableAutoConfiguration    // 核心：自动配置
@ComponentScan             // 包扫描
public @interface SpringBootApplication {}
```

### @EnableAutoConfiguration 工作流程

```
@EnableAutoConfiguration
    → @Import(AutoConfigurationImportSelector.class)
        → spring.factories 中 EnableAutoConfiguration 配置列表
        → 逐条评估 @Conditional 条件
        → 条件匹配则加载对应的 AutoConfiguration
```

### 自定义 AutoConfiguration

```java
// 1. 业务类
public class SmsSender {
    private final String accessKey;
    private final String secretKey;

    public SmsSender(String accessKey, String secretKey) {
        this.accessKey = accessKey;
        this.secretKey = secretKey;
    }

    public void send(String phone, String message) {
        System.out.printf("Send SMS to %s: %s%n", phone, message);
    }
}

// 2. 配置属性
@ConfigurationProperties(prefix = "sms")
public class SmsProperties {
    private String accessKey;
    private String secretKey;
    // getters & setters
}

// 3. 自动配置类
@Configuration
@ConditionalOnClass(SmsSender.class)
@EnableConfigurationProperties(SmsProperties.class)
public class SmsAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean
    @ConditionalOnProperty(prefix = "sms", name = "enabled", havingValue = "true", matchIfMissing = true)
    public SmsSender smsSender(SmsProperties properties) {
        return new SmsSender(properties.getAccessKey(), properties.getSecretKey());
    }
}

// 4. META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
// sms.SmsAutoConfiguration
```

### 常用条件注解

| 注解 | 条件说明 |
|------|----------|
| @ConditionalOnClass | 类路径存在指定类 |
| @ConditionalOnMissingBean | 容器中没有指定 Bean |
| @ConditionalOnProperty | 配置属性匹配 |
| @ConditionalOnExpression | SpEL 表达式 |
| @ConditionalOnWebApplication | Web 环境 |
| @ConditionalOnResource | 资源文件存在 |

## 三、Actuator 生产监控

### 核心端点

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus,loggers,env,heapdump,threaddump
      base-path: /actuator
  endpoint:
    health:
      show-details: when-authorized
    shutdown:
      enabled: false
  metrics:
    tags:
      application: ${spring.application.name}
```

### 自定义 Health Indicator

```java
@Component
public class DatabaseHealthIndicator implements HealthIndicator {
    @Autowired
    private DataSource dataSource;

    @Override
    public Health health() {
        try (Connection conn = dataSource.getConnection()) {
            if (conn.isValid(3)) {
                return Health.up()
                    .withDetail("database", "reachable")
                    .withDetail("type", conn.getMetaData().getDatabaseProductName())
                    .build();
            }
            return Health.down().withDetail("database", "unreachable").build();
        } catch (Exception e) {
            return Health.down(e).build();
        }
    }
}

// 自定义 Metrics
@Component
public class OrderMetrics {
    private final Counter orderCreated;
    private final Counter paymentFailed;
    private final Timer orderProcessing;

    public OrderMetrics(MeterRegistry registry) {
        this.orderCreated = registry.counter("order.created.total");
        this.paymentFailed = registry.counter("order.payment.failed");
        this.orderProcessing = registry.timer("order.processing.time");
    }

    public void recordOrder() {
        orderCreated.increment();
    }

    @Timed(value = "order.payment", description = "Payment processing time")
    public void processPayment() {
        // ...
    }
}
```

## 四、配置管理

### 配置加密

```java
@Configuration
public class EncryptionConfig {
    @Bean
    public EnvironmentPostProcessor encryptedPropertyProcessor() {
        return (environment, application) -> {
            // 读取加密配置并解密后注入环境
            String encrypted = environment.getProperty("db.password.encrypted");
            if (encrypted != null) {
                String decrypted = decrypt(encrypted);
                System.setProperty("db.password", decrypted);
            }
        };
    }

    private String decrypt(String encrypted) {
        // AES/GCM 解密
        // ...
        return decrypted;
    }
}

// application.yml 中引用
db:
  password.encrypted: "ENC(MsFVAsdf...)"  # 加密后的密码
  password: ${db.password.encrypted}       # 解密后替换
```

### 多环境配置

```yaml
# application-dev.yml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/dev_db
  redis:
    host: localhost

# application-prod.yml
spring:
  datasource:
    url: jdbc:mysql://prod-cluster:3306/prod_db
    hikari:
      maximum-pool-size: 50
      minimum-idle: 10
  redis:
    host: redis-cluster
    timeout: 3000ms
    lettuce:
      pool:
        max-active: 32
```

## 五、启动优化

```java
@Component
public class StartupTimeReporter implements ApplicationRunner {
    @Override
    public void run(ApplicationArguments args) {
        // 使用 Spring ApplicationStartedEvent 或 ApplicationReadyEvent
    }
}

@Configuration
public class LazyInitConfig {
    // 延迟初始化：非核心 Bean 在使用时才初始化
    @Bean
    @Lazy(value = false)  // false 表示非延迟
    public ReportService reportService() {
        return new ReportService();
    }
}

// 启动分析
// VM Options: -Dspring.autoconfigure.exclude=org.springframework.boot.autoconfigure.data.mongo.MongoDataAutoConfiguration
// 排除不必要的自动配置可减少 30%+ 启动时间

// 启动缓存: spring-context-indexer 依赖预编译
// <dependency>
//     <groupId>org.springframework</groupId>
//     <artifactId>spring-context-indexer</artifactId>
//     <optional>true</optional>
// </dependency>
```

## 课后练习

1. 实现一个自定义 Metrics 拦截器，统计每个 API 的 QPS 和 P99 延迟
2. 编写一个 Spring Boot Starter（如：短信发送、OSS 存储）
3. 使用 Micrometer + Prometheus 构建应用监控看板
4. 实现动态配置刷新（基于 Apollo / Nacos 或自定义 + @RefreshScope）

## 自测题

1. @ConditionalOnMissingBean 的作用？ A) 类存在时创建 B) Bean 不存在时创建 C) 属性匹配时创建 D) 表达式为真时创建
2. Actuator 中哪个端点可用于修改日志级别？ A) health B) env C) loggers D) metrics
3. Spring Boot 启动过程中最早执行的扩展点是？ A) ApplicationRunner B) CommandLineRunner C) ApplicationContextInitializer D) BeanPostProcessor

**答案：** 1-B, 2-C, 3-C
