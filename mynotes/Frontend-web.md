class="xxx-xxx_xxx"
Program Structure:
public 
src 
  assets 
    styles 
  components 
  views 
  router
  store 
  types 
  api 
  util(s) 
  mock 
  App.vue 
  main.js ts
index.html 
.env .env.example 
.gitignore 
tsconfig.json 
tsconfig.node.json 
xxx.d.ts 
package.json 修改后 npm i 刷新package-lock.json(锁定版本,确保环境一致) 
package-lock.json 
vite.config.js ts
import { defineConfig } from "vite" // 构造/解析器
import vue from "@vitejs/plugin-vue" // 声明是一个vue项目 @组织/包(作用域包避免重名)

export default defineConfig({
  plugins: [vue()] // 挂载vue插件,让vite能够解析.vue文件 
})

构造之后的项目代码是只有入口文件和静态资源文件的,URL未必是正确的文件系统资源定位
需要使用Nginx进行代理实现正确的访问 

Emmet(代码缩写扩展工具): element>element*n[class="className"]{$}+element

## HTML基本语法
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1.0"> 
  <title>HTML</title>
  <link rel="stylesheet" href="./src/assets/styles/main.css">
  <style>
    summary::-webkit-details-marker {
      display: none;
    }

    summary::marker {
      display: none;
    }
  </style>
</head>
<body>
  <header>
    <nav>
      <ul>
        <li>><a href="#" target="_blank / _self">跳转链接</a></li>
      </ul>
    </nav>
  </header>
  <main>
    <section>
      <article>
        &lt;hn&gt; &nbsp; &lt;/hn&gt;
        <p>
          <pre>
            <code>
              content 
            </code>
          </pre>
        </p>
      </article>
    </section>

    <aside>
      <blockquote>
        <q>引用内容</q>
      </blockquote>
    </aside>

    <div>
      <span><strong>加粗</strong><ins>下划线</ins><em>斜体</em><del>删除线</del></span>
      <table border="1">
        <caption>TableName</caption>
        <!-- 表格th和td有padding和border属性可是用于css -->
        <!-- 表格结构化标签会限制colspan和rowspan,表格结构化后是明确大块 --> 

        <thead>
          <tr>
            <th>表头</th>
            <th>表头</th>
            <th>表头</th>
          </tr>
        </thead>

        <tbody>
          <tr>
            <td colspan="2" rowspan="2">内容</td>
            <td>内容</td>
          </tr>

          <tr>
            <td>内容</td>
          </tr>
        </tbody>

        <tfoot>
          <tr>
            <td colspan="3">内容</td>
          </tr>
        </tfoot>
      </table>        
    </div>

    <div class="html-media">
      <img src="path" alt="失败显示出现替代文本" title="鼠标悬浮显示标题"> 
      <video src="path" controls muted loop autoplay poster="path"></video>
      <audio src="path" controls muted loop></audio>
    </div>

    <div class="html-interact">
      <form>
        <!-- maxlength浏览器限制输入 minlength浏览器提示 -->
        <input id="id" name="name" type="text / password" placeholder="输入" minlength="n" maxlength="n" pattern="^.*?[^0-9]+.{n, m}$" required autocomplete="off / [username / current-password / new-password / email]"></input>
        <!-- v-model自动和value双向绑定,对于多选框若选有值可以都返回到数组里 -->
        <input type="radio" v-model="var" value="value">
        <input type="checkbox" v-model="varArray" value="value">
        <textarea style="resize: none;" cols="n" rows="n" placeholder="文本段" minlength="n" maxlength="n"></textarea>
        <el-select v-model="var" placeholder="请选择">
          <el-option label="label" value="value"></el-option>
        </el-select>
        <button type="reset"></button>
      </form>
    </div>
  </main>
  <footer>
    <el-badge value="value">
      <div>content</div>
    </el-badge>

    <dl>
      <dt>descriptTitle</dt>
      <dd>descriptData</dd>
    </dl>

    <detail open style="list-style: none; display: block; cursor: pointer;">
      <summary>点击展开</summary>
      <div class="content">content</div>
    </detail>

    <progress value="n" max="x">无value浏览器显示循环加载动画</progress>
  </footer>
