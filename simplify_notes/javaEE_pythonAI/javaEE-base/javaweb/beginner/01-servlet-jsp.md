# JavaWeb 基础

## 一、Servlet 基础

### 1. Servlet 生命周期

```java
import jakarta.servlet.*;
import jakarta.servlet.annotation.*;
import jakarta.servlet.http.*;
import java.io.IOException;

@WebServlet(name = "HelloServlet", urlPatterns = "/hello")
public class HelloServlet extends HttpServlet {

    // 初始化方法（容器启动时调用一次）
    @Override
    public void init(ServletConfig config) throws ServletException {
        System.out.println("Servlet 初始化");
        super.init(config);
    }

    // 处理 GET 请求
    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        resp.setContentType("text/html;charset=UTF-8");
        resp.getWriter().write("<h1>Hello, GET!</h1>");
    }

    // 处理 POST 请求
    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        String name = req.getParameter("name");
        resp.setContentType("text/html;charset=UTF-8");
        resp.getWriter().write("<h1>Hello, " + name + "!</h1>");
    }

    // 销毁方法（容器关闭时调用）
    @Override
    public void destroy() {
        System.out.println("Servlet 销毁");
    }
}
```

### 2. 请求和响应

```java
@WebServlet("/request")
public class RequestServlet extends HttpServlet {

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {

        // 获取请求参数
        String name = req.getParameter("name");
        String[] hobbies = req.getParameterValues("hobby");

        // 获取请求头
        String userAgent = req.getHeader("User-Agent");
        String acceptLanguage = req.getHeader("Accept-Language");

        // 获取请求方式
        String method = req.getMethod();

        // 获取请求URL
        String requestURL = req.getRequestURL().toString();
        String requestURI = req.getRequestURI();
        String contextPath = req.getContextPath();
        String servletPath = req.getServletPath();

        // 获取远程地址
        String remoteAddr = req.getRemoteAddr();
        int remotePort = req.getRemotePort();

        // 获取会话
        HttpSession session = req.getSession();
        session.setAttribute("timestamp", System.currentTimeMillis());

        // 设置请求属性
        req.setAttribute("username", "admin");

        // 转发
        // req.getRequestDispatcher("/target").forward(req, resp);

        // 重定向
        // resp.sendRedirect("/other");

        // 设置响应
        resp.setContentType("text/html;charset=UTF-8");
        resp.setCharacterEncoding("UTF-8");

        PrintWriter writer = resp.getWriter();
        writer.write("<html><body>");
        writer.write("<h1>请求信息</h1>");
        writer.write("<p>方式: " + method + "</p>");
        writer.write("<p>URL: " + requestURL + "</p>");
        writer.write("<p>URI: " + requestURI + "</p>");
        writer.write("<p>上下文路径: " + contextPath + "</p>");
        writer.write("<p>Servlet路径: " + servletPath + "</p>");
        writer.write("<p>客户端IP: " + remoteAddr + "</p>");
        writer.write("</body></html>");
    }
}
```

### 3. 会话管理

```java
@WebServlet("/session")
public class SessionServlet extends HttpServlet {

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {

        // 获取或创建会话
        HttpSession session = req.getSession(true);

        // 设置会话属性
        session.setAttribute("username", "张三");
        session.setAttribute("loginTime", new Date());

        // 获取会话ID
        String sessionId = session.getId();

        // 获取会话创建时间
        long creationTime = session.getCreationTime();

        // 获取最后访问时间
        long lastAccessedTime = session.getLastAccessedTime();

        // 获取最大不活动时间（秒）
        int maxInactiveInterval = session.getMaxInactiveInterval();

        // 使会话失效
        // session.invalidate();

        // 设置Cookie
        Cookie cookie = new Cookie("theme", "dark");
        cookie.setMaxAge(60 * 60 * 24 * 7);  // 7天
        cookie.setPath("/");
        resp.addCookie(cookie);

        resp.setContentType("text/html;charset=UTF-8");
        resp.getWriter().write("""
            <html>
            <body>
                <h1>会话信息</h1>
                <p>会话ID: %s</p>
                <p>创建时间: %s</p>
                <p>最后访问: %s</p>
                <p>最大空闲: %d秒</p>
            </body>
            </html>
            """.formatted(sessionId, new Date(creationTime),
                new Date(lastAccessedTime), maxInactiveInterval));
    }
}
```

