import datetime
import hashlib

from app import db


def str2md5(str):
    return hashlib.sha256(hashlib.sha256(str.encode('utf-8')).hexdigest().encode('utf-8')).hexdigest()


class User(db.Document):
    name = db.StringField()
    permission = db.IntField(default=0)
    user_id = db.StringField()
    bio = db.StringField()
    last_modify = db.DateTimeField()
    create_datetime = db.DateTimeField()
    password = db.StringField()
    nickname = db.StringField()
    status = db.StringField(default='p')

    def set_password(self, password):
        self.password = str2md5(password)
        return self.save()

    def valid_password(self, password):
        return self.password == str2md5(password)

    def insert_user(name, user_id, password, permission):
        return User(name=name, user_id=user_id, 
                    password=str2md5(password), permission=permission, 
                    create_datetime=datetime.datetime.now(), last_modify=datetime.datetime.now()).save()

    def get_or_create(name, user_id, password, permission):
        _t = User.objects(name=name,user_id=user_id,password=str2md5(password),permission=permission)
        if any(_t):
            return _t.first()
        else:
            return User(
                name=name,
                user_id=user_id, 
                password=str2md5(password),
                permission=permission
            ).save()

    def get_base_info(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "user_id": self.user_id,
            "bio": self.bio,
            "permission": self.permission
        }


if User.objects().count() == 0:
    User.insert_user("Admin", "1234567890", "123456", 5)
