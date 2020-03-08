import os
import sys

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

#应用设置
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'\
    + os.path.join(os.path.dirname(app.root_path), 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控(暂时不知道用途)
# 拓展类
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'signin' #未登录视图保护的重定向端点

@login_manager.user_loader
def load_user(user_id): #用户加载回调函数,具体意义不明
    from Web.models import User
    user = User.query.get(int(user_id))
    return user

#模板上下文
'''暂时不需要
@app.context_processor
def inject_user():
    from Web.models import User
    users = User.query.all() #数据只有三个,此处查询所有用户并注入
    return users #这样做不确定是否可行
'''

# 将视图函数、命令函数注册到程序实例上
from Web import views, commands