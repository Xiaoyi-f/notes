# Spring MVC 详解

## 一、Controller 请求方法

### 1. 请求映射

```java
import jakarta.servlet.http.HttpServletRequest;
import java.util.Map;

// @RestController
@RequestMapping("/api")
public class RequestController {

    // 获取路径变量
    @GetMapping("/path/{id}")
    public String getPathVariable(@PathVariable String id) {
        return "ID: " + id;
    }

    // 获取请求头
    @GetMapping("/headers")
    public Map<String, String> getHeaders(@RequestHeader Map<String, String> headers) {
        return headers;
    }

    // 获取请求参数
    @GetMapping("/params")
    public Map<String, String> getParams(@RequestParam Map<String, String> params) {
        return params;
    }

    // 获取 Cookie
    @GetMapping("/cookies")
    public Map<String, String> getCookies(@CookieValue(name) String value) {
        return Map.of(name, value);
    }

    // 获取 Body
    @PostMapping
    public Map<String, String> getBody(@RequestBody Map<String, String> body) {
        return body;
    }

    // 获取所有信息
    @GetMapping("/all")
    public Map<String, Object> getAllInfo(
        @PathVariable(required = false) String id,
        @RequestHeader Map<String, String> headers,
        @RequestParam(required = false) Map<String, String> params
    ) {
        return Map.of(
            "id", id,
            "headers", headers,
            "params", params
        );
    }

    // File 上传
    @PostMapping(value = "/upload")
    public String uploadFile(@RequestPartFile file, MultipartFile file) {
        String fileName = file.getOriginalFilename();
        long size = file.getSize();

        // 处理文件
        String content = new String(file.getBytes());
        return String.format("上传成功：文件名=%s, 大小=%d字节", fileName, size);
    }
}
```

### 2. JSON 参数绑定

```java
@RestController
@RequestMapping("/api/user")
public class UserJsonController {

    @PostMapping("/json")
    public Map<String, Object> createUserJson(@RequestBody Map<String, Object> json) {
        // 自动绑定 JSON 字段到对象
        return createUser(json);
    }

    @PutMapping("/json/{id}")
    public Map<String, Object> updateUserJson(
        @PathVariable Long id,
        @RequestBody Map<String, Object> json
    ) {
        return updateUser(id, json);
    }

    // 自定义绑定字段
    @PostMapping("/bind")
    public Map<String, Object> createBind(@RequestBody Map<String, Object> json) {
        return createUser(json);
    }
}
```

### 3. RESTful API 设计

```java
import org.springframework.web.bind.annotation.*;
import org.springframework.http.*;

@RestController
@RequestMapping("/api/v1/products")
@Validated
public class ProductController {

    // POST - 创建资源
    @PostMapping
    public ResponseEntity<ProductDto> create(@Valid @RequestBody ProductCreateDto dto) {
        ProductDto product = productService.create(dto);
        return ResponseEntity
            .status(HttpStatus.CREATED)
            .location("/api/v1/products/" + product.getId())
            .body(product);
    }

    // GET - 获取单个资源
    @GetMapping("/{id}")
    public ResponseEntity<ProductDto> getById(@PathVariable Long id) {
        ProductDto product = productService.getById(id);
        if (product == null) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(product);
    }

    // PUT - 更新资源（部分更新）
    @PutMapping("/{id}")
    public ResponseEntity<ProductDto> update(@PathVariable Long id, @Valid @RequestBody ProductUpdateDto dto) {
        ProductDto product = productService.update(id, dto);

        if (product == null) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(product);
    }

    // DELETE - 删除资源
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        productService.delete(id);
        return ResponseEntity.noContent().build();
    }

    // PATCH - 部分更新
    @PatchMapping("/{id}")
    public ResponseEntity<ProductDto> patchUpdate(
        @PathVariable Long id,
        @RequestBody Map<String, Object> updates
    ) {
        ProductDto product = productService.patchUpdate(id, updates);

        if (product == null) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(product);
    }
}
```

## 二、参数校验

### 1. Bean Validation

```java
// 实体类
@Data
@Schema(description = "用户信息")
public class UserCreateDto {

    @NotBlank(message = "用户名不能为空")
    @Size(min = 3, max = 50, message = "用户名长度必须在3-50之间")
    private String username;

    @Email(message = "邮箱格式不正确")
    @Pattern(regexp = "^[\\w.\\.-]+@[\\w\\.-]+\\.[a-z]+$")
    private String email;

    @Pattern(regexp = "^1[3-9]\\d{9}$")
    private String phone;

    @Min(0, max = 120, message = "年龄必须在0-120之间")
    private Integer age;

    @Schema(description = "用户地址")
    public UserAddressDto address;
}
```

