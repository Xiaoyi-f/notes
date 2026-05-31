# JavaSE 集合框架

## 一、集合框架概述

```
Collection (接口)
    ├── List (接口)        - 有序、可重复
    │   ├── ArrayList      - 数组实现，查询快，增删慢
    │   ├── LinkedList     - 链表实现，增删快，查询慢
    │   ├── Vector         - 线程安全（已过时）
    │   └── Stack          - 栈结构
    │
    ├── Set (接口)         - 无序、不可重复
    │   ├── HashSet        - 哈希表实现
    │   ├── LinkedHashSet  - 链表+哈希表，有序
    │   └── TreeSet        - 红黑树实现，有序
    │
    └── Queue (接口)       - 队列结构
        ├── LinkedList
        ├── PriorityQueue
        └── ArrayDeque

Map (接口)                - 键值对
    ├── HashMap            - 哈希表实现
    ├── LinkedHashMap      - 有序哈希表
    ├── TreeMap            - 红黑树实现，有序
    ├── HashTable          - 线程安全（已过时）
    └── ConcurrentHashMap  - 线程安全
```

## 二、List 集合

### 1. ArrayList

```java
import java.util.*;

public class ArrayListDemo {
    public static void main(String[] args) {
        // 创建 ArrayList
        List<String> list = new ArrayList<>();
        List<Integer> numbers = new ArrayList<>(10);  // 初始容量

        // 添加元素
        list.add("Apple");
        list.add("Banana");
        list.add("Orange");
        list.add(1, "Grape");  // 在指定位置插入

        // 获取元素
        String first = list.get(0);
        System.out.println("第一个元素: " + first);

        // 修改元素
        list.set(1, "Mango");

        // 删除元素
        list.remove(2);        // 按索引删除
        list.remove("Apple");  // 按对象删除

        // 查找元素
        boolean contains = list.contains("Mango");
        int index = list.indexOf("Grape");

        // 大小和判断
        System.out.println("大小: " + list.size());
        System.out.println("是否为空: " + list.isEmpty());

        // 遍历
        System.out.println("\\n遍历方式1: for循环");
        for (int i = 0; i < list.size(); i++) {
            System.out.println(list.get(i));
        }

        System.out.println("\\n遍历方式2: 增强for");
        for (String item : list) {
            System.out.println(item);
        }

        System.out.println("\\n遍历方式3: Iterator");
        Iterator<String> iterator = list.iterator();
        while (iterator.hasNext()) {
            String item = iterator.next();
            System.out.println(item);
        }

        System.out.println("\\n遍历方式4: ListIterator（双向遍历）");
        ListIterator<String> listIterator = list.listIterator(list.size());
        while (listIterator.hasPrevious()) {
            System.out.println(listIterator.previous());
        }

        System.out.println("\\n遍历方式5: forEach + Lambda（Java 8+）");
        list.forEach(item -> System.out.println(item));

        // 转换为数组
        String[] array = list.toArray(new String[0]);

        // 批量操作
        List<String> newItems = Arrays.asList("Pear", "Peach");
        list.addAll(newItems);
        list.removeAll(newItems);  // 删除所有在集合中的元素
        list.retainAll(Arrays.asList("Grape", "Mango"));  // 保留交集

        // 清空
        list.clear();

        // 数组转 List
        String[] fruits = {"Apple", "Banana", "Orange"};
        List<String> fruitList = Arrays.asList(fruits);  // 不可修改
        List<String> mutableList = new ArrayList<>(Arrays.asList(fruits));  // 可修改

        // ArrayList 性能测试
        performanceTest();
    }

    public static void performanceTest() {
        int size = 100000;

        // ArrayList 插入性能
        long start = System.currentTimeMillis();
        List<Integer> arrayList = new ArrayList<>();
        for (int i = 0; i < size; i++) {
            arrayList.add(i);  // 尾部插入快
        }
        long end = System.currentTimeMillis();
        System.out.printf("ArrayList 尾部插入 %d 个元素: %dms\\n", size, end - start);

        // 中间插入性能
        start = System.currentTimeMillis();
        for (int i = 0; i < 1000; i++) {
            arrayList.add(size / 2, -1);  // 中间插入慢
        }
        end = System.currentTimeMillis();
        System.out.printf("ArrayList 中间插入 1000 个元素: %dms\\n", end - start);

        // 随机访问性能
        start = System.currentTimeMillis();
        for (int i = 0; i < size; i++) {
            int value = arrayList.get(i);  // 随机访问快
        }
        end = System.currentTimeMillis();
        System.out.printf("ArrayList 随机访问 %d 次: %dms\\n", size, end - start);
    }
}
```

