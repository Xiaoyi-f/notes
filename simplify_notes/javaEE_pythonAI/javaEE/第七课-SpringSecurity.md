# Spring 学习笔记 - 第七课：Spring Security

## 1. 什么是 Spring Security？

**Spring Security = Spring 生态的安全框架**

提供认证（Authentication）和授权（Authorization）功能。

### 核心概念

| 概念 | 说明 | 示例 |
|------|------|------|
| **认证（Authentication）** | 验证你是谁 | 登录验证用户名密码 |
| **授权（Authorization）** | 验证你能做什么 | 判断用户是否有访问权限 |
| **主体（Principal）** | 当前用户 | 当前登录的用户对象 |
| **凭证（Credential）** | 证明身份的信息 | 密码、Token |
| **权限（Authority）** | 用户拥有的权限 | ROLE_ADMIN、ROLE_USER |

---

## 2. 快速开始

### 添加依赖

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-security</artifactId>
</dependency>
```

### 默认行为

添加依赖后，Spring Security 会自动：
- 保护所有 HTTP 端点
- 生成默认用户 `user`
- 生成随机密码（控制台输出）

```bash
Using generated security password: 78fa095d-3f4b-49b2-a58f-d5f75e1b8a09
```

---

## 3. Security 配置

### 基础配置

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            // 关闭 CSRF
            .csrf(csrf -> csrf.disable())

            // 配置请求授权
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/public/**").permitAll()      // 公开接口
                .requestMatchers("/api/admin/**").hasRole("ADMIN")   // 需要 ADMIN 角色
                .requestMatchers("/api/user/**").hasAnyRole("ADMIN", "USER")  // 需要角色
                .anyRequest().authenticated()                        // 其他需要认证
            )

            // 配置表单登录
            .formLogin(form -> form
                .loginPage("/login")                      // 自定义登录页
                .loginProcessingUrl("/api/auth/login")    // 登录处理地址
                .usernameParameter("username")            // 用户名参数名
                .passwordParameter("password")            // 密码参数名
                .defaultSuccessUrl("/api/user/profile")   // 登录成功跳转
                .failureUrl("/login?error")               // 登录失败跳转
                .permitAll()
            )

            // 配置登出
            .logout(logout -> logout
                .logoutUrl("/api/auth/logout")            // 登出地址
                .logoutSuccessUrl("/login")               // 登出成功跳转
                .deleteCookies("JSESSIONID")              // 删除 Cookie
                .permitAll()
            )

            // 异常处理
            .exceptionHandling(exception -> exception
                .authenticationEntryPoint((request, response, authException) -> {
                    response.setStatus(401);
                    response.setContentType("application/json");
                    response.getWriter().write("{\"code\":401,\"message\":\"未登录\"}");
                })
                .accessDeniedHandler((request, response, accessDeniedException) -> {
                    response.setStatus(403);
                    response.setContentType("application/json");
                    response.getWriter().write("{\"code\":403,\"message\":\"无权限\"}");
                })
            );

        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
```

### 用户详情服务

```java
@Service
public class CustomUserDetailsService implements UserDetailsService {

    @Autowired
    private UserRepository userRepository;

    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        User user = userRepository.findByUsername(username)
            .orElseThrow(() -> new UsernameNotFoundException("用户不存在"));

        // 转换为 UserDetails
        return org.springframework.security.core.userdetails.User.builder()
            .username(user.getUsername())
            .password(user.getPassword())
            .roles(user.getRoles().stream().map(Role::getName).toArray(String[]::new))
            .build();
    }
}
```

### 认证管理器

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Autowired
    private CustomUserDetailsService userDetailsService;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Bean
    public AuthenticationManager authenticationManager(AuthenticationConfiguration config) throws Exception {
        return config.getAuthenticationManager();
    }

    @Bean
    public AuthenticationProvider authenticationProvider() {
        DaoAuthenticationProvider provider = new DaoAuthenticationProvider();
        provider.setUserDetailsService(userDetailsService);
        provider.setPasswordEncoder(passwordEncoder);
        return provider;
    }
}
```

---

## 4. 密码编码器

### BCryptPasswordEncoder（推荐）

```java
@Service
public class UserService {

