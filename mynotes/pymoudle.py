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