### 4. 文件上传

```java
@WebServlet("/upload")
@MultipartConfig(
    fileSizeThreshold = 1024 * 1024,      // 1MB
    maxFileSize = 1024 * 1024 * 10,         // 10MB
    maxRequestSize = 1024 * 1024 * 100,     // 100MB
    location = "/tmp/uploads"                 // 上传目录
)
public class UploadServlet extends HttpServlet {

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {

        req.setCharacterEncoding("UTF-8");

        // 获取上传的文件
        Part part = req.getPart("file");

        if (part == null || part.getSize() == 0) {
            resp.setContentType("text/html;charset=UTF-8");
            resp.getWriter().write("<script>alert('请选择文件');window.history.back();</script>");
            return;
        }

        // 获取文件信息
        String fileName = part.getSubmittedFileName();
        String contentType = part.getContentType();
        long fileSize = part.getSize();

        // 生成唯一文件名
        String extension = fileName.substring(fileName.lastIndexOf("."));
        String uniqueFileName = UUID.randomUUID().toString() + extension;

        // 保存文件
        String uploadPath = getServletContext().getRealPath("/uploads");
        File uploadDir = new File(uploadPath);
        if (!uploadDir.exists()) {
            uploadDir.mkdirs();
        }

        String filePath = uploadPath + File.separator + uniqueFileName;
        part.write(filePath);

        // 响应
        resp.setContentType("text/html;charset=UTF-8");
        resp.getWriter().write("""
            <html>
            <body>
                <h1>上传成功</h1>
                <p>文件名: %s</p>
                <p>类型: %s</p>
                <p>大小: %d 字节</p>
                <img src="/uploads/%s" style="max-width: 200px;">
            </body>
            </html>
            """.formatted(fileName, contentType, fileSize, uniqueFileName));
    }

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {

        resp.setContentType("text/html;charset=UTF-8");
        resp.getWriter().write("""
            <html>
            <body>
                <h1>文件上传</h1>
                <form action="upload" method="post" enctype="multipart/form-data">
                    <input type="file" name="file" required>
                    <button type="submit">上传</button>
                </form>
            </body>
            </html>
            """);
    }
}
```

### 5. 过滤器

```java
// 字符编码过滤器
@WebFilter(urlPatterns = "/*")
public class EncodingFilter implements Filter {

    private String encoding = "UTF-8";

    @Override
    public void init(FilterConfig filterConfig) {
        String encodingParam = filterConfig.getInitParameter("encoding");
        if (encodingParam != null) {
            encoding = encodingParam;
        }
    }

    @Override
    public void doFilter(ServletRequest request, ServletResponse response,
                           FilterChain chain) throws IOException, ServletException {

        request.setCharacterEncoding(encoding);
        response.setCharacterEncoding(encoding);
        response.setContentType("text/html;charset=" + encoding);

        chain.doFilter(request, response);
    }

    @Override
    public void destroy() {}
}

// 登录检查过滤器
@WebFilter(
    urlPatterns = {"/protected/*", "/admin/*"},
    filterName = "loginCheckFilter"
)
public class LoginCheckFilter implements Filter {

    @Override
    public void doFilter(ServletRequest request, ServletResponse response,
                           FilterChain chain) throws IOException, ServletException {

        HttpServletRequest req = (HttpServletRequest) request;
        HttpServletResponse resp = (HttpServletResponse) response;

        HttpSession session = req.getSession(false);

        // 检查会话
        if (session == null || session.getAttribute("user") == null) {
            resp.sendRedirect(req.getContextPath() + "/login");
            return;
        }

        chain.doFilter(request, response);
    }

    // 其他方法...
}

// 跨域过滤器
@WebFilter(urlPatterns = "/*")
public class CorsFilter implements Filter {

    @Override
    public void doFilter(ServletRequest request, ServletResponse response,
                           FilterChain chain) throws IOException, ServletException {

        HttpServletResponse resp = (HttpServletResponse) response;

        resp.setHeader("Access-Control-Allow-Origin", "*");
        resp.setHeader("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS");
        resp.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");
        resp.setHeader("Access-Control-Max-Age", "3600");

        if ("OPTIONS".equals(((HttpServletRequest) request).getMethod())) {
            resp.setStatus(HttpServletResponse.SC_OK);
            return;
        }

        chain.doFilter(request, response);
    }

    // 其他方法...
}
```