    @Autowired
    private PasswordEncoder passwordEncoder;

    public void register(User user) {
        // 加密密码
        String encodedPassword = passwordEncoder.encode(user.getPassword());
        user.setPassword(encodedPassword);
        userRepository.save(user);
    }

    public boolean checkPassword(String rawPassword, String encodedPassword) {
        return passwordEncoder.matches(rawPassword, encodedPassword);
    }
}
```

### 其他编码器

| 编码器 | 说明 |
|--------|------|
| `BCryptPasswordEncoder` | BCrypt 加密（推荐） |
| `NoOpPasswordEncoder` | 明文（不安全） |
| `Pbkdf2PasswordEncoder` | PBKDF2 加密 |
| `SCryptPasswordEncoder` | SCrypt 加密 |
| `Argon2PasswordEncoder` | Argon2 加密 |

---

## 5. JWT 认证（高频考点）

### 什么是 JWT？

**JWT = JSON Web Token**

一种跨域认证解决方案，由三部分组成：

```
Header.Payload.Signature
```

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
   ↑                    ↑                              ↑
  Header             Payload                       Signature
```

### JWT 结构

| 部分 | 说明 | 示例 |
|------|------|------|
| **Header** | 算法和类型 | `{"alg":"HS256","typ":"JWT"}` |
| **Payload** | 数据（用户信息） | `{"sub":"123","name":"John"}` |
| **Signature** | 签名 | 签名验证数据完整性 |

### JWT 实现

#### 添加依赖

```xml
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-api</artifactId>
    <version>0.11.5</version>
</dependency>
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-impl</artifactId>
    <version>0.11.5</version>
    <scope>runtime</scope>
</dependency>
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-jackson</artifactId>
    <version>0.11.5</version>
    <scope>runtime</scope>
</dependency>
```

#### JWT 工具类

```java
@Component
public class JwtUtil {

    private String secret = "my-secret-key";
    private long expiration = 86400000; // 24小时

    // 生成 Token
    public String generateToken(String username) {
        Date now = new Date();
        Date expiryDate = new Date(now.getTime() + expiration);

        return Jwts.builder()
            .setSubject(username)
            .setIssuedAt(now)
            .setExpiration(expiryDate)
            .signWith(SignatureAlgorithm.HS256, secret)
            .compact();
    }

    // 从 Token 获取用户名
    public String getUsernameFromToken(String token) {
        Claims claims = Jwts.parser()
            .setSigningKey(secret)
            .parseClaimsJws(token)
            .getBody();
        return claims.getSubject();
    }

    // 验证 Token
    public boolean validateToken(String token) {
        try {
            Jwts.parser().setSigningKey(secret).parseClaimsJws(token);
            return true;
        } catch (JwtException | IllegalArgumentException e) {
            return false;
        }
    }

    // 获取过期时间
    public Date getExpirationDateFromToken(String token) {
        Claims claims = Jwts.parser()
            .setSigningKey(secret)
            .parseClaimsJws(token)
            .getBody();
        return claims.getExpiration();
    }

    // 判断是否过期
    public boolean isTokenExpired(String token) {
        Date expiration = getExpirationDateFromToken(token);
        return expiration.before(new Date());
    }
}
```

#### JWT 登录接口

```java
@RestController
@RequestMapping("/api/auth")
public class AuthController {

    @Autowired
    private AuthenticationManager authenticationManager;

    @Autowired
    private JwtUtil jwtUtil;

    @Autowired
    private UserRepository userRepository;

    @PostMapping("/login")
    public ResponseEntity<LoginResponse> login(@RequestBody LoginRequest request) {
        // 认证
        Authentication authentication = authenticationManager.authenticate(
            new UsernamePasswordAuthenticationToken(request.getUsername(), request.getPassword())
        );

        // 设置 SecurityContext
        SecurityContextHolder.getContext().setAuthentication(authentication);

        // 生成 Token
        String token = jwtUtil.generateToken(request.getUsername());

        // 获取用户信息
        User user = userRepository.findByUsername(request.getUsername()).orElse(null);

        return ResponseEntity.ok(new LoginResponse(token, user));
    }

    @PostMapping("/register")
    public ResponseEntity<User> register(@RequestBody RegisterRequest request) {
        // 创建用户
        User user = new User();
        user.setUsername(request.getUsername());
        user.setPassword(passwordEncoder.encode(request.getPassword()));
        userRepository.save(user);

        return ResponseEntity.ok(user);
    }
}
```