</body>
</html>

## CSS 基本语法 高级实现(Vibe-Coding)
.text, .font {
  text-align: center;
  color: rgba(255, 255, 255, 0.5);
  text-decoration: none;
  text-shadow: 0 0 5px rgba(0, 0, 0, 0.5);
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
  font-size: 16px;
  font-weight: 300;
  line-height: 1;
  white-space: nowrap; 
  overflow: hidden;
  overflow-wrap: break-word;
  text-overflow: "...";
}

img, video, div, span {
  display: block / inline-block / inline; 
  box-shadow: 0 0 5px rgba(0, 0, 0, 0.5);
  background-color: rgba(255, 255, 255, 0.5);
  background-image: url("path")
  background-size: cover;
  background-position: center;
  border: 1px solid rgba(0, 0, 0, 0.5);
  padding: 10px 10px 10px 10px;
  margin: 10px 10px 10px 10px;
  border-radius: 5px;
  object-fit: cover;
  object-position: center;
  width: 100vw;
  height: 100vh;
  user-select: none;
  pointer-events: none;
  cursor: pointer / text / grab / grabbing / not-allowed; 
}

.positon {
  position: relative(灵魂出窍,本体定位) / absolute(相对祖先,完全放飞) / fixed(固定不动) / sticky(本体定位,偏位出窍); 
  top / right / bottom / left : 0; 
  z-index: 0; 
}

.flex {
  display: flex;
  flex: grow shrink basis; /* 子元素属性 auto 优先按照内容大小布局 */
  flex-direction: row[-reverse] / column[-reverse];
  flex-wrap: nowrap / wrap / wrap-reverse;
  justify-content: flex-start / flex-end / center / space-between(左右贴边) / space-around(左右等格) / space-evenly(左右留格);
  align-content: flex-start / flex-end / center / space-between / space-around / stretch;
  align-items: flex-start / flex-end / center / baseline / stretch;
  align-self: auto / stretch / center / flex-start / flex-end / baseline; /* 子元素属性 */
  order: 0; /* 灵魂出窍,本体定位 */
  gap: 10px;
}

.grid {
  grid-template-areas: 
  "header header header"
  "nav main aside"
  "nav footer aside";
  grid-template-columns: 200px 1fr 200px; /* repeat(auto-fill(固定列宽) / auto-fit(允许放大), minmax(100px, 1fr)) */
  grid-template-rows: 200px 1fr 200px;
  gap: 10px;
}

@keyframes AnimationName {
  0% {
    background-color: red;
  }
  75% {
    background-color: yellow;
  }
}

.transition, .animation, .transform {
  transition: all 1s;
  animation: AnimationName 1s infinite / n;
  transform: translate(100%, 100rem); /* 自身宽高百分比,左上角为移动点 ->(x) v(y) */
}

@media (min-width: 600px) {}
@media (max-width: 600px) {}

## scss vite解析
npm install sass --save-dev 
<style scoped lang="scss">
  $var: value; // 变量 支持运算与作用域 

  .father {
    color: $var; 

    &:hover {
      // & 代表父选择器 .father 
      color: darken($var, 百分比); // 变暗函数
      color: lighten($var, 百分比); // 变亮函数 
    }

    .son {
      color: $var;
    }
  }

  %extend-template {
    // 不会被用到css,继承时候发挥作用
  }

  .extend {
    @extend %extend-template; // 继承使用extend-template
  }
</style> 

## JS
const array = [1, 2, 3]
cosnt iter = array[Symbol.iterator]()
iter.next() // { value: 1, done: false }

async await // Promise 语法糖
alert prompt 
console.log() console.clear() console.error()
Object.keys() Object.values() Object.entries()

array.sort(function(a, b) {
  return a - b 
})

class User extends Oject {
  constructor(name, xx) {
    super()
    this.name = name 
    this.secret = xx 
  }

  superMethod() {
    super.superMethod()
  }
}

const user = new User("name")

`${}` ? : typeof ...var ...args  [key]

let [a, b, c] = [1, 2, 3]
let {a, b, c} = {a: 1, b: 2, c: 3} 

