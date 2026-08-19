# LangChain 基础入门

## 什么是 LangChain？

LangChain 是一个用于构建由大语言模型(LLM)驱动的应用程序的框架。它提供了一套工具和抽象，让开发者能够轻松构建复杂的 AI 应用。

### 核心组件

1. **LLMs（大语言模型）** - 调用语言模型
2. **Prompts（提示词）** - 管理和优化提示词
3. **Chains（链）** - 将多个组件串联起来
4. **Agents（代理）** - 让 LLM 决定下一步行动
5. **Memory（记忆）** - 维护会话状态
6. **Tools（工具）** - Agent 可以使用的功能

## 安装 LangChain

```bash
# 基础安装
pip install langchain langchain-core

# 社区扩展（包含各种工具）
pip install langchain-community

# OpenAI 集成
pip install langchain-openai

# 其他可选包
pip install langchain-anthropic    # Claude
pip install langchain-cohere       # Cohere
pip install langchain-google-genai # Google Gemini
```

## 环境配置

```python
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 设置 API Key
os.environ["OPENAI_API_KEY"] = "your-openai-api-key"
os.environ["ANTHROPIC_API_KEY"] = "your-anthropic-api-key"

# 或者直接设置
import getpass
os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")
```

## 1. LLM 基础使用

### 基础 LLM 调用

```python
from langchain_openai import ChatOpenAI

# 初始化模型
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.7,
    max_tokens=1000,
    api_key=os.environ["OPENAI_API_KEY"]
)

# 简单调用
response = llm.invoke("Hello, how are you?")
print(response.content)

# 带参数调用
response = llm.invoke(
    "写一首关于春天的诗",
    temperature=0.9,  # 更有创造性
    max_tokens=200
)
```

### 支持的模型

```python
# OpenAI 模型
from langchain_openai import ChatOpenAI

gpt4 = ChatOpenAI(model="gpt-4")
gpt4_turbo = ChatOpenAI(model="gpt-4-turbo-preview")
gpt35 = ChatOpenAI(model="gpt-3.5-turbo")

# Anthropic Claude
from langchain_anthropic import ChatAnthropic

claude = ChatAnthropic(model="claude-3-sonnet-20240229")
claude_opus = ChatAnthropic(model="claude-3-opus-20240229")

# Google Gemini
from langchain_google_genai import ChatGoogleGenerativeAI

gemini = ChatGoogleGenerativeAI(model="gemini-pro")

# Hugging Face
from langchain_huggingface import HuggingFaceEndpoint

llama = HuggingFaceEndpoint(
    repo_id="meta-llama/Meta-Llama-3-8B-Instruct",
    huggingfacehub_api_token="your-token"
)
```

## 2. 提示词管理

### PromptTemplate

```python
from langchain.prompts import PromptTemplate

# 创建简单模板
template = "告诉我关于{topic}的信息"
prompt = PromptTemplate.from_template(template)

# 格式化提示词
formatted_prompt = prompt.format(topic="机器学习")
print(formatted_prompt)

# 在 LLM 中使用
response = llm.invoke(prompt.format(topic="机器学习"))
```

### ChatPromptTemplate

```python
from langchain.prompts import ChatPromptTemplate
from langchain.prompts.chat import SystemMessagePromptTemplate, HumanMessagePromptTemplate

# 创建聊天提示模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的{role}助手。"),
    ("human", "{user_input}")
])

# 格式化
messages = prompt.format_messages(
    role="编程",
    user_input="如何定义一个Python函数？"
)

response = llm.invoke(messages)
```

### Few-Shot Prompting

```python
from langchain.prompts.few_shot import FewShotPromptTemplate
from langchain.prompts.prompt import PromptTemplate

# 定义示例
examples = [
    {
        "question": "1+1=?",
        "answer": "2"
    },
    {
        "question": "10-5=?",
        "answer": "5"
    },
    {
        "question": "2*3=?",
        "answer": "6"
    }
]

# 创建示例提示模板
example_prompt = PromptTemplate(
    input_variables=["question", "answer"],
    template="问题: {question}\\n答案: {answer}"
)

# 创建 Few-Shot 提示模板
few_shot_prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix="以下是几个数学计算的例子：",
    suffix="\\n问题: {input}\\n答案:",
    input_variables=["input"]
)

# 使用
prompt = few_shot_prompt.format(input="4*5+3=?")
response = llm.invoke(prompt)
```

### Prompt 优化技巧

