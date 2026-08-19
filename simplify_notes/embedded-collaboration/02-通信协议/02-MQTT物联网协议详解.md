# 02 - MQTT 物联网协议详解——设备与云端对话的"标准语言"

---

## 一、什么是 MQTT？

**MQTT = Message Queuing Telemetry Transport**
          消息    队列      遥测       传输

**一句话理解**：MQTT 是一种"发布/订阅"模式的轻量级通信协议，专门为资源受限的物联网设备设计。设备不用知道对方是谁，只要往某个"话题"（Topic）发消息，订阅了这个话题的人就能收到。

```
传统HTTP通信（一对一）：              MQTT通信（一对多/多对多）：

┌─────┐   请求    ┌─────┐           ┌─────┐   发布     ┌─────┐
│ App │ ────────► │ 云  │           │设备A│ ────────► │Broker│
└─────┘           └─────┘           └─────┘  temp/1   │  中转站│
                      │                              └─────┘
                      │ 响应                               │
                      ▼                                    │
                   ┌─────┐                                 │
                   │ App │                                 │
                   └─────┘                                 ▼
                                                    ┌──────────┐
                                                    │ temp/1   │
                                                    │  ──────► │◄── 订阅
                                                    │ 消息队列  │    的手机App
                                                    └──────────┘
                                                           │
                                                           ▼
                                                    ┌──────────┐
                                                    │  电脑    │
                                                    │ 上位机   │
                                                    │ 也订阅了  │
                                                    └──────────┘
```

**为什么物联网用 MQTT 而不是 HTTP？**

| | HTTP | MQTT |
|--|------|------|
| 连接方式 | 每次请求都要新建连接 | 建立一次，长期保持 |
| 实时性 | 轮询（定时问） | 订阅后主动推送 |
| 带宽 | 头部大（几百字节） | 头部极小（2字节） |
| 功耗 | 高（频繁连接） | 低（长连接+心跳） |
| 一对多 | 困难 | 天然支持 |

---

## 二、MQTT 核心概念

### 1. Broker（代理/中转站）

```
Broker 是 MQTT 的"邮局"，所有消息都经过它中转。

┌─────────────────────────────────────────┐
│              MQTT Broker                │
│                                         │
│   订阅表：                               │
│   ┌─────────────┬─────────────────┐    │
│   │   Topic     │   订阅者列表     │    │
│   ├─────────────┼─────────────────┤    │
│   │ home/1/temp │ [App1, Web1]    │    │
│   │ home/1/humi │ [App1]          │    │
│   │ factory/a   │ [Web1, Web2]    │    │
│   └─────────────┴─────────────────┘    │
│                                         │
│   收到 "home/1/temp" 的消息时：          │
│   → 查订阅表 → 发给 App1 和 Web1        │
│                                         │
└─────────────────────────────────────────┘
```

**常用的 Broker**：
- **EMQX**（企业级，功能最全）
- **Mosquitto**（轻量级，适合学习）
- **HiveMQ**（商业版，稳定性好）
- **阿里云IoT Hub / 腾讯云IoT Explorer**（云厂商托管）

### 2. Topic（话题/主题）

Topic 是消息的分类标签，用 `/` 分隔层级。

```
Topic 设计示例：

智能家居场景：
  home/001/livingroom/temperature   ← 001号家客厅温度
  home/001/livingroom/humidity      ← 001号家客厅湿度
  home/001/bedroom/light/status     ← 001号家卧室灯状态
  home/001/bedroom/light/cmd        ← 001号家卧室灯控制命令

工厂监控场景：
  factory/line1/machineA/temperature
  factory/line1/machineA/pressure
  factory/line1/machineA/alarm
  factory/line1/machineA/cmd
```

**Topic 通配符**：

| 通配符 | 含义 | 例子 |
|--------|------|------|
| `+` | 匹配一层 | `home/+/temperature` 匹配 `home/001/temperature`、`home/002/temperature` |
| `#` | 匹配多层 | `home/001/#` 匹配 `home/001` 下的所有子话题 |

```
订阅 home/+/temperature：
  ✅ home/001/temperature
  ✅ home/002/temperature
  ❌ home/001/livingroom/temperature  （+只匹配一层）

订阅 home/001/#：
  ✅ home/001/temperature
  ✅ home/001/livingroom/light
  ✅ home/001/livingroom/light/status
```

### 3. Publish（发布）和 Subscribe（订阅）

```
设备A（温度传感器）                    手机App
    │                                    │
    │  1. 订阅 "home/001/+/cmd"         │
    │◄───────────────────────────────────│
    │                                    │
    │  2. 发布 "home/001/temp" : 25.5   │
    │───────────────────────────────────►│
    │                                    │
    │  3. 发布 "home/001/cmd" : LED_ON  │
    │◄───────────────────────────────────│
    │                                    │
```

