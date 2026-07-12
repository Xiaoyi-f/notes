## Git
git config --global --list 查看配置
git config --global user.name "用户名"
git config --global user.email "邮箱"

cd xxx
git init
git clone -b branch url
git checkout -b branchName
git pull nickName branch
git status
git branch -d branch
git add .
git commit -m commitContent
git push -u nickName branch
git remote -v
git remove add nickName url
git remote rm nickName
git merge branch

# 代理 按顺序执行
git config --global http.proxy 127.0.0.1:代理端口
git config --global https.proxy 127.0.0.1:代理端口

# 关闭代理
git config --global --unset http.proxy
git config --global --unset https.proxy

.gitattributes
Git属性配置文件

.editorconfig 是一套开源通用代码格式化标准

.gitignore
! --> 强制允许推送

Tip: 若子文件夹中有也有git配置文件，提交到仓库之后可能将对应的子文件夹视为子模块且点击打不开

gitee github codeup --> 仓库

codeup (云效) --> 阿里云:
创建组织 -> 创建项目 -> 创建仓库 -> 手动关联项目管理与仓库 -> 拉人 -> 设置项目参与者/管理员 -> 进行项目 -> 完结

## Node -- 基于v8浏览器内核的服务端运行环境 脱离浏览器
安装 nvm 管理 不同版本的 node
nvm list
nvm list available
nvm install [版本号]
nvm uninstall [版本号]
nvm use [版本号]

npx 执行命令

node 项目都需要有 package.json 以即 package-lock.json 作为 项目配置文件 其中 type 属性设置为 module
npm create vue@latest [项目名] 创建 vue 项目
npm list
npm install --save [包名@版本号] 安装到 dependencies
npm install --save-dev [包名@版本号] 安装到 devDependencies
npm uninstall [包名@版本号]
npm config list
npm config set registry [源]

## JSON
json基本数据结构: 字符串、数字、布尔值、空值(None、null...)、对象/字典、数组/列表
核心规则/标准:
1.键名必须使用双引号包裹
2.字符串必须使用双引号包裹
3.不能有注释
4.最后一个元素不要逗号
5.值不使用前导零

## XML
<?xml version="1.0" encoding="UTF-8"?>
<!-- 注释 -->
<!-- 元素自由命名，底层以树构造 -->
<!-- xml区分大小写 -->
<!-- 命名空间属性 xmlns="url" -->




