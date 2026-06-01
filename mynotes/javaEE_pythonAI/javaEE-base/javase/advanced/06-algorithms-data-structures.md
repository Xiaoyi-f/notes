# 算法与数据结构

## 一、时间复杂度与空间复杂度

### 1. 复杂度定义

```java
/**
 * 时间复杂度：算法执行时间随输入规模增长的度量
 * 空间复杂度：算法所需额外空间随输入规模增长的度量
 */

// 常见复杂度对比
public class ComplexityComparison {
    // O(1) - 常数时间
    public int getFirst(int[] arr) {
        return arr[0];  // 无论数组多大，只执行一次
    }

    // O(log n) - 对数时间
    public int binarySearch(int[] arr, int target) {
        int left = 0, right = arr.length - 1;
        while (left <= right) {
            int mid = left + (right - left) / 2;
            if (arr[mid] == target) return mid;
            if (arr[mid] < target) left = mid + 1;
            else right = mid - 1;
        }
        return -1;  // 每次循环范围减半
    }

    // O(n) - 线性时间
    public int sum(int[] arr) {
        int total = 0;
        for (int num : arr) {
            total += num;  // 遍历一次
        }
        return total;
    }

    // O(n log n) - 线性对数时间
    public void quickSort(int[] arr, int low, int high) {
        if (low < high) {
            int pivot = partition(arr, low, high);
            quickSort(arr, low, pivot - 1);
            quickSort(arr, pivot + 1, high);  // 分治递归
        }
    }

    // O(n²) - 平方时间
    public void bubbleSort(int[] arr) {
        for (int i = 0; i < arr.length; i++) {
            for (int j = 0; j < arr.length - i - 1; j++) {
                if (arr[j] > arr[j + 1]) {
                    // 交换
                    int temp = arr[j];
                    arr[j] = arr[j + 1];
                    arr[j + 1] = temp;
                }
            }
        }
    }

    // O(2ⁿ) - 指数时间
    public int fibonacci(int n) {
        if (n <= 1) return n;
        return fibonacci(n - 1) + fibonacci(n - 2);  // 递归树
    }

    // O(n!) - 阶乘时间
    public void permutation(String str, int l, int r) {
        if (l == r) {
            System.out.println(str);
        } else {
            for (int i = l; i <= r; i++) {
                str = swap(str, l, i);
                permutation(str, l + 1, r);
                str = swap(str, l, i);  // 回溯
            }
        }
    }
}
```

## 二、排序算法

### 1. 冒泡排序

```java
public class BubbleSort {
    public static void sort(int[] arr) {
        int n = arr.length;
        boolean swapped;
        for (int i = 0; i < n - 1; i++) {
            swapped = false;
            for (int j = 0; j < n - i - 1; j++) {
                if (arr[j] > arr[j + 1]) {
                    // 交换相邻元素
                    int temp = arr[j];
                    arr[j] = arr[j + 1];
                    arr[j + 1] = temp;
                    swapped = true;
                }
            }
            // 如果没有交换，说明已经有序
            if (!swapped) break;
        }
    }

    // 时间复杂度：O(n²)
    // 空间复杂度：O(1)
    // 稳定性：稳定
}
```

### 2. 选择排序

```java
public class SelectionSort {
    public static void sort(int[] arr) {
        int n = arr.length;
        for (int i = 0; i < n - 1; i++) {
            int minIdx = i;
            // 找到最小元素
            for (int j = i + 1; j < n; j++) {
                if (arr[j] < arr[minIdx]) {
                    minIdx = j;
                }
            }
            // 交换
            if (minIdx != i) {
                int temp = arr[i];
                arr[i] = arr[minIdx];
                arr[minIdx] = temp;
            }
        }
    }

    // 时间复杂度：O(n²)
    // 空间复杂度：O(1)
    // 稳定性：不稳定
}
```

### 3. 插入排序

