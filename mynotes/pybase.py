# python -m venv .venv
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
dict_var.update({"author": "Python Authors"})
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


## 进程与线程管理 