### 2. LinkedList

```java
import java.util.*;

public class LinkedListDemo {
    public static void main(String[] args) {
        // LinkedList 同时实现了 List 和 Deque 接口
        LinkedList<String> list = new LinkedList<>();

        // List 操作
        list.add("A");
        list.add("B");
        list.add("C");
        list.addFirst("First");  // 头部添加
        list.addLast("Last");    // 尾部添加

        // Deque（双端队列）操作
        list.offer("D");         // 尾部添加
        list.offerFirst("First2");
        list.offerLast("Last2");

        list.poll();             // 获取并移除头部
        list.pollFirst();
        list.pollLast();

        list.peek();             // 获取头部元素
        list.peekFirst();
        list.peekLast();

        // 栈操作
        list.push("Stack");      // 压栈
        list.pop();              // 出栈

        System.out.println("LinkedList: " + list);

        // 性能对比
        comparePerformance();
    }

    public static void comparePerformance() {
        int size = 100000;

        // LinkedList vs ArrayList 性能对比

        // 1. 尾部插入
        System.out.println("\\n=== 尾部插入性能对比 ===");
        testInsertAtEnd(size);

        // 2. 头部插入
        System.out.println("\\n=== 头部插入性能对比 ===");
        testInsertAtBeginning(size);

        // 3. 中间插入
        System.out.println("\\n=== 中间插入性能对比 ===");
        testInsertAtMiddle(size);

        // 4. 随机访问
        System.out.println("\\n=== 随机访问性能对比 ===");
        testRandomAccess(size);

        // 5. 随机删除
        System.out.println("\\n=== 随机删除性能对比 ===");
        testRandomRemove(size);
    }

    public static void testInsertAtEnd(int size) {
        // ArrayList
        long start = System.currentTimeMillis();
        List<Integer> arrayList = new ArrayList<>();
        for (int i = 0; i < size; i++) {
            arrayList.add(i);
        }
        long end = System.currentTimeMillis();
        System.out.printf("ArrayList 尾部插入: %dms\\n", end - start);

        // LinkedList
        start = System.currentTimeMillis();
        LinkedList<Integer> linkedList = new LinkedList<>();
        for (int i = 0; i < size; i++) {
            linkedList.add(i);
        }
        end = System.currentTimeMillis();
        System.out.printf("LinkedList 尾部插入: %dms\\n", end - start);
    }

    public static void testInsertAtBeginning(int size) {
        // ArrayList
        long start = System.currentTimeMillis();
        List<Integer> arrayList = new ArrayList<>();
        for (int i = 0; i < size; i++) {
            arrayList.add(0, i);
        }
        long end = System.currentTimeMillis();
        System.out.printf("ArrayList 头部插入: %dms\\n", end - start);

        // LinkedList
        start = System.currentTimeMillis();
        LinkedList<Integer> linkedList = new LinkedList<>();
        for (int i = 0; i < size; i++) {
            linkedList.addFirst(i);
        }
        end = System.currentTimeMillis();
        System.out.printf("LinkedList 头部插入: %dms\\n", end - start);
    }

    public static void testInsertAtMiddle(int size) {
        // ArrayList
        long start = System.currentTimeMillis();
        List<Integer> arrayList = new ArrayList<>();
        for (int i = 0; i < size; i++) {
            arrayList.add(i);
        }
        for (int i = 0; i < 10000; i++) {
            arrayList.add(size / 2, -1);
        }
        long end = System.currentTimeMillis();
        System.out.printf("ArrayList 中间插入 10000 次: %dms\\n", end - start);

        // LinkedList
        start = System.currentTimeMillis();
        LinkedList<Integer> linkedList = new LinkedList<>();
        for (int i = 0; i < size; i++) {
            linkedList.add(i);
        }
        ListIterator<Integer> iterator = linkedList.listIterator(size / 2);
        for (int i = 0; i < 10000; i++) {
            iterator.add(-1);
        }
        end = System.currentTimeMillis();
        System.out.printf("LinkedList 中间插入 10000 次: %dms\\n", end - start);
    }

    public static void testRandomAccess(int size) {
        // 准备数据
        List<Integer> arrayList = new ArrayList<>();
        List<Integer> linkedList = new LinkedList<>();
        Random random = new Random();

        for (int i = 0; i < size; i++) {
            arrayList.add(i);
            linkedList.add(i);
        }

        // ArrayList
        long start = System.currentTimeMillis();
        for (int i = 0; i < size; i++) {
            arrayList.get(random.nextInt(size));
        }
        long end = System.currentTimeMillis();
        System.out.printf("ArrayList 随机访问 %d 次: %dms\\n", size, end - start);

        // LinkedList
        start = System.currentTimeMillis();
        for (int i = 0; i < size; i++) {
            linkedList.get(random.nextInt(size));
        }
        end = System.currentTimeMillis();
        System.out.printf("LinkedList 随机访问 %d 次: %dms\\n", end - start);
    }

    public static void testRandomRemove(int size) {
        // 准备数据
        List<Integer> arrayList = new ArrayList<>();
        List<Integer> linkedList = new LinkedList<>();
        Random random = new Random();

        for (int i = 0; i < size; i++) {
            arrayList.add(i);
            linkedList.add(i);
        }

        // ArrayList（使用迭代器删除）
        long start = System.currentTimeMillis();
        Iterator<Integer> iter = arrayList.iterator();
        while (iter.hasNext()) {
            if (random.nextBoolean()) {
                iter.remove();
            } else {
                iter.next();
            }
        }
        long end = System.currentTimeMillis();
        System.out.printf("ArrayList 随机删除: %dms\\n", end - start);

        // LinkedList
        start = System.currentTimeMillis();
        Iterator<Integer> iter2 = linkedList.iterator();
        while (iter2.hasNext()) {
            if (random.nextBoolean()) {
                iter2.remove();
            } else {
                iter2.next();
            }
        }
        end = System.currentTimeMillis();
        System.out.printf("LinkedList 随机删除: %dms\\n", end - start);
    }
}
```

