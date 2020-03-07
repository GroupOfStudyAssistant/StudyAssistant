from flask import render_template, url_for, request, redirect, flash
from flask_login import login_user, login_required, logout_user, current_user

from flaskweb import app, db
from flaskweb.models import User

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

        if not username or not password or not password1:
            flash('Invalid input.')
            return redirect(url_for('signup'))       

        userexist = User.query.filter_by(username = username).count()
        if userexist: #用户名已经存在
            flash('Username Occupied!')
            return redirect(url_for('signup'))
        if password!=password1: #密码验证失败
            flash('Two passwords do not match.')
            return redirect(url_for('signup')) #重定向为注册页(可改进保留用户名)
        # 保存到数据库
        user = User(username = username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Success Signup!')
        login_user(user)
        return redirect(url_for('welcome')) #直接登录

    # 如果不是post请求就返回模板
    return render_template('signup.html')

#登录功能
@app.route('/signin', methods = ['GET', 'POST'])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for('welcome'))

    if request.method == 'POST':
        username = request.form['user_name']
        password = request.form['user_password']
        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('signin'))
        
        user = User.query.filter_by(username = username).first()
        userexist = User.query.filter_by(username = username).count()
        #验证密码
        if userexist == 1 and username == user.username and user.validate_password(password):
            login_user(user) #登入
            flash('Login success.')
            return redirect(url_for('welcome'))
        flash('Invalid username or password.')
        return redirect(url_for('signin'))

    return render_template('signin.html')
    
#展示
@app.route('/welcome')
@login_required
def welcome():
    return render_template('welcome.html')

@app.route('/signout')
@login_required
def signout():
    logout_user()
    flash('Signout success.')
    return redirect(url_for('index'))
