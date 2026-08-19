# uni-app 全栈精通指南

> 从原理到实战，覆盖 H5 / Android / iOS / 小程序四端，达到大厂高级前端水平。

---

## 第一章：uni-app 核心原理

### 1.1 架构总览

uni-app 是一套**编译时 + 运行时**结合的跨端框架。核心思路：**写一套 Vue 代码，编译成各端原生代码**。

```
源码 (Vue3 + uni API)
        │
        ▼  uni-app 编译器 (vite 插件)
        │
  ┌─────┼─────┬─────────┬──────────┐
  ▼     ▼     ▼         ▼          ▼
 H5   Android  iOS    微信小程序  其他小程序
```

**编译时做的事**：
- 条件编译 (`#ifdef` / `#ifndef`) 剪掉不用的平台代码
- `pages.json` → 各端的路由/页面配置
- `manifest.json` → 各端的应用级配置 (AndroidManifest, iOS plist, app.json 等)
- `.vue` 单文件 → H5 用标准 Vue 组件，小程序用自定义组件格式

**运行时做的事**：
- `uni.xxx` API 屏蔽各端底层差异，统一调用
- WebView 桥接层处理 JS ↔ Native 通信
- 小程序运行时适配 (setData、WXS 等)

### 1.2 四端渲染原理对比

| 层级 | H5 | Android | iOS | 微信小程序 |
|------|-----|---------|-----|-----------|
| UI 渲染 | DOM / CSS | WebView (系统内核) | WKWebView | WebView (微信定制) |
| JS 引擎 | V8 (浏览器) | V8 (WebView内) | JavaScriptCore | V8 (微信定制) |
| 原生能力 | 浏览器 API | JS → Native Bridge | JS → Native Bridge | wx.xxx API |
| 包体积 | 无限制 | APK ~10MB+ | IPA ~15MB+ | 2MB 限制 (分包20MB) |
| 热更新 | 直接部署 | 需自己实现 | AppStore审核 | 微信审核 |
| 调试 | Chrome DevTools | Chrome Inspect / uni调试 | Safari Web Inspector | 微信开发者工具 |

### 1.3 条件编译：最核心的跨端技巧

```javascript
// 只会出现在对应平台编译产物中的代码
// #ifdef H5
console.log('这段代码只在 H5 中存在')
// #endif

// #ifdef APP-PLUS
console.log('这段代码只在 App (Android/iOS) 中存在')
// #endif

// #ifdef MP-WEIXIN
console.log('这段代码只在微信小程序中存在')
// #endif

// #ifndef H5
console.log('所有非 H5 平台都有这段代码')
// #endif

// 可以嵌套
// #ifdef APP-PLUS
  // #ifdef ANDROID
  console.log('只在 Android 上')
  // #endif
  // #ifdef IOS
  console.log('只在 iOS 上')
  // #endif
// #endif
```

**条件编译支持的场景**：
- `.js` / `.ts` 文件 ✓
- `.vue` 的 `<template>` ✓ 
- `.vue` 的 `<style>` ✓
- `.vue` 的 `<script>` ✓
- `.json` 文件 ✓
- `.css` / `.scss` 文件 ✓

**关键坑点**：
- 条件编译是**编译时**剪枝，不是运行时判断
- H5 开发时所有 `#ifdef` 块都会被保留（因为编译器不知道目标平台），只有在 `build` 时才剪掉
- `pages.json` 里的 `style` 可以用条件编译，但 `path` 不可以

---

## 第二章：项目配置完全解析

### 2.1 pages.json — 路由和页面配置

```json
{
  "pages": [
    {
      "path": "pages/home/index",
      "style": {
        "navigationBarTitleText": "首页",
        "navigationBarBackgroundColor": "#fff",
        "navigationBarTextStyle": "black",   // black / white
        "navigationStyle": "custom",          // default / custom (自定义导航栏)
        "enablePullDownRefresh": false,
        "backgroundColor": "#f5f5f5"         // 下拉刷新背景色
      }
    }
  ],
  
  // ★ TabBar 配置 ★
  "tabBar": {
    "custom": true,     // true = 使用自定义 tabBar，不渲染原生 tabBar
    "color": "#999",    // 未选中文字颜色
    "selectedColor": "#43aa8b",  // 选中文字颜色
    "backgroundColor": "#fff",
    "borderStyle": "black",      // black / white
    "list": [
      { "pagePath": "pages/home/index", "text": "首页" }
    ]
  },

  // ★ 全局样式 ★
  "globalStyle": {
    "navigationBarTextStyle": "black",
    "navigationBarTitleText": "食愈",
    "backgroundColor": "#ffffff"
  },

  // ★ 自动路由守卫 (uni-id) ★
  "uniIdRouter": {}
}
```

