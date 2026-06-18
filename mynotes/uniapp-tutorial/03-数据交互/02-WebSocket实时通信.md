# 02 - WebSocket 实时通信

> 用于需要实时推送的场景：聊天、消息通知、实时数据更新、在线状态等。

---

## 一、WebSocket 基础用法

```javascript
// utils/socket.js - WebSocket 封装

class SocketService {
  constructor() {
    this.socket = null
    this.isConnected = false
    this.reconnectTimer = null
    this.listeners = new Map()
    this.url = 'wss://api.yoursite.com/ws'  // 你的WebSocket地址
  }

  // 连接
  connect() {
    const token = uni.getStorageSync('token')
    
    this.socket = uni.connectSocket({
      url: `${this.url}?token=${token}`,
      success: () => console.log('WebSocket连接请求已发送')
    })

    this.socket.onOpen(() => {
      console.log('WebSocket连接成功')
      this.isConnected = true
      // 发送心跳
      this.startHeartbeat()
    })

    this.socket.onMessage((res) => {
      try {
        const data = JSON.parse(res.data)
        this.handleMessage(data)
      } catch (e) {
        console.log('收到非JSON消息：', res.data)
      }
    })

    this.socket.onClose(() => {
      console.log('WebSocket连接关闭')
      this.isConnected = false
      this.reconnect()
    })

    this.socket.onError((err) => {
      console.log('WebSocket错误：', err)
      this.isConnected = false
      this.reconnect()
    })
  }

  // 发送消息
  send(data) {
    if (!this.isConnected) {
      console.log('WebSocket未连接')
      return
    }
    this.socket.send({
      data: JSON.stringify(data)
    })
  }

  // 处理收到的消息
  handleMessage(data) {
    const { type, payload } = data
    
    // 触发对应类型的监听器
    if (this.listeners.has(type)) {
      this.listeners.get(type).forEach(callback => callback(payload))
    }
  }

  // 订阅消息类型
  on(type, callback) {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, [])
    }
    this.listeners.get(type).push(callback)
  }

  // 取消订阅
  off(type, callback) {
    if (this.listeners.has(type)) {
      const list = this.listeners.get(type)
      const index = list.indexOf(callback)
      if (index > -1) list.splice(index, 1)
    }
  }

  // 心跳
  startHeartbeat() {
    this.heartbeatTimer = setInterval(() => {
      this.send({ type: 'ping' })
    }, 30000)  // 30秒一次
  }

  // 断线重连
  reconnect() {
    if (this.reconnectTimer) return
    this.reconnectTimer = setTimeout(() => {
      console.log('尝试重连...')
      this.connect()
      this.reconnectTimer = null
    }, 5000)  // 5秒后重连
  }

  // 关闭连接
  close() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
    }
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
    }
    this.socket?.close()
  }
}

export default new SocketService()
```

---

## 二、在页面中使用

### 聊天页面示例

