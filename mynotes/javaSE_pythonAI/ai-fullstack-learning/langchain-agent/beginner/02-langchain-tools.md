# LangChain Tools 详解

## 什么是 Tools？

Tools 是 Agent 可以使用的功能组件，每个 Tool 执行特定的任务，如搜索网页、执行计算、查询数据库等。

## 内置工具

### 1. 搜索工具

```python
from langchain_community.tools import DuckDuckGoSearchRun, TavilySearchResults
from langchain_community.utilities import TavilyAPIWrapper

# DuckDuckGo 搜索（免费）
search = DuckDuckGoSearchRun()

result = search.run("Python 最新版本")
print(result)

# Tavily 搜索（需要 API Key，更适合 RAG）
tavily_api = TavilyAPIWrapper(api_key="your-tavily-api-key")
tavily_search = TavilySearchResults(api_wrapper=tavily_api)

results = tavily_search.run("2024年AI发展趋势")
print(results)
```

### 2. 计算工具

```python
from langchain_community.tools import ShellTool

# Shell 工具（执行 shell 命令）
shell_tool = ShellTool()

result = shell_tool.run("echo 'Hello World'")
print(result)

result = shell_tool.run("python -c 'print(2 + 2)'")
print(result)
```

### 3. 文件操作工具

```python
from langchain_community.tools import ReadFileTool, WriteFileTool

# 读取文件
read_tool = ReadFileTool()
content = read_tool.run("example.txt")

# 写入文件
write_tool = WriteFileTool()
write_tool.run({"file_path": "output.txt", "text": "Hello from LangChain!"})
```

### 4. Python REPL 工具

```python
from langchain_experimental.utilities import PythonREPL

# Python REPL 工具
python_repl = PythonREPL()

result = python_repl.run("print([x**2 for x in range(5)])")
print(result)  # [0, 1, 4, 9, 16]

result = python_repl.run("""
import math
print(math.sqrt(16))
""")
```

### 5. 数据库工具

```python
from langchain_community.utilities import SQLDatabase
from langchain_community.tools import QuerySQLDataBaseTool

# 连接数据库
db = SQLDatabase.from_uri("sqlite:///example.db")

# 查询工具
db_query_tool = QuerySQLDataBaseTool(db=db)

result = db_query_tool.run("SELECT * FROM users LIMIT 5")
print(result)
```

### 6. 推理工具

```python
from langchain.tools import Tool

# 自定义推理工具
def reasoning_tool(input_text: str) -> str:
    """执行复杂推理任务"""
    prompt = f"""
    请仔细分析以下陈述，判断其逻辑是否正确，并解释原因。

    陈述：{input_text}

    分析：
    """

    result = llm.invoke(prompt)
    return result.content

# 创建工具
reasoning = Tool(
    name="Reasoning",
    func=reasoning_tool,
    description="用于复杂逻辑推理和问题分析"
)
```

### 7. API 调用工具

```python
import requests

def weather_api(location: str) -> str:
    """获取天气信息"""
    # 使用免费的天气 API
    url = f"http://api.weatherapi.com/v1/current.json"
    params = {
        "key": "your-api-key",
        "q": location,
        "aqi": "no"
    }

    response = requests.get(url, params=params)
    data = response.json()

    return f"{location}当前天气：{data['current']['temp_c']}°C，{data['current']['condition']['text']}"

# 创建工具
weather = Tool(
    name="Weather",
    func=weather_api,
    description="获取指定地点的实时天气信息"
)

# 使用
print(weather.run("北京"))
```

## 自定义工具

### 基础自定义工具

```python
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import requests

# 定义输入模式
class WeatherInput(BaseModel):
    location: str = Field(description="城市名称，如'北京'、'上海'")

# 定义工具类
class WeatherTool(BaseTool):
    name = "Weather"
    description = "获取指定城市的实时天气信息"
    args_schema: Type[BaseModel] = WeatherInput

    def _run(self, location: str) -> str:
        # 同步运行
        api_key = "your-weather-api-key"
        url = f"http://api.weatherapi.com/v1/current.json"

        response = requests.get(
            url,
            params={"key": api_key, "q": location}
        )
        data = response.json()

        return f"{location}：{data['current']['temp_c']}°C，{data['current']['condition']['text']}"

    async def _arun(self, location: str) -> str:
        # 异步运行
        return self._run(location)

# 使用
weather_tool = WeatherTool()
result = weather_tool.run("广州")
print(result)
```

### 复杂自定义工具

```python
from typing import List
from pydantic import BaseModel, Field

class EmailInput(BaseModel):
    recipients: List[str] = Field(description="收件人邮箱列表")
    subject: str = Field(description="邮件主题")
    body: str = Field(description="邮件正文")

class EmailTool(BaseTool):
    name = "Email"
    description = "发送邮件给指定收件人"
    args_schema: Type[BaseModel] = EmailInput

    def _run(self, recipients: List[str], subject: str, body: str) -> str:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        # 创建邮件
        msg = MIMEMultipart()
        msg['From'] = "your-email@example.com"
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        # 发送邮件
        try:
            # 这里使用示例配置，实际使用时替换为真实 SMTP
            with smtplib.SMTP('smtp.example.com', 587) as server:
                server.starttls()
                server.login("your-email@example.com", "your-password")
                server.send_message(msg)

            return f"邮件已成功发送给 {len(recipients)} 个收件人"
        except Exception as e:
            return f"发送失败: {str(e)}"

# 使用
email_tool = EmailTool()
result = email_tool.run(
    recipients=["user1@example.com", "user2@example.com"],
    subject="会议通知",
    body="明天下午3点在会议室A开会。"
)
print(result)
```

