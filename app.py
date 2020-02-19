from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import os
import click
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'\
    + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控(暂时不知道用途)
db = SQLAlchemy(app)

#数据库模型
class User(db.Model):  # 表名将会是 user（自动生成，小写处理）
    id = db.Column(db.Integer, primary_key=True)  # 主键
    username = db.Column(db.String(20)) # 用户名 
    password_hash = db.Column(db.String(128)) # 密码散列

    # 密码与验证
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)



#路由修饰器
# 该路由仅用于展示,完成跳转到登录界面和注册界面的功能
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

#注册功能 警告信息用javascript实现更合适
@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    if request.method == 'POST': # 如果是提交表单
        username = request.form.get('user_name')
        password = request.form.get('user_password')
        password1 = request.form.get('user_password_1')
        if password!=password1: #密码验证失败
            flash('Two passwords do not match')
            return redirect(url_for('signup')) #重定向为注册页(可改进保留用户名)
        # 保存到数据库
        user = User(username = username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Success Signup!')
        return redirect(url_for('signin')) #重定向到登陆界面/可改进为直接登录
    # 如果不是post请求就返回模板
    return render_template('signup.html')

#登录功能
@app.route('/signin', methods = ['GET', 'POST'])
def signin():

    return render_template('signin.html')
#展示
@app.route('/welcome')
def welcome():

    return render_template('welcome.html')

#代码修饰器





#模板上下文
'''暂时不需要
@app.context_processor
def inject_user():
    users = User.query.all() #数据只有三个,此处查询所有用户并注入
    return users #这样做不确定是否可行
'''



# 注册flask命令
# 自动创建数据库
@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')  # 设置选项
def initdb(drop):
    """Initialize the database."""
    if drop:  # 判断是否输入了选项
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')  # 输出提示信息

#生成测试数据
@app.cli.command()
def forge():
    db.create_all()
    users = [
        {'username':'FanYx','password':'aaa'},
        {'username':'HuangWc','password':'aaa'},
        {'username':'HuWb','password':'aaa'}
    ]

    for u in users:
        user = User(username = u['username'])
        user.set_password(u['password'])
        db.session.add(user)

    db.session.commit()
    click.echo('Done')
