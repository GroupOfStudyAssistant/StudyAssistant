网站开发文档与使用文档.
(需要按照软件工程的要求书写)







### 使用web展示内容

使用flask框架实现web架构. 

后台逻辑使用python实现, 连接数据库.

范围初步限于计算机科学领域.

及时总结.

20200126

20200218

"/"路由对应欢迎界面,提供注册和登录的链接.

"/signup"路由对应注册界面, 提供注册功能,将用户输入添加到数据库, 并重定向到"/welcome"路由

"/signin"路由对应登录界面, 提供登录功能, 验证用户输入, 重定向到"/welcome"路由

"/welcome”路由对应登录后的界面, 进行内容的展示.(可以考虑与首页合并, 设计不同的视图.)
提供登出选项, 重定向到"/"



20200219

前端样式需要调整.
暂时不加入邮箱信息.(验证比较复杂,需要后期设计)
request.form.get()方法从post请求中获取表格数据,但是需要传入的参数为input标签的name属性值

> name 属性规定 input 元素的名称。
>
> name 属性用于对提交到服务器后的表单数据进行标识，或者在客户端通过 JavaScript 引用表单数据。只有设置了 name 属性的表单元素才能在提交表单时传递它们的值。

注册时会验证数据库中是否已经有用户名,因此用户名是唯一的.(但对于应用中声明的数据库模型类来说没有设置为主键)

SQLAlchemy的查询操作文档无法访问,如果要使用该数据库封装方案,则必须了解文档.

链接跳转时需要使用url_for函数以及jinja变量嵌入


未登录用户不能执行以下操作:
不能进入welcome界面(welcome路由)
不能登出(进入signout路由)
登录用户不能进行以下操作:
不能进入index路由(暂时)
不能登录.

#### 主要工作:

使用url_for修改链接目标. 组织模板继承和优化.
完成用户数据库与用户注册登录模块.
设计路由与模板的用户认证保护.

#### 未完成的:

应用结构文档和使用文档(感觉暂时不需要,因为只是个样品)
模块化测试.(20200223基本完成)
代码结构组织(代码都堆到app.py里边肯定不是长久之计)
部署上线

20200211待完善:

1. 标签页的样式（感觉是和landingpage的样式有冲突）
2. 关闭网页时自动logout（否则再次打开无signin signup按钮，只有最下方有welcome按钮），需要修改
3. 注册/登录成功后消息flash在页面顶部，刷新才会消失
4. welcome页面的搜索框是否需要加`<form method="post">`？

20200223

测试时同一个测试函数（针对同一个页面）内不会清空数据库，在测试该页面上不同的功能时可能需要手动退出之前的用户登录或者清空数据库

对assert的了解不够深入，不知道是否有更高效和精准的方法

目前的测试只有76%的覆盖率，还需提高

执行单元测试的方法：（出错则可看到出错信息）
```
(env) $ python test.py
...............
----------------------------------------------------------------------
Ran 15 tests in 2.942s

OK
```
查看测试覆盖率：
```
(env) $ pip install coverage
(env) $ coverage run --source=flaskweb test.py  (测试并汇报)
$ coverage report
Name     Stmts   Miss  Cover
----------------------------
xx.py     146      5    97%
```

20200224:
使用包组织程序，调整后项目文件结构如下：
```
├── .flaskenv
├── test.py            # 测试程序
└── flaskweb           # 程序包
    ├── __init__.py    # 包构造文件，创建程序实例和拓展对象，定义应用设置
    ├── commands.py    # 命令函数
    ├── models.py      # 模型类
    ├── views.py       # 视图函数
    ├── static
    │   ├── css
    │   │   ├──landing-page.css
    │   │   └──landing-page.min.css
    │   ├── img   
    │   │   └── ...(原模板自带图片7张)
    │   └── vendor
    │   │   └── ...(原模板自带样式和字体)
    └── templates
        ├── base.html
        ├── index.html
        ├── signin.html
        ├── signup.html
        └── welcome.html
```
运行程序方法没变，仍是在StudyAssistant文件夹下，先`flask initdb`初始化数据库，再`flask forge`生成虚拟数据，最后`flask run`运行

20200226:
老师提供的数据库包括8个表：
可用：
1. concept: concept和definition，均为text
2. entity: EntityName和Wiki(其维基百科链指)，待探索用法
3. mooc: name, chinesename, duration, platform, school, department
    1988条数据，其中200为计算机领域课程，中英文都有，url全不可用

不可用：
1. user: 师姐项目的user
2. userentity: EntityName和Master，意义不明
3. entityvideo: VID, EName, time，不可用（师姐遗留）
4. uservideo: VID, lastlearn(日期时间)
5. video: VID, VName, Course, Vurl，是Coursera上部分视频的记录，只涉及5门课内47个视频片段，大概是师姐遗留产物