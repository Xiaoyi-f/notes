# Spring 学习笔记 - 第五课：Spring MVC

## 1. 什么是 Spring MVC？

**Spring MVC = Spring 的 Web 框架**

### MVC 架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         浏览器（客户端）                          │
└─────────────────────────────────────────────────────────────────┘
                          ↓ HTTP 请求
┌─────────────────────────────────────────────────────────────────┐
│                     核心控制器：DispatcherServlet                 │
│                         （前端控制器）                            │
└─────────────────────────────────────────────────────────────────┘
                          ↓
        ┌───────────────────┼───────────────────┐
        ↓                   ↓                   ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ HandlerMapping│  │ Controller   │  │ ViewResolver │
│ (处理器映射)  │  │ (控制器)      │  │ (视图解析器)  │
└──────────────┘  └──────────────┘  └──────────────┘
        ↓                   ↓                   ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ 找到处理器    │  │ 业务逻辑处理  │  │ 解析视图      │
└──────────────┘  └──────────────┘  └──────────────┘
                          ↓
                  ┌──────────────┐
                  │    View      │
                  │  (视图/JSP)   │
                  └──────────────┘
                          ↓
                  ┌──────────────┐
                  │  HTML 页面    │
                  └──────────────┘
```

---

## 2. 核心组件（面试必考）

| 组件 | 说明 | 作用 |
|------|------|------|
| **DispatcherServlet** | 前端控制器 | 核心控制器，处理所有请求 |
| **HandlerMapping** | 处理器映射 | 根据 URL 找到对应的 Controller |
| **HandlerAdapter** | 处理器适配器 | 调用 Controller 方法 |
| **Controller** | 控制器 | 处理业务逻辑 |
| **ViewResolver** | 视图解析器 | 解析视图名返回视图对象 |
| **View** | 视图 | 渲染页面（JSP、Thymeleaf 等） |

### 执行流程

```
1. 用户发送请求 → DispatcherServlet
2. DispatcherServlet → HandlerMapping（找哪个 Controller 处理）
3. HandlerMapping → 返回 HandlerExecutionChain
4. DispatcherServlet → HandlerAdapter（执行 Controller）
5. HandlerAdapter → Controller（执行业务逻辑）
6. Controller → 返回 ModelAndView
7. DispatcherServlet → ViewResolver（解析视图）
8. ViewResolver → 返回 View
9. View → 渲染页面
10. DispatcherServlet → 返回响应给用户
```

---

## 3. @RequestMapping 注解

### 基本使用

```java
@RestController
@RequestMapping("/api/users")  // 类级别映射
public class UserController {

    @GetMapping                  // GET /api/users
    public List<User> findAll() {
        return userService.findAll();
    }

    @GetMapping("/{id}")         // GET /api/users/{id}
    public User findById(@PathVariable Long id) {
        return userService.findById(id);
    }

    @PostMapping                 // POST /api/users
    public User save(@RequestBody User user) {
        return userService.save(user);
    }

    @PutMapping("/{id}")         // PUT /api/users/{id}
    public User update(@PathVariable Long id, @RequestBody User user) {
        return userService.update(id, user);
    }

    @DeleteMapping("/{id}")      // DELETE /api/users/{id}
    public void delete(@PathVariable Long id) {
        userService.delete(id);
    }
}
```

### 常用属性

| 属性 | 说明 | 示例 |
|------|------|------|
| `value` / `path` | 请求路径 | `@RequestMapping("/users")` |
| `method` | 请求方法 | `@RequestMapping(method = RequestMethod.POST)` |
| `params` | 请求参数 | `@RequestMapping(params = "name")` |
| `headers` | 请求头 | `@RequestMapping(headers = "X-Requested-With=XMLHttpRequest")` |
| `consumes` | 接受的内容类型 | `@RequestMapping(consumes = "application/json")` |
| `produces` | 返回的内容类型 | `@RequestMapping(produces = "application/json")` |

### 组合注解

```java
@GetMapping      = @RequestMapping(method = RequestMethod.GET)
@PostMapping     = @RequestMapping(method = RequestMethod.POST)
@PutMapping      = @RequestMapping(method = RequestMethod.PUT)
@DeleteMapping   = @RequestMapping(method = RequestMethod.DELETE)
@PatchMapping    = @RequestMapping(method = RequestMethod.PATCH)
```

---

## 4. 参数绑定

### @PathVariable（路径变量）

```java
@GetMapping("/users/{id}")
public User getUser(@PathVariable Long id) {
    return userService.findById(id);
}

