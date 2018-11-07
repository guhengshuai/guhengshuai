# main目录：包含主要的业务逻辑的路由和视图
#__init__.py：对业务逻辑程序的初始化操作
from flask import Blueprint
main = Blueprint('main',__name__)
from . import views