**重要**：发布者不需要知道谁在订阅，订阅者不需要知道谁在发布。Broker 负责中转。

---

## 三、QoS（服务质量等级）

QoS 定义了消息传递的可靠程度，共有3个级别：

```
┌─────────────────────────────────────────────────────────────┐
│  QoS 0：最多一次（At most once）                              │
│  ┌──────┐         ┌──────┐                                  │
│  │ 设备  │ ──发送──►│Broker│                                  │
│  └──────┘         └──────┘                                  │
│       │              │                                      │
│       │ 不确认        │ 直接转发                               │
│       │              │                                      │
│       ▼              ▼                                      │
│  消息可能丢失！                                              │
│  适用：传感器周期性上报（丢了一包没关系，下一包又来了）          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  QoS 1：至少一次（At least once）                             │
│  ┌──────┐    发送    ┌──────┐                               │
│  │ 设备  │ ────────► │Broker│                               │
│  └──────┘            └──────┘                               │
│     ▲ │               │ │                                   │
│     │ └──收到确认─────┘ │                                   │
│     │                  │                                    │
│     └────没收到？重发───┘                                    │
│                                                             │
│  保证消息至少到达一次，但可能重复！                            │
│  适用：控制命令（必须到达，重复了设备要去重）                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  QoS 2：恰好一次（Exactly once）                              │
│  ┌──────┐            ┌──────┐                               │
│  │ 设备  │ ──发送────►│Broker│                               │
│  └──────┘            └──────┘                               │
│     ▲ │               │ │                                   │
│     │ └──收到PUBREC────┘ │                                   │
│     │                     │                                  │
│     │ ──释放──────►      │                                   │
│     │                     │                                  │
│     └──收到PUBCOMP───────┘                                   │
│                                                             │
│  四次握手，保证消息只到达一次，不重复！                         │
│  适用：极其重要的指令（如支付、安全相关）                        │
│  开销最大，一般不用                                            │
└─────────────────────────────────────────────────────────────┘
```

| QoS | 保证 | 开销 | 适用场景 |
|-----|------|------|---------|
| 0 | 最多一次 | 最小 | 传感器周期性上报 |
| 1 | 至少一次 | 中等 | 控制命令 |
| 2 | 恰好一次 | 最大 | 极其重要的操作 |

**实际项目中的选择**：
- 温度/湿度/压力等传感器数据 → **QoS 0**（丢了就等下一包）
- 开关灯、控制电机等命令 → **QoS 1**（必须到达，设备端做去重）
- 极少用 QoS 2（太慢，大部分场景 QoS 1 就够了）

---

## 四、其他重要特性

### 1. Retained Message（保留消息）

```
问题：App刚打开时，不知道设备当前状态

解决：设备发送保留消息

设备 ──发布(retain=true)──► "home/001/light/status" : "ON"
                              │
                              ▼
                         Broker 保存这条消息
                              │
App ──订阅──► "home/001/light/status"
                              │
                              ▼
                         立刻收到 "ON"
                         （不需要等设备再发一次）

新订阅者上线时，Broker 会把最新的保留消息立刻推送给它。
每个 Topic 只保留最后一条保留消息。
```

### 2. Will Message（遗嘱消息）

```
场景：设备突然断电，怎么通知云端？

解决：连接时设置遗嘱消息

设备连接Broker时：
  "我的遗嘱是：如果我断开了，
   请向 'home/001/status' 发布 'offline'"

正常断开：设备发 DISCONNECT → 不发遗嘱
异常断开：设备断电/断网 → Broker检测到 → 自动发遗嘱

这样云端就知道设备"意外掉线"了
```

### 3. Clean Session 和持久会话

```
Clean Session = true（默认）：
  - 断开连接后，Broker 不保存未送达的消息
  - 重连后收不到离线期间的消息
  - 适合：手机App（不重要的设备）

Clean Session = false：
  - 断开连接后，Broker 保存未送达的消息
  - 重连后立刻收到离线期间的所有消息
  - 适合：重要设备（如工厂监控设备）
```

---

## 五、MQTT 实战：用 MQTTX 调试

### 1. 安装和连接

```
1. 下载 MQTTX：https://mqttx.app/
2. 打开 MQTTX，新建连接

连接配置：
  名称：测试连接
  服务器地址：broker.emqx.io（免费的公共MQTT服务器）
  端口：1883（明文）或 8883（SSL）
  客户端ID：test-client-001（唯一标识）
  用户名/密码：（公共Broker不需要）
  
  [连接]
```

### 2. 订阅和发布

```
步骤1：订阅话题
  订阅主题：home/001/temperature
  QoS：0
  [订阅]

步骤2：发布消息
  主题：home/001/temperature
  消息内容：25.5
  QoS：0
  Retain： false
  [发送]

步骤3：观察
  你会立刻在订阅窗口看到收到的消息：25.5
  （因为自己发布的消息，自己也能收到）
```

