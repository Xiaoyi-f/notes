// java  强类型静态语言

/*
Java 一次性编译好再执行 javac编译 java运行
跨平台原理: java编译器 -> .class 字节码文件 -> java虚拟机(JVM) 
不同操作系统适配的JDK不一样
版本: JavaME -> JavaSE -> JavaEE 
*/

/*
java本身不内置包管理器 需要使用 Maven / Gradle 构建工具管理 
*/

/* 
安装对应版本 JDK -> 配置环境变量 %JAVA_HOME% (bin)
JDK JRE JVM 区别:
JDK(开发工具与运行环境) > JRE(运行环境) > JVM(运行程序核心) 
*/

/**
 * 文档注释 幂除法解决十进制与X进制之间的运算转换 
 * 一字节八位 可表示 2^8 种数 -> -(2^7) ~ (2^7 - 1)
 * 引用类型: 类 接口 数组 
 * java常见关键字:
 * private protected public 
 * abstract class extends final implements interface new static 
 * synchronized transient volatile 
 * break continue return java支持循环层标签控制 
 * do while if else instanceof for (初始化; 条件; 控制)  
 * switch case default switch具有穿透性
 * try cathc throw throws 
 * import package 
 * boolean byte char short int long float double null  
 * true false 
 * super this void 
 */

// 定义long变量时候在数值后面使用L 定义float变量时候在数值后面使用F
// 自动类型转换: 小数值自动转换给大类型 
// 强制类型转换: (类型)(val/var) 
/*
强制类型转换规则:
  引用类型强转，必须处在同一条继承链（父子类关系）

// / 运算符 -> 整数操作得到整数,小数参与才得到小数 
// byte short char 算数运算时候提升为int类型进行运算 

// + 可以用来连接字符串 
// 从左往右执行代码时候,遇到字符串且使用+操作会自动统一转为字符串 
// java支持自增自减 

// == --> 引用类型比较内存地址 基本类型比较数据值 

// 逻辑运算符 & | ^ ! 
// && || 短路特性 

import java.util.Scanner; 

// Scanner 只用于 System.in 或 new File("文件名") 等
Scanner sc = new Scanner(System.in); 
// System.in System.out System.err 系统 输入 / 输出 / 错误 流  

sc.hasNextLine();
String line = sc.nextLine();

char c = sc.next().charAt(0);
String str = sc.next(); 
int i = sc.nextInt(); 
long l = sc.nextLong(); 
float f = sc.nextFloat();
double d = sc.nextDouble();  
boolean b = sc.nextBoolean(); 
// 类型不会自动转布尔 静态强类型语言 只能输入 true / false 

// 通用存储逻辑 栈基本指针 堆实体对象

// java数组的内存逻辑和C语言的相同,但是内存模型和内存管理方式有本质区别
int[] arr = {1,2,3,4,5}; // 数组静态初始化
int[] arr = new int[10]; // 数组动态初始化 java内存给数组分配默认值 

/**
 * 数组默认值:
 * 整数 0 
 * 浮点数 0.0 
 * 布尔 false
 * 字符 '\u0000' 空
 * 引用类型 null
 * 
 * 常见问题:
 * 1)索引越界
 * 2)空指针异常 -> arr = null;  
 * 
 * 数组长度:
 * arr.length 
 */

/**
 * 方法
 * 修饰符 返回值数据类型 方法名(参数) {}
 * 
 * 注意事项
 * 1.方法不能嵌套定义 
 * 2.void表示无返回值 
 * 
 * 方法重载: 同一个类中定义多个同名方法,但是参数类型/数量不同 
 */

/**
 * 权限修饰符
 * private 本类私有 
 * public 公有 --> 一个java文件只能有一个public类 public类名需要与java文件名同名
 * default(默认) 同包 
 * protected 保护子类
 * 
 * 状态修饰符
 * final 最终态 --> 禁止修改、不被继承 --> 特点: 修饰引用类型时候 内存地址禁止修改,但是对象内部属性值可以改动 
 * static 静止态 --> 共享、提前加载 --> 规范使用类名访问 static方法 --> 只能访问静态成员变量/方法或局部属性   
 */

/**
 * 类是对现实生活中一类具有共同属性和行为的事物的抽象 
 * 类是对象的数据类型，对象是类的实体 --> 属性与行为 
 * 属性 --> 成员变量(堆内存) 局部变量(栈内存)   
 * 类的定义
 * 修饰符 class 类名
 * 属性声明后会被赋予默认值 
 * 整数类型 0 
 * 浮点数类型 0.0
 * 字符串 '\u0000' 空
 * 布尔 false
 * 引用类型 null
 * 
 * 标准类:
 * 构造方法
 * 属性 
 * getter / setter 
 * main 测试方法 --> JVM识别的程序入口 并非必须 
 */

