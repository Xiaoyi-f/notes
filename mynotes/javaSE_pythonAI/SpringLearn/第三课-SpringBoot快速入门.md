# Spring 学习笔记 - 第三课：Spring Boot 快速入门

## 1. 什么是 Spring Boot？

**Spring Boot = 简化 Spring 应用开发的框架**

### 为什么需要 Spring Boot？

#### 传统 Spring 开发痛点

```xml
<!-- 传统 Spring 需要配置大量 XML -->
<?xml version="1.0" encoding="UTF-8"?>
<beans xmlns="...">
    <!-- 数据源配置 -->
    <bean id="dataSource" class="...">
        <property name="url" value="jdbc:mysql://localhost:3306/db"/>
        <property name="username" value="root"/>
        <property name="password" value="123456"/>
    </bean>

    <!-- SessionFactory 配置 -->
    <bean id="sessionFactory" class="...">

    <!-- 事务管理器配置 -->
    <bean id="transactionManager" class="...">

    <!-- 各种扫描配置 -->
    <context:component-scan base-package="..."/>
</beans>
```

**问题：**
- 配置文件复杂繁琐
- 依赖管理混乱
- 开发效率低
- 部署复杂

#### Spring Boot 解决方案

```java
// 只需要一个注解！
@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

**优点：**
- 零配置（约定优于配置）
- 开箱即用
- 内嵌服务器
- 简化依赖管理

---

## 2. Spring Boot 核心特性

| 特性 | 说明 |
|------|------|
| **自动配置** | 根据依赖自动配置 Spring |
| **起步依赖** | 简化 Maven/Gradle 配置 |
| **内嵌服务器** | 无需部署 WAR 包 |
| **Actuator** | 提供生产级监控端点 |
| **无需 XML** | 全注解开发 |

---

## 3. 快速创建项目

### 方式一：Spring Initializr（官网）

访问 https://start.spring.io/

选择：
- Project: Maven / Gradle
- Language: Java
- Spring Boot: 最新稳定版
- Dependencies: Spring Web、Spring Data JPA、MySQL Driver 等

点击 Generate 下载项目

### 方式二：IDEA 创建

```
New Project → Spring Initializr → 选择依赖 → 创建
```

### 方式三：命令行创建

```bash
curl https://start.spring.io/starter.zip \
  -d dependencies=web,data-jpa,mysql \
  -d type=maven-project \
  -d language=java \
  -d bootVersion=3.2.0 \
  -d groupId=com.example \
  -d artifactId=springboot-demo \
  -o springboot-demo.zip

unzip springboot-demo.zip
```

---

## 4. 项目结构

```
springboot-demo/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/example/demo/
│   │   │       ├── DemoApplication.java      ← 启动类
│   │   │       ├── controller/               ← 控制器层
│   │   │       │   └── UserController.java
│   │   │       ├── service/                  ← 服务层
│   │   │       │   ├── UserService.java
│   │   │       │   └── impl/
│   │   │       │       └── UserServiceImpl.java
│   │   │       ├── dao/                      ← 数据访问层
│   │   │       │   └── UserRepository.java
│   │   │       ├── entity/                   ← 实体类
│   │   │       │   └── User.java
│   │   │       ├── dto/                      ← 数据传输对象
│   │   │       ├── config/                   ← 配置类
│   │   │       ├── exception/                ← 异常处理
│   │   │       └── util/                     ← 工具类
│   │   └── resources/
│   │       ├── application.yml              ← 配置文件
│   │       ├── application-dev.yml          ← 开发环境配置
│   │       ├── application-prod.yml         ← 生产环境配置
│   │       ├── application-test.yml         ← 测试环境配置
│   │       ├── static/                       ← 静态资源
│   │       ├── templates/                    ← 模板文件
│   │       └── logback-spring.xml           ← 日志配置
│   └── test/                                 ← 测试代码
├── pom.xml                                    ← Maven 配置
└── README.md
```

---

## 5. 核心注解详解

### @SpringBootApplication

这是一个组合注解，包含三个核心注解：

```java
@SpringBootConfiguration  // 标识为配置类（等同 @Configuration）
@EnableAutoConfiguration  // 启用自动配置
@ComponentScan           // 组件扫描
```

**等同于：**
```java
@Configuration
@EnableAutoConfiguration
@ComponentScan
public class Application {}
```

### 启动类示例

```java
@SpringBootApplication
public class DemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }
}
```

---

## 6. 配置文件

### application.yml（推荐）

```yaml
# 服务器配置
server:
  port: 8080
  servlet:
    context-path: /api

