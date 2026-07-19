import time
import json
import re
import random
from datetime import datetime

expires_time = datetime(2026, 7, 8, 12, 0, 0)
print(time.strftime("%Y-%m-%d, %H:%M:%S", time.localtime(time.time())), expires_time)
time.sleep(10)

data = {"name": "Python", "age": 10, "author": "Python Authors"}
json.loads(json.dumps(data, ensure_ascii=False))
# json.dump(data, file, ensure_ascii=False, indent=4)
# json.load(file)

text = "Hello Python"
pat = re.compile(r"^.*?[^0-9]+.{n, m}$", re.DOTALL)
pat.search(text)
pat.findall(text)

nums = [1, 3, 5, 7, 9]
randomInt = random.randrange(-1, 0) # 包前无后
randomFloat = random.uniform(-1.0, 0.0) # 包前有后
randomChoices = random.choices(nums, k=0)
randomSample = random.sample(nums, 0)
random.shuffle(nums)

import qrcode

# md5
import hashlib
text = 'secretTextTarget'
md5 = hashlib.md5() # 建对象
md5.update(text.encode('utf-8')) # 加数据
result = md5.hexdigest() # 生成16进制32位哈希码

# 邮件发送
import smtplib
from email.mime.text import MIMEText
import string

sender_email = "15779544219@163.com"
target_email = input("请输入目标邮箱:")
code = string.digits + string.ascii_letters
html_content = f"""
    ...
"""

message = MIMEText(html_content, "html", "utf-8")
message["Subject"] = "标题"
message["From"] = f"Author <{sender_email}>"
message["To"] = target_email

# SSL 加密 SMTP 固定端口号(163、QQ、126 邮箱统一 SSL 发件端口都是 465)
with smtplib.SMTP_SSL("smtp.163.com", 465) as server:
    server.login("account", "password")
    server.send_message(message)

# crawler
# 对于容易被封ip的网站,使用代理池
# requests 老牌/同步请求
import requests

url = ""
params = {"query": "value"}
payload = {}
headers = {}

response = requests.get(url, params=params, headers=headers, timeout=10, verify=False) # 忽略证书情况
response = requests.post(url, json=payload, headers=headers, timeout=10, verify=False, files={"后端接口名": "文件对象"}) # 非json数据使用data参数
response.encoding = "utf-8" # 设置编码规则将二进制流数据转换为有效response.text
response.content.decode("unicode-escape") # 二进制专属解码方法 解决\u问题(unicode解码乱码)
res_code = response.status_code
res_headers = response.headers
res_history = response.history
res_content = response.content # 二进制文件内容
res_text = response.text # 文本内容
res_cookies = response.cookies
res_json = response.json() # json格式文本

# HTML解构
from bs4 import BeautifulSoup

html = response.text
document = BeautifulSoup(html, "html.parser")

tag = 'a'
element = document.find(tag)
elements = document.find_all(tag)
# 节点被解析为字典,最后一个节点为None
for el in elements:
    href = el.get("href")
    text = el.text.strip()
    print(href, text)

# el.children el.descendants 返回迭代器对象
# el.parent 返回父元素

# 过滤器查找
def my_filter(el):
    check = el.parent == "div"
    return check

response = document.find(my_filter)
# response = document.find_all(my_filter)

el = document.select_one("选择器")
elements = document.select("选择器")

# oss操作
"""
通过aliyun创建OSS桶然后进入RAM控制台访问找到用户访问key信息
给OSS对应的权限
服务器A记录将域名指向一个IP地址，而CNAME记录将一个域名指向另一个域名
TXT记录负责描述和验证，解决相关校验问题 
Bucket配置 -> 域名管理
"""
import oss2
import uuid

class OSSManager:
    def __init__(self):
        self.auth = oss2.Auth(
            "access_key_id",
            "access_key_secret"
        )

        self.bucket = oss2.Bucket(
            self.auth,
            "endpoint",
            "bucket_name"
        )

        domain = "https://bucket_name.endpoint"

    def upload_file(self, file_content, filename, folder="uploads"):
        extension = filename.rsplit(".", 1)[-1] if "." in filename else ""
        new_name = f"{uuid.uuid4().hex}.{extension}" if extension else uuid.uuid4().hex
        oss_key = f"{folder}/{new_name}"

        self.bucket.put_object(oss_key, file_content)
        return f"{self.domain}/{oss_key}"

    def delete_file(self, url):
        if not url:
            return

        oss_key = url.replace(f"{self.domain}/", "")
        self.bucket.delete_object(oss_key)
        return True

    def file_exists(self, oss_key):
        return self.bucket.object_exists(oss_key)

# flask-socketio
from gevent import monkey
monkey.patch_all()
# gevent 是基于协程的异步库，想要实现高并发 WebSocket，必须替换掉 Python 原生阻塞 IO 底层 API
from dotenv import load_dotenv
from flask_socketio import SocketIO, emit, join_room, leave_room

load_dotenv()

