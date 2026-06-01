# Spring 学习笔记 - 第四课：Spring Boot 自动配置原理

## 1. 什么是自动配置？

**自动配置 = 根据类路径下的依赖和配置，自动创建和配置 Bean**

### 传统配置 vs 自动配置

```java
// 传统方式：手动配置每个 Bean
@Configuration
public class DataSourceConfig {
    @Bean
    public DataSource dataSource() {
        return new DriverManagerDataSource(url, username, password);
    }
}

// 自动配置：Spring Boot 自动检测并配置
// 只需添加依赖，无需手动配置
<dependency>
    <groupId>com.mysql</groupId>
    <artifactId>mysql-connector-j</artifactId>
</dependency>
```

---

## 2. 自动配置原理（面试核心）

### 原理流程图

```
┌─────────────────────────────────────────────────────────────────┐
│                        @SpringBootApplication                   │
├─────────────────────────────────────────────────────────────────┤
│  @SpringBootConfiguration  ───→ 标识为配置类                      │
│  @EnableAutoConfiguration ───→ 启用自动配置（核心！）             │
│  @ComponentScan           ───→ 扫描组件                          │
└─────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│                  @EnableAutoConfiguration                       │
│                   @Import(AutoConfigurationImportSelector.class) │
└─────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│              AutoConfigurationImportSelector                     │
│           读取 spring.factories 文件，获取自动配置类             │
│           位置：META-INF/spring.factories                       │
└─────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│                获取所有自动配置类（100+ 个）                     │
│  - DataSourceAutoConfiguration                                  │
│  - WebMvcAutoConfiguration                                      │
│  - JpaAutoConfiguration                                         │
│  - RedisAutoConfiguration                                       │
│  - ...                                                           │
└─────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│                  按需加载自动配置类                              │
│  通过 @Conditional 注解判断是否满足条件                         │
└─────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│                创建满足条件的 Bean                               │
└─────────────────────────────────────────────────────────────────┘
```

### 关键步骤

1. **@EnableAutoConfiguration** 启用自动配置
2. **AutoConfigurationImportSelector** 读取配置文件
3. **spring.factories** 获取所有自动配置类
4. **@Conditional** 按需加载
5. **创建 Bean** 注册到容器

---

## 3. spring.factories 文件

### 文件位置

```
spring-boot-autoconfigure-3.x.x.jar
└── META-INF
    └── org.springframework.boot.autoconfigure.AutoConfiguration.imports
```

### 文件内容示例（Spring Boot 3.x）

