# JavaSE 高级特性

## 一、泛型（Generics）

### 1. 泛型基础

```java
import java.util.*;

public class GenericsDemo {
    public static void main(String[] args) {
        // 泛型类
        Box<String> stringBox = new Box<>("Hello");
        Box<Integer> integerBox = new Box<>(100);

        System.out.println(stringBox.getT());
        System.out.println(integerBox.getT());

        // 泛型方法
        String str = printType("Generics");
        Integer num = printType(123);

        // 泛型接口
        Pair<String, Integer> pair = new OrderedPair<>("Score", 95);
        System.out.println(pair.getKey() + ": " + pair.getValue());

        // 通配符
        List<Integer> intList = Arrays.asList(1, 2, 3);
        List<Double> doubleList = Arrays.asList(1.5, 2.5, 3.5);

        printList(intList);
        printList(doubleList);

        // 上界通配符
        List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);
        double sum = sumOfList(numbers);
        System.out.println("\\nSum: " + sum);

        // 类型擦除
        typeErasureDemo();
    }

    // 泛型方法
    public static <T> T printType(T item) {
        System.out.println("Type: " + item.getClass().getSimpleName());
        return item;
    }

    // 通配符方法
    public static void printList(List<?> list) {
        for (Object item : list) {
            System.out.print(item + " ");
        }
        System.out.println();
    }

    // 上界通配符
    public static double sumOfList(List<? extends Number> list) {
        double sum = 0;
        for (Number number : list) {
            sum += number.doubleValue();
        }
        return sum;
    }

    // 类型擦除演示
    public static void typeErasureDemo() {
        List<String> stringList = new ArrayList<>();
        List<Integer> integerList = new ArrayList<>();

        // 运行时类型被擦除，都是 ArrayList
        System.out.println("\\n类型擦除:");
        System.out.println(stringList.getClass().getName());
        System.out.println(integerList.getClass().getName());
        System.out.println(stringList.getClass() == integerList.getClass());  // true
    }
}

// 泛型类
class Box<T> {
    private T t;

    public Box(T t) {
        this.t = t;
    }

    public T getT() {
        return t;
    }

    public void setT(T t) {
        this.t = t;
    }
}

// 多个类型参数
class Pair<K, V> {
    private K key;
    private V value;

    public Pair(K key, V value) {
        this.key = key;
        this.value = value;
    }

    public K getKey() { return key; }
    public V getValue() { return value; }
}

// 泛型接口
interface GenericPair<K, V> {
    K getKey();
    V getValue();
}

// 实现泛型接口
class OrderedPair<K, V> implements Pair<K, V> {
    private K key;
    private V value;

    public OrderedPair(K key, V value) {
        this.key = key;
        this.value = value;
    }

    public K getKey() { return key; }
    public V getValue() { return value; }
}
```

### 2. 泛型约束

```java
import java.util.*;

public class GenericsConstraintsDemo {
    public static void main(String[] args) {
        // 上界约束
        List<Integer> integers = Arrays.asList(1, 2, 3);
        System.out.println("Max: " + findMax(integers));

        List<String> strings = Arrays.asList("A", "B", "C");
        System.out.println("Max: " + findMax(strings));

        // 下界约束
        List<Number> numbers = new ArrayList<>();
        addNumbers(numbers, integers);
        addNumbers(numbers, Arrays.asList(1.5, 2.5));

        System.out.println("Numbers: " + numbers);
    }

    // 上界约束（extends）
    public static <T extends Comparable<T>> T findMax(List<T> list) {
        if (list.isEmpty()) {
            throw new IllegalArgumentException("List is empty");
        }

        T max = list.get(0);
        for (T item : list) {
            if (item.compareTo(max) > 0) {
                max = item;
            }
        }
        return max;
    }

    // 多个上界
    public static <T extends Number & Comparable<T>> T findMaxNumber(List<T> list) {
        if (list.isEmpty()) return null;

        T max = list.get(0);
        for (T item : list) {
            if (item.compareTo(max) > 0) {
                max = item;
            }
        }
        return max;
    }

    // 下界约束（super）- 只能用通配符
    public static void addNumbers(List<? super Integer> list, List<Integer> items) {
        list.addAll(items);
    }
}
```

## 二、反射（Reflection）

### 1. 反射基础

