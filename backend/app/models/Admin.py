import datetime
import hashlib
from app import db

def str2md5(str):
    return hashlib.sha256(hashlib.sha256(str.encode('utf-8')).hexdigest().encode('utf-8')).hexdigest()


class Admin(db.Document):
    user_id = db.StringField()
    password = db.StringField()

    def insert_admin(user_id, password): # 原则上只用一次
        return Admin(user_id=user_id, 
                    password=str2md5(password),
                    create_datetime=datetime.datetime.now(), last_modify=datetime.datetime.now()).save()

    def set_password(self, password):
        self.password = str2md5(password)
        self.last_modify = datetime.datetime.now()
        return self.save()

    def valid_password(self, password):
        return self.password == str2md5(password)