@GetMapping("/users/{id}/posts/{postId}")
public Post getUserPost(@PathVariable Long id, @PathVariable Long postId) {
    return userService.findPost(id, postId);
}

// 自定义名称
@GetMapping("/users/{userId}")
public User getUser(@PathVariable("userId") Long id) {
    return userService.findById(id);
}
```

### @RequestParam（请求参数）

```java
// 查询参数：/api/users?name=zhangsan&age=20
@GetMapping("/users")
public List<User> findUsers(
    @RequestParam String name,
    @RequestParam Integer age
) {
    return userService.findByNameAndAge(name, age);
}

// 可选参数
@GetMapping("/users")
public List<User> findUsers(
    @RequestParam(required = false) String name
) {
    return userService.findByName(name);
}

// 默认值
@GetMapping("/users")
public List<User> findUsers(
    @RequestParam(defaultValue = "0") int page,
    @RequestParam(defaultValue = "10") int size
) {
    return userService.findByPage(page, size);
}

// 多值参数
@GetMapping("/users")
public List<User> findUsers(@RequestParam List<Long> ids) {
    return userService.findByIds(ids);
}
```

### @RequestBody（请求体）

```java
// POST /api/users
// Content-Type: application/json
// Body: {"name": "zhangsan", "age": 20}
@PostMapping("/users")
public User save(@RequestBody User user) {
    return userService.save(user);
}

// 接收 Map
@PostMapping("/users")
public Map<String, Object> save(@RequestBody Map<String, Object> data) {
    return data;
}
```

### @RequestHeader（请求头）

```java
@GetMapping("/users")
public String getUser(
    @RequestHeader("Authorization") String token,
    @RequestHeader(value = "User-Agent", required = false) String userAgent
) {
    return "Token: " + token;
}
```

### @CookieValue（Cookie）

```java
@GetMapping("/users")
public String getUser(@CookieValue("sessionId") String sessionId) {
    return "Session: " + sessionId;
}
```

### @ModelAttribute（模型属性）

```java
// 表单提交数据自动绑定到对象
@PostMapping("/users")
public User save(@ModelAttribute User user) {
    return userService.save(user);
}

// 可以省略，默认会自动绑定
@PostMapping("/users")
public User save(User user) {
    return userService.save(user);
}
```

---

## 5. 返回值类型

| 类型 | 说明 | 示例 |
|------|------|------|
| **String** | 视图名 | `return "user/list"` |
| **void** | 默认视图名或直接响应 | |
| **ModelAndView** | 视图和模型 | `return new ModelAndView("list", model)` |
| **对象** | JSON 响应 | `return user` |
| **ResponseEntity** | 完整响应（状态码、头、体） | `return ResponseEntity.ok(user)` |
| **Map** | JSON 响应 | `return Map.of("name", "zhangsan")` |
| **List** | JSON 数组 | `return List.of(user1, user2)` |

### 示例

```java
@RestController
public class UserController {

    // 返回对象（JSON）
    @GetMapping("/users/{id}")
    public User findById(@PathVariable Long id) {
        return userService.findById(id);
    }

    // 返回 Map（JSON）
    @GetMapping("/users")
    public Map<String, Object> findAll() {
        Map<String, Object> result = new HashMap<>();
        result.put("data", userService.findAll());
        result.put("total", userService.count());
        return result;
    }