### 6. 监听器

```java
// Session 监听器
@WebListener
public class SessionListener implements HttpSessionListener,
        HttpSessionAttributeListener {

    @Override
    public void sessionCreated(HttpSessionEvent se) {
        System.out.println("Session 创建: " + se.getSession().getId());
        se.getSession().setMaxInactiveInterval(1800);  // 30分钟
    }

    @Override
    public void sessionDestroyed(HttpSessionEvent se) {
        System.out.println("Session 销毁: " + se.getSession().getId());
    }

    @Override
    public void attributeAdded(HttpSessionBindingEvent event) {
        System.out.println("Session 属性添加: " + event.getName() + "=" + event.getValue());
    }

    @Override
    public void attributeRemoved(HttpSessionBindingEvent event) {
        System.out.println("Session 属性移除: " + event.getName() + "=" + event.getValue());
    }

    @Override
    public void attributeReplaced(HttpSessionBindingEvent event) {
        System.out.println("Session 属性替换: " + event.getName() +
            " 旧值=" + event.getOldValue() +
            " 新值=" + event.getValue());
    }
}

// Servlet 上下文监听器
@WebListener
public class ContextListener implements ServletContextListener {

    @Override
    public void contextInitialized(ServletContextEvent sce) {
        System.out.println("应用启动");

        ServletContext context = sce.getServletContext();

        // 初始化配置
        String appVersion = context.getInitParameter("app.version");
        context.setAttribute("appVersion", appVersion);

        // 加载配置文件
        String configPath = context.getRealPath("/WEB-INF/config.properties");
        try {
            Properties props = new Properties();
            props.load(new FileInputStream(configPath));
            context.setAttribute("config", props);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    @Override
    public void contextDestroyed(ServletContextEvent sce) {
        System.out.println("应用关闭");

        // 清理资源
        // ...
    }
}

// 请求监听器
@WebListener
public class RequestListener implementsServletRequestListener {

    @Override
    public void requestInitialized(ServletRequestEvent sre) {
        HttpServletRequest request = (HttpServletRequest) sre.getServletRequest();
        System.out.println("请求开始: " + request.getRequestURI());

        // 记录请求开始时间
        request.setAttribute("startTime", System.currentTimeMillis());
    }

    @Override
    public void requestDestroyed(ServletRequestEvent sre) {
        HttpServletRequest request = (HttpServletRequest) sre.getServletRequest();

        Long startTime = (Long) request.getAttribute("startTime");
        if (startTime != null) {
            long duration = System.currentTimeMillis() - startTime;
            System.out.println("请求结束: " + request.getRequestURI() + ", 耗时: " + duration + "ms");
        }
    }
}
```

## 二、JSP 基础

### 1. JSP 指令

