# 01 - interface（接口）与 type（类型别名）

> 这是 TypeScript 最重要的概念。它们用来描述"对象长什么样"。

---

## 一、为什么需要接口？

```javascript
// JavaScript：定义用户对象
const user1 = { name: "张三", age: 25 }
const user2 = { name: "李四", age: 30 }
// 问题：这两个对象结构一样，但代码里看不出来
// 如果 user3 写成 { naem: "王五" }，JS 不会报错
```

```typescript
// TypeScript：用接口定义"对象的结构"
interface User {
  name: string    // 必须有 name 属性，类型是 string
  age: number     // 必须有 age 属性，类型是 number
}

const user1: User = { name: "张三", age: 25 }     // ✅
const user2: User = { name: "李四", age: 30 }     // ✅
const user3: User = { naem: "王五", age: 25 }     // ❌ 报错：不存在 "naem"，是否指 "name"?
const user4: User = { name: "赵六" }               // ❌ 报错：缺少 "age"
```

**接口的作用**：
1. 定义数据结构（像一份"合同"）
2. 编译时检查对象是否符合结构
3. IDE 提供代码提示

---

## 二、interface 详解

### 1. 基本用法

```typescript
interface User {
  id: number
  name: string
  email: string
}

// 使用接口
function greet(user: User): string {
  return `你好，${user.name}！你的邮箱是 ${user.email}`
}

greet({ id: 1, name: "张三", email: "zhangsan@example.com" })  // ✅
greet({ name: "李四" })  // ❌ 缺少 id 和 email
```

### 2. 可选属性（?）

```typescript
interface User {
  id: number
  name: string
  email: string
  phone?: string      // ? 表示可选：可能有，可能没有
  avatar?: string
}

const user1: User = {
  id: 1,
  name: "张三",
  email: "zhangsan@example.com"
  // phone 和 avatar 可以省略
}

const user2: User = {
  id: 2,
  name: "李四",
  email: "lisi@example.com",
  phone: "13800138000"   // 也可以加上
}
```

### 3. 只读属性（readonly）

```typescript
interface User {
  readonly id: number     // id 创建后不能修改
  name: string
  email: string
}

const user: User = { id: 1, name: "张三", email: "zs@example.com" }

user.name = "张三改名"     // ✅ name 可以改
user.id = 2               // ❌ 错误：id 是只读属性
```

**readonly 的应用场景**：

```typescript
// 配置项通常不应该被修改
interface AppConfig {
  readonly apiUrl: string
  readonly appName: string
  readonly version: string
}

const config: AppConfig = {
  apiUrl: "https://api.example.com",
  appName: "我的应用",
  version: "1.0.0"
}

// config.apiUrl = "xxx"   // ❌ 防止意外修改配置
```

### 4. 索引签名（动态属性）

```typescript
// 场景：对象有不确定数量的属性，但属性值类型相同
interface ScoreSheet {
  [subject: string]: number   // 任意 string 类型的属性，值都是 number
}

const scores: ScoreSheet = {
  math: 90,
  english: 85,
  chinese: 88,
  physics: 92     // 可以随便加属性
}

// 另一个场景：缓存对象
interface Cache {
  [key: string]: any   // 任意属性名，值类型不限
}

const cache: Cache = {}
cache["user:1"] = { name: "张三" }
cache["settings"] = { theme: "dark" }
```

### 5. 接口继承（extends）

```typescript
interface Person {
  name: string
  age: number
}

// Employee 继承了 Person 的所有属性，再加上自己的
interface Employee extends Person {
  company: string
  salary: number
}

const emp: Employee = {
  name: "张三",       // 来自 Person
  age: 28,           // 来自 Person
  company: "科技公司", // 自己的
  salary: 15000      // 自己的
}

// 也可以多重继承
interface Manager extends Employee {
  teamSize: number
}
```

### 6. 接口可以重复定义（声明合并）

```typescript
// TypeScript 独有的特性：同名接口会自动合并
interface User {
  name: string
}

interface User {
  age: number
}

// 实际效果等同于：
// interface User {
//   name: string
//   age: number
// }

const user: User = { name: "张三", age: 25 }  // ✅
```

**应用场景**：第三方库扩展。

```typescript
// 比如 Vue3 的组件实例类型扩展
declare module "vue" {
  interface ComponentCustomProperties {
    $myUtil: MyUtilType
  }
}
```

