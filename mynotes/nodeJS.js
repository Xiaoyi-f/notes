// 对比于python/java,node.js与客户创建连接不会新开线程浪费内存资源
// node.js主线程永远只有一个 node 就是 node.js 记得配置环境变量
// REPL环境(重点，Node / Python 天天用) 全称：Read - Eval - Print Loop
// node js文件 执行 事件循环与循环队列 npmjs.com 网站有node生态相关库/模块讲解
// module代表当前文件本身,分离不同文件作用域避免全局变量污染 
module.exports = {
  // xxx 导出的是对象,注意解构
}
// 在 package.json 中声明 "type": "module" 可以实现 import / export  
require('modulePath')


// 异步 先调度等待过程中继续往下执行 调度好执行回调代码块 
// 内置文件系统模块 
const fs = require("fs")

fs.writeFile("filePath", "content", (err) => { }) // 默认覆盖写入
fs.writeFileSync("filePath", "content", w)

// 不传递编码,默认返回的是Buffer对象 
fs.readFile("filePath", (err, data) => {
  console.log(data.toString()) // 默认toString()参数就是"utf8" 
})
let string = fs.readFileSync("filePath", "utf8")
console.log(string.toString())

fs.appendFile("filePath", "content", (err) => { }) // 默认追加写入 
fs.appendFileSync("filePath", "content")

fs.unlink("filePaht", (err) => { }) // 删除文件
fs.unlinkSync("filePath")

fs.mkdir("dirPath", { recursive: true }, (err) => { }) // 创建目录,支持创建多级目录  
fs.mkdirSync("dirPath", { recursive: true })

fs.readdir("dirPath", (err, files) => { }) 
const dirArray = fs.readdirSync("dirPath") 
console.log(dirArray)

fs.stat("filePath", (err, stats) => {
  stats.isFile()
  stats.isDirectory()
  stats.size // 文件大小
  stats.mtime // 文件修改时间 
  stats.ctime // 文件创建时间
  stats.atime // 文件访问时间
})

require("events")
const emitter = new EventEmitter()

// 触发回调按照绑定顺序依次执行 
emitter.on("start", (message) => { /* 行为一 */ })
emitter.on("start", (message) => { /* 行为二 */ })
emitter.emit("start", "message") // 触发事件并且传递参数 
emitter.once("start", (message) => { }) // 只触发一次,触发一次后自动解除注册 
emitter.removeAllListeners("start") 

global.variable = "global"
console.log(__filename, __dirname)

// HTTP协议是一种无状态的传输协议
// content-type 记录MIME类型

const http = require("http")
const url = require("url")

// npm install mysql2 --save 安装到生产依赖环境
const mysql = require("mysql")
const connection = mysql.createConnection({
  host: "localhost",
  user: "root",
  password: "password",
  database: "my_db",
  port: 3306,
  charset: "utf8mb4" 
})

const [rowsVal, rowsMeta] = await connection.execute("SELECT * FROM table_name WHERE id = ?", [1]) // [1] 为占位符数据填补 
// js中抛出异常使用throw,python中抛出异常使用raise

// 多个用户访问不用频繁创建和删除连接 
const pool = mysql.createPool({
  host: "localhost", 
  user: "root", 
  password: "password",
  database: "test_db",
  waitForConnections: true,
  connectionLimit: 10, // 最大连接数 
  queueLimit: 0, // 等待队列最大长度,0表示无限 
  enableKeepAlive: true, // 保持连接活跃
  keepAliveInitialDelay: 0 // 保持连接活跃的时间间隔
})

async function sql() {
  const [rowsVal, rowsMeta] = await pool.execute("")
  await pool.end() // 关闭连接池 
}

// 处理过程 中间件 -> 中间加工的工具 -> 中间件上游/中间件下游数据可以整改
// 通过 npm init 为应用创建一个package.json文件
// npm install express --save node.js的一个服务端框架 
const express = require("express")
const app = express() 
app.use(express.json()) // 使用express.json()中间件
app.use("/public", express.static("./assets")) // 将某个文件夹下静态资源挂载在/public路由中

// 除了get请求外,其他请求都能带请求体,但是delete请求不建议带请求体 
app.get("/:userId/:postId", (req, res) => {
  return res.status(200).json({
    params: req.params, // 函数里字符串对应参数/路由参数
    query: req.query,
    headers: {
      authorization: req.headers.authorization 
    },
    message: "Hello Express!"
  })
})

app.post("/", (req, res) => {
  const { name, age, email } = req.body // 要使用到上面的中间件 
  return res.status(200).json({
    message: "Hello Express!"
  })
})

app.put("/", (req, res) => {})

app.delete("/", (req, res) => {})

app.all("*", (req, res, next) => {
  req.url 
  req.method 
  req.path // 不加查询参数的请求路径
  next() // 若没有使用res.send/res.json等返回数据则必须使用next()允许继续路由/调用中间件 
})

// 3000端口
app.listen(3000, "127.0.0.1", () => {
  console.log("服务器启动成功")
})

// 路由中间件 类似python中蓝图 
const router = express.Router()

router.get("/", (req, res) => { })
// ...
module.exports = router 

const router = require("./router")
app.use(router)

const cookieParser = require("cookie-parser")
app.use(cookieParser())

app.get("/", (req, res, next) => {
  if (req.cookies.isVisited) {
    console.log(req.cookies)
  } else {
    res.cookie("isVisited", "true", { maxAge: 60 * 1000, httpOnly: true, sameSite: "Strict/Lax(Lax支持跨站get请求带cookies其他请求不可)", secure: true }) // 单位: ms
  }
  next()
})

