
from services.db_context import db

class My_wife(db.Model):
    __tablename__ = "my_wife"
    group_id = db.Column(db.BigInteger(), nullable=False)
    my_qq = db.Column(db.BigInteger(), primary_key=True)
    wife_qq = db.Column(db.BigInteger(), nullable=False)
    count_draw = db.Column(db.BigInteger(), nullable=False, default = 0)
    _idx1 = db.Index("my_wife_uid", "group_id", "my_qq", unique=True)
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
         
