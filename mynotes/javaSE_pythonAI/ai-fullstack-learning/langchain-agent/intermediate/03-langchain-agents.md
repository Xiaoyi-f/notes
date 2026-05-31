# LangChain Agents 详解

## 什么是 Agent？

Agent 是能够自主决策的智能体，它根据用户的输入和可用工具，决定如何一步步完成任务。

## Agent 的核心概念

```python
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# Agent 的思考过程
"""
用户: "北京的天气如何？"

Agent思考:
1. 理解问题：用户想知道北京的天气
2. 检查工具：我有天气查询工具
3. 选择工具：Weather
4. 执行工具：Weather.run("北京")
5. 处理结果：将天气信息返回给用户
"""
```

## 1. ReAct Agent

### 基础 ReAct Agent

```python
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import Tool
from langchain_openai import ChatOpenAI

# 创建工具
def get_weather(location: str) -> str:
    """获取天气信息"""
    # 模拟天气数据
    weather_data = {
        "北京": "晴天，25°C",
        "上海": "多云，28°C",
        "广州": "小雨，30°C"
    }
    return weather_data.get(location, f"抱歉，没有{location}的天气信息")

tools = [
    Tool(
        name="Weather",
        func=get_weather,
        description="获取指定城市的天气信息"
    ),
    Tool(
        name="Calculator",
        func=lambda x: str(eval(x)),
        description="执行数学计算，输入数学表达式"
    )
]

# 创建 LLM
llm = ChatOpenAI(model="gpt-4", temperature=0)

# 创建 ReAct Agent
prompt = PromptTemplate.from_template("""
你是一个有用的助手。使用可用的工具来回答用户的问题。

可用工具：
{tools}

工具名称：{tool_names}

使用以下格式：
问题：你要回答的问题
思考：你应该如何思考来解决当前的问题
行动：要执行的工具，应该是 [{tool_names}] 之一
行动输入：执行工具所需的输入
观察：执行工具后得到的结果
...（可以重复思考/行动/行动输入/观察）
思考：我现在知道最终答案了
最终答案：原始问题的最终答案

开始！

问题：{input}
思考：{agent_scratchpad}
""")

agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True
)

# 使用 Agent
result = agent_executor.invoke({"input": "北京的天气如何？"})
print(result["output"])
```

### 自定义 ReAct Prompt

```python
# 中文版 ReAct Prompt
custom_react_prompt = PromptTemplate.from_template("""
你是一个专业的AI助手。根据用户的问题，使用提供的工具来找到答案。

工具列表：
{tools}

工具名称：{tool_names}

思考过程：
1. 理解用户的意图
2. 分析需要哪些信息
3. 选择合适的工具
4. 执行工具并分析结果
5. 如果需要，重复以上步骤
6. 给出最终答案

回答格式：
思考: [你的思考过程]
行动: [工具名称]
行动输入: [工具输入]
观察: [工具输出]
...（重复直到获得足够信息）
最终答案: [你的最终回答]

当前问题：{input}

历史思考：{agent_scratchpad}
""")

agent = create_react_agent(llm, tools, custom_react_prompt)
```

## 2. 不同类型的 Agent

### Zero Shot ReAct Agent

```python
from langchain.agents import initialize_agent, AgentType, load_tools

# 自动选择工具，不需要示例
tools = load_tools(["llm-math"], llm=llm)

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

result = agent.run("3529的平方根是多少？")
```

### Conversational Agent

```python
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory

# 支持多轮对话的 Agent
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

tools = [
    Tool(
        name="Calculator",
        func=lambda x: str(eval(x)),
        description="执行数学计算"
    )
]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,
    verbose=True
)

# 多轮对话
agent.run("2+2等于多少？")
agent.run("刚才的计算结果加3是多少？")  # 会记得之前的答案
```

### Structured Chat Agent

```python
from langchain.agents import initialize_agent, AgentType, StructuredChatAgent, AgentExecutor
from langchain.schema import SystemMessage

# 支持结构化输入的 Agent
system_message = SystemMessage(content=(
    "你是一个专业的助手。使用提供的工具来完成任务。"
))

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    agent_kwargs={"system_message": system_message}
)
```

### OpenAI Functions Agent

```python
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI

# 使用 OpenAI Function Calling
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0
)

tools = [
    Tool(
        name="Weather",
        func=get_weather,
        description="获取指定城市的天气"
    )
]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True
)
```

