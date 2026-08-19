# 生产级 LangChain Agent 系统实战

## 一、项目概述

构建一个智能客服 Agent 系统，支持多工具调用、记忆管理、人工兜底，包含完整的监控与追踪体系。

### 技术栈

| 组件 | 选型 | 说明 |
|------|------|------|
| Agent 框架 | LangChain + LangGraph | 状态图驱动 |
| LLM | GPT-4o / Claude 3.5 | 复杂推理 |
| 工具执行 | Docker Sandbox | 安全沙箱 |
| 追踪 | LangSmith / MLflow | 全链路追踪 |
| 记忆 | Redis + Postgres | 短期+长期记忆 |
| 部署 | Kubernetes | 弹性扩缩 |

## 二、系统架构

```
┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
│  多渠道接入   │────▶│  Agent 编排  │────▶│  工具执行层      │
│  Web/微信/API │     │  LangGraph   │     │  Docker Sandbox  │
└──────────────┘     └──────┬───────┘     └──────────────────┘
                            │
                    ┌───────┴───────┐
                    │  记忆管理层    │
                    │ Redis+Postgres│
                    └───────┬───────┘
                            │
                    ┌───────┴───────┐
                    │  监控追踪      │
                    │ LangSmith     │
                    └───────────────┘
```

## 三、Agent 实现

### LangGraph 状态图

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import operator

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next_step: str
    tools_result: dict
    human_intervention: bool

def should_continue(state: AgentState) -> Literal["tools", "human", "end"]:
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.get("tool_calls"):
        return "tools"
    if state.get("human_intervention"):
        return "human"
    return "end"

# 构建状态图
graph = StateGraph(AgentState)
graph.add_node("agent", call_agent)
graph.add_node("tools", execute_tools)
graph.add_node("human", human_review)
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", should_continue)
graph.add_edge("tools", "agent")
graph.add_edge("human", "agent")
```

### Agent 智能体

```python
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

class CustomerServiceAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.1,
            streaming=True
        )
        self.tools = self._init_tools()
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """你是智能客服助手，遵循以下原则：
1. 态度友好专业
2. 不确定时引导转人工
3. 涉及个人信息时必须验证身份
4. 敏感操作需要用户二次确认"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        self.agent = create_openai_functions_agent(
            llm=self.llm, tools=self.tools, prompt=self.prompt
        )

    def _init_tools(self):
        from langchain_community.tools import (
            DuckDuckGoSearchRun, YouTubeSearchTool
        )
        return [
            DuckDuckGoSearchRun(),
            OrderQueryTool(),       # 查订单
            TicketCreateTool(),     # 创建工单
            RefundQueryTool(),      # 查退款
            KnowledgeBaseTool(),    # 知识库检索
        ]
```

### 自定义工具实现

```python
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Type

class OrderQueryInput(BaseModel):
    order_id: str = Field(description="订单号")
    user_id: str = Field(description="用户ID（需验证）")

class OrderQueryTool(BaseTool):
    name = "order_query"
    description = "查询订单状态，需要订单号和用户ID"
    args_schema: Type[BaseModel] = OrderQueryInput

    def _run(self, order_id: str, user_id: str) -> str:
        """查询订单状态"""
        # 调用订单系统 API
        order = query_order_api(order_id, user_id)
        if not order:
            return "未找到订单"
        return f"订单 {order_id} 状态：{order['status']}，金额：{order['amount']}"

class TicketCreateTool(BaseTool):
    name = "create_ticket"
    description = "创建客服工单，提交到工单系统"

    def _run(self, category: str, description: str, priority: str = "P3") -> str:
        ticket_id = create_ticket_api(category, description, priority)
        return f"工单已创建，编号：{ticket_id}"
```

## 四、记忆系统

```python
from langchain.memory import PostgresChatMessageHistory
from langchain_community.chat_message_histories import RedisChatMessageHistory
import json

class HybridMemory:
    """分层记忆：短期Redis + 长期Postgres"""

    def __init__(self, session_id: str, user_id: str):
        self.session_id = session_id
        self.user_id = user_id
        # 短期记忆（30min过期）
        self.short_term = RedisChatMessageHistory(
            session_id=session_id,
            url="redis://localhost:6379/0",
            ttl=1800
        )
        # 长期记忆（持久化）
        self.long_term = PostgresChatMessageHistory(
            session_id=user_id,
            connection_string="postgresql://user:pass@localhost:5432/memory"
        )

    def add_message(self, message: dict):
        self.short_term.add_message(message)
        self.long_term.add_message(message)

    def get_context(self, k: int = 10) -> str:
        """获取最近k轮对话作为上下文"""
        recent = self.short_term.messages[-k:]
        summary = self._summarize_long_term()
        return {
            "recent": recent,
            "user_summary": summary
        }

    def _summarize_long_term(self) -> str:
        """从长期记忆中提取用户画像"""
        history = self.long_term.messages
        if len(history) < 50:
            return ""
        # 用LLM提取用户偏好、常见问题
        summary_prompt = f"提取用户特征：{history[-100:]}"
        return llm.invoke(summary_prompt)
```

## 五、安全与兜底

### 输入安全过滤

```python
import re

class SafetyGuard:
    """输入安全过滤器"""

    SENSITIVE_PATTERNS = [
        r"\d{18}",           # 身份证号
        r"1[3-9]\d{9}",      # 手机号
        r"\d{16}",           # 信用卡号
    ]

    BLOCKED_KEYWORDS = [
        "sql注入", "delete from", "drop table",
        "<script>", "javascript:"
    ]

    @classmethod
    def validate_input(cls, text: str) -> tuple[bool, str]:
        # 脱敏检查
        for pattern in cls.SENSITIVE_PATTERNS:
            if re.search(pattern, text):
                return False, "输入包含敏感信息"
        # 注入检查
        for keyword in cls.BLOCKED_KEYWORDS:
            if keyword.lower() in text.lower():
                return False, "输入包含非法内容"
        return True, ""

    @classmethod
    def sanitize_output(cls, text: str) -> str:
        """输出脱敏"""
        for pattern in cls.SENSITIVE_PATTERNS:
            text = re.sub(pattern, "****", text)
        return text
```

### 人工兜底

```python
class HumanHandoff:
    """转人工策略"""

    HANDOFF_TRIGGERS = [
        "投诉", "赔偿", "退款到不了",
        "人工客服", "转人工",
        "你不行", "听不懂",
    ]

    @classmethod
    def should_handoff(cls, message: str, agent_confidence: float) -> bool:
        if agent_confidence < 0.4:
            return True
        for trigger in cls.HANDOFF_TRIGGERS:
            if trigger in message:
                return True
        return False

    @classmethod
    def create_handoff_ticket(cls, session_id: str, context: dict):
        """创建转人工工单"""
        ticket = {
            "source": "ai_agent",
            "session_id": session_id,
            "summary": cls._summarize_conversation(context),
            "priority": "P1" if "投诉" in context else "P2"
        }
        dispatch_to_human_agent(ticket)
```

## 六、监控与追踪

### LangSmith 追踪

```python
from langsmith import Client, traceable
from langsmith.run_trees import RunTree

# 配置 LangSmith
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "customer-service-agent"

@traceable(run_type="chain", name="agent_pipeline")
def agent_pipeline(input_text: str, user_id: str):
    run_tree = RunTree(
        name="CustomerServiceAgent",
        inputs={"question": input_text}
    )
    try:
        result = agent.invoke(input_text)
        run_tree.end(outputs=result)
        return result
    except Exception as e:
        run_tree.end(error=str(e))
        raise
```

### 业务监控指标

```python
from prometheus_client import Counter, Histogram

agent_calls = Counter("agent_calls_total", "Agent 调用次数", ["status", "tool"])
agent_latency = Histogram("agent_latency_seconds", "Agent 响应延迟", buckets=[1, 3, 5, 10, 30])
handoff_rate = Counter("human_handoff_total", "转人工次数", ["reason"])
tool_failures = Counter("tool_failures_total", "工具调用失败", ["tool_name"])
```

## 七、K8s 部署

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: customer-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: customer-agent
  template:
    metadata:
      labels:
        app: customer-agent
    spec:
      containers:
      - name: agent
        image: registry/agent:latest
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: llm-keys
              key: openai-api-key
        - name: REDIS_URL
          value: redis://redis-service:6379
        resources:
          limits:
            cpu: "2"
            memory: 4Gi
          requests:
            cpu: "500m"
            memory: 1Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: customer-agent-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: customer-agent
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## 八、面试考点

1. **LangGraph 相比 LCEL 的优势？** 支持循环、条件分支、人工介入，适合复杂多步任务
2. **如何避免 Agent 陷入死循环？** 设置最大迭代次数（5-10轮）+ 超时兜底 + 人工阈值
3. **工具调用的可靠性如何保证？** 重试机制（指数退避）+ 结果校验 + 降级策略
4. **多 Agent 协作模式？** Supervisor Agent 调度 Specialist Agent，通过 Message Queue 通信

## 九、课后练习

1. 实现一个 Agent 工具调用重试机制，失败 3 次后转人工
2. 为 Agent 添加 Reflection 机制：在返回前自我评估答案质量
3. 实现 LangGraph 的并行节点：同时调用多个独立工具
4. 对接企业微信/飞书消息通道，实现多渠道接入

## 自测题

1. LangGraph 的节点间数据传递方式？ A) 全局变量 B) 状态字典 C) 数据库 D) 消息队列
2. ReAct 模式中，"Thought-Action-Observation" 循环的目的？ A) 减少 LLM 调用 B) 逐步推理并观察结果 C) 多轮对话 D) 缓存
3. Agent 记忆管理中，短期记忆通常使用？ A) Redis TTL B) MySQL C) 文件 D) S3

**答案：** 1-B, 2-B, 3-A