```java
public class InsertionSort {
    public static void sort(int[] arr) {
        int n = arr.length;
        for (int i = 1; i < n; i++) {
            int key = arr[i];
            int j = i - 1;
            // 将大于 key 的元素后移
            while (j >= 0 && arr[j] > key) {
                arr[j + 1] = arr[j];
                j--;
            }
            arr[j + 1] = key;
        }
    }

    // 时间复杂度：O(n²)
    // 空间复杂度：O(1)
    // 稳定性：稳定
    // 适用场景：小规模数据或基本有序的数据
}
```

### 4. 快速排序

```java
public class QuickSort {
    public static void sort(int[] arr) {
        quickSort(arr, 0, arr.length - 1);
    }

    private static void quickSort(int[] arr, int low, int high) {
        if (low < high) {
            int pivotIndex = partition(arr, low, high);
            quickSort(arr, low, pivotIndex - 1);
            quickSort(arr, pivotIndex + 1, high);
        }
    }

    private static int partition(int[] arr, int low, int high) {
        int pivot = arr[high];  // 选择最后一个元素作为基准
        int i = low - 1;  // 小于基准的元素的边界

        for (int j = low; j < high; j++) {
            if (arr[j] < pivot) {
                i++;
                // 交换
                int temp = arr[i];
                arr[i] = arr[j];
                arr[j] = temp;
            }
        }
        // 将基准放到正确位置
        int temp = arr[i + 1];
        arr[i + 1] = arr[high];
        arr[high] = temp;

        return i + 1;
    }

    // 时间复杂度：平均 O(n log n)，最坏 O(n²)
    // 空间复杂度：O(log n) 递归栈
    // 稳定性：不稳定
    // 适用场景：大规模数据，平均性能最好
}
```

### 5. 归并排序

```java
public class MergeSort {
    public static void sort(int[] arr) {
        if (arr.length > 1) {
            int mid = arr.length / 2;
            int[] left = Arrays.copyOfRange(arr, 0, mid);
            int[] right = Arrays.copyOfRange(arr, mid, arr.length);

            sort(left);
            sort(right);
            merge(arr, left, right);
        }
    }

    private static void merge(int[] arr, int[] left, int[] right) {
        int i = 0, j = 0, k = 0;
        while (i < left.length && j < right.length) {
            if (left[i] <= right[j]) {
                arr[k++] = left[i++];
            } else {
                arr[k++] = right[j++];
            }
        }
        while (i < left.length) {
            arr[k++] = left[i++];
        }
        while (j < right.length) {
            arr[k++] = right[j++];
        }
    }

    // 时间复杂度：O(n log n)
    // 空间复杂度：O(n)
    // 稳定性：稳定
    // 适用场景：大规模数据，稳定排序
}
```

### 6. 堆排序

```java
public class HeapSort {
    public static void sort(int[] arr) {
        int n = arr.length;

        // 构建大顶堆
        for (int i = n / 2 - 1; i >= 0; i--) {
            heapify(arr, n, i);
        }

        // 逐个取出堆顶元素
        for (int i = n - 1; i > 0; i--) {
            // 交换堆顶和最后一个元素
            int temp = arr[0];
            arr[0] = arr[i];
            arr[i] = temp;

            // 重新堆化
            heapify(arr, i, 0);
        }
    }

    private static void heapify(int[] arr, int n, int i) {
        int largest = i;
        int left = 2 * i + 1;
        int right = 2 * i + 2;

        if (left < n && arr[left] > arr[largest]) {
            largest = left;
        }
        if (right < n && arr[right] > arr[largest]) {
            largest = right;
        }

        if (largest != i) {
            int temp = arr[i];
            arr[i] = arr[largest];
            arr[largest] = temp;

            heapify(arr, n, largest);
        }
    }

    // 时间复杂度：O(n log n)
    // 空间复杂度：O(1)
    // 稳定性：不稳定
    // 适用场景：内存受限的场景
}
```