#### JWT 过滤器

```java
@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    @Autowired
    private JwtUtil jwtUtil;

    @Autowired
    private CustomUserDetailsService userDetailsService;

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain filterChain) throws ServletException, IOException {
        // 获取 Authorization 头
        String authHeader = request.getHeader("Authorization");

        // 检查格式
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            filterChain.doFilter(request, response);
            return;
        }

        // 提取 Token
        String token = authHeader.substring(7);

        // 验证 Token
        if (!jwtUtil.validateToken(token)) {
            filterChain.doFilter(request, response);
            return;
        }

        // 获取用户名
        String username = jwtUtil.getUsernameFromToken(token);

        // 加载用户详情
        UserDetails userDetails = userDetailsService.loadUserByUsername(username);

        // 创建认证对象
        UsernamePasswordAuthenticationToken authentication =
            new UsernamePasswordAuthenticationToken(userDetails, null, userDetails.getAuthorities());

        // 设置到 SecurityContext
        SecurityContextHolder.getContext().setAuthentication(authentication);

        filterChain.doFilter(request, response);
    }
}
```

#### 添加 JWT 过滤器

```java
@Bean
public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
    http
        .csrf(csrf -> csrf.disable())
        .authorizeHttpRequests(auth -> auth
            .requestMatchers("/api/auth/**").permitAll()
            .anyRequest().authenticated()
        )
        .sessionManagement(session -> session
            .sessionCreationPolicy(SessionCreationPolicy.STATELESS)  // 无状态
        )
        .addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class);

    return http.build();
}
```

---

## 6. 权限控制

### @PreAuthorize

```java
@RestController
@RequestMapping("/api/admin")
public class AdminController {

    // 需要 ADMIN 角色
    @PreAuthorize("hasRole('ADMIN')")
    @GetMapping("/users")
    public List<User> getAllUsers() {
        return userRepository.findAll();
    }

    // 需要指定权限
    @PreAuthorize("hasAuthority('user:read')")
    @GetMapping("/users/{id}")
    public User getUser(@PathVariable Long id) {
        return userRepository.findById(id).orElse(null);
    }

    // 多个权限（满足一个即可）
    @PreAuthorize("hasAnyRole('ADMIN', 'USER')")
    @GetMapping("/profile")
    public User getProfile() {
        // ...
    }

    // 自定义权限判断
    @PreAuthorize("@permissionService.hasPermission(#id, 'user:read')")
    @GetMapping("/users/{id}")
    public User getUser(@PathVariable Long id) {
        // ...
    }

    // 当前用户只能是资源所有者
    @PreAuthorize("#userId == authentication.principal.id")
    @GetMapping("/users/{userId}/profile")
    public User getProfile(@PathVariable Long userId) {
        // ...
    }
}
```

### @PostAuthorize

```java
// 方法执行后再检查权限
@PostAuthorize("returnObject.owner == authentication.principal.username")
public Document getDocument(String documentId) {
    // ...
}
```

### 方法级安全配置

```java
@Configuration
@EnableMethodSecurity
public class MethodSecurityConfig {
}
```

---

## 7. 常用注解

| 注解 | 说明 | 示例 |
|------|------|------|
| `@PreAuthorize` | 方法执行前检查 | `@PreAuthorize("hasRole('ADMIN')")` |
| `@PostAuthorize` | 方法执行后检查 | `@PostAuthorize("returnObject.owner == ...")` |
| `@Secured` | 简化权限检查 | `@Secured("ROLE_ADMIN")` |
| `@RolesAllowed` | JSR-250 注解 | `@RolesAllowed("ADMIN")` |
| `@AuthenticationPrincipal` | 获取当前用户 | `public void method(@AuthenticationPrincipal User user)` |

