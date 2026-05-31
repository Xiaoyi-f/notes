# JavaWeb 进阶开发

## 一、概述

在 Servlet/JSP 基础上，深入 JavaWeb 核心技术：Filter、Listener、文件上传下载、Session 集群、跨域处理。

## 二、Filter 过滤器

### 执行流程

```
请求 → Filter1.doFilter() → Filter2.doFilter() → Servlet.service()
                                                      ↓
响应 ← Filter1.doFilter() ← Filter2.doFilter() ← Servlet.service()
```

### 过滤器链

```java
@WebFilter("/*")
public class LoggingFilter implements Filter {
    @Override
    public void init(FilterConfig config) {
        System.out.println("LoggingFilter initialized");
    }

    @Override
    public void doFilter(ServletRequest req, ServletResponse resp, 
                         FilterChain chain) throws IOException, ServletException {
        HttpServletRequest request = (HttpServletRequest) req;
        long start = System.currentTimeMillis();
        
        // 请求前
        log.info("Request: {} {}", request.getMethod(), request.getRequestURI());
        
        chain.doFilter(req, resp);  // 放行
        
        // 响应后
        long duration = System.currentTimeMillis() - start;
        log.info("Completed in {} ms", duration);
    }

    @Override
    public void destroy() { }
}
```

### 常见 Filter 场景

| Filter | 用途 | 注意事项 |
|--------|------|----------|
| CharacterEncodingFilter | 统一编码 UTF-8 | 放在 Filter 链最前面 |
| LoginFilter | 登录校验 | 排除 login/static 路径 |
| RateLimitFilter | 接口限流 | 基于令牌桶/滑动窗口 |
| CORSFilter | 跨域支持 | 配置允许的来源和方法 |
| XSSFilter | XSS 过滤 | 对输入参数做 HTML 转义 |

```java
// 登录校验 Filter
@WebFilter(value = "/*", initParams = {
    @WebInitParam(name = "excludePaths", value = "/login,/register,/static/*,/api/public/*")
})
public class AuthFilter implements Filter {
    private List<AntPathMatcher> excludePaths = new ArrayList<>();

    @Override
    public void init(FilterConfig config) {
        String paths = config.getInitParameter("excludePaths");
        for (String path : paths.split(",")) {
            excludePaths.add(new AntPathMatcher(path.trim()));
        }
    }

    @Override
    public void doFilter(ServletRequest req, ServletResponse resp, FilterChain chain) {
        HttpServletRequest request = (HttpServletRequest) req;
        String path = request.getRequestURI();
        
        // 白名单放行
        if (isExcluded(path)) {
            chain.doFilter(req, resp);
            return;
        }
        // 校验 Session
        HttpSession session = request.getSession(false);
        if (session == null || session.getAttribute("user") == null) {
            ((HttpServletResponse) resp).sendRedirect("/login");
            return;
        }
        chain.doFilter(req, resp);
    }
}
```

## 三、Listener 监听器

```java
// ServletContext 生命周期监听
@WebListener
public class ApplicationListener implements ServletContextListener {
    @Override
    public void contextInitialized(ServletContextEvent sce) {
        // 加载全局配置
        ServletContext ctx = sce.getServletContext();
        ctx.setAttribute("appName", "MyApp");
        ctx.setAttribute("startTime", System.currentTimeMillis());
    }

    @Override
    public void contextDestroyed(ServletContextEvent sce) {
        // 释放资源
        System.out.println("Application shutting down");
    }
}

// Session 监听 - 在线用户统计
@WebListener
public class OnlineUserListener implements HttpSessionListener {
    private static final AtomicInteger onlineCount = new AtomicInteger(0);

    @Override
    public void sessionCreated(HttpSessionEvent se) {
        onlineCount.incrementAndGet();
    }

    @Override
    public void sessionDestroyed(HttpSessionEvent se) {
        onlineCount.decrementAndGet();
    }

    public static int getOnlineCount() {
        return onlineCount.get();
    }
}
```

## 四、文件上传与下载

### 上传

