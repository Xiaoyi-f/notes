"""
项目文件夹规范
app.py 启动文件 
.env 环境变量  .env.example 环境变量示例
requirements.txt 依赖包文件 
utils 自定义工具 
routes 蓝图路由文件夹
db 数据库相关文件夹
config 配置文件夹
scripts 脚本文件夹 
agents agents文件夹 
rag rag文件夹 
"""

class Config:
    SECRET_KEY = "secret key" 
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://userName:password@url:port/dbName"
    SQLALCHEMY_TRACK_MODIFICATIONS = False 
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
    
from flask import Flask, jsonify, request, make_response, Blueprint, current_app 
from flask_cors import CORS
from sqlalchemy import and_, or_, not_, func
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import URLSafeTimedSerializer 
from functools import wraps 
import datetime 

app = Flask(__name__)
app.debug = False
# 签名传输的数据 记录下来
app.config.from_object('Config')
# 前后端不同源,不允许跨域携带凭证
CORS(app, supports_credentials=False, origins= [])  
# 后端生成并且返回Token之后应该立马存到前端

# 序列化实现Token 
serializer = URLSafeTimedSerializer(os.getenv("SECRET_KEY", salt="auth"))

# 依据用户账号生成token
serializer.dumps({"userAccount": userAccount})

# 验证Token 解密token 如果未过期、未被篡改 就返回 userAccount 否则返回 None
serializer.loads(token, max_age=xxx)["userAccount"]

# 通用规范: 注意websocket协议传递token要写在第一个url参数中

import jwt 

payload = {"userId": "userId", "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7), "iat": datetime.datetime.now(datetime.timezone.utc)}
token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")

try:
    payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
except jwt.ExpiredSignatureError:
    return None
except jwt.InvalidTokenError:
    return None
# token自动化装饰器 
def requireAuth(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization')
        token = auth.replace('Bearer ', '')
        userAccount = verifyToken(token)
        if not userAccount:
            return jsonify({"code": 401, "msg": "未登录或登录已过期"}), 401
        return func(*args, **kwargs)
    return decorated

xxxBp = Blueprint("xxx", __name__)

# 提示: 字典序 --> 从小到大 但是大写字母在小写字母之前 

@xxxBp.route("/xx", methods=["POST", "GET", "PUT", "DELETE"])
def demo():
    pass 

@app.before_request 
def beforeRequest():
    pass 

@app.after_request 
def afterRequest(resp):
    pass 

# 注册蓝图 
app.register_blueprint(xxxBp)

@app.route("/<int:num>/<float:decimal>/<string:name>", methods=["POST", "GET"])
def demo(num, decimal, name):
    """
    request.args.get("key", type=type) 字典 --> 查询参数 type->确保类型的转换 
    request.json 字典
    request.cookies 字典
    request.files 字典
    files[key].save("path")
    resp = make_response(data)

   '''
   后端在本次 HTTP 响应头里，添加一条 Set-Cookie 指令，命令浏览器在本地存储一条 Cookie 数据 
   之后浏览器每一次向指定域名发请求，都会自动把这条 Cookie 带给后端
   '''
   resp.set_cookie(
        "key",
        "value",
        max_age=2592000, # 单位: s
        domain="xxx.xx",
        samesite="Strict/Lax", # 跨站请求不带cookies 选择Strict模式或者Lax模式
        httponly=True, # 开启这个前端无法读取cookie，只能够通过后端来操作
        secure=True
    )

    return jsonify({"message": message, "data": data})
    """

# SSE 协议 
@app.route("/sse/xxx")
def xxx():
    def gen():
        yield f"data: {json.dumps({'status': 'connected'})}\n\n"
        yield f"event: eventName\n"
        yield f"data: {json.dumps({'data': 'data'})}\n\n"
    
    return Response(gen(), mimetype="text/event-stream")


# SQLAlchemy 技术 属于 ORM 技术(实现编程语言与数据库相连的中间件技术) 之一
db = SQLAlchemy()

def init(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

# 工具类 融合python使用时候调用 ORM对象.to_dict()
class BaseModel(db.Model):
    # 开启配置,该类不会被映射
    __abstract__ = True

    # 序列化ORM对象为py字典
    def to_dict(self):
        return {field.name: getattr(self, field.name) for field in self.__table__.c} # __table__.c -> columns 元信息

class Table(BaseModel):
    # 数据库内容采用蛇形命名规范
    __tablename__ = "table_name" 
    """
    # 可以手动传递第一个参数为字段名称 默认使用蛇形变量名作为字段名 
    field = db.Column(db.Integer, primary_key=True, autoincrement=True)
    db.BigInteger -> 针对于大量用户 
    ->
        db.String(n) unique=True nullable=False
        # ondelete= 'CASCADE' 表示级联删除 当对应的外键表行被删除 当前该行自动被删除 
        db.ForeignKey('table.field', ondelete='CASCADE') default=val --> 通过当前标的主键和外键表的主键进行一一对应
        db.Float db.Numeric(整体位数, 小数位数)-->需要使用float()进行转换为json形式 db.Boolean db.JSON(使用copy.deepcopy操作)

        db.DateTime --> python datetime 
        -- DateTime MySQL 类型实际存储格式 
        self.publishTime.isoformat() if self.publishTime else None
        示例:2026-5-31T14:30:45
        对象.year 
        对象.month
        对象.day
        对象.hour
        对象.minute
        对象.second

        db.Date --> python datetime 
        -- Date MySQL 类型实际存储格式 
        self.date.isoformat() if self.date else None 
        示例:2026-5-31
        对象.year 
        对象.month 
        对象.day 
    """

# 增
demo = Table(*args, **kwargs)
db.session.add(demo)
db.session.commit()

# 删
demo = Table.query.get(id)
db.session.delete(demo)
db.session.commit()

# 改
demo = Table.query.get(id)
demo.field = val
db.session.commit()

# 查
from sqlalchemy import func, and_, or_, not_ # func工具 和 用于ORM对象字段布尔表达式匹配的逻辑运算函数 and_(任意数量相关布尔表达式参数) or_(任意数量相关布尔表达式参数) not_(单个相关布尔表达式参数)
demo = Table.query.filter(Table.field布尔表达式).all() # .first() --> 没有对应的数据则返回空列表/空
demo = Table.query.filter(Table.field布尔表达式).order_by(func.random()).all()
demo = Table.query.get(字段) --> 用于外键和主键字段查询 

# 提交但是不永久保存 
db.session.flush() # 让数据"能被查到"，但还没"永久存下来"

# 测试
socket.run(app, host='0.0.0.0', port=5000)
# 对于不使用socket的项目
app.run(host='0.0.0.0', port=5000)
# 生产部署环境不要写这些，直接使用gunicorn管控
gunicorn -w 5 -b 0.0.0.0:5000 app:app # 普通模式 
gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 5 -b 0.0.0.0:5000 app:app # 协程模式

多进程（默认）: Gunicorn 默认采用 prefork 模型,启动时会复制出多个 Worker 进程（--workers=4 / -w 4）,每个进程独立监听端口,实现真正的并行处理请求
多线程（可选）: 如果指定 --threads=2,每个 Worker 进程内部会开启多个线程处理请求 --> 只有 -k gthread 开启多进程/多线程模式才可以配置--threads生效  

