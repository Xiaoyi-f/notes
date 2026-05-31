# MyBatis 核心源码与插件

## 一、概述

深入 MyBatis 核心机制：SQL 执行流程、插件机制、拦截器实现、MyBatis 与 MyBatis-Plus 集成原理、二级缓存优化。

## 二、MyBatis 执行流程

### 核心流程

```
SqlSessionFactoryBuilder.build()
    → XMLConfigBuilder.parse() 解析配置
    → SqlSessionFactory.openSession()
        → SqlSession.getMapper(UserMapper.class)
            → MapperProxy.invoke()
                → MappedStatement 获取 SQL
                → SqlSession.selectList()
                    → Executor.query()
                        → StatementHandler.prepare()
                        → ParameterHandler.setParameters()
                        → ResultSetHandler.handleResultSets()
                        → 返回结果
```

### 四大核心组件

```java
// 1. Executor - 执行器
// SimpleExecutor: 每次执行创建 Statement
// ReuseExecutor: 复用 Statement（缓存 PreparedStatement）
// BatchExecutor: 批量执行
configuration.setDefaultExecutorType(ExecutorType.BATCH);

// 2. StatementHandler - 语句处理器
public interface StatementHandler {
    Statement prepare(Connection connection, Integer transactionTimeout);
    void parameterize(Statement statement);
    <E> List<E> query(Statement statement, ResultHandler resultHandler);
    int update(Statement statement);
}

// 3. ParameterHandler - 参数处理器
public interface ParameterHandler {
    Object getParameterObject();
    void setParameters(PreparedStatement ps);
}

// 4. ResultSetHandler - 结果处理器
public interface ResultSetHandler {
    <E> List<E> handleResultSets(Statement stmt);
    void handleOutputParameters(CallableStatement cs);
}
```

## 三、拦截器机制

### 可拦截的四种对象

```java
@Intercepts({
    @Signature(type = Executor.class, method = "update",
              args = {MappedStatement.class, Object.class}),
    @Signature(type = Executor.class, method = "query",
              args = {MappedStatement.class, Object.class, RowBounds.class,
                      ResultHandler.class, CacheKey.class, BoundSql.class}),
    @Signature(type = StatementHandler.class, method = "prepare",
              args = {Connection.class, Integer.class}),
    @Signature(type = ParameterHandler.class, method = "setParameters",
              args = {PreparedStatement.class}),
    @Signature(type = ResultSetHandler.class, method = "handleResultSets",
              args = {Statement.class})
})
public class MyBatisInterceptor implements Interceptor {
    @Override
    public Object intercept(Invocation invocation) throws Throwable {
        // 前置处理
        Object target = invocation.getTarget();
        Method method = invocation.getMethod();
        Object[] args = invocation.getArgs();
        
        long start = System.currentTimeMillis();
        try {
            return invocation.proceed();  // 执行原方法
        } finally {
            long cost = System.currentTimeMillis() - start;
            log.info("MyBatis {}.{} cost={}ms",
                target.getClass().getSimpleName(), method.getName(), cost);
        }
    }

    @Override
    public Object plugin(Object target) {
        return Plugin.wrap(target, this);
    }

    @Override
    public void setProperties(Properties properties) {
        // 读取配置参数
    }
}
```

### 慢 SQL 拦截器

```java
@Intercepts(@Signature(type = StatementHandler.class, method = "query",
    args = {Statement.class, ResultHandler.class}))
public class SlowSqlInterceptor implements Interceptor {
    private long slowThresholdMs = 1000;

    @Override
    public Object intercept(Invocation invocation) throws Throwable {
        StatementHandler handler = (StatementHandler) invocation.getTarget();
        String sql = handler.getBoundSql().getSql();
        
        long start = System.currentTimeMillis();
        try {
            return invocation.proceed();
        } finally {
            long cost = System.currentTimeMillis() - start;
            if (cost > slowThresholdMs) {
                log.warn("Slow SQL detected ({}ms): {}", cost, formatSql(sql));
                // 发送告警
                alertService.sendSlowSqlAlert(sql, cost);
            }
        }
    }

    private String formatSql(String sql) {
        return sql.replaceAll("\\s+", " ").trim();
    }

    @Override
    public void setProperties(Properties properties) {
        this.slowThresholdMs = Long.parseLong(
            properties.getProperty("slowThresholdMs", "1000"));
    }
}
```

### 数据脱敏拦截器

