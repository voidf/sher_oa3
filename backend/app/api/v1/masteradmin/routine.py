import datetime
import hashlib
import json
import traceback

import requests
from flask import Blueprint
from flask import current_app as flaskapp
from flask import g, jsonify, request
from mongoengine.queryset.visitor import Q

from app.api import handle_error, validsign, verify_params, validcall
from app.common.result import falseReturn, trueReturn
from app.models.User import User
from app.models.Domain import Domain
from app.models.Sign import Sign
from app.models.Routine import Routine
from app.models.Admin import Admin
from app.models.Role import Role
from app.util.auth import generate_jwt, mverify_jwt
from app.util.sheet import sheet

mroutine_blueprint = Blueprint('mroutine', __name__, url_prefix='/mroutine')

time_table = {
    0:range(28800,36000),
    1:range(36000,43200),
    2:range(50400,57600),
    3:range(57600,64800),
    4:range(68400,75600)
}

@mroutine_blueprint.before_request
def before_request():
    try:
        if request.get_data():
            g.data = request.get_json(silent=True)
        Authorization = request.headers.get('Authorization', None)
        print(Authorization)
        if Authorization:
            token = Authorization
            g.token = token
            g.user, msg = mverify_jwt(token)
        else:
            pass
    except:
        traceback.print_exc()
        return falseReturn(None, '数据错误')

@handle_error
@mroutine_blueprint.route('/init', methods=['POST'])
@verify_params(params=['signtime'])
@validsign
def init_mroutine(): 
    if int(g.data['signtime']) not in range(0,35):
        return falseReturn(msg='值班时间段设置不合法')
    if Routine.init_routine(g.user,g.data['signtime']):
        return trueReturn()
    else:
        return falseReturn(msg='您已设置过签到时间')

@handle_error
@mroutine_blueprint.route('/change', methods=['POST'])
@verify_params(params=['user','signtime'])
@validsign

def change_mroutine(): # 永久调班
    if int(g.data['signtime']) not in range(0,35):
        return falseReturn(msg='值班时间段设置不合法')
    u = User.get_by_id(g.data['user'])
    Routine.objects(user=u).change_signtime(g.data['signtime'])
    return trueReturn()

@handle_error
@mroutine_blueprint.route('/shift', methods=['POST'])
@verify_params(params=['shift','shift_week'])
@validsign
def shift_mroutine(): # 临时调班
    if int(g.data['shift']) not in range(0,35):
        return falseReturn(msg='调班时间段设置不合法')
    if not Sign.objects(user=g.user,week=int(g.data['shift_week'])):
        r = Routine.objects(user=g.user).first()
        r.change_shift(g.data['shift'],g.data['shift_week'])
        return trueReturn()
    else:
        return falseReturn(msg='您已在此周签过到')

@handle_error
@mroutine_blueprint.route('/set_starttime', methods=['POST'])
@verify_params(params=['time'])
@validsign

def set_starttime(): # 设置系统启动时间
    d = datetime.datetime.strptime('%Y/%m/%d %H:%M:%S')
    Admin.objects().first().change_starttime(d)
    return trueReturn()