```java
import java.lang.reflect.*;
import java.util.*;

public class ReflectionDemo {
    public static void main(String[] args) throws Exception {
        // 获取 Class 对象的三种方式
        Class<?> clazz1 = String.class;
        Class<?> clazz2 = "Hello".getClass();
        Class<?> clazz3 = Class.forName("java.lang.String");

        System.out.println("Class name: " + clazz1.getName());
        System.out.println("Simple name: " + clazz1.getSimpleName());
        System.out.println("Package: " + clazz1.getPackage().getName());

        // 获取类的所有信息
        analyzeClass(Person.class);

        // 动态创建对象
        createObjectDynamically();

        // 动态调用方法
        invokeMethodDynamically();

        // 动态访问字段
        accessFieldDynamically();

        // 泛型类型擦除
        genericTypeErasure();

        // 注解处理
        processAnnotations();
    }

    // 分析类的所有信息
    public static void analyzeClass(Class<?> clazz) {
        System.out.println("\\n=== 分析类: " + clazz.getName() + " ===");

        // 父类
        Class<?> superClass = clazz.getSuperclass();
        System.out.println("父类: " + (superClass != null ? superClass.getName() : "无"));

        // 接口
        Class<?>[] interfaces = clazz.getInterfaces();
        System.out.println("实现的接口:");
        for (Class<?> iface : interfaces) {
            System.out.println("  - " + iface.getName());
        }

        // 构造器
        System.out.println("\\n构造器:");
        Constructor<?>[] constructors = clazz.getDeclaredConstructors();
        for (Constructor<?> constructor : constructors) {
            System.out.println("  " + constructor);
            System.out.println("    参数类型: " +
                Arrays.toString(constructor.getParameterTypes()));
        }

        // 字段
        System.out.println("\\n字段:");
        Field[] fields = clazz.getDeclaredFields();
        for (Field field : fields) {
            System.out.println("  " + Modifier.toString(field.getModifiers()) + " " +
                field.getType().getSimpleName() + " " + field.getName());
        }

        // 方法
        System.out.println("\\n方法:");
        Method[] methods = clazz.getDeclaredMethods();
        for (Method method : methods) {
            System.out.println("  " + Modifier.toString(method.getModifiers()) + " " +
                method.getReturnType().getSimpleName() + " " +
                method.getName() + "(" +
                Arrays.toString(method.getParameterTypes()) + ")");
        }
    }

    // 动态创建对象
    public static void createObjectDynamically() throws Exception {
        System.out.println("\\n=== 动态创建对象 ===");

        // 方式1: 使用 Class.newInstance()（已过时）
        // Person person1 = Person.class.newInstance();

        // 方式2: 使用 Constructor
        Constructor<Person> constructor = Person.class.getDeclaredConstructor(
            String.class, int.class
        );
        Person person = constructor.newInstance("张三", 25);

        System.out.println("创建的对象: " + person);

        // 调用私有构造器
        Constructor<Person> privateConstructor = Person.class.getDeclaredConstructor();
        privateConstructor.setAccessible(true);  // 暴力反射
        Person person2 = privateConstructor.newInstance();
        System.out.println("私有构造器创建的对象: " + person2);
    }

    // 动态调用方法
    public static void invokeMethodDynamically() throws Exception {
        System.out.println("\\n=== 动态调用方法 ===");

        Person person = new Person("李四", 30);

        // 调用公共方法
        Method sayHelloMethod = Person.class.getMethod("sayHello", String.class);
        String result = (String) sayHelloMethod.invoke(person, "World");
        System.out.println("sayHello 结果: " + result);

        // 调用私有方法
        Method privateMethod = Person.class.getDeclaredMethod("privateMethod");
        privateMethod.setAccessible(true);
        privateMethod.invoke(person);

        // 调用静态方法
        Method staticMethod = Person.class.getMethod("staticMethod");
        staticMethod.invoke(null);
    }

    // 动态访问字段
    public static void accessFieldDynamically() throws Exception {
        System.out.println("\\n=== 动态访问字段 ===");

        Person person = new Person("王五", 28);

        // 获取字段值
        Field nameField = Person.class.getDeclaredField("name");
        nameField.setAccessible(true);
        String name = (String) nameField.get(person);
        System.out.println("name 字段值: " + name);

        // 设置字段值
        nameField.set(person, "赵六");
        System.out.println("修改后的 name: " + person.getName());

        // 访问静态字段
        Field staticField = Person.class.getDeclaredField("STATIC_FIELD");
        staticField.setAccessible(true);
        staticField.set(null, "修改后的静态值");
        System.out.println("静态字段: " + Person.getStaticField());
    }

    // 泛型类型擦除
    public static void genericTypeErasure() throws Exception {
        System.out.println("\\n=== 泛型类型擦除 ===");

        // 定义泛型类
        class GenericBox<T> {
            private T value;
            public void setValue(T value) { this.value = value; }
            public T getValue() { return value; }
        }

        GenericBox<String> stringBox = new GenericBox<>();
        stringBox.setValue("Hello");

        // 获取字段的实际类型
        Field valueField = GenericBox.class.getDeclaredField("value");
        Type genericType = valueField.getGenericType();
        System.out.println("字段类型: " + genericType);

        // 获取方法的泛型返回类型
        Method getValueMethod = GenericBox.class.getMethod("getValue");
        Type returnType = getValueMethod.getGenericReturnType();
        System.out.println("方法返回类型: " + returnType);
    }

    // 注解处理
    public static void processAnnotations() throws Exception {
        System.out.println("\\n=== 注解处理 ===");

        Class<?> clazz = AnnotatedClass.class;

        // 类级别的注解
        if (clazz.isAnnotationPresent(MyAnnotation.class)) {
            MyAnnotation annotation = clazz.getAnnotation(MyAnnotation.class);
            System.out.println("类注解: " + annotation.value());
        }

        // 方法级别的注解
        Method[] methods = clazz.getDeclaredMethods();
        for (Method method : methods) {
            if (method.isAnnotationPresent(MyAnnotation.class)) {
                MyAnnotation annotation = method.getAnnotation(MyAnnotation.class);
                System.out.println("方法 " + method.getName() + " 注解: " + annotation.value());
            }
        }

        // 字段级别的注解
        Field[] fields = clazz.getDeclaredFields();
        for (Field field : fields) {
            if (field.isAnnotationPresent(MyAnnotation.class)) {
                MyAnnotation annotation = field.getAnnotation(MyAnnotation.class);
                System.out.println("字段 " + field.getName() + " 注解: " + annotation.value());
            }
        }
    }
}

// 测试类
class Person {
    private static String STATIC_FIELD = "静态字段";
    private String name;
    private int age;

    public Person() {}

    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public int getAge() {
        return age;
    }

    public void setAge(int age) {
        this.age = age;
    }

    public String sayHello(String target) {
        return "Hello, " + target + "! My name is " + name;
    }

    private void privateMethod() {
        System.out.println("这是私有方法");
    }

    public static void staticMethod() {
        System.out.println("这是静态方法");
    }

    public static String getStaticField() {
        return STATIC_FIELD;
    }

    @Override
    public String toString() {
        return "Person{name='" + name + "', age=" + age + "}";
    }
}

// 自定义注解
@Retention(RetentionPolicy.RUNTIME)
@Target({ElementType.TYPE, ElementType.METHOD, ElementType.FIELD})
@interface MyAnnotation {
    String value() default "";
    int priority() default 0;
}

// 使用注解的类
@MyAnnotation(value = "Annotated Class", priority = 1)
class AnnotatedClass {
    @MyAnnotation(value = "Annotated Field")
    private String field;

    @MyAnnotation(value = "Annotated Method", priority = 2)
    public void annotatedMethod() {}
}
```

