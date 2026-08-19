# Spring Boot 基础

## 一、Spring Boot 概述

Spring Boot 简化了 Spring 应用的初始搭建和开发过程，约定大于配置。

### 核心特性

```
自动配置 (Auto-Configuration)
    ↓
起步依赖 (Starters)
    ↓
内嵌服务器 (Embedded Servers)
    ↓
生产就绪 (Production Ready)
    ↓
简化配置 (Simplified Configuration)
```

## 二、快速开始

### 1. 项目结构

```
my-spring-boot-app/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/example/
│   │   │       ├── SpringBootAppApplication.java  # 启动类
│   │   │       ├── controller/                     # 控制器
│   │   │       ├── service/                        # 服务层
│   │   │       ├── repository/                     # 数据访问层
│   │   │       ├── entity/                         # 实体类
│   │   │       ├── dto/                            # 数据传输对象
│   │   │       ├── config/                         # 配置类
│   │   │       └── exception/                      # 异常处理
│   │   └── resources/
│   │       ├── application.yml                      # 主配置文件
│   │       ├── application-dev.yml                  # 开发环境
│   │       ├── application-prod.yml                 # 生产环境
│   │       ├── static/                              # 静态资源
│   │       ├── templates/                           # 模板文件
│   │       └── logback.xml                          # 日志配置
│   └── test/
│       └── java/
│           └── com/example/
│               └── SpringBootAppApplicationTests.java
└── pom.xml
```

### 2. 启动类

```java
package com.example.springbootapp;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication  // 组合注解：@SpringBootConfiguration + @EnableAutoConfiguration + @ComponentScan
public class SpringBootAppApplication {

    public static void main(String[] args) {
        SpringApplication.run(SpringBootAppApplication.class, args);
    }
}
```

## 三、配置文件

### application.yml

```yaml
# 应用配置
spring:
  application:
    name: my-spring-boot-app

  # Profile 配置
  profiles:
    active: dev

  # 数据源配置
  datasource:
    url: jdbc:mysql://localhost:3306/mydb?useSSL=false&serverTimezone=UTC
    username: root
    password: password
    driver-class-name: com.mysql.cj.jdbc.Driver
    # Hikari 连接池配置
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      connection-timeout: 30000
      idle-timeout: 600000
      max-lifetime: 1800000

  # JPA 配置
  jpa:
    hibernate:
      ddl-auto: update  # create, create-drop, update, validate, none
    show-sql: true
    properties:
      hibernate:
        dialect: org.hibernate.dialect.MySQL8Dialect
        format_sql: true

  # Redis 配置
  redis:
    host: localhost
    port: 6379
    password:
    database: 0
    lettuce:
      pool:
        max-active: 8
        max-idle: 8
        min-idle: 0

  # Web 配置
  web:
    resources:
      static-locations: classpath:/static/
    mvc:
      static-path-pattern: /static/**

# 服务器配置
server:
  port: 8080
  servlet:
    context-path: /api
  compression:
    enabled: true
  tomcat:
    threads:
      max: 200
      min-spare: 10

# 日志配置
logging:
  level:
    root: INFO
    com.example: DEBUG
    org.springframework.web: INFO
    org.hibernate.SQL: DEBUG
  file:
    name: logs/application.log
    max-size: 10MB
    max-history: 30
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n"

# 自定义配置
app:
  name: ${spring.application.name}
  version: 1.0.0
  author: Your Name
  features:
    enabled: true
    list:
      - feature1
      - feature2
      - feature3
  cache:
    ttl: 3600
    max-size: 1000

# Actuator 配置
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
      base-path: /actuator
  endpoint:
    health:
      show-details: always
  metrics:
    export:
      prometheus:
        enabled: true
```

### application-dev.yml

```yaml
server:
  port: 8080

spring:
  datasource:
    url: jdbc:mysql://localhost:3306/dev_db

logging:
  level:
    com.example: DEBUG
```

### application-prod.yml

```yaml
server:
  port: 80

spring:
  datasource:
    url: jdbc:mysql://prod-db:3306/prod_db

logging:
  level:
    com.example: INFO
  file:
    name: /var/log/app/application.log
```

## 四、配置属性类

