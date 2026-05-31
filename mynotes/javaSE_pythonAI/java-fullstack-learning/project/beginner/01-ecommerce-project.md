# 电商系统项目实战

## 项目架构

```
┌─────────────────────────────────────────────────────────┐
│                    前端层 (Vue/React)                      │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│                  API Gateway (Nginx)                        │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│              Spring Cloud Gateway                         │
│          - 认证鉴权  - 路由转发  - 限流熔断                    │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ↓            ↓            ↓
┌───────────┐ ┌───────────┐ ┌───────────┐
│ 用户服务   │ │ 订单服务   │ │ 商品服务   │
│           │ │           │ │           │
├───────────┤ ├───────────┤ ├───────────┤
│ 用户 CRUD │ │ 订单 CRUD │ │ 商品 CRUD │
│ 认证授权   │ │ 支付流程   │ │ 库存管理   │
│ 收货地址   │ │ 订单状态   │ │ 分类管理   │
└───────────┘ └───────────┘ └───────────┘
        ↓            ↓            ↓
┌─────────────────────────────────────────────────────────┐
│                  数据层                                    │
│  ┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐      │
│  │ MySQL │  │ Redis │  │ RabbitMQ│  │Elasticsearch│
│  └───────┘  └───────┘  └───────┘  └───────┘      │
└─────────────────────────────────────────────────────────┘
```

## 一、通用模块

### 1. 公共依赖

```xml
<!-- pom.xml -->
<dependencies>
    <!-- Spring Boot Starter -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-jpa</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-validation</artifactId>
    </dependency>

    <!-- Spring Cloud -->
    <dependency>
        <groupId>com.alibaba.cloud</groupId>
        <artifactId>spring-cloud-starter-alibaba-nacos-discovery</artifactId>
    </dependency>
    <dependency>
        <groupId>com.alibaba.cloud</groupId>
        <artifactId>spring-cloud-starter-alibaba-nacos-config</artifactId>
    </dependency>
    <dependency>
        <groupId>com.alibaba.cloud</groupId>
        <artifactId>spring-cloud-starter-alibaba-sentinel</artifactId>
    </dependency>

    <!-- OpenFeign -->
    <dependency>
        <groupId>org.springframework.cloud</groupId>
        <artifactId>spring-cloud-starter-openfeign</artifactId>
    </dependency>

    <!-- Redis -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-redis</artifactId>
    </dependency>
    <dependency>
        <groupId>org.apache.commons</groupId>
        <artifactId>commons-pool2</artifactId>
    </dependency>

    <!-- MySQL -->
    <dependency>
        <groupId>mysql</groupId>
        <artifactId>mysql-connector-java</artifactId>
    </dependency>

    <!-- MyBatis Plus -->
    <dependency>
        <groupId>com.baomidou</groupId>
        <artifactId>mybatis-plus-boot-starter</artifactId>
        <version>3.5.3</version>
    </dependency>

    <!-- RocketMQ -->
    <dependency>
        <groupId>org.apache.rocketmq</groupId>
        <artifactId>rocketmq-spring-boot-starter</artifactId>
        <version>2.2.3</version>
    </dependency>

    <!-- Lombok -->
    <dependency>
        <groupId>org.projectlombok</groupId>
        <artifactId>lombok</artifactId>
        <optional>true</optional>
    </dependency>

    <!-- Hutool 工具类 -->
    <dependency>
        <groupId>cn.hutool</groupId>
        <artifactId>hutool-all</artifactId>
        <version>5.8.20</version>
    </dependency>

    <!-- Jackson -->
    <dependency>
        <groupId>com.fasterxml.jackson.core</groupId>
        <artifactId>jackson-databind</artifactId>
    </dependency>
    <dependency>
        <groupId>com.fasterxml.jackson.datatype</groupId>
        <artifactId>jackson-datatype-jsr310</artifactId>
    </dependency>

    <!-- Knife4j 接口文档 -->
    <dependency>
        <groupId>com.github.xiaoymin</groupId>
        <artifactId>knife4j-openapi3-jakarta-spring-boot-starter</artifactId>
        <version>4.3.0</version>
    </dependency>

    <!-- Test -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-test</artifactId>
        <scope>test</scope>
    </dependency>
</dependencies>
```

### 2. 公共配置

