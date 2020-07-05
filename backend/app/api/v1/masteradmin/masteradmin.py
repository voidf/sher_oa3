import datetime
import hashlib
import json
import traceback

import requests
from flask import Blueprint
from flask import current_app as flaskapp
from flask import g, jsonify, request
from mongoengine.queryset.visitor import Q

from app.api import handle_error, validsign
from app.common.result import falseReturn, trueReturn
from app.models.Admin import Admin
from app.util.auth import generate_jwt, verify_jwt
from app.util.sheet import sheet

masteradmin_blueprint = Blueprint('masteradmin', __name__, url_prefix='/masteradmin')


@masteradmin_blueprint.before_request
def before_request():
    try:
        if request.get_data():
            g.data = request.get_json(silent=True)
        Authorization = request.headers.get('Authorization', None)
        print(Authorization)
        if Authorization:
            typ, token = Authorization.split()
            if typ == 'Bearer':
                g.token = token
                g.user, msg = verify_jwt(token)
        else:
            pass
    except:
        traceback.print_exc()
        return falseReturn(None, '数据错误')


@handle_error
@masteradmin_blueprint.route('/signin', methods=['POST'])
def signin():
    name = g.data.get("username", "").strip()
    password = g.data.get("password", "")
    user = Admin.objects(user_id=name).first()
    if not user or not user.valid_password(password):
        return falseReturn(None, "用户名或密码有误")
    return trueReturn({
        'user': user.get_base_info(),
        'token': generate_jwt(user),
    })

@handle_error
@masteradmin_blueprint.route('/import', methods=['POST'])
@validsign
def import_from_sheet():
    if 'file' not in request.files:
        return falseReturn(None, '无文件')
    f = request.files['file']
    if f.filename == '':
        return falseReturn(None, '未选择上传')
    else:
        sheet(f)
        return trueReturn()

        