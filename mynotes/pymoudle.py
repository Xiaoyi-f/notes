import time
import json
import re
import random
from datetime import datetime

# 对于容易被封ip的网站,使用代理池
expires_time = datetime(2026, 7, 8, 12, 0, 0)
print(time.strftime("%Y-%m-%d, %H:%M:%S", time.localtime(time.time())), expires_time)
time.sleep(10)

data = {"name": "Python", "age": 10, "author": "Python Authors"}
json.loads(json.dumps(data, ensure_ascii=False))
# json.dump(data, file, ensure_ascii=False, indent=4)
# json.load(file)

text = "Hello Python"
pat = re.compile(r".*?[^0-9]+?.{n, m}", re.DOTALL)
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

# Flask






