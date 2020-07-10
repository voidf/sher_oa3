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
from app.models.Admin import Admin
from app.models.Sign import Sign
from app.models.Routine import Routine
from app.models.Role import Role
from app.util.auth import generate_jwt, mverify_jwt
from app.util.sheet import sheet

msign_blueprint = Blueprint('msign', __name__, url_prefix='/msign')

time_table = {
    0: range(28800, 36000),
    1: range(36000, 43200),
    2: range(50400, 57600),
    3: range(57600, 64800),
    4: range(68400, 75600)
}


@msign_blueprint.before_request
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
@msign_blueprint.route('/do', methods=['GET'])
@validmsign
def do_msign():  # shift改变排班的week只是记签到目的week，不作为判断是否允许签到的依据
    wk = int((datetime.datetime.now - Admin.objects().first().server_starttime).total_seconds()) % (86400*7)
    r = Routine.objects(user=g.user).first()
    ima = datetime.datetime.now().timestamp() + 28800

    if r.signtime == r.shift:  # 没有调班
        if int((ima + 259200) % 604800 / 86400) == int(r.signtime / 5) and ima % 86400 in time_table[r.signtime % 5]:
            if not Sign.objects(user=g.user, week=wk):
                if Sign.create(user=g.user, typ='n', week=wk):
                    return trueReturn()
                else:
                    return falseReturn(msg='本时间段内签过到')
            else:
                return falseReturn(msg='本周已签过到')
        else:
            return falseReturn(msg='不在签到时段内')
    else:
        if int((ima + 259200) % 604800 / 86400) == int(r.shift / 5) and ima % 86400 in time_table[r.shift % 5]:
            if not Sign.objects(user=g.user, week=r.shift_week):
                if Sign.create(user=g.user, typ='s', week=r.shift_week):
                    r = r.recover_shift()
                    return trueReturn()
                else:
                    r = r.recover_shift()
                    return falseReturn(msg='本时间段内签过到')
            else:
                r = r.recover_shift()
                return falseReturn(msg='本周已签过到')
        else:
            return falseReturn(msg='不在签到时段内')


@handle_error
@msign_blueprint.route('/ls', methods=['GET'])
@validsign
def ls_msign():
    return trueReturn({'signs': [i.get_base_info() for i in Sign.objects(user=g.user)]})


@handle_error
@msign_blueprint.route('/export', methods=['GET'])
@validsign
def export_msign():
    return trueReturn({'all_signs': [{'user': j, 'signs': [i.get_base_info() for i in Sign.objects(user=j)]} for j in User.objects()]})