## 3. Agent 配置与优化

### 动态工具选择

```python
from typing import List, Dict

class DynamicToolAgent:
    def __init__(self, llm):
        self.llm = llm
        self.all_tools = {
            "weather": get_weather,
            "calculator": lambda x: str(eval(x)),
            "search": self._search,
        }

    def _select_tools(self, query: str) -> List[Tool]:
        """根据查询选择合适的工具"""
        prompt = f"""
        根据以下问题，选择需要的工具。可用工具：
        - weather: 天气查询
        - calculator: 数学计算
        - search: 信息搜索

        问题：{query}

        返回工具名称，用逗号分隔：
        """

        result = self.llm.invoke(prompt)
        selected_names = result.content.strip().split(", ")

        tools = []
        for name in selected_names:
            if name in self.all_tools:
                tools.append(Tool(
                    name=name,
                    func=self.all_tools[name],
                    description=f"{name}工具"
                ))

        return tools

    def run(self, query: str) -> str:
        """运行 Agent"""
        tools = self._select_tools(query)

        agent = initialize_agent(
            tools=tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=False
        )

        return agent.run(query)

# 使用
agent = DynamicToolAgent(llm)
result = agent.run("北京天气如何？")
```

### Agent 迭代优化

```python
from langchain.callbacks import get_openai_callback

def optimize_agent(agent, test_cases, iterations=5):
    """优化 Agent 表现"""
    results = []

    for i in range(iterations):
        print(f"\\n=== 迭代 {i + 1} ===")

        iteration_results = []
        with get_openai_callback() as cb:
            for case in test_cases:
                try:
                    result = agent.run(case["input"])
                    success = case["expected"] in result
                    iteration_results.append({
                        "input": case["input"],
                        "result": result,
                        "success": success
                    })
                except Exception as e:
                    iteration_results.append({
                        "input": case["input"],
                        "error": str(e),
                        "success": False
                    })

        success_rate = sum(r["success"] for r in iteration_results) / len(iteration_results)
        total_cost = cb.total_cost

        print(f"成功率: {success_rate:.2%}")
        print(f"总成本: ${total_cost:.4f}")

        results.append({
            "iteration": i + 1,
            "success_rate": success_rate,
            "cost": total_cost,
            "results": iteration_results
        })

        # 根据结果调整 agent（这里简化处理）
        if success_rate < 0.8:
            print("成功率较低，调整工具描述...")
            # 实际应用中可以在这里优化工具描述或提示词

    return results
```