## 三、查找算法

### 1. 二分查找

```java
public class BinarySearch {
    // 递归实现
    public static int searchRecursive(int[] arr, int target, int left, int right) {
        if (left > right) {
            return -1;
        }
        int mid = left + (right - left) / 2;
        if (arr[mid] == target) {
            return mid;
        } else if (arr[mid] < target) {
            return searchRecursive(arr, target, mid + 1, right);
        } else {
            return searchRecursive(arr, target, left, mid - 1);
        }
    }

    // 迭代实现
    public static int searchIterative(int[] arr, int target) {
        int left = 0, right = arr.length - 1;
        while (left <= right) {
            int mid = left + (right - left) / 2;
            if (arr[mid] == target) {
                return mid;
            } else if (arr[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        return -1;
    }

    // 查找第一个等于 target 的元素
    public static int findFirst(int[] arr, int target) {
        int left = 0, right = arr.length - 1;
        int result = -1;
        while (left <= right) {
            int mid = left + (right - left) / 2;
            if (arr[mid] == target) {
                result = mid;
                right = mid - 1;  // 继续向左查找
            } else if (arr[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        return result;
    }

    // 查找最后一个等于 target 的元素
    public static int findLast(int[] arr, int target) {
        int left = 0, right = arr.length - 1;
        int result = -1;
        while (left <= right) {
            int mid = left + (right - left) / 2;
            if (arr[mid] == target) {
                result = mid;
                left = mid + 1;  // 继续向右查找
            } else if (arr[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        return result;
    }

    // 时间复杂度：O(log n)
    // 前提：数组必须有序
}
```

## 四、数据结构

### 1. 数组与链表

```java
// 单链表实现
public class LinkedList {
    private Node head;
    private int size;

    private static class Node {
        int data;
        Node next;

        Node(int data) {
            this.data = data;
        }
    }

    // 添加元素
    public void add(int data) {
        Node newNode = new Node(data);
        if (head == null) {
            head = newNode;
        } else {
            Node current = head;
            while (current.next != null) {
                current = current.next;
            }
            current.next = newNode;
        }
        size++;
    }

    // 删除元素
    public boolean remove(int data) {
        if (head == null) return false;

        if (head.data == data) {
            head = head.next;
            size--;
            return true;
        }

        Node current = head;
        while (current.next != null && current.next.data != data) {
            current = current.next;
        }

        if (current.next != null) {
            current.next = current.next.next;
            size--;
            return true;
        }
        return false;
    }

    // 反转链表
    public void reverse() {
        Node prev = null;
        Node current = head;
        while (current != null) {
            Node next = current.next;
            current.next = prev;
            prev = current;
            current = next;
        }
        head = prev;
    }

    // 检测环
    public boolean hasCycle() {
        if (head == null) return false;

        Node slow = head;
        Node fast = head;

        while (fast != null && fast.next != null) {
            slow = slow.next;
            fast = fast.next.next;
            if (slow == fast) {
                return true;
            }
        }
        return false;
    }
}

// 双向链表实现
public class DoublyLinkedList {
    private Node head;
    private Node tail;
    private int size;

    private static class Node {
        int data;
        Node prev;
        Node next;

        Node(int data) {
            this.data = data;
        }
    }

    public void addFirst(int data) {
        Node newNode = new Node(data);
        if (head == null) {
            head = tail = newNode;
        } else {
            newNode.next = head;
            head.prev = newNode;
            head = newNode;
        }
        size++;
    }

    public void addLast(int data) {
        Node newNode = new Node(data);
        if (tail == null) {
            head = tail = newNode;
        } else {
            newNode.prev = tail;
            tail.next = newNode;
            tail = newNode;
        }
        size++;
    }
}
```

### 2. 栈与队列

