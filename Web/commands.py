# 自定义flask命令清单
import click

from Web import app, db
from Web.models import User

# 创建用户数据库
@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')  # 设置选项
def initdb(drop):
    """Initialize the database."""
    if drop:  # drop选项用于重建数据库
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')  # 输出提示信息

# 生成若干用户测试数据
@app.cli.command()
def forge():
    db.create_all() # 数据库若存在则不会重建,若不存在则会建立.
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
