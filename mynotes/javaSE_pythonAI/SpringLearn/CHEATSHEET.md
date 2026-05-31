# Spring 面试速查表

## IoC / DI 核心

### 注入方式对比
| 方式 | 注解 | 推荐度 |
|------|------|--------|
| 构造器注入 | `public Service(Dao dao)` | ⭐⭐⭐ 最推荐 |
| 字段注入 | `@Autowired private Dao dao` | ⭐⭐ 最常用 |
| Setter 注入 | `@Autowired public void setDao()` | ⭐ 少用 |

### Bean 作用域
| 作用域 | 说明 |
|--------|------|
| singleton | 默认，容器中唯一实例 |
| prototype | 每次获取新建实例 |
| request | 每个 HTTP 请求一个 |
| session | 每个 Session 一个 |

### Bean 生命周期
```
构造器 → @Autowired → @PostConstruct → 使用 → @PreDestroy → 销毁
```

## AOP 速查

### 通知类型执行顺序
```
@Around(前) → @Before → 目标方法 → @Around(后) → @AfterReturning/@AfterThrowing → @After
```

### 切入点表达式
```
execution(* com.example.service.*.*(..))
         ↑                      ↑ ↑  ↑
      返回值              包.类 方法 参数(..任意)
```

### 两种代理方式
| 方式 | 条件 | Spring Boot 默认 |
|------|------|-----------------|
| JDK 动态代理 | 有接口 | ❌ |
| CGLIB 代理 | 无接口(继承) | ✅ (2.x 起) |

## Spring Boot

### @SpringBootApplication = 三个注解
```
@SpringBootConfiguration  ← @Configuration
@EnableAutoConfiguration  ← 自动配置核心
@ComponentScan            ← 组件扫描
```

### 自动配置原理
```
@EnableAutoConfiguration → AutoConfigurationImportSelector
  → 读取 spring.factories / AutoConfiguration.imports
    → @Conditional 条件过滤 → 按需加载配置类
```

### 配置优先级 (高→低)
```
命令行 > 环境变量 > 外部 application-{profile}.yml > 内部 application.yml
```

### @Conditional 系列
| 注解 | 条件 |
|------|------|
| `@ConditionalOnClass` | 类存在 |
| `@ConditionalOnMissingBean` | Bean 不存在 |
| `@ConditionalOnProperty` | 配置属性匹配 |
| `@ConditionalOnWebApplication` | Web 应用 |

## Spring MVC

### 请求处理流程
```
DispatcherServlet → HandlerMapping(找Controller)
  → HandlerAdapter(执行) → Controller(业务)
    → ViewResolver(解析) → View(渲染) → 响应
```

### 参数绑定注解
| 注解 | 来源 | 示例 |
|------|------|------|
| `@PathVariable` | URL 路径 | `/users/{id}` |
| `@RequestParam` | 查询参数 | `?page=1` |
| `@RequestBody` | 请求体 JSON | `{"name":"张三"}` |
| `@RequestHeader` | 请求头 | Authorization |
| `@CookieValue` | Cookie | sessionId |

### 全局异常处理
```java
@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(Exception.class)
    public ResponseEntity<?> handle(Exception e) { ... }
}
```

## Spring Data JPA

### 核心注解
| 注解 | 作用 |
|------|------|
| `@Entity` | 实体类 |
| `@Table` | 表名映射 |
| `@Id` + `@GeneratedValue` | 主键自增 |
| `@Column` | 列映射 |
| `@OneToMany` / `@ManyToOne` | 关联映射 |

### 方法命名查询规则
```
findBy + 字段名 + [And/Or/Between/Like/OrderBy] + ...
```
示例：`findByUsernameAndAgeGreaterThan(String name, Integer age)`

### 事务传播行为
| 行为 | 说明 |
|------|------|
| REQUIRED (默认) | 有则加入，无则创建 |
| REQUIRES_NEW | 新建事务，挂起当前 |
| NESTED | 嵌套事务(savepoint) |

### @Transactional 失效 5 场景
1. 方法非 public
2. 类内部调用(不经过代理)
3. 异常被 catch 未抛出
4. 方法不在 Spring 管理的 Bean 中
5. 数据库引擎不支持事务(MyISAM)

## Spring Security

### 认证授权核心
```
认证(Authentication)：你是谁 → 登录
授权(Authorization)：你能做什么 → 权限
```

### JWT 结构
```
Header.Payload.Signature
eyJhbGc... .eyJzdWI... .SflKxw...
{算法类型}  {用户数据}   {签名验证}
```

### JWT vs Session
| | JWT | Session |
|------|-----|---------|
| 存储位置 | 客户端 | 服务器 |
| 服务器压力 | 低 | 高 |
| 分布式友好 | ✅ | ❌ |
| 令牌撤销 | 困难 | 容易 |

### 安全注解
```java
@PreAuthorize("hasRole('ADMIN')")          // 方法前检查角色
@PreAuthorize("hasAuthority('user:write')") // 方法前检查权限
@PostAuthorize("returnObject.owner == authentication.name") // 方法后检查
```

## 设计模式在 Spring 中的应用

| 模式 | Spring 中使用 |
|------|-------------|
| 工厂模式 | BeanFactory |
| 单例模式 | Bean 默认作用域 |
| 代理模式 | AOP |
| 模板方法 | JdbcTemplate, RestTemplate |
| 观察者模式 | ApplicationEvent |

## 面试高频 10 问

1. **IoC 和 DI 区别？** IoC 是思想(控制反转)，DI 是实现(依赖注入)
2. **AOP 原理？** JDK 动态代理(有接口) / CGLIB 代理(无接口)
3. **Bean 生命周期？** 实例化→注入→初始化(@PostConstruct)→销毁(@PreDestroy)
4. **Spring Boot 自动配置？** EnableAutoConfiguration → imports 文件 → @Conditional 按需加载
5. **@Transactional 失效原因？** 非 public、内部调用、捕获异常、非 Spring Bean
6. **Spring MVC 流程？** DispatcherServlet → HandlerMapping → Controller → ViewResolver → View
7. **Spring 如何解决循环依赖？** 三级缓存(仅 singleton + setter 注入)
8. **JWT 认证流程？** 登录→签发 Token→请求带 Token→过滤器验证→设置 SecurityContext
9. **@Autowired vs @Resource？** @Autowired byType, @Resource byName; 来源不同(Spring/JSR)
10. **事务隔离级别？** READ_UNCOMMITTED → READ_COMMITTED → REPEATABLE_READ → SERIALIZABLE