---

## 8. 常见面试问题

### Q1: Spring Security 认证流程？

**答案：**
1. 用户提交认证信息
2. `AuthenticationFilter` 拦截请求，创建 `Authentication` 对象
3. `AuthenticationManager` 进行认证
4. `UserDetailsService` 加载用户详情
5. `PasswordEncoder` 验证密码
6. 认证成功，将 `Authentication` 存入 `SecurityContext`

### Q2: JWT 和 Session 的区别？

**答案：**
| 特性 | JWT | Session |
|------|-----|---------|
| 存储 | 客户端 | 服务器 |
| 无状态 | 是 | 否 |
| 跨域 | 容易 | 困难 |
| 服务器压力 | 低 | 高 |
| 安全性 | 相对低 | 高 |
| 续期 | 困难 | 容易 |

### Q3: 常见的攻击方式及防御？

| 攻击 | 防御 |
|------|------|
| CSRF | CSRF Token、SameSite Cookie |
| XSS | 输入过滤、输出转义、CSP |
| SQL注入 | 预编译语句、参数校验 |
| 暴力破解 | 验证码、限流、账户锁定 |

---

## 9. 完整认证授权流程

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户登录                                   │
└─────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│                    提交用户名密码                                │
└─────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│                AuthenticationManager 认证                        │
│                      ↓                                           │
│               UserDetailsService 加载用户                        │
│                      ↓                                           │
│               PasswordEncoder 验证密码                          │
└─────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│                     认证成功                                     │
│                   生成 JWT Token                                 │
└─────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│                       访问接口                                   │
└─────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│                  JwtAuthenticationFilter                        │
│                      ↓                                           │
│                   验证 JWT Token                                │
│                      ↓                                           │
│               加载用户信息到 SecurityContext                     │
└─────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│                   FilterSecurityInterceptor                      │
│                      ↓                                           │
│                   检查权限（@PreAuthorize 等）                   │
└─────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│                    执行业务逻辑                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 本节面试考点总结

| 考点 | 问题 | 关键点 |
|------|------|--------|
| Spring Security | 核心功能？ | 认证和授权 |
| 认证流程 | 认证流程？ | AuthenticationManager → UserDetailsService → PasswordEncoder |
| 认证 vs 授权 | 区别？ | 认证验证你是谁，授权验证你能做什么 |
| JWT | 什么是 JWT？ | JSON Web Token，Header.Payload.Signature |
| JWT vs Session | 区别？ | JWT 无状态，Session 有状态 |
| 密码编码 | 推荐编码器？ | BCryptPasswordEncoder |
| 注解 | 常用注解？ | @PreAuthorize、@PostAuthorize、@Secured |
| CSRF | 什么是 CSRF？ | 跨站请求伪造攻击 |
| XSS | 什么是 XSS？ | 跨站脚本攻击 |

---

## ✅ 课后练习

1. 实现基于 JWT 的登录认证
2. 实现基于角色的权限控制
3. 实现 JWT 过滤器
4. 实现权限注解

```java
// 练习要求
// 功能：
// - 用户注册
// - JWT 登录
// - Token 刷新
// - 权限控制（基于角色）
// - 自定义权限判断

---

## 📝 自测题

1. Spring Security 的核心功能是？\
   A. 日志和监控  B. 认证和授权  C. 分页和排序  D. 缓存和事务
2. JWT 由哪三部分组成？\
   A. Header.Body.Footer  B. Header.Payload.Signature  C. Token.Data.Sign  D. Key.Value.Time
3. JWT 认证相比 Session 认证的优势是？\
   A. 更安全  B. 服务器存储少、支持分布式  C. 实现更简单  D. Token 无法被泄露
4. 推荐使用的密码编码器是？\
   A. MD5  B. SHA256  C. BCryptPasswordEncoder  D. NoOpPasswordEncoder

**答案：1-B, 2-B, 3-B, 4-C**

---

下一课：面试高频考点汇总（→ `第八课-面试高频考点.md`）
```