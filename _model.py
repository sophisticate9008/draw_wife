import re
from services.db_context import Model
from tortoise import fields

class My_wife(Model):
    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    group_id = fields.BigIntField()
    my_qq = fields.BigIntField()
    wife_qq = fields.BigIntField()
    count_draw = fields.IntField()
    
    class Meta:
        table = "my_wife"
        table_description = "群老婆数据表"
        unique_together = ("my_qq", "group_id")          
    @classmethod
    async def wife_revise(cls, group_id:int, my_qq:int, wife_qq):

        if me := await cls.get_or_none(group_id=group_id, my_qq=my_qq):
            me.wife_qq = wife_qq
            me.cout_draw += 1
            await me.save()
        else:
            await cls.create(group_id = group_id, my_qq = my_qq, wife_qq = wife_qq, count_draw = 1)
    @classmethod
    async def wife_view(cls, group_id:int, my_qq:int):

        if me := await cls.get_or_none(group_id=group_id, my_qq=my_qq):
            return me.wife_qq
        else:
            return 0

    @classmethod
    async def get_all_users(cls, group_id:int):
        if not group_id:
            query = await cls.all()
        else:
            query = await cls.filter(group_id = group_id).all()
        return query

class fake_wife(Model):
    __tablename__ = "fake_wife"
    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    group_id = fields.BigIntField()
    uid = fields.BigIntField()    
    name = fields.CharField()
    @classmethod
    async def make_wife(cls, group_id, uid, name):

        if me := await cls.get_or_none(group_id=group_id, uid=uid):  
            me.name = name
            await me.save()
        else:
            await cls.create(group_id = group_id, uid = uid, name = name)
    @classmethod
    async def del_wife(cls, group_id, uid):
        try:
            if me := await cls.get_or_none(group_id=group_id, uid=uid):
                await me.delete()
                return True
            else:
                return True
        except Exception:
            return False
    @classmethod
    async def get_name(cls, group_id, uid):
        if me := await cls.get_or_none(group_id=group_id, uid=uid): 
            return me.name
    
    @classmethod
    async def get_all(cls, group_id):
        if not group_id:
            query = await cls.all()
        else:
            query = await cls.filter(group_id = group_id).all()
        return query
