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

# python中控制rabbitmq主要使用 celery库, 或者 pika库
# pika负责基础的消息发送和接收但是不关心内容和用途
# celery是一个强大的分布式任务队列框架, 它利用发动机入pika或者更加底层的库来驱动自己,但它的核心是管理和调度各种任务



