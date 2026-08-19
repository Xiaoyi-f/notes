# Spring 学习笔记 - 第六课：Spring Data JPA

## 1. 什么是 JPA？

**JPA = Java Persistence API（Java 持久化 API）**

JPA 是 Java EE 标准的一套 ORM（对象关系映射）规范。

### 为什么需要 JPA？

**传统 JDBC 问题：**
```java
// 繁琐的 SQL 编写
String sql = "SELECT id, name, age FROM users WHERE name = ?";
PreparedStatement stmt = connection.prepareStatement(sql);
stmt.setString(1, "zhangsan");
ResultSet rs = stmt.executeQuery();

// 手动映射结果集
List<User> users = new ArrayList<>();
while (rs.next()) {
    User user = new User();
    user.setId(rs.getLong("id"));
    user.setName(rs.getString("name"));
    user.setAge(rs.getInt("age"));
    users.add(user);
}
```

**JPA 解决方案：**
```java
// 面向对象，无需写 SQL
List<User> users = userRepository.findByName("zhangsan");
```

### ORM 框架对比

| 特性 | JPA | MyBatis |
|------|-----|---------|
| 开发效率 | 高（自动生成 SQL） | 中（手动写 SQL） |
| 学习成本 | 中 | 低 |
| 性能 | 中（缓存优化） | 高（手写 SQL） |
| 灵活性 | 中（复杂 SQL 困难） | 高（完全控制 SQL） |
| 数据库无关 | 是（自动适配） | 否（SQL 差异） |

---

## 2. Spring Data JPA 核心概念

### 核心接口

```
Repository (标记接口)
    ↓
CrudRepository (CRUD 操作)
    ↓
PagingAndSortingRepository (分页排序)
    ↓
JpaRepository (JPA 扩展)
```

### 接口说明

| 接口 | 方法 |
|------|------|
| `Repository` | 标记接口，无方法 |
| `CrudRepository` | save、findAll、findById、delete 等 |
| `PagingAndSortingRepository` | findAll(Pageable)、findAll(Sort) |
| `JpaRepository` | 批量操作、刷新、flush 等 |

---

## 3. 快速开始

### 添加依赖

```xml
<dependencies>
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
</dependencies>
```

### 配置文件

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/demo?useUnicode=true&characterEncoding=utf8&useSSL=false&serverTimezone=Asia/Shanghai
    username: root
    password: 123456
    driver-class-name: com.mysql.cj.jdbc.Driver

  jpa:
    hibernate:
      ddl-auto: update  # 自动更新表结构
    show-sql: true      # 显示 SQL
    database-platform: org.hibernate.dialect.MySQL8Dialect
    properties:
      hibernate:
        format_sql: true  # 格式化 SQL
```

### ddl-auto 选项

| 选项 | 说明 | 使用场景 |
|------|------|----------|
| `none` | 不做任何操作 | 生产环境 |
| `validate` | 验证表结构 | 验证环境 |
| `update` | 自动更新表结构 | 开发环境 |
| `create` | 每次启动创建表 | 测试环境 |
| `create-drop` | 启动创建，关闭删除 | 测试环境 |

---

## 4. 实体类映射

### 基本注解

```java
@Entity              // 标识为实体类
@Table(name = "users")  // 指定表名
@Data
public class User {

    @Id                     // 主键
    @GeneratedValue(strategy = GenerationType.IDENTITY)  // 自增
    private Long id;

    @Column(name = "username", nullable = false, length = 50, unique = true)
    private String username;

    @Column(name = "password", nullable = false, length = 100)
    private String password;

    @Column(name = "email", length = 100)
    private String email;

    @Column(name = "age")
    private Integer age;

    @Column(name = "create_time", updatable = false)
    @CreationTimestamp
    private LocalDateTime createTime;

    @Column(name = "update_time")
    @UpdateTimestamp
    private LocalDateTime updateTime;

    @Transient  // 不映射到数据库
    private String tempField;
}
```

### 主键策略

| 策略 | 说明 |
|------|------|
| `GenerationType.IDENTITY` | 数据库自增 |
| `GenerationType.SEQUENCE` | 数据库序列 |
| `GenerationType.TABLE` | 数据库表模拟序列 |
| `GenerationType.AUTO` | 自动选择 |
| `GenerationType.UUID` | UUID（需自定义） |

---

## 5. 关联映射

### 一对多（One-to-Many）

```java
@Entity
@Data
public class Department {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;

