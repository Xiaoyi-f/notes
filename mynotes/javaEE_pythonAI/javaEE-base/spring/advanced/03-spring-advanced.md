# Spring 框架高级特性

## 一、概述

深入 Spring 框架核心：Bean 生命周期源码、事务传播机制深度解析、事件驱动架构、BeanFactoryPostProcessor 与扩展点。

## 二、Bean 生命周期

### 完整生命周期图

```
加载 Bean 定义 → 合并 BeanDefinition → 实例化（构造方法）
    → 属性填充（依赖注入）
    → Aware 接口回调（BeanNameAware, BeanFactoryAware, ApplicationContextAware）
    → BeanPostProcessor#postProcessBeforeInitialization
    → @PostConstruct / InitializingBean#afterPropertiesSet / init-method
    → BeanPostProcessor#postProcessAfterInitialization
    → 就绪状态
    → @PreDestroy / DisposableBean#destroy / destroy-method
```

### 源码级关键代码

```java
// AbstractAutowireCapableBeanFactory 核心方法
protected Object doCreateBean(String beanName, RootBeanDefinition mbd, Object[] args) {
    // 1. 实例化
    BeanWrapper instanceWrapper = createBeanInstance(beanName, mbd, args);
    
    // 2. 属性填充
    populateBean(beanName, mbd, instanceWrapper);
    
    // 3. 初始化
    exposedObject = initializeBean(beanName, exposedObject, mbd);
    return exposedObject;
}

protected Object initializeBean(String beanName, Object bean, RootBeanDefinition mbd) {
    // 3.1 Aware 回调
    invokeAwareMethods(beanName, bean);

    // 3.2 Before 初始化
    Object wrappedBean = applyBeanPostProcessorsBeforeInitialization(bean, beanName);
    
    // 3.3 初始化方法
    invokeInitMethods(beanName, wrappedBean, mbd);
    
    // 3.4 After 初始化
    wrappedBean = applyBeanPostProcessorsAfterInitialization(wrappedBean, beanName);
    return wrappedBean;
}
```

### 自定义扩展点

```java
@Component
public class MyBeanPostProcessor implements BeanPostProcessor {
    @Override
    public Object postProcessBeforeInitialization(Object bean, String beanName) {
        if (bean instanceof InitializingBean) {
            log.info("Before init: {}", beanName);
        }
        // 返回代理对象可以实现 AOP
        return bean;
    }

    @Override
    public Object postProcessAfterInitialization(Object bean, String beanName) {
        if (bean instanceof MyService) {
            log.info("After init: {}", beanName);
        }
        return bean;
    }
}

// 修改 Bean 定义
@Component
public class MyBeanFactoryPostProcessor implements BeanFactoryPostProcessor {
    @Override
    public void postProcessBeanFactory(ConfigurableListableBeanFactory beanFactory) {
        BeanDefinition bd = beanFactory.getBeanDefinition("myDataSource");
        MutablePropertyValues pv = bd.getPropertyValues();
        // 动态修改连接池参数
        if (pv.contains("maxActive")) {
            pv.add("maxActive", 50);
        }
    }
}
```

## 三、事务传播机制

### 7 种传播行为

| 传播行为 | 说明 | 适用场景 |
|----------|------|----------|
| REQUIRED (默认) | 加入当前事务，没有则新建 | 通用业务方法 |
| REQUIRES_NEW | 挂起当前，新建独立事务 | 操作日志、审计 |
| NESTED | 嵌套事务（JDBC 保存点） | 批量处理中某步失败回滚部分 |
| SUPPORTS | 有则加入，无则不用事务 | 查询方法 |
| NOT_SUPPORTED | 挂起当前，非事务执行 | 发送通知 |
| MANDATORY | 必须有事务，否则异常 | 内部调用 |
| NEVER | 不能有事务，否则异常 | 测试/清理 |

### 事务陷阱实战

