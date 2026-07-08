# python -m venv .venv
# pip config list / set
# pip freeze > requirements.txt / pip install -r requirements.txt
# __init__.py 包标识文件 自动本包提前导入使用__all__=[]声明
# int float bool str list dict set tuple complex
# help(keyword)
class Stats:
    def __init__(self, num, digits):
        self.num = num
        self.digits = digits
        self.list_var = [self.num, self.digits]

    def show(self):
        """
        min 和 max return ElementType
        others return NumType
        """
        # 参数函数通常巧妙使用lambda函数
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

string = "Hello Python"
string.replace("Hello", "Great")
print(string.count('o'), string.find("Python"), ''.join(string.split(' ', 1)))

list_var = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# reversed() 返回一个迭代器对象

