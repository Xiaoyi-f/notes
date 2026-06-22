## 规范Rule

CSS类名 --> xxx-xxx_xxx 

需要等待接口开发的代码块在上面注释"接口待开发"

js 统一使用没有分号的形式 

vue项目结构:

public 公开资源文件 

src 源代码文件夹 

- assets 静态资源文件
- components 自定义组件文件夹 
- router 路由文件夹 
  - index.js 首层页面路由
  - guard.js 路由守卫 
  - children.js 子层路由
- api 接口调用工具 
- mock 模拟数据 
- util 全局工具 
- views 页面 
- App.vue 根组件 
- main.js 全局的Script文件 
- .env 环境变量文件 
  - .env.development 
  - .env.production 
- index.html 入口文件 
- package.json 项目依赖包管理文件 
- vite.config.js vite解析器配置文件
- node_modules 项目依赖包文件 
- dist 解析构造后的项目发行文件夹
- .gitignore git的忽略配置文件 
-  README.md 项目说明文件 

## 单页应用SPA + history 路由 刷新 404 原理 

### 项目结构

vite等解析器打包之后，真实文件有:

​	index.html 入口文件 

​	js、css、图片等静态资源 

Tip: 不存在/home /content /detail ... 这种URL上的真实文件夹 

### 页面跳转原理 

在页面点击跳转到某个路由，只是js修改了浏览器地址栏URL

组件进行切换，这个操作不是刷新页面，毕竟vue实现出来的是单页应用程序 

当在某页面点击刷新，浏览器向Nginx发送请求 

但是请求的"路由文件"实际是不存在的，就会返回404

所以需要对Nginx进行配置，实现try_files $uri  ... 实现用户资源路口的定向 

vue会依据URL自动渲染符合对应的URL的路由页面 

**注意:** 缓存问题在前端中比较常见 

## HTML

H4: 依赖外部插件实现多媒体、存储靠Cookie，缺乏语义化，对于移动端不友好

H5: 原生支持多媒体和本地存储以即语义化标签，更适合移动端和现代Web应用

**--> 语法**

div span 

h1~h6 p strong em ins del &nbsp分号 pre code 

img video audio controls muted autoplay loop poster src alt title 

input type id class name value radio checkbox text password 

textarea style="resize: none;" cols rows placeholder pattern minlength maxlength 

el-select el-option value label

el-badge button type reset 

href="#id" --> 实现锚点跳转 

## CSS

text-align color linear-gradient() rgba() text-decoration list-style 

text-shadow box-shadow font-family font-size font-weight line-height(等盒高居中)

object-fit background-image background-color background-size background-position 

overflow hidden visibility visible display none block inline-block inline flex grid 

width height user-select pointer-events cursor pointer text grab grabbing not-allowed 

transition transform translate scale rotate animation infinite 

position relative absolute fixed sticky top right bottom left 

mask-image mask-size filter opacity() blur() brightness()

flex-basis flex-grow flex-shrink 

flex-direction row column 

justify-content: flex-start flex-end center space-between space-around space-evenly 

align-items align-item align-self order grid 

grid-template-areas grid-template-rows grid-template-columns gap 

repeat auto-fill auto-fit minmax px rem ch % vh vw dvh(动态 -> 减少/避免抖动)

@keyframes @media and or not 

## JS

Number String Boolean Undefined Null Symbol BigInt 

console.log async await Object.keys() Object.values() Object.entries()

`${}` ? : typeof [key] ...变量 

setTimeout setInterval clearTimeout clearInterval 

window.dispatchEvent(new CustomEvent('event', {detail: data}))

document.documentElement document.querySelector() document.querySelectorAll()

object.style object.getAttribute() object.setAttribute()

**localStorage sessionStorage 运用:**

方法: setItem() removeItem() getItem() clear()

document.cookie --> key1=value1; key2=value; key3=value 

**数组运用:**

数组.map((content, index) => {}) // 逐个取出数组中元素内容(索引)操作后返回一个新数组 

数组.forEach((arg) => {}) // 逐个取出数组中元素进行使用循环操作 

数组.filter((arg) => 布尔表达式) // 逐个取出数组中元素进行条件筛选返回新数组 

