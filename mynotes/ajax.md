### 第零层：AJAX（概念本身）
**AJAX（Asynchronous JavaScript and XML）** 不是一种编程语言，而是一套**编程思想/技术统称**，它的核心是：**在不刷新整个页面的情况下，通过浏览器内置的机制与服务器交换数据，并局部更新网页**

- 以前传输的数据格式是 XML（所以名字里带 XML），现在基本都被 **JSON** 取代
- `XMLHttpRequest`、`Fetch`、`axios` 都是实现 AJAX 思想的具体**工具/手段**

---

### 第一层：XMLHttpRequest（远古原生底层，兜底的兜底）
浏览器最早提供的原生 AJAX 实现（诞生于 1999 年），**它的写法非常繁琐**，基于回调函数和状态码判断，现在**绝对不建议在新项目中直接使用**，但了解它能让你看懂老代码，并理解 axios 在浏览器端的底层原理（axios 底层封装的正是它）

**基本教学：**

```javascript
// GET 请求 
function getData(url) {
  const xhr = new XMLHttpRequest(); // 1. 创建对象
  
  // 2. 配置请求：第三个参数 true 表示异步
  xhr.open('GET', url, true);
  
  // 3. 监听状态变化（核心痛点：回调 + 繁琐判断）
  xhr.onreadystatechange = function() {
    // readyState: 0=未初始化, 1=连接已建立, 2=请求已接收, 3=处理中, 4=完成
    if (xhr.readyState === 4) {
      if (xhr.status >= 200 && xhr.status < 300) {
        // 请求成功
        console.log('成功:', JSON.parse(xhr.responseText));
      } else {
        // 请求失败（404, 500 等）
        console.error('请求失败，状态码:', xhr.status);
      }
    }
  };
  
  // 4. 发送请求
  xhr.send();
}

// POST 请求（携带 JSON） 
function postData(url, data) {
  const xhr = new XMLHttpRequest();
  xhr.open('POST', url, true);
  
  // 必须手动设置请求头，告诉后端你发的是 JSON
  xhr.setRequestHeader('Content-Type', 'application/json');
  
  xhr.onreadystatechange = function() {
    if (xhr.readyState === 4 && xhr.status === 200) {
      console.log('提交成功:', JSON.parse(xhr.responseText));
    }
  };
  
  // 发送时把 JSON 对象转成字符串
  xhr.send(JSON.stringify(data));
}

// 调用示例
getData('https://api.example.com/users');
postData('https://api.example.com/users', { name: '张三' });
```
> **巨大痛点**：
> 1. 必须手动判断 `readyState === 4`
> 2. 不支持 Promise，多个请求连环嵌套直接形成“回调地狱”
> 3. 代码臃肿，难以维护

---

### 第二层：原生 Fetch（浏览器自带，现代兜底）

现代浏览器自带 `fetch`，基于 **Promise**，解决了 XHR 的回调地狱问题。但你必须要知道它的**大坑**：**`fetch` 只在网络断网时才会报错，HTTP 状态码（如 404、500）不会走 `catch`**

```javascript
// 基础 GET 请求
async function fetchData() {
  try {
    const response = await fetch('https://api.example.com/users');
    
    // ！！！必须手动检查状态码 ！！！
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    console.log(data);
  } catch (error) {
    console.error('请求失败(断网/CORS):', error);
  }
}
```
> **结论**：比 XHR 好用得多，但仍需手动处理状态码，项目里一般不会直接这么写

---

### 第三层：Axios（项目中的绝对主流）

实际企业级项目，**99% 都用 Axios**。它基于 Promise，自动转换 JSON，并且 **HTTP 404/500 会自动进入 catch**，不需要像 fetch 那样手动 `if (!response.ok)`

**安装与基础用法（精简回顾）：**
```bash
npm install axios
```
```javascript
import axios from 'axios';

// GET
const getUser = async (id) => {
  const response = await axios.get(`/api/user/${id}`);
  return response.data; // 数据在 .data 里
};

// POST
const createUser = async (userInfo) => {
  const response = await axios.post('/api/user', userInfo);
  return response.data;
};

// 错误处理（自动捕获 404/500）
try {
  await axios.get('/api/info');
} catch (error) {
  if (error.response) {
    console.log('接口报错:', error.response.status); // 404/500
  } else if (error.request) {
    console.log('网络异常/超时');
  }
}
```

---

### 第四层：生产级封装（必学！配合 Pinia）

实际开发绝对不能到处写 `axios.get`，必须**封装统一的请求模块**

**1. 新建 `src/utils/request.js`（封装 Axios 实例 + 拦截器）**
```javascript
import axios from 'axios';
import { useUserStore } from '@/stores/user';

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
});

// 请求拦截器（自动挂载 Token）
request.interceptors.request.use((config) => {
  const userStore = useUserStore();
  if (userStore.token) {
    config.headers.Authorization = `Bearer ${userStore.token}`;
  }
  return config;
});

// 响应拦截器（统一剥数据 + 处理 401）
request.interceptors.response.use(
  (response) => {
    if (response.data.code !== 0) {
      if (response.data.code === 401) {
        const userStore = useUserStore();
        userStore.logout();
        window.location.href = '/login';
      }
      return Promise.reject(new Error(response.data.msg || '业务异常'));
    }
    return response.data.data; // 直接剥掉外层 data
  },
  (error) => Promise.reject(error)
);

export default request;
```

**2. 新建 `src/api/user.js`（模块化管理接口）**
```javascript
import request from '@/utils/request';

export const getUserInfo = (id) => {
  return request({ url: `/user/${id}`, method: 'get' });
};
```

**3. 在 Pinia Store 中调用**
```javascript
import { defineStore } from 'pinia';
import { getUserInfo } from '@/api/user';

export const useUserStore = defineStore('user', {
  state: () => ({ name: '' }),
  actions: {
    async fetchUser(id) {
      const res = await getUserInfo(id); // res 已经是核心数据了
      this.name = res.name;
    }
  }
});
```

---

### 第五层：核心痛点与解决（速查表）

| 痛点                 | 解决方案（上述封装已包含）                        |
| :------------------- | :------------------------------------------------ |
| **Token 自动携带**   | 请求拦截器统一注入 `Authorization`                |
| **接口报错统一处理** | 响应拦截器判断 `code` 并 `reject`                 |
| **401 跳转登录**     | 响应拦截器里监听特定状态码，执行 `store.logout()` |
| **数据重复嵌套**     | 响应拦截器直接返回 `response.data.data`           |
| **Loading 状态**     | 请求拦截器开启，响应拦截器关闭（搭配 UI 库）      |

---

### 最终总结

1. **概念**：AJAX 是思想（异步无刷新请求）。
2. **远古层**：`XMLHttpRequest` 是老祖宗，**看懂就行，千万别写**
3. **原生层**：`fetch` 是亲儿子，但不处理 404/500，**不太顺手**
4. **主力层**：`axios` 是王者，**项目首选**
5. **工程层**：必须封装拦截器 + 配合 Pinia，**永不裸写**