```java
// 基础配置
@Configuration
public class CommonConfig {

    @Bean
    public RestTemplate restTemplate() {
        RestTemplate template = new RestTemplate();
        template.setMessageConverters(Arrays.asList(
            new StringHttpMessageConverter(),
            new MappingJackson2HttpMessageConverter()
        ));
        return template;
    }

    @Bean
    public ExecutorService executorService() {
        return new ThreadPoolExecutor(
            10,  // 核心线程数
            200, // 最大线程数
            60L, TimeUnit.SECONDS,  // 空闲线程存活时间
            new LinkedBlockingQueue<>(1000),  // 任务队列
            new ThreadPoolExecutor.CallerRunsPolicy()  // 拒绝策略
        );
    }
}

// 统一响应格式
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Result<T> {
    private Integer code;
    private String message;
    private T data;
    private Long timestamp;

    public static <T> Result<T> success() {
        return Result.<T>builder()
            .code(200)
            .message("success")
            .timestamp(System.currentTimeMillis())
            .build();
    }

    public static <T> Result<T> success(T data) {
        return Result.<T>builder()
            .code(200)
            .message("success")
            .data(data)
            .timestamp(System.currentTimeMillis())
            .build();
    }

    public static <T> Result<T> error(Integer code, String message) {
        return Result.<T>builder()
            .code(code)
            .message(message)
            .timestamp(System.currentTimeMillis())
            .build();
    }

    public static <T> Result<T> error(String message) {
        return error(500, message);
    }
}

// 分页响应
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PageResult<T> {
    private List<T> records;
    private long total;
    private long current;
    private long size;
    private long pages;

    public static <T> PageResult<T> of(Page<T> page) {
        return PageResult.<T>builder()
            .records(page.getContent())
            .total(page.getTotalElements())
            .current(page.getNumber() + 1)
            .size(page.getSize())
            .pages(page.getTotalPages())
            .build();
    }
}
```

### 3. 异常处理

```java
// 自定义异常
public class BusinessException extends RuntimeException {
    private final Integer code;

    public BusinessException(String message) {
        super(message);
        this.code = 500;
    }

    public BusinessException(Integer code, String message) {
        super(message);
        this.code = code;
    }

    public BusinessException(String message, Throwable cause) {
        super(message, cause);
        this.code = 500;
    }
}

public class ResourceNotFoundException extends BusinessException {
    public ResourceNotFoundException(String message) {
        super(404, message);
    }
}

// 全局异常处理
@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {

    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<Result<?>> handleBusinessException(BusinessException e) {
        log.warn("业务异常: {}", e.getMessage());
        return ResponseEntity.ok(Result.error(e.getCode(), e.getMessage()));
    }

    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<Result<?>> handleResourceNotFoundException(ResourceNotFoundException e) {
        log.warn("资源不存在: {}", e.getMessage());
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
            .body(Result.error(404, e.getMessage()));
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Result<?>> handleValidationException(MethodArgumentNotValidException e) {
        Map<String, String> errors = new HashMap<>();
        e.getBindingResult().getFieldErrors().forEach(error ->
            errors.put(error.getField(), error.getDefaultMessage())
        );

        log.warn("参数校验失败: {}", errors);
        return ResponseEntity.badRequest()
            .body(Result.<Map<String, String>>builder()
                .code(400)
                .message("参数校验失败")
                .data(errors)
                .timestamp(System.currentTimeMillis())
                .build());
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<Result<?>> handleException(Exception e) {
        log.error("系统异常", e);
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
            .body(Result.error(500, "服务器内部错误"));
    }
}
```

## 二、用户服务

### 1. 实体类

```java
@Data
@Entity
@Table(name = "t_user")
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true, length = 50)
    private String username;

    @Column(nullable = false, length = 100)
    private String password;

    @Column(length = 100)
    private String nickname;

    @Column(length = 100)
    private String email;

    @Column(length = 20)
    private String phone;

    @Column(length = 255)
    private String avatar;

    @Column(length = 20)
    @Enumerated(EnumType.STRING)
    private UserStatus status;

    @Column
    private Integer loginCount = 0;

    @Column
    private LocalDateTime lastLoginAt;

    @CreatedDate
    @Column(updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    private LocalDateTime updatedAt;
}

public enum UserStatus {
    ACTIVE, INACTIVE, LOCKED
}
```

### 2. Service 层

