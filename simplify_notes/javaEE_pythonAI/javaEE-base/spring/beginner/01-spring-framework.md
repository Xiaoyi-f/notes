# Spring Framework 基础

## 一、Spring 概述

Spring 是一个开源的轻量级 Java 开发框架，最初由 Rod Johnson 创建。

### Spring 核心特性

```text
┌─────────────────────────────────────────┐
│          Spring Framework               │
├─────────────────────────────────────────┤
│  Spring Web (MVC/WebFlux)               │
├─────────────────────────────────────────┤
│  Spring AOP                             │
├─────────────────────────────────────────┤
│  Spring Context (IoC 容器)              │
├─────────────────────────────────────────┤
│  Spring Core (Beans, Core, Context, SpEL)│
└─────────────────────────────────────────┘

核心概念:
1. IoC (Inversion of Control) - 控制反转
2. DI (Dependency Injection) - 依赖注入
3. AOP (Aspect-Oriented Programming) - 面向切面编程
```

## 二、IoC 和 DI

### 1. 依赖注入基础

```java
// 不使用 Spring（手动创建依赖）
public class UserServiceManual {
    private UserDao userDao;

    public UserServiceManual() {
        // 手动创建依赖
        this.userDao = new UserDao();
    }

    public void addUser(String username) {
        userDao.save(username);
    }
}

// 使用 Spring（依赖注入）
public class UserService {
    private final UserDao userDao;

    // 构造器注入（推荐）
    @Autowired
    public UserService(UserDao userDao) {
        this.userDao = userDao;
    }

    // Setter 注入
    /*
    @Autowired
    public void setUserDao(UserDao userDao) {
        this.userDao = userDao;
    }
    */

    // 字段注入（不推荐）
    /*
    @Autowired
    private UserDao userDao;
    */

    public void addUser(String username) {
        userDao.save(username);
    }
}

// DAO 接口
public interface UserDao {
    void save(String username);
}

// DAO 实现
@Repository
public class UserDaoImpl implements UserDao {
    @Override
    public void save(String username) {
        System.out.println("保存用户: " + username);
    }
}
```

### 2. Spring 配置方式

#### XML 配置方式

```xml
<!-- beans.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<beans xmlns="http://www.springframework.org/schema/beans"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xmlns:context="http://www.springframework.org/schema/context"
       xsi:schemaLocation="
           http://www.springframework.org/schema/beans
           http://www.springframework.org/schema/beans/spring-beans.xsd
           http://www.springframework.org/schema/context
           http://www.springframework.org/schema/context/spring-context.xsd">

    <!-- 启用注解扫描 -->
    <context:component-scan base-package="com.example"/>

    <!-- 手动注册 Bean -->
    <bean id="userDao" class="com.example.dao.UserDaoImpl"/>

    <bean id="userService" class="com.example.service.UserService">
        <constructor-arg ref="userDao"/>
    </bean>

</beans>
```

```java
// 使用 XML 配置
import org.springframework.context.support.ClassPathXmlApplicationContext;

public class SpringXmlDemo {
    public static void main(String[] args) {
        ApplicationContext context =
            new ClassPathXmlApplicationContext("beans.xml");

        UserService userService = context.getBean(UserService.class);
        userService.addUser("张三");
    }
}
```

#### 注解配置方式（推荐）

```java
// 主配置类
@Configuration
@ComponentScan(basePackages = "com.example")
public class AppConfig {
    // 可以在这里定义额外的 Bean
    @Bean
    public DataSource dataSource() {
        HikariDataSource dataSource = new HikariDataSource();
        dataSource.setJdbcUrl("jdbc:mysql://localhost:3306/db");
        dataSource.setUsername("root");
        dataSource.setPassword("password");
        return dataSource;
    }
}

// 使用注解配置
import org.springframework.context.annotation.AnnotationConfigApplicationContext;

public class SpringAnnotationDemo {
    public static void main(String[] args) {
        ApplicationContext context =
            new AnnotationConfigApplicationContext(AppConfig.class);

        UserService userService = context.getBean(UserService.class);
        userService.addUser("张三");
    }
}
```

## 三、Bean 的生命周期