### 组合工具

```python
from langchain.tools import StructuredTool

# 创建多个工具
tools = [
    WeatherTool(),
    SearchTool(),
    CalculatorTool(),
    EmailTool()
]

# 创建组合工具
combined_tool = StructuredTool.from_function(
    func=lambda query: self._execute_query(query, tools),
    name="MultiTool",
    description="执行多种操作，包括天气查询、搜索、计算和发送邮件"
)

def _execute_query(self, query: str, tools: List[BaseTool]) -> str:
    # 让 LLM 决定使用哪个工具
    tool_descriptions = "\\n".join([
        f"{tool.name}: {tool.description}"
        for tool in tools
    ])

    prompt = f"""
    根据以下工具描述，选择最适合处理以下请求的工具。

    工具列表：
    {tool_descriptions}

    请求：{query}

    只返回工具名称，不要其他内容。
    """

    tool_name = llm.invoke(prompt).content.strip()

    # 执行选定的工具
    for tool in tools:
        if tool.name == tool_name:
            return tool.run(query)

    return "未找到合适的工具"
```

## 工具优化技巧

### 工具描述优化

```python
# ❌ 不好的描述
bad_description = "计算器"

# ✅ 好的描述
good_description = """
执行数学计算，支持基础运算（加减乘除）和高级运算（三角函数、对数等）。
输入格式：数学表达式，如 "2 + 2", "sin(30)", "log(100)"
"""
```

### 工具参数验证

```python
from pydantic import validator

class CalculatorInput(BaseModel):
    expression: str = Field(description="要计算的数学表达式")

    @validator('expression')
    def validate_expression(cls, v):
        # 检查是否包含潜在危险的操作
        dangerous = ['__import__', 'exec', 'eval', 'open', 'file']
        if any(d in v for d in dangerous):
            raise ValueError("表达式包含不允许的操作")
        return v

class SafeCalculatorTool(BaseTool):
    name = "SafeCalculator"
    description = "安全的数学计算工具"
    args_schema: Type[BaseModel] = CalculatorInput

    def _run(self, expression: str) -> str:
        try:
            result = eval(expression, {'__builtins__': {}}, {
                'sin': __import__('math').sin,
                'cos': __import__('math').cos,
                'tan': __import__('math').tan,
                'log': __import__('math').log,
                'sqrt': __import__('math').sqrt,
            })
            return str(result)
        except Exception as e:
            return f"计算错误: {str(e)}"
```

### 工具错误处理

```python
class RobustTool(BaseTool):
    def _run(self, input_text: str) -> str:
        try:
            return self._execute(input_text)
        except ValueError as e:
            return f"输入错误: {str(e)}"
        except ConnectionError as e:
            return f"网络错误: {str(e)}"
        except Exception as e:
            # 记录详细错误日志
            import logging
            logging.error(f"Tool execution failed: {str(e)}")
            return f"执行失败，请稍后重试"

    def _execute(self, input_text: str) -> str:
        # 实际执行逻辑
        pass
```

### 工具缓存

```python
from functools import lru_cache
from hashlib import md5

class CachedTool(BaseTool):
    def __init__(self):
        super().__init__()
        self._cache = {}

    def _run(self, input_text: str) -> str:
        # 生成缓存键
        cache_key = md5(input_text.encode()).hexdigest()

        # 检查缓存
        if cache_key in self._cache:
            print("使用缓存结果")
            return self._cache[cache_key]

        # 执行并缓存
        result = self._execute(input_text)
        self._cache[cache_key] = result

        return result

    def clear_cache(self):
        self._cache = {}
```

## 工具集管理

```python
from langchain.agents import initialize_agent, Tool

# 创建工具集
tools = [
    Tool(
        name="Weather",
        func=lambda loc: f"{loc}的天气是晴天，25°C",
        description="获取指定城市的天气"
    ),
    Tool(
        name="Calculator",
        func=lambda expr: str(eval(expr)),
        description="执行数学计算，输入表达式"
    ),
    Tool(
        name="Search",
        func=lambda query: f"关于'{query}'的搜索结果...",
        description="搜索网络信息"
    )
]

# 初始化 agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent="zero-shot-react-description",
    verbose=True
)

# 使用 agent
result = agent.run("北京今天的天气如何？另外帮我计算2+3")
print(result)
```

## 小结

本节介绍了 LangChain Tools：

- **内置工具** - 搜索、计算、文件操作等
- **自定义工具** - 创建自己的工具
- **优化技巧** - 描述、验证、错误处理
- **工具集** - 管理多个工具

## 实践练习

### 编程题
1. 创建一个自定义 `StockTool`，接收股票代码返回实时价格（可以模拟）。要求：完整的 Pydantic 输入验证、错误处理和异步支持。
2. 将 3 个以上的工具注册到工具集中，编写一个测试脚本验证每个工具的描述和参数解析是否正确。

### 思考题
1. 工具描述（description）对 Agent 正确选择工具有多重要？设计一个好的工具描述应该包含哪些要素？
2. 在工具中直接使用 `eval()` 有什么安全风险？如何安全地实现计算工具？

### 自测题
1. 创建自定义 Tool 需要继承哪个基类？必须实现哪两个方法？
2. `args_schema` 的作用是什么？
3. 工具缓存应该在什么时候失效？

下一步将学习 LangChain Agents（→ `03-langchain-agents.md`）。