### Agent 并发执行

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class ConcurrentAgent:
    def __init__(self, agent, max_workers=5):
        self.agent = agent
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    async def run_batch(self, queries: List[str]) -> List[str]:
        """批量执行查询"""
        loop = asyncio.get_event_loop()
        tasks = []

        for query in queries:
            task = loop.run_in_executor(
                self.executor,
                self.agent.run,
                query
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        return results

# 使用
concurrent_agent = ConcurrentAgent(agent)

queries = [
    "北京天气如何？",
    "2+2等于多少？",
    "搜索Python最新版本",
    "计算100的阶乘",
    "上海天气如何？"
]

results = asyncio.run(concurrent_agent.run_batch(queries))
for query, result in zip(queries, results):
    print(f"Q: {query}")
    print(f"A: {result}\\n")
```

## 4. 高级 Agent 模式

### Router Agent

```python
from langchain.agents import initialize_agent, AgentType
from langchain.prompts import PromptTemplate

# 创建专门化 agents
weather_agent = initialize_agent(
    tools=[Tool(name="Weather", func=get_weather, description="天气查询")],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION
)

calculator_agent = initialize_agent(
    tools=[Tool(name="Calculator", func=lambda x: str(eval(x)), description="数学计算")],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION
)

# Router prompt
router_prompt = PromptTemplate.from_template("""
根据以下问题，选择最合适的专家助手：

1. 天气助手 - 处理天气相关问题
2. 计算助手 - 处理数学计算问题

问题：{input}

只返回专家名称（天气助手/计算助手）：
""")

def route_query(query: str):
    """路由查询到合适的 agent"""
    # 使用 LLM 选择 agent
    choice = llm.invoke(router_prompt.format(input=query)).content.strip()

    if "天气" in choice:
        return weather_agent.run(query)
    elif "计算" in choice:
        return calculator_agent.run(query)
    else:
        return llm.invoke(query).content

# 使用
print(route_query("北京天气如何？"))
print(route_query("2+2等于多少？"))
```

### Hierarchical Agent

```python
# 分层 Agent 架构
"""
用户请求
    ↓
Manager Agent（负责决策和任务分配）
    ↓
├── Researcher Agent（负责研究和信息收集）
├── Analyst Agent（负责分析和计算）
└── Writer Agent（负责撰写和格式化）
    ↓
Manager 汇总结果
    ↓
最终答案
"""

class ManagerAgent:
    def __init__(self):
        self.researcher = ResearcherAgent()
        self.analyst = AnalystAgent()
        self.writer = WriterAgent()

    def process(self, query: str) -> str:
        """处理用户请求"""
        # 1. 分析任务类型
        task_type = self._analyze_task(query)

        # 2. 分配任务
        if task_type == "research":
            research_result = self.researcher.run(query)
            analysis_result = self.analyst.analyze(research_result)
            return self.writer.write(analysis_result)

        elif task_type == "analysis":
            analysis_result = self.analyst.analyze(query)
            return self.writer.write(analysis_result)

        else:
            return self.writer.write(query)

    def _analyze_task(self, query: str) -> str:
        """分析任务类型"""
        # 简化实现
        if "研究" in query or "搜索" in query:
            return "research"
        elif "分析" in query or "计算" in query:
            return "analysis"
        return "general"

class ResearcherAgent:
    def run(self, query: str) -> str:
        """研究查询"""
        # 实际应用中调用搜索工具
        return f"关于'{query}'的研究结果..."

class AnalystAgent:
    def analyze(self, data: str) -> str:
        """分析数据"""
        # 实际应用中执行分析
        return f"分析结果：{data}"

class WriterAgent:
    def write(self, content: str) -> str:
        """撰写答案"""
        # 实际应用中格式化输出
        return f"最终答案：\\n{content}"
```

### Multi-Agent Collaboration

```python
from typing import List, Dict
import asyncio

class CollaborativeAgent:
    def __init__(self, agents: List):
        self.agents = agents

    async def collaborate(self, query: str, rounds: int = 2) -> str:
        """多轮协作"""
        current_input = query
        history = []

        for round_num in range(rounds):
            print(f"\\n=== 协作轮次 {round_num + 1} ===")

            # 每个 agent 处理
            tasks = []
            for agent in self.agents:
                task = agent.process(current_input)
                tasks.append(task)

            # 并行执行
            results = await asyncio.gather(*tasks)

            # 汇总结果
            summary = self._summarize_results(results)
            history.append({
                "round": round_num + 1,
                "results": results,
                "summary": summary
            })

            # 更新输入
            current_input = summary

        return current_input

    def _summarize_results(self, results: List[str]) -> str:
        """汇总结果"""
        summary_prompt = f"""
        汇总以下多个专家的意见：

        {chr(10).join([f"专家{i+1}: {result}" for i, result in enumerate(results)])}

        给出一个综合性的总结：
        """

        return llm.invoke(summary_prompt).content

# 使用
agent1 = WeatherAgent()
agent2 = CalculatorAgent()
agent3 = ResearchAgent()

collaborative = CollaborativeAgent([agent1, agent2, agent3])
result = asyncio.run(collaborative.collaborate("帮我分析北京今天的天气对户外活动的影响"))
```

## 小结

本节介绍了 LangChain Agents：

- **ReAct Agent** - 基础 Agent
- **不同类型** - Zero Shot, Conversational, Structured
- **配置优化** - 动态工具、迭代优化
- **高级模式** - Router, Hierarchical, Collaboration

## 实践练习

### 编程题
1. 创建一个具有 3 个工具（搜索、计算、天气）的 ReAct Agent，并用 5 个不同类型的查询测试它能否正确选择工具。
2. 实现一个 Router Agent，将用户请求自动分发到 3 个专业子 Agent，并汇总结果返回。

### 思考题
1. ReAct Agent 的"思考-行动-观察"循环有什么优缺点？什么情况下会陷入死循环？
2. Multi-Agent 协作中，如何处理 Agent 之间的信息冲突？

### 自测题
1. ReAct 模式的四个步骤是什么？
2. `handle_parsing_errors=True` 的作用是什么？
3. Conversational Agent 和普通 Agent 的核心区别是什么？

下一步将学习 LangChain 生产部署（→ `04-langchain-production.md`）。