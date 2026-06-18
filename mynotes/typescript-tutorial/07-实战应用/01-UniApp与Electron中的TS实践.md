# 01 - UniApp 和 Electron 项目中的 TypeScript 实践

---

## 一、UniApp + Vue3 + TypeScript 实战

### 1. 项目类型声明文件

```typescript
// types/global.d.ts
// 全局类型声明文件，不需要 import 就能用

declare module "vue" {
  interface ComponentCustomProperties {
    // 挂载到 Vue 实例上的全局属性
    $utils: typeof import("@/utils/common")
  }
}

// 声明 uni 对象的类型
declare interface Uni {
  // uni.request 等 API 的类型在 @dcloudio/uni-app 中已经定义
  // 这里可以扩展自定义的
  $showLoading: (title?: string) => void
}

// 声明静态资源导入
declare module "*.png" {
  const src: string
  export default src
}

declare module "*.jpg" {
  const src: string
  export default src
}
```

### 2. 完整的 API 层（带类型）

```typescript
// types/api.ts

// ── 通用响应 ──
export interface ApiResponse<T = unknown> {
  code: number
  data: T
  message: string
}

// ── 用户 ──
export interface User {
  id: number
  name: string
  avatar?: string
  phone?: string
  email?: string
  isVIP: boolean
  createdAt: string
}

export interface LoginRequest {
  phone: string
  password: string
}

export interface LoginResponse {
  token: string
  user: User
}

// ── 商品 ──
export interface Goods {
  id: number
  name: string
  price: number
  originalPrice?: number
  cover: string
  images?: string[]
  description: string
  stock: number
  category: string
  tags: string[]
  sales: number
}

export interface GoodsListRequest {
  page: number
  size: number
  keyword?: string
  category?: string
  sortBy?: "price_asc" | "price_desc" | "sales" | "new"
}

export interface GoodsListResponse {
  list: Goods[]
  total: number
  page: number
  size: number
}

// ── 订单 ──
export type OrderStatus = "pending" | "paid" | "shipped" | "completed" | "cancelled"

export interface OrderItem {
  goodsId: number
  goodsName: string
  goodsCover: string
  price: number
  quantity: number
}

export interface Order {
  id: string
  status: OrderStatus
  items: OrderItem[]
  totalAmount: number
  address: Address
  createdAt: string
  paidAt?: string
}

export interface Address {
  name: string
  phone: string
  province: string
  city: string
  district: string
  detail: string
}
```

```typescript
// api/request.ts
import { ApiResponse } from "@/types/api"

const BASE_URL = import.meta.env.VITE_API_URL

interface RequestOptions {
  url: string
  method?: "GET" | "POST" | "PUT" | "DELETE"
  data?: Record<string, unknown>
  params?: Record<string, unknown>
  loading?: boolean
}

async function request<T>(options: RequestOptions): Promise<T> {
  if (options.loading !== false) {
    uni.showLoading({ title: "加载中..." })
  }

  const token = uni.getStorageSync<string>("token")

  return new Promise((resolve, reject) => {
    uni.request({
      url: `${BASE_URL}${options.url}`,
      method: options.method || "GET",
      data: options.data,
      header: {
        "Content-Type": "application/json",
        Authorization: token ? `Bearer ${token}` : ""
      },
      success: (res) => {
        uni.hideLoading()
        const data = res.data as ApiResponse<T>

        if (data.code === 200) {
          resolve(data.data)
        } else if (data.code === 401) {
          uni.removeStorageSync("token")
          uni.navigateTo({ url: "/pages/login/login" })
          reject(new Error(data.message))
        } else {
          uni.showToast({ title: data.message, icon: "none" })
          reject(new Error(data.message))
        }
      },
      fail: (err) => {
        uni.hideLoading()
        uni.showToast({ title: "网络错误", icon: "none" })
        reject(err)
      }
    })
  })
}

export default request
```

