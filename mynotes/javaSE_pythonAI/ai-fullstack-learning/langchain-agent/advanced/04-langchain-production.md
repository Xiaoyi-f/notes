# LangChain 生产部署指南

## 1. API 服务封装

### FastAPI 封装

```python
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import logging

app = FastAPI(title="LangChain Agent API", version="1.0.0")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 请求/响应模型
class AgentRequest(BaseModel):
    query: str
    agent_type: str = "zero-shot"
    session_id: Optional[str] = None
    tools: Optional[List[str]] = None

class AgentResponse(BaseModel):
    answer: str
    session_id: str
    tools_used: List[str]
    latency_ms: float
    token_usage: dict

# Agent 工厂
class AgentFactory:
    def __init__(self):
        self.agents = {}
        self.agent_types = {
            "zero-shot": self._create_zero_shot_agent,
            "conversational": self._create_conversational_agent,
            "structured": self._create_structured_agent
        }

    def get_agent(self, agent_type: str, session_id: Optional[str] = None):
        """获取或创建 Agent"""
        cache_key = f"{agent_type}_{session_id or 'default'}"

        if cache_key not in self.agents:
            self.agents[cache_key] = self.agent_types[agent_type]()

        return self.agents[cache_key]

    def _create_zero_shot_agent(self):
        """创建 Zero Shot Agent"""
        from langchain.agents import initialize_agent, AgentType
        from langchain.tools import Tool

        tools = [
            Tool(
                name="Calculator",
                func=lambda x: str(eval(x)),
                description="执行数学计算"
            ),
            Tool(
                name="Weather",
                func=self._get_weather,
                description="查询天气"
            )
        ]

        return initialize_agent(
            tools=tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=False
        )

    def _create_conversational_agent(self):
        """创建对话 Agent"""
        from langchain.agents import initialize_agent, AgentType
        from langchain.memory import ConversationBufferMemory

        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

        # ... 工具定义 ...

        return initialize_agent(
            tools=tools,
            llm=self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=memory,
            verbose=False
        )

    def _get_weather(self, location: str) -> str:
        """天气查询（示例）"""
        return f"{location}今天晴天，25°C"

# 全局 Agent 工厂
agent_factory = AgentFactory()

@app.post("/agent/run", response_model=AgentResponse)
async def run_agent(request: AgentRequest):
    """运行 Agent"""
    import time

    start_time = time.time()

    try:
        # 获取 Agent
        agent = agent_factory.get_agent(request.agent_type, request.session_id)

        # 执行查询
        with get_openai_callback() as cb:
            result = agent.run(request.query)

            # 计算指标
            latency_ms = (time.time() - start_time) * 1000
            token_usage = {
                "total_tokens": cb.total_tokens,
                "prompt_tokens": cb.prompt_tokens,
                "completion_tokens": cb.completion_tokens,
                "total_cost": cb.total_cost
            }

        return AgentResponse(
            answer=result,
            session_id=request.session_id or "default",
            tools_used=[],
            latency_ms=latency_ms,
            token_usage=token_usage
        )

    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 启动服务
if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
```

### WebSocket 实时通信

```python
from fastapi import WebSocket, WebSocketDisconnect
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_message(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)

manager = ConnectionManager()

@app.websocket("/ws/agent/{session_id}")
async def websocket_agent(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)

    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            message = json.loads(data)

            # 处理请求
            response = await process_agent_request(
                query=message.get("query", ""),
                agent_type=message.get("agent_type", "zero-shot"),
                session_id=session_id
            )

            # 发送响应
            await manager.send_message(session_id, response)

    except WebSocketDisconnect:
        manager.disconnect(session_id)

async def process_agent_request(query: str, agent_type: str, session_id: str):
    """处理 Agent 请求"""
    agent = agent_factory.get_agent(agent_type, session_id)

    with get_openai_callback() as cb:
        result = agent.run(query)

        return {
            "type": "response",
            "answer": result,
            "token_usage": {
                "total_tokens": cb.total_tokens,
                "cost": cb.total_cost
            }
        }
```

