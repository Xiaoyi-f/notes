# 02 - OTA升级、心跳机制与断网续传

---

## 一、OTA（Over-The-Air）固件升级

### 为什么需要OTA？

```
场景：你的温控系统已经部署在100个客户家里，
      突然发现有个Bug，或者要加新功能。

❌ 没有OTA：
    你 ──► 开车去100个客户家
       ──► 拆开设备
       ──► 用烧录器刷程序
       ──► 装回去
       耗时：几个月，成本：几万元

✅ 有OTA：
    你 ──► 在后台上传新固件
       ──► 点击"批量升级"
       ──► 100台设备自动下载、验证、重启
       耗时：几分钟，成本：0元
```

### OTA 流程

```
┌─────────────────────────────────────────────────────────────┐
│                      OTA 升级流程                             │
│                                                              │
│   云端                          设备                          │
│    │                            │                            │
│    │ 1. 上传固件                │                            │
│    │    版本: V1.0.2            │                            │
│    │    大小: 512KB             │                            │
│    │    MD5: abc123...          │                            │
│    │                            │                            │
│    │ 2. 发布升级通知              │                            │
│    │    MQTT: device/1/ota/cmd  │                            │
│    │    {                       │                            │
│    │      "version": "1.0.2",   │                            │
│    │      "url": "https://...", │                            │
│    │      "size": 524288,       │                            │
│    │      "md5": "abc123...",   │                            │
│    │      "force": false        │                            │
│    │    }                       │                            │
│    │───────────────────────────►│                            │
│    │                            │                            │
│    │                            │ 3. 检查版本                  │
│    │                            │    当前: V1.0.1 < V1.0.2    │
│    │                            │    需要升级！                │
│    │                            │                            │
│    │                            │ 4. 下载固件                  │
│    │                            │    HTTPS分段下载              │
│    │                            │    存到Flash的"新固件区"      │
│    │                            │                            │
│    │                            │ 5. 验证MD5                   │
│    │                            │    计算下载文件的MD5          │
│    │                            │    和云端给的对比              │
│    │                            │                            │
│    │                            │ 6. 验证通过？                │
│    │                            │    ✅ → 设置标志位            │
│    │                            │    "下次启动用新固件"          │
│    │                            │                            │
│    │                            │ 7. 重启                     │
│    │                            │    Bootloader看到标志位       │
│    │                            │    → 加载新固件运行           │
│    │                            │                            │
│    │                            │ 8. 上报升级结果               │
│    │                            │    MQTT: device/1/ota/status │
│    │◄───────────────────────────│    { success: true }         │
│    │                            │                            │
└─────────────────────────────────────────────────────────────┘
```

### OTA 安全要点

```
1. 固件签名：
   用私钥对固件签名，设备用公钥验证
   防止黑客伪造固件

2. 回滚机制：
   保留旧固件，新固件启动失败自动回滚
   防止"变砖"

3. 断点续传：
   下载中断后，从断点继续，不用重新下
   节省流量和时间

4. 强制/可选升级：
   force=true：必须升级（安全漏洞修复）
   force=false：用户可选（功能更新）

5. 升级时段：
   避开设备工作时间
   如工厂设备：凌晨2点-4点升级
```

---

## 二、心跳机制——怎么知道设备还活着

### 问题

```
设备上线了，你怎么知道它还在线？

❌ 错误做法：等消息来判断
   "设备5分钟没发消息了..."
   "是掉线了？还是一切正常只是没数据？"
   分不清！

✅ 正确做法：主动心跳
   设备每30秒发一次心跳："我还活着"
   超过90秒没收到心跳 → 判定为离线
```

### 心跳设计

```typescript
// 设备端（嵌入式）
const HEARTBEAT_INTERVAL = 30000  // 30秒

function sendHeartbeat() {
  const heartbeat = {
    type: "heartbeat",
    deviceId: DEVICE_ID,
    timestamp: Date.now(),
    status: {
      wifiRssi: -65,        // WiFi信号强度
      freeHeap: 45000,      // 剩余内存
      uptime: 86400         // 运行时间（秒）
    }
  }
  mqtt.publish(`device/${DEVICE_ID}/heartbeat`, heartbeat)
}

setInterval(sendHeartbeat, HEARTBEAT_INTERVAL)
```