    // 返回 ResponseEntity
    @GetMapping("/users/{id}")
    public ResponseEntity<User> findById(@PathVariable Long id) {
        User user = userService.findById(id);
        if (user == null) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(user);
    }

    // 返回状态码
    @PostMapping("/users")
    public ResponseEntity<User> save(@RequestBody User user) {
        User saved = userService.save(user);
        return ResponseEntity.status(HttpStatus.CREATED).body(saved);
    }
}
```

---

## 6. 响应状态码

```java
@RestController
public class UserController {

    @GetMapping("/users/{id}")
    public ResponseEntity<User> findById(@PathVariable Long id) {
        User user = userService.findById(id);

        if (user == null) {
            return ResponseEntity.notFound().build();           // 404
        }

        return ResponseEntity.ok(user);                          // 200
    }

    @PostMapping("/users")
    public ResponseEntity<User> save(@RequestBody User user) {
        User saved = userService.save(user);
        return ResponseEntity
            .status(HttpStatus.CREATED)                         // 201
            .header("Location", "/api/users/" + saved.getId())
            .body(saved);
    }

    @PutMapping("/users/{id}")
    public ResponseEntity<User> update(@PathVariable Long id, @RequestBody User user) {
        if (!userService.exists(id)) {
            return ResponseEntity.notFound().build();           // 404
        }
        return ResponseEntity.ok(userService.update(id, user)); // 200
    }

    @DeleteMapping("/users/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        if (!userService.exists(id)) {
            return ResponseEntity.notFound().build();           // 404
        }
        userService.delete(id);
        return ResponseEntity.noContent().build();              // 204
    }
}
```

### 常用状态码

| 状态码 | 说明 | 使用场景 |
|--------|------|----------|
| 200 | OK | 请求成功 |
| 201 | Created | 创建成功 |
| 204 | No Content | 删除成功 |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未认证 |
| 403 | Forbidden | 无权限 |
| 404 | Not Found | 资源不存在 |
| 500 | Internal Server Error | 服务器内部错误 |

---

## 7. 异常处理

### @ExceptionHandler

```java
@RestController
public class UserController {

    @GetMapping("/users/{id}")
    public User findById(@PathVariable Long id) {
        User user = userService.findById(id);
        if (user == null) {
            throw new UserNotFoundException("用户不存在");
        }
        return user;
    }

    @ExceptionHandler(UserNotFoundException.class)
    public ResponseEntity<String> handleUserNotFound(UserNotFoundException e) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(e.getMessage());
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<String> handleException(Exception e) {
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("服务器错误");
    }
}
```

### @ControllerAdvice（全局异常处理）

```java
@ControllerAdvice
public class GlobalExceptionHandler {

    // 业务异常
    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ErrorResponse> handleBusinessException(BusinessException e) {
        ErrorResponse error = new ErrorResponse(
            e.getCode(),
            e.getMessage(),
            System.currentTimeMillis()
        );
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(error);
    }

    // 资源不存在
    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleResourceNotFound(ResourceNotFoundException e) {
        ErrorResponse error = new ErrorResponse(
            404,
            e.getMessage(),
            System.currentTimeMillis()
        );
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
    }

    // 参数校验异常
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidationException(MethodArgumentNotValidException e) {
        String message = e.getBindingResult()
            .getFieldErrors()
            .stream()
            .map(FieldError::getDefaultMessage)
            .collect(Collectors.joining(", "));

        ErrorResponse error = new ErrorResponse(400, message, System.currentTimeMillis());
        return ResponseEntity.badRequest().body(error);
    }

    // 全局异常
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleException(Exception e) {
        ErrorResponse error = new ErrorResponse(
            500,
            "服务器内部错误",
            System.currentTimeMillis()
        );
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
    }
}
```

### 统一响应格式

```java
@Data
@AllArgsConstructor
public class ApiResponse<T> {
    private int code;
    private String message;
    private T data;
    private long timestamp;