```vue
<!-- pages/chat/chat.vue -->
<template>
  <view class="chat-page">
    <scroll-view 
      scroll-y 
      class="message-list"
      :scroll-top="scrollTop"
      scroll-with-animation
    >
      <view 
        v-for="msg in messages" 
        :key="msg.id"
        class="message"
        :class="{ 'self': msg.from === userId }"
      >
        <image :src="msg.avatar" class="avatar" />
        <view class="bubble">
          <text class="name">{{ msg.name }}</text>
          <text class="content">{{ msg.content }}</text>
          <text class="time">{{ msg.time }}</text>
        </view>
      </view>
    </scroll-view>
    
    <view class="input-area">
      <input 
        v-model="inputText"
        class="input"
        placeholder="输入消息..."
        confirm-type="send"
        @confirm="sendMessage"
      />
      <button class="send-btn" @click="sendMessage">发送</button>
    </view>
  </view>
</template>

<script setup>
import { ref, onLoad, onUnload } from '@dcloudio/uni-app'
import socket from '@/utils/socket.js'

const messages = ref([])
const inputText = ref('')
const userId = ref('')
const scrollTop = ref(0)

onLoad((options) => {
  userId.value = uni.getStorageSync('userInfo').id
  
  // 连接WebSocket
  socket.connect()
  
  // 监听消息
  socket.on('message', (data) => {
    messages.value.push({
      id: Date.now(),
      from: data.from,
      name: data.name,
      avatar: data.avatar,
      content: data.content,
      time: formatTime(new Date())
    })
    scrollToBottom()
  })
  
  // 监听在线用户
  socket.on('online', (data) => {
    uni.showToast({ 
      title: `${data.name} 上线了`, 
      icon: 'none' 
    })
  })
  
  // 加载历史消息
  loadHistory()
})

onUnload(() => {
  socket.close()
})

const sendMessage = () => {
  if (!inputText.value.trim()) return
  
  const msg = {
    type: 'message',
    payload: {
      content: inputText.value,
      to: 'group'  // 或指定用户ID
    }
  }
  
  socket.send(msg)
  
  // 本地显示自己发的消息
  messages.value.push({
    id: Date.now(),
    from: userId.value,
    name: '我',
    avatar: '/static/my-avatar.png',
    content: inputText.value,
    time: formatTime(new Date())
  })
  
  inputText.value = ''
  scrollToBottom()
}

const loadHistory = async () => {
  // 从后端拉取历史消息
  // const res = await chatApi.getHistory()
  // messages.value = res.data
}

const scrollToBottom = () => {
  setTimeout(() => {
    scrollTop.value = messages.value.length * 1000
  }, 100)
}

const formatTime = (date) => {
  const h = date.getHours().toString().padStart(2, '0')
  const m = date.getMinutes().toString().padStart(2, '0')
  return `${h}:${m}`
}
</script>

<style scoped>
.chat-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
}
.message-list {
  flex: 1;
  padding: 20rpx;
  background: #f5f5f5;
}
.message {
  display: flex;
  margin-bottom: 30rpx;
}
.message.self {
  flex-direction: row-reverse;
}
.avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 8rpx;
}
.bubble {
  max-width: 60%;
  margin: 0 20rpx;
  background: white;
  padding: 20rpx;
  border-radius: 16rpx;
}
.message.self .bubble {
  background: #95ec69;
}
.name {
  font-size: 24rpx;
  color: #999;
  display: block;
  margin-bottom: 8rpx;
}
.content {
  font-size: 30rpx;
  color: #333;
}
.time {
  font-size: 20rpx;
  color: #bbb;
  display: block;
  text-align: right;
  margin-top: 8rpx;
}
.input-area {
  display: flex;
  padding: 20rpx;
  border-top: 1rpx solid #eee;
  background: white;
}
.input {
  flex: 1;
  height: 80rpx;
  background: #f5f5f5;
  border-radius: 40rpx;
  padding: 0 30rpx;
  margin-right: 20rpx;
}
.send-btn {
  width: 120rpx;
  height: 80rpx;
  line-height: 80rpx;
  padding: 0;
  background: #07c160;
  color: white;
  border-radius: 40rpx;
  font-size: 28rpx;
}
</style>
```

---

## 三、后端WebSocket架构参考

```
┌──────────────┐      WebSocket      ┌──────────────────┐
│   UniApp     │  ═════════════════► │   云服务器        │
│   客户端      │                     │  ┌────────────┐  │
│              │  ◄═════════════════  │  │ WebSocket  │  │
│              │    消息推送           │  │  网关服务   │  │
└──────────────┘                     │  └─────┬──────┘  │
                                     │        │         │
                                     │  ┌─────▼──────┐  │
                                     │  │  业务服务   │  │
                                     │  │  (Java/Go) │  │
                                     │  └─────┬──────┘  │
                                     │        │         │
                                     │  ┌─────▼──────┐  │
                                     │  │   Redis    │  │
                                     │  │ (消息队列)  │  │
                                     │  └────────────┘  │
                                     └──────────────────┘
```

**消息协议**：

```json
// 客户端 → 服务端：发送消息
{
  "type": "message",
  "payload": {
    "content": "你好",
    "to": "user_id_123"
  }
}

// 服务端 → 客户端：推送消息
{
  "type": "message",
  "payload": {
    "from": "user_id_456",
    "name": "李四",
    "avatar": "https://...",
    "content": "你好",
    "time": "14:30:00"
  }
}

// 心跳
{ "type": "ping" }
{ "type": "pong" }
```