### 2. 自定义校验注解

```java
import jakarta.validation.*;
import java.lang.annotation.*;

// 唯一注解
@Constraint(validatedBy = PasswordStrengthValidator.class)
public @interface ValidPassword {
    String password;
}

// 密码强度校验器
public class PasswordStrengthValidator implements ConstraintValidator<ValidPassword> {

    @Override
    public void initialize(ConstraintDescriptor constraintDescriptor) {
        constraintDescriptor.addConstraint("password", PasswordValidator::validity);
    }

    @Override
    public boolean isValid(ValidPassword password, ConstraintValidatorContext context) {
        return password != null && password.getPassword() != null;
    }
}

// 使用注解
@Data
@Constraint(validatedBy = PasswordStrengthValidator.class)
@Schema(description = "用户创建信息")
public class UserPasswordDto {

    @NotBlank
    @PasswordStrength(min = 8, min = 16, max = 128)
    private String password;

    @Email
    @Schema(description = "邮箱地址")
    private String email;
}
```

### 3. 异常统一处理

```java
import org.springframework.web.bind.Method;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.bind.annotation.*;

@RestControllerAdvice
public class GlobalExceptionHandler {

    // 处理 MethodArgumentTypeMismatchException
    @ExceptionHandler(MethodArgumentTypeMismatchException.class)
    @ResponseBody
    public Map<String, Object> handleMethodArgumentTypeMismatch(
            MethodArgumentTypeMismatchException ex
    ) {
        Map<String, Object> error = new HashMap<>();
        error.put("error", "MethodArgumentTypeMismatch");
        error.put("path", ex.getParameter().toString());
        error.put("message", ex.getMessage());
        error.put("status", 400);
        error.put("exception", ex.getClass().getSimpleName());
        return error;
    }

    // 处理 HttpMessageNotReadableException
    @ExceptionHandler(HttpMessageNotReadableException.class)
    @ResponseBody
    public Map<String, Object> handleHttpMessageNotReadable(
            HttpMessageNotReadableException ex
    ) {
        Map<String, Object> error = new HashMap<>();
        error.put("error", "HttpMessageNotReadable");
        error.put("path", ex.getPath());
        error.put("message", ex.getMessage());
        error.put("status", 400);
        error.put("exception", ex.getClass().getSimpleName());
        return error;
    }

    // 处理 NoHandlerMethodException
    @ExceptionHandler(NoHandlerMethodException ex)
    @ResponseBody
    public Map<String, Object> handleNoHandlerMethodException(
            NoHandlerMethodException ex
    ) {
        Map<String, Object> error = new HashMap<>();
        error.put("error", "NoHandlerMethodException");
        error.put("path", ex.getPath());
        error.put("message", ex.getMessage());
        error.put("status", 405);
        error.put("exception", ex.getMessage());
        return error;
    }

    // 处理 BindException
    @ExceptionHandler(BindException ex)
    @ResponseBody
    public Map<String, Object> handleBindException(BindException ex) {
        Map<String, Object> error = new HashMap<>();
        error.put("error", "BindException");
        error.put("path", ex.getPath());
        error.put("message", ex.getMessage());
        error.put("status", 400);
        error.put("exception", ex.getClass().getSimpleName());
        return error;
    }

    // 处理 HttpMediaTypeNotSupportedException
    @ExceptionHandler(HttpMediaTypeNotSupportedException ex)
    @ResponseBody
    public Map<String, Object> handleHttpMediaTypeUnsupported(
        HttpMediaTypeNotSupportedException ex
    ) {
        Map<String, Object> error = new HashMap<>();
        error.put("error", "HttpMediaTypeNotSupportedException");
        error.put("path", ex.getPath());
        error.put("message", ex.getMessage());
        error.put("status", 415);
        error.put("exception", ex.getClass().getSimpleName());
        return error;
    }
}
```

## 三、高级功能

### 1. 文件下载