```jsp
<%@ page language="java" contentType="text/html;charset=UTF-8" pageEncoding="UTF-8"%>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<%@ taglib prefix="fmt" uri="http://java.sun.com/jsp/jstl/fmt" %>

<!-- page 指令 -->
<%@ page import="java.util.*, java.text.*" %>
<%@ page isELIgnored="false" %>

<!-- include 指令 -->
<%@ include file="/WEB-INF/jspf/header.jspf" %>

<!-- taglib 指令 -->
<%@ taglib uri="http://struts.apache.org/tags-html" prefix="html" %>
<%@ taglib uri="http://struts.apache.org/tags-bean" prefix="bean" %>
<%@ taglib uri="http://struts.apache.org/tags-logic" prefix="logic" %>
```

### 2. JSP 动作元素

```jsp
<!-- 声明 -->
<%!
    public int add(int a, int b) {
        return a + b;
    }
%>

<!-- 脚本 -->
<%
    int x = 10;
    int y = 20;
    int sum = x + y;
    request.setAttribute("result", sum);
%>

<!-- 表达式 -->
<p>x + y = <%= x + y %></p>
<p>调用方法: <%= add(5, 3) %></p>

<!-- EL 表达式 -->
<p>使用EL: ${1 + 2}</p>
<p>请求参数: ${param.name}</p>
<p>会话属性: ${session.user.username}</p>
<p>Cookie: ${cookie.JSESSIONID.value}</p>

<!-- JSTL 标签 -->
<c:set var="message" value="Hello JSTL" />
<p>${message}</p>

<!-- 条件判断 -->
<c:if test="${user.age >= 18}">
    <p>成年人</p>
</c:if>

<c:choose>
    <c:when test="${user.age < 18}">
        <p>未成年</p>
    </c:when>
    <c:when test="${user.age >= 60}">
        <p>老年</p>
    </c:when>
    <c:otherwise>
        <p>青年</p>
    </c:otherwise>
</c:choose>

<!-- 循环 -->
<c:forEach var="item" items="${products}" varStatus="status">
    <tr>
        <td>${status.index + 1}</td>
        <td>${item.name}</td>
        <td>${item.price}</td>
    </tr>
</c:forEach>

<!-- URL 重写 -->
<c:url value="/product" var="productUrl">
    <c:param name="id" value="${product.id}" />
</c:url>
<a href="${productUrl}">查看商品</a>
```

### 3. 自定义标签

```java
// 标签处理器
public class DateTag extends SimpleTagSupport {

    private String pattern;
    private String var;

    public void setPattern(String pattern) {
        this.pattern = pattern;
    }

    public void setVar(String var) {
        this.var = var;
    }

    @Override
    public void doTag() throws JspException, IOException {
        Date now = new Date();
        SimpleDateFormat sdf;

        if (pattern != null) {
            sdf = new SimpleDateFormat(pattern);
        } else {
            sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        }

        String dateStr = sdf.format(now);

        if (var != null) {
            getJspContext().setAttribute(var, dateStr);
        } else {
            getJspContext().getOut().write(dateStr);
        }
    }
}

// TLD 文件
<?xml version="1.0" encoding="UTF-8"?>
<taglib xmlns="http://java.sun.com/xml/ns/j2ee"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://java.sun.com/xml/ns/j2ee
        http://java.sun.com/xml/ns/j2ee/web-jsptaglibrary_2_0.xsd"
        version="2.0">

    <tlib-version>2.0</tlib-version>
    <short-name>my</short-name>
    <uri>http://www.example.com/tags</uri>
    <display-name>My Tags</display-name>

    <tag>
        <name>date</name>
        <tag-class>com.example.tag.DateTag</tag-class>
        <body-content>empty</body-content>
        <attribute>
            <name>pattern</name>
            <required>false</required>
            <rtexprvalue>true</rtexprvalue>
        </attribute>
        <attribute>
            <name>var</name>
            <required>false</required>
            <rtexprvalue>true</rtexprvalue>
        </attribute>
    </tag>
</taglib>
```

## 三、MVC 模式手动实现

### 1. 核心控制器

