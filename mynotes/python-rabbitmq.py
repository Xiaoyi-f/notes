"""
WSGI（Web Server Gateway Interface） 是 Python 专门为 Web 应用定义的一套“翻译官协议”
Web 服务器（如 Gunicorn/Nginx）：说“底层网络语言”（监听端口、处理 TCP 连接）
Flask 代码：说“Python 函数语言”（处理请求、返回 JSON）
WSGI 就是它们之间的“同声传译官”，规定了两边怎么对话
gunicorn -w 4 app:app，这里的 Gunicorn 就是一个 WSGI 服务器。它的工作流程是：
Gunicorn 监听 5000 端口，收到 HTTP 请求
Gunicorn 把请求头、请求体、环境变量翻译成 Python 字典（environ）
Gunicorn 调用你的 Flask 应用（app），把字典传进去
Flask 执行完业务逻辑，返回一个 Python 对象（response）
Gunicorn 把 Python 对象翻译回 HTTP 响应，发回给客户端
"""

"""
使用场景:
  1.异步处理任务
  2.流量削峰填谷
  3.应用解耦与任务调度 
"""

# python中控制rabbitmq主要使用 celery库, 或者 pika库
# pika负责基础的消息发送和接收但是不关心内容和用途
# celery是一个强大的分布式任务队列框架, 它利用发动机入pika或者更加底层的库来驱动自己,但它的核心是管理和调度各种任务
# celery worker 需要单独使用命令启动单独进程执行消费者任务 
"""
celery --app 当前目录对应模块文件名(点号作为分隔符).celery_app worker --loglevel=debug / info / warning 
--concurrency 并发数  --> 默认--pool=prefetch需以管理员身份运行 或 --pool=solo 表示单进程模式 --pool=gevent 表示协程模式
"""

# pip install celery
from celery import Celery
from celery.schedules import crontab 
from celery.result impot AsyncResult

# Broker 消息代理服务器(中间人) 对应连接RabbitMQ
# Celery 消息代理服务器调度总部 管理层 
# Celery Worker 一个独立运行的操作系统进程 主要作为消费者调度者 
# AMQP 高级消息队列协议 
broker_url = f"amqp://{username}:{password}@{host}:{port}/{vhost}"
result_backend = f"redis://{password}@{host}:{port}/{db}"

# 创建一个管理总部 
celery_app = Celery("总部名字", broker=broker_url, backend=result_backend, include=["快递员名称"]) # include 导入任务函数

# 刷新配置
celery_app.conf.update(
    task_serializer="json", # 打包形式
    result_serializer="json", # 打包形式
    accept_content=["json"], # 只接收json格式数据 对应打包形式 
    result_backend=result_backend,
    task_ignore_result=False, # 扔掉回执单 任务执行后无需回传
    task_acks_late=True, # 任务执行完再确认 进程奔溃回投
    time_zone="Asia/Shanghai", # 国内北京时间 东八区
    enable_utc=True, # 使用UTC国际时间
    worker_prefetch_multiplier=1, # 一次只拿一件 
    broker_connection_retry_on_startup=True # 快递站没开门就等着 
)

# 定时任务
celery_app.beat_schedule = {
    "schedule_task_name": {
        "task": "task_name",
        "schedule": crontab(hour=8, minute=0), # 每天早上8点执行
        # "args": (), # 任务参数 可选 
        "kwargs": {} # 任务参数 可选
    }
}

QUEUE_TASK_MAP = {}

# 对下面工具进行风转为项目内工具函数 给要注册的任务函数使用 @celery_app.task(name="task_name")
# res 为 AsyncResult 对象
res = celery_app.send_task("task_name", args=(), kwargs={}, queue="queue_name")

def task_status(task_id):
    res = AsyncResult(task_id, app=celery_app)
    state = res.state

    if state == 'PENDING':
        return {"status": "PENDING", "message": "任务还在队列中等待，尚未被 Worker 领取"}
    
    elif state == 'STARTED':
        return {"status": "STARTED", "message": "Worker 正在执行中，请稍候..."}
    
    elif state == 'SUCCESS':
        # 获取返回值（就是你业务函数里的 return 内容）
        # 注意：如果任务函数没有 return，这里拿到的就是 None
        return {"status": "SUCCESS", "result": res.get(), "message": "执行成功！"}
    
    elif state == 'FAILURE':
        # 获取报错信息（堆栈跟踪）
        error_traceback = res.traceback
        return {"status": "FAILURE", "error": error_traceback, "message": "执行失败！"}
    
    elif state == 'RETRY':
        return {"status": "RETRY", "message": "任务正在重试中..."}
    
    else:
        return {"status": state, "message": f"未知状态: {state}"}