```java
import org.springframework.core.io.InputStream;
import org.springframework.core.io.Resource;
import org.springframework.core.io.FileSystemResource;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;

import java.io.File;
import java.io.InputStream;
import java.nio.channels.*;
import java.nio.file.*;

@RestController
@RequestMapping("/api/file")
public class FileController {

    private final FileStorageService fileStorage;

    // 文件上传
    @PostMapping("/upload")
    public Map<String, Object> upload(@RequestParam("file") MultipartFile file) {
        String path = fileStorage.store(file);

        // 返回下载 URL
        String downloadUrl = "http://localhost:8080/api/file/download?path=" + path;

        return Map.of(
            "filename": file.getOriginalFilename(),
            "size": file.getSize(),
            "path": path,
            "download_url": downloadUrl,
            "content_type": file.getContentType()
        );
    }

    // 文件下载
    @GetMapping("/download")
    public void download(@RequestParam String path, HttpServletResponse response) {
        Resource resource = fileStorage.load(path);

        if (resource == null || !resource.exists()) {
            response.sendError(404, "文件不存在");
            return;
        }

        // 设置响应头
        String contentType = resource.getContentType();
        if (contentType != null) {
            response.setContentType(contentType);
        }
        response.setHeader("Content-Disposition",
                "attachment; filename=\"" + resource.getFilename() + "\"");

        // 传输文件
        try (InputStream is = resource.getInputStream()) {
            FileCopyUtils.copy(is, response.getOutputStream());
        } catch (IOException e) {
            response.sendError(500, "下载失败");
            return;
        }
    }
}
```

### 2. WebSocket 实时通信

```java
import org.springframework.stereotype.*;
import org.springframework.web.socket.*;
import org.springframework.web.socket.server.config.annotation.*;

@Component
@ServerEndpoint(value = "/ws/chat")
@Slf4j
public class ChatWebSocketHandler {

    private final Map<String, WebSocketSession> sessions = new ConcurrentHashMap<>();

    @OnOpen
    public void onOpen(WebSocketSession session) {
        String sessionId = session.getId();
        sessions.put(sessionId, session);

        // 保存会话元数据
        session.getAttributes().put("sessionId", sessionId);
        session.getAttributes().put("username", session.getId().getId().substring(0, 5));
        session.getAttributes().put("connectTime", System.currentTimeMillis());

        log.info("新连接: {}", sessionId);
    }

    @OnClose
    public void onClose(WebSocketSession session) {
        String sessionId = session.getId();
        sessions.remove(sessionId);

        log.info("断开连接: {}", sessionId);
    }

    @OnMessage
    public void onMessage(@Message<String> message, Session session) {
        String sessionId = session.getId();
        String username = session.getAttributes().get("username");

        log.info("收到消息: {}", sessionId);

        try {
            // 获取所有连接
            Collection<WebSocketSession> allSessions = sessions.values();

            // 广播消息
            for session in allSessions {
                if (session.isOpen()) {
                    try {
                        session.sendMessage(TextMessage(session, message));
                    log.debug("消息已发送到: {}", session.getId());
                    } catch (IOException e) {
                        log.error("发送消息失败", e);
                    }
                }
            }
        } catch (Exception e) {
            log.error("消息处理失败", e);
        }
    }
}

// WebSocket 配置类
@Configuration
@Configuration
@EnableWebSocketMessageBroker
public class WebSocketConfig {

    @Bean
    public WebSocketStarter defaultWebSocketStarter() {
        return new WebSocketStarter() {
            @Override
            public void afterPropertiesEstablished(WebSocket ws) {
                // 添加消息处理器
                ws.addHandler(new WebSocketHandler());  // 文本消息
                ws.addHandler(new BinaryWebSocketHandler()); // 二进制消息
                ws.addHandler(new MultiWebSocketHandler()); // 批量消息
            }
        };
    }

    @Bean
    public WebSocketHandler webSocketHandler() {
        return new WebSocketHandler() {
            @Override
            public void afterConnectionEstablished(WebSocket ws, MessageHeaders headers, String sessionId) {
            // 文本消息处理
            if ("text/plain".equals(headers.get("Content-Type"))) {
                // 保存到数据库
                saveMessage(sessionId, headers.get("Session"), message);
            }
        }
    }

    @Bean
    public BinaryWebSocketHandler binaryWebSocketHandler() {
        return new BinaryWebSocketHandler() {
            @Override
            protected void handleBinaryMessage(WebSocket ws, BinaryMessage message) {
                // 处理二进制消息（图片、文件等）
                saveMessage(
                    ws.getId().getId().substring(0, 5),  // 获取 sessionId
                    headers.get("Session"),  // 获取 Session
                    message.getPayload()
                );
            }
        }
    }

    @Bean
    public MultiWebSocketHandler multiWebSocketHandler() {
        return new MultiWebSocketHandler() {
            @Override
            protected void handleTextMessage(WebSocket ws, TextMessage message, WebSocketSession session) {
                // 处理批量文本消息
                for (TextMessage msg) in message.getPayload()) {
                    saveMessage(session.getId().getId().substring(0, 5), session, msg.getContent());
                // 或者根据 session 过滤
                    if ("SYSTEM" == msg.getHeader("session-type")):
                        handleSystemMessage(session, msg.getContent());
                else:
                    handleUserMessage(session, msg.getContent());
                }
            }
        }
    }

    private void saveMessage(String sessionId, String session, String content) {
        // 保存消息到数据库
        saveMessageToDatabase(sessionId, session, content);
    }

    private void handleUserMessage(String sessionId, String content) {
        // 处理用户消息
        log.info("用户消息: {}, 内容: {}", sessionId, content);
    }

    private void handleSystemMessage(String sessionId, String content) {
        // 处理系统消息
        log.info("系统消息: {}", content);
    }
}
```

