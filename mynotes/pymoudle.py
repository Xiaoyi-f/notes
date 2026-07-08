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
from bs4 import BeautifulSoup

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



