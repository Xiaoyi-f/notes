# Spring 学习笔记 - 第二课：AOP（面向切面编程）

## 1. 什么是 AOP？

**AOP = Aspect Oriented Programming（面向切面编程）**

### 核心思想
AOP 是一种编程思想，通过**预编译**和**运行期动态代理**实现程序功能的统一维护。

### 为什么要用 AOP？

**问题场景：**
```java
public class UserService {
    public void save() {
        // 记录日志
        System.out.println("开始保存用户");

        // 权限检查
        checkPermission();

        // 事务管理
        beginTransaction();

        // 业务逻辑
        userDao.save();

        // 提交事务
        commitTransaction();

        // 记录日志
        System.out.println("保存用户完成");
    }

    public void delete() {
        // 重复的代码...
        System.out.println("开始删除用户");
        checkPermission();
        beginTransaction();
        userDao.delete();
        commitTransaction();
        System.out.println("删除用户完成");
    }
}
```

**问题：**
- 大量重复代码（日志、权限、事务）
- 业务逻辑混杂，难以维护
- 修改一处要改多处

**AOP 解决方案：**
```java
// 业务代码保持纯净
public class UserService {
    public void save() {
        userDao.save();  // 只写核心业务逻辑
    }

    public void delete() {
        userDao.delete();
    }
}

// 通用功能通过 AOP 统一处理
@Aspect
@Component
public class LogAspect {
    @Before("execution(* com.example.service.*.*(..))")
    public void logBefore() {
        System.out.println("方法开始执行");
    }
}
```

---

## 2. AOP 核心概念（必背）

### 概念对比表

| 概念 | 英文 | 解释 |
|------|------|------|
| **切面** | Aspect | 横切关注点的模块化（如日志、事务） |
| **连接点** | JoinPoint | 程序执行的某个特定位置（方法调用、异常抛出） |
| **切入点** | Pointcut | 匹配连接点的表达式（在哪些方法上生效） |
| **通知** | Advice | 在切入点执行的操作（前置、后置、环绕等） |
| **目标对象** | Target Object | 被代理的对象 |
| **代理** | Proxy | AOP 框架创建的对象 |
| **织入** | Weaving | 将切面应用到目标对象并创建代理的过程 |

### 图示理解

```
┌─────────────────────────────────────────────────────┐
│                   切面（Aspect）                      │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐              │
│  │  日志   │  │ 事务管理 │  │ 权限检查 │              │
│  └─────────┘  └─────────┘  └─────────┘              │
└─────────────────────────────────────────────────────┘
                        ↓ 织入（Weaving）
┌─────────────────────────────────────────────────────┐
│              目标对象（Target Object）                │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐              │
│  │save()   │  │delete() │  │update() │              │
│  └─────────┘  └─────────┘  └─────────┘              │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│                   代理对象（Proxy）                    │
│  (被增强后的目标对象，包含切面逻辑)                     │
└─────────────────────────────────────────────────────┘
```

---

## 3. 通知类型（Advice）

| 类型 | 注解 | 执行时机 | 使用场景 |
|------|------|----------|----------|
| **前置通知** | `@Before` | 目标方法执行前 | 参数校验、权限检查 |
| **后置通知** | `@After` | 目标方法执行后（无论成功失败） | 释放资源、清理工作 |
| **返回通知** | `@AfterReturning` | 目标方法成功返回后 | 记录返回值、结果处理 |
| **异常通知** | `@AfterThrowing` | 目标方法抛出异常后 | 异常日志、告警 |
| **环绕通知** | `@Around` | 目标方法执行前后 | 性能监控、事务控制 |

### 执行顺序

```
┌──────────────────────────────────────────────────────────┐
│                    @Before                                │  ← 前置通知
├──────────────────────────────────────────────────────────┤
│                    @Around                                │  ← 环绕通知前半部分
│                  ┌──────────┐                            │
│                  │ 目标方法  │                            │  ← 执行目标方法
│                  └──────────┘                            │
│                    @Around                                │  ← 环绕通知后半部分
├──────────────────────────────────────────────────────────┤
│  成功返回: @AfterReturning     失败: @AfterThrowing       │  ← 返回/异常通知
├──────────────────────────────────────────────────────────┤
│                    @After                                 │  ← 后置通知（总是执行）
└──────────────────────────────────────────────────────────┘
```

---

## 4. 切入点表达式（Pointcut Expression）

### 基本语法

```
execution(访问修饰符 返回值类型 包名.类名.方法名(参数) 异常类型)
```

### 常用表达式示例

