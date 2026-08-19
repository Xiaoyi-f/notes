# 01 - electron-builder 打包配置与发布

---

## 一、安装与配置

```bash
npm install electron-builder --save-dev
```

```json
// package.json
{
  "name": "my-electron-app",
  "version": "1.0.0",
  "description": "我的Electron应用",
  "author": "你的名字",
  "main": "electron/main.js",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "electron:dev": "vite && electron .",
    "electron:build": "vite build && electron-builder",
    "electron:build:win": "vite build && electron-builder --win",
    "electron:build:mac": "vite build && electron-builder --mac",
    "electron:build:linux": "vite build && electron-builder --linux"
  },
  "build": {
    "appId": "com.yourcompany.appname",
    "productName": "我的应用",
    "copyright": "Copyright © 2024",
    "directories": {
      "output": "release"
    },
    "files": [
      "dist/**/*",
      "electron/**/*"
    ],
    "extraResources": [
      {
        "from": "resources/",
        "to": "resources"
      }
    ],
    "asar": true,
    "asarUnpack": [
      "**/*.node"
    ]
  }
}
```

---

## 二、Windows 打包配置

```json
// package.json 的 build 字段中添加
{
  "build": {
    "win": {
      "target": [
        {
          "target": "nsis",
          "arch": ["x64", "ia32"]
        },
        {
          "target": "portable",
          "arch": ["x64"]
        }
      ],
      "icon": "build/icon.ico",
      "publisherName": "你的公司名称",
      "verifyUpdateCodeSignature": false,
      "requestedExecutionLevel": "requireAdministrator"
    },
    "nsis": {
      "oneClick": false,
      "allowToChangeInstallationDirectory": true,
      "installerIcon": "build/icon.ico",
      "uninstallerIcon": "build/icon.ico",
      "installerHeaderIcon": "build/icon.ico",
      "createDesktopShortcut": true,
      "createStartMenuShortcut": true,
      "shortcutName": "我的应用",
      "include": "build/installer.nsh",
      "license": "LICENSE.txt"
    }
  }
}
```

**Windows 输出文件**：
- `.exe` - 安装程序（NSIS）
- `.exe` - 便携版（Portable）
- 自动更新文件：`latest.yml`

---

## 三、Mac 打包配置

```json
// package.json 的 build 字段中添加
{
  "build": {
    "mac": {
      "target": [
        {
          "target": "dmg",
          "arch": ["x64", "arm64"]
        },
        {
          "target": "zip",
          "arch": ["x64", "arm64"]
        }
      ],
      "icon": "build/icon.icns",
      "category": "public.app-category.utilities",
      "hardenedRuntime": true,
      "gatekeeperAssess": false,
      "entitlements": "build/entitlements.mac.plist",
      "entitlementsInherit": "build/entitlements.mac.plist"
    },
    "dmg": {
      "contents": [
        {
          "x": 130,
          "y": 220
        },
        {
          "x": 410,
          "y": 220,
          "type": "link",
          "path": "/Applications"
        }
      ],
      "window": {
        "width": 540,
        "height": 380
      }
    }
  }
}
```

**Mac 签名（发布到App Store需要）**：

```bash
# 1. 加入 Apple Developer Program ($99/年)
# 2. 创建证书和描述文件
# 3. 配置环境变量
export CSC_LINK="path/to/certificate.p12"
export CSC_KEY_PASSWORD="证书密码"

# 4. 打包
npm run electron:build:mac
```

**Mac 输出文件**：
- `.dmg` - 磁盘映像安装包
- `.zip` - 压缩包
- 自动更新文件：`latest-mac.yml`

---

## 四、Linux 打包配置

```json
// package.json 的 build 字段中添加
{
  "build": {
    "linux": {
      "target": [
        {
          "target": "AppImage",
          "arch": ["x64"]
        },
        {
          "target": "deb",
          "arch": ["x64"]
        },
        {
          "target": "rpm",
          "arch": ["x64"]
        }
      ],
      "icon": "build/icons",
      "category": "Utility",
      "maintainer": "你的名字 <email@example.com>",
      "vendor": "你的公司",
      "synopsis": "应用简短描述",
      "description": "应用详细描述"
    }
  }
}
```

