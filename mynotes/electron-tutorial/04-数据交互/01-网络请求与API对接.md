# 01 - 网络请求与后端API对接

---

## 一、Electron 中发起 HTTP 请求

### 方式一：前端使用 fetch/axios（推荐）

```bash
# 安装 axios
npm install axios
```

```javascript
// src/utils/request.js
import axios from 'axios'

const request = axios.create({
  baseURL: 'https://api.yoursite.com',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    const data = response.data
    if (data.code !== 200) {
      return Promise.reject(data)
    }
    return data
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token过期，跳转登录
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default request
```

### 方式二：主进程使用 Node.js 请求（适合下载文件）

```javascript
// main.js
const https = require('https')
const fs = require('fs')
const path = require('path')

// 下载文件
ipcMain.handle('download-file', async (event, { url, fileName }) => {
  const downloadPath = path.join(app.getPath('downloads'), fileName)
  
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(downloadPath)
    
    https.get(url, (response) => {
      const totalBytes = parseInt(response.headers['content-length'] || 0)
      let downloadedBytes = 0
      
      response.on('data', (chunk) => {
        downloadedBytes += chunk.length
        const progress = totalBytes ? Math.round((downloadedBytes / totalBytes) * 100) : 0
        
        // 发送进度到渲染进程
        event.sender.send('download-progress', { progress, fileName })
      })
      
      response.pipe(file)
      
      file.on('finish', () => {
        file.close()
        resolve({ success: true, path: downloadPath })
      })
      
      file.on('error', (err) => {
        fs.unlink(downloadPath, () => {})
        reject({ success: false, error: err.message })
      })
    })
  })
})
```

---

## 二、WebSocket 实时通信

```javascript
// src/utils/websocket.js
class ElectronWebSocket {
  constructor() {
    this.ws = null
    this.reconnectTimer = null
    this.listeners = new Map()
    this.url = 'wss://api.yoursite.com/ws'
  }

  connect() {
    const token = localStorage.getItem('token')
    this.ws = new WebSocket(`${this.url}?token=${token}`)

    this.ws.onopen = () => {
      console.log('WebSocket connected')
      this.emit('connected')
      this.startHeartbeat()
    }

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        this.handleMessage(data)
      } catch (e) {
        console.log('Received:', event.data)
      }
    }

    this.ws.onclose = () => {
      console.log('WebSocket closed')
      this.emit('disconnected')
      this.reconnect()
    }

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      this.emit('error', error)
    }
  }

  send(data) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    }
  }

  handleMessage(data) {
    const { type, payload } = data
    this.emit(type, payload)
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    this.listeners.get(event).push(callback)
  }

  off(event, callback) {
    const list = this.listeners.get(event)
    if (list) {
      const index = list.indexOf(callback)
      if (index > -1) list.splice(index, 1)
    }
  }

  emit(event, ...args) {
    const list = this.listeners.get(event)
    if (list) {
      list.forEach(cb => cb(...args))
    }
  }

  startHeartbeat() {
    this.heartbeatTimer = setInterval(() => {
      this.send({ type: 'ping' })
    }, 30000)
  }

  reconnect() {
    if (this.reconnectTimer) return
    this.reconnectTimer = setTimeout(() => {
      this.connect()
      this.reconnectTimer = null
    }, 5000)
  }

  close() {
    clearInterval(this.heartbeatTimer)
    clearTimeout(this.reconnectTimer)
    this.ws?.close()
  }
}

export default new ElectronWebSocket()
```