setTimeout setInterval clearTimeout clearInterval 
window.dispatchEvent(new CustomEvent("eventName", { detail: { data } }))
window.addEventListener("eventName", (event) => {
  const res = event.detail 
})

document.documentElement 
document.querySelector() document.querySelectorAll()
object.getAttribute() object.setAttribute(attr, val)

JSON.stringify(obj)
JSON.parse(str) 
localStorage / sessionStorage -> setItem(key, val) getItem(key) removeItem(key) clear() 
document.cookie = "key=val; key=val"

array.length string.length
array.map((val, idx) => {})
array.filter((val, idx) => {})
array.forEach((val, idx) => {})
array.find((val, idx) => {})
pop push shift unshift slice 
splice(start, deleteCount, ...val) 
array.includes(val)

for (const item in obj / array) {}
for (const item of string) {}

String(val).trim()
window.scrollTo(x, y)

// 避免用户输入url显示内容为特殊字符时被浏览器解析错误
window.encodeURI(str) window.decodeURI(str) 

try {} catch(err) {} finally {}

const now = new Date() // 自动记录这个运行时系统时间
getFullYear getMonth getDate getHours getMinutes getSeconds 

// Map对象(键可以使任何类型,object对象的键只能是字符串/Symbol)
const map = new Map()
map.set("key", "value")
map.get("key")
map.delete("key")
map.clear()

// Set对象 
const set = new Set()
Array.from(set)
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

// Reflect对象 
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
  if (true) {
    resolve("成功") // pending -> fulfilled 并且传递信息
  } else {
    reject(new Error("失败")) // pending -> rejected 并且传递错误
  }
})

promise.then((data) => {
  // 行为
}, (err) => {
  // 错误处理 
})

function* generator() {
  yield val 
}

const iter = generator()
iter.next()

// Ajax 底层
const xhr = new XMLHttpRequest()
// JQuery.ajax 和 Axios 都是基于XMLHttpRequest

## TS
// npm install typescrit
// tsc --init 生成tsconfig.json文件 
// tsconfig.json 中添加 "include": ["pathTSFile"] 执行 tsc 自动按照配置文件编译 
// .d.ts 文件作为类型声明文件,库/模块有自带的类型声明文件

/// <reference types="vite/client" /> 三斜杆指令 向编译器传递指令,这里的示例表示引入vite提供的客户端类型定义包

any unknown void never number string boolean as 
[number, boolean?]
Array<type>
(arg: type) => type 
enum Enum { A, B, C } 
type Alias = number | string 

abstract class Abs {
  constructor() {}
  abstract abstractMethod(): void 
  static staticMethod() {}
}

// implements 实现
interface Interface { 
  property: type 
  method(): type 
}

class Class {
  constructor(protected x: type, private readonly secret: type) {
    this.x = x
  }

  public override func() {
    // ...
  }
}

// Space.func()
namespace Space {
  export function func() {}
}

/* 泛型 定义时泛名 使用时类型 */

interface Interface {
  length: number
}

// 维护属性和默认类型
function func<T extends Interface, U = string>(x: T, y: U): [U, T] {
  return [y.length, x.length]
}

## 事件
@click @dbclick @click.right 
@mousedown @mouseup 
@mouseenter @mouseleave @mousemove 
@input @focus @keydown="handleKeyDown"
@keyup.enter @keyup.esc @keyup.f1 
@keyup.up @keyup.down @keyup.left @keyup.right
@contextmenu.prevent.stop="handleContextMenu"
const handleKeyDown = (event) => {
  if (event.key === "F12") {
    event.preventDefault() 
    event.stopPropagation()
  }
}

## Vue3 
v-bingd:attr 
v-model 
v-if v-else-if v-else 
v-show="布尔表达式"
v-for (content, index/key) in target :key 
@event 
{{}}

ref() obj.value 模版内自动解包  
reactive()

new URL(path, import.meta.url).href 

import { ElMessage } from "element-plus"
ElMessage({
  message: "message",
  type: "info / warning",
  duration: 2000,
  offset: 56,
  showClose: true, 
})

<router-link to="routerPath"></router-link>
<router-view></router-view>

onMounted(() => {})
onUnmounted(() => {})