## 三、注解（Annotations）

```java
import java.lang.annotation.*;
import java.lang.reflect.*;

public class AnnotationDemo {
    public static void main(String[] args) throws Exception {
        // 运行时处理注解
        processRuntimeAnnotations();

        // 使用注解进行验证
        annotationValidation();

        // 自定义注解处理器
        customAnnotationProcessor();
    }

    // 运行时注解处理
    public static void processRuntimeAnnotations() throws Exception {
        System.out.println("=== 运行时注解处理 ===");

        Class<?> clazz = User.class;

        // 获取类注解
        Entity entity = clazz.getAnnotation(Entity.class);
        if (entity != null) {
            System.out.println("表名: " + entity.tableName());
        }

        // 获取所有字段
        Field[] fields = clazz.getDeclaredFields();
        for (Field field : fields) {
            // Id 注解
            Id idAnnotation = field.getAnnotation(Id.class);
            if (idAnnotation != null) {
                System.out.println("主键字段: " + field.getName());
            }

            // Column 注解
            Column column = field.getAnnotation(Column.class);
            if (column != null) {
                System.out.println("字段: " + field.getName() +
                    ", 列名: " + column.name() +
                    ", 长度: " + column.length());
            }

            // NotNull 注解
            NotNull notNull = field.getAnnotation(NotNull.class);
            if (notNull != null) {
                System.out.println("  字段 " + field.getName() + " 不能为空");
            }
        }
    }

    // 注解验证
    public static void annotationValidation() {
        System.out.println("\\n=== 注解验证 ===");

        Order order = new Order("", -1, "");

        // 验证
        Validator.validate(order);
    }

    // 自定义注解处理器
    public static void customAnnotationProcessor() throws Exception {
        System.out.println("\\n=== 自定义注解处理器 ===");

        Class<?> clazz = ProcessedClass.class;
        Object obj = clazz.newInstance();

        // 处理所有带 @Process 注解的方法
        Method[] methods = clazz.getDeclaredMethods();
        for (Method method : methods) {
            Process process = method.getAnnotation(Process.class);
            if (process != null) {
                method.setAccessible(true);
                method.invoke(obj);
                System.out.println("处理方法: " + method.getName() +
                    ", 优先级: " + process.priority());
            }
        }
    }
}

// 常用注解定义
@Entity(tableName = "t_user")
class User {
    @Id
    @Column(name = "id", length = 20)
    private Long id;

    @Column(name = "username", length = 50)
    @NotNull(message = "用户名不能为空")
    private String username;

    @Column(name = "age")
    @Min(value = 0, message = "年龄不能小于0")
    @Max(value = 150, message = "年龄不能大于150")
    private Integer age;

    // getters and setters
}

// 注解定义
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
@interface Entity {
    String tableName() default "";
}

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface Id {}

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface Column {
    String name() default "";
    int length() default 255;
}

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface NotNull {
    String message() default "不能为空";
}

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface Min {
    int value();
    String message() default "";
}

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface Max {
    int value();
    String message() default "";
}

// 验证器
class Validator {
    public static void validate(Object obj) {
        Class<?> clazz = obj.getClass();
        Field[] fields = clazz.getDeclaredFields();

        for (Field field : fields) {
            field.setAccessible(true);

            try {
                Object value = field.get(obj);

                // NotNull 验证
                NotNull notNull = field.getAnnotation(NotNull.class);
                if (notNull != null && (value == null ||
                    (value instanceof String && ((String) value).isEmpty()))) {
                    System.out.println(notNull.message());
                }

                // Min 验证
                Min min = field.getAnnotation(Min.class);
                if (min != null && value instanceof Number) {
                    Number num = (Number) value;
                    if (num.doubleValue() < min.value()) {
                        System.out.println(min.message());
                    }
                }

                // Max 验证
                Max max = field.getAnnotation(Max.class);
                if (max != null && value instanceof Number) {
                    Number num = (Number) value;
                    if (num.doubleValue() > max.value()) {
                        System.out.println(max.message());
                    }
                }

            } catch (IllegalAccessException e) {
                e.printStackTrace();
            }
        }
    }
}

// 测试类
class Order {
    @NotNull(message = "订单号不能为空")
    private String orderId;

    @Min(value = 1, message = "金额不能小于1")
    private double amount;

    @NotNull(message = "客户不能为空")
    private String customer;

    public Order(String orderId, double amount, String customer) {
        this.orderId = orderId;
        this.amount = amount;
        this.customer = customer;
    }
}

// 自定义处理注解
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
@interface Process {
    int priority() default 0;
}

class ProcessedClass {
    @Process(priority = 1)
    private void method1() {
        System.out.println("执行方法1");
    }

    @Process(priority = 2)
    private void method2() {
        System.out.println("执行方法2");
    }
}
```