```java
@Service
@Transactional
@Slf4j
public class UserService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final UserMapper userMapper;
    private final StringRedisTemplate stringRedisTemplate;

    public UserService(UserRepository userRepository,
                        PasswordEncoder passwordEncoder,
                        UserMapper userMapper,
                        StringRedisTemplate stringRedisTemplate) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.userMapper = userMapper;
        this.stringRedisTemplate = stringRedisTemplate;
    }

    // 注册
    public User register(UserRegisterDto dto) {
        // 检查用户名是否存在
        if (userRepository.existsByUsername(dto.getUsername())) {
            throw new BusinessException("用户名已存在");
        }

        // 检查邮箱是否存在
        if (dto.getEmail() != null && userRepository.existsByEmail(dto.getEmail())) {
            throw new BusinessException("邮箱已被注册");
        }

        // 创建用户
        User user = User.builder()
            .username(dto.getUsername())
            .password(passwordEncoder.encode(dto.getPassword()))
            .nickname(dto.getNickname())
            .email(dto.getEmail())
            .phone(dto.getPhone())
            .status(UserStatus.ACTIVE)
            .build();

        user = userRepository.save(user);

        // 发送验证邮件
        if (user.getEmail() != null) {
            sendVerificationEmail(user);
        }

        return user;
    }

    // 登录
    public LoginResult login(LoginDto dto) {
        // 查找用户
        User user = userRepository.findByUsername(dto.getUsername())
            .orElseThrow(() -> new BusinessException("用户名或密码错误"));

        // 检查状态
        if (user.getStatus() != UserStatus.ACTIVE) {
            throw new BusinessException("账号已被锁定或禁用");
        }

        // 验证密码
        if (!passwordEncoder.matches(dto.getPassword(), user.getPassword())) {
            throw new BusinessException("用户名或密码错误");
        }

        // 更新登录信息
        user.setLoginCount(user.getLoginCount() + 1);
        user.setLastLoginAt(LocalDateTime.now());
        userRepository.save(user);

        // 生成 Token
        String token = JwtUtil.generateToken(user.getId(), user.getUsername());

        // 缓存用户信息
        String cacheKey = "user:info:" + user.getId();
        stringRedisTemplate.opsForValue().set(cacheKey, user, 24, TimeUnit.HOURS);

        // 记录登录日志
        recordLoginLog(user.getId(), dto.getIp());

        return LoginResult.builder()
            .token(token)
            .userInfo(userMapper.toDto(user))
            .build();
    }

    // 获取用户信息
    public UserInfoDto getUserInfo(Long userId) {
        // 先从缓存获取
        String cacheKey = "user:info:" + userId;
        User cachedUser = (User) stringRedisTemplate.opsForValue().get(cacheKey);

        if (cachedUser != null) {
            return userMapper.toDto(cachedUser);
        }

        // 从数据库获取
        User user = userRepository.findById(userId)
            .orElseThrow(() -> new ResourceNotFoundException("用户不存在"));

        // 放入缓存
        stringRedisTemplate.opsForValue().set(cacheKey, user, 24, TimeUnit.HOURS);

        return userMapper.toDto(user);
    }

    // 更新用户信息
    public void updateUserInfo(Long userId, UserUpdateDto dto) {
        User user = userRepository.findById(userId)
            .orElseThrow(() -> new ResourceNotFoundException("用户不存在"));

        // 更新字段
        if (dto.getNickname() != null) {
            user.setNickname(dto.getNickname());
        }
        if (dto.getAvatar() != null) {
            user.setAvatar(dto.getAvatar());
        }
        if (dto.getEmail() != null) {
            user.setEmail(dto.getEmail());
        }
        if (dto.getPhone() != null) {
            user.setPhone(dto.getPhone());
        }

        user = userRepository.save(user);

        // 更新缓存
        String cacheKey = "user:info:" + userId;
        stringRedisTemplate.opsForValue().set(cacheKey, user, 24, TimeUnit.HOURS);
    }

    // 修改密码
    public void changePassword(Long userId, ChangePasswordDto dto) {
        User user = userRepository.findById(userId)
            .orElseThrow(() -> new ResourceNotFoundException("用户不存在"));

        // 验证旧密码
        if (!passwordEncoder.matches(dto.getOldPassword(), user.getPassword())) {
            throw new BusinessException("原密码不正确");
        }

        // 更新密码
        user.setPassword(passwordEncoder.encode(dto.getNewPassword()));
        userRepository.save(user);

        // 清除缓存，强制重新登录
        String cacheKey = "user:info:" + userId;
        stringRedisTemplate.delete(cacheKey);
    }

    private void sendVerificationEmail(User user) {
        // 发送验证邮件逻辑
    }

    private void recordLoginLog(Long userId, String ip) {
        // 记录登录日志逻辑
    }
}
```

