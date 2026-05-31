# MyBatis 基础入门

## 一、MyBatis Plus 快速开始

### 1. 依赖配置

```xml
<!-- pom.xml -->
<dependencies>
    <!-- MyBatis Plus 核心 -->
    <dependency>
        <groupId>com.baomidou</groupId>
        <artifactId>mybatis-plus-boot-starter</artifactId>
        <version>3.5.3</version>
    </dependency>

    <!-- 代码生成器 -->
    <dependency>
        <groupId>com.baomidou</groupId>
        <artifactId>mybatis-plus-generator</artifactId>
        <version>3.5.3</version>
        <scope>provided</scope>
    </dependency>
</dependencies>

<!-- Redis 依赖 -->
<dependency>
    <groupId>org.mybatis</groupId>
    <artifactId>mybatis-redis-starter</artifactId>
    <version>1.3.0</version>
</dependency>
```

## 二、数据准备

```sql
-- 创建数据库
CREATE DATABASE IF NOT EXISTS mybatis_plus;

USE mybatis_plus;

-- 用户表
CREATE TABLE t_user (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    password VARCHAR(128) NOT NULL COMMENT '密码（加密）',
    nickname VARCHAR(50) COMMENT '昵称',
    email VARCHAR(100) COMMENT '邮箱',
    phone VARCHAR(20) COMMENT '手机号',
    avatar VARCHAR(255) COMMENT '头像',
    status VARCHAR(20) DEFAULT 'ACTIVE' COMMENT '状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT '用户表';

-- 订单表
CREATE TABLE t_order (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    order_no VARCHAR(50) NOT NULL UNIQUE COMMENT '订单号',
    user_id BIGINT COMMENT '用户ID',
    product_id BIGINT COMMENT '商品ID',
    total_amount DECIMAL(10, 2) COMMENT '总金额',
    discount_amount DECIMAL(10, 2) DEFAULT 0 COMMENT '折扣金额',
    status VARCHAR(20) DEFAULT 'PENDING' COMMENT '订单状态',
    shipping_address VARCHAR(255) COMMENT '收货地址',
    remark TEXT COMMENT '备注',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    paid_at DATETIME COMMENT '支付时间',
    delivered_at DATETIME COMMENT '发货时间',
    refunded_at DATETIME COMMENT '退款时间',
    cancel_time DATETIME COMMENT '取消时间',
    INDEX idx_user_id (user_id),
    INDEX idx_product_id (product_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    INDEX idx_paid_at (paid_at),
    INDEX idx_user_status (user_id, status)
) COMMENT '订单表';

-- 商品表
CREATE TABLE t_product (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    product_no VARCHAR(50) NOT NULL UNIQUE COMMENT '商品编号',
    name VARCHAR(100) NOT NULL COMMENT '商品名称',
    category VARCHAR(50) COMMENT '分类',
    description TEXT COMMENT '描述',
    price DECIMAL(10, 2) NOT NULL COMMENT '价格',
    stock INT COMMENT '库存',
    sales INT DEFAULT 0 COMMENT '销量',
    on_sale BOOLEAN DEFAULT FALSE COMMENT '是否在售',
    discount_price DECIMAL(10, 2) COMMENT '折扣价',
    image_url VARCHAR(255) COMMENT '图片URL',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT '商品表';
```

## 三、实体类