```java
// 栈实现（使用数组）
public class Stack {
    private int[] elements;
    private int top;
    private int capacity;

    public Stack(int capacity) {
        this.capacity = capacity;
        this.elements = new int[capacity];
        this.top = -1;
    }

    public void push(int data) {
        if (isFull()) {
            throw new StackOverflowError("Stack is full");
        }
        elements[++top] = data;
    }

    public int pop() {
        if (isEmpty()) {
            throw new EmptyStackException();
        }
        return elements[top--];
    }

    public int peek() {
        if (isEmpty()) {
            throw new EmptyStackException();
        }
        return elements[top];
    }

    public boolean isEmpty() {
        return top == -1;
    }

    public boolean isFull() {
        return top == capacity - 1;
    }

    public int size() {
        return top + 1;
    }
}

// 队列实现（使用数组）
public class Queue {
    private int[] elements;
    private int front;
    private int rear;
    private int size;
    private int capacity;

    public Queue(int capacity) {
        this.capacity = capacity;
        this.elements = new int[capacity];
        this.front = 0;
        this.rear = -1;
        this.size = 0;
    }

    public void enqueue(int data) {
        if (isFull()) {
            throw new IllegalStateException("Queue is full");
        }
        rear = (rear + 1) % capacity;
        elements[rear] = data;
        size++;
    }

    public int dequeue() {
        if (isEmpty()) {
            throw new IllegalStateException("Queue is empty");
        }
        int data = elements[front];
        front = (front + 1) % capacity;
        size--;
        return data;
    }

    public int peek() {
        if (isEmpty()) {
            throw new IllegalStateException("Queue is empty");
        }
        return elements[front];
    }

    public boolean isEmpty() {
        return size == 0;
    }

    public boolean isFull() {
        return size == capacity;
    }
}
```

### 3. 树

```java
// 二叉树节点
class TreeNode {
    int val;
    TreeNode left;
    TreeNode right;

    TreeNode(int val) {
        this.val = val;
    }
}

// 二叉搜索树
public class BST {
    private TreeNode root;

    // 插入
    public void insert(int val) {
        root = insertRec(root, val);
    }

    private TreeNode insertRec(TreeNode root, int val) {
        if (root == null) {
            return new TreeNode(val);
        }
        if (val < root.val) {
            root.left = insertRec(root.left, val);
        } else if (val > root.val) {
            root.right = insertRec(root.right, val);
        }
        return root;
    }

    // 查找
    public boolean search(int val) {
        return searchRec(root, val);
    }

    private boolean searchRec(TreeNode root, int val) {
        if (root == null) {
            return false;
        }
        if (root.val == val) {
            return true;
        }
        if (val < root.val) {
            return searchRec(root.left, val);
        }
        return searchRec(root.right, val);
    }

    // 中序遍历（得到有序序列）
    public void inorder() {
        inorderRec(root);
    }

    private void inorderRec(TreeNode root) {
        if (root != null) {
            inorderRec(root.left);
            System.out.print(root.val + " ");
            inorderRec(root.right);
        }
    }

    // 层序遍历
    public void levelOrder() {
        if (root == null) return;

        Queue<TreeNode> queue = new java.util.LinkedList<>();
        queue.offer(root);

        while (!queue.isEmpty()) {
            TreeNode node = queue.poll();
            System.out.print(node.val + " ");

            if (node.left != null) queue.offer(node.left);
            if (node.right != null) queue.offer(node.right);
        }
    }
}
```

### 4. 哈希表