## 2. 监控与追踪

### LangSmith 集成

```python
import os
from langchain_openai import ChatOpenAI

# 配置 LangSmith
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-langsmith-api-key"
os.environ["LANGCHAIN_PROJECT"] = "my-rag-project"

# LLM 自动追踪
llm = ChatOpenAI(model="gpt-4")
result = llm.invoke("Hello")

# 查看追踪：访问 https://smith.langchain.com
```

### 自定义追踪

```python
from langchain.callbacks import BaseCallbackHandler
import time
from typing import Any, Dict, List

class DetailedTracingHandler(BaseCallbackHandler):
    """详细的追踪处理器"""

    def __init__(self):
        self.traces = []

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs
    ) -> None:
        """LLM 开始时"""
        self.traces.append({
            "event": "llm_start",
            "timestamp": time.time(),
            "model": serialized.get("name", "unknown"),
            "prompts": prompts
        })

    def on_llm_end(self, response, **kwargs) -> None:
        """LLM 结束时"""
        self.traces[-1]["event"] = "llm_end"
        self.traces[-1]["tokens_used"] = response.llm_output.get("token_usage", {})
        self.traces[-1]["duration"] = time.time() - self.traces[-1]["timestamp"]

    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs):
        """工具开始时"""
        self.traces.append({
            "event": "tool_start",
            "timestamp": time.time(),
            "tool": serialized.get("name", "unknown"),
            "input": input_str
        })

    def on_tool_end(self, output: str, **kwargs):
        """工具结束时"""
        self.traces[-1]["event"] = "tool_end"
        self.traces[-1]["output"] = output
        self.traces[-1]["duration"] = time.time() - self.traces[-1]["timestamp"]

    def get_traces(self):
        """获取追踪记录"""
        return self.traces

# 使用追踪器
tracing_handler = DetailedTracingHandler()

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    callbacks=[tracing_handler]
)

result = agent_executor.invoke({"input": "查询天气"})

# 查看追踪
for trace in tracing_handler.get_traces():
    print(f"{trace['event']}: {trace}")
```

### 性能监控

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

# 定义指标
agent_requests = Counter('agent_requests_total', 'Total agent requests', ['agent_type', 'status'])
agent_duration = Histogram('agent_duration_seconds', 'Agent execution duration', ['agent_type'])
active_sessions = Gauge('agent_active_sessions', 'Number of active sessions')
token_usage = Histogram('agent_tokens_used', 'Tokens used per request', ['agent_type'])

class MonitoredAgent:
    def __init__(self, agent, agent_type: str):
        self.agent = agent
        self.agent_type = agent_type

    def run(self, query: str) -> str:
        """运行并监控 Agent"""
        start_time = time.time()
        status = "success"

        try:
            active_sessions.inc()
            agent_requests.labels(agent_type=self.agent_type, status="started").inc()

            result = self.agent.run(query)

            # 记录指标
            duration = time.time() - start_time
            agent_duration.labels(agent_type=self.agent_type).observe(duration)
            agent_requests.labels(agent_type=self.agent_type, status="success").inc()

            return result

        except Exception as e:
            status = "error"
            agent_requests.labels(agent_type=self.agent_type, status="error").inc()
            raise

        finally:
            active_sessions.dec()

# 启动 metrics 服务器
start_http_server(9090)

# 使用
monitored_agent = MonitoredAgent(agent, "zero-shot")
result = monitored_agent.run("查询天气")
```

## 3. 错误处理与重试

### 智能重试

```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
import logging

logger = logging.getLogger(__name__)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((ConnectionError, TimeoutError)),
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
async def safe_llm_call(llm, prompt: str) -> str:
    """安全的 LLM 调用，带重试"""
    response = await llm.ainvoke(prompt)
    return response.content