### 3. Controller 层

```java
@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
@Slf4j
public class UserController {

    private final UserService userService;

    @PostMapping("/register")
    public Result<UserInfoDto> register(@Valid @RequestBody UserRegisterDto dto) {
        User user = userService.register(dto);
        return Result.success(userService.getUserInfo(user.getId()));
    }

    @PostMapping("/login")
    public Result<LoginResult> login(@Valid @RequestBody LoginDto dto) {
        LoginResult result = userService.login(dto);
        return Result.success(result);
    }

    @GetMapping("/info")
    public Result<UserInfoDto> getUserInfo(@RequestHeader("X-User-Id") Long userId) {
        return Result.success(userService.getUserInfo(userId));
    }

    @PutMapping("/info")
    public Result<Void> updateUserInfo(
        @RequestHeader("X-User-Id") Long userId,
        @Valid @RequestBody UserUpdateDto dto
    ) {
        userService.updateUserInfo(userId, dto);
        return Result.success();
    }

    @PostMapping("/password")
    public Result<Void> changePassword(
        @RequestHeader("X-User-Id") Long userId,
        @Valid @RequestBody ChangePasswordDto dto
    ) {
        userService.changePassword(userId, dto);
        return Result.success();
    }

    @GetMapping("/search")
    public Result<PageResult<UserInfoDto>> searchUsers(
        @RequestParam String keyword,
        @RequestParam(defaultValue = "1") int page,
        @RequestParam(defaultValue = "10") int size
    ) {
        Page<UserInfoDto> result = userService.searchUsers(keyword, page, size);
        return Result.success(PageResult.of(result));
    }
}
```

## 三、订单服务

### 1. 订单实体

```java
@Data
@Entity
@Table(name = "t_order")
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Order {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true, length = 50)
    private String orderNo;

    @Column(nullable = false)
    private Long userId;

    @Column(nullable = false)
    private Long productId;

    @Column(nullable = false)
    private Integer quantity;

    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal totalAmount;

    @Column(length = 20)
    @Enumerated(EnumType.STRING)
    private OrderStatus status;

    @Column
    private LocalDateTime paidAt;

    @Column
    private LocalDateTime shippedAt;

    @Column
    private LocalDateTime deliveredAt;

    @CreatedDate
    @Column(updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    private LocalDateTime updatedAt;

    @Version
    private Integer version;
}

public enum OrderStatus {
    PENDING,       // 待支付
    PAID,          // 已支付
    SHIPPED,       // 已发货
    DELIVERED,     // 已收货
    CANCELLED,     // 已取消
    REFUNDED       // 已退款
}
```

### 2. 订单服务