---

## 三、type（类型别名）详解

### 1. 基本用法

```typescript
// type 给一个类型起别名
type UserID = number
type UserName = string

type User = {
  id: UserID
  name: UserName
  email: string
}

const user: User = { id: 1, name: "张三", email: "zs@example.com" }
```

### 2. type 可以做什么 interface 做不到的事

```typescript
// 1. 联合类型（interface 不支持）
type Status = "pending" | "success" | "failed"
type ID = string | number

let status: Status = "pending"     // ✅
status = "success"                 // ✅
status = "done"                    // ❌ 只能是那三个值之一

// 2. 交叉类型
type Person = { name: string }
type Employee = Person & { company: string }   // 合并两个类型

const emp: Employee = { name: "张三", company: "ABC" }

// 3. 基本类型的别名
type StringOrNumber = string | number

// 4. 元组类型
type Point = [number, number]

// 5. 条件类型
type IsString<T> = T extends string ? true : false
```

---

## 四、interface vs type 选哪个？

| 特性 | interface | type |
|------|-----------|------|
| 描述对象结构 | ✅ | ✅ |
| 可重复定义（声明合并） | ✅ | ❌ |
| 联合类型 | ❌ | ✅ |
| 交叉类型 | 用 extends | 用 & |
| 基本类型别名 | ❌ | ✅ |
| 描述函数 | ✅ | ✅ |

**简单规则**：
- 描述对象结构（类、组件 props）→ 用 `interface`
- 需要联合类型、交叉类型、给基本类型起别名 → 用 `type`
- 不确定时 → 用 `interface`（更常用，更直观）

```typescript
// 推荐用法示例

// 对象结构 → interface
interface User {
  id: number
  name: string
}

interface ApiResponse<T> {
  code: number
  data: T
  message: string
}

// 联合类型 → type
type Status = "loading" | "success" | "error"
type Theme = "light" | "dark" | "auto"

// 复杂类型组合 → type
type UserOrNull = User | null
type AdminUser = User & { permissions: string[] }

// 函数类型 → 两种都可以
interface GreetFn {
  (name: string): string
}

type GreetFn2 = (name: string) => string
```

---

## 五、实战：定义 API 接口类型

```typescript
// types/api.ts

// ── 用户相关 ──
export interface User {
  id: number
  name: string
  email: string
  avatar?: string
  phone?: string
  createdAt: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  token: string
  user: User
}

// ── 商品相关 ──
export interface Goods {
  id: number
  name: string
  price: number
  originalPrice?: number
  cover: string
  description?: string
  stock: number
  category: string
  tags?: string[]
}

export interface GoodsListRequest {
  page: number
  size: number
  keyword?: string
  category?: string
  sortBy?: "price" | "sales" | "new"
}

export interface GoodsListResponse {
  list: Goods[]
  total: number
  page: number
  size: number
}

// ── 通用响应 ──
export interface ApiResponse<T = unknown> {
  code: number
  data: T
  message: string
}

export type ApiError = {
  code: number
  message: string
  details?: Record<string, string[]>
}
```

---

## 六、接口的鸭子类型（Duck Typing）

TypeScript 的接口检查不看对象"是什么"，只看对象"有什么"。

```typescript
interface Point {
  x: number
  y: number
}

function printPoint(p: Point) {
  console.log(`(${p.x}, ${p.y})`)
}

// 只要是 "有 x 和 y 两个 number 属性的对象" 都可以传
const point1: Point = { x: 10, y: 20 }
printPoint(point1)  // ✅

const point2 = { x: 30, y: 40, z: 50 }  // 多了一个 z
printPoint(point2)  // ✅ 也可以！因为至少有 x 和 y

const point3 = { x: 60 }  // 缺少 y
printPoint(point3)  // ❌ 报错：缺少 y
```

**好处**：灵活性高，只要结构匹配就能用。

**注意点**：多余属性的检查。

```typescript
// 直接字面量赋值时，会有" excess property check（多余属性检查）"
const p: Point = { x: 10, y: 20, z: 30 }  // ❌ 报错：对象字面量不能指定未定义的属性

// 但通过变量传入就不会检查
const obj = { x: 10, y: 20, z: 30 }
const p2: Point = obj  // ✅ 可以
```