### 3. CopyOnWriteArrayList（线程安全）

```java
import java.util.concurrent.*;
import java.util.*;

public class CopyOnWriteArrayListDemo {
    public static void main(String[] args) throws InterruptedException {
        // CopyOnWriteArrayList - 写时复制，适合读多写少
        CopyOnWriteArrayList<String> list = new CopyOnWriteArrayList<>();

        // 添加数据
        list.add("A");
        list.add("B");
        list.add("C");

        // 多线程读写测试
        testConcurrentAccess();

        // 对比 ArrayList（线程不安全）
        testArrayListThreadSafety();
    }

    public static void testConcurrentAccess() throws InterruptedException {
        CopyOnWriteArrayList<Integer> list = new CopyOnWriteArrayList<>();

        // 初始化数据
        for (int i = 0; i < 1000; i++) {
            list.add(i);
        }

        // 创建多个线程同时读取
        ExecutorService executor = Executors.newFixedThreadPool(10);
        CountDownLatch latch = new CountDownLatch(10);

        long start = System.currentTimeMillis();

        for (int i = 0; i < 10; i++) {
            executor.submit(() -> {
                try {
                    // 读取操作
                    for (int j = 0; j < 100000; j++) {
                        list.get(j % list.size());
                    }
                } finally {
                    latch.countDown();
                }
            });
        }

        latch.await();
        long end = System.currentTimeMillis();

        System.out.printf("CopyOnWriteArrayList 并发读取: %dms\\n", end - start);
        executor.shutdown();
    }

    public static void testArrayListThreadSafety() {
        List<Integer> list = new ArrayList<>();
        ExecutorService executor = Executors.newFixedThreadPool(10);
        CountDownLatch latch = new CountDownLatch(10);

        // 多线程写入 ArrayList（会出现问题）
        for (int i = 0; i < 10; i++) {
            final int threadId = i;
            executor.submit(() -> {
                try {
                    for (int j = 0; j < 1000; j++) {
                        list.add(threadId * 1000 + j);
                    }
                } finally {
                    latch.countDown();
                }
            });
        }

        try {
            latch.await();
            System.out.println("ArrayList 实际大小: " + list.size());
            System.out.println("期望大小: " + (10 * 1000));
            if (list.size() < 10000) {
                System.out.println("ArrayList 在多线程下出现数据丢失！");
            }
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

        executor.shutdown();
    }
}
```

## 三、Set 集合

### 1. HashSet

