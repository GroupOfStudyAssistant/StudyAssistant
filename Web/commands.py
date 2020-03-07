import click

from flaskweb import app, db
from flaskweb.models import User

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
    click.echo('Done.')