```java
import org.springframework.beans.factory.DisposableBean;
import org.springframework.beans.factory.InitializingBean;
import org.springframework.context.annotation.*;
import javax.annotation.PostConstruct;
import javax.annotation.PreDestroy;

// 定义 Bean
@Component
public class LifecycleBean implements InitializingBean, DisposableBean {

    // 1. 构造器
    public LifecycleBean() {
        System.out.println("1. 构造器执行");
    }

    // 2. @PostConstruct（推荐）
    @PostConstruct
    public void postConstruct() {
        System.out.println("2. @PostConstruct 执行");
    }

    // 3. InitializingBean 接口
    @Override
    public void afterPropertiesSet() {
        System.out.println("3. afterPropertiesSet 执行");
    }

    // 4. @Bean 的 initMethod
    public void customInit() {
        System.out.println("4. customInit 执行");
    }

    // Bean 使用中...

    // 销毁阶段
    @PreDestroy
    public void preDestroy() {
        System.out.println("5. @PreDestroy 执行");
    }

    @Override
    public void destroy() {
        System.out.println("6. destroy 执行");
    }

    public void customDestroy() {
        System.out.println("7. customDestroy 执行");
    }
}

// 配置类
@Configuration
public class LifecycleConfig {
    @Bean(initMethod = "customInit", destroyMethod = "customDestroy")
    public LifecycleBean lifecycleBean() {
        return new LifecycleBean();
    }
}

// 测试
public class LifecycleDemo {
    public static void main(String[] args) {
        // 使用 ConfigurableApplicationContext 才能触发销毁
        ConfigurableApplicationContext context =
            new AnnotationConfigApplicationContext(LifecycleConfig.class);

        LifecycleBean bean = context.getBean(LifecycleBean.class);

        // 关闭容器触发销毁
        context.close();
    }
}
```

## 四、Bean 的作用域

```java
import org.springframework.beans.factory.config.BeanDefinition;
import org.springframework.context.annotation.*;

// 单例（默认）
@Component
@Scope(BeanDefinition.SCOPE_SINGLETON)
public class SingletonBean {
    public SingletonBean() {
        System.out.println("SingletonBean 构造器");
    }
}

// 原型（每次获取创建新实例）
@Component
@Scope(BeanDefinition.SCOPE_PROTOTYPE)
public class PrototypeBean {
    public PrototypeBean() {
        System.out.println("PrototypeBean 构造器");
    }
}

// 请求作用域（Web 环境）
@Component
@Scope(WebApplicationContext.SCOPE_REQUEST)
@RefreshScope
public class RequestBean {
    // 每个 HTTP 请求创建一个新实例
}

// 会话作用域（Web 环境）
@Component
@Scope(WebApplicationContext.SCOPE_SESSION)
public class SessionBean {
    // 每个 HTTP Session 创建一个新实例
}

// 应用作用域
@Component
@Scope(WebApplicationContext.SCOPE_APPLICATION)
public class ApplicationBean {
    // 整个 Web 应用共享一个实例
}

// 测试不同作用域
@Configuration
@ComponentScan(basePackages = "com.example")
public class ScopeConfig {}

public class ScopeDemo {
    public static void main(String[] args) {
        ApplicationContext context =
            new AnnotationConfigApplicationContext(ScopeConfig.class);

        // 单例：只创建一次
        SingletonBean singleton1 = context.getBean(SingletonBean.class);
        SingletonBean singleton2 = context.getBean(SingletonBean.class);
        System.out.println("单例是否相同: " + (singleton1 == singleton2));

        // 原型：每次创建新实例
        PrototypeBean prototype1 = context.getBean(PrototypeBean.class);
        PrototypeBean prototype2 = context.getBean(PrototypeBean.class);
        System.out.println("原型是否相同: " + (prototype1 == prototype2));
    }
}
```

## 五、依赖注入详解

### 1. 构造器注入（推荐）

```java
@Service
public class OrderService {
    private final UserService userService;
    private final ProductService productService;
    private final PaymentService paymentService;

    // 构造器注入 - 所有依赖在构造时确定，便于测试
    @Autowired
    public OrderService(
        UserService userService,
        ProductService productService,
        PaymentService paymentService
    ) {
        this.userService = userService;
        this.productService = productService;
        this.paymentService = paymentService;
    }

    // Spring 4.3+ 如果只有一个构造器，@Autowired 可以省略
    // Lombok 可以简化为:
    // @RequiredArgsConstructor
    // private final UserService userService;
}
```

### 2. Setter 注入