数组.find((arg) => 布尔表达式) // 逐个取出数组中元素进行匹配，返回第一个匹配的元素，没有匹配项返回undefined

try {} catch(err) {} finally {}

数组方法: pop() shift(删头) push(添尾) unshift(添头) slice(start, end) splice(start, deleteCount, item1, item2 ...) split()

String(content).trim()

window.scrollTo(x, y)

表单对象.validity.patternMismatch -> boolean 

encodeURI()

decodeURI()

核心URL结构字符 : / ? & =

**事件运用:**

@click @dbclick @click.right 
@mousedown.prevent @mouseup 
@mouseenter @mouseleave @mousemove
@input @submit.prevent 
@keyup.enter @keyup.esc @keydown 
@contextmenu.prevent.stop 
event.key === 'F12'
event.clientX event.clientY -> px 
event.preventDefault event.stopPropagation() 

## Vue3

v-bind:属性 or :属性

v-model

v-if v-else-if v-else 

v-show 

v-for (content, index/key) in target :key 

v-on or @ 

v-once 

{{}}



import { nextTick } from 'vue'

nextTick(() => {

​	// 等待组件完成渲染执行 

})

 

特别支持语法: <div v-for="day in 7" :key="day">{{ ['日','一','二','三','四','五','六'][day-1] }}</div>



const dynamicObj = ref(obj) 模板内自动解包 --> script内解包: dynamicObj.value 

const dynamicObj = reactive(obj) 数组或对象 无需解包

new URL(path, import.meta.url).href



<component :is="componentName"></component>



**组件通信运用:**

defineProps(['传值属性'])

const emit = defineEmits(['事件'])

emit('事件', '值')

@event="backFunc"



**插槽运用:**

<template>

​	<slot name="slot">默认内容</slot>

</template>

<Component>

​	<template #slot>插槽内容</template>

</Component>



import { ElMessage } from 'element-plus'

ElMessage({

​	message: 'message',

​	center: true,

​	duration: 1800,

​	offset: 56,

​	showClose: true,

​	type: 'info'  // 'warning' 

})



<router-link to="routerPath"></router-link>

<router-view></router-view>



**生命周期钩子运用:**

onMounted(() => {})

onUnmounted(() => {})



**计算属性和监听器运用:**

const computedTemp = computed({

​	get() {

​		return xx

​	},

​	set(new) {}

})



watch(变量, (新变量, 旧变量) => {}, { deep: true, immediate: true })



**防抖与节流运用:**

import { debounce, throttle } from 'lodash-es'

const debounceTemp = debounce(() => {}, time)

const throttleTemp = throttle(() => {}, time)

debounceTemp.cancel()

throttleTemp.cancel()



**路由器和路由运用:**

import { useRouter, useRoute } from 'vue-router' 

const router = useRouter()

const route = useRoute() 

route.path 不包含查询参数和锚点的路由路径

route.meta 当前路由对象的meta

route.params 当前路由的路由参数(例子如:id...)

route.query 当前路由的查询参数 

router.push({path: 'path', params: {}, query: {}})



**项目路由配置运用:**

import { createRouter, createWebHistory } from 'vue-router'

const routes = [

​	{

​		path: '/path/:var(regular|value)',

​		name: 'pathName',

​		component: () => import(),

​		meta: {},

​		children: ...childrenRoute

​	}

]

const router = createRouter({

​	history: createWebHistory(import.meta.env.BASE_URL),

​	routes,

​	scrollBehavior(to, from, savedPosition) {

​		if (savedPosition) {

​			return savedPosition

​		} else {

​			return { top: 0 }

​		}

​	}

})



**路由守卫运用:**

router.beforeEach((to, from) => {})

router.afterEach((to, from) => {})



**main.js基本配置:**

import ElementPlus from 'element-plus'

import { createPinia } from 'pinia'

import { createApp } from 'vue' 

import App from './App.vue'

import router from './router'

const app = createApp(App)

app.use(createPinia())

app.use(ElementPlus, zIndex: 999999999)

app.use(router)

app.mount('#app')



**pinia的store运用:**

import { defineStore } from 'pinia' 

export const useXxxStore = defineStore('xxx', () => {return {}})

