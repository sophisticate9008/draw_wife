import re
from services.db_context import db

class My_wife(db.Model):
    __tablename__ = "my_wife"
    id = db.Column(db.Integer(), primary_key=True)
    group_id = db.Column(db.BigInteger(), nullable=False)
    my_qq = db.Column(db.BigInteger(), nullable=True)
    wife_qq = db.Column(db.BigInteger(), nullable=False)
    count_draw = db.Column(db.BigInteger(), nullable=False, default = 0)
    wife_idx1 = db.Index("my_wife_uid", "group_id", "my_qq", unique=True)
    @classmethod
    async def wife_revise(cls, group_id:int, my_qq:int, wife_qq):
        query = cls.query.where((cls.group_id == group_id) & (cls.my_qq == my_qq))
        query = query.with_for_update()
        me = await query.gino.first()
        if me:
            await me.update(wife_qq = wife_qq).apply()
            await me.update(count_draw = me.count_draw + 1).apply()
        else:
            await cls.create(group_id = group_id, my_qq = my_qq, wife_qq = wife_qq, count_draw = 1)
    @classmethod
    async def wife_view(cls, group_id:int, my_qq:int):
        query = cls.query.where((cls.group_id == group_id) & (cls.my_qq == my_qq))
        query = query.with_for_update()
        me = await query.gino.first()
        if me:
            return me.wife_qq
        else:
            return 0

    @classmethod
    async def get_all_users(cls, group_id:int):
        if not group_id:
            query = await cls.query.gino.all()
        else:
            query = await cls.query.where((cls.group_id == group_id)).gino.all()
        return query

class fake_wife(db.Model):
    __tablename__ = "fake_wife"
    id = db.Column(db.Integer(), primary_key=True)
    group_id = db.Column(db.BigInteger(), nullable=False)
    uid = db.Column(db.BigInteger(), nullable=True)       
    name = db.Column(db.Unicode(), nullable=False)
    @classmethod
    async def make_wife(cls, group, uid, name):
        query = cls.query.where((cls.group_id == group) & (cls.uid == uid))
        query = query.with_for_update()
        me = await query.gino.first()     
        if me:    
            await me.update(name = name).apply()
        else:
            await cls.create(group_id = group, uid = uid, name = name)
    @classmethod
    async def del_wife(cls, group, uid):
        query = cls.query.where((cls.group_id == group) & (cls.uid == uid))
        query = query.with_for_update()
        me = await query.gino.first()
        try:
            if me is None:
                return True
            else:
                await cls.delete.where((cls.group_id == group) & (cls.uid == uid)).gino.status()
                return True
        except Exception:
            return False
    @classmethod
    async def get_name(cls, group, uid):
        query = cls.query.where((cls.group_id == group) & (cls.uid == uid))
        query = query.with_for_update()
        me = await query.gino.first()     
        return me.name
    
    @classmethod
    async def get_all(cls, group):
        if not group:
            query = await cls.query.gino.all()
        else:
            query = await cls.query.where((cls.group_id == group)).gino.all()
        return query
