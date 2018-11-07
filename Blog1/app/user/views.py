from flask import render_template
from . import user
from .. import db
from ..models import *

@user.route('/user')
def main_index():
    return "这是user中的首页"