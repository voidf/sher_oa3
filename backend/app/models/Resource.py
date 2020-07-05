from app import db
from app.models.UserBase import UserBase

import datetime

class Resource(db.Document):
    name = db.StringField()
    last_modify = db.DateTimeField()
    create_datetime = db.DateTimeField()
    url = db.StringField()
    writable = db.ListField(db.ReferenceField(UserBase))
    readable = db.ListField(db.ReferenceField(UserBase))

    def rename(self,new_name:str) -> self:
        self.name = new_name
        self.last_modify = datetime.datetime.now()
        return self.save()

    def change_url(self,new_url:str) -> self:
        self.url = new_url
        self.last_modify = datetime.datetime.now()
        return self.save()

    def new_resource(author:UserBase):
        return Resource(writable=[author],readable=[author],last_modify=datetime.datetime.now())

    def remove(self):
        self.delete()

    def append_access(self,new_writables=[],new_readables=[]):
        for _ in new_writables:
            self.update(add_to_set__writable=_)
        for _ in new_readables:
            self.update(add_to_set__readable=_)
        return self

    def discard_access(self,ban_writables=[],ban_readables=[]):
        for _ in ban_writables:
            self.update(pull__writable=_)
        for _ in ban_readables:
            self.update(pull__readable=_)
        return self

    def modify_access(self,new_writables=[],new_readables=[]):
        self.writable = new_writables
        self.readable = new_readables
        return self.save()

    def get_base_info(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "last_modify": self.last_modify,
            "create_datetime": self.create_datetime
        }