```java
import java.util.*;

public class HashSetDemo {
    public static void main(String[] args) {
        // 创建 HashSet
        Set<String> set = new HashSet<>();

        // 添加元素（无序）
        set.add("Apple");
        set.add("Banana");
        set.add("Orange");
        set.add("Apple");  // 重复元素不会被添加

        System.out.println("HashSet: " + set);
        System.out.println("大小: " + set.size());

        // 判断包含
        System.out.println("包含Apple: " + set.contains("Apple"));

        // 删除
        set.remove("Banana");

        // 遍历
        for (String item : set) {
            System.out.println(item);
        }

        // 自定义对象使用 HashSet（需要重写 hashCode 和 equals）
        Set<Person> personSet = new HashSet<>();
        personSet.add(new Person("张三", 25));
        personSet.add(new Person("李四", 30));
        personSet.add(new Person("张三", 25));  // 不会被添加

        System.out.println("\\nPersonSet 大小: " + personSet.size());  // 应该是2

        // 集合操作
        Set<String> set1 = new HashSet<>(Arrays.asList("A", "B", "C"));
        Set<String> set2 = new HashSet<>(Arrays.asList("C", "D", "E"));

        // 并集
        Set<String> union = new HashSet<>(set1);
        union.addAll(set2);
        System.out.println("并集: " + union);

        // 交集
        Set<String> intersection = new HashSet<>(set1);
        intersection.retainAll(set2);
        System.out.println("交集: " + intersection);

        // 差集
        Set<String> difference = new HashSet<>(set1);
        difference.removeAll(set2);
        System.out.println("差集: " + difference);
    }
}

class Person {
    private String name;
    private int age;

    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }

    // 重写 hashCode
    @Override
    public int hashCode() {
        return Objects.hash(name, age);
    }

    // 重写 equals
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        Person person = (Person) obj;
        return age == person.age && Objects.equals(name, person.name);
    }

    @Override
    public String toString() {
        return name + "(" + age + ")";
    }
}
```

### 2. LinkedHashSet

```java
import java.util.*;

public class LinkedHashSetDemo {
    public static void main(String[] args) {
        // LinkedHashSet - 有序的 HashSet
        Set<String> linkedHashSet = new LinkedHashSet<>();

        linkedHashSet.add("A");
        linkedHashSet.add("B");
        linkedHashSet.add("C");
        linkedHashSet.add("D");

        System.out.println("LinkedHashSet: " + linkedHashSet);
        System.out.println("插入顺序保持: " + (new ArrayList<>(linkedHashSet).equals(
            Arrays.asList("A", "B", "C", "D"))));

        // 使用场景：需要去重但保持插入顺序
        List<String> names = Arrays.asList("张三", "李四", "张三", "王五", "李四");
        Set<String> uniqueNames = new LinkedHashSet<>(names);

        System.out.println("\\n原始列表: " + names);
        System.out.println("去重后: " + new ArrayList<>(uniqueNames));
    }
}
```

### 3. TreeSet

```java
import java.util.*;

public class TreeSetDemo {
    public static void main(String[] args) {
        // TreeSet - 自然排序
        Set<Integer> treeSet = new TreeSet<>();

        treeSet.add(5);
        treeSet.add(2);
        treeSet.add(8);
        treeSet.add(1);
        treeSet.add(9);

        System.out.println("TreeSet: " + treeSet);  // 自动排序: [1, 2, 5, 8, 9]

        // 特有方法
        System.out.println("第一个元素: " + treeSet.first());
        System.out.println("最后一个元素: " + treeSet.last());
        System.out.println("小于5的子集: " + treeSet.headSet(5));
        System.out.println("大于等于5的子集: " + treeSet.tailSet(5));

        // 自定义排序
        Set<String> reverseSet = new TreeSet<>(Collections.reverseOrder());
        reverseSet.add("A");
        reverseSet.add("B");
        reverseSet.add("C");
        System.out.println("\\n倒序TreeSet: " + reverseSet);

        // 自定义对象排序（实现 Comparable 接口）
        Set<Student> studentSet = new TreeSet<>();
        studentSet.add(new Student("张三", 85));
        studentSet.add(new Student("李四", 92));
        studentSet.add(new Student("王五", 78));
        studentSet.add(new Student("赵六", 85));

        System.out.println("\\n按分数排序的学生:");
        for (Student student : studentSet) {
            System.out.println(student);
        }

        // 使用 Comparator 自定义排序
        Set<Student> nameOrderSet = new TreeSet<>(Comparator.comparing(Student::getName));
        nameOrderSet.addAll(studentSet);
        System.out.println("\\n按姓名排序的学生:");
        for (Student student : nameOrderSet) {
            System.out.println(student);
        }
    }
}

class Student implements Comparable<Student> {
    private String name;
    private int score;

    public Student(String name, int score) {
        this.name = name;
        this.score = score;
    }

    public String getName() {
        return name;
    }

    @Override
    public int compareTo(Student other) {
        // 先按分数降序，分数相同按姓名升序
        if (this.score != other.score) {
            return other.score - this.score;
        }
        return this.name.compareTo(other.name);
    }

    @Override
    public String toString() {
        return name + ": " + score;
    }
}
```

