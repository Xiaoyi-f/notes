Css类命名 xxx-xxx_xxx 

## 前端项目结构
public 
src 
  assets 
  components 
  views 
  stores 
  router 
    index.js 
    guard.js 
    children.js 
  api
  mock
  util

  App.vue 
  main.js 

.env 
  .env.development 
  .env.production 
.gitignore 
README.md 

index.html 


前端解析构造后真实文件变成 入口文件 js/css 静态资源 
路由切换逻辑 -> 改变url -> 匹配路由 -> Nginx代理响应页面 -> 渲染 

H4依赖外部插件 H5原生支持多媒体以及本地存储,适合移动端现代Web应用 


## HTML基本语法 -> vibecoding 
div span 
h1~h6 p strong em ins del &nbsp分号 pre code 
img video audio controls muted autoplay loop poster src alt title 
input type id class name value radio checkbox text password 
textarea style="resize: none;" cols rows placeholder pattern minlength maxlength 
el-select el-option value label
el-badge button type reset 
href="#id" --> 实现锚点跳转 
detail summary ul 
progress link
## CSS基本语法 -> vibecoding 
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
高级特性 -> ES6 有些浏览器还不太支持所以有转 ES5 的概念

类型: Number String Boolean Null Undefined Symbol BigInt NaN 

Symbol 有独一无二特性,就算创建两个一模一样的Symbol,他们也不等
// 迭代器 
const array = [1, 2, 3]
const iter = array[Symbol.iterator]()
iter.next() // {value: 1, done: false} 

async await 
alert prompt 
console.log() console.clear() console.error()
Object.keys() Object.values() Object.entries() 

array.sort(function(a, b) {
    return a - b
})

_private 私有属性/方法约定 #private 私有属性/方法实现
class User extends Object {
  constructor(name, xxx) {
    super() // 传递参数
    this.name = name
    this.secret = xxx
  }
  superMethod() {
    super.superMethod()
  }
}
const user = new User('name')

只有默认导出的内容才可以导入时候不写花括号
`${}` ? :  typeof [key] ...var ...args 
// 箭头函数没有本身的this

# 变量的解构赋值
let [a, b, c] = [1, 2, 3] 
let {a, b, c} = {a: 1, b: 2, c: 3}

setTimeout setInterval clearTimeout clearInterval
window.全局变量/常量  
window.dispatchEvent(new CustomEvent('event', {detail: data}))

document.documentElement
element.nextSibling element.previousSibling  
document.querySelector() document.querySelectorAll()
object.getAttribute() object.setAttribute(属性, 值) 

JSON.stringify(obj)
JSON.parse(str)
localStorage/sessionStorage -> setItem(key, value) getItem(key) removeItem(key) clear()
document.cookie = "keyOne=valueOne; keyTwo=valueTwo; keyThree=valueThree"

除了 Object.create(null) 生成的对象以外:
自动继承原型对象内容
所有普通对象、所有构造函数（自定义 / 内置）身上的 .prototype 对象，它们自身的隐式原型 __proto__ 全都指向 Object.prototype
new Object() 动态对象 函数对象可new prototype原型属性 -> 关联

array.length 动态数组 
array.map((val, index) => {逐个操作}) // 返回新数组 
array.forEach((val, index) => {逐个操作}) // 纯行为 
array.filter((val, index) => {布尔表达式}) // 返回新数组 
array.find((val, index) => {布尔表达式}) // 返回第一个匹配的元素,无匹配项则返回undefined
array -> pop() push() shift() unshift() slice(start, end) splice(start, deleteCount, item1, item2 ...)

// 累加器 
array.reduce(callback, initialValue) 
// array.reduce((acc, cur) => acc + cur, 0) 

String(val).trim()
window.scrollTo(x, y) 

formObject.validity.patternMismatch --> boolean 

字母数字留，符号结构留，中文空格特殊符，统统都得走
encodeURI(str) decodeURI(str) --> 保留结构符编解码
encodeURIComponent(str) decodeURIComponent(str) --> 全编解码 

