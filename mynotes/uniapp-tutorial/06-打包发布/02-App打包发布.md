# 02 - App（Android/iOS）打包与发布

---

## 一、云打包（最简单，推荐新手）

### 步骤：

```
1. HBuilderX → 发行 → 原生App-云打包
2. 选择平台：Android / iOS / 两者都选
3. Android配置：
   ├── 包名：com.yourcompany.appname（唯一标识）
   ├── 证书：使用DCloud公用证书（测试）或上传自己的.jks证书
   └── 渠道：选择需要的应用市场
4. iOS配置：
   ├── Bundle ID：com.yourcompany.appname
   ├── 证书：需要.p12证书 + .mobileprovision描述文件
   └── 需要Mac电脑或付费使用DCloud云编译服务
5. 点击 "打包"
6. 等待几分钟，下载生成的 .apk / .ipa 文件
```

### Android证书生成：

```bash
# 使用JDK的keytool生成
keytool -genkey -alias myalias -keyalg RSA -keysize 2048 -validity 36500 -keystore myapp.jks

# 查看证书信息
keytool -list -v -keystore myapp.jks
```

---

## 二、本地打包（Android）

```
1. 下载 Android Studio
2. HBuilderX → 发行 → 原生App-本地打包 → 生成本地打包App资源
3. 下载 App离线SDK：https://nativesupport.dcloud.net.cn/
4. 用 Android Studio 打开 SDK 中的示例项目
5. 替换 assets/apps 下的资源为步骤2生成的资源
6. 配置包名、签名
7. Build → Generate Signed Bundle/APK
```

---

## 三、发布到应用市场

### Android 市场：

| 市场 | 地址 | 备注 |
|------|------|------|
| 华为应用市场 | https://developer.huawei.com/ | 需企业资质 |
| 小米应用商店 | https://dev.mi.com/ | 需软著 |
| OPPO/vivo | 各自开发者平台 | 需软著 |
| 应用宝 | https://app.open.qq.com/ | 需软著 |

**必备材料**：
- 软件著作权证书（软著）
- 企业营业执照（个人可用身份证）
- ICP备案/许可证（部分需要）
- 隐私政策网页

### iOS App Store：

```
1. 注册 Apple Developer 账号（$99/年）
2. 准备 Mac 电脑
3. 用 Xcode 打开项目或使用 Transporter 上传
4. App Store Connect 填写应用信息
5. 提交审核（通常1-2天）
```

---

## 四、热更新（不用重新上架）

```javascript
// App启动时检查更新
// #ifdef APP-PLUS
import { onLaunch } from '@dcloudio/uni-app'

onLaunch(() => {
  checkUpdate()
})

const checkUpdate = () => {
  // 向后端查询最新版本
  uni.request({
    url: 'https://api.yoursite.com/api/version/latest',
    success: (res) => {
      const latest = res.data.version
      const current = plus.runtime.version
      
      if (latest > current) {
        uni.showModal({
          title: '发现新版本',
          content: res.data.changelog,
          success: (modalRes) => {
            if (modalRes.confirm) {
              // 下载wgt包进行热更新
              downloadUpdate(res.data.wgtUrl)
            }
          }
        })
      }
    }
  })
}

const downloadUpdate = (url) => {
  uni.showLoading({ title: '下载中...' })
  
  const downloadTask = uni.downloadFile({
    url,
    success: (res) => {
      if (res.statusCode === 200) {
        // 安装wgt包
        plus.runtime.install(res.tempFilePath, {
          force: true
        }, () => {
          uni.hideLoading()
          uni.showModal({
            title: '更新完成',
            content: '需要重启应用',
            showCancel: false,
            success: () => {
              plus.runtime.restart()
            }
          })
        })
      }
    }
  })
  
  // 下载进度
  downloadTask.onProgressUpdate((res) => {
    console.log('下载进度：' + res.progress + '%')
  })
}
// #endif
```