# 使用
result = await safe_llm_call(llm, "你的问题")
```

### 降级策略

```python
class AgentFallback:
    def __init__(self):
        self.primary_agent = self._create_primary_agent()
        self.fallback_agent = self._create_fallback_agent()

    async def run_with_fallback(self, query: str) -> str:
        """带降级的执行"""
        try:
            return await self.primary_agent.arun(query)
        except Exception as e:
            logger.warning(f"Primary agent failed: {e}, using fallback")
            try:
                return await self.fallback_agent.arun(query)
            except Exception as e:
                logger.error(f"Fallback agent also failed: {e}")
                return "抱歉，服务暂时不可用，请稍后重试。"
```

## 4. 缓存策略

### Redis 缓存

```python
import redis
import json
import hashlib
from functools import wraps

class AgentCache:
    def __init__(self, redis_url="redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url)
        self.ttl = 3600  # 1小时

    def _get_cache_key(self, agent_type: str, query: str) -> str:
        """生成缓存键"""
        hash_obj = hashlib.md5(f"{agent_type}:{query}".encode())
        return f"agent:{agent_type}:{hash_obj.hexdigest()}"

    def get(self, agent_type: str, query: str) -> Optional[str]:
        """获取缓存"""
        key = self._get_cache_key(agent_type, query)
        cached = self.redis_client.get(key)
        if cached:
            return json.loads(cached)
        return None

    def set(self, agent_type: str, query: str, result: str):
        """设置缓存"""
        key = self._get_cache_key(agent_type, query)
        self.redis_client.setex(
            key,
            self.ttl,
            json.dumps(result)
        )

def cached_agent_run(cache: AgentCache):
    """装饰器：缓存 Agent 运行结果"""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, query: str, *args, **kwargs):
            # 尝试从缓存获取
            agent_type = self.__class__.__name__
            cached = cache.get(agent_type, query)
            if cached:
                logger.info(f"Cache hit for query: {query}")
                return cached

            # 执行查询
            result = await func(query, *args, **kwargs)

            # 缓存结果
            cache.set(agent_type, query, result)

            return result
        return wrapper
    return decorator

# 使用
cache = AgentCache()

class CachedAgent:
    @cached_agent_run(cache)
    async def run(self, query: str) -> str:
        # 实际执行逻辑
        return self.agent.run(query)
```

## 5. 安全与认证

### API Key 管理

```python
from fastapi import Header, HTTPException, Depends
import jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

def create_access_token(data: dict):
    """创建访问令牌"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """验证令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(authorization: str = Header(...)):
    """获取当前用户"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.split(" ")[1]
    payload = verify_token(token)
    return payload

@app.post("/agent/run")
async def run_agent(
    request: AgentRequest,
    current_user: dict = Depends(get_current_user)
):
    """需要认证的 Agent 端点"""
    # 检查用户权限
    if not current_user.get("permissions", {}).get("agent:run", False):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    # 执行 Agent
    result = agent.run(request.query)
    return {"answer": result}
```

## 小结

本节介绍了 LangChain 生产部署：

- **API 封装** - FastAPI, WebSocket
- **监控追踪** - LangSmith, 自定义追踪
- **错误处理** - 重试, 降级
- **缓存策略** - Redis 缓存
- **安全认证** - JWT, API Key

## 实践练习

### 编程题
1. 基于 FastAPI 封装一个带 JWT 认证的 Agent API，包含速率限制（rate limiting）和请求日志。
2. 使用 LangSmith 追踪一个 Agent 的完整执行过程，分析哪一步耗时最长。

### 思考题
1. 在生产环境中，Agent 的 Token 消耗成本如何控制和优化？
2. 当 Agent 调用失败时，降级策略应该如何设计？

### 自测题
1. LangSmith 主要用于什么目的？
2. 断路器模式中 `failure_threshold` 和 `recovery_timeout` 分别控制什么？
3. 为什么推荐使用 `tenacity` 库而不是手动写重试逻辑？

下一步将学习知识图谱技术（→ `knowledge-graph/beginner/01-knowledge-graph-basics.md`）。