```java
import org.springframework.boot.context.properties.*;
import org.springframework.stereotype.*;
import java.util.*;

@Configuration
@ConfigurationProperties(prefix = "app")
@Data  // Lombok
@Component
@Validated
public class AppProperties {
    private String name;
    private String version;
    private String author;

    @NotNull
    private Features features;

    @NotNull
    private Cache cache;

    @Data
    public static class Features {
        private boolean enabled;
        private List<String> list;
    }

    @Data
    public static class Cache {
        private int ttl;
        private int maxSize;
    }
}

// 使用
@Service
public class SomeService {
    private final AppProperties appProperties;

    public SomeService(AppProperties appProperties) {
        this.appProperties = appProperties;
        System.out.println("App Name: " + appProperties.getName());
    }
}
```

## 五、RESTful API

### 1. Controller

```java
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import java.util.*;

@RestController
@RequestMapping("/users")
public class UserController {
    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    // GET /users - 获取所有用户
    @GetMapping
    public ResponseEntity<List<User>> getAllUsers() {
        List<User> users = userService.findAll();
        return ResponseEntity.ok(users);
    }

    // GET /users/{id} - 获取单个用户
    @GetMapping("/{id}")
    public ResponseEntity<User> getUserById(@PathVariable Long id) {
        return userService.findById(id)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }

    // POST /users - 创建用户
    @PostMapping
    public ResponseEntity<User> createUser(@Valid @RequestBody UserCreateDto dto) {
        User user = userService.create(dto);
        return ResponseEntity
            .status(HttpStatus.CREATED)
            .body(user);
    }

    // PUT /users/{id} - 更新用户
    @PutMapping("/{id}")
    public ResponseEntity<User> updateUser(
        @PathVariable Long id,
        @Valid @RequestBody UserUpdateDto dto
    ) {
        return userService.update(id, dto)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }

    // DELETE /users/{id} - 删除用户
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        if (userService.delete(id)) {
            return ResponseEntity.noContent().build();
        }
        return ResponseEntity.notFound().build();
    }

    // GET /users/search?name=xxx - 搜索用户
    @GetMapping("/search")
    public ResponseEntity<List<User>> searchUsers(@RequestParam String name) {
        List<User> users = userService.searchByName(name);
        return ResponseEntity.ok(users);
    }

    // 分页查询
    @GetMapping("/page")
    public ResponseEntity<Page<User>> getUsersByPage(
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "10") int size,
        @RequestParam(defaultValue = "id") String sort
    ) {
        Pageable pageable = PageRequest.of(page, size, Sort.by(sort));
        Page<User> result = userService.findAll(pageable);
        return ResponseEntity.ok(result);
    }
}
```

### 2. DTO（数据传输对象）

```java
import jakarta.validation.constraints.*;

@Data
public class UserCreateDto {
    @NotBlank(message = "用户名不能为空")
    @Size(min = 3, max = 20, message = "用户名长度必须在3-20之间")
    private String username;

    @NotBlank(message = "密码不能为空")
    @Size(min = 6, max = 20, message = "密码长度必须在6-20之间")
    private String password;

    @Email(message = "邮箱格式不正确")
    private String email;

    @Pattern(regexp = "^1[3-9]\\\\d{9}$", message = "手机号格式不正确")
    private String phone;
}

@Data
public class UserUpdateDto {
    private String email;
    private String phone;
    private Integer age;
}

@Data
public class UserResponseDto {
    private Long id;
    private String username;
    private String email;
    private Integer age;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
```

### 3. Service

