# JavaSE 基础入门

## 一、Java 环境搭建

### 1. JDK 安装与配置

```bash
# 下载 JDK (推荐 JDK 17 或 21 LTS)
https://www.oracle.com/java/technologies/downloads/

# Linux/Mac 配置环境变量
export JAVA_HOME=/path/to/jdk
export PATH=$JAVA_HOME/bin:$PATH
export CLASSPATH=.:$JAVA_HOME/lib/dt.jar:$JAVA_HOME/lib/tools.jar

# Windows 配置环境变量
# 系统属性 -> 环境变量
# JAVA_HOME = C:\Program Files\Java\jdk-17
# PATH = %JAVA_HOME%\bin
# CLASSPATH = .;%JAVA_HOME%\lib\dt.jar;%JAVA_HOME%\lib\tools.jar

# 验证安装
java -version
javac -version
```

### 2. 第一个 Java 程序

```java
// Hello.java
public class Hello {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
        System.out.println("Hello, Java!");
    }
}

// 编译
javac Hello.java

// 运行
java Hello
```

## 二、Java 基础语法

### 1. 变量与数据类型

```java
public class DataTypeDemo {
    public static void main(String[] args) {
        // 八大基本数据类型
        byte b = 127;                    // 1字节，-128到127
        short s = 32767;                 // 2字节，-32768到32767
        int i = 2147483647;              // 4字节，约21亿
        long l = 9223372036854775807L;   // 8字节，需要L后缀

        float f = 3.14f;                 // 4字节，需要f后缀
        double d = 3.141592653589793;    // 8字节，默认类型

        char c = 'A';                    // 2字节，Unicode字符
        boolean flag = true;             // 1字节，true/false

        // 引用数据类型
        String str = "Hello, Java!";     // 字符串
        int[] arr = {1, 2, 3, 4, 5};     // 数组

        // 类型转换
        // 自动类型提升
        int num1 = 100;
        double num2 = num1;              // int -> double 自动转换

        // 强制类型转换
        double num3 = 99.99;
        int num4 = (int) num3;           // 99，小数部分丢失

        // 类型溢出
        int max = Integer.MAX_VALUE;
        int overflow = max + 1;          // -2147483648
    }
}
```

### 2. 运算符

```java
public class OperatorDemo {
    public static void main(String[] args) {
        // 算术运算符
        int a = 10, b = 3;
        System.out.println(a + b);       // 13，加法
        System.out.println(a - b);       // 7，减法
        System.out.println(a * b);       // 30，乘法
        System.out.println(a / b);       // 3，整数除法
        System.out.println(a % b);       // 1，取余

        // 自增自减
        int x = 5;
        System.out.println(x++);         // 5，先使用后自增
        System.out.println(x);           // 6
        System.out.println(++x);         // 7，先自增后使用

        // 比较运算符
        System.out.println(a == b);      // false，等于
        System.out.println(a != b);      // true，不等于
        System.out.println(a > b);       // true，大于
        System.out.println(a >= b);      // true，大于等于

        // 逻辑运算符
        boolean m = true, n = false;
        System.out.println(m && n);      // false，逻辑与（短路）
        System.out.println(m || n);      // true，逻辑或（短路）
        System.out.println(!m);          // false，逻辑非
        System.out.println(m & n);       // false，按位与（不短路）

        // 三目运算符
        int max = (a > b) ? a : b;       // 10，a大返回a，否则返回b

        // 位运算符
        int bit1 = 5;     // 101
        int bit2 = 3;     // 011
        System.out.println(bit1 & bit2); // 1，按位与 001
        System.out.println(bit1 | bit2); // 7，按位或 111
        System.out.println(bit1 ^ bit2); // 6，按位异或 110
        System.out.println(~bit1);       // -6，按位取反
        System.out.println(bit1 << 1);   // 10，左移1位
        System.out.println(bit1 >> 1);   // 2，右移1位
        System.out.println(bit1 >>> 1);  // 2，无符号右移
    }
}
```

### 3. 流程控制