```
# org.springframework.boot.autoconfigure.AutoConfiguration.imports
org.springframework.boot.autoconfigure.admin.SpringApplicationAdminJmxAutoConfiguration
org.springframework.boot.autoconfigure.aop.AopAutoConfiguration
org.springframework.boot.autoconfigure.amqp.RabbitAutoConfiguration
org.springframework.boot.autoconfigure.batch.BatchAutoConfiguration
org.springframework.boot.autoconfigure.cache.CacheAutoConfiguration
org.springframework.boot.autoconfigure.cassandra.CassandraAutoConfiguration
org.springframework.boot.autoconfigure.context.ConfigurationPropertiesAutoConfiguration
org.springframework.boot.autoconfigure.dao.PersistenceExceptionTranslationAutoConfiguration
org.springframework.boot.autoconfigure.data.cassandra.CassandraDataAutoConfiguration
org.springframework.boot.autoconfigure.data.cassandra.CassandraReactiveDataAutoConfiguration
org.springframework.boot.autoconfigure.data.cassandra.CassandraRepositoriesAutoConfiguration
org.springframework.boot.autoconfigure.data.couchbase.CouchbaseDataAutoConfiguration
org.springframework.boot.autoconfigure.data.couchbase.CouchbaseReactiveDataAutoConfiguration
org.springframework.boot.autoconfigure.data.couchbase.CouchbaseRepositoriesAutoConfiguration
org.springframework.boot.autoconfigure.data.elasticsearch.ElasticsearchDataAutoConfiguration
org.springframework.boot.autoconfigure.data.elasticsearch.ElasticsearchReactiveDataAutoConfiguration
org.springframework.boot.autoconfigure.data.elasticsearch.ElasticsearchRepositoriesAutoConfiguration
org.springframework.boot.autoconfigure.data.jdbc.JdbcRepositoriesAutoConfiguration
org.springframework.boot.autoconfigure.data.jpa.JpaRepositoriesAutoConfiguration
org.springframework.boot.autoconfigure.data.ldap.LdapRepositoriesAutoConfiguration
org.springframework.boot.autoconfigure.data.mongo.MongoDataAutoConfiguration
org.springframework.boot.autoconfigure.data.mongo.MongoReactiveDataAutoConfiguration
org.springframework.boot.autoconfigure.data.mongo.MongoRepositoriesAutoConfiguration
org.springframework.boot.autoconfigure.data.neo4j.Neo4jDataAutoConfiguration
org.springframework.boot.autoconfigure.data.neo4j.Neo4jReactiveDataAutoConfiguration
org.springframework.boot.autoconfigure.data.neo4j.Neo4jRepositoriesAutoConfiguration
org.springframework.boot.autoconfigure.data.r2dbc.R2dbcDataAutoConfiguration
org.springframework.boot.autoconfigure.data.r2dbc.R2dbcRepositoriesAutoConfiguration
org.springframework.boot.autoconfigure.data.redis.RedisAutoConfiguration
org.springframework.boot.autoconfigure.data.redis.RedisReactiveAutoConfiguration
org.springframework.boot.autoconfigure.data.redis.RedisRepositoriesAutoConfiguration
org.springframework.boot.autoconfigure.data.rest.RepositoryRestMvcAutoConfiguration
org.springframework.boot.autoconfigure.data.web.RepositoryRestMvcAutoConfiguration
org.springframework.boot.autoconfigure.elasticsearch.ElasticsearchRestClientAutoConfiguration
org.springframework.boot.autoconfigure.flyway.FlywayAutoConfiguration
org.springframework.boot.autoconfigure.freemarker.FreeMarkerAutoConfiguration
org.springframework.boot.autoconfigure.groovy.template.GroovyTemplateAutoConfiguration
org.springframework.boot.autoconfigure.gson.GsonAutoConfiguration
org.springframework.boot.autoconfigure.h2.H2ConsoleAutoConfiguration
org.springframework.boot.autoconfigure.hazelcast.HazelcastAutoConfiguration
org.springframework.boot.autoconfigure.hateoas.HypermediaAutoConfiguration
org.springframework.boot.autoconfigure.integration.IntegrationAutoConfiguration
org.springframework.boot.autoconfigure.jackson.JacksonAutoConfiguration
org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration
org.springframework.boot.autoconfigure.jdbc.JdbcTemplateAutoConfiguration
org.springframework.boot.autoconfigure.jdbc.JndiDataSourceAutoConfiguration
org.springframework.boot.autoconfigure.jms.JmsAutoConfiguration
org.springframework.boot.autoconfigure.jmx.JmxAutoConfiguration
org.springframework.boot.autoconfigure.mail.MailSenderAutoConfiguration
org.springframework.boot.autoconfigure.mongo.MongoAutoConfiguration
org.springframework.boot.autoconfigure.mongo.MongoReactiveAutoConfiguration
org.springframework.boot.autoconfigure.mustache.MustacheAutoConfiguration
org.springframework.boot.autoconfigure.orm.jpa.HibernateJpaAutoConfiguration
org.springframework.boot.autoconfigure.quartz.QuartzAutoConfiguration
org.springframework.boot.autoconfigure.r2dbc.R2dbcAutoConfiguration
org.springframework.boot.autoconfigure.rabbit.RabbitAutoConfiguration
org.springframework.boot.autoconfigure.reactor.core.ReactorCoreAutoConfiguration
org.springframework.boot.autoconfigure.security.servlet.SecurityAutoConfiguration
org.springframework.boot.autoconfigure.security.servlet.UserDetailsServiceAutoConfiguration
org.springframework.boot.autoconfigure.sendgrid.SendGridAutoConfiguration
org.springframework.boot.autoconfigure.session.SessionAutoConfiguration
org.springframework.boot.autoconfigure.solr.SolrAutoConfiguration
org.springframework.boot.autoconfigure.task.TaskExecutionAutoConfiguration
org.springframework.boot.autoconfigure.task.TaskSchedulingAutoConfiguration
org.springframework.boot.autoconfigure.thymeleaf.ThymeleafAutoConfiguration
org.springframework.boot.autoconfigure.transaction.TransactionAutoConfiguration
org.springframework.boot.autoconfigure.validation.ValidationAutoConfiguration
org.springframework.boot.autoconfigure.web.client.RestTemplateAutoConfiguration
org.springframework.boot.autoconfigure.web.embedded.EmbeddedWebServerFactoryCustomizerAutoConfiguration
org.springframework.boot.autoconfigure.web.servlet.DispatcherServletAutoConfiguration
org.springframework.boot.autoconfigure.web.servlet.ServletWebServerFactoryAutoConfiguration
org.springframework.boot.autoconfigure.web.servlet.WebMvcAutoConfiguration
org.springframework.boot.autoconfigure.web.servlet.error.ErrorMvcAutoConfiguration
org.springframework.boot.autoconfigure.web.servlet.filter.FormContentFilterAutoConfiguration
org.springframework.boot.autoconfigure.websocket.servlet.WebSocketServletAutoConfiguration
```