```java
import org.springframework.data.domain.*;
import org.springframework.stereotype.*;
import org.springframework.transaction.annotation.*;
import java.util.*;

@Service
@Transactional
public class UserService {
    private final UserRepository userRepository;
    private final UserMapper userMapper;

    public UserService(UserRepository userRepository, UserMapper userMapper) {
        this.userRepository = userRepository;
        this.userMapper = userMapper;
    }

    public List<User> findAll() {
        return userRepository.findAll();
    }

    public Optional<User> findById(Long id) {
        return userRepository.findById(id);
    }

    public Page<User> findAll(Pageable pageable) {
        return userRepository.findAll(pageable);
    }

    public List<User> searchByName(String name) {
        return userRepository.findByUsernameContaining(name);
    }

    public User create(UserCreateDto dto) {
        // 检查用户名是否存在
        if (userRepository.existsByUsername(dto.getUsername())) {
            throw new BusinessException("用户名已存在");
        }

        User user = userMapper.toEntity(dto);
        user.setCreatedAt(LocalDateTime.now());
        user.setUpdatedAt(LocalDateTime.now());

        return userRepository.save(user);
    }

    public Optional<User> update(Long id, UserUpdateDto dto) {
        return userRepository.findById(id).map(user -> {
            if (dto.getEmail() != null) {
                user.setEmail(dto.getEmail());
            }
            if (dto.getPhone() != null) {
                user.setPhone(dto.getPhone());
            }
            if (dto.getAge() != null) {
                user.setAge(dto.getAge());
            }
            user.setUpdatedAt(LocalDateTime.now());
            return userRepository.save(user);
        });
    }

    public boolean delete(Long id) {
        if (userRepository.existsById(id)) {
            userRepository.deleteById(id);
            return true;
        }
        return false;
    }

    @Transactional(readOnly = true)
    public UserResponseDto getUserResponse(Long id) {
        User user = userRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("用户不存在"));
        return userMapper.toDto(user);
    }
}
```

### 4. Repository

```java
import org.springframework.data.jpa.repository.*;
import org.springframework.data.repository.query.*;
import org.springframework.data.domain.*;
import java.util.*;

@Entity
@Table(name = "t_user")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false)
    private String username;

    @Column(nullable = false)
    private String password;

    private String email;
    private String phone;
    private Integer age;

    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    @Version
    private Integer version;  // 乐观锁
}

@Repository
public interface UserRepository extends JpaRepository<User, Long>, JpaSpecificationExecutor<User> {

    // 根据用户名查找
    Optional<User> findByUsername(String username);

    // 查询用户名包含关键字的用户
    List<User> findByUsernameContaining(String keyword);

    // 检查用户名是否存在
    boolean existsByUsername(String username);

    // 根据邮箱查询
    Optional<User> findByEmail(String email);

    // 多条件查询
    List<User> findByUsernameContainingAndEmailNotNull(String username);

    // 分页查询
    Page<User> findByAgeGreaterThan(int age, Pageable pageable);

    // 统计查询
    long countByAgeGreaterThan(int age);

    // 删除查询
    @Modifying
    @Query("DELETE FROM User u WHERE u.age < ?1")
    void deleteByAgeLessThan(int age);

    // 自定义 JPQL 查询
    @Query("SELECT u FROM User u WHERE u.username LIKE %:keyword%")
    List<User> searchUsers(@Param("keyword") String keyword);

    // 原生 SQL 查询
    @Query(value = "SELECT * FROM t_user WHERE age > :age", nativeQuery = true)
    List<User> findUsersByAgeNative(@Param("age") int age);

    // 投影查询
    @Query("SELECT new com.example.dto.UserSummary(u.id, u.username, u.email) FROM User u")
    List<UserSummary> findAllSummaries();
}
```

## 六、异常处理

```java
// 自定义异常
public class BusinessException extends RuntimeException {
    private final String code;

    public BusinessException(String message) {
        super(message);
        this.code = "BUSINESS_ERROR";
    }

    public BusinessException(String code, String message) {
        super(message);
        this.code = code;
    }
}

public class ResourceNotFoundException extends RuntimeException {
    public ResourceNotFoundException(String message) {
        super(message);
    }
}

// 全局异常处理器
@RestControllerAdvice
public class GlobalExceptionHandler {

    // 处理业务异常
    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ErrorResponse> handleBusinessException(BusinessException ex) {
        ErrorResponse error = ErrorResponse.builder()
            .code(ex.getCode())
            .message(ex.getMessage())
            .timestamp(LocalDateTime.now())
            .build();
        return ResponseEntity.badRequest().body(error);
    }

    // 处理资源不存在异常
    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleResourceNotFoundException(ResourceNotFoundException ex) {
        ErrorResponse error = ErrorResponse.builder()
            .code("NOT_FOUND")
            .message(ex.getMessage())
            .timestamp(LocalDateTime.now())
            .build();
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
    }

    // 处理参数校验异常
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidationException(MethodArgumentNotValidException ex) {
        Map<String, String> errors = new HashMap<>();
        ex.getBindingResult().getFieldErrors().forEach(error ->
            errors.put(error.getField(), error.getDefaultMessage())
        );

        ErrorResponse error = ErrorResponse.builder()
            .code("VALIDATION_ERROR")
            .message("参数校验失败")
            .details(errors)
            .timestamp(LocalDateTime.now())
            .build();

        return ResponseEntity.badRequest().body(error);
    }

    // 处理所有未捕获的异常
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleException(Exception ex) {
        ErrorResponse error = ErrorResponse.builder()
            .code("INTERNAL_ERROR")
            .message("服务器内部错误")
            .timestamp(LocalDateTime.now())
            .build();

        // 记录日志
        log.error("未捕获的异常", ex);

        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
    }
}

// 错误响应 DTO
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ErrorResponse {
    private String code;
    private String message;
    private Map<String, String> details;
    private LocalDateTime timestamp;
}
```