```java
@Service
public class OrderService {
    @Autowired
    private OrderService self;  // 自注入解决 this 调用问题

    // 陷阱1：内部方法调用导致事务失效
    public void createOrder(OrderDTO dto) {
        // this.saveOrder(dto);  // ❌ 事务不生效（this 是原始对象）
        self.saveOrder(dto);      // ✅ 自注入，走代理
    }

    @Transactional(rollbackFor = Exception.class)
    public void saveOrder(OrderDTO dto) {
        orderDao.insert(dto);
        inventoryService.deduct(dto.getProductId(), dto.getQuantity());
    }

    // 陷阱2：try-catch 吞掉异常
    @Transactional
    public void processPayment(Long orderId) {
        try {
            paymentService.pay(orderId);
        } catch (Exception e) {
            log.error("Payment failed", e);
            // ❌ 异常被捕获，不会回滚
            throw new RuntimeException(e);  // ✅ 必须抛出
        }
    }

    // 陷阱3：事务传播 REQUIRES_NEW 正确用法
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void saveAuditLog(AuditLog log) {
        // 即使主事务回滚，审计日志也要保留
        auditDao.insert(log);
    }
}

// 事务边界错误场景排查
@Transactional
public void batchProcess(List<Order> orders) {
    for (int i = 0; i < orders.size(); i++) {
        try {
            processOne(orders.get(i));  // 每个订单独立事务
        } catch (Exception e) {
            log.error("Order {} failed", orders.get(i).getId(), e);
            // 继续处理下一个
        }
    }
}
```

## 四、事件驱动

### 自定义事件

```java
// 事件
public class OrderCreatedEvent extends ApplicationEvent {
    private final OrderDTO order;

    public OrderCreatedEvent(Object source, OrderDTO order) {
        super(source);
        this.order = order;
    }
    public OrderDTO getOrder() { return order; }
}

// 发布事件
@Service
public class OrderService {
    @Autowired
    private ApplicationEventPublisher publisher;

    @Transactional
    public void createOrder(OrderDTO order) {
        orderDao.insert(order);
        // 事务提交后再发布事件（避免事件处理时查不到数据）
        TransactionSynchronizationManager.registerSynchronization(
            new TransactionSynchronization() {
                @Override
                public void afterCommit() {
                    publisher.publishEvent(new OrderCreatedEvent(this, order));
                }
            }
        );
    }
}

// 监听事件（异步处理）
@Component
public class OrderEventListener {
    @Async
    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void handleOrderCreated(OrderCreatedEvent event) {
        // 发送短信
        smsService.send(event.getOrder().getUserId(), "订单已创建");
        // 更新库存
        inventoryService.lock(event.getOrder().getProductId());
    }
}

// 配置异步事件支持
@Configuration
@EnableAsync
public class AsyncConfig implements AsyncConfigurer {
    @Override
    public Executor getAsyncExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(5);
        executor.setMaxPoolSize(20);
        executor.setQueueCapacity(100);
        executor.setThreadNamePrefix("event-");
        executor.initialize();
        return executor;
    }
}
```

## 五、@Transactional 底层原理

```
@Transactional 标注方法
    → TransactionInterceptor 拦截
    → 获取事务属性（传播、隔离级别等）
    → PlatformTransactionManager.getTransaction()
        → DataSourceTransactionManager.doBegin()
            → connection.setAutoCommit(false)
            → connection.setTransactionIsolation(level)
    → 执行业务方法
    → 成功: connection.commit()
    → 异常: connection.rollback()
    → 恢复: connection.setAutoCommit(true)
```

## 课后练习

1. 实现一个 @RetryOnFailure 注解，在指定异常时自动重试
2. 分析 Spring 循环依赖的解决方案（三级缓存），画出流程图
3. 实现一个自定义 Scope（如 RefreshScope），支持 Bean 动态刷新
4. 实现事务传播的 NESTED 行为演示用例

## 自测题

1. Spring 解决构造器循环依赖的方式？ A) 三级缓存 B) 延迟加载 C) @Lazy 注解 D) 无法解决
2. REQUIRES_NEW 传播行为在遇到嵌套调用时？ A) 复用外层事务 B) 挂起外层新建事务 C) 报错 D) 不使用事务
3. TransactionSynchronizationManager.registerSynchronization 用于？ A) 开启事务 B) 注册事务同步回调 C) 提交事务 D) 回滚事务

**答案：** 1-D（构造器循环依赖无法解决，Setter 注入用三级缓存）, 2-B, 3-B
