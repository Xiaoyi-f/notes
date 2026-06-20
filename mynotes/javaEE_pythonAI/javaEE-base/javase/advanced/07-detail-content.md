# Java细节内容
## 前言/配置
java特性: 
先编译、后虚拟机执行，兼顾跨平台与运行性能
静态类型语言，有明确的类型标明

java下载配置环境变量 -> %JAVA_HOME%
IDEA项目配置JDK:
项目结构(SDK SofewareDevelopmentKit 添加JDK) -> 项目结构(项目 配对项目SDK) -> 设置(Java编译器 字节码版本 和语言版本相同即可)

maven下载配置环境变量 -> %MAVEN_HOME% -> conf/settings.xml配置
    1.配置镜像源
        <mirror>
          <id>idName</id>
          <mirrorOf>*</mirrorOf>
          <name>mirrorName</name>
          <url>http://my.repository.com/repo/path</url>
        </mirror>
    2.配置JDK版本(编译版本)
        <profiles>
            <profile>
                <id>jdk-config</id>
                <activation>
                    <activeByDefault>true</activeByDefault>
                </activation>
                <properties>
                    <maven.compiler.source>版本号</maven.compiler.source>
                    <maven.compiler.target>版本号</maven.compiler.target>
                    <maven.compiler.compilerVersion>版本号</maven.compiler.compilerVersion>
                </properties>
            </profile>
        </profiles>
    3.不同版本JDK配置不同对应源
           <profile>
             <id>jdk-x.x</id>

             <activation>
               <jdk>x.x</jdk>
             </activation>

             <repositories>
               <repository>
                 <id>jdkxx</id>
                 <name>特定JDK版本的特定使用源</name>
                 <url>对应源URL</url>
                 <layout>default</layout>
                 <snapshotPolicy>always</snapshotPolicy>
               </repository>
             </repositories>
           </profile>
    4.配置本地仓库路径 -> maven下载的依赖存放在本地的位置
        <localRepository>localPath</localRepository>
    5.mvn help:effective-settings 检查配置是否生效
maven项目结构:
    my-maven-project/                    # 项目根目录
    │
    ├── pom.xml                          # Maven核心配置文件
    │
    ├── src/                             # 源代码目录
    │   │
    │   ├── main/                        # 主代码目录（最终要打包的）
    │   │   ├── java/                    # Java源代码
    │   │   │   └── com/
    │   │   │       └── example/
    │   │   │           └── App.java     # 主类
    │   │   │
    │   │   ├── resources/               # 资源文件（配置文件等）
    │   │       ├── application.properties
    │   │       ├── logback.xml
    │   │       └── messages.properties
    │   │
    │   │
    │   │
    │   │
    │   │
    │   │
    │   │
    │   │
    │   └── test/                        # 测试代码目录（不会被打包）
    │       ├── java/                    # 单元测试代码
    │       │   └── com/
    │       │       └── example/
    │       │           └── AppTest.java # JUnit测试类
    │       │
    │       └── resources/               # 测试专用资源文件
    │           └── test-config.properties
    │
    ├── target/                          # 编译输出目录
    │   ├── classes/                     # 编译后的.class文件
    │   ├── test-classes/                # 测试编译后的.class文件
    │   ├── my-app-1.0.0.jar            # 打包后的jar文件
    │   ├── maven-status/                # Maven状态信息
    │   └── surefire-reports/            # 测试报告
    │
    ├── .gitignore                       # Git版本控制忽略文件
    ├── README.md                        # 项目说明文档
    └── LICENSE                          # 开源许可证

## 内置模块 
java.util.Random:
    import java.util.Random;
    Random randomObj = new Random();
    // float 精度 6-7位    double 精度 15-17位
    // 绝大多数直接使用double是最万能的
    int intNum = randomObj.nextInt(10) + 10;
    float floatNum = randomObj.nextFloat()
    double doubleNum = randomObj.nextDouble();
    // Math.random() 等价类似于 randomObj.nextDouble();
    boolean randomBoolean = randomObj.nextBoolean();

java.lang 内置包(无需导入可用):
        Math.max(a, b)
        Math.min(a, b)
        Math.sqrt(num)
        Math.abs(num)
        Math.random()
        Math.pow()
        Math.round()

        System.out 标准输出流 
        System.err 标准错误流 
        System.in 标准输入流 
        System.currentTimeMillis() 获取当前时间戳
        System.arraycopy() 数组复制 大量数据 性能最高 Arrays.copyOf() Arrays.copyOfRange() List.toArray() 底层
        System.exit(0) 终止JVM

        // final型
        enum 枚举类 {}
        枚举类.values() 返回该枚举的所有常量数组 
        枚举类.valueOf("常量名") 获取枚举类中指定常量的对象

