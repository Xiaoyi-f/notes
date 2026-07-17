// npm install typescrit -g
// tsc --init 生成tsconfig.json文件 "target": "ES6"
// tsconfig.json 中添加 "include": ["pathTSFile"] 执行 tsc 自动按照配置文件编译
// 或者删除tsconfig.json文件,使用 tsc 指定ts文件 编译 tsc --watch 会自动监视编译
// 使用 : 类型声明 
let type: any = "any type" // 不进行类型声明即隐式any 可以任意赋值,破坏其他声明
const unknownNow: unknown = "unknown type"
// 使用断言 
type = unknownNow as any 
(unknownNow as any).xxx 

function neverOver(): never {
  throw new Error("never")
}

// void 可以接受 return undefined
function voidReturn(): void {
  console.log(new Error("never"))
}

// object(对象类型) 与 Object(除null/undefined外)
// variableData? 字面量类型常用 表示有何不有都可 
let func: (arg: number) => number
func = function (arg) { return arg }

let arr1: number[]
let arr2: Array<number>

// 固定数量/类型且支持可选? 元组类型 
let tuple: [number, string, boolean?]
let moreTuple: [number, ...string[]]

// 一组一组相关值放到枚举,更快、防止写错
// 默认为数字枚举且从零开始(有方向映射)、字符串枚举(自定义值为字符串,没有反向映射) 
enum Color { Red, Green, Blue }
Color[0] // Red

// 别名与联合
type Name = string | number 

// 交叉 
type Address = {
  num: number,
  cell: number,
  room: string
}

type Area = {
  height: number,
  width: number 
}

type House = Address & Area 

class People {
  constructor(protected name: string) {
    this.name = name 
  }

  public sayHello() {
    console.log('hello')
  }
}

class Student extends People {
  constructor(protected name: string,
    public grade: string, private readonly idCard: string) {
    super(name)
    this.grade = grade 
    this.idCard = idCard 
  }

  public override sayHello() {
    console.log(`Hello, my name is ${this.name} and I'm in grade ${this.grade}`)
  }
}

// public 修饰符 类外部、内部、子类都能够使用 可以省略不写
// protected 修饰符 类内部和子类能够使用
// private 修饰符 只有类内部能够使用
// readonly 修饰符 设置只读属性

abstract class Abs {
  constructor(public name: string) { this.name = name }
  abstract sayHello(): void
  abs(): void {
    console.log('abs')
  }
}

class C extends Abs {
  constructor(public name: string) {
    super(name)
  }
  sayHello() {
    console.log('hello')
  }
}

// interface 有和并性与继承性 使用 implements 实现 多接口
// <> 泛型 定义时 使用时
// .d.ts文件 为现有的js代码提供类型信息 使得ts使用这些库或模块时也能类型检查和提示
// .d.ts文件 可以从官方库中找


/*
泛型的核心思想

```
function getFirst<T>(arr: T[]): T
            ↑                ↑      ↑
         类型参数          参数类型   返回类型

调用时：
getFirst<number>([1, 2, 3])
         ↑
      把 T 替换为 number

结果：
function getFirst(arr: number[]): number
```
*/

/*
泛型函数

### 1. 基本用法

  ```typescript
// 交换两个变量的值
function swap<T, U>(a: T, b: U): [U, T] {
  return [b, a]
}

const result = swap(1, "hello")
// result 的类型是 [string, number]
// result[0] 是 "hello"（string）
// result[1] 是 1（number）
```

### 2. 泛型约束（限制 T 的范围）

```typescript
// 问题：不是所有类型都有 length 属性
function getLength<T>(item: T): number {
  return item.length   // ❌ 错误：T 不一定有 length 属性
}

// 解决：用 extends 约束 T 必须有 length
interface HasLength {
  length: number
}

function getLength<T extends HasLength>(item: T): number {
  return item.length   // ✅ T 一定有 length
}

getLength("hello")        // ✅ string 有 length
getLength([1, 2, 3])      // ✅ 数组有 length
getLength({ length: 10 }) // ✅ 对象有 length
// getLength(123)         // ❌ number 没有 length
```

### 3. 泛型默认值

  ```typescript
// 如果不传泛型参数，默认用 string
function createArray<T = string>(length: number, value: T): T[] {
  return Array(length).fill(value)
}

const strArr = createArray(3, "x")       // 推断为 string[]
const numArr = createArray<number>(3, 0) // 显式指定 number[]
```
*/