```typescript
// api/user.ts
import request from "./request"
import { LoginRequest, LoginResponse, User, ApiResponse } from "@/types/api"

export const userApi = {
  login: (data: LoginRequest) =
003e
    request<LoginResponse>({ url: "/api/user/login", method: "POST", data }),

  getUserInfo: () =>
    request<User>({ url: "/api/user/info" }),

  updateUserInfo: (data: Partial<User>) =>
    request<User>({ url: "/api/user/info", method: "PUT", data }),

  uploadAvatar: (filePath: string) => {
    return new Promise<{ url: string }>((resolve, reject) => {
      uni.uploadFile({
        url: `${import.meta.env.VITE_API_URL}/api/user/avatar`,
        filePath,
        name: "file",
        success: (res) => {
          const data = JSON.parse(res.data) as ApiResponse<{ url: string }>
          resolve(data.data)
        },
        fail: reject
      })
    })
  }
}
```

### 3. Pinia Store（带类型）

```typescript
// stores/user.ts
import { defineStore } from "pinia"
import { ref, computed } from "vue"
import { User } from "@/types/api"
import { userApi } from "@/api/user"

export const useUserStore = defineStore("user", () => {
  // State
  const token = ref<string>(uni.getStorageSync("token") || "")
  const userInfo = ref<User | null>(null)

  // Getters
  const isLogin = computed<boolean>(() => !!token.value)
  const displayName = computed<string>(() => userInfo.value?.name || "游客")
  const avatar = computed<string | undefined>(() => userInfo.value?.avatar)

  // Actions
  const setToken = (val: string): void => {
    token.value = val
    uni.setStorageSync("token", val)
  }

  const fetchUserInfo = async (): Promise<void> => {
    try {
      const data = await userApi.getUserInfo()
      userInfo.value = data
    } catch {
      userInfo.value = null
    }
  }

  const logout = (): void => {
    token.value = ""
    userInfo.value = null
    uni.removeStorageSync("token")
    uni.removeStorageSync("userInfo")
  }

  return {
    token,
    userInfo,
    isLogin,
    displayName,
    avatar,
    setToken,
    fetchUserInfo,
    logout
  }
})
```

### 4. 页面组件（完整类型示例）

```vue
<!-- pages/goods-list/goods-list.vue -->
<script setup lang="ts">
import { ref, onLoad, onReachBottom, onPullDownRefresh } from "@dcloudio/uni-app"
import { useUserStore } from "@/stores/user"
import { goodsApi } from "@/api/goods"
import { Goods, GoodsListRequest, GoodsListResponse } from "@/types/api"

// ── 类型定义 ──
interface ListState {
  page: number
  size: number
  total: number
  loading: boolean
  finished: boolean
  keyword: string
  category: string
}

// ── 响应式状态 ──
const userStore = useUserStore()
const goodsList = ref<Goods[]>([])
const state = ref<ListState>({
  page: 1,
  size: 10,
  total: 0,
  loading: false,
  finished: false,
  keyword: "",
  category: ""
})

// ── 方法 ──
const fetchGoodsList = async (isRefresh: boolean = false): Promise<void> => {
  if (state.value.loading) return
  if (state.value.finished && !isRefresh) return

  state.value.loading = true

  try {
    const params: GoodsListRequest = {
      page: isRefresh ? 1 : state.value.page,
      size: state.value.size,
      keyword: state.value.keyword || undefined,
      category: state.value.category || undefined
    }

    const res: GoodsListResponse = await goodsApi.getList(params)

    if (isRefresh) {
      goodsList.value = res.list
      state.value.page = 2
      state.value.finished = false
      uni.stopPullDownRefresh()
    } else {
      goodsList.value.push(...res.list)
      state.value.page++
    }

    state.value.total = res.total

    if (goodsList.value.length >= res.total) {
      state.value.finished = true
    }
  } catch (err) {
    console.error("加载商品列表失败:", err)
  } finally {
    state.value.loading = false
  }
}

const onSearch = (keyword: string): void => {
  state.value.keyword = keyword
  fetchGoodsList(true)
}

const goDetail = (goodsId: number): void => {
  uni.navigateTo({
    url: `/pages/goods-detail/goods-detail?id=${goodsId}`
  })
}

// ── 生命周期 ──
onLoad((options: Record<string, string>) => {
  if (options.category) {
    state.value.category = options.category
  }
  fetchGoodsList(true)
})

onReachBottom(() => fetchGoodsList(false))
onPullDownRefresh(() => fetchGoodsList(true))
</script>

<template>
  <view class="goods-list">
    <search-bar @search="onSearch" />

    <scroll-view scroll-y class="list">
      <goods-card
        v-for="goods in goodsList"
        :key="goods.id"
        :goods="goods"
        @click="goDetail(goods.id)"
      />

      <view v-if="state.loading" class="loading">加载中...</view>
      <view v-if="state.finished" class="finished">没有更多了</view>
    </scroll-view>
  </view>
</template>
```