## 四、Map 集合

### 1. HashMap

```java
import java.util.*;
import java.util.concurrent.*;

public class HashMapDemo {
    public static void main(String[] args) {
        // 创建 HashMap
        Map<String, Integer> map = new HashMap<>();

        // 添加元素
        map.put("Apple", 5);
        map.put("Banana", 3);
        map.put("Orange", 7);
        map.put("Grape", 4);
        map.put("Apple", 10);  // 覆盖旧值

        System.out.println("HashMap: " + map);
        System.out.println("大小: " + map.size());

        // 获取元素
        Integer appleCount = map.get("Apple");
        System.out.println("Apple 数量: " + appleCount);

        // 获取不存在的键（返回 null 或默认值）
        Integer pearCount = map.get("Pear");
        System.out.println("Pear 数量: " + pearCount);
        System.out.println("Pear 数量(getOrDefault): " + map.getOrDefault("Pear", 0));

        // 判断包含
        System.out.println("包含Apple: " + map.containsKey("Apple"));
        System.out.println("包含值5: " + map.containsValue(5));

        // 获取所有键和值
        Set<String> keys = map.keySet();
        Collection<Integer> values = map.values();
        Set<Map.Entry<String, Integer>> entries = map.entrySet();

        // 遍历方式
        System.out.println("\\n遍历方式1: keySet");
        for (String key : keys) {
            System.out.println(key + " = " + map.get(key));
        }

        System.out.println("\\n遍历方式2: entrySet（推荐）");
        for (Map.Entry<String, Integer> entry : entries) {
            System.out.println(entry.getKey() + " = " + entry.getValue());
        }

        System.out.println("\\n遍历方式3: forEach + Lambda");
        map.forEach((key, value) -> System.out.println(key + " = " + value));

        // 删除元素
        map.remove("Banana");
        System.out.println("\\n删除Banana后: " + map);

        // 批量操作
        Map<String, Integer> newItems = new HashMap<>();
        newItems.put("Pear", 6);
        newItems.put("Peach", 8);
        map.putAll(newItems);

        // 清空
        // map.clear();

        // HashMap 实现统计词频
        countWordFrequency();

        // 多线程 HashMap 的问题
        testHashMapThreadSafety();
    }

    public static void countWordFrequency() {
        String text = "Hello World Hello Java World Programming Hello";

        String[] words = text.split(" ");
        Map<String, Integer> frequency = new HashMap<>();

        for (String word : words) {
            // 方式1
            /*
            if (frequency.containsKey(word)) {
                frequency.put(word, frequency.get(word) + 1);
            } else {
                frequency.put(word, 1);
            }
            */

            // 方式2（推荐）
            frequency.put(word, frequency.getOrDefault(word, 0) + 1);

            // 方式3（Java 8+）
            // frequency.merge(word, 1, Integer::sum);
        }

        System.out.println("\\n词频统计: " + frequency);

        // 按值排序
        List<Map.Entry<String, Integer>> sorted = new ArrayList<>(frequency.entrySet());
        sorted.sort(Map.Entry.<String, Integer>comparingByValue().reversed());

        System.out.println("按频率排序:");
        sorted.forEach(entry -> System.out.println(entry.getKey() + ": " + entry.getValue()));
    }

    public static void testHashMapThreadSafety() {
        // HashMap 在多线程下不安全，会死循环或数据丢失
        Map<Integer, Integer> map = new HashMap<>();
        ExecutorService executor = Executors.newFixedThreadPool(10);
        CountDownLatch latch = new CountDownLatch(10);

        for (int i = 0; i < 10; i++) {
            final int threadId = i;
            executor.submit(() -> {
                try {
                    for (int j = 0; j < 1000; j++) {
                        map.put(threadId * 1000 + j, j);
                    }
                } finally {
                    latch.countDown();
                }
            });
        }

        try {
            latch.await();
            System.out.println("\\nHashMap 实际大小: " + map.size());
            System.out.println("期望大小: " + (10 * 1000));
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

        executor.shutdown();
    }
}
```

### 2. ConcurrentHashMap（线程安全）