    public static <T> ApiResponse<T> success(T data) {
        return new ApiResponse<>(200, "成功", data, System.currentTimeMillis());
    }

    public static <T> ApiResponse<T> error(int code, String message) {
        return new ApiResponse<>(code, message, null, System.currentTimeMillis());
    }
}
```

```java
@RestController
public class UserController {

    @GetMapping("/users/{id}")
    public ApiResponse<User> findById(@PathVariable Long id) {
        User user = userService.findById(id);
        return ApiResponse.success(user);
    }
}
```

---

## 8. 参数校验

### 添加依赖

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-validation</artifactId>
</dependency>
```

### 校验注解

| 注解 | 说明 |
|------|------|
| `@NotNull` | 不能为 null |
| `@NotBlank` | 字符串不能为空（只用于字符串） |
| `@NotEmpty` | 集合不能为空 |
| `@Size(min=, max=)` | 字符串/集合长度范围 |
| `@Min(value)` | 数字最小值 |
| `@Max(value)` | 数字最大值 |
| `@Email` | 邮箱格式 |
| `@Pattern(regexp)` | 正则表达式 |
| `@Past` | 日期必须是过去 |
| `@Future` | 日期必须是未来 |

### 使用示例

```java
@Data
public class UserCreateRequest {
    @NotBlank(message = "用户名不能为空")
    @Size(min = 2, max = 20, message = "用户名长度2-20")
    private String username;

    @NotBlank(message = "密码不能为空")
    @Size(min = 6, max = 20, message = "密码长度6-20")
    private String password;

    @Email(message = "邮箱格式不正确")
    private String email;

    @Min(value = 18, message = "年龄必须大于18")
    private Integer age;
}
```

```java
@RestController
public class UserController {

    @PostMapping("/users")
    public ApiResponse<User> save(@Valid @RequestBody UserCreateRequest request) {
        User user = userService.save(request);
        return ApiResponse.success(user);
    }
}
```

### 分组校验

```java
public interface Create {
}
public interface Update {
}

@Data
public class UserRequest {
    @Null(groups = Create.class, message = "创建时ID必须为空")
    @NotNull(groups = Update.class, message = "更新时ID不能为空")
    private Long id;

    @NotBlank(groups = {Create.class, Update.class})
    private String username;
}
```

```java
@PostMapping("/users")
public ApiResponse<User> save(@Validated(Create.class) @RequestBody UserRequest request) {
    return ApiResponse.success(userService.save(request));
}
```

---

## 9. 拦截器

### 创建拦截器

```java
@Component
public class LoginInterceptor implements HandlerInterceptor {

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
        System.out.println("preHandle: 请求处理前");

        // 检查 token
        String token = request.getHeader("Authorization");
        if (token == null || !token.startsWith("Bearer ")) {
            response.setStatus(401);
            response.getWriter().write("未登录");
            return false;
        }

        return true;  // true 继续执行，false 中断
    }

    @Override
    public void postHandle(HttpServletRequest request, HttpServletResponse response, Object handler, ModelAndView modelAndView) throws Exception {
        System.out.println("postHandle: 请求处理后，视图渲染前");
    }

    @Override
    public void afterCompletion(HttpServletRequest request, HttpServletResponse response, Object handler, Exception ex) throws Exception {
        System.out.println("afterCompletion: 请求处理完成");
    }
}
```

### 注册拦截器

```java
@Configuration
public class WebMvcConfig implements WebMvcConfigurer {

    @Autowired
    private LoginInterceptor loginInterceptor;

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(loginInterceptor)
                .addPathPatterns("/api/**")      // 拦截的路径
                .excludePathPatterns(           // 不拦截的路径
                    "/api/login",
                    "/api/register",
                    "/api/public/**"
                );
    }
}
```

---

## 10. 跨域处理

### 方式一：@CrossOrigin

```java
@RestController
@CrossOrigin(origins = "http://localhost:3000")
public class UserController {

    @GetMapping("/users")
    public List<User> findAll() {
        return userService.findAll();
    }
}
```