# 应用名称
spring:
  application:
    name: demo

  # 数据源配置
  datasource:
    url: jdbc:mysql://localhost:3306/demo?useUnicode=true&characterEncoding=utf8
    username: root
    password: 123456
    driver-class-name: com.mysql.cj.jdbc.Driver

  # JPA 配置
  jpa:
    hibernate:
      ddl-auto: update
    show-sql: true
    database-platform: org.hibernate.dialect.MySQL8Dialect

# 日志配置
logging:
  level:
    root: info
    com.example.demo: debug
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n"
```

### application.properties

```properties
server.port=8080
spring.application.name=demo
spring.datasource.url=jdbc:mysql://localhost:3306/demo
spring.datasource.username=root
spring.datasource.password=123456
```

**对比：**
| 特性 | yml | properties |
|------|-----|------------|
| 层级结构 | 清晰（推荐） | 扁平 |
| 重复前缀 | 不需要 | 需要 |
| 注释支持 | ✅ | ✅ |

---

## 7. 常用配置

### 多环境配置

```yaml
# application.yml
spring:
  profiles:
    active: dev  # 激活 dev 环境

---
# application-dev.yml
server:
  port: 8080

---
# application-prod.yml
server:
  port: 80
```

### 自定义配置

```yaml
# application.yml
app:
  name: 我的系统
  version: 1.0.0
  author: 张三
  features:
    - feature1
    - feature2
```

```java
@Component
@ConfigurationProperties(prefix = "app")
public class AppConfig {
    private String name;
    private String version;
    private String author;
    private List<String> features;

    // getter & setter
}
```

```java
@RestController
public class ConfigController {
    @Autowired
    private AppConfig appConfig;

    @GetMapping("/config")
    public Map<String, Object> getConfig() {
        Map<String, Object> map = new HashMap<>();
        map.put("name", appConfig.getName());
        map.put("version", appConfig.getVersion());
        return map;
    }
}
```

### 配置优先级（从高到低）

| 优先级 | 位置 |
|--------|------|
| 1 | 命令行参数 |
| 2 | `SPRING_APPLICATION_JSON` 环境变量 |
| 3 | JNDI 属性 |
| 4 | Java 系统属性 |
| 5 | 操作系统环境变量 |
| 6 | jar 包外部的 `application-{profile}.properties` |
| 7 | jar 包内部的 `application-{profile}.properties` |
| 8 | jar 包外部的 `application.properties` |
| 9 | jar 包内部的 `application.properties` |
| 10 | @PropertySource 注解 |
| 11 | 默认属性 |

---

## 8. 第一个 Hello World

### Controller 层

```java
@RestController
@RequestMapping("/api")
public class HelloController {

    @GetMapping("/hello")
    public String hello() {
        return "Hello, Spring Boot!";
    }

    @GetMapping("/hello/{name}")
    public Map<String, String> hello(@PathVariable String name) {
        Map<String, String> result = new HashMap<>();
        result.put("message", "Hello, " + name + "!");
        return result;
    }
}
```

### 启动访问

```
启动后访问：http://localhost:8080/api/hello
```

---

## 9. RESTful API 开发

### 常用注解

| 注解 | 说明 |
|------|------|
| `@RestController` | 组合注解：@Controller + @ResponseBody |
| `@RequestMapping` | 请求映射（通用） |
| `@GetMapping` | GET 请求 |
| `@PostMapping` | POST 请求 |
| `@PutMapping` | PUT 请求 |
| `@DeleteMapping` | DELETE 请求 |
| `@PathVariable` | 路径变量 |
| `@RequestParam` | 请求参数 |
| `@RequestBody` | 请求体 |
| `@RequestHeader` | 请求头 |

### 完整 CRUD 示例

```java
@RestController
@RequestMapping("/api/users")
public class UserController {

    @Autowired
    private UserService userService;

    // 查询所有
    @GetMapping
    public List<User> findAll() {
        return userService.findAll();
    }

    // 根据 ID 查询
    @GetMapping("/{id}")
    public User findById(@PathVariable Long id) {
        return userService.findById(id);
    }