```java
@WebServlet("/")
public class DispatcherServlet extends HttpServlet {

    private Map<String, Handler> handlers = new HashMap<>();

    @Override
    public void init() throws ServletException {
        // 注册处理器
        handlers.put("/user/list", new UserListHandler());
        handlers.put("/user/create", new UserCreateHandler());
        handlers.put("/user/update", new UserUpdateHandler());
        handlers.put("/user/delete", new UserDeleteHandler());
    }

    @Override
    protected void service(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {

        String uri = req.getRequestURI();
        String contextPath = req.getContextPath();
        String path = uri.substring(contextPath.length());

        // 处理静态资源
        if (path.startsWith("/static/")) {
            // 返回静态文件
            return;
        }

        // 路由到处理器
        Handler handler = handlers.get(path);
        if (handler != null) {
            handler.handle(req, resp);
        } else {
            resp.sendError(404, "页面不存在");
        }
    }
}

// 处理器接口
public interface Handler {
    void handle(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException;
}

// 用户列表处理器
public class UserListHandler implements Handler {

    private final UserService userService = new UserService();

    @Override
    public void handle(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {

        List<User> users = userService.findAll();

        req.setAttribute("users", users);
        req.getRequestDispatcher("/WEB-INF/jsp/user/list.jsp").forward(req, resp);
    }
}

// 用户创建处理器
public class UserCreateHandler implements Handler {

    private final UserService userService = new UserService();

    @Override
    public void handle(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {

        if ("GET".equals(req.getMethod())) {
            req.getRequestDispatcher("/WEB-INF/jsp/user/form.jsp").forward(req, resp);
        } else {
            User user = new User();
            user.setUsername(req.getParameter("username"));
            user.setPassword(req.getParameter("password"));
            user.setEmail(req.getParameter("email"));

            userService.save(user);

            resp.sendRedirect(req.getContextPath() + "/user/list");
        }
    }
}
```

### 2. 视图解析

```java
public class ViewResolver {

    private final String prefix;
    private final String suffix;

    public ViewResolver(String prefix, String suffix) {
        this.prefix = prefix;
        this.suffix = suffix;
    }

    public String resolve(String viewName) {
        return prefix + viewName + suffix;
    }
}

// 模型和视图
public class ModelAndView {

    private String viewName;
    private Map<String, Object> model = new HashMap<>();

    public ModelAndView(String viewName) {
        this.viewName = viewName;
    }

    public ModelAndView(String viewName, Map<String, Object> model) {
        this.viewName = viewName;
        this.model = model;
    }

    public void addObject(String key, Object value) {
        model.put(key, value);
    }

    public String getViewName() {
        return viewName;
    }

    public Map<String, Object> getModel() {
        return model;
    }
}
```

## 四、综合示例：用户管理系统

### 1. 项目结构

```
webapp/
├── WEB-INF/
│   ├── jsp/
│   │   ├── header.jspf
│   │   ├── footer.jspf
│   │   └── user/
│   │       ├── list.jsp
│   │       ├── form.jsp
│   │       └── detail.jsp
│   ├── lib/
│   ├── web.xml
│   └── config/
│       └── application.properties
├── static/
│   ├── css/
│   ├── js/
│   └── images/
└── index.jsp
```

### 2. Web.xml 配置