const computed = computed({
  get() { return xx }, 
  set(newValue) {}
})

watch(var, (newVar, oldVar) => {}, { deep: true, immediate: true })

// 插槽
<template>
  <slot name="slot">默认内容</slot>
</template>

<Component>
  <template #slot>插槽内容</template>
</Component>


import { toRefs } from "vue"  
// 子组件接收父组件协议属性数据的协议声明
const props = defineProps({
  message: String
  count: Number 
})

// 响应对象再赋值会切断响应
const { message, count } = toRefs(props)

// 子组件发送给父组件事件的声明
const emit = defineEmits(["event"])

emit("event", "data")
@event="backFunc"

// 防抖与节流
import { debounce, throttle } from "lodash-es"

const debounceFunc = debounce(() => {}, time)
const throttleFunc = throttle(() => {}, time)
debounceFunc.cancel()
throttleFunc.cancel()

// 路由器和路由
import { useRouter, useRoute } from "vue-router" 

const router = useRouter()
const route = useRoute()

route.path 
route.meta 
route.params 
route.query 

router.replace({ path: "path", params: { }, query: { }})
router.push({ path: "path", params: {}, query: { key: "value" }})

const routes = [
  {
    path: "path",
    name: "name",
    component: () => import("component"),
    meta: { key: "value" },
    children: ...childrenRoutes 
  }
]

router.beforeEach((to, from) => { return true })
router.afterEach((to, from) => { return true })

createApp(App).use(router).use(createPinia()).use(ElementPlus, zIndex: 999999999, button: { autoInsertSpace: false }).mount("#app")

// store 
import { defineStore, storeToRefs } from "pinia" 

export const useXxxStore = defineStore("xxx", () => {
  return { object }
})

const xxxStore = useXxxStore() 
const { xxx } = storeToRefs(xxxStore) 

## axios 
import axios from "axios" 

const requests = axios.create({
  baseURL: "http://xxx.xx",
  timeout: 10000
})

requests.interceptors.request.use(
  (config) => {
    const cookies = document.cookie.split("; ")
    const tokens = cookies.map((cookie) => {
      const [key, value] = cookie.split("=")
      return { key, value }
    })

    // 行为 

    return config
  }, 
  (err) => {
    return Promise.reject(err) 
  }
)

requests.interceptors.response.use(
  (res) => {
    const data = res.data 
    const bizCode = Number(data.code)
    if (bizCode === 200) {
      return data.data 
    }

    const message = String(data.message)
    ElMessage({
      message: message,
      type: "error",
      duration: 3000,
      offset: 56,
      showClose: true
    }) 

    return Promise.reject(new Error(message))
  },
  (err) => {
    if (err.code === "ECONNABORTED" || err.code === "ERR_CANCELED") {
      return Promise.reject(new Error("请求中断"))
    }

    return Promise.reject(err)
  }
)

// data为请求体
requests.get(url, { params: params })
requests.post(url, data, { params: params }) 
requests.put(url, data, { params: params })
requests.delete(url, { params: params })

## socket.io-client 
import { io } from "socket.io-client" 

const socket = io("http://xxx.xx", {
  reconnection: true, 
  reconnectionAttempts: 5,
  reconnectionDelay: 1000,
  timeout: 10000,
  transports: ["websocket"]
})

// 内置事件监听 
socket.on("connect", () => {})
socket.on("connect_error", (err) => {})
socket.on("disconnect", (reason) => {})

// 发送数据 
socket.emit("customEvent", {})

// 监听事件 
socket.on("customEvent", (data) => {})

// 单次监听
socket.once("customEvent", (data) => {})

// 删除监听器 
socket.off("customEvent")


## SSE监听,JS自带
eventSource = new EventSource("http://xxx.xx/sse/xxx")

// 监听所有消息,包括自定义事件
eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data)
}

// 错误处理,SSE会自动重连
eventSource.onerror = (err) => {
  console.error("SSE 连接错误", err)
}

// 监听自定义事件
eventSource.addEventListener("customEvent", (event) => {
  const data = JSON.parse(event.data)
})

if (eventSource) eventSource.close() // 关闭连接 