| 表达式 | 说明 |
|--------|------|
| `execution(* com.example.service.*.*(..))` | service 包下所有类的所有方法 |
| `execution(public * *(..))` | 所有 public 方法 |
| `execution(* *.*(..))` | 所有方法 |
| `execution(* com.example.service.UserService.*(..))` | UserService 类的所有方法 |
| `execution(* com.example.service.UserService.save(..))` | UserService 的 save 方法 |
| `execution(* com.example..*(..))` | com.example 包及其子包的所有方法 |
| `execution(* save*(..))` | 所有以 save 开头的方法 |
| `execution(* *(String, ..))` | 第一个参数是 String 的方法 |
| `execution(* *(..)) throws IOException` | 抛出 IOException 的方法 |

### 特殊字符

| 符号 | 含义 |
|------|------|
| `*` | 匹配任意数量的字符（除 . 外） |
| `..` | 匹配任意数量的字符（包括 .） |
| `+` | 匹配指定类及其子类 |

---

## 5. 实战代码示例

### 5.1 添加依赖

```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-aop</artifactId>
</dependency>
```

### 5.2 创建切面

```java
@Aspect
@Component
public class LogAspect {

    // 定义切入点：service 包下所有方法
    @Pointcut("execution(* com.example.service.*.*(..))")
    public void servicePointcut() {}

    // 前置通知
    @Before("servicePointcut()")
    public void before(JoinPoint joinPoint) {
        String methodName = joinPoint.getSignature().getName();
        Object[] args = joinPoint.getArgs();
        System.out.println("前置通知：执行方法 " + methodName + "，参数：" + Arrays.toString(args));
    }

    // 后置通知
    @After("servicePointcut()")
    public void after(JoinPoint joinPoint) {
        String methodName = joinPoint.getSignature().getName();
        System.out.println("后置通知：方法 " + methodName + " 执行完成");
    }

    // 返回通知
    @AfterReturning(pointcut = "servicePointcut()", returning = "result")
    public void afterReturning(JoinPoint joinPoint, Object result) {
        String methodName = joinPoint.getSignature().getName();
        System.out.println("返回通知：方法 " + methodName + " 返回值：" + result);
    }

    // 异常通知
    @AfterThrowing(pointcut = "servicePointcut()", throwing = "ex")
    public void afterThrowing(JoinPoint joinPoint, Exception ex) {
        String methodName = joinPoint.getSignature().getName();
        System.out.println("异常通知：方法 " + methodName + " 抛出异常：" + ex.getMessage());
    }

    // 环绕通知
    @Around("servicePointcut()")
    public Object around(ProceedingJoinPoint joinPoint) throws Throwable {
        String methodName = joinPoint.getSignature().getName();
        long startTime = System.currentTimeMillis();

        System.out.println("环绕通知：方法 " + methodName + " 开始执行");

        try {
            // 执行目标方法
            Object result = joinPoint.proceed();
            long endTime = System.currentTimeMillis();
            System.out.println("环绕通知：方法 " + methodName + " 执行耗时：" + (endTime - startTime) + "ms");
            return result;
        } catch (Exception e) {
            System.out.println("环绕通知：方法 " + methodName + " 执行异常");
            throw e;
        }
    }
}
```

### 5.3 自定义注解 + AOP

```java
// 1. 自定义注解
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface Log {
    String value() default "";
}

// 2. 使用注解
@Service
public class UserService {

    @Log("保存用户")
    public void save(User user) {
        userDao.save(user);
    }
}

// 3. 切面匹配注解
@Aspect
@Component
public class LogAspect {

    @Around("@annotation(log)")  // 匹配带 @Log 注解的方法
    public Object around(ProceedingJoinPoint joinPoint, Log log) throws Throwable {
        String description = log.value();
        System.out.println("执行操作：" + description);
        return joinPoint.proceed();
    }
}
```

---

## 6. AOP 实现原理（面试必考）

### 6.1 两种代理方式

| 方式 | 实现技术 | 适用场景 |
|------|----------|----------|
| **JDK 动态代理** | Java 反射 | 目标类实现了接口 |
| **CGLIB 代理** | 字节码增强 | 目标类未实现接口 |

### 6.2 JDK 动态代理原理

```java
// 简化版原理
public class JDKProxy implements InvocationHandler {
    private Object target;

    public Object getProxy() {
        // 创建代理对象
        return Proxy.newProxyInstance(
            target.getClass().getClassLoader(),
            target.getClass().getInterfaces(),
            this
        );
    }

    @Override
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        // 前置逻辑
        System.out.println("方法执行前");

        // 调用目标方法
        Object result = method.invoke(target, args);

        // 后置逻辑
        System.out.println("方法执行后");

        return result;
    }
}
```