```java
public class ControlFlowDemo {
    public static void main(String[] args) {
        // if-else 语句
        int score = 85;
        if (score >= 90) {
            System.out.println("优秀");
        } else if (score >= 80) {
            System.out.println("良好");
        } else if (score >= 60) {
            System.out.println("及格");
        } else {
            System.out.println("不及格");
        }

        // switch 语句（Java 12+ 新语法）
        int day = 5;
        switch (day) {
            case 1 -> System.out.println("星期一");
            case 2 -> System.out.println("星期二");
            case 3 -> System.out.println("星期三");
            case 4 -> System.out.println("星期四");
            case 5 -> System.out.println("星期五");
            case 6, 7 -> System.out.println("周末");
            default -> System.out.println("无效");
        }

        // switch 表达式（返回值）
        String dayName = switch (day) {
            case 1 -> "星期一";
            case 2 -> "星期二";
            case 3 -> "星期三";
            case 4 -> "星期四";
            case 5 -> "星期五";
            case 6, 7 -> "周末";
            default -> "无效";
        };

        // for 循环
        for (int i = 0; i < 5; i++) {
            System.out.println("for循环: " + i);
        }

        // 增强 for 循环（遍历数组/集合）
        int[] numbers = {1, 2, 3, 4, 5};
        for (int num : numbers) {
            System.out.println("增强for: " + num);
        }

        // while 循环
        int i = 0;
        while (i < 5) {
            System.out.println("while循环: " + i);
            i++;
        }

        // do-while 循环（至少执行一次）
        int j = 0;
        do {
            System.out.println("do-while循环: " + j);
            j++;
        } while (j < 5);

        // break 和 continue
        for (int k = 0; k < 10; k++) {
            if (k == 3) {
                continue;  // 跳过本次循环
            }
            if (k == 7) {
                break;     // 退出循环
            }
            System.out.println("break/continue: " + k);
        }

        // 标签跳出多层循环
        outer:
        for (int m = 0; m < 3; m++) {
            for (int n = 0; n < 3; n++) {
                if (m == 1 && n == 1) {
                    break outer;  // 跳出外层循环
                }
                System.out.println("m=" + m + ", n=" + n);
            }
        }
    }
}
```

### 4. 方法

```java
public class MethodDemo {
    // 静态方法（类方法）
    public static void staticMethod() {
        System.out.println("静态方法");
    }

    // 实例方法
    public void instanceMethod() {
        System.out.println("实例方法");
    }

    // 带参数的方法
    public static int add(int a, int b) {
        return a + b;
    }

    // 可变参数
    public static int sum(int... numbers) {
        int total = 0;
        for (int num : numbers) {
            total += num;
        }
        return total;
    }

    // 方法重载（同名不同参）
    public static void print(String str) {
        System.out.println(str);
    }

    public static void print(int num) {
        System.out.println(num);
    }

    public static void print(String str, int num) {
        System.out.println(str + ": " + num);
    }

    // 递归方法
    public static int factorial(int n) {
        if (n <= 1) {
            return 1;
        }
        return n * factorial(n - 1);
    }

    public static void main(String[] args) {
        staticMethod();

        MethodDemo demo = new MethodDemo();
        demo.instanceMethod();

        System.out.println(add(3, 5));
        System.out.println(sum(1, 2, 3, 4, 5));

        print("Hello");
        print(100);
        print("Score", 95);

        System.out.println(factorial(5));  // 120
    }
}
```

## 三、面向对象编程

### 1. 类与对象

```java
// 类的定义
class Person {
    // 成员变量（属性）
    private String name;
    private int age;

    // 构造方法
    public Person() {
        this("Unknown", 0);
    }

    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }

    // Getter/Setter 方法
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

    // 成员方法
    public void introduce() {
        System.out.println("我叫" + name + "，今年" + age + "岁");
    }

    // 静态方法（类方法）
    public static void printInfo() {
        System.out.println("这是一个Person类");
    }

    // 静态代码块（类加载时执行）
    static {
        System.out.println("Person类被加载");
    }

    // 代码块（创建对象时执行）
    {
        System.out.println("Person对象被创建");
    }
}

// 使用类
public class ObjectDemo {
    public static void main(String[] args) {
        // 创建对象
        Person person1 = new Person("张三", 25);
        Person person2 = new Person();
        person2.setName("李四");
        person2.setAge(30);

        // 调用方法
        person1.introduce();
        person2.introduce();

        // 调用静态方法
        Person.printInfo();
    }
}
```