**tabBar.custom: true 的关键行为**：
- H5：不渲染 `.uni-tabbar` DOM 节点
- Android/iOS：不渲染原生 TabBar View
- 微信小程序：不渲染原生的 `tabBar` 组件
- 开发者必须自己在每个 Tab 页中引入自定义 TabBar 组件
- `uni.switchTab()` 可以正常使用

### 2.2 manifest.json — 应用级配置

```json
{
  "name": "应用名",
  "appid": "__UNI__XXXX",
  "versionName": "1.0.0",
  "versionCode": "100",
  
  // ★ App 端专用配置 ★
  "app-plus": {
    "splashscreen": { "autoclose": true, "delay": 0 },
    "modules": { "OAuth": {} },          // 需要的原生模块
    "distribute": {
      "android": {
        "permissions": ["<uses-permission .../>"],
        "minSdkVersion": 21,
        "targetSdkVersion": 33
      },
      "ios": {
        "privacyDescription": {
          "NSCameraUsageDescription": "需要使用相机"
        }
      }
    },
    "nativePlugins": {}                  // 原生插件
  },
  
  // ★ 微信小程序专用 ★
  "mp-weixin": {
    "appid": "wxXXXX",
    "setting": { "urlCheck": false },
    "usingComponents": true
  },
  
  "vueVersion": "3",                     // "2" 或 "3"
  "locale": "zh-Hans"
}
```

---

## 第三章：uni API 完全指南

### 3.1 路由导航

```javascript
// 保留当前页，跳转到新页面（新页面压栈）
uni.navigateTo({ url: '/pages/detail/index?id=1' })

// 关闭当前页，跳转到新页面
uni.redirectTo({ url: '/pages/login/index' })

// 关闭所有页面，打开新页面（常用于登录后跳首页）
uni.reLaunch({ url: '/pages/home/index' })

// ★ 跳转到 tabBar 页面（必须使用这个，navigateTo 不行）★
uni.switchTab({ url: '/pages/home/index' })

// 返回上一页
uni.navigateBack({ delta: 1 })

// 获取当前页面栈
const pages = getCurrentPages()
const currentPage = pages[pages.length - 1]
const route = currentPage.route           // 'pages/home/index'
const options = currentPage.options        // { id: '1' }
```

**关键注意**：
- `switchTab` 只能跳 `tabBar.list` 里配置的页面
- `navigateTo` 不能跳 tabBar 页面（会失败）
- 页面栈最多 10 层（小程序限制）
- `reLaunch` 会销毁 Pinia store（因为整个应用重新初始化）

### 3.2 网络请求

```javascript
uni.request({
  url: 'https://api.example.com/data',
  method: 'GET',
  data: { page: 1 },
  header: { 'Authorization': 'Bearer xxx' },
  timeout: 15000,
  success: (res) => { console.log(res.data) },
  fail: (err) => { console.error(err) }
})

// 上传文件
uni.uploadFile({
  url: 'https://api.example.com/upload',
  filePath: tempFilePath,
  name: 'file',
  formData: { folder: 'avatars' },
  success: (res) => { console.log(JSON.parse(res.data)) }
})

// WebSocket
const socket = uni.connectSocket({ url: 'wss://...' })
socket.onOpen(() => {})
socket.onMessage((res) => { console.log(res.data) })
socket.send({ data: JSON.stringify({ msg: 'hello' }) })
```