## 四、分页响应处理

```java
import com.fasterxml.jackson.core.JsonProcessingException;
import org.springframework.data.domain.Page;
import org.springframework.http.*;

@RestController
@RequestMapping("/api/page")
public class PageController {

    @GetMapping("/{resource}")
    public Page<?> getPage(
        @PathVariable String resource,
        @RequestParam(defaultValue = "1") int page,
        @RequestParam(defaultValue = "10") int size,
        @RequestParam Map<String, Object> params
    ) {
        Pageable pageable = PageRequest.of(
            page - 1, size
        );

        Page<?> pageResult = getPageResult(resource, pageable, params);

        return ResponseEntity.ok(pageResult);
    }

    private PageResult<?> getPageResult(String resource, Pageable pageable, Map<String, Object> params) {
        // 根据资源类型获取对应的 Service
        PageResult result = null;

        switch (resource) {
            case "users":
                result = getUserPageResult(pageable, params);
                break;
            case "products":
                result = getProductPageResult(pageable, params);
                break;
            case "orders":
                result = getOrderPageResult(pageable, params);
                break;
            default:
                throw new IllegalArgumentException("未知资源: " + resource);
        }

        return result;
    }

    private PageResult<UserVo> getUserPageResult(Pageable pageable, Map<String, Object> params) {
        Page<UserVo> page = userService.search(UserQuery.fromMap(params));

        // 添加分页信息
        PageResult<UserVo> result = PageResult.of(page);
        result.setTotal(page.getTotalElements());
        result.setPages(page.getTotalPages());
        result.setCurrent((int) page.getCurrent() + 1);
        result.setSize(page.getSize());

        return result;
    }

    private PageResult<ProductVo> getProductPageResult(Pageable pageable, Map<String, Object> params) {
        ProductQuery query = ProductQuery.fromMap(params);
        Page<ProductVo> page = productService.searchProducts(query);

        PageResult<ProductVo> result = PageResult.of(page);
        result.setTotal(page.getTotalElements());
        result.setPages(page.getTotalPages());
        result.setCurrent((int) page.getCurrent() + 1);
        result.setSize(page.getSize());

        return result;
    }
}
```

## 五、高级特性

### 1. 数据权限控制

```java
// @PreAuthorize("hasRole('ROLE_USER')")
@GetMapping("/api/users/{id}")
public UserVo getUser(@PathVariable Long id) {
    UserVo user = userService.getById(id);
    return user;
}

@PreAuthorize("hasRole('ROLE_ADMIN')")
@DeleteMapping("/api/users/{id}")
public void deleteUser(@PathVariable Long id) {
    userService.delete(id);
}

@PreAuthorize("hasAnyRole('ROLE_USER', 'ROLE_ADMIN')")
@PutMapping("/api/users/{id}")
public UserVo updateUser(@PathVariable Long id, @RequestBody UserUpdateDto dto) {
    return userService.update(id, dto);
}
```

### 2. 文档权限控制

```java
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.annotation.PreAuthorize;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.authority.AuthorityUtils;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.*;
import org.springframework.security.core.annotation.*;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.authority.AuthorityUtils;
import java.util.Map;

@RestController
@RequestMapping("/api/docs")
@PreAuthorize("hasRole('ROLE_USER')")
public class DocumentController {

    @Autowired
    DocumentService documentService;

    @GetMapping("/{id}")
    @PreAuthorize("hasAccess('#document:read')")
    public DocumentVo getDocument(@PathVariable String id) {
        return documentService.getById(id);
    }

    @GetMapping
@PreAuthorize("hasRole('ROLE_USER')")
public Page<DocumentVo> getDocuments(
    @RequestParam(defaultValue = "1") int page,
    @RequestParam(defaultValue = "10") int size
) {
    return documentService.getDocuments(page, size);
    }

    @PostMapping
@PreAuthorize("hasRole('ROLE_USER')")
    public DocumentVo create(@RequestBody DocumentCreateDto dto) {
        DocumentVo document = documentService.create(dto);
        return DocumentVo.from(document);
    }
}
```