### 3. 多客户端测试

```
打开两个 MQTTX 窗口：

窗口1（模拟设备）：
  连接：device-001
  发布：home/001/temperature = 25.5

窗口2（模拟手机App）：
  连接：app-001
  订阅：home/001/temperature

结果：窗口2立刻收到 25.5
```

---

## 六、在 UniApp/Electron 中使用 MQTT

### UniApp 中使用 MQTT（小程序/App）

```typescript
// utils/mqtt.ts
import mqtt from 'mqtt/dist/mqtt.esm'

const MQTT_BROKER = 'wss://broker.emqx.io:8084/mqtt'

class MqttClient {
  private client: mqtt.MqttClient | null = null
  private callbacks: Map<string, ((data: unknown) => void)[]> = new Map()

  connect(clientId: string): Promise<void> {
    return new Promise((resolve, reject) => {
      this.client = mqtt.connect(MQTT_BROKER, {
        clientId,
        clean: true,
        connectTimeout: 4000,
        reconnectPeriod: 4000
      })

      this.client.on('connect', () => {
        console.log('MQTT连接成功')
        resolve()
      })

      this.client.on('message', (topic, message) => {
        const handlers = this.callbacks.get(topic)
        handlers?.forEach(fn => fn(JSON.parse(message.toString())))
      })

      this.client.on('error', reject)
    })
  }

  subscribe(topic: string, callback: (data: unknown) => void): void {
    this.client?.subscribe(topic)
    if (!this.callbacks.has(topic)) {
      this.callbacks.set(topic, [])
    }
    this.callbacks.get(topic)?.push(callback)
  }

  publish(topic: string, data: unknown): void {
    this.client?.publish(topic, JSON.stringify(data))
  }

  disconnect(): void {
    this.client?.end()
  }
}

export default new MqttClient()
```

```typescript
// 页面中使用
import mqttClient from '@/utils/mqtt'
import { onLoad, onUnload } from '@dcloudio/uni-app'

onLoad(async () => {
  await mqttClient.connect('app-user-001')

  // 订阅设备温度
  mqttClient.subscribe('home/001/temperature', (data) => {
    console.log('当前温度:', data)
  })

  // 订阅设备状态
  mqttClient.subscribe('home/001/status', (data) => {
    console.log('设备状态:', data)
  })
})

// 发送控制命令
const turnOnLight = () => {
  mqttClient.publish('home/001/light/cmd', {
    action: 'on',
    brightness: 100
  })
}

onUnload(() => {
  mqttClient.disconnect()
})
```

### Electron 中使用 MQTT

```typescript
// Electron 渲染进程中使用（和UniApp一样）
// 或主进程中使用（Node.js mqtt库）

import mqtt from 'mqtt'

const client = mqtt.connect('mqtt://broker.emqx.io:1883')

client.on('connect', () => {
  client.subscribe('factory/+/alarm')
})

client.on('message', (topic, message) => {
  const alarm = JSON.parse(message.toString())
  // 弹出系统通知
  new Notification('设备报警', {
    body: `${topic}: ${alarm.message}`
  })
})
```

---

## 七、MQTT Topic 设计最佳实践

```
❌ 不好的设计：
  topic1 = "temp"
  topic2 = "device1_data"
  topic3 = "light_control"
  问题：没有层级，无法扩展，容易冲突

✅ 好的设计：
  {项目}/{设备ID}/{位置}/{功能}/{方向}

  上行（设备→云端）：
    factory/line1/machineA/temperature
    factory/line1/machineA/pressure
    factory/line1/machineA/status
    factory/line1/machineA/alarm

  下行（云端→设备）：
    factory/line1/machineA/cmd
    factory/line1/machineA/config

  状态（设备当前状态，retain=true）：
    factory/line1/machineA/status

  在线状态（遗嘱消息）：
    factory/line1/machineA/online
```

---

## 八、MQTT vs HTTP/WebSocket 选择指南

| 场景 | 推荐协议 | 原因 |
|------|---------|------|
| 设备定时上报传感器数据 | **MQTT** | 低功耗，不需要轮询 |
| 云端控制设备 | **MQTT** | 实时推送，不用等设备轮询 |
| 设备上传大文件/图片 | **HTTP** | MQTT不适合传大数据 |
| App和云端API交互 | **HTTP** | 请求-响应模式，RESTful |
| 实时聊天/通知 | **WebSocket/MQTT** | 双向实时 |
| 设备首次注册 | **HTTP** | 需要复杂的认证流程 |

**混合架构**：
```
设备 ──MQTT──► Broker ──► 云端后台
                      │
                      ├──► 时序数据库（传感器数据）
                      │
                      └──► App推送（实时状态）

App ──HTTP──► 云端API（用户信息、历史数据查询）
```