```java
@Service
@Transactional
@Slf4j
public class OrderService {

    private final OrderRepository orderRepository;
    private final ProductClient productClient;
    private final OrderMessageProducer messageProducer;
    private final DistributedLock distributedLock;
    private final RedisTemplate<String, Object> redisTemplate;

    // 创建订单（分布式事务）
    public Order createOrder(OrderCreateDto dto, Long userId) {
        String lockKey = "order:lock:" + userId + ":" + dto.getProductId();

        return distributedLock.executeWithLock(lockKey, () -> {
            // 1. 检查商品库存
            ProductDto product = productClient.getProduct(dto.getProductId());

            if (product.getStock() < dto.getQuantity()) {
                throw new BusinessException("库存不足");
            }

            // 2. 锁定库存（Redis 扣减）
            String stockKey = "product:stock:" + dto.getProductId();
            Long stock = redisTemplate.opsForValue().decrement(stockKey);

            if (stock == null || stock < 0) {
                // 恢复计数
                redisTemplate.opsForValue().increment(stockKey);
                throw new BusinessException("库存不足");
            }

            // 3. 计算价格
            BigDecimal totalAmount = product.getPrice()
                .multiply(BigDecimal.valueOf(dto.getQuantity()));

            // 4. 创建订单
            String orderNo = generateOrderNo();
            Order order = Order.builder()
                .orderNo(orderNo)
                .userId(userId)
                .productId(dto.getProductId())
                .quantity(dto.getQuantity())
                .totalAmount(totalAmount)
                .status(OrderStatus.PENDING)
                .build();

            order = orderRepository.save(order);

            // 5. 发送消息到下游系统
            OrderCreatedMessage message = OrderCreatedMessage.builder()
                .orderId(order.getId())
                .orderNo(orderNo)
                .userId(userId)
                .productId(dto.getProductId())
                .quantity(dto.getQuantity())
                .totalAmount(totalAmount)
                .build();

            messageProducer.sendOrderCreated(message);

            return order;
        });
    }

    // 支付订单
    public void payOrder(Long orderId, Long userId) {
        Order order = orderRepository.findById(orderId)
            .orElseThrow(() -> new ResourceNotFoundException("订单不存在"));

        // 验证订单归属
        if (!order.getUserId().equals(userId)) {
            throw new BusinessException("无权操作此订单");
        }

        // 验证订单状态
        if (order.getStatus() != OrderStatus.PENDING) {
            throw new BusinessException("订单状态不正确");
        }

        // 模拟支付
        boolean paymentSuccess = mockPayment(order.getTotalAmount());

        if (paymentSuccess) {
            // 更新订单状态
            order.setStatus(OrderStatus.PAID);
            order.setPaidAt(LocalDateTime.now());
            order = orderRepository.save(order);

            // 发送支付成功消息
            OrderPaidMessage message = OrderPaidMessage.builder()
                .orderId(order.getId())
                .orderNo(order.getOrderNo())
                .userId(order.getUserId())
                .productId(order.getProductId())
                .paidAt(LocalDateTime.now())
                .build();

            messageProducer.sendOrderPaid(message);
        } else {
            throw new BusinessException("支付失败");
        }
    }

    // 取消订单
    public void cancelOrder(Long orderId, Long userId) {
        Order order = orderRepository.findById(orderId)
            .orElseThrow(() -> new ResourceNotFoundException("订单不存在"));

        // 验证订单归属
        if (!order.getUserId().equals(userId)) {
            throw new BusinessException("无权操作此订单");
        }

        // 只能取消待支付和已支付未发货的订单
        if (order.getStatus() != OrderStatus.PENDING && order.getStatus() != OrderStatus.PAID) {
            throw new BusinessException("订单状态不允许取消");
        }

        // 更新订单状态
        order.setStatus(OrderStatus.CANCELLED);
        orderRepository.save(order);

        // 发送取消消息（恢复库存）
        OrderCancelledMessage message = OrderCancelledMessage.builder()
            .orderId(order.getId())
            .orderNo(order.getOrderNo())
            .productId(order.getProductId())
            .quantity(order.getQuantity())
            .build();

        messageProducer.sendOrderCancelled(message);
    }

    // 查询订单详情
    public OrderDetailDto getOrderDetail(Long orderId, Long userId) {
        Order order = orderRepository.findById(orderId)
            .orElseThrow(() -> new ResourceNotFoundException("订单不存在"));

        // 如果不是自己的订单，返回脱敏信息
        if (!order.getUserId().equals(userId)) {
            throw new BusinessException("无权查看此订单");
        }

        // 获取商品信息
        ProductDto product = productClient.getProduct(order.getProductId());

        return OrderDetailDto.builder()
            .orderNo(order.getOrderNo())
            .status(order.getStatus())
            .totalAmount(order.getTotalAmount())
            .quantity(order.getQuantity())
            .product(product)
            .createdAt(order.getCreatedAt())
            .paidAt(order.getPaidAt())
            .build();
    }

    // 查询用户订单列表
    public PageResult<OrderDto> getUserOrders(Long userId, OrderQueryDto query) {
        Pageable pageable = PageRequest.of(query.getPage() - 1, query.getSize());
        Page<Order> page = orderRepository.findByUserId(userId, pageable);

        List<OrderDto> orders = page.getContent().stream()
            .map(this::convertToDto)
            .collect(Collectors.toList());

        return PageResult.of(new PageImpl<>(orders, pageable, page.getTotalElements()));
    }

    private String generateOrderNo() {
        return LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMddHHmmss"))
            + RandomUtil.randomNumbers(6);
    }

    private boolean mockPayment(BigDecimal amount) {
        // 模拟支付逻辑，99%成功率
        return RandomUtil.randomInt(1, 100) <= 99;
    }

    private OrderDto convertToDto(Order order) {
        return OrderDto.builder()
            .orderId(order.getId())
            .orderNo(order.getOrderNo())
            .status(order.getStatus())
            .totalAmount(order.getTotalAmount())
            .createdAt(order.getCreatedAt())
            .build();
    }
}
```