## 外部库 
Commons-io 库:
    在项目文件夹中创建一个lib文件夹
    将jar包放到里面，idea右键Add as Library 
    在类中导包使用     
    关键方法:
        static void copyFile(File srcFile, File destFile)
        static void copyDirectory(File srcDir, File destDir)
        static void copyDirectoryToDirectory(File srcDir, File destDir)
        static void deleteDirectory(File directory)
        static void cleanDirectory(File directory)
        static String readFileToString(File file, Charset encoding)
        static void write(File file, CharSequence data, String encoding)

## 多线程与多进程:
    线程是操作系统能够进行运算调度的最小单位，他被包含在进程中，是进程中的实际运作单位
    进程是程序的基本执行实体
    程序面快速理解: 
        1.每一行代码执行之后假设都会有一段缓冲时间再执行下一行代码，但是如果有多个线程这个缓冲浪费的时间会越短，实现并发
        2.并发: 在同一时刻有多个指令在单核上交替执行
        3.并行: 在同一时刻有多个指令在多核上同时执行
        4.操作系统上标明的硬件x核xx线程代表可以实现最多同时两个进程并行，xx线程并行，超过数量则会触发并发+并行
        5.java中每个线程都有自己的优先级别

    JVM 启动时候 就会自动启动多条线程 其中有一条 main 线程
    在以前，我们写的所有的代码，其实都是运行在main线程当中

    线程的生命周期 
    1. 新建状态(new)
    2. 就绪状态(start)
    3. 运行状态(run) 直接交出去给操作系统管理 
    4. 阻塞状态(锁...等问题) 
    5. 等待状态(wait) 计时等待(sleep) sleep 方法让线程睡眠 时间到后 不会立马执行下面的代码 需要回到 就绪 状态 然后需要重新排队等待CPU分配时间片 
    6. 死亡状态(dead) run 方法执行完毕 start 自动调用run方法
   
    Tip:
      具体执行 拿到CPU资源 由操作系统调度决定 
      同时运行的数量 ≤ CPU核心数 Java线程只是“可以竞争CPU”，但不保证同时执行
      java 默认是单进程多线程模型 进程之间是相对独立的，一个崩溃另外一个不受到影响 
      除非实在要隔离资源，避免崩溃导致影响到整个项目的运作才需要使用多进程实现防止崩溃
      当然，运维层面也是可以实现多进程管理的 JVM本身就是一个进程 通常需要真正隔离的话，一般将多个功能拆分成为多个服务进行独立部署(微服务)
      如果是整的在代码中开多个进程，容易导致进程间通信复杂 资源开销大 调试、日志追踪等困难 
      线程处理速度太块，处理内容不多，也可能出现一个线程快速就解决了所有问题的情况，如果要突出多线程一起执行，可以让线程睡眠一会 

## 线程池工作流程
    1. 判断核心线程是否已满？
    ├─ 否 → 创建核心线程执行任务
    └─ 是 → 进入步骤2

    2. 判断任务队列是否已满？
    ├─ 否 → 将任务放入队列，等待空闲核心线程执行
    └─ 是 → 进入步骤3

    3. 判断线程总数（核心+非核心）是否达到 maximumPoolSize？
    ├─ 否 → 创建非核心线程执行任务（临时线程）
    └─ 是 → 进入步骤4

    4. 执行拒绝策略（RejectedExecutionHandler）

    有任务提交时，线程池会创建线程去执行任务，执行完毕归还线程 

    线程池多大合适?
    CPU 密集型运算: 最大并行数 + 1
    I/O 密集型运算: 最大并行数 * 期望CPU利用率 * 总时间(CPU计算时间+等待时间) / CPU计算时间

## 网络编程
    IP对象
    InetAddress address = InetAddress.getByName("主机名/ip");
    System.out.println(address);
    String name = address.getHostName();
    String ip = address.getHostAddress();
    System.out.println(ip); 

    端口号
    由两个字节表示的整数，取值范围: 0~65535
    其中0~1023为保留端口，1024~5000为用户自定义端口，5000~65535为系统端口
    一个端口号只能够被一个应用程序使用

    协议
    OSI模型 应用 表示 回话 传输 网络 数据链路 物理 
    TCP/IP模型 应用(HTTP、FTP、DNS ...) 传输(TCP、UDP ...) 网络(IP、ICMP、ARP ...) 物理+数据链路(二进制 物理设备传输) 简短，节约资源
    由上往下 由下往上

    UDP协议: 面向无连接的通信协议(可能丢失传输资源) 速度快 有大小限制(<= 64K) 数据不安全 易丢失数据
    TCP协议: 传输控制协议TCP 面向连接的通信协议 速度慢 无限

    网络编程三要素: IP地址(设备在网络中唯一标识)、端口号(应用程序在设备中唯一标识)、协议(数据在网络中传输的规则)
    常见协议: UDP TCP http https ftp ssh smtp ...
    ipv4 采用 32 位 地址长度 分成 4 组 点分十进制 2^32
    ipv6 采用 128 位 地址长度 分成 8 组 16 进制 2^128