```java
@Service
public class EmailService {
    private JavaMailSender mailSender;
    private String fromAddress;

    // Setter 注入 - 适合可选依赖
    @Autowired
    public void setMailSender(JavaMailSender mailSender) {
        this.mailSender = mailSender;
    }

    @Autowired
    public void setFromAddress(@Value("${mail.from}") String fromAddress) {
        this.fromAddress = fromAddress;
    }
}
```

### 3. 注入集合

```java
@Service
public class PluginService {
    private List<Plugin> plugins;
    private Map<String, Plugin> pluginMap;

    // 注入 List
    @Autowired
    public void setPlugins(List<Plugin> plugins) {
        this.plugins = plugins;
        System.out.println("已加载 " + plugins.size() + " 个插件");
    }

    // 注入 Map（key 为 Bean 名称）
    @Autowired
    public void setPluginMap(Map<String, Plugin> pluginMap) {
        this.pluginMap = pluginMap;
        pluginMap.forEach((name, plugin) ->
            System.out.println("插件: " + name)
        );
    }

    // 使用 @Order 或 @Priority 排序
    @Component
    @Order(1)
    public class PluginA implements Plugin {}

    @Component
    @Order(2)
    public class PluginB implements Plugin {}
}
```

### 4. 条件注入

```java
// 使用 @Conditional
@Component
@Conditional(WindowsCondition.class)
public class WindowsService {}

@Component
@Conditional(LinuxCondition.class)
public class LinuxService {}

// 自定义条件
public class WindowsCondition implements Condition {
    @Override
    public boolean matches(ConditionContext context, AnnotatedTypeMetadata metadata) {
        return context.getEnvironment().getProperty("os.name")
            .contains("Windows");
    }
}

// 使用 @ConditionalOnProperty（Spring Boot）
@Component
@ConditionalOnProperty(name = "feature.enabled", havingValue = "true")
public class FeatureService {}

// 使用 @Profile
@Component
@Profile("dev")
public class DevDatabaseConfig {}

@Component
@Profile("prod")
public class ProdDatabaseConfig {}
```

## 六、配置属性

```java
import org.springframework.beans.factory.annotation.*;
import org.springframework.boot.context.properties.*;
import org.springframework.stereotype.*;

// 方式1: 使用 @Value
@Component
public class AppProperties {
    @Value("${app.name}")
    private String name;

    @Value("${app.version}")
    private String version;

    @Value("${app.port:8080}")
    private int port;

    @Value("${app.features:feature1,feature2}")
    private String[] features;

    // getters
}

// 方式2: 使用 @ConfigurationProperties（推荐）
@Configuration
@ConfigurationProperties(prefix = "app")
public class AppConfiguration {
    private String name;
    private String version;
    private int port = 8080;
    private Database database;
    private List<Server> servers;

    // getters and setters

    public static class Database {
        private String url;
        private String username;
        private String password;
        private int maxConnections = 10;

        // getters and setters
    }

    public static class Server {
        private String host;
        private int port;

        // getters and setters
    }
}

// 配置文件 (application.yml)
/*
app:
  name: MyApplication
  version: 1.0.0
  port: 8080
  database:
    url: jdbc:mysql://localhost:3306/mydb
    username: root
    password: secret
    max-connections: 20
  servers:
    - host: server1
      port: 8001
    - host: server2
      port: 8002
*/

// 启用配置属性
@EnableConfigurationProperties(AppConfiguration.class)
@SpringBootApplication
public class Application {}
```

## 七、Profile

```java
// 定义 Profile
@Configuration
@Profile("dev")
public class DevConfig {
    @Bean
    public DataSource dataSource() {
        HikariDataSource ds = new HikariDataSource();
        ds.setJdbcUrl("jdbc:mysql://localhost:3306/dev");
        return ds;
    }
}

@Configuration
@Profile("prod")
public class ProdConfig {
    @Bean
    public DataSource dataSource() {
        HikariDataSource ds = new HikariDataSource();
        ds.setJdbcUrl("jdbc:mysql://prod-db:3306/app");
        return ds;
    }
}

// 激活 Profile
// 1. application.properties
// spring.profiles.active=dev

// 2. 启动参数
// java -jar app.jar --spring.profiles.active=prod

// 3. 代码激活
@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        new SpringApplicationBuilder(Application.class)
            .profiles("dev")
            .run(args);
    }
}

// 多 Profile
@Profile({"dev", "test"})  // dev 或 test
public class DevTestConfig {}

@Profile("!prod")  // 非 prod
public class NonProdConfig {}
```

