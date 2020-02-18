from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import click

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'\
    + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控(暂时不知道用途)
db = SQLAlchemy(app)

#数据库模型
class User(db.Model):  # 表名将会是 user（自动生成，小写处理）
    id = db.Column(db.Integer, primary_key=True)  # 主键
    name = db.Column(db.String(20))  # 名字



#路由修饰器
@app.route('/', methods=['GET', 'POST'])
def index():
    # 该路由仅用于展示,完成跳转到登录界面和注册界面的功能
    return render_template('index.html')


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

@app.cli.command()
def forge():
    #生成测试数据
    db.create_all()
    users = [
        {'name':'FanYx'},
        {'name':'HuangWc'},
        {'name':'HuWb'}
    ]

    for u in users:
        user = User(name = u['name'])
        db.session.add(user)

    db.session.commit()
    click.echo('Done')

