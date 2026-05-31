# Spring 学习笔记 - 第一课：Spring 核心

## 1. 什么是 IoC？

**IoC = Inversion of Control（控制反转）**

### 传统开发方式 vs IoC 方式

#### 传统开发方式
```java
// 自己创建对象，控制权在自己手里
public class UserService {
    private UserDao userDao = new UserDao();  // 自己new

    public void save() {
        userDao.save();
    }
}
```

#### IoC 方式
```java
// 对象交给容器管理，控制权反转给 Spring
public class UserService {
    @Autowired
    private UserDao userDao;  // 容器注入

    public void save() {
        userDao.save();
    }
}
```

### 对比表

| 对比项 | 传统方式 | IoC 方式 |
|--------|----------|----------|
| 对象创建 | 自己 `new` | Spring 容器创建 |
| 对象管理 | 自己管理 | Spring 容器管理 |
| 耦合度 | 高（强耦合） | 低（松耦合） |
| 测试 | 难 | 容易 |

---

## 2. 什么是 DI？

**DI = Dependency Injection（依赖注入）**

DI 是 IoC 的实现方式。Spring 容器**主动**将依赖对象注入到需要的地方。

### 三种注入方式

#### 1. 字段注入（最常用，但不推荐用于需要测试的场景）
```java
@Component
public class UserService {
    @Autowired
    private UserDao userDao;
}
```

#### 2. 构造器注入（推荐，最安全）
```java
@Component
public class UserService {
    private final UserDao userDao;

    public UserService(UserDao userDao) {
        this.userDao = userDao;
    }
}
```

#### 3. Setter 注入（较少用）
```java
@Component
public class UserService {
    private UserDao userDao;

    @Autowired
    public void setUserDao(UserDao userDao) {
        this.userDao = userDao;
    }
}
```

---

## 3. Spring 容器

Spring 容器是 IoC 的核心，负责管理所有 Bean 的生命周期。

```java
// 启动 Spring 容器
ApplicationContext context = new AnnotationConfigApplicationContext(AppConfig.class);

// 获取 Bean
UserService userService = context.getBean(UserService.class);

// 使用
userService.save();
```

---

## 4. 常用注解（必背）

| 注解 | 作用 | 使用位置 |
|------|------|----------|
| `@Component` | 标识为 Spring Bean | 类 |
| `@Service` | 标识 Service 层组件 | 类 |
| `@Repository` | 标识 DAO 层组件 | 类 |
| `@Controller` | 标识 Controller 层组件 | 类 |
| `@Autowired` | 自动装配依赖 | 字段/构造器/方法 |
| `@Configuration` | 标识配置类 | 类 |
| `@Bean` | 注册 Bean 到容器 | 方法 |

### 示例代码
```java
@Configuration
public class AppConfig {

    @Bean
    public UserService userService(UserDao userDao) {
        return new UserService(userDao);
    }
}

@Service
public class UserService {
    @Autowired
    private UserDao userDao;
}

@Repository
public class UserDao {
    public void save() {
        // 数据库操作
    }
}
```

---

## 5. Bean 的作用域（面试常考）

| 作用域 | 说明 | 使用场景 |
|--------|------|----------|
| `singleton`（默认） | 容器中只有一个实例 | 无状态对象 |
| `prototype` | 每次获取都创建新实例 | 有状态对象 |
| `request` | 每个 HTTP 请求一个实例 | Web 应用 |
| `session` | 每个 HTTP Session 一个实例 | Web 应用 |

```java
@Service
@Scope("prototype")  // 每次获取都创建新实例
public class UserService {
}
```

---

## 6. Bean 的生命周期（高频考点）

```
实例化 → 属性赋值 → 初始化 → 使用 → 销毁
   ↓           ↓         ↓       ↓      ↓
构造器    @Autowired  @PostConstruct  @PreDestroy
```

### 生命周期示例代码
```java
@Component
public class UserService {

    // 1. 构造器
    public UserService() {
        System.out.println("1. 实例化");
    }

    // 2. 属性注入
    @Autowired
    private UserDao userDao;

    // 3. 初始化
    @PostConstruct
    public void init() {
        System.out.println("3. 初始化");
    }

    // 4. 销毁
    @PreDestroy
    public void destroy() {
        System.out.println("5. 销毁");
    }
}
```

---

## 🎯 本节面试考点总结

| 考点 | 问题 | 关键点 |
|------|------|--------|
| IoC | 什么是 IoC？ | 控制反转，将对象创建权交给容器 |
| DI | 什么是 DI？ | 依赖注入，IoC 的实现方式 |
| 区别 | IoC 和 DI 的关系？ | IoC 是思想，DI 是实现 |
| 注入方式 | 有哪些注入方式？ | 字段、构造器、Setter |
| 作用域 | Bean 的作用域有哪些？ | singleton、prototype、request、session |
| 生命周期 | Bean 的生命周期？ | 实例化→属性赋值→初始化→使用→销毁 |

---

## ✅ 课后练习

目标：实现一个简单的 Spring 应用

要求：
1. 创建 UserService 和 UserDao
2. 使用依赖注入
3. 测试能否正常调用

项目结构：
```
SpringLearn/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/
│   │   │       └── springlearn/
│   │   │           ├── SpringLearnApplication.java
│   │   │           ├── service/
│   │   │           │   └── UserService.java
│   │   │           └── dao/
│   │   │               └── UserDao.java
│   │   └── resources/
└── pom.xml

---

## 📝 自测题

1. 以下哪个不是 Spring 的依赖注入方式？\
   A. 字段注入  B. 构造器注入  C. 静态方法注入  D. Setter 注入
2. Spring Bean 的默认作用域是？\
   A. prototype  B. singleton  C. request  D. session
3. Bean 生命周期的正确顺序是？\
   A. 初始化→实例化→属性赋值→销毁  B. 实例化→属性赋值→初始化→销毁  C. 属性赋值→实例化→初始化→销毁
4. IoC 和 DI 的关系描述正确的是？\
   A. DI 是思想，IoC 是实现  B. IoC 是思想，DI 是实现  C. 二者无关  D. 二者等同

**答案：1-C, 2-B, 3-B, 4-B**

---

下一课：AOP 面向切面编程（→ `第二课-AOP面向切面编程.md`）
```