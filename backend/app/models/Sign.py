from app import db
import datetime


class Sign(db.Document):

    create_datetime = db.DateTimeField()  # 签到时间
    typ = db.StringField()  # 签到类型，分为'n'正常签到和's'换班签到
    week = db.IntField()  # 签到周
    
    user = db.ReferenceField(app.models.User.User,reverse_delete_rule=2)

    def create(user: app.models.User.User, typ: str, week: int) -> bool:
        if user.last_sign:
            if user.last_sign.timestamp() / 7200 != datetime.datetime.now() / 7200:  # 卡两个小时内多次签到的情况
                s = Sign(create_datetime=datetime.datetime.now(),
                         typ=typ, week=week)
                user.last_sign = s
                s.save()
                user.save()
                return True
            else:
                return False
        else:
            s = Sign(create_datetime=datetime.datetime.now(),
                     typ=typ, week=week)
            user.last_sign = s
            s.save()
            user.save()
            return True

    def get_by_id(id):
        return Sign(id=id).first()

    def get_by_user(user:app.models.User.User) -> dict:
        return {"signs":[i.get_base_info() for i in Sign.objects(user=user)]}

    def get_base_info(self) -> dict:
        return {
            "id": str(self.id), 
            "create_datetime": self.create_datetime,
            "week": self.week,
            "typ": self.typ,
            "user": self.user
        }
import app.models.User