    @OneToMany(mappedBy = "department", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<Employee> employees;
}

@Entity
@Data
public class Employee {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "department_id")
    private Department department;
}
```

### 多对多（Many-to-Many）

```java
@Entity
@Data
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String username;

    @ManyToMany(cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    @JoinTable(
        name = "user_role",
        joinColumns = @JoinColumn(name = "user_id"),
        inverseJoinColumns = @JoinColumn(name = "role_id")
    )
    private Set<Role> roles = new HashSet<>();
}

@Entity
@Data
public class Role {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;

    @ManyToMany(mappedBy = "roles")
    private Set<User> users = new HashSet<>();
}
```

### 一对一（One-to-One）

```java
@Entity
@Data
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String username;

    @OneToOne(cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    @JoinColumn(name = "profile_id")
    private UserProfile profile;
}

@Entity
@Data
public class UserProfile {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String nickname;

    private String avatar;

    @OneToOne(mappedBy = "profile")
    private User user;
}
```

### 级联操作（Cascade）

| 类型 | 说明 |
|------|------|
| `CascadeType.PERSIST` | 级联保存 |
| `CascadeType.MERGE` | 级联更新 |
| `CascadeType.REMOVE` | 级联删除 |
| `CascadeType.REFRESH` | 级联刷新 |
| `CascadeType.DETACH` | 级联分离 |
| `CascadeType.ALL` | 全部 |

### 加载方式（Fetch）

| 类型 | 说明 |
|------|------|
| `FetchType.LAZY` | 延迟加载（推荐） |
| `FetchType.EAGER` | 立即加载 |

---

## 6. Repository 接口

### 基础 CRUD

```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    // JpaRepository 自带方法
    // save() / saveAll()
    // findById() / findAll() / findAllById()
    // count() / existsById()
    // delete() / deleteById() / deleteAll()
}
```

### 方法命名查询

```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    // 根据用户名查询
    User findByUsername(String username);

    // 根据用户名和年龄查询
    User findByUsernameAndAge(String username, Integer age);

    // 查询年龄大于指定值
    List<User> findByAgeGreaterThan(Integer age);

    // 查询年龄在范围内
    List<User> findByAgeBetween(Integer min, Integer max);

    // 模糊查询
    List<User> findByUsernameLike(String username);

    // 查询指定用户名列表
    List<User> findByUsernameIn(List<String> usernames);

    // 排序查询
    List<User> findByAgeOrderByCreateTimeDesc(Integer age);

    // 统计
    Long countByAgeGreaterThan(Integer age);

    // 判断存在
    boolean existsByUsername(String username);
}
```

### 方法命名规则

| 关键字 | 示例 | SQL |
|--------|------|-----|
| `findBy` | `findByUsername` | WHERE username = ? |
| `And` | `findByUsernameAndAge` | WHERE username = ? AND age = ? |
| `Or` | `findByUsernameOrEmail` | WHERE username = ? OR email = ? |
| `Between` | `findByAgeBetween` | WHERE age BETWEEN ? AND ? |
| `LessThan` | `findByAgeLessThan` | WHERE age < ? |
| `GreaterThan` | `findByAgeGreaterThan` | WHERE age > ? |
| `Like` | `findByUsernameLike` | WHERE username LIKE ? |
| `In` | `findByUsernameIn` | WHERE username IN (?) |
| `OrderBy` | `findByAgeOrderByCreateTimeDesc` | WHERE age = ? ORDER BY create_time DESC |
| `Not` | `findByUsernameNot` | WHERE username != ? |

---

## 7. @Query 注解

### JPQL 查询

```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    @Query("SELECT u FROM User u WHERE u.username = ?1")
    User findByUsername(String username);

    @Query("SELECT u FROM User u WHERE u.username = :username AND u.age = :age")
    User findByUsernameAndAge(@Param("username") String username, @Param("age") Integer age);

    @Query("SELECT u FROM User u WHERE u.age > :min AND u.age < :max")
    List<User> findByAgeRange(@Param("min") Integer min, @Param("max") Integer max);

    @Query("SELECT COUNT(u) FROM User u WHERE u.age > :age")
    Long countByAgeGreaterThan(@Param("age") Integer age);

    @Query("SELECT new com.example.dto.UserDto(u.id, u.username, u.email) FROM User u")
    List<UserDto> findAllUserDto();
}
```

### 原生 SQL 查询

```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    @Query(value = "SELECT * FROM users WHERE username = ?1", nativeQuery = true)
    User findByUsername(String username);

    @Query(value = "SELECT COUNT(*) FROM users", nativeQuery = true)
    Long countUsers();
}
```

### 修改操作

```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    @Modifying
    @Query("UPDATE User u SET u.age = :age WHERE u.id = :id")
    int updateAgeById(@Param("id") Long id, @Param("age") Integer age);

    @Modifying
    @Query("DELETE FROM User u WHERE u.age < :age")
    int deleteByAgeLessThan(@Param("age") Integer age);
}
```

> 注意：使用 `@Modifying` 的方法需要在 Service 层加 `@Transactional`

---

## 8. 分页和排序

### 分页查询

```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    Page<User> findByAge(Integer age, Pageable pageable);

    Page<User> findByAgeGreaterThan(Integer age, Pageable pageable);
}
```

```java
@Service
public class UserService {

