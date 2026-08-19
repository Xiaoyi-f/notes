# 02 - App（Android/iOS）打包与发布

---

## 打包之前需要先生成签名证书

说明: 证书就是证明"这个App是你做的" 没有证书，手机不让你安装

**keytool 是什么工具？**

JDK（Java Development Kit）自带的密钥 / 证书管理命令行工具

1. 生成**数字签名证书、公私密钥对**（非对称加密 RSA）；
2. 创建密钥库文件（keystore），把私钥、证书加密保存；
3. 安卓打包、Java 程序签名、HTTPS 证书签发都会用它。

加密原理简述：

- RSA 非对称加密：生成一对密钥

  - 私钥：存在 keystore 文件，保密，用来给 APP 签名；
  - 公钥：打包进 APP，系统校验安装包是否被篡改；

- 签名作用：安卓系统识别安装包唯一开发者，防止盗版 / 篡改

**keystore 文件原理**

`.keystore` 是**加密密钥仓库文件**：

- 内部存储：1 组公私钥 + 开发者证书信息
- 文件本身有**仓库密码**（访问整个文件需要）
- 里面每一套密钥别名（alias）还有单独**私钥密码**
- 没有密码无法读取、无法用它给 APK 签名
- 丢失无法找回，APP 无法更新上架

```
keytool -genkey -alias myalias -keyalg RSA -keysize 2048 -validity 36500 -keystore myapp.jks  // 生成证书
keytool -list -v -keystore myapp.jks  // 查看证书信息
```

**系统会问你**（按顺序回答）：

1. 输入密钥库口令：设置一个密码（记牢！比如 `123456`）
2. 你的姓名、组织单位、城市、省份、国家：随便填，但建议填真实信息
3. 确认后，输入刚才设置的密码两次

> **执行完后**，你会在当前目录看到 `myapp.keystore` 文件 **保存好！** **以后更新App还要用它!**

**基本流程:**

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

## 注意点

**包名规则:**

```
1. 必须全部小写字母 + 数字 + 下划线（_）或点（.）
2. 必须至少包含两个部分，用点分隔： 前缀.后缀
   例如：com.example.app
3. 每个部分必须以字母开头（不能是数字或下划线）
4. 不能包含中文、空格、特殊符号（-、@、# 等）
5. 不能是 Java 关键字（如 int、class）
6. 长度不限，但建议不要太长（20~50 字符以内）
实例: cn.tuotuomiao.foodnice
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