/**
 * package com.xxx.xxx; // 声明所属包 包层级文件夹结构必须对应为 com/xxx/xxx 
 * 包实现命名空间的划分,同时用于组织代码以即划定默认权限范围 包支持导入 
 * 
 * 封装(private)、继承(extends)、多态 
 * 封装: 将对象的属性（数据） 私有化（private），仅通过公共的方法（行为） 对外提供访问和修改的入口
 * 继承: 创建一个新类（子类/派生类）继承已有类（父类/超类）的属性和方法，并可以扩展新功能或重写旧方法
 * 多态: 同一个行为（方法调用）在不同的对象上产生不同的执行结果，多态依赖于继承（或接口实现）和方法重写（Override）
 * 
 * 多态实现: 同一类事物继承同一个主类进行子类实体方法实现与父类调用方法实现 
 * 多态规范: 以父类为标准 成员变量编译运行都要看父类 成员方法编译看父类运行看子类
 * 标准多态运用: 使用父类对象调用方法传递子类对象作为参数,不同子类对象触发不同
 * 
 * 多态转型:
 * 
 * 
 * this代表当前对象(可以作为参数) this.成员变量 this.方法 this()代表调用构造方法(构造方法和类同名) 
 * 如果你在方法末尾写 return this; 就可以实现链式调用 
 * 
 * super.父类成员变量 super.父类方法 super() 父类构造方法  
 * super代表当前对象的父类引用 super不是对象引用不可以像this一样作为对象使用 
 * 
 * 私有方法不被继承,私有方法也不存在重写 override 
 * 方法重写规则 子类重写方法的访问权限不能低于父类方法权限 public > protected(同包或子类) > 默认(仅限同包) > private 
 * 
 * 继承链的访问规则遵循就近原则
 * 调用子类的构造方法时候JVM会先调用父类的无参构造方法 
 * 如果父类提供有参构造方法而没有无参构造方法，子类又没有显式调用父类的有参构造，那么编译直接报错，根本轮不到 JVM 运行
 * 
 * 注意: 因为 static 方法属于类，在类加载时就存在，此时可能还没有对象产生，所以禁止在static方法中使用this
 * 
 * java构造方法禁止标明返回值类型也不写返回值 --> 标准  
 * 真正把创建好的对象“返回”给变量的，是 new 关键字背后的 JVM（Java虚拟机）机制
 */

/**
 * String 类 代表字符串 java中所有字符串都被实现为此类的实例 
 * String 类 在 java.lang 包下 使用时不需要导包 JVM默认自动加载 内置源码在src.zip中 
 * String 类 内容不可变,有变动会改变内存地址 
 * StringBuilder 类 内容可变 节省内存空间  
 */
String str_one = new String(); // 一定会新开对象 可以接收 字符串字面值 / 字符数组 / 字节数组 创建字符串对象   
String str_two = "hello world"; // 优先从字符串常量池查找数据进行复用 
boolean str_bool = str_one.equals(str_two) // 比较逻辑值 Object类提供 所有类/对象都拥有   

StringBuilder sb = new StringBuilder("Hello"); // 参数可以传String变量
sb.append("StringBuilder"); // 追加内容  

// 默认情况 对象.toString() 返回 getClass().getName() + "@" + Integer.toHexString(hashCode()) 
// sb 有重写 toString

String s = sb.toString(); // 把对象转换为字符串描述 Object类提供 所有类/对象都拥有   
StringBuilder reverse_sb = sb.reverse(); // 反转字符串 

// 对象.hashCode() Object类 提供 内存中同一个对象的hashCode值相同
// hashCode 用于提高查询效率 改写equals方法时候必须同时改写hashCode() 
// 规则: equals 结果为 true 则 两个对象的hashCode必须相同 结果为 false 则两个对象的hashCode可同(hash碰撞)可不同

// 对象.getClass() Object类 提供 获取对象所属类所在的包名名称 
// 对象.getClass().getName() Object类 提供 获取对象所属类的 包名 + 类名 
// 部分类自实现getName() 

// 正则表达式 
str.matches(regex_expr) // 全串匹配 字符串支持matches方法进行正则匹配 返回布尔值 
str.split(regex_expr) // 分割字符串为数组 并且删除匹配的局部正则内容 

/**
 * 包装类:
 * Byte 
 * Short
 * Character
 * Integer (int类型参数 或 纯数字字符串)
 * Long
 * Float
 * Double 
 * Boolean    
 */

// Integer 
// Integer.valueOf(int num) 将基本类型num转为包装类Integer 处于[-128, 127]区间的数字可以直接复用缓存池中已经存在对象
// Integer.parseInt(String str) 将字符串转为基本类型int
// 对象.intValue() 将包装类Integer转为基本类型int
// 对象.toString() 将包装类Integer转为字符串

// 基本数据类型转为包装数据类型称为装箱 
// 包装数据类型转为基本数据类型称为拆箱
// java支持自动装箱(底层调用valueOf)和自动拆箱(底层调用xxxValue) 

// 其他包装类 
// 包装类.valueOf(基本数据类型) 
/**
 * - Integer：-128 ~ 127
 * - Byte：全部范围（-128~127）全部缓存
 * - Short：-128 ~ 127
 * - Long：-128 ~ 127
 * - Character：\u0000 ~ \u007F（0~127） 
 * - Boolean：TRUE / FALSE 
 * Float / Double 无缓存   
 * */ 
// 对象.xxxValue() 将包装类转基本类型 
// 对象.toString() 将包装类转为字符串

// String.valueOf(基本数据类型) String支持valueOf

/**
 * Math类 --> java.lang 
 * 常用方法:
 * double max(double a, double b)
 * double min(double a, double b)
 * double abs(double x) 
 * double sqrt(double x) 
 * double ceil(double x) 
 * double floor(double x) 
 * int round(float x) 
 * double random() // 生成 [0.0, 1.0) 之间的随机数  
 */

import java.time.format.DateTimeFormatter; 
import java.time.LocalDateTime;

LocalDateTime now = LocalDateTime.now();

DateTimeFormatter dtf = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
String now_str = now.format(dtf);