### 2. 封装

```java
public class EncapsulationDemo {
    private int id;
    private String name;
    private double salary;

    // 使用 lombok 可以简化 Getter/Setter
    // @Data
    public class Employee {
        private int id;
        private String name;
        private double salary;

        // 构造器
        public Employee(int id, String name, double salary) {
            this.id = id;
            this.name = name;
            this.salary = salary;
        }

        // Getter
        public int getId() {
            return id;
        }

        public String getName() {
            return name;
        }

        public double getSalary() {
            return salary;
        }

        // Setter
        public void setSalary(double salary) {
            if (salary >= 0) {
                this.salary = salary;
            } else {
                throw new IllegalArgumentException("薪水不能为负数");
            }
        }

        // 业务方法
        public void raiseSalary(double percent) {
            if (percent > 0 && percent <= 100) {
                this.salary *= (1 + percent / 100);
            }
        }

        @Override
        public String toString() {
            return "Employee{id=" + id + ", name='" + name + "', salary=" + salary + "}";
        }
    }
}
```

### 3. 继承

```java
// 父类
class Animal {
    protected String name;
    protected int age;

    public Animal(String name, int age) {
        this.name = name;
        this.age = age;
    }

    public void eat() {
        System.out.println(name + "正在吃东西");
    }

    public void sleep() {
        System.out.println(name + "正在睡觉");
    }
}

// 子类
class Dog extends Animal {
    private String breed;

    public Dog(String name, int age, String breed) {
        super(name, age);  // 调用父类构造器
        this.breed = breed;
    }

    // 方法重写
    @Override
    public void eat() {
        System.out.println(name + "正在吃狗粮");
    }

    // 子类特有方法
    public void bark() {
        System.out.println(name + "汪汪叫");
    }
}

class Cat extends Animal {
    public Cat(String name, int age) {
        super(name, age);
    }

    @Override
    public void eat() {
        System.out.println(name + "正在吃猫粮");
    }

    public void meow() {
        System.out.println(name + "喵喵叫");
    }
}

// 使用继承
public class InheritanceDemo {
    public static void main(String[] args) {
        Dog dog = new Dog("旺财", 3, "金毛");
        Cat cat = new Cat("咪咪", 2);

        dog.eat();
        dog.bark();
        dog.sleep();

        cat.eat();
        cat.meow();
        cat.sleep();

        // 向上转型
        Animal animal1 = dog;
        Animal animal2 = cat;

        // 动态绑定
        animal1.eat();  // 调用 Dog 的 eat
        animal2.eat();  // 调用 Cat 的 eat

        // 向下转型（需要 instanceof 判断）
        if (animal1 instanceof Dog) {
            Dog d = (Dog) animal1;
            d.bark();
        }
    }
}
```

### 4. 多态