# WebSocket核心实例，gevent协程异步
# 协程是实现异步的一种技术载体
socketio = SocketIO(
    app,
    async_mode="gevent",
    cors_allowed_origins=["https://front.domain.com"],
    path="/ws/socket"
)

sid_room_map = {}

# 监听内置事件鉴权
@socketio.on("connect")
def ws_connect():
    token = request.args.get("token")
    if token != os.getenv("VALID_TOKEN"):
        return False

# 监听业务事件进入房间
@socketio.on("join_session")
def ws_join_room(room_id):
    sid = request.sid # 每一条 WebSocket 连接的唯一身份证
    sid_room_map[sid] = room_id # 底层将sid归入room_id分组
    join_room(room_id)
    emit("system_notice", {"msg": f"进入会话{room_id}"})

# 监听业务事件接收任务
@socketio.on("agent_task")
def ws_recv_task(data):
    room = sid_room_map[request.sid]
    emit("task_ack", {"code":200}) # 单发当前连接
    emit("task_broad", data, room=room) # 房间内推送

# 监听内置事件断开连接
@socketio.on("disconnect")
def ws_disconnect():
    sid = request.sid
    if sid in sid_room_map:
        room = sid_room_map.pop(sid)
        leave_room(room)

# 服务端主动推送WS消息
def ws_push(room_id, chunk_data):
    socketio.emit("ai_stream_chunk", chunk_data, room=room_id)

# redis 
import redis 
REDIS_CONFIG = {
    "host": "127.0.0.1",
    "port": 6379,
    "db": 0,
    "password": "password",
    "decode_responses": True,
    "socket_timeout": 5, # 设置超时报错,避免卡死 
    "max_connections": 20
}

pool = redis.ConnectionPool(**REDIS_CONFIG) # 字典解包为键值参数 *List/Tuple列表/元组解包为位置参数 
redis_cli = redis.Redis(connection_pool=pool)

redis_cli.set("key", "value", ex=3600) # 单位: s
redis_cli.setnx("key", "value") # 键不存在才执行 

redis_cli.get("key")
redis_cli.exists("key")
redis_cli.ttl("key") # 获取剩余过期时间 -1表示永久 -2表示不存在 
redis_cli.expire("key", 3600) # 重置过期时间

redis_cli.delete("key1", "key2", ...)

redis_cli.hset("hash_key", mapping={
    "key1": "value1",
    "key2": "value2"
})

# 有序双向列表
redis_cli.hget("hash_key", "key")
redis_cli.hgetall("hash_key") # 返回字典 
redis_cli.hmget("hash_key", ["key1", "key2"]) # 取指定字段 
redis_cli.hexists("hash_key", "key")
redis_cli.hdel("hash_key", "key1", "key2")
redis_cli.expire("hash_key", 3600) # 重置过期时间

redis_cli.rpush("key", "value")
redis_cli.lpush("key", "value")

res = redis_cli.lrange("key", 0, -1) # 包头包尾

# llen 获取列表总长度
count = redis_cli.llen("key")

pop_data = redis_cli.lpop("msg_queue")
pop_data = redis_cli.rpop("msg_queue")

# 集合
redis_cli.sadd("key", "value1", "value2", ...)

set = redis_cli.smembers("key")

# 判断某个值是否存在集合内
is_in = redis_cli.sismember("key", "value") # True

# 删除集合里指定元素
redis_cli.srem("key", "value")

# 取两个集合的交集
common = redis_cli.sinter("key1", "key2")


# weasyprint 生成pdf 
from weasyprint import HTML
from flask import send_file
import io
@app.route("/export_pdf/<int:user_id>")
def export_pdf(user_id):
    # 获取用户信息
    html_content = f"""渲染HTML代码内容"""
    pdf_file = HTML(string=html_content).write_pdf()
    return send_file(io.BytesIO(pdf_file), as_attachment=True, # 开启附件下载模式 
    download_name=f"{user["name"]}_简历.pdf", mimeType="application/pdf")


# httpx 支持异步/现代 
# pip install httpx 
# pip install httpx[http2] 支持http2
import httpx 

client = httpx.Client(
    base_url="http://xxx.xx",
    timeout=10,
    headers={
        "User-Agent": "xxx"
    },
    follow_redirects=True, # 自动重定向
    http2=True 
)

try:
    # response -> json() text content status_code cookies headers encoding content.decode('unicode-escape')
    getResponse = client.get("xxx", params={"key": "value"}, header={"key": "value"})
    postResponse = client.post("xxx", json={"key": "value"}, params={"key": "value"}, header={"key": "value"}) # data={"key": "value"} files=files 
    putResponse = client.put("xxx", json={"key": "value"}, params={"key": "value"}, header={"key": "value"})
    deleteResponse = client.delete("xxx", params={"key": "value"}, header={"key": "value"})
finally:
    client.close()

async def func():
    response = await client.requestMethod()
    return response.dataStruct 

data = asyncio.run(func())

async def func():
    tasks = [func(), func()]
    # 并发执行 
    results = await asyncio.gather(*tasks)
    return results 


    