```typescript
// 云端（心跳检测服务）
const HEARTBEAT_TIMEOUT = 90000   // 90秒没心跳算离线
const deviceStatus = new Map<string, { lastHeartbeat: number; online: boolean }>()

// 收到心跳时更新
mqtt.on('heartbeat', (topic, message) => {
  const { deviceId } = JSON.parse(message)
  deviceStatus.set(deviceId, {
    lastHeartbeat: Date.now(),
    online: true
  })
})

// 定时检查
setInterval(() => {
  const now = Date.now()
  for (const [deviceId, status] of deviceStatus) {
    if (status.online && now - status.lastHeartbeat > HEARTBEAT_TIMEOUT) {
      status.online = false
      console.log(`设备 ${deviceId} 离线`)
      // 发送告警通知
      sendAlert(deviceId, 'DEVICE_OFFLINE')
    }
  }
}, 10000)
```

### 心跳间隔选择

| 场景 | 心跳间隔 | 超时时间 | 原因 |
|------|---------|---------|------|
| 家庭设备 | 60秒 | 3分钟 | 省电，网络稳定 |
| 工厂监控 | 30秒 | 90秒 | 需要及时发现故障 |
| 车载设备 | 10秒 | 30秒 | 移动中网络不稳定 |
| 医疗设备 | 5秒 | 15秒 | 安全要求高 |

---

## 三、断网续传——网络不好时数据不丢

### 问题

```
设备在地下停车场，WiFi信号不好：

时间线：
  10:00 ──► 网络正常，数据正常上报
  10:05 ──► 网络断了！
  10:05-10:30 ──► 25分钟断网
  10:30 ──► 网络恢复

❌ 不做处理：
   10:05-10:30 的数据全部丢失！
   数据库里这25分钟是空白

✅ 做断网续传：
   断网期间数据存在设备本地
   网络恢复后批量上报
   数据库完整无缺失
```

### 实现方案

```
设备端（存储策略）：

┌─────────────────────────────────────────┐
│           数据缓存队列                     │
│                                         │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐  │
│  │10:05 │ │10:06 │ │10:07 │ │10:08 │  │
│  │25.5°C│ │25.6°C│ │25.7°C│ │25.8°C│  │
│  └──────┘ └──────┘ └──────┘ └──────┘  │
│                                         │
│  存储方式：                              │
│  - 内存环形缓冲区（存最近100条）          │
│  - SPI Flash/SPIFFS（存更多）            │
│                                         │
│  数据格式（紧凑）：                       │
│  [时间戳(4B), 温度(2B), 湿度(2B)]        │
│  每条8字节，100条 = 800字节              │
└─────────────────────────────────────────┘

网络恢复后上报：
  MQTT publish: device/1/batch
  {
    "type": "batch_upload",
    "count": 100,
    "data": [
      { "t": 1700003100, "temp": 255, "humi": 600 },
      { "t": 1700003160, "temp": 256, "humi": 605 },
      ...
    ]
  }
```

### 云端处理批量数据

```typescript
// 云端收到批量数据
app.post('/api/device/batch', async (req, res) => {
  const { deviceId, data } = req.body

  // 批量写入时序数据库
  const points = data.map(item => ({
    measurement: 'sensor_data',
    tags: { device_id: deviceId },
    fields: {
      temperature: item.temp / 100,
      humidity: item.humi / 100
    },
    timestamp: item.t * 1000000  // 转为纳秒
  }))

  await influxDB.writePoints(points)

  res.json({ success: true, received: data.length })
})
```

---

## 四、时序数据库——传感器数据的"归宿"

### 为什么不用MySQL存传感器数据？

```
MySQL存传感器数据：
  1台设备 × 1分钟1条 × 10个传感器 = 14400条/天
  100台设备 = 144万条/天
  1年 = 5.2亿条！

  MySQL查询 "过去30天的温度趋势"
  → 扫描 millions 行，慢！

时序数据库（InfluxDB/TDengine）：
  专为时间序列数据优化
  相同查询毫秒级
  自动压缩，省存储
  内置聚合函数（avg/max/min over time）
```

### InfluxDB 基础

```sql
-- 写入数据
INSERT sensor_data,device_id=1 temperature=25.5,humidity=60 1700000000000000000

-- 查询最近1小时的温度
SELECT MEAN(temperature) FROM sensor_data
WHERE device_id = '1' AND time > now() - 1h
GROUP BY time(1m)

-- 查询温度超过30°C的告警
SELECT * FROM sensor_data
WHERE temperature > 30 AND time > now() - 1d
```

### 数据保留策略

```sql
-- 原始数据保留7天
-- 1分钟聚合保留30天
-- 1小时聚合保留1年
-- 1天聚合永久保留

CREATE RETENTION POLICY "raw" ON "iot_db" DURATION 7d REPLICATION 1
CREATE RETENTION POLICY "1m" ON "iot_db" DURATION 30d REPLICATION 1
CREATE RETENTION POLICY "1h" ON "iot_db" DURATION 365d REPLICATION 1
```