### 方式二：全局配置

```java
@Configuration
public class CorsConfig implements WebMvcConfigurer {

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")
                .allowedOrigins("http://localhost:3000")
                .allowedMethods("GET", "POST", "PUT", "DELETE")
                .allowedHeaders("*")
                .allowCredentials(true)
                .maxAge(3600);
    }
}
```

---

## 11. 文件上传

```java
@RestController
public class FileController {

    @PostMapping("/upload")
    public String upload(@RequestParam("file") MultipartFile file) throws IOException {
        if (file.isEmpty()) {
            return "文件为空";
        }

        // 保存文件
        String filename = file.getOriginalFilename();
        String filePath = "/uploads/" + filename;
        file.transferTo(new File(filePath));

        return "上传成功: " + filename;
    }

    @PostMapping("/uploads")
    public List<String> uploads(@RequestParam("files") MultipartFile[] files) throws IOException {
        List<String> filenames = new ArrayList<>();
        for (MultipartFile file : files) {
            String filename = file.getOriginalFilename();
            file.transferTo(new File("/uploads/" + filename));
            filenames.add(filename);
        }
        return filenames;
    }
}
```

### 配置文件

```yaml
spring:
  servlet:
    multipart:
      enabled: true
      max-file-size: 10MB
      max-request-size: 100MB
```

---

## 12. RESTful API 规范

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/users | 查询所有 |
| GET | /api/users/{id} | 查询单个 |
| GET | /api/users?page=1&size=10 | 分页查询 |
| POST | /api/users | 新增 |
| PUT | /api/users/{id} | 完整更新 |
| PATCH | /api/users/{id} | 部分更新 |
| DELETE | /api/users/{id} | 删除 |

---

## 🎯 本节面试考点总结

| 考点 | 问题 | 关键点 |
|------|------|--------|
| 核心组件 | Spring MVC 核心组件？ | DispatcherServlet、HandlerMapping、HandlerAdapter、Controller、ViewResolver、View |
| 执行流程 | 请求处理流程？ | DispatcherServlet → HandlerMapping → HandlerAdapter → Controller → ViewResolver → View |
| @RequestMapping | 常用属性？ | value、method、params、headers、consumes、produces |
| 参数绑定 | 参数绑定注解？ | @PathVariable、@RequestParam、@RequestBody、@RequestHeader、@CookieValue |
| 返回值 | 返回值类型？ | String、void、ModelAndView、对象、ResponseEntity |
| 异常处理 | 全局异常处理？ | @ControllerAdvice + @ExceptionHandler |
| 拦截器 | 拦截器三个方法？ | preHandle、postHandle、afterCompletion |
| 跨域 | 跨域处理方式？ | @CrossOrigin、全局配置 |

---

## ✅ 课后练习

1. 实现完整的用户 CRUD 接口
2. 实现全局异常处理
3. 实现登录拦截器
4. 实现文件上传功能

```java
// 练习要求
// 项目名：springboot-mvc-demo
// 接口：
// - 用户管理 CRUD
// - 统一异常处理
// - 统一响应格式
// - 登录拦截器
// - 文件上传

---

## 📝 自测题

1. Spring MVC 的核心前端控制器是？\
   A. ViewResolver  B. HandlerMapping  C. DispatcherServlet  D. Controller
2. 获取 URL 路径 `/users/5` 中的 `5` 应该用哪个注解？\
   A. @RequestParam  B. @PathVariable  C. @RequestBody  D. @PathVariable("id")
3. 全局异常处理使用哪个注解？\
   A. @ExceptionHandler  B. @ControllerAdvice  C. @ResponseStatus  D. @RestControllerAdvice
4. HTTP 状态码 204 表示？\
   A. 创建成功  B. 请求成功  C. 无内容（删除成功）  D. 未授权

**答案：1-C, 2-B, 3-B, 4-C**

---

下一课：Spring Data JPA（→ `第六课-SpringDataJPA.md`）
```