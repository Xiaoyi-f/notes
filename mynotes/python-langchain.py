from langchain.agents import create_agent
from langchain.chat_models import init_chat_model 

// 具体配置相关API参考相关文档且问AI
model = init_chat_model(
  model="xxxmodel", 
  base_url="https://api.xxx.com", 
  api_key="api_key",
  temperature=0.7,
  max_tokens=1024,
  top_p=1.0,
  top_k=50,
  streaming=True
  )

system_prompt="""
# 身份
- 你是一个编程助手，你的名字是xiaoyi
# 指令
- 定义变量时,使用snake_case命名规则,而不是camelCase命名规则
- 不要返回markdown格式说明,只要返回代码即可
(巧妙使用各种提示词技巧)
"""

agent = create_agent(
  model=model,
  system_prompt=system_prompt,
  response_format=Demo 
)

langchain中LLM返回的消息统一被封装为BaseMessage,他是Agent中基本的上下文单元
SystemMessage -> role="system" (系统提示词)
HumanMessage -> role="user"
AIMessage -> role="assistant"
ToolMessage -> role="tool"

response = agent.invoke({
  "message": [
    SystemMessage(content="You are a helpful assistant."),
    HumanMessage(content="What is the meaning of life?"),
    AIMessage(content="The meaning of life is to live.")
  ]
})

# 多模态模型: 能同时接收、理解、生成多种不同数据类型数据的AI模型
message = HumanMessage(content=[
  {"type": "text", "text": "What is the meaning of life?"},
  {"type": "image", "url": "https://example.com/image.png"}
])

stream = agent.stream({
  "messages": [message]
}, stream_mode=True)

# 上传本地图片
1.上传本地图片
2.将图片转为base64格式
import base64 
img_bytes = bytes(img_content)
img_b64 = base64.b64encode(img_bytes).decode("utf-8")
HumanMessage(content=[
  {"type": "image", "base64": img_b64, "mime_type": "image/png"},
  {"type": "text", "text": "用文本描述这个图片"}
])

# dataclass只能标识类型但是不会校验,但是pydantic的BaseModel会校验
# pydantic通常用来做模型的结构化输出
from pydantic import BaseModel
class Demo(BaseModel):
    name: str
    location: str
    vibe: str 
# 拿取response["structured_response"]返回的就是Demo对象

# 工具使用
from langchain_core.tools import tool 

@tool
def tool(x):
    """
    Description
    ArgsDescription 
    """
    return x 

# langchain中预定义好的工具
# pip install langchain-tavily - 给AI用的Web搜索工具
from langchain_tavily import TavilySearch 
search_tool = TavilySearch(
  max_results=5,
  topic="general" # news, finance, technology, health, education, sports, entertainment, business, government, and more
)

@tool
def search(query):
    """Search the web for information"""
    return search_tool.invoke(query)

# 模型默认是无状态的,需要实现记忆
Agent记忆 短期记忆 长期记忆 
from langchain.agents.middleware import SummarizationMiddleware 
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver 
middleware = SummarizationMiddleware(
  model=model,
  trigger=("messages", 3), # 对话消息达到3条时进行压缩
  keep=("messages", 1) # 压缩的对话合并为一段
)
saver = InMemorySaver()
agent = create_agent(
  model=model,
  tools=[tool],
  middleware=[middleware]
  checkpointer=saver
)

# 一次连续对话使用同一个thread_id
agent.invoke(
  {"messages": [message]},
  {"configurable": {"thread_id": "xxx"}} 
)

# 删除对应线程的记忆 
saver.delete_thread("xxx")
# 获取某个线程最新快照数据
saver.get_tuple("xxx")

# 可以使用Postgre或其他数据库实现长期记忆,也可以使用Chroma/Milvus

# RAG 检索增强生成
基本阶段: 索引阶段 -> 检索阶段 -> 生成阶段 
向量是文本的数学身份证,一段文字的语义信息,转换为数字列表,让计算机能看懂"文字的含义并做相似度计算(余弦相似度等算法实现,n级维度/主题)"
维度越高语义化越明确,但是开销越大

# chain链: 将组件串联,上一个组件的输出作为下一个组件的输入
chain = model | component 
# 底层 | 调用 __or__ 重写类的 __or__ 即可实现管道 
# 前提: 只有Runnable/Callable、Mapping(字典父类)子类对象才能入链
chain.invoke(input)
chain.stream(input)

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.output_parsers import StrOutputParser 
chain = model | StrOutputParser() | model | JsonOutputParser() 

# 封装函数组件 
from langchain_core.runnables import RunnableLambda 
func = RunnableLambda(lambda ai_message: {"name": ai_message.content}) # 传普通函数亦可
chain = model | func | model 

# 文本加载与分割
from langchain_text_splitters import RecursiveCharacterTextSplitter 

loader = TextLoader(
  "xxx.txt",
  encoding="utf-8"
)

docs = loader.load()
splitter = RecursiveCharacterTextSplitter(
  chunk_size=500, # 分段的最大字符数
  chunk_overlap=50, # 允许前后段之间重叠的字符数
  separators=["\n\n", "\n", "！", "!", "？", "?", "。", ".", "，", ",", "；", ";", " ", ""],
  length_function=len
)

# 返回一个装着Document对象的列表
split_docs = splitter.split_documents(docs)

# 文档转向量与向量存储
# pip install chromadb 
from langchain_chroma import Chroma 

# 通过向量转换模型实现转向量
vector_store = Chroma(
  collection_name="xxx",
  embedding_function=Model(),
  persist_directory="path"
)

# 增加
vector_store.add_texts(["xxx", "xxx"])
vector_store.add_documents(
  documents=docs,
  ids=["id" + str(i) for i in range(1, len(docs) + 1)]
)

# 删除
vector_store.delete(["id1", "id2", ...])

# 检索
results = vector_store.similarity_search(
  query="检索内容/问题",
  k=3 # 检索的结果数
)

# 实现入链 手动转变形式/类型 利用字典封装入链 ...
retriever = vector_store.as_retriever(search_kwargs={"k": 2})
# 检索后获取结果进行提示词构建然后传递给ai

# 加载CSV文档
from langchain_community.document_loaders import CSVLoader 

loader = CSVLoader(
  file_path="path.csv",
  encoding="utf-8",
  source_column="字段名"
)
documents = loader.load()