## 八、Spring 事件机制

```java
// 定义事件
public class UserCreatedEvent extends ApplicationEvent {
    private final String username;

    public UserCreatedEvent(Object source, String username) {
        super(source);
        this.username = username;
    }

    public String getUsername() {
        return username;
    }
}

// 事件发布器
@Service
public class UserService {
    private final ApplicationEventPublisher eventPublisher;

    public UserService(ApplicationEventPublisher eventPublisher) {
        this.eventPublisher = eventPublisher;
    }

    public void createUser(String username) {
        // 创建用户逻辑
        System.out.println("创建用户: " + username);

        // 发布事件
        UserCreatedEvent event = new UserCreatedEvent(this, username);
        eventPublisher.publishEvent(event);
    }
}

// 事件监听器（方式1）
@Component
public class EmailNotificationListener {
    @EventListener
    public void handleUserCreated(UserCreatedEvent event) {
        System.out.println("发送欢迎邮件给: " + event.getUsername());
    }
}

// 事件监听器（方式2）
@Component
public class AuditLogListener {
    @EventListener
    public void handleUserCreated(UserCreatedEvent event) {
        System.out.println("记录审计日志: 用户 " + event.getUsername() + " 已创建");
    }
}

// 异步事件监听
@Component
public class AsyncEventListener {
    @EventListener
    @Async
    public void handleAsyncEvent(UserCreatedEvent event) {
        System.out.println("异步处理: " + event.getUsername());
    }
}

// 条件监听
@Component
public class ConditionalListener {
    @EventListener(condition = "#event.username.length() > 5")
    public void handleLongUsername(UserCreatedEvent event) {
        System.out.println("长用户名处理: " + event.getUsername());
    }
}
```

## 九、AOP（面向切面编程）

```java
import org.aspectj.lang.*;
import org.aspectj.lang.annotation.*;
import org.springframework.stereotype.*;

// 定义切面
@Aspect
@Component
public class LoggingAspect {

    // 定义切点
    @Pointcut("execution(* com.example.service.*.*(..))")
    public void serviceLayer() {}

    @Pointcut("@annotation(com.example.annotation.Loggable)")
    public void loggableMethod() {}

    // 前置通知
    @Before("serviceLayer()")
    public void beforeAdvice(JoinPoint joinPoint) {
        System.out.println("Before: " + joinPoint.getSignature().getName());
    }

    // 后置通知
    @After("serviceLayer()")
    public void afterAdvice(JoinPoint joinPoint) {
        System.out.println("After: " + joinPoint.getSignature().getName());
    }

    // 返回通知
    @AfterReturning(pointcut = "serviceLayer()", returning = "result")
    public void afterReturningAdvice(JoinPoint joinPoint, Object result) {
        System.out.println("AfterReturning: " + joinPoint.getSignature().getName()
            + ", Result: " + result);
    }

    // 异常通知
    @AfterThrowing(pointcut = "serviceLayer()", throwing = "exception")
    public void afterThrowingAdvice(JoinPoint joinPoint, Throwable exception) {
        System.out.println("AfterThrowing: " + joinPoint.getSignature().getName()
            + ", Exception: " + exception.getMessage());
    }

    // 环绕通知（最强大）
    @Around("serviceLayer()")
    public Object aroundAdvice(ProceedingJoinPoint joinPoint) throws Throwable {
        long startTime = System.currentTimeMillis();

        System.out.println("Around Before: " + joinPoint.getSignature().getName());

        try {
            // 执行目标方法
            Object result = joinPoint.proceed();

            long endTime = System.currentTimeMillis();
            System.out.println("Around After: " + joinPoint.getSignature().getName()
                + ", 耗时: " + (endTime - startTime) + "ms");

            return result;
        } catch (Exception e) {
            System.out.println("Around Exception: " + e.getMessage());
            throw e;
        }
    }

    // 注解切点
    @Before("@annotation(com.example.annotation.Loggable)")
    public void loggableAdvice(JoinPoint joinPoint) {
        System.out.println("Loggable Method: " + joinPoint.getSignature().getName());
    }
}

// 自定义注解
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface Loggable {}

// 使用
@Service
public class ProductService {
    @Loggable
    public Product findProduct(Long id) {
        // 业务逻辑
        return new Product(id, "Product " + id);
    }

    public void saveProduct(Product product) {
        // 业务逻辑
    }
}
```