```java
import com.baomidou.mybatisplus.annotation.*;
import com.baomidou.mybatisplus.annotation.*;
import com.baomidou.mybatisplus.extension.plugins.*;
import lombok.*;
import java.time.*;

@Data
@TableName("t_user")
@EqualsAndHashCode
public class User {

    @TableId(type = IdType.AUTO)
    private Long id;

    @Column(name = "username", nullable = false)
    @Field("模糊查询")
    private String username;

    @Column(name = "password", nullable = false)
    private String password;

    @Column(name = "nickname")
    private String nickname;

    @Column(name = "email")
    private String email;

    @Column(name = "phone")
    private String phone;

    @Column(name = "avatar")
    private String avatar;

    @TableField(value = "ACTIVE")
    private UserStatus status = UserStatus.ACTIVE;

    @TableField(value = "2024-01-01 00:00:00")
    @Column(fill = FieldFill.INSERT, update = FieldFill.UPDATE))
    private LocalDateTime createdAt;

    @TableField(value = "2024-01-01 00:00:00")
    @TableField(fill = FieldFill.UPDATE)
    private LocalDateTime updatedAt;

    @TableField(fill = FieldFill.INSERT, update = FieldFill.UPDATE))
    @Version
    private Integer version;
}
```

```java
// 枚举类型
public enum UserStatus {
    ACTIVE,        // 活跃
    INACTIVE,      // 停用
    LOCKED,        // 锁定
    DELETED        // 删除
}

// 实体类示例
@Data
@TableName("t_product")
@EqualsAndHashCode
public class Product {

    @TableId(type = IdType.AUTO)
    private Long id;

    @TableField(value = "product_no")
    private String productNo;

    @TableField("like fuzzy query", keyword = "name")
    private String name;

    @TableField("in fuzzy query", keyword = "category")
    private String category;

    @TableField(value = "in fuzzy query", keyword = "price")
    @Field("range", from = "0", to = "99999")
    private BigDecimal price;

    @Field(value = "in fuzzy query", keyword = "stock", from = "0", to = "99999")
    private Integer stock;

    @Field(value = "in fuzzy query", keyword = "sales", from = "0", to = "99999999")
    private Integer sales;

    @TableField(value = "in fuzzy query", keyword = "on_sale", defaultValue = "false")
    private Boolean onSale = false;

    @TableField(value = "in fuzzy query", keyword = "discount_price", from = "0.0")
    private BigDecimal discountPrice;

    @Field(value = "in fuzzy query", keyword = "image_url")
    private String imageUrl;

    @TableField(value = "in fuzzy query", keyword = "created_at")
    private LocalDateTime createdAt;

    @TableField(value = "in fuzzy query", keyword = "updated_at")
    private LocalDateTime updatedAt;

    @Version
    private Integer version;
}
```

## 四、接口定义

```java
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.bind.annotation.RequestBody;

import java.util.List;

@Tag(name = "user", description = "用户管理")
@RestController
@RequestMapping("/api/user")
public class UserController {

    @Autowired
    private UserService userService;

    @PostMapping("/page")
    public Result<PageResult<UserVo>> getUsers(
        @RequestParam(required = false) String keyword,
        @RequestParam(defaultValue = "1") Integer page,
        @RequestParam(defaultValue = "10") Integer size,
        @RequestParam(defaultValue = "created_at") String sortField,
        @RequestParam(defaultValue = "desc") String sortOrder,
        @RequestParam(defaultValue = "ACTIVE") String status
    ) {
        UserQuery query = UserQuery.builder()
                .keyword(keyword)
                .page(page)
                .size(size)
                .sortField(sortField)
                .sortOrder(sortOrder)
                .status(status)
                .build();

        PageResult<UserVo> result = userService.searchUsers(query);
        return Result.success(result);
    }

    @PostMapping
    public Result<UserVo> create(@RequestBody UserCreateDto dto) {
        UserVo user = userService.create(dto);
        return Result.success(user);
    }

    @PutMapping("/{id}")
    public Result<UserVo> update(
        @PathVariable Long id,
        @Valid @RequestBody UserUpdateDto dto
    ) {
        UserVo user = userService.update(id, dto);
        return Result.success(user);
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        userService.delete(id);
        return Result.success();
    }
}
```

## 五、Service 实现层