```java
// 形状接口
interface Shape {
    double area();      // 计算面积
    double perimeter(); // 计算周长
}

// 圆形类
class Circle implements Shape {
    private double radius;

    public Circle(double radius) {
        this.radius = radius;
    }

    @Override
    public double area() {
        return Math.PI * radius * radius;
    }

    @Override
    public double perimeter() {
        return 2 * Math.PI * radius;
    }
}

// 矩形类
class Rectangle implements Shape {
    private double width;
    private double height;

    public Rectangle(double width, double height) {
        this.width = width;
        this.height = height;
    }

    @Override
    public double area() {
        return width * height;
    }

    @Override
    public double perimeter() {
        return 2 * (width + height);
    }
}

// 形状管理器
class ShapeManager {
    private List<Shape> shapes = new ArrayList<>();

    public void addShape(Shape shape) {
        shapes.add(shape);
    }

    public double totalArea() {
        double total = 0;
        for (Shape shape : shapes) {
            total += shape.area();  // 多态调用
        }
        return total;
    }
}

// 使用多态
public class PolymorphismDemo {
    public static void main(String[] args) {
        ShapeManager manager = new ShapeManager();

        // 添加不同形状
        manager.addShape(new Circle(5));
        manager.addShape(new Rectangle(4, 6));
        manager.addShape(new Circle(3));

        System.out.println("总面积: " + manager.totalArea());

        // 多态参数
        processShape(new Circle(5));
        processShape(new Rectangle(4, 6));
    }

    // 多态方法
    public static void processShape(Shape shape) {
        System.out.println("形状面积: " + shape.area());
        System.out.println("形状周长: " + shape.perimeter());
    }
}
```

### 5. 抽象类与接口

```java
// 抽象类
abstract class Vehicle {
    private String brand;
    private int speed;

    public Vehicle(String brand, int speed) {
        this.brand = brand;
        this.speed = speed;
    }

    // 具体方法
    public void accelerate() {
        speed += 10;
        System.out.println(brand + "加速，当前速度: " + speed);
    }

    public void brake() {
        speed = Math.max(0, speed - 10);
        System.out.println(brand + "减速，当前速度: " + speed);
    }

    // 抽象方法（子类必须实现）
    public abstract void start();
    public abstract void stop();
}

// 接口（Java 8+ 支持默认方法和静态方法）
interface Flyable {
    void fly();

    // 默认方法
    default void flyFast() {
        System.out.println("高速飞行中...");
    }

    // 静态方法
    static void checkCondition() {
        System.out.println("检查飞行条件...");
    }
}

interface Swimmable {
    void swim();
}

// 继承抽象类，实现接口
class Car extends Vehicle {
    public Car(String brand, int speed) {
        super(brand, speed);
    }

    @Override
    public void start() {
        System.out.println("汽车启动");
    }

    @Override
    public void stop() {
        System.out.println("汽车停止");
    }
}

class Boat extends Vehicle implements Swimmable {
    public Boat(String brand, int speed) {
        super(brand, speed);
    }

    @Override
    public void start() {
        System.out.println("船只启动");
    }

    @Override
    public void stop() {
        System.out.println("船只停止");
    }

    @Override
    public void swim() {
        System.out.println("船只航行");
    }
}

class Airplane extends Vehicle implements Flyable {
    public Airplane(String brand, int speed) {
        super(brand, speed);
    }

    @Override
    public void start() {
        System.out.println("飞机起飞");
    }

    @Override
    public void stop() {
        System.out.println("飞机降落");
    }

    @Override
    public void fly() {
        System.out.println("飞机飞行");
    }
}

// 接口的多重继承
interface InterfaceA {
    default void method() {
        System.out.println("InterfaceA");
    }
}

interface InterfaceB {
    default void method() {
        System.out.println("InterfaceB");
    }
}

class MultiImplement implements InterfaceA, InterfaceB {
    @Override
    public void method() {
        // 需要明确指定调用哪个接口的默认方法
        InterfaceA.super.method();  // 或 InterfaceB.super.method()
    }
}
```

### 6. 内部类

