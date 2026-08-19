# python -m venv .venv
# 注意: powershell 不会从当前文件运行指令文件 要写 .\指令文件 执行 
# pip config list / set
# pip freeze > requirements.txt / pip install -r requirements.txt
# __init__.py 包标识文件 自动本包提前导入使用__all__=[]声明
# int float bool str list dict set tuple complex
# help(keyword)

"""
Python 同步编译同步解释 python编译且运行 
跨平台原理: python解释器 : 解释器内置编译器 -> .pyc 字节码 文件 -> 运行虚拟机 
不同操作系统适配的JDK不一样
"""

"""
关键词
False None True 
and or not as assert async await break continue
class def del for while from import 
global nonlocal return 
in is lambda pass raise 
try except finally with
yield if elif else  
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

class Base(ABC):
    @abstractmethod
    def show(self):
        pass

# 君子协议: _var 表示protected形式 __var 表示private形式

class Stats(Base):
    def __init__(self, num, digits):
        super().__init__()
        self.num = num
        self.digits = digits
        self.list_var = [self.num, self.digits]
        self.demo = "demo" if True else None 

    def show(self):
        """
        min 和 max return ElementType
        others return NumType
        """
        # 参数函数通常巧妙使用lambda函数
        super().father_method()
        self.list_var = sorted(self.list_var, key=None, reverse=False) # / * 字典序
        print(self.list_var[0], self.list_var[1], self.list_var, # 警告则加\ 扩展f字符串
            all(self.list_var), any(self.list_var), sep=' and ', end='\n')
        return {
            "abs": abs(self.num),
            "round": round(self.num, self.digits),
            "sum": sum([self.num, True, False]),
            "min": min([self.num, True, False]),
            "max": max([self.num, True, False])
        }

# isinstance(obj, match_type) 扩展支持继承
print(type(Stats(True, False).show())) # return typeObj -> keyword

class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

print(Color.RED.name)
print(Color.RED.value)

@dataclass
class Pythonista:
    name: str = "Pythonista"
    age: int = 10

pythonista = Pythonista()
print(pythonista.name, pythonista.age)

string = "Hello Python"
string.replace("Hello", "Great")
print(string.count('o'), string.find("Python"), ''.join(string.split(' ', 1)))

del # 关键字 -> 删除变量引用或容器元素/键
list_var = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
len(list_var)
list_var.append(list_var.pop(-1))
list_var.insert(0, 0)
list_var.remove(0)
list_var.index(10)
# 支持列表+拼接

# 累加器 
# from functools import reduce 
# reduce(lambda acc, cur: acc + cur, nums, 0) 

for index, value in enumerate(list_var):
    print(index, value)

set_frozen = frozenset({1, 2, 3, 4, 5, 6, 7, 8, 9, 10})
set_var = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
print(set_var.union(set_frozen), set_var.intersection(set_frozen), set_var.difference(set_frozen), sep='\n')
set_var.discard(9)
set_var.add(9)

tuple_fix = (1, 2, 3,)

dict_var = {"name": "Python", "age": 10}
dict_var.pop("name", None)
dict_var.update({"author": "Python Authors"})
dict_var.setdefault(key, default_value)
print(dict_var.get("name"), dict_var.get("age"), dict_var.get("author"))
print(dict_var.keys(), dict_var.values(), dict_var.items(), sep='\n')

# 生成器函数与yield
def gen():
    print("1号执行")
    yield 1
    print("2号执行")
    yield 2
generator = gen()
# StopIteration 相关异常
print(next(generator), next(generator))
# reversed() 返回一个迭代器对象

with open('file', 'rwab+') as file:
    file.write("Hello Python")
    file.readline()
    file.writelines(["Hello Python", "Great Python"])

# 上下文协议与上下文管理器
# __enter__ __exit__ with

# 推导式 -> 列表、字典{k: v}、集合{}、生成器()
# [表达式 for 变量 in 可迭代对象 if 条件] 列表使用中括号,其他使用对应的符号和形式即可

## 进程与线程管理 --> 实际项目中大多数使用异步任务队列 进程与线程被封装在底层
## 写离线脚本、爬虫、数据处理工具时候可以用到 --> 明确本地服务 与 外部服务 区别 
import concurrent.futures
import requests
import os

def task(arg):
    pass

# 线程池
# max_workers 设大点没关系，一般设 10~20
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    # 提交所有任务
    future_list = [executor.submit(task, arg) for arg in args]
    
    # as_completed 谁先完成先处理谁
    for future in concurrent.futures.as_completed(future_list):
        try:
            result = future.result()
            print(f"成功: {result}")
        except Exception as e:
            print(f"报错: {e}")  

def hard_compute(arg):
    pass 

if __name__ == "__main__":
    data = [10000, 20000, 30000]  # 输入数据
    
    # 进程池
    # max_workers 默认就是 CPU 核数，直接不写也行
    with concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        # map 会保持顺序，且自动分配任务
        results = executor.map(hard_compute, data)
        for res in results:
            print(res)            

# 进程 / 线程 单开使用
import threading 
import time 

def worker(args):
    time.sleep(5) 
    # 干活 

task = threading.Thread(target=worker, args=(args), daemon=True) # daemon 主线程退出自动关停
task.start()

import multiprocessing 

def compute_worker(args)
    time.sleep(5) 
    # 干活

volume = multiprocessing.Process(target=compute_worker, args=(args), daemon=True) # daemon 主进程退出自动关停
volume.start() 

volume.join() # 等待 volume 进程结束 





