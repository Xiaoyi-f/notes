// java  强类型静态语言

/*
Java 一次性编译好再执行 javac编译 java运行
跨平台原理: java编译器 -> .class 字节码文件 -> java虚拟机(JVM) 
不同操作系统适配的JDK不一样
版本: JavaME -> JavaSE -> JavaEE 
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

// / 运算符 -> 整数操作得到整数,小数参与才得到小数 
// byte short char 算数运算时候提升为int类型进行运算 

// + 可以用来连接字符串 
// 从左往右执行代码时候,遇到字符串且使用+操作会自动统一转为字符串 
// java支持自增自减 

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
 * 类是对现实生活中一类具有共同属性和行为的事物的抽象 
 * 类是对象的数据类型，对象是类的实体 --> 属性与行为 
 * 
 * 类的定义
 * 修饰符 class 类名
 * 属性声明后会被赋予默认值 
 * 整数类型 0 
 * 浮点数类型 0.0
 * 字符串 '\u0000' 空
 * 布尔 false
 * 引用类型 null
 */


