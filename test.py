import unittest # 测试框架，用于对函数等独立的单元编写测试

from app import app, db, User, initdb, forge

class WebsiteTestCase(unittest.TestCase): # 测试用例

    def setUp(self): # 测试固件
        # 更新配置
        app.config.update(
            TESTING=True, # 开启测试模式
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:' # 使用SQLite内存性数据库测试
        )
        # 创建数据库和表
        db.create_all()
        user = User(name='Test')
        user.set_password('123')
        db.session.add(user)
        db.session.commit()

        self.client = app.test_client() # 创建测试客户端
        self.runner = app.test_cli_runner() # 创建测试命令运行器
    
    def tearDown(self):
        db.session.remove() # 清除数据会话
        db.drop_all() # 删除数据库表
        
    # 测试程序实例是否存在
    def test_app_exist(self):
        self.assertIsNotNone(app)

    # 测试程序是否处于测试模式
    def test_app_is_testing(self):
        self.assertTrue(app.config['TESTING'])

    # 测试主页
    def test_index_page(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertIn('StudyAssistant', data)
        self.assertEqual(response.status_code, 200)

    # 辅助方法，用于登录用户
    def login(self):
        self.client.post('/signin', data=dict( # POST请求提交表单
            user_name='Test', # <input>元素的name属性
            user_password='123'
        ), follow_redirects=True) # 跟随重定向
    

    # 测试需要登录的项目，暂时不需要
    '''
    def test_xxx(self):
        self.login()

        response = self.client.post('/', data=dict(
            user_name='xx',
            user_password='xx'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item created.', data)
        self.assertIn('New Movie', data)

        response = self.client.post
    '''

    # 测试登录保护
    def test_login_protect(self):
        response = self.client.get('/welcome')
        data = response.get_data(as_text=True)
        self.assertIn('Please log in to access this page.')
        self.assertNotIn('Log Out', data)
        self.assertNotIn('StudyAssistant', data)

    # 测试登录
    def test_signin_page(self):
        response = self.client.post('/signin', data=dict(
            user_name='Test', 
            user_password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Login success.', data)
        self.assertNotIn('StudyAssistant', data)
        self.assertIn('Search for...', data)
        self.assertIn('Test', data)
        self.assertIn('Log Out', data)

        # 测试使用错误的密码登录
        response = self.client.post('/signin', data=dict(
            user_name='Test',
            user_password='456'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid username or password.', data)

        # 测试使用不存在的用户名登录
        response = self.client.post('/signin', data=dict(
            user_name='TestWrong',
            user_password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid username or password.', data)        

        # 测试使用空用户名登录
        response = self.client.post('/signin', data=dict(
            user_name='',
            user_password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid input.', data) 

        # 测试使用空密码登录
        response = self.client.post('/signin', data=dict(
            user_name='Test',
            user_password=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid input.', data)   

    # 测试注册
    def test_signup_page(self):
        '''
        不太清楚测试时数据库是否会随时清空/以测试函数为单元清空
        如果是，则signup测试都会提示Username Occupied!
        '''

        response = self.client.post('/signup', data=dict(
            user_name='Test', 
            user_password='123', 
            user_password_1='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Success Signup!', data)
        self.assertNotIn('StudyAssistant', data)
        self.assertIn('Search for...', data)
        self.assertIn('Test', data)
        self.assertIn('Log Out', data)

        # 测试使用已存在的用户名注册
        self.client.post('/signin', data=dict( 
            user_name='Test01', 
            user_password='12301'
        ), follow_redirects=True) 

        response = self.client.post('/signup', data=dict(
            user_name='Test01',
            user_password='12301',
            user_password_1='12301'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Success Signup!', data)
        self.assertIn('Username Occupied!', data)   

        # 两次密码输入不一致
        response = self.client.post('/signup, data=dict(
            user_name='Test',
            user_password='123',
            user_password_1='456'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Success Signup!', data)
        self.assertIn('Two passwords do not match.', data)              

        # 测试使用空用户名注册
        response = self.client.post('/signup', data=dict(
            user_name='',
            user_password='123',
            user_password_1='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Success Signup!', data)
        self.assertIn('Invalid input.', data) 

        # 测试使用空密码注册
        response = self.client.post('/signup', data=dict(
            user_name='Test',
            user_password='',
            user_password_1='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Success Signup!', data)
        self.assertIn('Invalid input.', data)   

        response = self.client.post('/signup', data=dict(
            user_name='Test',
            user_password='123',
            user_password_1=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Success Signup!', data)
        self.assertIn('Invalid input.', data)

    # 测试登出
    def test_logout(self):
        self.login()

        response = self.client.get('/logout', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Signout success.', data) 
        self.assertIn('StudyAssistant', data)
        self.assertIn('Sign In', data)
        self.assertIn('Sign Up', data)
        self.assertNotIn('Search for...', data)
        self.assertNotIn('Log Out', data)

    # 测试welcome页面
    def test_welcome_page(self):
        self.login()

        response = self.client.get('/welcome')
        data = response.get_data(as_text=True)
        self.assertIn('Test', data)
        self.assertIn('Search for...', data)
        self.assertIn('Log Out', data)        
        self.assertNotIn('StudyAssistant', data)
        self.assertEqual(response.status_code, 200)

    # 测试初始化数据库
    def test_initdb_command(self):
        result = self.runner.invoke(initdb)
        self.assertIn('Initialized database.', result.output)

    # 测试虚拟数据
    def test_forge_command(self):
        result = self.runner.invoke(forge)
        self.assertIn('Done.', result.output)
        self.assertNotEqual(User.query.count(), 0)

if __name__ == '__main__':
    unittest.main()