---

## 二、Electron + Vue3 + TypeScript 实战

### 1. 主进程类型定义

```typescript
// electron/types.ts

// IPC 通信通道定义（避免魔法字符串）
export const IPC_CHANNELS = {
  WINDOW: {
    MINIMIZE: "window:minimize",
    MAXIMIZE: "window:maximize",
    CLOSE: "window:close",
    RESIZE: "window:resize"
  },
  FILE: {
    READ: "file:read",
    WRITE: "file:write",
    SELECT: "file:select",
    WATCH: "file:watch"
  },
  APP: {
    GET_VERSION: "app:get-version",
    GET_PATH: "app:get-path",
    CHECK_UPDATE: "app:check-update"
  },
  STORE: {
    GET: "store:get",
    SET: "store:set",
    DELETE: "store:delete"
  }
} as const

// 窗口控制参数
export interface WindowControlPayload {
  action: "minimize" | "maximize" | "unmaximize" | "close"
}

// 文件操作参数
export interface FileReadPayload {
  filePath: string
  encoding?: BufferEncoding
}

export interface FileWritePayload {
  filePath: string
  content: string
}

// 存储操作参数
export interface StoreSetPayload {
  key: string
  value: unknown
}
```

### 2. 预加载脚本（类型安全的 IPC）

```typescript
// electron/preload.ts
import { contextBridge, ipcRenderer } from "electron"
import { IPC_CHANNELS } from "./types"

// 类型安全的 API 暴露
const electronAPI = {
  // 窗口控制
  window: {
    minimize: () => ipcRenderer.send(IPC_CHANNELS.WINDOW.MINIMIZE),
    maximize: () => ipcRenderer.send(IPC_CHANNELS.WINDOW.MAXIMIZE),
    close: () => ipcRenderer.send(IPC_CHANNELS.WINDOW.CLOSE),
    onMaximizeChange: (callback: (isMaximized: boolean) => void) => {
      const handler = (_: unknown, isMaximized: boolean) => callback(isMaximized)
      ipcRenderer.on(IPC_CHANNELS.WINDOW.RESIZE, handler)
      return () => ipcRenderer.removeListener(IPC_CHANNELS.WINDOW.RESIZE, handler)
    }
  },

  // 文件操作
  file: {
    read: (filePath: string) =>
      ipcRenderer.invoke(IPC_CHANNELS.FILE.READ, { filePath }),
    write: (filePath: string, content: string) =>
      ipcRenderer.invoke(IPC_CHANNELS.FILE.WRITE, { filePath, content }),
    select: (options?: { filters?: Electron.FileFilter[] }) =>
      ipcRenderer.invoke(IPC_CHANNELS.FILE.SELECT, options)
  },

  // 存储
  store: {
    get: <T = unknown>(key: string): Promise<T | undefined> =>
      ipcRenderer.invoke(IPC_CHANNELS.STORE.GET, key),
    set: <T>(key: string, value: T): Promise<void> =>
      ipcRenderer.invoke(IPC_CHANNELS.STORE.SET, { key, value }),
    delete: (key: string): Promise<void> =>
      ipcRenderer.invoke(IPC_CHANNELS.STORE.DELETE, key)
  },

  // 应用信息
  app: {
    getVersion: (): Promise<string> =>
      ipcRenderer.invoke(IPC_CHANNELS.APP.GET_VERSION),
    getPath: (name: "home" | "appData" | "userData" | "temp" | "desktop"): Promise<string> =>
      ipcRenderer.invoke(IPC_CHANNELS.APP.GET_PATH, name),
    checkUpdate: (): Promise<{ hasUpdate: boolean; version?: string }> =>
      ipcRenderer.invoke(IPC_CHANNELS.APP.CHECK_UPDATE)
  }
}

contextBridge.exposeInMainWorld("electronAPI", electronAPI)

// 声明全局类型
declare global {
  interface Window {
    electronAPI: typeof electronAPI
  }
}
```