```java
public class InnerClassDemo {
    private int x = 10;

    // 成员内部类
    class Inner {
        private int y = 20;

        public void display() {
            // 可以访问外部类的私有成员
            System.out.println("外部类 x: " + x);
            System.out.println("内部类 y: " + y);
        }
    }

    // 静态内部类
    static class StaticInner {
        private int z = 30;

        public void display() {
            // 只能访问外部类的静态成员
            System.out.println("静态内部类 z: " + z);
        }
    }

    // 方法内部类
    public void method() {
        class MethodInner {
            private int w = 40;

            public void display() {
                System.out.println("方法内部类 w: " + w);
            }
        }

        MethodInner inner = new MethodInner();
        inner.display();
    }

    // 匿名内部类
    public interface Greeting {
        void sayHello();
    }

    public void useAnonymousClass() {
        Greeting greeting = new Greeting() {
            @Override
            public void sayHello() {
                System.out.println("Hello from anonymous class!");
            }
        };

        greeting.sayHello();
    }

    public static void main(String[] args) {
        InnerClassDemo outer = new InnerClassDemo();

        // 创建成员内部类
        Inner inner = outer.new Inner();
        inner.display();

        // 创建静态内部类
        StaticInner staticInner = new StaticInner();
        staticInner.display();

        // 方法内部类
        outer.method();

        // 匿名内部类
        outer.useAnonymousClass();
    }
}
```

## 四、数组与字符串

### 1. 数组操作

```java
import java.util.Arrays;

public class ArrayDemo {
    public static void main(String[] args) {
        // 数组声明与初始化
        int[] arr1 = new int[5];                    // 声明并创建
        int[] arr2 = {1, 2, 3, 4, 5};               // 静态初始化
        int[] arr3 = new int[]{6, 7, 8, 9, 10};     // 动态初始化

        // 数组赋值
        arr1[0] = 100;
        arr1[1] = 200;

        // 数组遍历
        for (int i = 0; i < arr1.length; i++) {
            System.out.println(arr1[i]);
        }

        // 增强for遍历
        for (int num : arr2) {
            System.out.println(num);
        }

        // 数组复制
        int[] copy1 = Arrays.copyOf(arr2, arr2.length);
        int[] copy2 = Arrays.copyOfRange(arr2, 1, 4);
        System.arraycopy(arr2, 0, copy1, 0, arr2.length);

        // 数组排序
        int[] unsorted = {5, 2, 8, 1, 9};
        Arrays.sort(unsorted);
        System.out.println(Arrays.toString(unsorted));

        // 二分查找（需要先排序）
        int index = Arrays.binarySearch(unsorted, 8);
        System.out.println("8的位置: " + index);

        // 数组填充
        int[] fill = new int[5];
        Arrays.fill(fill, 10);
        System.out.println(Arrays.toString(fill));

        // 数组比较
        int[] arr4 = {1, 2, 3};
        int[] arr5 = {1, 2, 3};
        System.out.println(Arrays.equals(arr4, arr5));  // true

        // 多维数组
        int[][] matrix = {
            {1, 2, 3},
            {4, 5, 6},
            {7, 8, 9}
        };

        // 遍历二维数组
        for (int i = 0; i < matrix.length; i++) {
            for (int j = 0; j < matrix[i].length; j++) {
                System.out.print(matrix[i][j] + " ");
            }
            System.out.println();
        }

        // 常用数组操作工具方法
        int[] data = {3, 1, 4, 1, 5, 9, 2, 6};
        System.out.println("最小值: " + findMin(data));
        System.out.println("最大值: " + findMax(data));
        System.out.println("和: " + sum(data));
        System.out.println("平均值: " + average(data));
        System.out.println("去重: " + Arrays.toString(removeDuplicates(data)));
    }

    // 查找最小值
    public static int findMin(int[] arr) {
        int min = arr[0];
        for (int num : arr) {
            if (num < min) {
                min = num;
            }
        }
        return min;
    }

    // 查找最大值
    public static int findMax(int[] arr) {
        int max = arr[0];
        for (int num : arr) {
            if (num > max) {
                max = num;
            }
        }
        return max;
    }

    // 求和
    public static int sum(int[] arr) {
        int total = 0;
        for (int num : arr) {
            total += num;
        }
        return total;
    }

    // 求平均值
    public static double average(int[] arr) {
        return (double) sum(arr) / arr.length;
    }

    // 数组去重
    public static int[] removeDuplicates(int[] arr) {
        Arrays.sort(arr);
        int n = arr.length;
        int j = 0;

        for (int i = 0; i < n - 1; i++) {
            if (arr[i] != arr[i + 1]) {
                arr[j++] = arr[i];
            }
        }
        arr[j++] = arr[n - 1];

        return Arrays.copyOf(arr, j);
    }
}
```