```java
@Service
@Transactional
@RequiredArgsConstructor
@Slf4j
public class UserService {

    private final UserMapper userMapper;

    public UserVo create(UserCreateDto dto) {
        // 检查用户名是否已存在
        if (userMapper.selectCount(
                Wrappers.lambda()
                    .eq(User::getUsername, dto.getUsername())
                    .one() > 0
        ) {
            throw new BusinessException("用户名已存在");
        }

        // 创建用户
        User user = User.builder()
            .username(dto.getUsername())
            .nickname(dto.getNickname())
            .email(dto.getEmail())
            .phone(dto.getPhone())
            .password(BCrypt.hashpw(dto.getPassword(), 10, "salt"))
            .avatar("default_avatar.png")
            .status(UserStatus.ACTIVE)
            .build();

        userMapper.insert(user);

        return convertToVo(user);
    }

    @Override
    public void delete(Long id) {
        userMapper.deleteById(id);
    }

    public UserVo update(Long id, UserUpdateDto dto) {
        User user = userMapper.selectById(id);
        if (user == null) {
            throw new BusinessException("用户不存在");
        }

        if (dto.getNickname() != null) {
            user.setNickname(dto.getNickname());
        }
        if (dto.getAvatar() != null) {
            user.setAvatar(dto.getAvatar());
        }
        if (dto.getEmail() != null) {
            user.setEmail(dto.getEmail());
        }

        user.setUpdatedAt(LocalDateTime.now());

        userMapper.updateById(user);

        return convertToVo(user);
    }

    private UserVo convertToVo(User user) {
        return UserVo.builder()
            .id(user.getId())
            .username(user.getUsername())
            .nickname(user.getNickname())
            .email(user.getEmail())
            .phone(user.getPhone())
            .avatar(user.getAvatar())
            .status(user.getStatus())
            .createdAt(user.getCreatedAt())
            .updatedAt(user.getUpdatedAt())
            .build();
    }
}
```

## 六、进阶功能

### 1. 多租户支持

```java
// 启用多租户插件
@MultiTenantService
@RequiredArgsConstructor
public class TenantAwareService {

    private final UserMapper userMapper;

    // TenantAware 查询
    @Override
    public List<User> getAllUsers() {
        List<User> allUsers = userMapper.selectList(null);
        // 自动过滤当前租户数据
        return allUsers;
    }
}
```

### 2. 软删除

```java
// 实体添加删除注解
@Table(name = "t_product")
@TableLogic(
    value = "deleted_at IS NOT NULL")
)
public class Product extends BaseEntity {

    @TableLogic(fill = FieldFill.Field(UPDATE))
    @TableLogic(fill = FieldFill.INSERT))
    private LocalDateTime deletedAt;
}
```

## 小结

本节补充了 MyBatis Plus 高级用法：

- **接口定义** - Mapper 接口
- **XML Mapper** - 自定义 SQL、联合查询
- **条件构造器** - Lambda 动态查询
- **代码生成器** - 自动生成注解、工具类
- **分页查询** - 手动分页工具类
- **批量操作** - 插入、更新、删除优化
- **项目技巧** - 批量处理、分批处理

## 实践练习

### 编程题
1. 使用 MyBatis Plus 的代码生成器生成一套完整的 CRUD 代码，然后自定义复杂查询：多表关联查询、动态条件查询、分页查询。
2. 实现 MyBatis 的一级缓存和二级缓存配置，验证不同作用域下的缓存命中情况。

### 思考题
1. MyBatis 中 `#{}` 和 `${}` 的区别？为什么推荐使用 `#{}`？
2. MyBatis Plus 相比原生 MyBatis 有哪些提升？在什么场景下仍需要手写 XML？

### 自测题
1. MyBatis 的核心组件有哪些？
2. MyBatis Plus 的 ActiveRecord 模式和 Mapper 模式有什么区别？
3. MyBatis 二级缓存的适用场景和注意事项？

下一步将学习项目实战（→ `project/beginner/01-ecommerce-project.md`）。