## 四、IO 流（Input/Output）

### 1. 字节流

```java
import java.io.*;
import java.nio.file.*;
import java.util.*;

public class ByteStreamDemo {
    public static void main(String[] args) throws Exception {
        // 文件读写
        fileReadWrite();

        // 文件复制
        fileCopy();

        // 内存操作流
        memoryStream();

        // 缓冲流
        bufferedStream();

        // 数据流
        dataStream();

        // 对象流（序列化）
        objectStream();
    }

    // 文件读写
    public static void fileReadWrite() throws Exception {
        System.out.println("=== 文件读写 ===");

        // 写文件
        try (FileOutputStream fos = new FileOutputStream("test.txt")) {
            String content = "Hello, World!\\n你好，世界！";
            fos.write(content.getBytes());
        }

        // 读文件
        try (FileInputStream fis = new FileInputStream("test.txt")) {
            byte[] buffer = new byte[1024];
            int len;
            StringBuilder sb = new StringBuilder();

            while ((len = fis.read(buffer)) != -1) {
                sb.append(new String(buffer, 0, len));
            }

            System.out.println(sb.toString());
        }

        // 使用 Files API（Java 7+）
        Path path = Paths.get("test2.txt");
        Files.write(path, "使用 Files API 写入".getBytes());

        List<String> lines = Files.readAllLines(path);
        System.out.println("文件内容: " + lines.get(0));
    }

    // 文件复制
    public static void fileCopy() throws Exception {
        System.out.println("\\n=== 文件复制 ===");

        // 方式1：传统方式
        long start = System.currentTimeMillis();
        try (FileInputStream fis = new FileInputStream("test.txt");
             FileOutputStream fos = new FileOutputStream("test_copy1.txt")) {

            byte[] buffer = new byte[1024];
            int len;
            while ((len = fis.read(buffer)) != -1) {
                fos.write(buffer, 0, len);
            }
        }
        System.out.println("传统复制耗时: " + (System.currentTimeMillis() - start) + "ms");

        // 方式2：缓冲流
        start = System.currentTimeMillis();
        try (BufferedInputStream bis = new BufferedInputStream(new FileInputStream("test.txt"));
             BufferedOutputStream bos = new BufferedOutputStream(new FileOutputStream("test_copy2.txt"))) {

            byte[] buffer = new byte[1024];
            int len;
            while ((len = bis.read(buffer)) != -1) {
                bos.write(buffer, 0, len);
            }
        }
        System.out.println("缓冲流复制耗时: " + (System.currentTimeMillis() - start) + "ms");

        // 方式3：NIO Files.copy
        start = System.currentTimeMillis();
        Files.copy(Paths.get("test.txt"), Paths.get("test_copy3.txt"));
        System.out.println("Files.copy 耗时: " + (System.currentTimeMillis() - start) + "ms");

        // 方式4：FileChannel
        start = System.currentTimeMillis();
        try (FileChannel srcChannel = new FileInputStream("test.txt").getChannel();
             FileChannel destChannel = new FileOutputStream("test_copy4.txt").getChannel()) {

            destChannel.transferFrom(srcChannel, 0, srcChannel.size());
        }
        System.out.println("FileChannel 耗时: " + (System.currentTimeMillis() - start) + "ms");
    }

    // 内存操作流
    public static void memoryStream() throws Exception {
        System.out.println("\\n=== 内存操作流 ===");

        // ByteArrayOutputStream
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        baos.write("Hello".getBytes());
        baos.write(" ".getBytes());
        baos.write("World".getBytes());

        byte[] data = baos.toByteArray();
        System.out.println("内存数据: " + new String(data));

        // ByteArrayInputStream
        ByteArrayInputStream bais = new ByteArrayInputStream(data);
        int ch;
        while ((ch = bais.read()) != -1) {
            System.out.print((char) ch);
        }
        System.out.println();
    }

    // 缓冲流
    public static void bufferedStream() throws Exception {
        System.out.println("\\n=== 缓冲流 ===");

        // 性能对比
        int size = 1000000;
        byte[] data = new byte[size];
        new Random().nextBytes(data);

        // 不使用缓冲
        long start = System.currentTimeMillis();
        try (FileOutputStream fos = new FileOutputStream("large1.dat")) {
            fos.write(data);
        }
        long time1 = System.currentTimeMillis() - start;

        // 使用缓冲
        start = System.currentTimeMillis();
        try (BufferedOutputStream bos = new BufferedOutputStream(
                new FileOutputStream("large2.dat"))) {
            bos.write(data);
        }
        long time2 = System.currentTimeMillis() - start;

        System.out.printf("不缓冲: %dms, 缓冲: %dms\\n", time1, time2);
    }

    // 数据流
    public static void dataStream() throws Exception {
        System.out.println("\\n=== 数据流 ===");

        // 写入各种类型数据
        try (DataOutputStream dos = new DataOutputStream(
                new FileOutputStream("data.dat"))) {
            dos.writeInt(100);
            dos.writeDouble(3.14);
            dos.writeUTF("Hello");
            dos.writeBoolean(true);
        }

        // 读取各种类型数据
        try (DataInputStream dis = new DataInputStream(
                new FileInputStream("data.dat"))) {
            int i = dis.readInt();
            double d = dis.readDouble();
            String s = dis.readUTF();
            boolean b = dis.readBoolean();

            System.out.printf("int=%d, double=%.2f, string=%s, boolean=%b\\n",
                i, d, s, b);
        }
    }

    // 对象流（序列化）
    public static void objectStream() throws Exception {
        System.out.println("\\n=== 对象流 ===");

        // 序列化
        Person person = new Person("张三", 25);
        try (ObjectOutputStream oos = new ObjectOutputStream(
                new FileOutputStream("person.obj"))) {
            oos.writeObject(person);
        }

        // 反序列化
        try (ObjectInputStream ois = new ObjectInputStream(
                new FileInputStream("person.obj"))) {
            Person deserialized = (Person) ois.readObject();
            System.out.println("反序列化: " + deserialized);
        }
    }
}

// 可序列化的类
class Person implements Serializable {
    private static final long serialVersionUID = 1L;
    private String name;
    private int age;
    transient private String secret = "机密信息";  // transient 不会被序列化

    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }

    @Override
    public String toString() {
        return "Person{name='" + name + "', age=" + age + "}";
    }
}
```