### 3. 订单Controller

```java
@RestController
@RequestMapping("/api/orders")
@RequiredArgsConstructor
public class OrderController {

    private final OrderService orderService;

    @PostMapping
    public Result<OrderDto> createOrder(
        @Valid @RequestBody OrderCreateDto dto,
        @RequestHeader("X-User-Id") Long userId
    ) {
        Order order = orderService.createOrder(dto, userId);
        return Result.success(OrderDto.from(order));
    }

    @PostMapping("/{orderId}/pay")
    public Result<Void> payOrder(
        @PathVariable Long orderId,
        @RequestHeader("X-User-Id") Long userId
    ) {
        orderService.payOrder(orderId, userId);
        return Result.success();
    }

    @PostMapping("/{orderId}/cancel")
    public Result<Void> cancelOrder(
        @PathVariable Long orderId,
        @RequestHeader("X-User-Id") Long userId
    ) {
        orderService.cancelOrder(orderId, userId);
        return Result.success();
    }

    @GetMapping("/{orderId}")
    public Result<OrderDetailDto> getOrderDetail(
        @PathVariable Long orderId,
        @RequestHeader("X-User-Id") Long userId
    ) {
        OrderDetailDto detail = orderService.getOrderDetail(orderId, userId);
        return Result.success(detail);
    }

    @GetMapping("/my")
    public Result<PageResult<OrderDto>> getMyOrders(
        @RequestHeader("X-User-Id") Long userId,
        OrderQueryDto query
    ) {
        PageResult<OrderDto> result = orderService.getUserOrders(userId, query);
        return Result.success(result);
    }
}
```

## 四、商品服务

### 1. 商品实体

```java
@Data
@Entity
@Table(name = "t_product")
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Product {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true, length = 50)
    private String productNo;

    @Column(nullable = false, length = 100)
    private String name;

    @Column(length = 20)
    private String category;

    @Column(columnDefinition = "TEXT")
    private String description;

    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal price;

    @Column(nullable = false)
    private Integer stock;

    @Column(nullable = false)
    private Integer sales = 0;

    @Column(length = 255)
    private String image;

    @Column
    private Boolean onSale = false;

    @Column(precision = 5, scale = 2)
    private BigDecimal discountPrice;

    @CreatedDate
    @Column(updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    private LocalDateTime updatedAt;
}
```

### 2. 商品服务

