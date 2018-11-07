# 主业务逻辑中的视图和路由的定义
import datetime

from flask import render_template, request, redirect
# 导入蓝图程序，用于构建路由
import os

from . import main
# 导入db，用于操作数据库
from .. import db
# 导入实体类，用于操作数据库
from ..models import *
from flask import session

@main.route('/')
def main_index():
    # 查询所有的category的信息
    category = Category.query.all()
    # 查询所有的Topic的信息
    topics = Topic.query.all()

    # 获取登录信息
    if 'uid' in session and 'uname' in session:
        user = User.query.filter_by(id=session.get('uid')).first()

    return render_template('index.html',params=locals())

# 登录页面的访问路径
@main.route('/login',methods=['GET','POST'])
def login_views():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        # 接收前端传递过来的数据
        loginname = request.form.get('username')
        pwd = request.form.get('password')
        # 使用接收的用户名和密码到数据库中查询
        user = User.query.filter_by(loginname=loginname,upwd=pwd).first()
        # 如果用户存在，将信息保存进session并重定向回首页，否则重定向回登录页
        if user:
            session['uid'] = user.id
            session['uname'] = user.uname
            return redirect('/')
        else:
            errMsg = "用户名或密码不正确"
            return render_template('login.html',errMsg=errMsg)

#退出的访问路径
@main.route('/logout')
def logout_views():
    if 'uid' in session and 'uname' in session:
        del session['uid']
        del session['uname']
    return redirect('/')

# 注册页面的访问地址
@main.route('/register',methods=['GET','POST'])
def register_views():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        # 获取文本框中值并赋值给user实体对象
        user = User()
        user.loginname = request.form['loginname']
        user.uname = request.form['username']
        user.email = request.form['email']
        user.url = request.form['url']
        user.upwd = request.form['password']
        # 将数据保存进数据库 - 注册
        db.session.add(user)
        # 手动提交，目的是为了获取提交后的user的id
        db.session.commit()
        # 当user成功插入数据库之后，程序会自动将所有信息取出来再赋值给user
        print("新用户ID为：%s" % user.id)
        # 完成登录的操作
        session['uid'] = user.id
        session['uname'] = user.uname
        return redirect('/')

# 发表博客的访问地址
@main.route('/release',methods=['GET','POST'])
def release_views():
    if request.method == 'GET':
        # 权限验证：验证用户是否有发表博客的权限即必须是登录用户并且is_author的值必须为1
        if 'uid' not in session or 'uname' not in session:
            return redirect('/login')
        else:
            user = User.query.filter_by(id=session.get('uid')).first()
            if user.is_author != 1:
                return redirect('/')
        # 查询category和blogtype
        categorys = Category.query.all()
        blogTypes = BlogType.query.all()
        return render_template('release.html',params=locals())
    else:
        # 处理post请求即发表博客的处理
        topic = Topic()
        # 为title赋值
        topic.title = request.form.get('author')
        # 为blogtype_id赋值
        topic.blogtype_id = request.form.get('list')
        # 为category_id赋值
        topic.category_id = request.form.get('category')
        # 为user_id赋值
        topic.user_id = session['uid']
        # 为content赋值
        topic.content = request.form.get('content')
        # 为pub_date赋值
        topic.pub_date = datetime.datetime.now().strftime("%Y-%m-%d")
        # 选择性的为images赋值
        if request.files:
            # 取出文件
            f = request.files['picture']
            # 出路文件名称，将名称赋值给topic.images
            # 获取当前时间，作为文件名
            ftime = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
            # 获取文件的扩展名
            ext = f.filename.split('.')[1]
            filename = ftime+"."+ext
            topic.images = 'upload/'+filename
            # 将文件保存至服务器
            basedir = os.path.dirname(os.path.dirname(__file__))
            print(basedir)
            upload_path = os.path.join(basedir,'static/upload',filename)
            print(upload_path)
            f.save(upload_path)

        db.session.add(topic)
        return redirect('/')

@main.route('/info',methods=['GET','POST'])
def info_views():
    if request.method == 'GET':
        # 查询要看的博客信息
        topic_id = request.args.get('topic_id')
        topic = Topic.query.filter_by(id=topic_id).first()
        # 更新阅读量
        topic.read_num = int(topic.read_num) + 1
        db.session.add(topic)
        # 查找上一篇 以及 下一篇
        # 上一篇：查询topic_id比当前topic_id值小的最后一条数据
        prevTopic = Topic.query.filter(Topic.id<topic.id).order_by('id desc').first()
        # 下一篇：查询topic_id比当前topic_id值大的第一条数据
        nextTopic = Topic.query.filter(Topic.id>topic.id).first()
        print(prevTopic,nextTopic)
        # 查询登录用户
        if 'uid' in session and 'uname' in session:
            user = User.query.filter_by(id=session['uid'])
        return render_template('info.html',params=locals())