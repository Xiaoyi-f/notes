# JavaWeb 高级框架与架构

## 一、概述

从原生 Servlet 过渡到框架时代：掌握 Spring MVC 核心源码、RESTful 最佳实践、接口规范设计、API 版本管理。

## 二、Spring MVC 核心源码分析

### DispatcherServlet 处理流程

```
1. 请求到达 DispatcherServlet
2. HandlerMapping 查找 Handler（@RequestMapping）
3. HandlerAdapter 执行 Handler（参数解析、调用方法）
4. HandlerInterceptor preHandle → 业务方法 → postHandle
5. ViewResolver 解析视图 / @ResponseBody 直接输出
6. HandlerInterceptor afterCompletion
```

### 自定义参数解析器

```java
@Target(ElementType.PARAMETER)
@Retention(RetentionPolicy.RUNTIME)
public @interface CurrentUser {
    boolean required() default true;
}

public class CurrentUserArgumentResolver implements HandlerMethodArgumentResolver {
    @Override
    public boolean supportsParameter(MethodParameter parameter) {
        return parameter.hasParameterAnnotation(CurrentUser.class)
            && parameter.getParameterType().equals(UserVO.class);
    }

    @Override
    public Object resolveArgument(MethodParameter parameter, ModelAndViewContainer mavContainer,
                                  NativeWebRequest webRequest, WebDataBinderFactory binderFactory) {
        HttpServletRequest request = (HttpServletRequest) webRequest.getNativeRequest();
        String token = request.getHeader("Authorization");
        if (token == null || token.isEmpty()) {
            CurrentUser annotation = parameter.getParameterAnnotation(CurrentUser.class);
            if (annotation != null && annotation.required()) {
                throw new UnauthorizedException("User not authenticated");
            }
            return null;
        }
        return userService.getUserFromToken(token);
    }
}
```

### RESTful API 设计规范

```java
@RestController
@RequestMapping("/api/v1/users")
public class UserController {

    @GetMapping
    public ApiResult<PageResult<UserVO>> list(@PageableDefault Pageable pageable,
                                               @RequestParam(required = false) String keyword) {
        return ApiResult.success(userService.listUsers(pageable, keyword));
    }

    @GetMapping("/{id}")
    public ApiResult<UserVO> detail(@PathVariable Long id) {
        return ApiResult.success(userService.getUser(id));
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public ApiResult<UserVO> create(@Valid @RequestBody UserCreateRequest request) {
        return ApiResult.success(userService.createUser(request));
    }

    @PutMapping("/{id}")
    public ApiResult<UserVO> update(@PathVariable Long id, @Valid @RequestBody UserUpdateRequest request) {
        return ApiResult.success(userService.updateUser(id, request));
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void delete(@PathVariable Long id) {
        userService.deleteUser(id);
    }
}
```

## 三、接口设计模式

### 统一响应体

```java
public class ApiResult<T> {
    private int code;
    private String message;
    private T data;
    private long timestamp;

    private ApiResult(int code, String message, T data) {
        this.code = code;
        this.message = message;
        this.data = data;
        this.timestamp = System.currentTimeMillis();
    }

    public static <T> ApiResult<T> success(T data) {
        return new ApiResult<>(200, "success", data);
    }

    public static <T> ApiResult<T> error(int code, String message) {
        return new ApiResult<>(code, message, null);
    }
}

// 全局异常处理
@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ApiResult<Void> handleValidation(MethodArgumentNotValidException e) {
        String message = e.getBindingResult().getFieldErrors().stream()
            .map(f -> f.getField() + ": " + f.getDefaultMessage())
            .collect(Collectors.joining(", "));
        return ApiResult.error(400, message);
    }

    @ExceptionHandler(BusinessException.class)
    public ApiResult<Void> handleBusiness(BusinessException e) {
        return ApiResult.error(e.getCode(), e.getMessage());
    }

    @ExceptionHandler(Exception.class)
    public ApiResult<Void> handleException(Exception e) {
        log.error("Unhandled exception", e);
        return ApiResult.error(500, "Internal server error");
    }
}
```

### API 版本管理