    @Autowired
    private UserRepository userRepository;

    public Page<User> findByPage(int page, int size) {
        Pageable pageable = PageRequest.of(page, size);
        return userRepository.findAll(pageable);
    }

    public Page<User> findByAgePage(int age, int page, int size) {
        Pageable pageable = PageRequest.of(page, size);
        return userRepository.findByAge(age, pageable);
    }
}
```

### 排序查询

```java
// 基本排序
Sort sort = Sort.by(Sort.Direction.DESC, "createTime");
List<User> users = userRepository.findAll(sort);

// 多字段排序
Sort sort = Sort.by(
    Sort.Order.desc("createTime"),
    Sort.Order.asc("username")
);
List<User> users = userRepository.findAll(sort);

// 分页 + 排序
Pageable pageable = PageRequest.of(0, 10, Sort.by("createTime").descending());
Page<User> users = userRepository.findAll(pageable);
```

### 分页返回信息

```java
Page<User> page = userRepository.findAll(PageRequest.of(0, 10));

// 分页信息
int totalPages = page.getTotalPages();      // 总页数
long totalElements = page.getTotalElements(); // 总记录数
int currentPage = page.getNumber();         // 当前页
int pageSize = page.getSize();              // 每页大小

// 数据
List<User> users = page.getContent();
```

---

## 9. 事务管理

### @Transactional

```java
@Service
public class UserService {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private OrderRepository orderRepository;

    // 添加事务
    @Transactional
    public void createUserWithOrder(User user, Order order) {
        userRepository.save(user);
        orderRepository.save(order);
        // 两个操作要么都成功，要么都回滚
    }

    // 只读事务
    @Transactional(readOnly = true)
    public User findById(Long id) {
        return userRepository.findById(id).orElse(null);
    }

    // 指定事务传播行为
    @Transactional(propagation = Propagation.REQUIRED)
    public void required() {
        // 默认行为，加入当前事务
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void requiresNew() {
        // 创建新事务
    }

    // 指定隔离级别
    @Transactional(isolation = Isolation.READ_COMMITTED)
    public void withIsolation() {
        // READ_COMMITTED 隔离级别
    }

    // 指定回滚异常
    @Transactional(rollbackFor = Exception.class)
    public void rollbackForException() {
        // 所有异常都回滚（默认只回滚 RuntimeException）
    }

    // 不回滚异常
    @Transactional(noRollbackFor = BusinessException.class)
    public void noRollback() {
        // BusinessException 不触发回滚
    }

    // 超时设置
    @Transactional(timeout = 30)
    public void withTimeout() {
        // 30秒超时
    }
}
```

### 事务传播行为（面试常考）

| 类型 | 说明 |
|------|------|
| `REQUIRED`（默认） | 有事务则加入，无则创建 |
| `REQUIRES_NEW` | 创建新事务，挂起当前事务 |
| `SUPPORTS` | 有事务则加入，无则非事务执行 |
| `NOT_SUPPORTED` | 以非事务方式执行，挂起当前事务 |
| `MANDATORY` | 必须在事务中执行，否则抛异常 |
| `NEVER` | 以非事务方式执行，有事务则抛异常 |
| `NESTED` | 嵌套事务 |

### 事务隔离级别

| 级别 | 说明 | 问题 |
|------|------|------|
| `DEFAULT` | 使用数据库默认 | |
| `READ_UNCOMMITTED` | 读未提交 | 脏读、不可重复读、幻读 |
| `READ_COMMITTED` | 读已提交 | 不可重复读、幻读 |
| `REPEATABLE_READ` | 可重复读 | 幻读 |
| `SERIALIZABLE` | 串行化 | 无问题，性能差 |

---

## 10. 审计功能

### 启用审计

```java
@Configuration
@EnableJpaAuditing
public class JpaConfig {
}
```

### 实体类配置

```java
@Entity
@EntityListeners(AuditingEntityListener.class)
@Data
public class BaseEntity {