**网络请求的最佳实践**：
```javascript
// 封装统一的 request 工具
const BASE_URL = 'https://api.example.com'

function request(method, url, data, options = {}) {
  const token = uni.getStorageSync('token')
  const fullUrl = url.startsWith('http') ? url : BASE_URL + url
  
  return new Promise((resolve, reject) => {
    uni.request({
      url: fullUrl, method,
      header: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      },
      data,
      timeout: options.timeout || 15000,
      success: (res) => {
        if (res.statusCode === 401) {
          uni.removeStorageSync('token')
          uni.reLaunch({ url: '/pages/login/index' })
          return
        }
        if (res.data?.code === 200) resolve(res.data.data)
        else reject(new Error(res.data?.message))
      },
      fail: reject
    })
  })
}

export const get = (url, params, opts) => {
  const qs = params ? '?' + new URLSearchParams(params).toString() : ''
  return request('GET', url + qs, undefined, opts)
}
export const post = (url, data, opts) => request('POST', url, data, opts)
export const put = (url, data, opts) => request('PUT', url, data, opts)
export const del = (url, params, opts) => {
  const qs = params ? '?' + new URLSearchParams(params).toString() : ''
  return request('DELETE', url + qs, undefined, opts)
}
```

### 3.3 存储 (Storage)

```javascript
// 同步操作（简单、常用）
uni.setStorageSync('key', 'value')
const val = uni.getStorageSync('key')
uni.removeStorageSync('key')

// 异步操作（大数据量时用）
uni.setStorage({ key: 'key', data: 'value', success: () => {} })
uni.getStorage({ key: 'key', success: (res) => { console.log(res.data) } })

// 存储限制（各端不同）
// H5: 5-10MB (localStorage)
// App: 无限制 (原生 SQLite)
// 小程序: 10MB
```

### 3.4 生命周期 (Vue3 方式)

```javascript
// ★ 在 <script setup> 中使用 uni 生命周期 ★
import { onLaunch, onShow, onHide, onError } from '@dcloudio/uni-app'

// 应用级生命周期 (通常在 App.vue 中)
onLaunch(() => { console.log('App 启动') })
onShow(() => { console.log('App 从后台进入前台') })
onHide(() => { console.log('App 进入后台') })

// ★ 页面级生命周期 (在页面组件中使用) ★
import { onLoad, onReady, onShow, onHide, onUnload } from '@dcloudio/uni-app'

onLoad((options) => {     // 页面加载，接收路由参数
  console.log('页面参数:', options.id)
})
onReady(() => {})          // 页面初次渲染完成
onShow(() => {})           // 页面显示 (每次切换到此页都触发)
onHide(() => {})           // 页面隐藏
onUnload(() => {})         // 页面销毁
onPullDownRefresh(() => {  // 下拉刷新
  // 请求完数据后必须调用
  uni.stopPullDownRefresh()
})
onReachBottom(() => {})    // 触底加载更多
```

**关键区别**：
- Vue 的 `onMounted` ≠ uni 的 `onReady`：`onMounted` 可能在数据还没渲染完就触发
- `onShow` 在**每次**页面显示时都触发（包括从子页面返回）
- App 端的 `onShow` 和 `onHide` 对应应用的前后台切换
- `onLoad` 只在首次加载时触发一次，适合获取路由参数

### 3.5 界面交互

```javascript
// Toast
uni.showToast({ title: '成功', icon: 'success', duration: 2000 })
uni.hideToast()

// Loading
uni.showLoading({ title: '加载中...' })
uni.hideLoading()

// 模态框
uni.showModal({
  title: '确认', content: '确定要删除吗？',
  success: (res) => { if (res.confirm) { /* 确定 */ } }
})

// ActionSheet
uni.showActionSheet({
  itemList: ['选项1', '选项2'],
  success: (res) => { console.log(res.tapIndex) }
})

// 导航栏 Loading
uni.showNavigationBarLoading()
uni.hideNavigationBarLoading()
```

### 3.6 图片和媒体

```javascript
// 选择图片
uni.chooseImage({
  count: 1,
  sizeType: ['compressed'],
  success: (res) => { console.log(res.tempFilePaths) }
})

// 预览图片（全屏画廊）
uni.previewImage({
  urls: ['https://...', 'https://...'],
  current: 0
})

// 选择视频
uni.chooseVideo({
  maxDuration: 60,
  success: (res) => { console.log(res.tempFilePath, res.duration) }
})

// 拍照/录像
uni.chooseMedia({
  count: 1,
  mediaType: ['image', 'video'],
  success: (res) => { console.log(res.tempFiles) }
})
```

---

## 第四章：各端差异深度剖析

### 4.1 H5 端

**实现原理**：uni-app 编译成标准 Vue 3 SPA，运行在浏览器中。