```java
@Intercepts(@Signature(type = ResultSetHandler.class, method = "handleResultSets",
    args = {Statement.class}))
public class DataMaskInterceptor implements Interceptor {
    @Override
    public Object intercept(Invocation invocation) throws Throwable {
        Object result = invocation.proceed();
        if (result instanceof List) {
            for (Object item : (List<?>) result) {
                maskFields(item);
            }
        }
        return result;
    }

    private void maskFields(Object obj) {
        if (obj == null) return;
        for (Field field : obj.getClass().getDeclaredFields()) {
            DataMask mask = field.getAnnotation(DataMask.class);
            if (mask != null) {
                field.setAccessible(true);
                try {
                    String value = (String) field.get(obj);
                    if (value != null) {
                        field.set(obj, maskValue(value, mask.type()));
                    }
                } catch (IllegalAccessException e) {
                    log.error("Data mask failed", e);
                }
            }
        }
    }

    private String maskValue(String value, MaskType type) {
        switch (type) {
            case PHONE:    return value.replaceAll("(\\d{3})\\d{4}(\\d{4})", "$1****$2");
            case ID_CARD:  return value.replaceAll("(\\d{6})\\d{8}(\\d{4})", "$1********$2");
            case EMAIL:    return value.replaceAll("(\\w{3}).*(@.*)", "$1***$2");
            case NAME:     return value.replaceAll("(.{1}).*", "$1*");
            default:       return value;
        }
    }
}

@Target(ElementType.FIELD)
@Retention(RetentionPolicy.RUNTIME)
public @interface DataMask {
    MaskType type();
}

public enum MaskType {
    PHONE, ID_CARD, EMAIL, NAME, ADDRESS
}
```

## 四、二级缓存

### 缓存层级

```
一级缓存（SqlSession 级别）
    ↓ 查询时优先查
二级缓存（Namespace/Mapper 级别）
    ↓ 跨 SqlSession 共享
自定义缓存（Redis）
```

### 自定义 Redis 二级缓存

```java
public class RedisCache implements Cache {
    private final String id;
    private RedisTemplate<String, Object> redisTemplate;

    public RedisCache(String id) {
        this.id = id;
    }

    @Override
    public String getId() { return id; }

    @Override
    public void putObject(Object key, Object value) {
        getRedisTemplate().opsForValue()
            .set(getKey(key), value, 1, TimeUnit.HOURS);
    }

    @Override
    public Object getObject(Object key) {
        return getRedisTemplate().opsForValue().get(getKey(key));
    }

    @Override
    public Object removeObject(Object key) {
        Object value = getObject(key);
        getRedisTemplate().delete(getKey(key));
        return value;
    }

    @Override
    public void clear() {
        getRedisTemplate().delete(keys());
    }

    @Override
    public int getSize() {
        return keys().size();
    }

    private String getKey(Object key) {
        return "mybatis:cache:" + id + ":" + key;
    }

    private RedisTemplate<String, Object> getRedisTemplate() {
        if (redisTemplate == null) {
            redisTemplate = (RedisTemplate<String, Object>)
                SpringContextHolder.getBean("redisTemplate");
        }
        return redisTemplate;
    }
}

// Mapper 中启用二级缓存
@CacheNamespace(implementation = RedisCache.class, eviction = FifoCache.class)
public interface UserMapper extends BaseMapper<User> {
}
```

## 面试考点

1. **MyBatis 一级缓存和二级缓存区别？** 一级缓存 SqlSession 级别，默认开启；二级缓存 Mapper 级别，需手动开启
2. **插件如何拦截 SQL 执行？** 通过 JDK 动态代理拦截四大接口（Executor, StatementHandler, ParameterHandler, ResultSetHandler）
3. **PageHelper 分页原理？** 拦截 StatementHandler 的 prepare 方法，改写 SQL 添加 limit
4. **MyBatis 中 `#{}` 和 `${}` 的区别？** `#{}` 预编译（防止 SQL 注入），`${}` 直接拼接（有注入风险）

## 课后练习

1. 实现一个 @EncryptField 注解 + 拦截器实现字段自动加解密
2. 实现分库分表拦截器（按月份自动路由到不同表）
3. 实现 MyBatis 的 SQL 审计日志插件
4. 分析 Mapper 接口是如何通过 JDK 动态代理生成实现类的

## 自测题

1. MyBatis 的插件可以拦截以下哪个对象？ A) DataSource B) Transaction C) StatementHandler D) Configuration
2. MyBatis 中 `#{}` 和 `${}` 哪个可能导致 SQL 注入？ A) #{} B) ${} C) 两者都会 D) 两者都不会
3. MyBatis 二级缓存默认的淘汰策略是？ A) LRU B) FIFO C) LFU D) 软引用

**答案：** 1-C, 2-B, 3-A