```python
# 1. 明确的角色定义
system_prompt = """
你是一个经验丰富的Python开发工程师，拥有10年以上的开发经验。
你的回答应该：
1. 准确且专业
2. 包含代码示例
3. 解释最佳实践
4. 指出常见陷阱
"""

# 2. 输出格式规范
output_format_prompt = """
请按照以下格式回答：

## 问题分析
...

## 解决方案
```python
代码
```

## 注意事项
1. ...
2. ...
"""

# 3. 思维链提示
cot_prompt = """
让我们一步步思考这个问题：

步骤1: 理解问题
步骤2: 分析需求
步骤3: 设计方案
步骤4: 实现代码
步骤5: 验证结果

请按照以上步骤回答：{question}
"""
```

## 3. Output Parsers（输出解析器）

### 基础解析器

```python
from langchain.output_parsers import CommaSeparatedListOutputParser
from langchain.prompts import PromptTemplate

# 创建逗号分隔列表解析器
parser = CommaSeparatedListOutputParser()

# 获取格式说明
format_instructions = parser.get_format_instructions()

# 创建提示词
prompt = PromptTemplate(
    template="列出五个{subject}。\\n{format_instructions}",
    input_variables=["subject"],
    partial_variables={"format_instructions": format_instructions}
)

# 使用
formatted_prompt = prompt.format(subject="编程语言")
response = llm.invoke(formatted_prompt)

# 解析输出
result = parser.parse(response.content)
print(result)  # ['Python', 'JavaScript', 'Java', 'C++', 'Go']
```

### JSON 解析器

```python
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List

# 定义输出模型
class ProgrammingLanguage(BaseModel):
    name: str = Field(description="编程语言名称")
    year: int = Field(description="发明年份")
    creator: str = Field(description="创造者")
    features: List[str] = Field(description="主要特性")

# 创建解析器
parser = PydanticOutputParser(pydantic_object=ProgrammingLanguage)

# 获取格式说明
format_instructions = parser.get_format_instructions()

# 创建提示词
prompt = PromptTemplate(
    template="提供Python编程语言的详细信息。\\n{format_instructions}",
    input_variables=[],
    partial_variables={"format_instructions": format_instructions}
)

# 使用
formatted_prompt = prompt.format()
response = llm.invoke(formatted_prompt)

# 解析输出
result = parser.parse(response.content)
print(result.name)      # Python
print(result.year)      # 1991
print(result.creator)   # Guido van Rossum
print(result.features)  # ['简洁易读', '动态类型', ...]
```

### 结构化输出解析器

```python
from langchain.output_parsers import StructuredOutputParser, ResponseSchema

# 定义响应模式
response_schemas = [
    ResponseSchema(
        name="summary",
        description="文本摘要",
        type="string"
    ),
    ResponseSchema(
        name="keywords",
        description="关键词列表",
        type="array"
    ),
    ResponseSchema(
        name="sentiment",
        description="情感倾向（正面/负面/中性）",
        type="string"
    )
]

# 创建解析器
output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

# 获取格式说明
format_instructions = output_parser.get_format_instructions()

# 使用
prompt = PromptTemplate(
    template="分析以下文本：\\n{input_text}\\n\\n{format_instructions}",
    input_variables=["input_text"],
    partial_variables={"format_instructions": format_instructions}
)

formatted_prompt = prompt.format(input_text="今天天气真好，我很开心！")
response = llm.invoke(formatted_prompt)

# 解析输出
result = output_parser.parse(response.content)
print(result["summary"])     # 表达了积极的情绪
print(result["keywords"])    # ['天气', '开心']
print(result["sentiment"])   # 正面
```

## 4. Chains（链）

### SimpleChain

```python
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# 创建提示模板
prompt = PromptTemplate(
    input_variables=["product", "audience"],
    template="为{product}写一个面向{audience}的广告文案。"
)

# 创建链
chain = LLMChain(
    llm=llm,
    prompt=prompt
)

# 执行链
result = chain.invoke({
    "product": "智能手表",
    "audience": "健身爱好者"
})

print(result["text"])
```

### Sequential Chain

```python
from langchain.chains import SimpleSequentialChain

# 第一个链：生成故事大纲
story_outline_prompt = PromptTemplate(
    input_variables=["topic"],
    template="为'{topic}'创作一个简短的故事大纲。"
)
story_outline_chain = LLMChain(
    llm=llm,
    prompt=story_outline_prompt
)

# 第二个链：根据大纲写故事
story_prompt = PromptTemplate(
    input_variables=["outline"],
    template="根据以下大纲写一个完整的故事：\\n{outline}"
)
story_chain = LLMChain(
    llm=llm,
    prompt=story_prompt
)

# 创建顺序链
combined_chain = SimpleSequentialChain(
    chains=[story_outline_chain, story_chain],
    verbose=True  # 显示中间步骤
)

# 执行
result = combined_chain.invoke("时间旅行")
print(result["output"])
```