**特点**：
- 完整的 DOM/CSS/JS 能力，CSS 动画完全可用
- 无包体积限制
- 可以利用所有 Web API（localStorage、WebSocket、Geolocation 等）
- **没有**原生导航栏、原生 TabBar（`custom: true` 时框架不渲染）
- 跨域问题需要配置 proxy 或后端 CORS

**H5 特有的坑**：
```
1. 微信 JS-SDK 需要公众号配置
2. 支付宝/微信支付在 H5 需要跳转
3. 部分 CSS (如 safe-area) 在浏览器全屏模式下才生效
4. window.history 需要自己管理（uni 的路由基于 history API）
5. 原生模块 (如 plus.xxx) 不可用
```

**调试**：直接用 Chrome DevTools。

### 4.2 Android 端

**实现原理**：整个 uni-app 运行在 Android 系统的 WebView 中。JS 通过 Bridge 调用原生能力。

```
┌─────────────────────────────┐
│       Android APK            │
│  ┌───────────────────────┐  │
│  │    WebView (系统内核)  │  │
│  │  ┌─────────────────┐  │  │
│  │  │  uni-app (Vue3) │  │  │
│  │  │  + CSS + JS     │  │  │
│  │  └────────┬────────┘  │  │
│  │           │ Bridge     │  │
│  └───────────┼────────────┘  │
│              ▼                │
│  ┌───────────────────────┐   │
│  │   原生模块 (Java)      │   │
│  │   - plus.push         │   │
│  │   - plus.camera       │   │
│  │   - plus.geolocation  │   │
│  └───────────────────────┘   │
└──────────────────────────────┘
```

**特点**：
- 使用系统 WebView（Android 5.0+ 基于 Chromium）
- `plus.xxx` API 可用（调用原生功能）
- 无跨域限制（WebView 不检查 CORS）
- CSS 动画性能不如原生
- **tabBar 的 `shown` 字段控制原生 TabBar 显示**

**Android 特有的坑**：
```
1. 不同厂商 WebView 内核版本不同（华为、小米、OPPO 差异大）
2. 软键盘弹出时页面布局可能错乱
3. 返回键默认行为是 navigateBack
4. 通知需要申请权限（Android 13+）
5. 文件路径需要原生处理 (plus.io)
6. tabBar.custom:true 仍然可能生成 shown:true 的 manifest → 需要 patch
```

**调试**：
```
1. USB 连接手机，打开开发者模式
2. Chrome 地址栏输入 chrome://inspect
3. 找到 WebView → inspect
4. 或者在 HBuilderX 中「运行到手机」自动连接调试
```

### 4.3 iOS 端

**实现原理**：与 Android 类似，但在 WKWebView 中运行，Bridge 层使用 JavaScriptCore。

**特点**：
- 使用 WKWebView（iOS 8+）
- 渲染性能优于 Android（Apple 的 JIT 优化更好）
- 底部安全区域 `env(safe-area-inset-bottom)` 必须适配（刘海屏）
- App Store 审核严格
- `plus.xxx` API 同样可用

**iOS 特有的坑**：
```
1. WKWebView 跨域请求有额外限制
2. 不支持 WebRTC（除非 iOS 14.3+）
3. 软键盘弹出行为与 Android 完全不同
4. 本地存储可能被系统清理
5. 企业证书打包和AppStore打包差异大
6. UUID 和 IDFA 限制
```

**调试**：
```
1. Mac + Xcode + Safari
2. Safari → 开发 → 选择设备 → 选择 WebView
```

### 4.4 微信小程序

**实现原理**：编译成小程序原生代码（WXML + WXSS + JS），在微信的 JavaScriptCore 引擎中运行。

```
uni-app .vue 文件
      │
      ▼ 编译器
      │
小程序原生格式:
  ├── .wxml   (模板)
  ├── .wxss   (样式)
  ├── .js     (逻辑)
  └── .json   (配置)
```

**特点**：
- 无 DOM、无 BOM、无 Web API
- 视图层和逻辑层分离，通过 `setData` 通信
- 每个包限制 2MB（总包可拆分到 20MB）
- 所有网络请求必须在管理后台配置合法域名
- 不能使用 Vue 的 `transition`、`keep-alive` 等