```java
import java.util.*;
import java.util.concurrent.*;

public class ConcurrentHashMapDemo {
    public static void main(String[] args) throws InterruptedException {
        // ConcurrentHashMap - 线程安全的 HashMap
        ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();

        // 基本操作与 HashMap 相同
        map.put("A", 1);
        map.put("B", 2);
        map.put("C", 3);

        // 原子操作
        map.putIfAbsent("D", 4);
        map.replace("A", 10);  // 原子替换
        map.replace("B", 2, 20);  // 只有旧值匹配时才替换

        // 计算操作（原子）
        map.compute("C", (key, value) -> value == null ? 0 : value * 2);
        map.computeIfAbsent("E", key -> 5);
        map.computeIfPresent("A", (key, value) -> value + 1);

        System.out.println("ConcurrentHashMap: " + map);

        // 合并操作
        map.merge("F", 100, Integer::sum);
        map.merge("A", 1, Integer::sum);

        // 多线程测试
        testConcurrentPerformance();

        // 对比性能
        comparePerformance();
    }

    public static void testConcurrentPerformance() throws InterruptedException {
        ConcurrentHashMap<Integer, Integer> map = new ConcurrentHashMap<>();
        ExecutorService executor = Executors.newFixedThreadPool(10);
        CountDownLatch latch = new CountDownLatch(10);

        long start = System.currentTimeMillis();

        for (int i = 0; i < 10; i++) {
            final int threadId = i;
            executor.submit(() -> {
                try {
                    for (int j = 0; j < 10000; j++) {
                        // 原子操作
                        map.merge(threadId, 1, Integer::sum);
                    }
                } finally {
                    latch.countDown();
                }
            });
        }

        latch.await();
        long end = System.currentTimeMillis();

        System.out.println("\\nConcurrentHashMap 并发写入测试:");
        System.out.println("实际大小: " + map.size());
        System.out.println("期望大小: " + 10);
        System.out.println("耗时: " + (end - start) + "ms");

        executor.shutdown();
    }

    public static void comparePerformance() throws InterruptedException {
        int threads = 10;
        int operations = 100000;

        // ConcurrentHashMap 性能
        ConcurrentHashMap<Integer, Integer> concurrentMap = new ConcurrentHashMap<>();
        ExecutorService executor = Executors.newFixedThreadPool(threads);
        CountDownLatch latch = new CountDownLatch(threads);

        long start = System.currentTimeMillis();

        for (int i = 0; i < threads; i++) {
            final int threadId = i;
            executor.submit(() -> {
                try {
                    for (int j = 0; j < operations; j++) {
                        concurrentMap.put(threadId * operations + j, j);
                    }
                } finally {
                    latch.countDown();
                }
            });
        }

        latch.await();
        long concurrentTime = System.currentTimeMillis() - start;

        // Collections.synchronizedMap 性能
        Map<Integer, Integer> synchronizedMap = Collections.synchronizedMap(new HashMap<>());
        executor = Executors.newFixedThreadPool(threads);
        latch = new CountDownLatch(threads);

        start = System.currentTimeMillis();

        for (int i = 0; i < threads; i++) {
            final int threadId = i;
            executor.submit(() -> {
                try {
                    for (int j = 0; j < operations; j++) {
                        synchronizedMap.put(threadId * operations + j, j);
                    }
                } finally {
                    latch.countDown();
                }
            });
        }

        latch.await();
        long synchronizedTime = System.currentTimeMillis() - start;

        System.out.println("\\n性能对比:");
        System.out.printf("ConcurrentHashMap: %dms\\n", concurrentTime);
        System.out.printf("synchronizedMap: %dms\\n", synchronizedTime);
        System.out.printf("ConcurrentHashMap 更快: %.2f倍\\n", (double)synchronizedTime / concurrentTime);

        executor.shutdown();
    }
}
```

## 五、Collections 工具类