### Router Chain

```python
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains.router import MultiPromptChain
from langchain.chains.router.llm_router import LLMRouterChain, RouterOutputParser

# 定义不同场景的提示词
physics_template = """
你是一个物理专家。请回答以下物理问题：
{input}
"""

math_template = """
你是一个数学专家。请回答以下数学问题：
{input}
"""

history_template = """
你是一个历史专家。请回答以下历史问题：
{input}
"""

# 创建不同领域的链
physics_chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate.from_template(physics_template)
)

math_chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate.from_template(math_template)
)

history_chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate.from_template(history_template)
)

# 定义路由提示
router_template = """
请将以下问题分类为：物理、数学、历史之一。

问题：{input}

只返回分类结果，不要其他内容。
"""

# 创建路由链
router_prompt = PromptTemplate.from_template(router_template)
router_chain = LLMRouterChain.from_llm(
    llm=llm,
    prompt=router_prompt
)

# 创建多提示词链
chain = MultiPromptChain(
    router_chain=router_chain,
    destination_chains={
        "物理": physics_chain,
        "数学": math_chain,
        "历史": history_chain
    },
    default_chain=LLMChain(llm=llm, prompt=PromptTemplate.from_template("{input}"))
)

# 使用
result = chain.invoke("E=mc²是什么意思？")
print(result["text"])
```

## 5. Memory（记忆）

### ConversationBufferMemory

```python
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

# 创建对话记忆
memory = ConversationBufferMemory()

# 创建对话链
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

# 第一轮对话
response1 = conversation.predict(input="我叫小明")
print(response1)

# 第二轮对话（会记住之前的信息）
response2 = conversation.predict(input="我叫什么名字？")
print(response2)  # 会正确回答"小明"

# 查看记忆内容
print(memory.load_memory_variables({}))
```

### ConversationBufferWindowMemory

```python
from langchain.memory import ConversationBufferWindowMemory

# 只保留最近的K轮对话
window_memory = ConversationBufferWindowMemory(k=2)

conversation = ConversationChain(
    llm=llm,
    memory=window_memory
)

# 进行多轮对话
conversation.predict(input="第一轮")
conversation.predict(input="第二轮")
conversation.predict(input="第三轮")
conversation.predict(input="第四轮")

# 只会记住第三轮和第四轮
print(window_memory.load_memory_variables({}))
```

### ConversationSummaryMemory

```python
from langchain.memory import ConversationSummaryMemory

# 自动总结对话历史
summary_memory = ConversationSummaryMemory(llm=llm)

conversation = ConversationChain(
    llm=llm,
    memory=summary_memory,
    verbose=True
)

# 长对话会自动被总结
for i in range(5):
    conversation.predict(input=f"问题{i}")
```

### 自定义记忆

```python
from langchain.memory import BaseMemory
from typing import Dict, Any

class CustomMemory(BaseMemory):
    def __init__(self):
        self.memories = {}

    @property
    def memory_variables(self) -> list:
        return ["custom_memory"]

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, str]:
        return {"custom_memory": str(self.memories)}

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]):
        self.memories[inputs.get("input", "")] = outputs.get("response", "")

    def clear(self):
        self.memories = {}

# 使用自定义记忆
custom_memory = CustomMemory()
conversation = ConversationChain(
    llm=llm,
    memory=custom_memory
)
```

## 小结

本节介绍了 LangChain 的基础组件：

- **LLMs** - 模型调用
- **Prompts** - 提示词管理
- **Output Parsers** - 输出解析
- **Chains** - 组件串联
- **Memory** - 对话记忆

## 实践练习

### 编程题
1. 使用 `PydanticOutputParser` 创建一个输出解析器，让 LLM 输出包含"主题、关键词、摘要"三个字段的结构化 JSON。
2. 实现一个 `RouterChain`，根据用户问题自动路由到"编程助手"、"数学助手"或"通用助手"，每个助手使用不同的 System Prompt。

### 思考题
1. `ConversationBufferMemory` 和 `ConversationSummaryMemory` 各适合什么场景？在长对话中应该如何选择？
2. Few-Shot Prompting 的示例数量和多样性对输出质量有什么影响？

### 自测题
1. LangChain 的六大核心组件是什么？
2. `PromptTemplate` 和 `ChatPromptTemplate` 的区别是什么？
3. `SequentialChain` 和 `RouterChain` 的使用场景有何不同？

下一步将学习 LangChain Tools（→ `02-langchain-tools.md`）。