### 2. String 操作

```java
public class StringDemo {
    public static void main(String[] args) {
        // String 创建（不可变）
        String str1 = "Hello";                     // 字符串常量池
        String str2 = new String("Hello");         // 堆内存
        String str3 = "Hello";                     // 复用常量池

        System.out.println(str1 == str2);          // false，不同内存地址
        System.out.println(str1 == str3);          // true，相同常量
        System.out.println(str1.equals(str2));     // true，内容相同

        // StringBuilder（可变，线程不安全）
        StringBuilder sb = new StringBuilder();
        sb.append("Hello");
        sb.append(" ");
        sb.append("World");
        System.out.println(sb.toString());         // Hello World

        // StringBuffer（可变，线程安全）
        StringBuffer buffer = new StringBuffer();
        buffer.append("Java");
        buffer.append(" is");
        buffer.append(" awesome");
        System.out.println(buffer.toString());      // Java is awesome

        // 常用 String 方法
        String text = "Hello, Java Programming!";

        System.out.println("长度: " + text.length());
        System.out.println("字符[6]: " + text.charAt(6));
        System.out.println("子串: " + text.substring(7, 11));
        System.out.println("是否包含Java: " + text.contains("Java"));
        System.out.println("开始位置: " + text.indexOf("Java"));
        System.out.println("替换: " + text.replace("Java", "Python"));
        System.out.println("转小写: " + text.toLowerCase());
        System.out.println("转大写: " + text.toUpperCase());
        System.out.println("去除空格: " + text.trim());

        // 分割
        String[] words = text.split(" ");
        for (String word : words) {
            System.out.println(word);
        }

        // 格式化字符串
        String name = "张三";
        int age = 25;
        String formatted = String.format("姓名: %s, 年龄: %d", name, age);
        System.out.println(formatted);

        // 数字格式化
        double pi = 3.141592653589793;
        System.out.println(String.format("π = %.2f", pi));
        System.out.println(String.format("π = %.4f", pi));

        // 字符串比较
        String a = "abc";
        String b = "abcd";
        System.out.println(a.compareTo(b));       // -1，a < b
        System.out.println(b.compareTo(a));       // 1，b > a

        // 字符串连接性能比较
        stringConcatenationPerformance();
    }

    public static void stringConcatenationPerformance() {
        int iterations = 10000;

        // 使用 + 拼接
        long start = System.currentTimeMillis();
        String result = "";
        for (int i = 0; i < iterations; i++) {
            result += i;
        }
        long end = System.currentTimeMillis();
        System.out.println("使用 + 拼接: " + (end - start) + "ms");

        // 使用 StringBuilder
        start = System.currentTimeMillis();
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < iterations; i++) {
            sb.append(i);
        }
        result = sb.toString();
        end = System.currentTimeMillis();
        System.out.println("使用 StringBuilder: " + (end - start) + "ms");
    }
}
```

## 五、异常处理

