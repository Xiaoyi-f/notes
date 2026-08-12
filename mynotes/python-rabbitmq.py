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

# import aio_pika # --> FastAPI 使用

# connection = await aio_pika.connect_robust(
#   "amqp://user_name:password@ip_address:port/vhost"
# )

# RabbitMQ 是一款开源、基于 AMQP 协议的消息中间件（Message Broker），提供异步消息队列能力
# 对于 flask/django(WSGI模型) 使用 同步方式的 rabbitmq SDK --> pika
# 对于 fastapi(ASGI模型) 使用 异步方式的 rabbitmq SDK --> aio_pika
# pip install pika / aio_pika
# 开启rabbitmq服务 -> 先安装 Erlang依赖 -> 再安装 rabbitmq 搜索相关使用命令管理服务 / 直接使用 docker镜像(建议)

import json
import os
import threading
import pika
from dotenv import load_dotenv

load_dotenv()

class MQClient:
    """
    RabbitMQ 客户端单例，负责管理与 RabbitMQ 服务器的连接。
    所有生产者和消费者复用同一个连接，避免频繁创建/销毁 TCP 连接。
    """
    _connection = None

    @classmethod
    def get_connection(cls):
        """获取全局唯一的连接实例，如果连接断开则自动重连"""
        if cls._connection is None or cls._connection.is_closed:
            # pika底层有is_closed
            credentials = pika.PlainCredentials(
                os.getenv("RABBITMQ_USER", "guest"),
                os.getenv("RABBITMQ_PASSWORD", "guest")
            )
            params = pika.ConnectionParameters(
                host=os.getenv("RABBITMQ_IP", "localhost"),
                port=int(os.getenv("RABBITMQ_PORT", 5672)),
                virtual_host=os.getenv("RABBITMQ_VHOST", "/"),
                credentials=credentials,
                heartbeat=600  # 保持长连接
            )
            cls._connection = pika.BlockingConnection(params)
        return cls._connection


def publish_task(queue_name: str, task_data: dict):
    """
    生产者：将任务发布到指定队列

    :param queue_name: 队列名称（建议与消费者使用相同名称）
    :param task_data: 任务参数字典，会被序列化为 JSON 发送
    """
    conn = MQClient.get_connection()
    channel = conn.channel()
    # 声明队列（持久化）
    channel.queue_declare(queue=queue_name, durable=True)
    # 发布消息
    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=json.dumps(task_data, ensure_ascii=False).encode('utf-8'),
        properties=pika.BasicProperties(
            delivery_mode=2  # 消息持久化
        )
    )
    print(f"[{queue_name}] 任务已入队: {task_data}")


def start_consumer(queue_name: str, task_func):
    """
    消费者：启动一个阻塞式消费者，处理指定队列中的任务

    :param queue_name: 队列名称
    :param task_func: 业务处理函数，接收字典参数（即 task_data 解包后的键值对）
    """
    def callback(chan, method, properties, body):
        # 四个固定参数
        data = json.loads(body.decode())
        print(f"[{queue_name}] 收到任务，开始执行")
        try:
            # 将字典解包为关键字参数传递给业务函数
            task_func(**data)
            chan.basic_ack(delivery_tag=method.delivery_tag)  # 手动确认
            print(f"[{queue_name}] 任务执行成功")
        except Exception as err:
            print(f"[{queue_name}] 任务执行失败: {err}")
            # 根据业务需求决定是否重试（requeue=True 会重新入队 手动实现重试限制）
            chan.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    conn = MQClient.get_connection()
    channel = conn.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_qos(prefetch_count=1)          # 每次只取一条消息
    channel.basic_consume(
        queue=queue_name,
        on_message_callback=callback,
        auto_ack=False
    )
    print(f"[*] 开始监听队列: {queue_name}")
    channel.start_consuming()   # 阻塞，直到被中断


def start_background_consumer(queue_name: str, task_func):
    """
    :param queue_name: 队列名称
    :param task_func: 业务处理函数
    """
    thread = threading.Thread(
        target=start_consumer,
        args=(queue_name, task_func),
        daemon=True   # 主线程退出时自动终止
    )
    thread.start()
    print(f"[{queue_name}] 消费者已在后台启动")