```vue
<!-- 聊天组件 -->
<template>
  <div class="chat">
    <div class="messages" ref="msgContainer">
      <div
        v-for="msg in messages"
        :key="msg.id"
        class="message"
        :class="{ self: msg.from === userId }"
      >
        <span class="name">{{ msg.name }}</span>
        <span class="content">{{ msg.content }}</span>
      </div>
    </div>
    
    <div class="input-area">
      <input v-model="inputText" @keyup.enter="send" placeholder="输入消息..." />
      <button @click="send">发送</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import ws from '@/utils/websocket.js'

const messages = ref([])
const inputText = ref('')
const userId = ref('')
const msgContainer = ref(null)

onMounted(() => {
  userId.value = localStorage.getItem('userId')
  
  ws.connect()
  
  ws.on('message', (data) => {
    messages.value.push(data)
    scrollToBottom()
  })
})

onUnmounted(() => {
  ws.close()
})

const send = () => {
  if (!inputText.value.trim()) return
  
  ws.send({
    type: 'message',
    payload: {
      content: inputText.value,
      from: userId.value
    }
  })
  
  inputText.value = ''
}

const scrollToBottom = () => {
  setTimeout(() => {
    msgContainer.value.scrollTop = msgContainer.value.scrollHeight
  }, 100)
}
</script>
```

---

## 三、SQLite 本地数据库

```bash
npm install better-sqlite3
```

```javascript
// main.js
const Database = require('better-sqlite3')
const path = require('path')

// 创建/连接数据库
const dbPath = path.join(app.getPath('userData'), 'app.db')
const db = new Database(dbPath)

// 创建表
db.exec(`
  CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )
`)

// IPC接口
ipcMain.handle('db-insert-message', (event, { sender, content }) => {
  const stmt = db.prepare('INSERT INTO messages (sender, content) VALUES (?, ?)')
  const result = stmt.run(sender, content)
  return { id: result.lastInsertRowid }
})

ipcMain.handle('db-get-messages', (event, { limit = 50, offset = 0 }) => {
  const stmt = db.prepare('SELECT * FROM messages ORDER BY created_at DESC LIMIT ? OFFSET ?')
  return stmt.all(limit, offset)
})

ipcMain.handle('db-delete-message', (event, id) => {
  const stmt = db.prepare('DELETE FROM messages WHERE id = ?')
  return stmt.run(id)
})
```

---

## 四、完整的登录系统示例

```vue
<!-- views/Login.vue -->
<template>
  <div class="login-page">
    <div class="login-box">
      <h2>用户登录</h2>
      
      <div class="form-item">
        <label>账号</label>
        <input v-model="form.username" placeholder="请输入账号" />
      </div>
      
      <div class="form-item">
        <label>密码</label>
        <input v-model="form.password" type="password" placeholder="请输入密码" />
      </div>
      
      <div class="form-item">
        <label>
          <input type="checkbox" v-model="rememberMe" />
          记住密码
        </label>
      </div>
      
      <button class="login-btn" :disabled="loading" @click="login">
        {{ loading ? '登录中...' : '登录' }}
      </button>
      
      <p v-if="error" class="error">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import request from '@/utils/request.js'

const router = useRouter()
const form = ref({ username: '', password: '' })
const rememberMe = ref(false)
const loading = ref(false)
const error = ref('')

onMounted(async () => {
  // 读取记住的账号
  const saved = await window.electronAPI?.store?.get('loginInfo')
  if (saved) {
    form.value.username = saved.username
    rememberMe.value = true
  }
})

const login = async () => {
  if (!form.value.username || !form.value.password) {
    error.value = '请填写完整信息'
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    const res = await request.post('/api/user/login', {
      username: form.value.username,
      password: form.value.password
    })
    
    // 保存Token
    localStorage.setItem('token', res.data.token)
    localStorage.setItem('userId', res.data.user.id)
    
    // 记住密码
    if (rememberMe.value) {
      await window.electronAPI?.store?.set('loginInfo', {
        username: form.value.username
      })
    } else {
      await window.electronAPI?.store?.delete('loginInfo')
    }
    
    // 跳转到首页
    router.push('/')
    
  } catch (err) {
    error.value = err.msg || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.login-box {
  width: 360px;
  padding: 40px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}
h2 { text-align: center; margin-bottom: 30px; color: #333; }
.form-item { margin-bottom: 20px; }
.form-item label {
  display: block;
  margin-bottom: 8px;
  color: #666;
  font-size: 14px;
}
.form-item input[type="text"],
.form-item input[type="password"] {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  box-sizing: border-box;
}
.login-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
}
.login-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.error { color: #e74c3c; text-align: center; margin-top: 15px; }
</style>
```