**小程序特有的坑**：
```
1. v-for 中的 :key 会强制编译成 wx:key
2. CSS 不支持部分选择器 (如 attribute selector)
3. 不支持 SVG（需要用 base64 image）
4. 不支持 webp 图片（部分新版支持）
5. 组件命名不能用驼峰
6. wxss 不支持本地图片（需要 base64 或网络图片）
7. 生命周期函数名固定 (onLoad, onShow 等)
8. 不支持在 APP.vue 中使用组件
9. 不支持 Position: fixed 在某些场景 (如 input focus)
```

**调试**：微信开发者工具（Mac/Windows）。

---

## 第五章：数据管理和状态

### 5.1 Pinia Store（项目实际使用）

```javascript
// stores/app.js
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  // ★ State（用 ref 而不是 reactive，保证响应式解构）★
  const currentUser = ref({ userId: '', nickname: '' })
  const isLoggedIn = ref(false)
  
  // ★ Getters（用 computed）★
  // pinia 自动映射为 getter
  
  // ★ Actions（用普通函数）★
  function setCurrentUser(payload) {
    currentUser.value = { ...currentUser.value, ...payload }
  }
  
  // ★ 异步 Action ★
  async function ensureProfileLoaded(userId) {
    try {
      const result = await getUserProfile(userId)
      setCurrentUser({
        nickname: result.nickname,
        avatarUrl: result.avatarUrl,
        // ...
      })
    } catch { /* handle error */ }
  }
  
  return {
    currentUser, isLoggedIn,
    setCurrentUser, ensureProfileLoaded
  }
})
```

```javascript
// 在页面/组件中使用
import { useAppStore } from '@/stores/app'
const appStore = useAppStore()

// 直接访问（响应式）
console.log(appStore.currentUser.nickname)

// 调用 action
appStore.setCurrentUser({ nickname: '新昵称' })
await appStore.ensureProfileLoaded(1)
```

**为什么不用 Vuex**：
- Pinia 是 Vue 官方推荐的 Vuex 5
- 完整的 TypeScript 支持
- 无需 mutations（直接修改 state）
- 完美支持 Composition API
- 更好的 DevTools 集成

### 5.2 跨页面通信

```javascript
// ★ uni.$emit / uni.$on（全局事件总线）★
// 页面A发送
uni.$emit('data:updated', { id: 1 })

// 页面B接收（通常在 onLoad 或 onShow 中注册）
uni.$on('data:updated', (data) => { console.log(data.id) })

// ★ 清理事件监听（防止内存泄漏）★
onUnload(() => { uni.$off('data:updated') })
```

---

## 第六章：uni-ui 组件库和自定义组件

### 6.1 uni-ui 核心组件

```javascript
// 安装
npm install @dcloudio/uni-ui

// 使用（按需引入，不用注册）
import UniIcons from '@dcloudio/uni-ui/lib/uni-icons/uni-icons.vue'
import UniList from '@dcloudio/uni-ui/lib/uni-list/uni-list.vue'
```

### 6.2 自定义组件最佳实践

```vue
<!-- components/CustomTabBar.vue -->
<template>
  <view class="tab-bar-container">
    <view class="bottom-nav">
      <view 
        v-for="item in tabs" :key="item.key"
        :class="['bottom-nav__item', { 'is-active': currentTab === item.key }]"
        @click="onTabClick(item)">
        <text class="nav-icon">{{ item.icon }}</text>
        <text class="nav-text">{{ item.label }}</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const currentTab = ref('home')

// 通过 uni.$on 实时更新高亮
if (typeof uni !== 'undefined') {
  uni.$on('tab:switch', (key) => { currentTab.value = key })
}

function onTabClick(item) {
  currentTab.value = item.key
  uni.switchTab({ url: item.path })
}
</script>

<style scoped>
.tab-bar-container {
  position: fixed; bottom: 0; left: 0; right: 0;
  z-index: 1000;
}
</style>
```

---

## 第七章：CSS 适配各端

### 7.1 安全区域适配

```css
/* iPhone X 及以上刘海屏 */
page {
  padding-top: env(safe-area-inset-top);        /* 状态栏高度 */
  padding-bottom: env(safe-area-inset-bottom);  /* 底部 Home 指示器 */
}

/* 固定顶部元素 */
.fixed-top {
  position: fixed;
  top: 0;
  padding-top: env(safe-area-inset-top);
}

/* 固定底部元素（自定义 TabBar） */
.custom-tabbar {
  position: fixed;
  bottom: 0;
  height: calc(50px + env(safe-area-inset-bottom));
  padding-bottom: env(safe-area-inset-bottom);
}
```