```java
import java.util.*;

public class CollectionsDemo {
    public static void main(String[] args) {
        // 排序
        List<Integer> numbers = new ArrayList<>(Arrays.asList(5, 2, 8, 1, 9, 3));
        System.out.println("排序前: " + numbers);
        Collections.sort(numbers);
        System.out.println("排序后: " + numbers);

        // 反向排序
        Collections.sort(numbers, Collections.reverseOrder());
        System.out.println("降序排序: " + numbers);

        // 打乱
        Collections.shuffle(numbers);
        System.out.println("打乱后: " + numbers);

        // 查找（需要先排序）
        Collections.sort(numbers);
        int index = Collections.binarySearch(numbers, 5);
        System.out.println("\\n5的位置: " + index);

        // 填充
        List<Integer> filled = new ArrayList<>(Arrays.asList(1, 2, 3, 4, 5));
        Collections.fill(filled, 0);
        System.out.println("\\n填充后: " + filled);

        // 复制
        List<Integer> source = new ArrayList<>(Arrays.asList(1, 2, 3));
        List<Integer> dest = new ArrayList<>(Arrays.asList(0, 0, 0));
        Collections.copy(dest, source);
        System.out.println("复制后: " + dest);

        // 交换
        List<Integer> swapList = new ArrayList<>(Arrays.asList(1, 2, 3, 4, 5));
        Collections.swap(swapList, 0, 4);
        System.out.println("\\n交换后: " + swapList);

        // 旋转
        List<Integer> rotateList = new ArrayList<>(Arrays.asList(1, 2, 3, 4, 5));
        Collections.rotate(rotateList, 2);
        System.out.println("右旋2位: " + rotateList);

        // 频率统计
        List<String> words = Arrays.asList("a", "b", "a", "c", "a", "b");
        int freq = Collections.frequency(words, "a");
        System.out.println("\\n'a' 出现次数: " + freq);

        // 最大最小值
        System.out.println("最大值: " + Collections.max(numbers));
        System.out.println("最小值: " + Collections.min(numbers));

        // 不可修改集合
        List<String> immutableList = Collections.unmodifiableList(
            new ArrayList<>(Arrays.asList("A", "B", "C"))
        );
        // immutableList.add("D");  // 会抛出异常

        // 同步集合
        List<String> syncList = Collections.synchronizedList(new ArrayList<>());
        syncList.add("A");

        // 空集合
        List<String> emptyList = Collections.emptyList();
        Set<String> emptySet = Collections.emptySet();
        Map<String, Integer> emptyMap = Collections.emptyMap();

        // 单元素集合
        List<String> singletonList = Collections.singletonList("A");
        Set<String> singletonSet = Collections.singleton("A");

        // nCopies
        List<Integer> nCopies = Collections.nCopies(5, 100);
        System.out.println("\\nnCopies: " + nCopies);
    }
}
```

## 六、实战练习：购物车系统