```java
@Target({ElementType.TYPE, ElementType.METHOD})
@Retention(RetentionPolicy.RUNTIME)
public @interface APIVersion {
    String value() default "1.0";
}

// 基于 Header 的版本路由
public class VersionRequestMappingHandlerMapping extends RequestMappingHandlerMapping {
    @Override
    protected RequestCondition<?> getCustomTypeCondition(Class<?> handlerType) {
        APIVersion version = handlerType.getAnnotation(APIVersion.class);
        return version != null ? new VersionRequestCondition(version.value()) : null;
    }

    @Override
    protected RequestCondition<?> getCustomMethodCondition(Method method) {
        APIVersion version = method.getAnnotation(APIVersion.class);
        return version != null ? new VersionRequestCondition(version.value()) : null;
    }
}

public class VersionRequestCondition implements RequestCondition<VersionRequestCondition> {
    private final String version;

    public VersionRequestCondition(String version) {
        this.version = version;
    }

    @Override
    public VersionRequestCondition combine(VersionRequestCondition other) {
        return new VersionRequestCondition(other.version);
    }

    @Override
    public VersionRequestCondition getMatchingCondition(HttpServletRequest request) {
        String header = request.getHeader("X-API-Version");
        if (header != null && header.equals(version)) {
            return this;
        }
        return null;
    }

    @Override
    public int compareTo(VersionRequestCondition other, HttpServletRequest request) {
        return other.version.compareTo(this.version);
    }
}
```

## 四、接口安全防护

### 防重放攻击

```java
@Component
public class NonceInterceptor implements HandlerInterceptor {
    private final RedisTemplate<String, String> redisTemplate;
    private static final Duration NONCE_TTL = Duration.ofMinutes(5);

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {
        String nonce = request.getHeader("X-Nonce");
        String timestamp = request.getHeader("X-Timestamp");

        if (nonce == null || timestamp == null) {
            throw new SecurityException("Missing nonce or timestamp");
        }
        // 检查时间戳偏差（最多5分钟）
        long requestTime = Long.parseLong(timestamp);
        if (Math.abs(System.currentTimeMillis() - requestTime) > 300_000) {
            throw new SecurityException("Request expired");
        }
        // 检查 nonce 是否已使用（Redis SETNX）
        Boolean isNew = redisTemplate.opsForValue()
            .setIfAbsent("nonce:" + nonce, "used", NONCE_TTL);
        if (Boolean.FALSE.equals(isNew)) {
            throw new SecurityException("Nonce already used");
        }
        return true;
    }
}
```

### 接口签名校验

```java
public class ApiSignUtil {
    public static String generateSign(Map<String, String> params, String secret) {
        String sorted = params.entrySet().stream()
            .sorted(Map.Entry.comparingByKey())
            .map(e -> e.getKey() + "=" + e.getValue())
            .collect(Collectors.joining("&"));
        String raw = sorted + "&key=" + secret;
        return DigestUtils.md5DigestAsHex(raw.getBytes(StandardCharsets.UTF_8)).toUpperCase();
    }

    public static boolean verifySign(Map<String, String> params, String sign, String secret) {
        String expected = generateSign(params, secret);
        return expected.equals(sign);
    }
}
```

## 课后练习

1. 实现一个自定义 HandlerMethodReturnValueHandler，自动包装返回值为 ApiResult
2. 基于 Filter 实现 API 签名校验中间件
3. 实现接口级权限注解 @RequirePermission，支持 SpEL
4. 设计一个多版本并存的 Controller 方案（URL Path 版本 vs Header 版本）

## 自测题

1. DispatcherServlet 中为 Controller 方法注入参数的是？ A) HandlerMapping B) HandlerAdapter C) ViewResolver D) HandlerExceptionResolver
2. @RestControllerAdvice 相当于哪两个注解的组合？ A) @ControllerAdvice + @ResponseBody B) @Component + @ControllerAdvice C) @Controller + @ResponseBody D) @ExceptionHandler + @ResponseBody
3. Nonce 防重放的原理是？ A) 加密请求 B) 一次性令牌去重 C) IP 限制 D) 频率限制

**答案：** 1-B, 2-A, 3-B