/*
泛型接口

  ```typescript
// 通用的 API 响应接口
interface ApiResponse<T> {
  code: number
  data: T
  message: string
}

// 用户列表接口
interface User {
  id: number
  name: string
}

// 使用时指定 data 的类型
type UserListResponse = ApiResponse<User[]>

// 等价于：
// type UserListResponse = {
//   code: number
//   data: User[]
//   message: string
// }

// 实际使用
const response: UserListResponse = {
  code: 200,
  data: [
    { id: 1, name: "张三" },
    { id: 2, name: "李四" }
  ],
  message: "success"
}

// 也可以直接写
const response2: ApiResponse<{ token: string }> = {
  code: 200,
  data: { token: "abc123" },
  message: "登录成功"
}
```
*/

/*
泛型在 Vue3 + UniApp 中的实战

### 1. 通用的请求封装

  ```typescript
// utils/request.ts
import axios, { AxiosResponse } from 'axios'

// 后端统一返回格式
interface ApiResult<T> {
  code: number
  data: T
  message: string
}

// 封装请求函数，用泛型指定返回数据的类型
async function request<T>(config: {
  url: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: unknown
  params?: Record<string, unknown>
}): Promise<T> {
  const response: AxiosResponse<ApiResult<T>> = await axios({
    baseURL: 'https://api.yoursite.com',
    ...config
  })

  if (response.data.code !== 200) {
    throw new Error(response.data.message)
  }

  return response.data.data
}

// ── 使用 ──

interface User {
  id: number
  name: string
  email: string
}

// 获取用户详情：自动推断返回 User 类型
const user = await request<User>({
  url: '/api/users/1'
})
// user 的类型是 User
console.log(user.name)   // ✅ 有代码提示

// 获取用户列表
const users = await request<User[]>({
  url: '/api/users'
})
// users 的类型是 User[]
users.forEach(u => console.log(u.name))  // ✅ 有代码提示

// 登录接口
interface LoginData {
  token: string
  user: User
}

const loginResult = await request<LoginData>({
  url: '/api/login',
  method: 'POST',
  data: { username: 'xxx', password: 'xxx' }
})
// loginResult.token 有提示
// loginResult.user.name 有提示
```

### 2. 通用的 useList 组合式函数

  ```typescript
// composables/useList.ts
import { ref, computed } from 'vue'

interface UseListOptions<T> {
  fetchFn: (params: { page: number; size: number }) => Promise<{
    list: T[]
    total: number
  }>
  pageSize?: number
}

interface UseListReturn<T> {
  list: Ref<T[]>
  loading: Ref<boolean>
  finished: Ref<boolean>
  total: Ref<number>
  loadMore: () => Promise<void>
  refresh: () => Promise<void>
}

export function useList<T>(options: UseListOptions<T>): UseListReturn<T> {
  const list = ref<T[]>([])
  const loading = ref(false)
  const finished = ref(false)
  const total = ref(0)
  const page = ref(1)
  const size = options.pageSize || 10

  const loadMore = async () => {
    if (loading.value || finished.value) return
    loading.value = true

    try {
      const res = await options.fetchFn({ page: page.value, size })
      list.value.push(...res.list)
      total.value = res.total
      page.value++

      if (list.value.length >= res.total) {
        finished.value = true
      }
    } finally {
      loading.value = false
    }
  }

  const refresh = async () => {
    page.value = 1
    list.value = []
    finished.value = false
    await loadMore()
  }

  return { list, loading, finished, total, loadMore, refresh }
}

// ── 使用 ──

interface Goods {
  id: number
  name: string
  price: number
}

const { list, loading, finished, loadMore, refresh } = useList<Goods>({
  fetchFn: goodsApi.getList,
  pageSize: 10
})

// list 的类型自动推断为 Ref<Goods[]>
// 遍历时有完整的 Goods 属性提示
```
*/

/*
泛型思维总结
遇到这些情况时，考虑用泛型：

1. 函数逻辑相同，但处理的数据类型不同
   → function xxx<T>(data: T): T

2. 数据结构相同，但内部元素类型不同
   → interface Response<T> { data: T }

3. 工具函数需要适配多种类型
   → function pick<T, K extends keyof T>(obj: T, keys: K[]): Pick<T, K>

泛型的本质：把"类型"也变成"参数"，延迟到使用时再确定。
*/
