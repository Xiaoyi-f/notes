import json 
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

import aio_pika

# connection = await aio_pika.connect_robust(
#   "amqp://user_name:password@ip_address:port/vhost"
# )

# RabbitMQ 是一款开源、基于 AMQP 协议的消息中间件（Message Broker），提供异步消息队列能力
# 对于 flask/django(WSGI模型) 使用 同步方式的 rabbitmq SDK --> pika 
# 对于 fastapi(ASGI模型) 使用 异步方式的 rabbitmq SDK --> aio_pika 
# pip install pika / aio_pika 
# 开启rabbitmq服务 -> 先安装 Erlang依赖 -> 再安装 rabbitmq 搜索相关使用命令管理服务 / 直接使用 docker镜像(建议)

import pika 

# RabbitMQ 是一个消息代理，它可以在同一台服务器上为多个不同的项目或环境提供服务。为了避免不同项目之间的队列、交换机互相干扰，RabbitMQ 引入了 vhost 的概念
# 浏览器访问 http://localhost:15672，默认账号密码都是 guest
credentials = pika.PlainCredentials('user_name', 'password')
parameters = pika.ConnectionParameters('ip_address', port, 'vhost', credentials)
# connection = pika.BlockingConnection(parameters)

# 定义任务函数 
def task(args):
    pass 

# 定义生产者
def publish_xxx_task(args):
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel() # TCP连接上创建虚拟通道

    # 声明队列 durable=True 表示消息持久化
    channel.queue_declare(queue='xxx_task_queue', durable=True)

    # 构造消息体
    message = json.dumps({
      'args': args 
    })

    # 发送消息 
    channel.basic_publish(
      exchange='', # 默认交换机 
      routing_key='xxx_task_queue', # 使用默认交换机时必须使用队列名
      body=message.encode("utf-8"),
      properties=pika.BasicProperties(
        delivery_mode=2 # 2 表示消息持久化
      )
    )

    connection.close() 
    print(f"[xxx_task] 任务 已入队: xxxx")

# 定义消费者 从任务队列取任务并真正执行
from tasks import task # 导入自己写的任务函数 

def callback(channel, method, properties, body):
    data = json.loads(body.decode()) # 字典 消息体  

    print(f"[xxx_task] 任务 准备执行: xxxx")

    try:
        task(data['args']) 
        channel.basic_ack(delivery_tag=method.delivery_tag) # 手动告诉 RabbitMQ 消息处理完 可以删除 
        print(f"[xxx_task] 任务 已完成: xxxx")
    except Exception as err:
        print(f"[xxx_task] 任务执行失败 发生错误: {err}")    

def main():
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel() # TCP连接上创建虚拟通道

    # 创建任务队列
    channel.queue_declare(queue='xxx_task_queue', durable=True)

    # 每次只取一条消息,处理完再取下一条 
    channel.basic_qos(prefetch_count=1)

    # 创建消费者
    channel.basic_consume(queue='xxx_task_queue', on_message_callback=callback, auto_ack=False)

    print(f"[*] 正在监听任务队列: xxxx")
    channel.start_consuming()