```java
import java.util.*;

public class ShoppingCart {
    private Map<String, CartItem> items = new HashMap<>();
    private Map<String, Product> products = new HashMap<>();

    // 产品类
    static class Product {
        private String id;
        private String name;
        private double price;

        public Product(String id, String name, double price) {
            this.id = id;
            this.name = name;
            this.price = price;
        }

        public String getId() { return id; }
        public String getName() { return name; }
        public double getPrice() { return price; }

        @Override
        public String toString() {
            return name + " (¥" + price + ")";
        }
    }

    // 购物车项
    static class CartItem {
        private Product product;
        private int quantity;

        public CartItem(Product product, int quantity) {
            this.product = product;
            this.quantity = quantity;
        }

        public Product getProduct() { return product; }
        public int getQuantity() { return quantity; }
        public double getTotalPrice() { return product.getPrice() * quantity; }

        public void setQuantity(int quantity) {
            this.quantity = quantity;
        }

        @Override
        public String toString() {
            return product + " x " + quantity + " = ¥" + getTotalPrice();
        }
    }

    // 添加商品
    public void addProduct(String productId, int quantity) {
        Product product = products.get(productId);
        if (product == null) {
            System.out.println("商品不存在");
            return;
        }

        CartItem item = items.get(productId);
        if (item == null) {
            items.put(productId, new CartItem(product, quantity));
        } else {
            item.setQuantity(item.getQuantity() + quantity);
        }

        System.out.println("添加成功: " + product.getName() + " x " + quantity);
    }

    // 移除商品
    public void removeProduct(String productId) {
        CartItem item = items.remove(productId);
        if (item != null) {
            System.out.println("移除成功: " + item.getProduct().getName());
        } else {
            System.out.println("商品不存在于购物车");
        }
    }

    // 更新数量
    public void updateQuantity(String productId, int quantity) {
        CartItem item = items.get(productId);
        if (item != null) {
            if (quantity <= 0) {
                removeProduct(productId);
            } else {
                item.setQuantity(quantity);
                System.out.println("更新成功: " + item.getProduct().getName() + " x " + quantity);
            }
        }
    }

    // 获取总价
    public double getTotalPrice() {
        double total = 0;
        for (CartItem item : items.values()) {
            total += item.getTotalPrice();
        }
        return total;
    }

    // 获取总数量
    public int getTotalQuantity() {
        int total = 0;
        for (CartItem item : items.values()) {
            total += item.getQuantity();
        }
        return total;
    }

    // 显示购物车
    public void displayCart() {
        if (items.isEmpty()) {
            System.out.println("购物车为空");
            return;
        }

        System.out.println("\\n=== 购物车 ===");
        System.out.println("商品\\t\\t数量\\t单价\\t小计");
        System.out.println("--------------------------------");

        for (CartItem item : items.values()) {
            Product p = item.getProduct();
            System.out.printf("%-12s\\t%d\\t¥%.2f\\t¥%.2f\\n",
                p.getName(),
                item.getQuantity(),
                p.getPrice(),
                item.getTotalPrice()
            );
        }

        System.out.println("--------------------------------");
        System.out.printf("总计: %d 件商品，总价: ¥%.2f\\n",
            getTotalQuantity(), getTotalPrice());
    }

    // 清空购物车
    public void clear() {
        items.clear();
        System.out.println("购物车已清空");
    }

    // 初始化商品
    public void initProducts() {
        products.put("P001", new Product("P001", "手机", 3999.00));
        products.put("P002", new Product("P002", "笔记本", 5999.00));
        products.put("P003", new Product("P003", "耳机", 299.00));
        products.put("P004", new Product("P004", "键盘", 199.00));
        products.put("P005", new Product("P005", "鼠标", 99.00));
    }

    public static void main(String[] args) {
        ShoppingCart cart = new ShoppingCart();
        cart.initProducts();

        Scanner scanner = new Scanner(System.in);

        while (true) {
            System.out.println("\\n=== 购物车系统 ===");
            System.out.println("1. 查看商品列表");
            System.out.println("2. 添加商品到购物车");
            System.out.println("3. 移除购物车商品");
            System.out.println("4. 修改商品数量");
            System.out.println("5. 查看购物车");
            System.out.println("6. 清空购物车");
            System.out.println("7. 结算");
            System.out.println("0. 退出");
            System.out.print("请选择: ");

            int choice = scanner.nextInt();

            switch (choice) {
                case 1:
                    System.out.println("\\n商品列表:");
                    for (Product product : cart.products.values()) {
                        System.out.println(product.getId() + ". " + product);
                    }
                    break;

                case 2:
                    scanner.nextLine();
                    System.out.print("请输入商品ID: ");
                    String addId = scanner.nextLine();
                    System.out.print("请输入数量: ");
                    int addQty = scanner.nextInt();
                    cart.addProduct(addId, addQty);
                    break;

                case 3:
                    scanner.nextLine();
                    System.out.print("请输入要移除的商品ID: ");
                    String removeId = scanner.nextLine();
                    cart.removeProduct(removeId);
                    break;

                case 4:
                    scanner.nextLine();
                    System.out.print("请输入商品ID: ");
                    String updateId = scanner.nextLine();
                    System.out.print("请输入新数量: ");
                    int updateQty = scanner.nextInt();
                    cart.updateQuantity(updateId, updateQty);
                    break;

                case 5:
                    cart.displayCart();
                    break;

                case 6:
                    cart.clear();
                    break;

                case 7:
                    cart.displayCart();
                    System.out.println("\\n感谢您的购买！");
                    cart.clear();
                    break;

                case 0:
                    System.out.println("再见！");
                    scanner.close();
                    return;

                default:
                    System.out.println("无效的选择");
            }
        }
    }
}
```

## 小结

本节学习了 Java 集合框架：

- **List** - ArrayList、LinkedList、CopyOnWriteArrayList
- **Set** - HashSet、LinkedHashSet、TreeSet
- **Map** - HashMap、ConcurrentHashMap
- **工具类** - Collections 排序、查找等操作
- **实战项目** - 购物车系统

## 实践练习

### 编程题
1. 实现一个 LRU（最近最少使用）缓存，用 LinkedHashMap 实现，支持 `get(key)` 和 `put(key, value)` 操作，容量达到上限时自动删除最久未使用的元素。
2. 扩展购物车系统：添加"商品分类浏览""按价格排序""库存检查"功能。

### 思考题
1. HashMap 在 JDK 1.8 中为什么用红黑树替代链表（当链表长度 > 8 时）？
2. CopyOnWriteArrayList 适合什么场景？为什么不适用于写多读少的场景？

### 自测题
1. ArrayList 和 LinkedList 的内部实现原理和性能差异？
2. HashSet 如何判断元素重复？
3. ConcurrentHashMap 在 JDK 1.8 中用什么方式保证线程安全？

下一步将学习 Java 高级特性（→ `03-java-se-advanced.md`）。