### 2. 字符流

```java
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

public class CharStreamDemo {
    public static void main(String[] args) throws Exception {
        // 字符流读写
        charStreamReadWrite();

        // 按行读写
        readWriteByLine();

        // 字符缓冲流
        bufferedCharStream();

        // 字符集处理
        charsetHandling();

        // 文件操作
        fileOperations();
    }

    // 字符流读写
    public static void charStreamReadWrite() throws Exception {
        System.out.println("=== 字符流读写 ===");

        // 写文件
        try (FileWriter fw = new FileWriter("char_test.txt")) {
            fw.write("Hello, World!\\n");
            fw.write("你好，世界！\\n");
            fw.write("Java 字符流");
        }

        // 读文件
        try (FileReader fr = new FileReader("char_test.txt")) {
            int ch;
            while ((ch = fr.read()) != -1) {
                System.out.print((char) ch);
            }
        }
        System.out.println();

        // 使用指定字符集
        try (OutputStreamWriter osw = new OutputStreamWriter(
                new FileOutputStream("utf8_test.txt"), StandardCharsets.UTF_8)) {
            osw.write("UTF-8 编码测试");
        }

        try (InputStreamReader isr = new InputStreamReader(
                new FileInputStream("utf8_test.txt"), StandardCharsets.UTF_8)) {
            char[] buffer = new char[1024];
            int len;
            StringBuilder sb = new StringBuilder();
            while ((len = isr.read(buffer)) != -1) {
                sb.append(buffer, 0, len);
            }
            System.out.println(sb.toString());
        }
    }

    // 按行读写
    public static void readWriteByLine() throws Exception {
        System.out.println("\\n=== 按行读写 ===");

        // 写入多行
        List<String> lines = Arrays.asList(
            "第一行",
            "第二行",
            "第三行"
        );

        try (BufferedWriter bw = new BufferedWriter(new FileWriter("lines.txt"))) {
            for (String line : lines) {
                bw.write(line);
                bw.newLine();  // 写入换行符
            }
        }

        // 读取多行
        try (BufferedReader br = new BufferedReader(new FileReader("lines.txt"))) {
            String line;
            while ((line = br.readLine()) != null) {
                System.out.println(line);
            }
        }
    }

    // 字符缓冲流
    public static void bufferedCharStream() throws Exception {
        System.out.println("\\n=== 字符缓冲流 ===");

        // 性能对比
        int lines = 10000;
        List<String> content = new ArrayList<>();
        for (int i = 0; i < lines; i++) {
            content.add("Line " + i);
        }

        // 不使用缓冲
        long start = System.currentTimeMillis();
        try (FileWriter fw = new FileWriter("unbuffered.txt")) {
            for (String line : content) {
                fw.write(line + "\\n");
            }
        }
        long time1 = System.currentTimeMillis() - start;

        // 使用缓冲
        start = System.currentTimeMillis();
        try (BufferedWriter bw = new BufferedWriter(new FileWriter("buffered.txt"))) {
            for (String line : content) {
                bw.write(line);
                bw.newLine();
            }
        }
        long time2 = System.currentTimeMillis() - start;

        System.out.printf("不缓冲: %dms, 缓冲: %dms\\n", time1, time2);
    }

    // 字符集处理
    public static void charsetHandling() throws Exception {
        System.out.println("\\n=== 字符集处理 ===");

        // 获取可用字符集
        SortedMap<String, Charset> charsets = Charset.availableCharsets();
        System.out.println("可用字符集数量: " + charsets.size());

        // 常用字符集
        String text = "中文测试";
        for (String charsetName : Arrays.asList("UTF-8", "GBK", "ISO-8859-1")) {
            byte[] bytes = text.getBytes(charsetName);
            String decoded = new String(bytes, charsetName);
            boolean same = text.equals(decoded);

            System.out.printf("%-10s: 原始=%s, 解码=%s, 相同=%b\\n",
                charsetName, text, decoded, same);
        }
    }

    // 文件操作
    public static void fileOperations() throws Exception {
        System.out.println("\\n=== 文件操作 ===");

        Path dir = Paths.get("test_dir");
        Path file = dir.resolve("test.txt");

        // 创建目录
        if (!Files.exists(dir)) {
            Files.createDirectories(dir);
        }

        // 写入文件
        Files.write(file, "文件内容".getBytes());

        // 文件信息
        System.out.println("是否存在: " + Files.exists(file));
        System.out.println("是否可读: " + Files.isReadable(file));
        System.out.println("是否可写: " + Files.isWritable(file));
        System.out.println("文件大小: " + Files.size(file) + " bytes");
        System.out.println("最后修改: " + Files.getLastModifiedTime(file));

        // 遍历目录
        System.out.println("\\n目录内容:");
        try (DirectoryStream<Path> stream = Files.newDirectoryStream(dir)) {
            for (Path entry : stream) {
                System.out.println("  " + entry.getFileName() +
                    " (" + (Files.isDirectory(entry) ? "目录" : "文件") + ")");
            }
        }

        // 复制、移动、删除
        Path copy = dir.resolve("test_copy.txt");
        Files.copy(file, copy, StandardCopyOption.REPLACE_EXISTING);

        Path move = dir.resolve("test_moved.txt");
        Files.move(copy, move, StandardCopyOption.REPLACE_EXISTING);

        // Files.delete(move);

        // 查找文件
        System.out.println("\\n查找 .txt 文件:");
        Files.walk(dir)
            .filter(p -> p.toString().endsWith(".txt"))
            .forEach(p -> System.out.println("  " + p));

        // 清理
        Files.walk(dir)
            .sorted(Comparator.reverseOrder())
            .forEach(p -> {
                try {
                    Files.delete(p);
                } catch (IOException e) {
                    e.printStackTrace();
                }
            });
    }
}
```