---

## 4. @Conditional 系列注解（核心！）

自动配置按需加载的关键注解：

| 注解 | 条件 |
|------|------|
| `@ConditionalOnClass` | 类路径下存在指定类 |
| `@ConditionalOnMissingClass` | 类路径下不存在指定类 |
| `@ConditionalOnBean` | 容器中存在指定 Bean |
| `@ConditionalOnMissingBean` | 容器中不存在指定 Bean |
| `@ConditionalOnProperty` | 配置文件中指定属性匹配 |
| `@ConditionalOnResource` | 类路径下存在指定资源 |
| `@ConditionalOnExpression` | SpEL 表达式为 true |
| `@ConditionalOnJava` | Java 版本匹配 |
| `@ConditionalOnWebApplication` | 是 Web 应用 |
| `@ConditionalOnNotWebApplication` | 不是 Web 应用 |

### 使用示例

```java
@Configuration
@ConditionalOnClass(DataSource.class)  // 类路径下有 DataSource 类才加载
@ConditionalOnMissingBean(DataSource.class)  // 容器中没有 DataSource Bean 才加载
@EnableConfigurationProperties(DataSourceProperties.class)
public class DataSourceAutoConfiguration {

    @Bean
    @ConditionalOnProperty(prefix = "spring.datasource", name = "url")  // 有这个配置才创建
    public DataSource dataSource(DataSourceProperties properties) {
        return createDataSource(properties);
    }
}
```

---

## 5. 自动配置类源码解析

### DataSourceAutoConfiguration

```java
@Configuration(proxyBeanMethods = false)
@ConditionalOnClass({ DataSource.class, EmbeddedDatabaseType.class })
@ConditionalOnMissingBean(type = "javax.sql.DataSource")
@EnableConfigurationProperties(DataSourceProperties.class)
@Import({ DataSourcePoolMetadataProvidersConfiguration.class,
          DataSourceInitializationConfiguration.class })
public class DataSourceAutoConfiguration {

    @Configuration(proxyBeanMethods = false)
    @Conditional(PooledDataSourceCondition.class)
    @ConditionalOnMissingBean(DataSource.class)
    @Import({ DataSourceConfiguration.Hikari.class,
              DataSourceConfiguration.Tomcat.class,
              DataSourceConfiguration.Dbcp2.class,
              DataSourceConfiguration.OracleUcp.class,
              DataSourceConfiguration.Generic.class })
    protected static class PooledDataSourceConfiguration {

    }

    @Configuration(proxyBeanMethods = false)
    @Conditional(EmbeddedDatabaseCondition.class)
    @ConditionalOnMissingBean(DataSource.class)
    protected static class EmbeddedDatabaseConfiguration {

        @Bean
        public DataSource dataSource(DataSourceProperties properties) {
            return new EmbeddedDatabaseBuilder()
                .setType(EmbeddedDatabaseType.H2)
                .build();
        }
    }
}
```