## 异步
一种编程模式 --> 当一个任务需要等待时，程序等那个任务完成后再回调调用函数并且处理结果 
这个过程只会影响回调函数的调用，不影响其他代码的运行

反射允许对成员变量(字段)、成员方法和构造方法的信息进行编程式访问修饰符、异常、名字、类型、值、形参、创建对象、返回值、注解、运行方法

## 代理
代理可以无侵入式的给对象增强其他的功能
调用者 -> 代理 -> 对象
代理中就是对象需要被代理的方法
java中通过接口保证代理样子

静态代理:
    // 1. 接口（保证代理样子）
    public interface BankService {
        void transfer(String from, String to, int money);
    }

    // 2. 原始对象（被代理的）
    public class BankServiceImpl implements BankService {
        @Override
        public void transfer(String from, String to, int money) {
            System.out.println("转账 " + money + " 元");
        }
    }

    // 3. 代理类（手写，和原始类实现同一接口）
    public class BankServiceProxy implements BankService {
        private BankService target;  // 持有原始对象
        
        public BankServiceProxy(BankService target) {
            this.target = target;
        }
        
        @Override
        public void transfer(String from, String to, int money) {
            // 前置增强
            System.out.println("开始日志...");
            long start = System.currentTimeMillis();
            
            // 调用原始对象
            target.transfer(from, to, money);
            
            // 后置增强
            System.out.println("耗时: " + (System.currentTimeMillis() - start) + "ms");
        }
    }

    // 4. 使用
    BankService service = new BankServiceProxy(new BankServiceImpl());
    service.transfer("A", "B", 100);

    缺点：每个被代理的类都要手写一个代理类 → 代码冗余

动态代理:
public class JdkProxyDemo {
public static void main(String[] args) {
    // 1. 原始对象
    BankService target = new BankServiceImpl();
    
    // 2. 创建代理
    BankService proxy = (BankService) Proxy.newProxyInstance(
        target.getClass().getClassLoader(),  // 类加载器
        target.getClass().getInterfaces(),   // 要代理的接口
        new InvocationHandler() {             // 增强逻辑
            @Override
            public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
                // 前置增强
                System.out.println("【JDK动态代理】方法: " + method.getName() + " 开始执行");
                long start = System.currentTimeMillis();
                
                // 调用原始方法
                Object result = method.invoke(target, args);
                
                // 后置增强
                System.out.println("【JDK动态代理】耗时: " + (System.currentTimeMillis() - start) + "ms");
                return result;
            }
        }
    );
    
    // 3. 调用代理
    proxy.transfer("A", "B", 100);
}
}

执行流程：
调用 proxy.transfer()
→ InvocationHandler.invoke() 
→ 前置增强
→ method.invoke(target, args)  // 真正调用原始对象
→ 后置增强

关键点：
- Proxy.newProxyInstance 在内存中动态创建了一个类
- 这个类实现了你指定的接口
- 所有方法调用都会转发到 InvocationHandler.invoke()

## 细节
Java中所有类都直接或间接继承自同一个根类 Object
package 域名链路 声明包
方法不能够嵌套
new创建的对象，即使是离开对应作用域，对应的标识符不再能使用，但是底层的内存还是没有清空，然而new创建的对象会被GC监控消除
访问控制修饰符:
    public 公共的，可以被任何其他类访问
    protected 受保护的，对于同一包内所有类和无论何处包的任何子类可见
    default 默认，只对于同一个包内类可见
    private 私有，只能在定义的类中可见，其他任何地方不可见 --> final 特性 
非访问控制修饰符:
    static 类和实例均可直接调用
    final 使不可变
java确保命名空间不冲突的方式: 将域名反转逐层命名
基本数据类型
    byte(1)、char(2)、short(2)、int(4)、long(8)、float(4)、double(8)、boolean看JVM
    对应的包装类: Byte Character Short Integer Long Float Double Boolean
    Integer 默认缓存 -128 到 127
    new 方式会无视缓存直接创建新的内存和地址，但是valueOf会优先使用缓存，缓存池生效
    Java 的集合框架（如 ArrayList, HashMap）和泛型只能存储对象，不能存储基本类型。包装类是解决这个问题的唯一途径
    包装类提供了大量的工具函数
    自动装箱和自动拆箱:
        Integer i = 100; // 等价于 Integer i = Integer.valueOf(100);
        int n = i; // 等价于 int n = i.intValue();
    基本数据类型内存不可变
字面量
    后缀: L、F、D
    前缀: 0B 0 0X
    数字字面量允许使用下划线分割
    科学计数法中间符: E
java支持通过标签控制循环
"委托"是一种设计思想——把任务交给另一个对象去执行
System.out.println() System.out.printf()
自动换行输出只能使用+拼接
格式化输出可以使用如下占位符:
    %d %s %f(无论float或double) %c %b(boolean) %n(跨平台换行，\n是Unicode编码) %% （m.n）
java的箭头函数可以使用this
只有实现Iterable接口的对象才有资格调用forEach()