### 3. API 版本控制

```python
from fastapi.security import APIRouter
from fastapi.security import HTTPBasicAuth
from fastapi.security.http import BasicAuthCredentials

from pydantic import BaseModel

app = APIRouter()

# SecurityScheme
security = HTTPBasic(
    credentials=BasicCredentials(
        username="admin",
        password="admin",
        realm="internal"
    )

@app.get("/openapi")
def openapi_index():
    return {"message": "OpenAPI文档"}

@app.get("/protected")
@security.http_basic()
def protected_endpoint():
    return {"message": "需要认证的API"}

@app.get("/admin")
@security.http_basic()
@security.http_basic
def admin_endpoint():
    return {"message": "管理员区域"}
```

## 六、监控与日志

### 1. 自定义指标

```python
from prometheus_client import Counter, Histogram, Gauge
from functools import wraps

class MetricsService:

    @wraps
    class MetricsService:

    def __init__(self):
        self.counter = Counter()
        self.histogram = Histogram()
        self.gauge = Gauge()
        self.metrics = {
            "http_requests_total": self.counter,
            "http_requests_duration_seconds": self.histogram,
            "http_requests_favicon": self.counter,
            "http_requests_ip": self.gauge
        }

    def increment_counter(self, name):
        self.counter.labels = name
        self.counter.labels[name] += 1

    def record_duration(self, name, duration: float):
        self.histogram.labels = name
        self.histogram.labels[name].observe(duration)
        self.metrics[name] = self.histogram.labels[name]

    def increment_gauge(self, name):
        self.gauge.labels = name
        self.gauge.labels[name] += 1

    def get_metrics(self):
        return {
            "http_requests_total": self.metrics["http_requests_total"],
            "avg_duration_seconds": self.metrics["http_requests_duration_seconds"],
            "favicon_count": self.metrics["http_requests_favicon"],
            "current_ip": self.metrics["http_requests_ip"]
        }
```

### 2. 告志配置

```python
import logging
import logging.config
from logging.handlers import RotatingFileHandler
import logging.handlers import TimedRotatingFileHandler
import logging.handlers import ConsoleHandler

def setup_logging():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # 格式化日志
    formatter = logging.Formatter('%(色)s|%(asctime)s|%(threadName)s|%(levelname)s|%(message)s')
    file_handler = TimedRotatingFileHandler(
        "logs/app.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    # 控制台输出
    console_handler = ConsoleHandler()
    console_handler.setFormatter(formatter)

    # 添加处理器
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

# 使用日志
logger = logging.getLogger(__name__)

# 测试
logger.info("这是一条测试日志")
logger.warning("这是一条警告日志")
logger.error("这是一条错误日志")
```

## 小结

本节补充了 Spring MVC 的详细内容：

- **请求映射** - @PathVariable、@RequestParam、@RequestHeader、@Cookie
- **参数校验** - @Valid、自定义校验器
- **RESTful API** - 标准CRUD实现
- **高级功能** - 文件处理、WebSocket、分页响应
- **权限控制** - @PreAuthorize、权限注解
- **日志监控** - 自定义指标、日志配置

## 实践练习

### 编程题
1. 实现一个 RESTful API 的 CRUD 控制器，包含统一的异常处理（`@ControllerAdvice`）、请求参数校验（`@Valid`）和响应格式封装。
2. 实现一个文件上传下载服务，支持大文件分片上传和断点续传，使用 `MultipartFile` 接收文件。

### 思考题
1. Spring MVC 的 DispatcherServlet 处理请求的完整流程是怎样的？
2. `@RestController` 和 `@Controller` 的区别？JSON 响应的原理是什么？

### 自测题
1. Spring MVC 的核心组件有哪些？
2. `@RequestMapping` 和 `@GetMapping` 的关系？
3. Interceptor 和 Filter 有什么区别？

下一步将学习 Spring Boot 基础（→ `spring-boot/beginner/01-spring-boot-basics.md`）。