### WebMvcAutoConfiguration

```java
@Configuration(proxyBeanMethods = false)
@ConditionalOnWebApplication(type = Type.SERVLET)
@ConditionalOnClass({ Servlet.class, DispatcherServlet.class, WebMvcConfigurer.class })
@ConditionalOnMissingBean(WebMvcConfigurationSupport.class)
@AutoConfigureOrder(Ordered.HIGHEST_PRECEDENCE + 10)
@ImportRuntimeHints(WebResourcesRuntimeHints.class)
public class WebMvcAutoConfiguration {

    @Bean
    public RequestMappingHandlerMapping requestMappingHandlerMapping(
            RequestMappingHandlerMapping mvcContentNegotiationManager,
            FormattingConversionService mvcConversionService,
            ResourceUrlProvider mvcResourceUrlProvider) {
        // 创建 RequestMappingHandlerMapping
        return mapping;
    }

    @Bean
    public RequestMappingHandlerAdapter requestMappingHandlerAdapter(
            RequestMappingHandlerMapping mvcContentNegotiationManager,
            FormattingConversionService mvcConversionService,
            Validator mvcValidator) {
        // 创建 RequestMappingHandlerAdapter
        return adapter;
    }
}
```

---

## 6. 禁用自动配置

### 方式一：@SpringBootApplication 排除

```java
@SpringBootApplication(exclude = { DataSourceAutoConfiguration.class })
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

### 方式二：配置文件排除

```yaml
spring:
  autoconfigure:
    exclude:
      - org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration
      - org.springframework.boot.autoconfigure.data.redis.RedisAutoConfiguration
```

---

## 7. 自定义自动配置

### 步骤

1. 创建自动配置类
2. 创建配置属性类
3. 注册自动配置

### 示例

```java
// 1. 配置属性类
@ConfigurationProperties(prefix = "myapp")
public class MyAppProperties {
    private String name;
    private int timeout = 3000;
    // getter & setter
}

// 2. 自动配置类
@Configuration
@ConditionalOnClass(MyService.class)
@EnableConfigurationProperties(MyAppProperties.class)
public class MyAppAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean
    public MyService myService(MyAppProperties properties) {
        return new MyService(properties.getName(), properties.getTimeout());
    }
}

// 3. 注册自动配置
// src/main/resources/META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
com.example.autoconfigure.MyAppAutoConfiguration
```

---

## 8. 配置属性类

### @ConfigurationProperties

```java
@Configuration
@ConfigurationProperties(prefix = "spring.datasource")
public class DataSourceProperties {
    private String url;
    private String username;
    private String password;
    private String driverClassName;
    // getter & setter
}
```

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/db
    username: root
    password: 123456
    driver-class-name: com.mysql.cj.jdbc.Driver
```

### @Value vs @ConfigurationProperties

| 特性 | @Value | @ConfigurationProperties |
|------|--------|-------------------------|
| 绑定方式 | 单个属性 | 批量绑定 |
| SpEL 支持 | ✅ | ❌ |
| 类型转换 | 自动 | 自动 |
| 校验 | 不支持 | 支持 JSR303 |
| 松散绑定 | ❌ | ✅（user_name 可绑定 userName） |

```java
// @Value 示例
@Component
public class Config {
    @Value("${app.name}")
    private String name;

    @Value("#{10 * 2}")
    private int value;
}

// @ConfigurationProperties 示例
@Component
@ConfigurationProperties(prefix = "app")
public class Config {
    private String name;
    private int timeout;
    // getter & setter
}
```

---

## 9. Spring Boot 启动流程

```
┌─────────────────────────────────────────────────────────────┐
│              SpringApplication.run()                        │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│           1. 创建 SpringApplication 对象                     │
│              - 推断应用类型（Web/普通）                      │
│              - 加载所有 ApplicationContextInitializer       │
│              - 加载所有 ApplicationListener                 │
│              - 推断主类                                      │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│           2. 执行 run() 方法                                │
│              - 记录启动时间                                  │
│              - 启动监听器                                    │
│              - 准备环境（Environment）                       │
│              - 打印 Banner                                   │
│              - 创建 ApplicationContext                       │
│              - 刷新容器                                      │
│              - 调用 Runner                                   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│         3. 创建 ApplicationContext                          │
│              - 加载 Bean 定义                                │
│              - 刷新容器（createBeans）                        │
│              - 自动配置生效                                  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│              4. 启动完成                                     │
└─────────────────────────────────────────────────────────────┘
```