**特点：**
- 只能代理实现了接口的类
- 生成的代理类是接口的实现类
- 性能相对较好

### 6.3 CGLIB 代理原理

```java
// CGLIB 通过继承目标类创建子类，重写方法
public class CGLIBProxy implements MethodInterceptor {
    private Object target;

    public Object getProxy() {
        // 创建代理对象（目标类的子类）
        Enhancer enhancer = new Enhancer();
        enhancer.setSuperclass(target.getClass());
        enhancer.setCallback(this);
        return enhancer.create();
    }

    @Override
    public Object intercept(Object obj, Method method, Object[] args, MethodProxy proxy) throws Throwable {
        // 前置逻辑
        System.out.println("方法执行前");

        // 调用目标方法
        Object result = proxy.invokeSuper(obj, args);

        // 后置逻辑
        System.out.println("方法执行后");

        return result;
    }
}
```

**特点：**
- 可以代理没有实现接口的类
- 生成的代理类是目标类的子类
- 无法代理 final 修饰的方法
- Spring Boot 2.x 默认使用 CGLIB

### 6.4 Spring AOP vs AspectJ

| 特性 | Spring AOP | AspectJ |
|------|------------|---------|
| 实现方式 | 运行期动态代理 | 编译期/类加载期织入 |
| 性能 | 较低（运行时反射） | 较高（编译时织入） |
| 功能 | 仅支持方法级别 | 支持字段、构造器等 |
| 复杂度 | 简单 | 复杂 |
| 使用场景 | 大多数场景 | 需要高性能或细粒度控制 |

---

## 7. 常见应用场景

| 场景 | 切面类型 | 通知类型 |
|------|----------|----------|
| 日志记录 | 日志切面 | @Around / @Before / @After |
| 权限控制 | 权限切面 | @Before |
| 事务管理 | 事务切面 | @Around |
| 性能监控 | 性能切面 | @Around |
| 异常处理 | 异常切面 | @AfterThrowing |
| 缓存处理 | 缓存切面 | @Around / @AfterReturning |

---

## 🎯 本节面试考点总结

| 考点 | 问题 | 关键点 |
|------|------|--------|
| AOP | 什么是 AOP？ | 面向切面编程，解决横切关注点问题 |
| 核心概念 | AOP 的核心概念有哪些？ | 切面、连接点、切入点、通知、目标对象、代理、织入 |
| 通知类型 | 有哪些通知类型？ | Before、After、AfterReturning、AfterThrowing、Around |
| 执行顺序 | 通知的执行顺序？ | Around(前) → Before → 方法 → Around(后) → AfterReturning/AfterThrowing → After |
| 切入点 | 常用切入点表达式？ | `execution(* com.example..*(..))` |
| 实现原理 | Spring AOP 实现原理？ | JDK 动态代理（有接口）、CGLIB（无接口） |
| 代理区别 | JDK 动态代理 vs CGLIB？ | JDK 用接口，CGLIB 用继承 |
| Spring AOP vs AspectJ | 区别？ | Spring AOP 运行时动态代理，AspectJ 编译时织入 |

---

## ✅ 课后练习

1. 创建一个日志切面，记录所有 service 方法执行时间
2. 使用自定义注解实现权限检查
3. 实现一个缓存切面（先查缓存，没有则执行方法并缓存结果）

```java
// 练习项目结构
SpringLearn/
├── aspect/
│   ├── LogAspect.java          // 日志切面
│   ├── CacheAspect.java        // 缓存切面
│   └── PermissionAspect.java   // 权限切面
├── annotation/
│   ├── Log.java
│   ├── Cacheable.java
│   └── RequirePermission.java
└── service/
    └── UserService.java

---

## 📝 自测题

1. AOP 中，"切面"对应的英文是？\
   A. JoinPoint  B. Pointcut  C. Aspect  D. Advice
2. 目标方法执行前后都会执行的通知类型是？\
   A. @Before  B. @After  C. @AfterReturning  D. @Around
3. Spring Boot 2.x 默认使用的 AOP 代理方式是？\
   A. JDK 动态代理  B. CGLIB 代理  C. AspectJ 编译时织入
4. 切入点表达式 `execution(* com.example.service.*.*(..))` 中第一个 `*` 表示？\
   A. 任意包名  B. 任意返回值类型  C. 任意类名  D. 任意方法名

**答案：1-C, 2-D, 3-B, 4-B**

---

下一课：Spring Boot 快速入门（→ `第三课-SpringBoot快速入门.md`）
```