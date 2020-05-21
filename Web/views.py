# 视图函数文件

from flask import render_template, url_for, request, redirect, flash
from flask_login import login_user, login_required, logout_user, current_user

from Web import app, db
from Web.models import User
# from BuildIndex.app import vec
import pymysql, json



# 该路由仅用于展示,完成跳转到登录界面和注册界面的功能
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

#注册功能 警告信息用javascript实现更合适
@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    if request.method == 'POST': # 提交表单会发送POST请求
        username = request.form.get('user_name')
        password = request.form.get('user_password')
        password1 = request.form.get('user_password_1')

        if not username or not password or not password1: # 某字段为空的处理
            flash('Invalid input.')
            return redirect(url_for('signup'))

        userexist = User.query.filter_by(username = username).count() # 判断用户是否存在
        if userexist:
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

    if request.method == 'POST': # 提交表单会发送POST请求
        username = request.form['user_name']
        password = request.form['user_password']
        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('signin'))
        
        userexist = User.query.filter_by(username = username).count()
        user = User.query.filter_by(username = username).first()
        #验证密码
        if userexist == 1 and username == user.username and user.validate_password(password):
            login_user(user) #登入
            flash('Login success.')
            return redirect(url_for('welcome'))

        flash('Invalid username or password.')
        return redirect(url_for('signin'))

    return render_template('signin.html')

# 相当于使用一个路由完成登出的功能,比较浪费,最好用js做
@app.route('/signout')
@login_required
def signout():
    logout_user()
    flash('Signout success.')
    return redirect(url_for('index'))



######## 核心功能
from Web.proc_txt4srch import get_concepts,get_relations,get_moocs,get_prereqs
#搜索页
@app.route('/welcome', methods = ['GET', 'POST']) # 允许使用get和post方式发送搜索请求.
@login_required  #可以考虑把用户登陆限制去掉
def welcome(): 
    concepts = [{'_source': {'concept': '机器学习', 'definition': '''机器学习是一门多领域交叉学科，涉及概率论、统计学、逼近论、凸分析、算法复杂度理论等多门学科。
        专门研究计算机怎样模拟或实现人类的学习行为，以获取新的知识或技能，重新组织已有的知识结构使之不断改善自身的性能。
        它是人工智能的核心，是使计算机具有智能的根本途径。'''}}]
    relations = []
    moocs = []
    prereqs = {"_source": {}}
    bbb= []

    if request.method == 'POST':  # POST请求表示提交表单
        textforsearch = request.form.get("keywords")
    else: # get请求从requests中获取参数
        textforsearch = request.args.get('search', '') # 默认值为空

    if textforsearch.strip(): # 如果不是是空白字符才进行检索处理
        concepts = get_concepts(textforsearch)
        relations, bbb = get_relations(textforsearch)
        #print(relations)
        moocs = get_moocs(textforsearch)
        prereqs = get_prereqs(textforsearch) # 得到的是我们认为和搜索词最接近的uni_course的数据

    return render_template('welcome.html', concepts = concepts, relations = relations, moocs = moocs, textforsearch = textforsearch, prereqs = prereqs,bbb = bbb)