## 七、参数校验

```java
import jakarta.validation.*;

// 校验组
public interface CreateGroup {}

public interface UpdateGroup {}

// DTO
@Data
public class UserCreateDto {
    @NotNull(groups = CreateGroup.class, message = "用户ID不能为空")
    private Long id;

    @NotBlank(message = "用户名不能为空")
    @Size(min = 3, max = 20, message = "用户名长度必须在3-20之间")
    private String username;

    @NotBlank(message = "密码不能为空")
    @Pattern(regexp = "^(?=.*[A-Za-z])(?=.*\\d)[A-Za-z\\d]{8,}$",
             message = "密码必须包含字母和数字，至少8位")
    private String password;

    @Email(message = "邮箱格式不正确")
    private String email;

    @Min(value = 0, message = "年龄不能小于0")
    @Max(value = 150, message = "年龄不能大于150")
    private Integer age;

    @AssertTrue(message = "必须同意协议")
    private boolean agreedToTerms;
}

// Controller 中使用
@RestController
@RequestMapping("/users")
@Validated
public class UserController {

    @PostMapping
    public ResponseEntity<User> createUser(
        @Validated(CreateGroup.class) @RequestBody UserCreateDto dto
    ) {
        // 校验通过
        return ResponseEntity.ok(userService.create(dto));
    }

    // 路径变量校验
    @GetMapping("/{id}")
    public ResponseEntity<User> getUser(
        @PathVariable @Min(1) Long id
    ) {
        return ResponseEntity.ok(userService.findById(id));
    }

    // 请求参数校验
    @GetMapping("/search")
    public ResponseEntity<List<User>> search(
        @RequestParam @NotBlank String keyword,
        @RequestParam(defaultValue = "0") @Min(0) Integer page
    ) {
        return ResponseEntity.ok(userService.search(keyword, page));
    }

    // 自定义校验注解
    @Target({ElementType.FIELD})
    @Retention(RetentionPolicy.RUNTIME)
    @Constraint(validatedBy = UsernameValidator.class)
    public @interface ValidUsername {
        String message() default "用户名格式不正确";
        Class<?>[] groups() default {};
        Class<? extends Payload>[] payload() default {};
    }

    // 自定义校验器
    public class UsernameValidator implements ConstraintValidator<ValidUsername, String> {
        @Override
        public void initialize(ValidUsername constraintAnnotation) {}

        @Override
        public boolean isValid(String value, ConstraintValidatorContext context) {
            if (value == null) {
                return true;
            }
            // 自定义校验逻辑
            return value.matches("^[a-zA-Z0-9_]{3,20}$");
        }
    }

    // 使用自定义注解
    @Data
    public class UserDto {
        @ValidUsername
        private String username;
    }
}
```

## 八、数据库操作

### JPA 实体

```java
import jakarta.persistence.*;
import org.springframework.data.annotation.*;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;
import java.time.*;

@Entity
@Table(name = "t_user", indexes = {
    @Index(name = "idx_username", columnList = "username"),
    @Index(name = "idx_email", columnList = "email")
})
@EntityListeners(AuditingEntityListener.class)
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true, length = 50)
    private String username;

    @Column(nullable = false)
    private String password;

    @Column(length = 100)
    private String email;

    @Column(length = 20)
    private String phone;

    @Column
    private Integer age;

    @Enumerated(EnumType.STRING)
    @Column(length = 20)
    private UserStatus status;

    @Lob
    private String bio;

    // 审计字段
    @CreatedDate
    @Column(updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    private LocalDateTime updatedAt;

    @CreatedBy
    @Column(updatable = false, length = 50)
    private String createdBy;

    @LastModifiedBy
    @Column(length = 50)
    private String modifiedBy;

    @Version
    private Integer version;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
        if (status == null) {
            status = UserStatus.ACTIVE;
        }
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}

public enum UserStatus {
    ACTIVE, INACTIVE, LOCKED
}

// 启用审计
@Configuration
@EnableJpaAuditing
public class JpaConfig {
    @Bean
    public AuditorAware<String> auditorProvider() {
        return () -> Optional.of("system");  // 实际应用中从 Security Context 获取
    }
}
```

