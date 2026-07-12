"""
项目文件夹规范
app.py 启动文件 
.env 环境变量  .env.example 
requirements.txt 依赖包文件 
util 自定义工具 
route 蓝图路由文件夹
db 数据库相关文件夹
service 特殊服务功能文件夹
script 脚本文件夹 
"""

class Config:
    SECRET_KEY = "secret key" 
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://userName:password@url:port/dbName"
    SQLALCHEMY_TRACK_MODIFICATIONS = False 
    
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
# 前后端不同源,允许跨域携带凭证
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
   后端在本次 HTTP 响应头里，添加一条 Set-Cookie 指令，命令浏览器在本地存储一条 Cookie 数据 
   之后浏览器每一次向指定域名发请求，都会自动把这条 Cookie 带给后端
    resp.set_cookie(
        "key",
        "value",
        max_age=2592000, # 单位: s
        domain="xxx.xx",
        samesite="Strict/Lax", # 跨站请求不带cookies
        httponly=True, # 开启这个前端无法读取cookie，只能够通过后端来操作
        secure=True
    )
    """

# SQLAlchemy 技术 属于 ORM 技术(实现编程语言与数据库相连的中间件技术) 之一
db = SQLAlchemy()
db.init_app(app) 

# 表名默认就是类名小写 如果是驼峰命名的话，默认就是使用_(下划线隔离)
class Table(db.Model):
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

    def toDict(self):
        data = {
            "xx": self.xx 
        }
        
        return data 

with app.app_context():
    db.create_all()

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
demo = Table.query.filter(Table.field布尔表达式).all() # .first() --> 没有对应的数据则返回空列表/空
demo = Table.query.filter(Table.field布尔表达式).order_by(func.random()).all()
demo = Table.query.get(字段) --> 用于外键和主键字段查询 

# 提交但是不永久保存 
db.session.flush() 让数据"能被查到"，但还没"永久存下来"

# python中使用时候可以直接使用SQLAlchemy对象，但是传递数据时候不能够传递SQLAlchemy对象

# 测试
socket.run(app, host='0.0.0.0', port=5000)
# 对于不使用socket的项目
app.run(host='0.0.0.0', port=5000)
# 生产部署环境不要写这些，直接使用gunicorn管控
gunicorn -w 5 -b 0.0.0.0:5000 app:app
gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 5 -b 0.0.0.0:5000 app:app