```java
import java.io.*;

public class ExceptionDemo {
    public static void main(String[] args) {
        // try-catch 基础
        try {
            int result = divide(10, 0);
            System.out.println(result);
        } catch (ArithmeticException e) {
            System.out.println("除数不能为零: " + e.getMessage());
        }

        // 多异常捕获
        try {
            String str = null;
            System.out.println(str.length());
            int[] arr = new int[5];
            System.out.println(arr[10]);
        } catch (NullPointerException e) {
            System.out.println("空指针异常");
        } catch (ArrayIndexOutOfBoundsException e) {
            System.out.println("数组越界异常");
        } catch (Exception e) {
            System.out.println("其他异常");
        }

        // finally 块（总会执行）
        try {
            readFile("nonexistent.txt");
        } catch (IOException e) {
            System.out.println("文件读取失败");
        } finally {
            System.out.println("finally 块执行");
        }

        // try-with-resources（自动关闭资源，Java 7+）
        try (BufferedReader reader = new BufferedReader(new FileReader("example.txt"))) {
            String line;
            while ((line = reader.readLine()) != null) {
                System.out.println(line);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }

        // 抛出异常
        try {
            validateAge(-5);
        } catch (IllegalArgumentException e) {
            System.out.println(e.getMessage());
        }

        // 自定义异常
        try {
            withdraw(100, 150);
        } catch (InsufficientBalanceException e) {
            System.out.println(e.getMessage());
        }
    }

    // 可能抛出异常的方法
    public static int divide(int a, int b) throws ArithmeticException {
        return a / b;
    }

    // 抛出异常
    public static void validateAge(int age) {
        if (age < 0) {
            throw new IllegalArgumentException("年龄不能为负数");
        }
        if (age > 150) {
            throw new IllegalArgumentException("年龄不能超过150岁");
        }
    }

    // 读取文件（声明异常）
    public static void readFile(String filename) throws IOException {
        BufferedReader reader = new BufferedReader(new FileReader(filename));
        try {
            reader.readLine();
        } finally {
            reader.close();
        }
    }

    // 取款方法
    public static void withdraw(double balance, double amount) throws InsufficientBalanceException {
        if (amount > balance) {
            throw new InsufficientBalanceException("余额不足，无法取款");
        }
        System.out.println("取款成功，剩余余额: " + (balance - amount));
    }
}

// 自定义异常类
class InsufficientBalanceException extends Exception {
    public InsufficientBalanceException(String message) {
        super(message);
    }
}

// 运行时异常（不强制处理）
class CustomRuntimeException extends RuntimeException {
    public CustomRuntimeException(String message) {
        super(message);
    }
}
```

## 六、实战练习