### 3. 前端组合式函数（类型安全）

```typescript
// src/composables/useElectron.ts
import { ref, onMounted, onUnmounted } from "vue"

export function useElectron() {
  const isElectron = ref(false)
  const isMaximized = ref(false)

  onMounted(() => {
    isElectron.value = !!window.electronAPI

    if (window.electronAPI?.window?.onMaximizeChange) {
      const unsubscribe = window.electronAPI.window.onMaximizeChange(
        (maximized: boolean) => {
          isMaximized.value = maximized
        }
      )

      onUnmounted(() => {
        unsubscribe?.()
      })
    }
  })

  const minimize = () => window.electronAPI?.window?.minimize()
  const maximize = () => window.electronAPI?.window?.maximize()
  const close = () => window.electronAPI?.window?.close()

  return {
    isElectron,
    isMaximized,
    minimize,
    maximize,
    close
  }
}

// src/composables/useStore.ts
export function useStore() {
  const get = async <T>(key: string): Promise<T | undefined> => {
    if (window.electronAPI?.store) {
      return window.electronAPI.store.get<T>(key)
    }
    // H5 环境降级到 localStorage
    const value = localStorage.getItem(key)
    return value ? (JSON.parse(value) as T) : undefined
  }

  const set = async <T>(key: string, value: T): Promise<void> => {
    if (window.electronAPI?.store) {
      await window.electronAPI.store.set(key, value)
    } else {
      localStorage.setItem(key, JSON.stringify(value))
    }
  }

  return { get, set }
}
```

### 4. 类型声明文件

```typescript
// src/types/electron.d.ts
// 如果不用 preload 暴露，需要声明 electron 模块

/// <reference types="electron">

declare module "electron" {
  export interface IpcRenderer {
    send(channel: string, ...args: unknown[]): void
    invoke(channel: string, ...args: unknown[]): Promise<unknown>
    on(channel: string, listener: (...args: unknown[]) => void): void
    removeListener(channel: string, listener: (...args: unknown[]) => void): void
  }
}

// 声明环境变量
interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_WS_URL: string
  readonly VITE_APP_NAME: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
```

---

## 三、TypeScript 最佳实践清单

```
✅ 1. 开启 strict: true（tsconfig.json）
   这是 TS 的灵魂，关闭等于白用

✅ 2. 避免 any
   用 unknown 代替不确定的类型
   用泛型代替需要兼容多种类型的场景

✅ 3. 优先用 interface 定义对象结构
   需要联合/交叉类型时用 type

✅ 4. 函数返回值尽量显式标注
   特别是异步函数 Promise<T>

✅ 5. 给 API 响应定义类型
   前后端协作的基础

✅ 6. 利用类型推断减少冗余
   不需要每个变量都写类型

✅ 7. 用工具类型减少重复定义
   Pick, Omit, Partial 等

✅ 8. 用常量代替魔法字符串
   IPC 通道名、状态值等

✅ 9. 为第三方库补充类型声明
   没有 @types/xxx 时自己写 .d.ts

✅ 10. 类型和运行时都要校验
   TS 只在编译时检查，运行时数据仍需验证
```