```xml
<?xml version="1.0" encoding="UTF-8"?>
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://xmlns.jcp.org/xml/ns/javaee
         http://xmlns.jcp.org/xml/ns/javaee/web-app_4_0.xsd"
         version="4.0">

    <display-name>UserManagementSystem</display-name>

    <!-- 字符编码过滤器 -->
    <filter>
        <filter-name>encodingFilter</filter-name>
        <filter-class>com.example.filter.EncodingFilter</filter-class>
        <init-param>
            <param-name>encoding</param-name>
            <param-value>UTF-8</param-value>
        </init-param>
    </filter>
    <filter-mapping>
        <filter-name>encodingFilter</filter-name>
        <url-pattern>/*</url-pattern>
    </filter-mapping>

    <!-- 登录检查过滤器 -->
    <filter>
        <filter-name>loginCheckFilter</filter-name>
        <filter-class>com.example.filter.LoginCheckFilter</filter-class>
    </filter>
    <filter-mapping>
        <filter-name>loginCheckFilter</filter-name>
        <url-pattern>/protected/*</url-pattern>
        <url-pattern>/admin/*</url-pattern>
    </filter-mapping>

    <!-- 上下文监听器 -->
    <listener>
        <listener-class>com.example.listener.ContextListener</listener-class>
    </listener>
    <listener>
        <listener-class>com.example.listener.SessionListener</listener-class>
    </listener>

    <!-- 前端控制器 -->
    <servlet>
        <servlet-name>dispatcherServlet</servlet-name>
        <servlet-class>com.example.servlet.DispatcherServlet</servlet-class>
        <load-on-startup>1</load-on-startup>
    </servlet>

    <servlet-mapping>
        <servlet-name>dispatcherServlet</servlet-name>
        <url-pattern>/</url-pattern>
    </servlet-mapping>

    <!-- 默认页面 -->
    <welcome-file-list>
        <welcome-file>index.jsp</welcome-file>
    </welcome-file-list>

    <!-- 错误页面 -->
    <error-page>
        <error-code>404</error-code>
        <location>/WEB-INF/jsp/error/404.jsp</location>
    </error-page>
    <error-page>
        <error-code>500</error-code>
        <location>/WEB-INF/jsp/error/500.jsp</location>
    </error-page>

    <!-- 会话配置 -->
    <session-config>
        <session-timeout>30</session-timeout>
    </session-config>
</web-app>
```

### 3. 主页面

```jsp
<%@ page language="java" contentType="text/html;charset=UTF-8" pageEncoding="UTF-8"%>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>用户管理系统</title>
    <link href="${pageContext.request.contextPath}/static/css/style.css" rel="stylesheet">
</head>
<body>
    <div class="container">
        <header>
            <h1>用户管理系统</h1>
            <nav>
                <a href="${pageContext.request.contextPath}/user/list">用户列表</a>
                <a href="${pageContext.request.contextPath}/user/create">添加用户</a>
                <a href="${pageContext.request.contextPath}/protected/dashboard">控制台</a>
            </nav>
        </header>

        <main>
            <c:if test="${not empty message}">
                <div class="alert ${message.type}">${message.content}</div>
            </c:if>

            <h2>欢迎使用</h2>
            <p>请使用上方导航菜单操作。</p>
        </main>

        <%@ include file="/WEB-INF/jspf/footer.jspf" %>
    </div>
</body>
</html>
```

## 小结

本节学习了 JavaWeb 基础：

- **Servlet** - 生命周期、请求响应、会话管理、文件上传
- **过滤器** - 字符编码、登录检查、跨域
- **监听器** - 会话监听、上下文监听、请求监听
- **JSP** - 指令、动作元素、自定义标签
- **MVC模式** - 手动实现简易MVC框架

现代开发中，Servlet/JSP 已被 SpringMVC 等框架取代，但理解原理有助于深入学习。

## 实践练习

### 编程题
1. 使用 Servlet + JSP 实现一个简单的用户登录注册系统，包括表单验证、Session 管理和数据库存储（使用 JDBC）。
2. 实现一个 Filter 记录所有 HTTP 请求的耗时日志，并添加 CORS 支持。

### 思考题
1. Servlet 是单例还是多例？为什么 Servlet 设计为单例模式？线程安全问题如何解决？
2. JSP 和现代前端框架（React/Vue）相比，各自的优势和劣势？

### 自测题
1. Servlet 的生命周期包括哪几个阶段？
2. `forward` 和 `redirect` 的区别？
3. Filter 和 Interceptor 的执行顺序？

下一步将学习 Spring 框架基础（→ `spring/beginner/01-spring-framework.md`）。