```java
@Service
@Transactional
@Slf4j
public class ProductService {

    private final ProductRepository productRepository;
    private final RedisTemplate<String, Object> redisTemplate;
    private final StringRedisTemplate stringRedisTemplate;

    // 创建商品
    public Product createProduct(ProductCreateDto dto) {
        // 检查商品编号是否存在
        if (productRepository.existsByProductNo(dto.getProductNo())) {
            throw new BusinessException("商品编号已存在");
        }

        Product product = Product.builder()
            .productNo(dto.getProductNo())
            .name(dto.getName())
            .category(dto.getCategory())
            .description(dto.getDescription())
            .price(dto.getPrice())
            .stock(dto.getStock())
            .onSale(dto.getOnSale())
            .discountPrice(dto.getOnSale() ? dto.getDiscountPrice() : null)
            .build();

        product = productRepository.save(product);

        // 缓存商品信息
        cacheProduct(product);

        return product;
    }

    // 获取商品信息（带缓存）
    public ProductDto getProduct(Long productId) {
        // 先从缓存获取
        String cacheKey = "product:" + productId;
        ProductDto cached = (ProductDto) redisTemplate.opsForValue().get(cacheKey);

        if (cached != null) {
            return cached;
        }

        // 从数据库获取
        Product product = productRepository.findById(productId)
            .orElseThrow(() -> new ResourceNotFoundException("商品不存在"));

        ProductDto dto = convertToDto(product);

        // 放入缓存
        redisTemplate.opsForValue().set(cacheKey, dto, 1, TimeUnit.HOURS);

        return dto;
    }

    // 扣减库存（分布式锁）
    public boolean deductStock(Long productId, Integer quantity) {
        String lockKey = "product:lock:" + productId;

        return distributedLock.executeWithLock(lockKey, () -> {
            Product product = productRepository.findById(productId)
                .orElseThrow(() -> new ResourceNotFoundException("商品不存在"));

            if (product.getStock() < quantity) {
                return false;
            }

            // 扣减库存
            product.setStock(product.getStock() - quantity);
            product.setSales(product.getSales() + quantity);
            product = productRepository.save(product);

            // 更新缓存
            cacheProduct(product);

            return true;
        });
    }

    // 搜索商品（使用 Elasticsearch）
    public PageResult<ProductDto> searchProducts(String keyword, int page, int size) {
        // 实际应用中使用 Elasticsearch
        Pageable pageable = PageRequest.of(page - 1, size, Sort.by("sales").descending());
        Page<Product> page;

        if (StringUtils.hasText(keyword)) {
            page = productRepository.findByNameContaining(keyword, pageable);
        } else {
            page = productRepository.findAll(pageable);
        }

        List<ProductDto> products = page.getContent().stream()
            .map(this::convertToDto)
            .collect(Collectors.toList());

        return PageResult.of(new PageImpl<>(products, pageable, page.getTotalElements()));
    }

    // 批量导入商品
    @Async
    public void importProducts(List<ProductCreateDto> products) {
        List<Product> entities = products.stream()
            .map(dto -> Product.builder()
                .productNo(dto.getProductNo())
                .name(dto.getName())
                .category(dto.getCategory())
                .description(dto.getDescription())
                .price(dto.getPrice())
                .stock(dto.getStock())
                .onSale(dto.getOnSale())
                .discountPrice(dto.getOnSale() ? dto.getDiscountPrice() : null)
                .build())
            .collect(Collectors.toList());

        List<Product> saved = productRepository.saveAll(entities);

        // 批量缓存
        Map<String, Product> cacheMap = new HashMap<>();
        for (Product product : saved) {
            cacheMap.put("product:" + product.getId(), convertToDto(product));
        }
        redisTemplate.opsForValue().multiSet(cacheMap);

        // 同步到 Elasticsearch
        syncToElasticsearch(saved);

        log.info("批量导入 {} 个商品成功", saved.size());
    }

    private void cacheProduct(Product product) {
        String cacheKey = "product:" + product.getId();
        redisTemplate.opsForValue().set(cacheKey, convertToDto(product), 1, TimeUnit.HOURS);

        // 更新库存缓存
        String stockKey = "product:stock:" + product.getId();
        stringRedisTemplate.opsForValue().set(stockKey, String.valueOf(product.getStock()));
    }

    private ProductDto convertToDto(Product product) {
        return ProductDto.builder()
            .id(product.getId())
            .productNo(product.getProductNo())
            .name(product.getName())
            .category(product.getCategory())
            .description(product.getDescription())
            .price(product.getPrice())
            .stock(product.getStock())
            .sales(product.getSales())
            .image(product.getImage())
            .onSale(product.getOnSale())
            .discountPrice(product.getDiscountPrice())
            .build();
    }

    private void syncToElasticsearch(List<Product> products) {
        // 同步到 Elasticsearch
    }
}
```

## 小结

本项目实现了完整的电商系统核心功能：

- **用户服务** - 注册、登录、信息管理
- **订单服务** - 创建订单、支付、取消订单
- **商品服务** - 商品管理、库存扣减、搜索

项目特点：
- 微服务架构（Spring Cloud Alibaba）
- 分布式事务（Seata）
- 分布式锁（Redisson）
- 消息队列（RocketMQ）
- 缓存（Redis）
- 接口文档（Knife4j）

## 实践练习

### 编程题
1. 为电商系统添加"秒杀"功能：使用 Redis 预减库存 + 消息队列异步下单 + 限流保护，支持 10000 QPS 的并发。
2. 为电商系统添加"订单超时自动取消"功能：下单 30 分钟后未支付自动取消并恢复库存。

### 思考题
1. 电商系统中，订单号的生成方案有哪些？雪花算法（Snowflake）的优缺点？
2. 微服务架构下的分布式事务如何处理？TCC、Saga、可靠消息最终一致性各适合什么场景？

### 自测题
1. 电商系统通常包含哪些核心微服务模块？
2. 秒杀系统的核心技术要点是什么？
3. 分布式系统中如何实现全局唯一 ID？

下一步将学习系统设计（→ `system-design/beginner/01-system-design-basics.md`）。