##  解压缩流

```
// 解压 / 压缩 流 java标准库只内置ZIP压缩包的原生支持 
        public static void toZip(File src, zipOutputStream zos, String name) throws IOException {
            File[] files = src.listFiles();
            for (File file : files) {
                if (file.isFile()) {
                    ZipEntry entry = new ZipEntry(name + "\\" + file.getName());
                    zos.putNextEntry(entry);
                    FileInputStream fis = new FileInputStream(file);
                    int b;
                    while ((b = fis.read()) != -1) {
                        zos.write(b);
                    }
                    fis.close();
                    zos.closeEntry();
                } else {
                    toZip(file, zos, name + "\\" + file.getName());
                }
            }
        }

        File src = new File("path/filename");
        File destParent = src.getParentFile();
        File dest = new File(destParent, src.getName() + ".zip");
        ZipOutputStream zos = new ZipOutputStream(new FileOutputStream(dest));
        toZip(src, zos, src.getName());
        zos.close();
```

## 五、NIO（New IO）

```java
import java.io.*;
import java.nio.*;
import java.nio.channels.*;
import java.nio.file.*;
import java.util.*;

public class NIODemo {
    public static void main(String[] args) throws Exception {
        // Buffer 操作
        bufferOperations();

        // Channel 操作
        channelOperations();

        // 文件锁
        fileLock();

        // 内存映射文件
        mappedFile();

        // 异步IO
        asyncIO();
    }

    // Buffer 操作
    public static void bufferOperations() {
        System.out.println("=== Buffer 操作 ===");

        // 创建 ByteBuffer
        ByteBuffer buffer = ByteBuffer.allocate(1024);
        System.out.println("初始状态:");
        System.out.printf("capacity=%d, position=%d, limit=%d\\n",
            buffer.capacity(), buffer.position(), buffer.limit());

        // 写入数据
        buffer.put("Hello".getBytes());
        System.out.println("\\n写入后:");
        System.out.printf("capacity=%d, position=%d, limit=%d\\n",
            buffer.capacity(), buffer.position(), buffer.limit());

        // 切换为读模式
        buffer.flip();
        System.out.println("\\nflip后:");
        System.out.printf("capacity=%d, position=%d, limit=%d\\n",
            buffer.capacity(), buffer.position(), buffer.limit());

        // 读取数据
        byte[] data = new byte[buffer.remaining()];
        buffer.get(data);
        System.out.println("读取内容: " + new String(data));

        // 重置
        buffer.clear();
        System.out.println("\\nclear后:");
        System.out.printf("capacity=%d, position=%d, limit=%d\\n",
            buffer.capacity(), buffer.position(), buffer.limit());

        // 其他 Buffer 类型
        CharBuffer charBuffer = CharBuffer.allocate(100);
        IntBuffer intBuffer = IntBuffer.allocate(100);
        DoubleBuffer doubleBuffer = DoubleBuffer.allocate(100);

        // 直接 Buffer（零拷贝）
        ByteBuffer directBuffer = ByteBuffer.allocateDirect(1024);
        System.out.println("\\n是否为直接 Buffer: " + directBuffer.isDirect());
    }

    // Channel 操作
    public static void channelOperations() throws Exception {
        System.out.println("\\n=== Channel 操作 ===");

        // 准备数据
        byte[] data = "Hello, Channel!".getBytes();

        // FileChannel 写入
        try (RandomAccessFile file = new RandomAccessFile("channel_test.txt", "rw");
             FileChannel channel = file.getChannel()) {

            // 使用 Buffer 写入
            ByteBuffer buffer = ByteBuffer.wrap(data);
            channel.write(buffer);

            System.out.println("写入位置: " + channel.position());
        }

        // FileChannel 读取
        try (RandomAccessFile file = new RandomAccessFile("channel_test.txt", "r");
             FileChannel channel = file.getChannel()) {

            ByteBuffer buffer = ByteBuffer.allocate(1024);
            channel.read(buffer);

            buffer.flip();
            System.out.println("读取内容: " + new String(buffer.array(), 0, buffer.limit()));
        }

        // 分散读取和聚集写入
        scatterGather();
    }

    // 分散读取和聚集写入
    public static void scatterGather() throws Exception {
        System.out.println("\\n=== 分散读取和聚集写入 ===");

        // 准备文件
        String content = "Part1 Part2 Part3";
        Files.write(Paths.get("scatter_test.txt"), content.getBytes());

        // 分散读取（Scattering Reads）
        try (FileChannel channel = FileChannel.open(
                Paths.get("scatter_test.txt"),
                StandardOpenOption.READ)) {

            ByteBuffer buffer1 = ByteBuffer.allocate(5);
            ByteBuffer buffer2 = ByteBuffer.allocate(10);
            ByteBuffer buffer3 = ByteBuffer.allocate(10);

            ByteBuffer[] buffers = {buffer1, buffer2, buffer3};
            channel.read(buffers);

            System.out.println("Buffer1: " + new String(buffer1.array(), 0, buffer1.position()));
            System.out.println("Buffer2: " + new String(buffer2.array(), 0, buffer2.position()));
            System.out.println("Buffer3: " + new String(buffer3.array(), 0, buffer3.position()));
        }

        // 聚集写入（Gathering Writes）
        try (FileChannel channel = FileChannel.open(
                Paths.get("gather_test.txt"),
                StandardOpenOption.WRITE,
                StandardOpenOption.CREATE)) {

            ByteBuffer part1 = ByteBuffer.wrap("First".getBytes());
            ByteBuffer part2 = ByteBuffer.wrap("Second".getBytes());
            ByteBuffer part3 = ByteBuffer.wrap("Third".getBytes());

            ByteBuffer[] buffers = {part1, part2, part3};
            channel.write(buffers);

            System.out.println("聚集写入完成");
        }
    }

    // 文件锁
    public static void fileLock() throws Exception {
        System.out.println("\\n=== 文件锁 ===");

        try (RandomAccessFile file = new RandomAccessFile("lock_test.txt", "rw");
             FileChannel channel = file.getChannel()) {

            // 获取文件锁
            FileLock lock = channel.tryLock();
            if (lock != null) {
                System.out.println("获取文件锁成功");

                try {
                    Thread.sleep(2000);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }

                lock.release();
                System.out.println("释放文件锁");
            } else {
                System.out.println("获取文件锁失败");
            }
        }
    }

    // 内存映射文件
    public static void mappedFile() throws Exception {
        System.out.println("\\n=== 内存映射文件 ===");

        // 写入文件
        try (RandomAccessFile file = new RandomAccessFile("mmap_test.txt", "rw");
             FileChannel channel = file.getChannel()) {

            // 映射文件到内存
            MappedByteBuffer buffer = channel.map(
                FileChannel.MapMode.READ_WRITE, 0, 1024);

            // 直接操作内存
            buffer.put(0, (byte) 'H');
            buffer.put(1, (byte) 'e');
            buffer.put(2, (byte) 'l');
            buffer.put(3, (byte) 'l');
            buffer.put(4, (byte) 'o');

            System.out.println("内存映射写入完成");
        }

        // 读取文件
        try (FileChannel channel = FileChannel.open(
                Paths.get("mmap_test.txt"),
                StandardOpenOption.READ)) {

            MappedByteBuffer buffer = channel.map(
                FileChannel.MapMode.READ_ONLY, 0, 1024);

            byte[] data = new byte[5];
            buffer.get(data);
            System.out.println("读取内容: " + new String(data));
        }
    }

    // 异步IO
    public static void asyncIO() throws Exception {
        System.out.println("\\n=== 异步IO ===");

        AsynchronousFileChannel channel = AsynchronousFileChannel.open(
            Paths.get("async_test.txt"),
            StandardOpenOption.WRITE,
            StandardOpenOption.CREATE);

        // 异步写入
        ByteBuffer buffer = ByteBuffer.wrap("Async IO Test".getBytes());
        Future<Integer> writeResult = channel.write(buffer, 0);

        while (!writeResult.isDone()) {
            System.out.println("写入中...");
        }

        System.out.println("写入完成，字节数: " + writeResult.get());

        // 异步读取
        channel = AsynchronousFileChannel.open(
            Paths.get("async_test.txt"),
            StandardOpenOption.READ);

        ByteBuffer readBuffer = ByteBuffer.allocate(1024);
        Future<Integer> readResult = channel.read(readBuffer, 0);

        while (!readResult.isDone()) {
            System.out.println("读取中...");
        }

        readBuffer.flip();
        System.out.println("读取内容: " + new String(readBuffer.array(), 0, readResult.limit()));

        channel.close();
    }
}
```

## 小结

本节学习了 JavaSE 高级特性：

- **泛型** - 泛型类、方法、约束、通配符
- **反射** - 动态获取类信息、创建对象、调用方法
- **注解** - 自定义注解、运行时处理、验证
- **IO 流** - 字节流、字符流、NIO、异步IO
- **实战应用** - 各种场景的完整代码示例

## 实践练习

### 编程题
1. 使用反射实现一个简单的依赖注入框架：扫描指定包下的类，自动发现带 `@Inject` 注解的字段并注入实例。
2. 使用 NIO 的 FileChannel 实现一个高性能的大文件复制工具，支持进度显示和断点续传。

### 思考题
1. 泛型类型擦除有什么影响？为什么 Java 选择类型擦除而不是真泛型？
2. 反射的性能开销有多大？在什么场景下应该避免使用反射？

### 自测题
1. `? extends T` 和 `? super T` 的区别是什么？（PECS 原则）
2. 创建 Class 对象有哪三种方式？
3. NIO 的 Buffer 有哪三个核心属性？`flip()` 和 `clear()` 的区别？

下一步将学习 Java 并发编程（→ `04-java-concurrency.md`）。