```java
// 简单哈希表实现
public class HashMap<K, V> {
    private static final int DEFAULT_CAPACITY = 16;
    private static final float LOAD_FACTOR = 0.75f;

    private Entry<K, V>[] table;
    private int size;
    private int threshold;

    @SuppressWarnings("unchecked")
    public HashMap() {
        table = new Entry[DEFAULT_CAPACITY];
        threshold = (int) (DEFAULT_CAPACITY * LOAD_FACTOR);
    }

    public void put(K key, V value) {
        if (size >= threshold) {
            resize();
        }

        int index = getIndex(key);
        Entry<K, V> entry = table[index];

        while (entry != null) {
            if (entry.key.equals(key)) {
                entry.value = value;
                return;
            }
            entry = entry.next;
        }

        // 头插法
        Entry<K, V> newEntry = new Entry<>(key, value, table[index]);
        table[index] = newEntry;
        size++;
    }

    public V get(K key) {
        int index =getIndex(key);
        Entry<K, V> entry = table[index];

        while (entry != null) {
            if (entry.key.equals(key)) {
                return entry.value;
            }
            entry = entry.next;
        }
        return null;
    }

    public V remove(K key) {
        int index = getIndex(key);
        Entry<K, V> entry = table[index];
        Entry<K, V> prev = null;

        while (entry != null) {
            if (entry.key.equals(key)) {
                if (prev == null) {
                    table[index] = entry.next;
                } else {
                    prev.next = entry.next;
                }
                size--;
                return entry.value;
            }
            prev = entry;
            entry = entry.next;
        }
        return null;
    }

    private int getIndex(K key) {
        int hashCode = key == null ? 0 : key.hashCode();
        return (hashCode & 0x7FFFFFFF) % table.length;
    }

    @SuppressWarnings("unchecked")
    private void resize() {
        Entry<K, V>[] oldTable = table;
        table = new Entry[oldTable.length * 2];
        threshold = (int) (table.length * LOAD_FACTOR);
        size = 0;

        for (Entry<K, V> entry : oldTable) {
            while (entry != null) {
                put(entry.key, entry.value);
                entry = entry.next;
            }
        }
    }

    private static class Entry<K, V> {
        final K key;
        V value;
        Entry<K, V> next;

        Entry(K key, V value, Entry<K, V> next) {
            this.key = key;
            this.value = value;
            this.next = next;
        }
    }
}
```

## 五、常见算法问题

### 1. 两数之和

```java
public class TwoSum {
    // 给定一个整数数组 nums 和一个目标值 target
    // 返回两个数的索引，使它们相加等于 target

    // 暴力解法 O(n²)
    public static int[] twoSumBrute(int[] nums, int target) {
        for (int i = 0; i < nums.length; i++) {
            for (int j = i + 1; j < nums.length; j++) {
                if (nums[i] + nums[j] == target) {
                    return new int[]{i, j};
                }
            }
        }
        return new int[]{-1, -1};
    }

    // 哈希表解法 O(n)
    public static int[] twoSumHash(int[] nums, int target) {
        Map<Integer, Integer> map = new HashMap<>();
        for (int i = 0; i < nums.length; i++) {
            int complement = target - nums[i];
            if (map.containsKey(complement)) {
                return new int[]{map.get(complement), i};
            }
            map.put(nums[i], i);
        }
        return new int[]{-1, -1};
    }
}
```

### 2. 最长公共子序列

```java
public class LongestCommonSubsequence {
    // 返回两个字符串的最长公共子序列长度
    public static int lcs(String text1, String text2) {
        int m = text1.length();
        int n = text2.length();
        int[][] dp = new int[m + 1][n + 1];

        for (int i = 1; i <= m; i++) {
            for (int j = 1; j <= n; j++) {
                if (text1.charAt(i - 1) == text2.charAt(j - 1)) {
                    dp[i][j] = dp[i - 1][j - 1] + 1;
                } else {
                    dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);
                }
            }
        }
        return dp[m][n];
    }

    // 时间复杂度：O(m*n)
    // 空间复杂度：O(m*n)
}
```

### 3. 动态规划问题