### 关键代码位置

| 阶段 | 类名 | 方法 |
|------|------|------|
| 创建 SpringApplication | SpringApplication | 构造方法 |
| 准备环境 | SpringApplication | prepareEnvironment() |
| 创建容器 | SpringApplication | createApplicationContext() |
| 刷新容器 | SpringApplication | refreshContext() |
| 自动配置 | AutoConfigurationImportSelector | selectImports() |

---

## 10. 常见面试问题

### Q1: Spring Boot 自动配置原理？

**答案：**
1. `@EnableAutoConfiguration` 导入 `AutoConfigurationImportSelector`
2. 读取 `spring.factories` 文件获取所有自动配置类
3. 通过 `@Conditional` 系列注解按需加载
4. 满足条件的自动配置类创建 Bean

### Q2: 如何禁用某个自动配置？

**答案：**
```java
// 方式一
@SpringBootApplication(exclude = DataSourceAutoConfiguration.class)

// 方式二
spring.autoconfigure.exclude=org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration
```

### Q3: @Conditional 注解有哪些？

**答案：**
`@ConditionalOnClass`、`@ConditionalOnMissingClass`、
`@ConditionalOnBean`、`@ConditionalOnMissingBean`、
`@ConditionalOnProperty`、`@ConditionalOnWebApplication` 等

### Q4: @Value 和 @ConfigurationProperties 区别？

**答案：**
- `@Value`：单个属性绑定，支持 SpEL
- `@ConfigurationProperties`：批量绑定，支持校验和松散绑定

---

## 🎯 本节面试考点总结

| 考点 | 问题 | 关键点 |
|------|------|--------|
| 自动配置 | 自动配置原理？ | EnableAutoConfiguration → AutoConfigurationImportSelector → spring.factories → @Conditional |
| spring.factories | 位置和作用？ | META-INF/spring.factories，存储自动配置类列表 |
| @Conditional | 常用注解？ | OnClass、OnMissingBean、OnProperty、OnWebApplication |
| 禁用自动配置 | 如何禁用？ | exclude 属性或配置文件 |
| 配置绑定 | @Value vs @ConfigurationProperties | 单个 vs 批量 |
| 启动流程 | 启动流程？ | 创建SpringApplication → prepareEnvironment → createApplicationContext → refreshContext |
| 配置属性 | 松散绑定？ | user_name 可绑定 userName |

---

## ✅ 课后练习

1. 查看 DataSourceAutoConfiguration 源码
2. 自定义一个自动配置类
3. 使用 @ConditionalOnProperty 控制配置加载

```java
// 练习要求
// 自定义一个 MailAutoConfiguration
// 条件：
// 1. 类路径下有 JavaMailSender 类
// 2. 配置文件中有 spring.mail.host
// 3. 容器中没有 JavaMailSender Bean

---

## 📝 自测题

1. 自动配置的核心入口注解是？\
   A. @SpringBootApplication  B. @EnableAutoConfiguration  C. @ComponentScan  D. @Import
2. Spring Boot 3.x 中，自动配置类列表存储在？\
   A. spring.factories  B. AutoConfiguration.imports  C. application.yml  D. spring-config.xml
3. 只在类路径下有 DataSource 类时才加载配置，使用哪个注解？\
   A. @ConditionalOnBean  B. @ConditionalOnClass  C. @ConditionalOnProperty  D. @ConditionalOnMissingBean
4. @Value 相比 @ConfigurationProperties 的优势是？\
   A. 批量绑定  B. 支持 JSR303 校验  C. 支持 SpEL 表达式  D. 支持松散绑定

**答案：1-B, 2-B, 3-B, 4-C**

---

下一课：Spring MVC（→ `第五课-SpringMVC.md`）
```