### MyBatis

```java
// Mapper 接口
@Mapper
public interface UserMapper {
    @Select("SELECT * FROM t_user WHERE id = #{id}")
    User findById(Long id);

    @Insert("INSERT INTO t_user(username, password, email) " +
            "VALUES(#{username}, #{password}, #{email})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(User user);

    @Update("UPDATE t_user SET email = #{email} WHERE id = #{id}")
    int update(User user);

    @Delete("DELETE FROM t_user WHERE id = #{id}")
    int deleteById(Long id);

    // 动态 SQL
    @SelectProvider(type = UserSqlProvider.class, method = "buildSelectQuery")
    List<User> findByCondition(UserQuery query);
}

// SQL 提供器
public class UserSqlProvider {
    public String buildSelectQuery(UserQuery query) {
        return new SQL() {{
            SELECT("*");
            FROM("t_user");

            if (query.getUsername() != null) {
                WHERE("username LIKE CONCAT('%', #{username}, '%')");
            }
            if (query.getEmail() != null) {
                AND();
                WHERE("email = #{email}");
            }
            if (query.getMinAge() != null) {
                AND();
                WHERE("age >= #{minAge}");
            }
            if (query.getMaxAge() != null) {
                AND();
                WHERE("age <= #{maxAge}");
            }

            ORDER_BY("id DESC");
        }}.toString();
    }
}

// XML 配置
/*
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
    "http://mybatis.org/dtd/mybatis-3-mapper.dtd">

<mapper namespace="com.example.mapper.UserMapper">
    <resultMap id="BaseResultMap" type="com.example.entity.User">
        <id column="id" property="id" jdbcType="BIGINT"/>
        <result column="username" property="username" jdbcType="VARCHAR"/>
        <result column="password" property="password" jdbcType="VARCHAR"/>
        <result column="email" property="email" jdbcType="VARCHAR"/>
        <result column="age" property="age" jdbcType="INTEGER"/>
    </resultMap>

    <select id="findById" resultMap="BaseResultMap">
        SELECT * FROM t_user WHERE id = #{id}
    </select>

    <insert id="insert" parameterType="com.example.entity.User"
            useGeneratedKeys="true" keyProperty="id">
        INSERT INTO t_user (username, password, email)
        VALUES (#{username}, #{password}, #{email})
    </insert>

    <update id="update" parameterType="com.example.entity.User">
        UPDATE t_user
        <set>
            <if test="email != null">email = #{email},</if>
            <if test="age != null">age = #{age},</if>
        </set>
        WHERE id = #{id}
    </update>
</mapper>
*/
```

## 小结

本节学习了 Spring Boot 基础：

- **项目结构** - 标准项目目录布局
- **配置文件** - application.yml 多环境配置
- **RESTful API** - Controller、Service、Repository
- **异常处理** - 全局异常处理器
- **参数校验** - Bean Validation
- **数据库操作** - JPA 和 MyBatis

## 实践练习

### 编程题
1. 从零搭建一个 Spring Boot 项目，集成 MyBatis Plus + MySQL，实现一个完整的用户 CRUD 接口，包含分页查询和条件筛选。
2. 使用 Spring Boot Actuator + Micrometer + Prometheus 实现应用监控，配置健康检查、Metrics 指标采集和自定义业务指标。

### 思考题
1. Spring Boot 的自动配置原理是什么？`@SpringBootApplication` 注解包含哪三个注解？
2. Spring Boot Starter 的工作机制？如何自定义一个 Starter？

### 自测题
1. `application.yml` 和 `application.properties` 的区别？
2. Spring Boot 支持哪些内嵌服务器？
3. `@ConfigurationProperties` 的作用？

下一步将学习 Spring Cloud Alibaba 微服务（→ `spring-cloud-alibaba/beginner/01-spring-cloud-alibaba.md`）。