const xxxStore = useXxxStore() 

const { xxx } = storeToRefs(xxxStore) 



**Json运用:**

字符串、数字、布尔值、空值、数组/列表、对象/字典

键名和字符串必须使用双引号

无注释且最后一个字段无逗号 



**XML运用:**

<?xml version="1.0" encoding="UTF-8"?>

<!-- 元素自由命名，底层以树构造 -->

<!-- XML区分大小写 --> 



**Axios运用:**

```
import axios from 'axios'
import { ElMessage } from 'element-plus'

const instance = axios.create({
	baseURL: envBaseURL,
	timeout: 10000
})


instance.interceptors.request.use(
	(config) => {
		const token = localStorage.getItem('token')
		if (token) {
			config.headers.Authorization = Bearer ${token}
		}
		return config 
	},
	(err) => {
		console.error('请求配置错误', err)
		return Promise.reject(err) 
	}
)



instance.interceptors.response.use(
	(response) => {
		const res = response.data 
		const bizCode = Number(res.code)
		if (bizCode === 200) {
			return res.data 
		}
		
		const message = String(res.message || '操作失败')
		ElMessage.error(message)
		return Promise.reject(new Error(message))

	},
	(err) => {
 	    if (err.code === 'ERR_CANCELED') {
      		return Promise.reject(err)
    	}
    	
        let message = '请求失败'
        if (err.response) {
            switch (err.response.status) {
                case 400:
                message = '请求参数错误'
                break
                case 401:
                message = '未登录或登录已过期'
                case 403:
                message = '没有权限'
                break
                case 404:
                message = '请求资源不存在'
                break
                case 500:
                message = '服务器错误'
                break
                case 503:
                message = '服务维护中'
                break
                default:
                message = `连接失败(${err.response.status})`
        	}
        } else if (err.code === 'ECONNABORTED') {
            message = '请求超时, 请稍后重试'
        } else if (err.code === 'ECONNREFUSED') {
            message = '无法连接到服务器'
        } else if (err.code === 'ENOTFOUND') {
            message = '网络连接失败'
        } else if (!navigator.onLine) {
            message = '网络已断开, 请检查网络'
        } else if (err.message === 'Network Error') {
            message = '接口请求失败'
        } else if (err.message) {
            message = err.message
        }
        
        return Promise.reject(err)
    }
)

export function axiosGet(url, params) {
    const res = instance.get(url, { params: params })
    return res 
}

export function axiosPost(url, data) {
    const res = instance.post(url, data)
    return res 
}

export function axiosPut(url, data, params) {
    const res = instance.put(url, data, { params: params })
    return res 
}

export function axiosDelete(url, params) {
    const res = instance.delete(url, { params: params })
    return res 
}
```

**WebSocket运用:**

```
npm install socket.io-client

import { io } from 'socket.io-client'

const socket = io('backEndUrl', {
    reconnection: true,
    reconnectionAttempts: 5,
    reconnectionDelay: 1000,
    timeout: 20000,
    transports: ['websocket']
})

// 内置事件监听
socket.on('connect', () => {})
socket.on('connect_error', (err) => { console.log('连接失败:', err.message) })
socket.on('disconnect', (reason) => { console.log('连接中断:', reason) })

// 发送数据
socket.emit('customEventName', {})

// 监听事件
socket.on('customEventName', (data) => {})

// 单次监听
socket.once('customEventName', (data) => {})

// 删除监听器
socket.off('customEventName')
```

**协议规范运用:**

REST[Representational State Transfer（表现层状态转移）] 规范 --> RESTful是一个形容词: 表示遵守REST规范的

>= HTTP/1
>传输: TCP
>写好接口文档，方便接口连接:
>   URL
>   Method
>   Data
>   Params
>将 REST 规范 类比为 "写信":
>信封地址: URL
>信封抬头 写上你要做的动作/行为:
>   GET：“获取信息”
>   POST：“提交数据”
>   PUT：“替换全部数据”
>   DELETE：“删除数据”
>信封内容: 主要以 Json 形式

websocket 规范 (无单一规范):
>= HTTP/2
>持续连接，快速响应，占用资源(资源管控)
>协议分类: wss(安全型) ws