**Linux 输出文件**：
- `.AppImage` - 通用Linux可执行文件（推荐）
- `.deb` - Debian/Ubuntu 安装包
- `.rpm` - RedHat/Fedora 安装包

---

## 五、图标准备

```
build/
├── icon.ico          # Windows图标 (256x256)
├── icon.icns         # Mac图标 (1024x1024)
└── icons/
    ├── 16x16.png
    ├── 32x32.png
    ├── 48x48.png
    ├── 64x64.png
    ├── 128x128.png
    ├── 256x256.png
    ├── 512x512.png
    └── 1024x1024.png
```

**图标生成工具**：
- 在线：https://appicon.co/
- 命令行：`npm install -g electron-icon-builder`

---

## 六、自动更新

```bash
npm install electron-updater
```

```javascript
// main.js
const { autoUpdater } = require('electron-updater')
const { dialog } = require('electron')

// 配置更新服务器
autoUpdater.setFeedURL({
  provider: 'generic',
  url: 'https://yoursite.com/updates/',
  channel: 'latest'
})

// 检查更新
function checkForUpdates() {
  autoUpdater.checkForUpdatesAndNotify()
}

// 发现更新
autoUpdater.on('update-available', (info) => {
  dialog.showMessageBox({
    type: 'info',
    title: '发现新版本',
    message: `发现新版本 ${info.version}，正在下载...`,
    buttons: ['确定']
  })
})

// 下载进度
autoUpdater.on('download-progress', (progress) => {
  const percent = Math.round(progress.percent)
  console.log(`下载进度: ${percent}%`)
  // 可以发送进度到渲染进程显示
})

// 下载完成
autoUpdater.on('update-downloaded', (info) => {
  dialog.showMessageBox({
    type: 'info',
    title: '更新已下载',
    message: '新版本已下载，是否立即安装？',
    buttons: ['稍后', '立即安装']
  }).then((result) => {
    if (result.response === 1) {
      autoUpdater.quitAndInstall()
    }
  })
})

// 更新错误
autoUpdater.on('error', (err) => {
  console.error('更新错误:', err)
})

// 应用启动时检查更新
app.whenReady().then(() => {
  createWindow()
  checkForUpdates()
  
  // 每小时检查一次
  setInterval(checkForUpdates, 60 * 60 * 1000)
})
```

**更新服务器目录结构**：

```
https://yoursite.com/updates/
├── latest.yml              # Windows更新信息
├── latest-mac.yml          # Mac更新信息
├── latest-linux.yml        # Linux更新信息
├── my-app-1.0.1.exe        # Windows安装包
├── my-app-1.0.1.exe.blockmap
├── my-app-1.0.1.dmg        # Mac安装包
├── my-app-1.0.1.dmg.blockmap
└── my-app-1.0.1.AppImage   # Linux安装包
```

---

## 七、完整打包流程

```bash
# 1. 确认代码已提交git（electron-builder需要）
git add .
git commit -m "prepare for release v1.0.0"

# 2. 修改版本号
npm version patch    # 1.0.0 -> 1.0.1
npm version minor    # 1.0.0 -> 1.1.0
npm version major    # 1.0.0 -> 2.0.0

# 3. 打包所有平台
npm run electron:build

# 4. 只打包Windows
npm run electron:build:win

# 5. 只打包Mac（需要Mac或签名服务）
npm run electron:build:mac

# 6. 只打包Linux
npm run electron:build:linux
```

---

## 八、打包常见问题

| 问题 | 解决 |
|------|------|
| 打包后白屏 | 检查 `loadFile` 路径是否正确，开发环境和生产环境路径不同 |
| 图标不显示 | 检查图标路径和格式，Windows用.ico，Mac用.icns |
| 打包体积太大 | 使用 `asarUnpack` 精简，排除不必要的依赖 |
| 外部资源找不到 | 使用 `extraResources` 配置额外资源 |
| 原生模块报错 | 确保原生模块已正确编译，使用 `electron-rebuild` |
| 杀毒软件误报 | 使用代码签名证书 |

```bash
# 重新编译原生模块
npm install -g electron-rebuild
electron-rebuild

# 或者
npx electron-rebuild
```