```java
import java.util.Scanner;

public class PracticalExercise {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        // 练习1：计算器
        System.out.println("=== 简易计算器 ===");
        calculator(scanner);

        // 练习2：学生成绩管理系统
        System.out.println("\\n=== 学生成绩管理系统 ===");
        studentManagementSystem(scanner);

        scanner.close();
    }

    // 简易计算器
    public static void calculator(Scanner scanner) {
        System.out.print("请输入第一个数: ");
        double num1 = scanner.nextDouble();

        System.out.print("请输入运算符 (+, -, *, /): ");
        String operator = scanner.next();

        System.out.print("请输入第二个数: ");
        double num2 = scanner.nextDouble();

        double result;
        switch (operator) {
            case "+":
                result = num1 + num2;
                break;
            case "-":
                result = num1 - num2;
                break;
            case "*":
                result = num1 * num2;
                break;
            case "/":
                if (num2 == 0) {
                    System.out.println("除数不能为零");
                    return;
                }
                result = num1 / num2;
                break;
            default:
                System.out.println("无效的运算符");
                return;
        }

        System.out.printf("%.2f %s %.2f = %.2f\\n", num1, operator, num2, result);
    }

    // 学生成绩管理系统
    public static void studentManagementSystem(Scanner scanner) {
        // 学生数据
        String[] names = new String[10];
        double[] scores = new double[10];
        int count = 0;

        while (true) {
            System.out.println("\\n1. 添加学生");
            System.out.println("2. 查看所有学生");
            System.out.println("3. 查找学生");
            System.out.println("4. 修改成绩");
            System.out.println("5. 删除学生");
            System.out.println("6. 统计信息");
            System.out.println("0. 退出");
            System.out.print("请选择: ");

            int choice = scanner.nextInt();

            switch (choice) {
                case 1:
                    if (count >= 10) {
                        System.out.println("学生数量已满");
                        break;
                    }
                    scanner.nextLine();  // 消耗换行符
                    System.out.print("请输入学生姓名: ");
                    names[count] = scanner.nextLine();
                    System.out.print("请输入学生成绩: ");
                    scores[count] = scanner.nextDouble();
                    count++;
                    System.out.println("添加成功");
                    break;

                case 2:
                    System.out.println("\\n学生列表:");
                    System.out.println("序号\\t姓名\\t成绩");
                    for (int i = 0; i < count; i++) {
                        System.out.printf("%d\\t%s\\t%.1f\\n", i + 1, names[i], scores[i]);
                    }
                    break;

                case 3:
                    scanner.nextLine();
                    System.out.print("请输入要查找的学生姓名: ");
                    String searchName = scanner.nextLine();
                    boolean found = false;
                    for (int i = 0; i < count; i++) {
                        if (names[i].equals(searchName)) {
                            System.out.printf("姓名: %s, 成绩: %.1f\\n", names[i], scores[i]);
                            found = true;
                            break;
                        }
                    }
                    if (!found) {
                        System.out.println("未找到该学生");
                    }
                    break;

                case 4:
                    System.out.print("请输入要修改的学生序号: ");
                    int modifyIndex = scanner.nextInt() - 1;
                    if (modifyIndex >= 0 && modifyIndex < count) {
                        System.out.print("请输入新成绩: ");
                        scores[modifyIndex] = scanner.nextDouble();
                        System.out.println("修改成功");
                    } else {
                        System.out.println("无效的序号");
                    }
                    break;

                case 5:
                    System.out.print("请输入要删除的学生序号: ");
                    int deleteIndex = scanner.nextInt() - 1;
                    if (deleteIndex >= 0 && deleteIndex < count) {
                        for (int i = deleteIndex; i < count - 1; i++) {
                            names[i] = names[i + 1];
                            scores[i] = scores[i + 1];
                        }
                        count--;
                        System.out.println("删除成功");
                    } else {
                        System.out.println("无效的序号");
                    }
                    break;

                case 6:
                    if (count == 0) {
                        System.out.println("没有学生数据");
                        break;
                    }
                    double sum = 0;
                    double max = scores[0];
                    double min = scores[0];
                    int excellent = 0, pass = 0, fail = 0;

                    for (int i = 0; i < count; i++) {
                        sum += scores[i];
                        if (scores[i] > max) max = scores[i];
                        if (scores[i] < min) min = scores[i];
                        if (scores[i] >= 90) excellent++;
                        else if (scores[i] >= 60) pass++;
                        else fail++;
                    }

                    System.out.println("\\n统计信息:");
                    System.out.printf("学生总数: %d\\n", count);
                    System.out.printf("平均分: %.2f\\n", sum / count);
                    System.out.printf("最高分: %.1f\\n", max);
                    System.out.printf("最低分: %.1f\\n", min);
                    System.out.printf("优秀人数(90+): %d\\n", excellent);
                    System.out.printf("及格人数(60-89): %d\\n", pass);
                    System.out.printf("不及格人数(<60): %d\\n", fail);
                    break;

                case 0:
                    System.out.println("退出系统");
                    return;

                default:
                    System.out.println("无效的选择");
            }
        }
    }
}
```

## 小结

本节学习了 JavaSE 的基础知识：

- **环境搭建** - JDK 安装配置
- **基础语法** - 变量、运算符、流程控制
- **面向对象** - 封装、继承、多态、抽象类、接口
- **数据类型** - 数组、字符串操作
- **异常处理** - try-catch、自定义异常
- **实战练习** - 计算器、学生管理系统

## 实践练习

### 编程题
1. 用面向对象的方式设计一个"银行账户系统"：包含 Account（账户）基类以及 SavingAccount（储蓄账户）和 CreditAccount（信用卡账户）子类，实现存款、取款、转账功能。
2. 扩展学生成绩管理系统：使用 ArrayList 替代数组存储学生数据，并添加按成绩排序功能和导出 CSV 文件功能。

### 思考题
1. 接口和抽象类的使用场景有什么不同？什么时候应该用接口，什么时候用抽象类？
2. String、StringBuilder、StringBuffer 三者的区别和适用场景？

### 自测题
1. Java 的八大基本数据类型是什么？
2. `equals()` 和 `==` 的区别是什么？
3. 方法重载（Overload）和重写（Override）的区别是什么？

下一步将学习集合框架（→ `02-java-se-collections.md`）。