    @CreatedDate
    @Column(name = "create_time", updatable = false)
    private LocalDateTime createTime;

    @LastModifiedDate
    @Column(name = "update_time")
    private LocalDateTime updateTime;

    @CreatedBy
    @Column(name = "create_by", updatable = false)
    private String createBy;

    @LastModifiedBy
    @Column(name = "update_by")
    private String updateBy;
}

@Entity
@Data
public class User extends BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String username;
}
```

### 配置审计用户

```java
@Component
public class AuditorAwareImpl implements AuditorAware<String> {

    @Override
    public Optional<String> getCurrentAuditor() {
        // 从 SecurityContext 获取当前用户
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return Optional.of("system");
        }
        return Optional.of(authentication.getName());
    }
}
```

---

## 🎯 本节面试考点总结

| 考点 | 问题 | 关键点 |
|------|------|--------|
| JPA | 什么是 JPA？ | Java 持久化 API，ORM 规范 |
| JPA vs MyBatis | 区别？ | JPA 自动生成 SQL，MyBatis 手写 SQL |
| 核心注解 | 实体类注解？ | @Entity、@Table、@Id、@Column、@GeneratedValue |
| 关联映射 | 关联类型？ | @OneToOne、@OneToMany、@ManyToOne、@ManyToMany |
| 级联操作 | CascadeType？ | PERSIST、MERGE、REMOVE、REFRESH、DETACH、ALL |
| 加载方式 | FetchType？ | LAZY（延迟）、EAGER（立即） |
| 方法命名 | 查询规则？ | findByUsername、findByUsernameAndAge |
| @Query | JPQL vs SQL？ | JPQL 面向对象，SQL 原生查询 |
| 分页 | Pageable？ | PageRequest.of(page, size) |
| 事务 | @Transactional？ | propagation、isolation、rollbackFor |
| 传播行为 | 常用传播？ | REQUIRED、REQUIRES_NEW |
| 审计 | 审计功能？ | @CreatedDate、@LastModifiedDate |

---

## ✅ 课后练习

1. 创建用户、角色、部门实体
2. 实现一对多、多对多关系映射
3. 实现 CRUD、分页、排序查询
4. 使用 @Query 编写复杂查询

```java
// 练习要求
// 实体：User、Role、Department
// 关系：
// - User - Department: 多对一
// - User - Role: 多对多
// 功能：
// - CRUD 操作
// - 分页查询
// - 条件查询
// - 事务操作

---

## 📝 自测题

1. 查询方法名 `findByUsernameAndAge` 中，JPA 会自动生成什么条件？\
   A. OR  B. AND  C. LIKE  D. BETWEEN
2. 事务传播行为 `REQUIRES_NEW` 的含义是？\
   A. 加入当前事务  B. 创建新事务  C. 非事务执行  D. 抛出异常
3. N+1 查询问题的解决方案是？\
   A. 使用 EAGER 加载  B. 使用 @EntityGraph  C. 增加索引  D. 使用 @Query
4. `CascadeType.ALL` 不包含以下哪个？\
   A. PERSIST  B. MERGE  C. LOAD  D. REMOVE

**答案：1-B, 2-B, 3-B, 4-C**

---

下一课：Spring Security（→ `第七课-SpringSecurity.md`）
```