```java
@WebServlet("/upload")
@MultipartConfig(
    location = "/tmp",
    maxFileSize = 10 * 1024 * 1024,      // 单个文件 10MB
    maxRequestSize = 50 * 1024 * 1024,    // 总请求 50MB
    fileSizeThreshold = 5 * 1024 * 1024   // 超过 5MB 写入磁盘
)
public class FileUploadServlet extends HttpServlet {
    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) 
            throws IOException {
        String uploadDir = "/data/uploads/" + LocalDate.now();
        Files.createDirectories(Path.of(uploadDir));

        for (Part part : req.getParts()) {
            String fileName = getFileName(part);
            if (fileName == null || fileName.isEmpty()) continue;
            
            // 防重名
            String uniqueName = UUID.randomUUID() + "_" + fileName;
            part.write(uploadDir + "/" + uniqueName);
        }
        resp.getWriter().write("Upload success");
    }

    private String getFileName(Part part) {
        String cd = part.getHeader("content-disposition");
        for (String token : cd.split(";")) {
            if (token.trim().startsWith("filename")) {
                return token.substring(token.indexOf('=') + 2, token.length() - 1);
            }
        }
        return null;
    }
}
```

### 下载

```java
@WebServlet("/download")
public class FileDownloadServlet extends HttpServlet {
    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) 
            throws IOException {
        String filePath = "/data/uploads/" + req.getParameter("file");
        File file = new File(filePath);
        if (!file.exists()) {
            resp.sendError(404, "File not found");
            return;
        }
        resp.setContentType("application/octet-stream");
        resp.setHeader("Content-Disposition", 
            "attachment; filename=" + URLEncoder.encode(file.getName(), "UTF-8"));
        resp.setContentLengthLong(file.length());

        try (InputStream is = new FileInputStream(file);
             OutputStream os = resp.getOutputStream()) {
            IOUtils.copy(is, os);
        }
    }
}
```

## 五、Session 集群方案

### Redis Session 共享

```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.springframework.session</groupId>
    <artifactId>spring-session-data-redis</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>
```

```java
@Configuration
@EnableRedisHttpSession(maxInactiveIntervalInSeconds = 1800)
public class SessionConfig {
    @Bean
    public LettuceConnectionFactory redisConnectionFactory() {
        return new LettuceConnectionFactory("redis-master", 6379);
    }
}
```

### Session 策略对比

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| Sticky Session | 实现简单 | 节点宕机丢失会话 | 小型集群 |
| Redis 共享 | 高可用、无单点 | 增加 RT | 中小型应用 |
| JWT Token | 无状态 | 无法主动吊销 | REST API |
| 数据库共享 | 持久化 | 性能差 | 已不推荐 |

## 六、跨域处理 (CORS)

```java
@WebFilter("/api/*")
public class CORSFilter implements Filter {
    @Override
    public void doFilter(ServletRequest req, ServletResponse resp, FilterChain chain) {
        HttpServletResponse response = (HttpServletResponse) resp;
        response.setHeader("Access-Control-Allow-Origin", "https://admin.example.com");
        response.setHeader("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS");
        response.setHeader("Access-Control-Allow-Headers", "Content-Type,Authorization");
        response.setHeader("Access-Control-Max-Age", "3600");
        response.setHeader("Access-Control-Allow-Credentials", "true");

        if ("OPTIONS".equalsIgnoreCase(((HttpServletRequest) req).getMethod())) {
            response.setStatus(HttpServletResponse.SC_OK);
            return;
        }
        chain.doFilter(req, resp);
    }
}
```

## 课后练习

1. 实现一个 IP 限流 Filter，每分钟每个 IP 最多 60 次请求
2. 基于 SessionListener 实现当前在线用户列表 API
3. 实现断点续传下载（支持 Range 头）
4. 将 JWT 登录校验集成到 Filter 中

## 自测题

1. Filter 的执行顺序由什么决定？ A) Filter 名称 B) web.xml 中的顺序 C) @Order 注解 D) 随机
2. ServletContextListener 的触发时机？ A) 每次请求 B) 应用启动/关闭 C) Session 创建 D) JSP 编译
3. @MultipartConfig 的 maxFileSize 默认为？ A) 1MB B) 无限 C) -1L D) 10MB

**答案：** 1-B, 2-B, 3-C
