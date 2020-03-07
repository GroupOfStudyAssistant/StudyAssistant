from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from flaskweb import db

#数据库模型
class User(db.Model, UserMixin):  # 表名将会是 user（自动生成，小写处理）
    id = db.Column(db.Integer, primary_key=True)  # 主键
    username = db.Column(db.String(20)) # 用户名 
    password_hash = db.Column(db.String(128)) # 密码散列

    # 密码与验证
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)