```java
// 斐波那契数列
public class Fibonacci {
    // 记忆化递归
    private static final Map<Integer, Integer> memo = new HashMap<>();

    public static int fibWithMemo(int n) {
        if (n <= 1) return n;
        if (memo.containsKey(n)) return memo.get(n);

        int result = fibWithMemo(n - 1) + fibWithMemo(n - 2);
        memo.put(n, result);
        return result;
    }

    // 动态规划（迭代）
    public static int fibDP(int n) {
        if (n <= 1) return n;

        int[] dp = new int[n + 1];
        dp[0] = 0;
        dp[1] = 1;

        for (int i = 2; i <= n; i++) {
            dp[i] = dp[i - 1] + dp[i - 2];
        }
        return dp[n];
    }

    // 空间优化
    public static int fibOptimized(int n) {
        if (n <= 1) return n;

        int prev = 0, curr = 1;
        for (int i = 2; i <= n; i++) {
            int next = prev + curr;
            prev = curr;
            curr = next;
        }
        return curr;
    }
}

// 爬楼梯问题
public class ClimbStairs {
    // 每次可以爬 1 或 2 个台阶
    public static int climbStairs(int n) {
        if (n <= 2) return n;

        int[] dp = new int[n + 1];
        dp[1] = 1;
        dp[2] = 2;

        for (int i = 3; i <= n; i++) {
            dp[i] = dp[i - 1] + dp[i - 2];
        }
        return dp[n];
    }

    // 空间优化
    public static int climbStairsOptimized(int n) {
        if (n <= 2) return n;

        int prev = 1, curr = 2;
        for (int i = 3; i <= n; i++) {
            int next = prev + curr;
            prev = curr;
            curr = next;
        }
        return curr;
    }
}
```

### 4. 回溯算法

```java
// 全排列
public class Permutations {
    public static List<List<Integer>> permute(int[] nums) {
        List<List<Integer>> result = new ArrayList<>();
        backtrack(result, new ArrayList<>(), nums);
        return result;
    }

    private static void backtrack(List<List<Integer>> result,
                                    List<Integer> tempList,
                                    int[] nums) {
        if (tempList.size() == nums.length) {
            result.add(new ArrayList<>(tempList));
            return;
        }

        for (int i = 0; i < nums.length; i++) {
            if (tempList.contains(nums[i])) continue;

            tempList.add(nums[i]);
            backtrack(result, tempList, nums);
            tempList.remove(tempList.size() - 1);
        }
    }
}

// N 皇后问题
public class NQueens {
    public static List<List<String>> solveNQueens(int n) {
        List<List<String>> result = new ArrayList<>();
        char[][] board = new char[n][n];

        for (int i = 0; i < n; i++) {
            Arrays.fill(board[i], '.');
        }

        solve(result, board, 0);
        return result;
    }

    private static void solve(List<List<String>> result,
                             char[][] board,
                             int row) {
        if (row == board.length) {
            result.add(construct(board));
            return;
        }

        for (int col = 0; col < board.length; col++) {
            if (isValid(board, row, col)) {
                board[row][col] = 'Q';
                solve(result, board, row + 1);
                board[row][col] = '.';
            }
        }
    }

    private static boolean isValid(char[][] board, int row, int col) {
        int n = board.length;

        // 检查列
        for (int i = 0; i < row; i++) {
            if (board[i][col] == 'Q') return false;
        }

        // 检查对角线
        for (int i = 1; i <= row; i++) {
            // 左上对角线
            if (col - i >= 0 && board[row - i][col - i] == 'Q') {
                return false;
            }
            // 右上对角线
            if (col + i < n && board[row - i][col + i] == 'Q') {
                return false;
            }
        }

        return true;
    }

    private static List<String> construct(char[][] board) {
        List<String> result = new ArrayList<>();
        for (char[] row : board) {
            result.add(new String(row));
        }
        return result;
    }
}
```

## 六、面试高频题

### 1. 反转链表

