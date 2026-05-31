# MyBatis-Plus 实战

## 一、概述

MyBatis-Plus 是 MyBatis 的增强工具，提供了 CRUD 自动生成、分页、条件构造器、乐观锁等生产力特性。

## 二、快速集成

```xml
<dependency>
    <groupId>com.baomidou</groupId>
    <artifactId>mybatis-plus-boot-starter</artifactId>
    <version>3.5.5</version>
</dependency>
```

```yaml
mybatis-plus:
  global-config:
    db-config:
      id-type: auto                  # 主键自增
      logic-delete-field: deleted    # 逻辑删除字段
      logic-delete-value: 1
      logic-not-delete-value: 0
  configuration:
    map-underscore-to-camel-case: true
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl
  mapper-locations: classpath*:/mapper/**/*.xml
```

## 三、BaseMapper 与 Service

```java
// Entity
@Data
@TableName("user")
public class User {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String name;
    private Integer age;
    private String email;
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;
    @Version
    private Integer version;
    @TableLogic
    private Integer deleted;
}

// Mapper
@Mapper
public interface UserMapper extends BaseMapper<User> {
    // 继承的方法：
    // int insert(T entity)
    // int deleteById(Serializable id)
    // int updateById(T entity)
    // T selectById(Serializable id)
    // List<T> selectList(Wrapper<T> wrapper)
    // Page<T> selectPage(Page<T> page, Wrapper<T> wrapper)
}

// Service 层
@Service
public class UserService extends ServiceImpl<UserMapper, User> {
    // 继承的方法：
    // boolean save(T entity)
    // boolean saveBatch(Collection<T> entityList)
    // boolean updateById(T entity)
    // boolean removeById(Serializable id)
    // T getById(Serializable id)
    // List<T> list(Wrapper<T> wrapper)
    // Page<T> page(Page<T> page, Wrapper<T> wrapper)
}
```

## 四、条件构造器

```java
@Service
public class UserQueryService {

    // LambdaQueryWrapper（推荐，防止字段名写错）
    public List<User> findByCondition(UserQuery query) {
        return lambdaQuery()
            .like(StringUtils.hasText(query.getName()), User::getName, query.getName())
            .ge(query.getMinAge() != null, User::getAge, query.getMinAge())
            .le(query.getMaxAge() != null, User::getAge, query.getMaxAge())
            .eq(query.getEmail() != null, User::getEmail, query.getEmail())
            .orderByDesc(User::getCreateTime)
            .page(new Page<>(query.getPageNum(), query.getPageSize()))
            .getRecords();
    }

    // 复杂查询
    public List<UserVO> searchUsers(String keyword, Integer age, String email) {
        return baseMapper.selectUsers(new LambdaQueryWrapper<User>()
            .and(w -> w.like(User::getName, keyword)
                       .or().like(User::getEmail, keyword))
            .eq(age != null, User::getAge, age)
            .like(email != null, User::getEmail, email)
        );
    }

    // 动态 SQL
    public List<User> dynamicQuery(Map<String, Object> params) {
        return list(new QueryWrapper<User>()
            .allEq(params, false)  // 过滤 null 值
        );
    }
}
```

### 常用条件方法

| 方法 | 说明 | 示例 |
|------|------|------|
| eq | 等于 | eq(User::getName, "张三") |
| ne | 不等于 | ne(User::getAge, 18) |
| gt / ge | 大于 / 大于等于 | gt(User::getAge, 20) |
| lt / le | 小于 / 小于等于 | lt(User::getAge, 60) |
| like | LIKE '%值%' | like(User::getName, "张") |
| likeLeft | LIKE '%值' | likeLeft(User::getName, "张") |
| in / notIn | IN / NOT IN | in(User::getId, ids) |
| between | BETWEEN | between(User::getAge, 18, 60) |
| isNull / isNotNull | IS NULL | isNull(User::getEmail) |
| orderByDesc | ORDER BY DESC | orderByDesc(User::getCreateTime) |
| groupBy | GROUP BY | groupBy(User::getAge) |

## 五、分页插件

```java
@Configuration
@MapperScan("com.example.mapper")
public class MyBatisPlusConfig {
    @Bean
    public MybatisPlusInterceptor mybatisPlusInterceptor() {
        MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
        // 分页插件
        interceptor.addInnerInterceptor(new PaginationInnerInterceptor(DbType.MYSQL));
        // 乐观锁插件
        interceptor.addInnerInterceptor(new OptimisticLockerInnerInterceptor());
        return interceptor;
    }
}

// 使用分页
public Page<UserVO> pageUsers(int pageNum, int pageSize, String keyword) {
    Page<User> page = new Page<>(pageNum, pageSize);
    LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<User>()
        .like(StringUtils.hasText(keyword), User::getName, keyword);
    
    Page<User> result = baseMapper.selectPage(page, wrapper);
    
    // 转换为 VO
    Page<UserVO> voPage = new Page<>(result.getCurrent(), result.getSize(), result.getTotal());
    voPage.setRecords(result.getRecords().stream()
        .map(this::toVO).collect(Collectors.toList()));
    return voPage;
}
```

## 六、乐观锁

```java
// Entity 中添加 @Version
@Data
public class Product {
    private Long id;
    private String name;
    private Integer stock;
    @Version
    private Integer version;
}

// 使用乐观锁扣减库存
@Service
public class StockService {
    public boolean deductStock(Long productId, int quantity) {
        Product product = productMapper.selectById(productId);
        if (product.getStock() < quantity) {
            throw new BusinessException("库存不足");
        }
        product.setStock(product.getStock() - quantity);
        // 更新时自动检查 version，version 不匹配则更新 0 行
        int updated = productMapper.updateById(product);
        // 更新 0 行代表其他线程已修改，重试
        return updated > 0;
    }
}
```

## 七、代码生成器

```java
public class CodeGenerator {
    public static void main(String[] args) {
        FastAutoGenerator.create("jdbc:mysql://localhost:3306/db", "root", "123456")
            .globalConfig(builder -> builder
                .author("XiaoYi")
                .outputDir("/src/main/java")
                .enableSwagger()
            )
            .packageConfig(builder -> builder
                .parent("com.example")
                .entity("entity")
                .service("service")
                .controller("controller")
            )
            .strategyConfig(builder -> builder
                .addInclude("user", "order", "product")
                .entityBuilder().enableLombok()
                .serviceBuilder().formatServiceFileName("%sService")
            )
            .execute();
    }
}
```

## 课后练习

1. 使用 MyBatis-Plus 实现复杂报表查询（多表关联 + 聚合）
2. 实现基于乐观锁的秒杀库存扣减
3. 自定义一个 TypeHandler 处理 JSON 字段
4. 使用代码生成器生成完整的 CRUD 模块

## 自测题

1. MyBatis-Plus 中 @TableLogic 默认逻辑删除值？ A) 0-未删除 1-已删除 B) 1-未删除 0-已删除 C) true-删除 false-未 D) Y-删除 N-未
2. LambdaQueryWrapper 相比 QueryWrapper 的优势？ A) 性能更好 B) 编译期类型检查 C) SQL 注入防护 D) B+C
3. @Version 注解的字段在更新时的作用？ A) 自动递增 B) CAS 乐观锁 C) 悲观锁 D) 分布式锁

**答案：** 1-A, 2-D, 3-B