try {} catch(err) {} finally {}

const now = new Date()
// 分别获取各时间单位
const year = now.getFullYear()        
const month = now.getMonth() + 1     
const day = now.getDate()            
const hours = now.getHours()         
const minutes = now.getMinutes()      
const seconds = now.getSeconds()     

// Map对象
const map = new Map()
map.set("key", "value")
map.get("key")
map.delete("key")
map.clear()

// Set对象 
const set = new Set()
set.add("value")
set.delete("value")
set.size 

// Proxy对象 响应监控
const obj = { name: "name", age: "age" }
const proxy = new Proxy(obj, {
    // 读取属性时触发
    get(target, attr, proxy) {
        // 行为
        return target[attr]
    },
    // 修改属性时触发 
    set(target, attr, value, proxy) {
        // 行为
    }
})

// Reflect 对象 
const user = { age: 20 }
// 读取
Reflect.get(user, 'age') // 20
// 修改
Reflect.set(user, 'age', 22)
// 是否存在
Reflect.has(user, 'age') // true
// 删除
Reflect.deleteProperty(user, 'age')

// 异步 
const promise = new Promise((resolve, reject) => {
    // 行为
    if (true) {
        resolve("成功时传递的数据")
    } else {
        reject(new Error("失败时传递错误"))
    }
})

// Promise 代码是异步执行的，等待过程中下面的代码不会被阻塞
promise.then((data) => {
    // 行为
}, (error) => {
    // 错误处理 
})

// 全部完成才触发then,一个错误整体结束,返回结果数组和传参数组严格对应
Promise.all([promise1, promise2, ...]).then((data) => {}, (error) => {})

// 生成器 
function* generator() {
    yield val 
}

const genObj = generator()
genObj.next() 
## TS 


## 事件
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


const dynamicObj = ref(obj) 模板内自动解包 -- script内解包: dynamicObj.value 

const dynamicObj = reactive(obj) 数组或对象 无需解包

new URL(path, import.meta.url).href


<component :is="componentName"></component>


**组件通信**

defineProps(['传值属性'])

const emit = defineEmits(['事件'])

emit('事件', '值')

@event="backFunc"


**插槽**

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


**生命周期钩子**
onMounted(() => {})
onUnmounted(() => {})


**计算属性和监听器**

const computedTemp = computed({
​	get() {
​		return xx
​	},
​	set(new) {}
})


watch(变量, (新变量, 旧变量) => {}, { deep: true, immediate: true })


**防抖与节流**
import { debounce, throttle } from 'lodash-es'

const debounceTemp = debounce(() => {}, time)
const throttleTemp = throttle(() => {}, time)
debounceTemp.cancel()
throttleTemp.cancel()


**路由器和路由**
import { useRouter, useRoute } from 'vue-router' 

const router = useRouter()
const route = useRoute() 
route.path 不包含查询参数和锚点的路由路径
route.meta 当前路由对象的meta
route.params 当前路由的路由参数(例子如:id...)
route.query 当前路由的查询参数 
router.push({path: 'path', params: {}, query: {}})


**项目路由配置**

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



**路由守卫**
router.beforeEach((to, from) => {})
router.afterEach((to, from) => {})


**main.js基本配置**
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


**pinia的store**
import { defineStore } from 'pinia' 

export const useXxxStore = defineStore('xxx', () => {return {}})
const xxxStore = useXxxStore() 
const { xxx } = storeToRefs(xxxStore) 


**Json**
字符串、数字、布尔值、空值、数组/列表、对象/字典
键名和字符串必须使用双引号
无注释且最后一个字段无逗号 



**XML**
<?xml version="1.0" encoding="UTF-8"?>
<!-- 元素自由命名，底层以树构造 -->
<!-- XML区分大小写 --> 


**Axios**

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

**WebSocket**

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

**协议规范**

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