```java
public class ReverseList {
    // 迭代反转
    public static ListNode reverse(ListNode head) {
        ListNode prev = null;
        ListNode current = head;

        while (current != null) {
            ListNode next = current.next;
            current.next = prev;
            prev = current;
            current = next;
        }
        return prev;
    }

    // 递归反转
    public static ListNode reverseRecursive(ListNode head) {
        if (head == null || head.next == null) {
            return head;
        }

        ListNode newHead = reverseRecursive(head.next);
        head.next.next = head;
        head.next = null;
        return newHead;
    }

    static class ListNode {
        int val;
        ListNode next;

        ListNode(int val) {
            this.val = val;
        }
    }
}
```

### 2. 判断链表是否有环

```java
public class LinkedListCycle {
    public static boolean hasCycle(ListNode head) {
        if (head == null || head.next == null) {
            return false;
        }

        ListNode slow = head;
        ListNode fast = head;

        while (fast != null && fast.next != null) {
            slow = slow.next;
            fast = fast.next.next;
            if (slow == fast) {
                return true;
            }
        }
        return false;
    }

    // 找到环的起始点
    public static ListNode detectCycle(ListNode head) {
        if (head == null || head.next == null) {
            return null;
        }

        ListNode slow = head, fast = head;

        while (fast != null && fast.next != null) {
            slow = slow.next;
            fast = fast.next.next;
            if (slow == fast) {
                // 有环，找环的起点
                slow = head;
                while (slow != fast) {
                    slow = slow.next;
                    fast = fast.next;
                }
                return slow;
            }
        }
        return null;
    }
}
```

### 3. 数组去重

```java
public class RemoveDuplicates {
    // 有序数组去重
    public static int removeDuplicates(int[] nums) {
        if (nums.length == 0) return 0;

        int slow = 1;  // 慢指针指向不重复的位置

        for (int fast = 1; fast < nums.length; fast++) {
            if (nums[fast] != nums[fast - 1]) {
                nums[slow++] = nums[fast];
            }
        }
        return slow;
    }

    // 无序数组去重
    public static int[] removeDuplicatesUnordered(int[] nums) {
        Set<Integer> set = new LinkedHashSet<>();
        for (int num : nums) {
            set.add(num);
        }
        return set.stream().mapToInt(Integer::intValue).toArray();
    }
}
```

### 4. 寻找数组中的重复数字

```java
public class FindDuplicate {
    // 数组范围 1-n，其中有一个重复数字
    public static int findDuplicate(int[] nums) {
        int slow = 0, fast = 0;

        // 第一阶段：找到相遇点
        do {
            slow = nums[slow];
            fast = nums[nums[fast]];
        } while (slow != fast);

        // 第二阶段：找到入口
        slow = 0;
        while (slow != fast) {
            slow = nums[slow];
            fast = nums[fast];
        }
        return slow;
    }
}
```

## 小结

本节学习了算法与数据结构：

- **复杂度分析** - 时间复杂度、空间复杂度
- **排序算法** - 冒泡、选择、插入、快排、归并、堆排
- **查找算法** - 二分查找及其变种
- **数据结构** - 数组、链表、栈、队列、树、哈希表
- **常见算法** - 动态规划、回溯、贪心、分治
- **面试高频题** - 反转链表、判断环、去重、重复数字

## 实践练习

### 编程题
1. 手动实现一个 LRU 缓存（不能使用 LinkedHashMap），使用 HashMap + 双向链表，支持 O(1) 的 get 和 put 操作。
2. 实现一个简单的路由匹配算法：支持 `/users/:id/posts/:postId` 这样的路径参数匹配，返回匹配到的参数 Map。

### 思考题
1. 快速排序在什么情况下会退化为 O(n²)？如何避免？
2. 哈希表解决冲突的方法有哪些？拉链法和开放寻址法各有什么优缺点？

### 自测题
1. 快排、归并、堆排的时间复杂度和空间复杂度分别是多少？
2. 二分查找的前提条件是什么？
3. 什么是动态规划？它和分治算法有什么区别？

下一步将学习 Java Web 基础（→ `javaweb/beginner/01-servlet-jsp.md`）。