    // 分页查询
    @GetMapping
    public Page<User> findByPage(
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "10") int size) {
        return userService.findByPage(page, size);
    }

    // 新增
    @PostMapping
    public User save(@RequestBody User user) {
        return userService.save(user);
    }

    // 更新
    @PutMapping("/{id}")
    public User update(@PathVariable Long id, @RequestBody User user) {
        return userService.update(id, user);
    }

    // 删除
    @DeleteMapping("/{id}")
    public void delete(@PathVariable Long id) {
        userService.delete(id);
    }
}
```

---

## 10. 常用起步依赖（Starter）

| Starter | 说明 |
|---------|------|
| `spring-boot-starter-web` | Web 开发（包含 Spring MVC、Tomcat） |
| `spring-boot-starter-data-jpa` | JPA 数据访问 |
| `spring-boot-starter-data-redis` | Redis |
| `spring-boot-starter-security` | 安全认证 |
| `spring-boot-starter-validation` | 参数校验 |
| `spring-boot-starter-aop` | AOP 支持 |
| `spring-boot-starter-test` | 测试 |
| `spring-boot-starter-actuator` | 监控端点 |

### pom.xml 示例

```xml
<dependencies>
    <!-- Web -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>

    <!-- JPA -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-jpa</artifactId>
    </dependency>

    <!-- MySQL -->
    <dependency>
        <groupId>com.mysql</groupId>
        <artifactId>mysql-connector-j</artifactId>
        <scope>runtime</scope>
    </dependency>

    <!-- Lombok -->
    <dependency>
        <groupId>org.projectlombok</groupId>
        <artifactId>lombok</artifactId>
        <optional>true</optional>
    </dependency>

    <!-- 测试 -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-test</artifactId>
        <scope>test</scope>
    </dependency>
</dependencies>
```

---

## 11. 热部署

### 添加依赖

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-devtools</artifactId>
    <scope>runtime</scope>
    <optional>true</optional>
</dependency>
```

### IDEA 设置

```
1. Settings → Build → Compiler → 勾选 "Build project automatically"
2. 按 Ctrl + Shift + Alt + / → Registry → 勾选 "compiler.automake.allow.when.app.running"
```

---

## 🎯 本节面试考点总结

| 考点 | 问题 | 关键点 |
|------|------|--------|
| Spring Boot | 什么是 Spring Boot？ | 简化 Spring 开发的框架，约定优于配置 |
| 优势 | Spring Boot 优势？ | 零配置、开箱即用、内嵌服务器、简化依赖 |
| @SpringBootApplication | 这个注解包含什么？ | @Configuration + @EnableAutoConfiguration + @ComponentScan |
| 自动配置 | 自动配置原理？ | 根据类路径下的依赖自动配置 Bean |
| 配置优先级 | 配置优先级顺序？ | 命令行 > 环境变量 > 外部配置文件 > 内部配置文件 |
| 启动器 | 什么是 Starter？ | 简化依赖管理的起步依赖 |

---

## ✅ 课后练习

1. 创建一个 Spring Boot 项目
2. 实现一个完整的用户 CRUD 接口
3. 配置多环境（dev/test/prod）
4. 实现热部署

```java
// 练习要求
// 项目名：springboot-hello
// 功能：用户管理 CRUD
// 接口：
// - GET    /api/users        查询所有
// - GET    /api/users/{id}   根据ID查询
// - POST   /api/users        新增用户
// - PUT    /api/users/{id}   更新用户
// - DELETE /api/users/{id}   删除用户

---

## 📝 自测题

1. @SpringBootApplication 不包含以下哪个注解？\
   A. @Configuration  B. @EnableAutoConfiguration  C. @ComponentScan  D. @EnableTransactionManagement
2. yml 相比 properties 的主要优势是？\
   A. 执行速度更快  B. 支持层级结构  C. 兼容性更好  D. 安全性更高
3. ddl-auto 在哪个配置项下？\
   A. spring.datasource  B. spring.jpa.hibernate  C. server.servlet  D. spring.autoconfigure
4. Spring Boot 配置优先级最高的是？\
   A. 命令行参数  B. 环境变量  C. 外部 application.yml  D. 内部 application.yml

**答案：1-D, 2-B, 3-B, 4-A**

---

下一课：自动配置原理（→ `第四课-SpringBoot自动配置原理.md`）
```