## 十、事务管理

```java
import org.springframework.transaction.annotation.*;

// 声明式事务
@Service
public class OrderService {
    private final OrderRepository orderRepository;
    private final PaymentService paymentService;

    public OrderService(OrderRepository orderRepository, PaymentService paymentService) {
        this.orderRepository = orderRepository;
        this.paymentService = paymentService;
    }

    // 基本事务
    @Transactional
    public void createOrder(Order order) {
        orderRepository.save(order);
        paymentService.processPayment(order);
    }

    // 只读事务（查询优化）
    @Transactional(readOnly = true)
    public Order getOrder(Long id) {
        return orderRepository.findById(id);
    }

    // 设置隔离级别
    @Transactional(
        isolation = Isolation.READ_COMMITTED,
        timeout = 30
    )
    public void transfer(Long fromId, Long toId, BigDecimal amount) {
        // 转账逻辑
    }

    // 设置传播行为
    @Transactional(propagation = Propagation.REQUIRED)  // 默认
    public void defaultPropagation() {}

    @Transactional(propagation = Propagation.REQUIRES_NEW)  // 新建事务
    public void newTransaction() {}

    @Transactional(propagation = Propagation.SUPPORTS)  // 支持事务但不强制
    public void supportTransaction() {}

    @Transactional(propagation = Propagation.MANDATORY)  // 必须在事务中
    public void mandatoryTransaction() {}

    @Transactional(propagation = Propagation.NOT_SUPPORTED)  // 不使用事务
    public void notSupportedTransaction() {}

    @Transactional(propagation = Propagation.NEVER)  // 禁止事务
    public void neverTransaction() {}

    @Transactional(propagation = Propagation.NESTED)  // 嵌套事务
    public void nestedTransaction() {}

    // 设置回滚条件
    @Transactional(rollbackFor = {BusinessException.class, SystemException.class})
    public void rollbackForSpecificException() {}

    @Transactional(noRollbackFor = BusinessException.class)
    public void noRollbackForSpecificException() {}

    // 编程式事务
    private final TransactionTemplate transactionTemplate;

    public OrderService(OrderRepository orderRepository,
                        PaymentService paymentService,
                        TransactionTemplate transactionTemplate) {
        this.orderRepository = orderRepository;
        this.paymentService = paymentService;
        this.transactionTemplate = transactionTemplate;
    }

    public void createOrderWithTransaction(Order order) {
        transactionTemplate.execute(status -> {
            try {
                orderRepository.save(order);
                paymentService.processPayment(order);
                return null;
            } catch (Exception e) {
                status.setRollbackOnly();
                throw e;
            }
        });
    }
}

// 事务配置
@Configuration
@EnableTransactionManagement
public class TransactionConfig {
    @Bean
    public PlatformTransactionManager transactionManager(DataSource dataSource) {
        return new DataSourceTransactionManager(dataSource);
    }
}
```

## 小结

本节学习了 Spring Framework 基础：

- **IoC/DI** - 依赖注入的三种方式
- **Bean 管理** - 生命周期、作用域、配置
- **Profile** - 环境配置
- **事件机制** - ApplicationEvent
- **AOP** - 切面编程
- **事务管理** - 声明式和编程式事务

## 实践练习

### 编程题
1. 使用 Spring IoC 容器管理 Bean，分别用 XML 配置、注解配置和 Java Config 三种方式实现依赖注入。
2. 使用 Spring AOP 实现一个方法级别的性能监控切面，记录每个 Service 方法的执行时间，超过阈值时打印警告日志。

### 思考题
1. Spring 的 Bean 作用域有哪些？prototype Bean 中注入 singleton Bean 会有什么问题？如何解决？
2. Spring AOP 和 AspectJ 的区别？什么场景应该选择 AspectJ？

### 自测题
1. IoC 和 DI 分别是什么？它们之间的关系？
2. Spring 中 Bean 的生命周期？
3. `@Autowired` 和 `@Resource` 的区别？

下一步将学习 Spring MVC（→ `spring/intermediate/02-spring-mvc.md`）。