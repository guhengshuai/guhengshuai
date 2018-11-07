# user目录：针对用户业务逻辑处理的目录
# 针对用户业务逻辑处理的初始化行为
from flask import Blueprint
user = Blueprint('user',__name__)
from . import views