### 7.2 响应式单位 rpx

```
rpx 是 uni-app 的核心尺寸单位：

750rpx = 屏幕宽度（无论什么设备）

换算：
  iPhone 6  (375px) → 1rpx = 0.5px
  iPhone 6+ (414px) → 1rpx = 0.552px
  Android   (360px) → 1rpx = 0.48px
  
使用建议：
- 字体、间距、圆角用 rpx → 自动等比缩放
- 边框用 1px（物理像素）→ 不会等比缩放变粗
```

### 7.3 CSS 兼容性速查

| 特性 | H5 | App | 小程序 |
|------|-----|-----|--------|
| flexbox | ✓ | ✓ | ✓ |
| grid | ✓ | ✓ | ✗ (部分) |
| position: fixed | ✓ | ✓ | ✗ (在 input focus 时失效) |
| backdrop-filter | ✓ | ✗ | ✗ |
| CSS 变量 (--var) | ✓ | ✓ | ✓ |
| @keyframes | ✓ | ✓ | ✓ |
| vh/vw 单位 | ✓ | ✓ | ✓ (部分) |
| overflow: scroll | ✓ | ✓ | ✓ |
| -webkit-line-clamp | ✓ | ✓ | ✓ |

---

## 第八章：打包和发布

### 8.1 H5 部署

```bash
npm run build:h5
# 产物在 dist/build/h5/
# 直接部署到任意静态服务器 (Nginx / OSS / CDN)
```

### 8.2 Android APK 打包

```bash
# 方式一：本地打包
npm run build:app
# 然后用 HBuilderX → 发行 → 原生App-本地打包

# 方式二：云打包（推荐）
# HBuilderX → 发行 → 原生App-云打包
# 选择 .jks 签名文件
# 等待云端编译完成 → 下载 APK
```

### 8.3 iOS IPA 打包

```
需要：
1. Mac 电脑
2. Xcode
3. Apple Developer 账号 ($99/年)
4. 在 HBuilderX 中配置证书
5. 发行 → 原生App-云打包
```

### 8.4 微信小程序发布

```bash
npm run build:mp-weixin
# 产物在 dist/build/mp-weixin/
# 用微信开发者工具打开，上传即可
```

---

## 第九章：性能优化

### 9.1 首屏加载优化

```javascript
// 1. 分包加载（小程序必须）
// pages.json
{
  "subPackages": [
    {
      "root": "pages/tools",
      "pages": [
        { "path": "focus-timer/index" },
        { "path": "weather/index" }
      ]
    }
  ]
}

// 2. 预加载分包
{
  "preloadRule": {
    "pages/home/index": {
      "network": "all",
      "packages": ["pages/tools"]
    }
  }
}

// 3. 组件异步加载
const HeavyComponent = defineAsyncComponent(() => 
  import('./HeavyComponent.vue')
)
```

### 9.2 列表性能

```html
<!-- 长列表必须用 virtual-list -->
<scroll-view scroll-y>
  <!-- 不要 v-for 渲染 1000+ 条 -->
  <!-- 用 uni-load-more 做分页加载 -->
</scroll-view>
```

### 9.3 图片优化

```html
<!-- lazy-load 懒加载 -->
<image :src="url" mode="aspectFill" lazy-load />

<!-- 根据屏幕密度加载不同尺寸 -->
<image :src="url + '?x-oss-process=image/resize,w_200'" />
```

---

## 第十章：大厂级别面试要点

### 架构设计问题
- 解释 uni-app 如何在编译时将 Vue 转为小程序原生代码
- 条件编译的实现原理和限制
- 多端适配中 CSS 方案的优劣对比 (rpx vs rem vs vw)
- 为什么 `custom: true` 在 Android 上还需要 patch manifest

### 性能问题  
- WebView 桥接的性能瓶颈在哪？如何优化？
- 小程序 setData 的优化策略
- 首屏加载时间如何优化到 2 秒以内
- 长列表渲染方案选型

### 工程化问题
- 多端项目的 CI/CD 怎么设计
- 如何管理多环境的 API 地址
- 组件库如何设计才能跨端复用
- 多端差异如何用设计模式优雅处理

### 实战问题
- 微信支付在多端的实现差异
- 推送通知在 Android / iOS 的实现差异
- 地图组件在各端的兼容性处理
- 文件上传在各端的差异和统一方案
