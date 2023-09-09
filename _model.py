import asyncio
import functools
import os
import sqlite3

conn = sqlite3.connect(os.path.dirname(__file__)+"/wifes.db", check_same_thread=False)


class Model:
    __abstract__ = True

    def __init__(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)

    @classmethod
    async def execute(cls, command: str, *args):
        loop = asyncio.get_event_loop()
        cursor = await loop.run_in_executor(None, functools.partial(conn.cursor))
        try:
            await loop.run_in_executor(None, functools.partial(cursor.execute, command, args))
            rows = await loop.run_in_executor(None, cursor.fetchall)
            await loop.run_in_executor(None, conn.commit)  # 提交数据
        except Exception as e:
            raise e
        finally:
            await loop.run_in_executor(None, cursor.close)
        return rows
    


class My_wife(Model):
    __tablename__ = "my_wife"
    async def __init__():
        sql_create_table = """
        CREATE TABLE IF NOT EXISTS my_wife (
          group_id BIGINT NOT NULL,
          my_qq BIGINT NULL,
          wife_qq BIGINT NOT NULL,
          count_draw INTEGER NOT NULL DEFAULT 0,
          UNIQUE(group_id, wife_qq)
        );
        """
        await Model.execute(sql_create_table)
    
    @classmethod
    async def wife_revise(cls, group_id:int, my_qq:int, wife_qq):
        command = f"SELECT * FROM {cls.__tablename__} WHERE group_id=? AND my_qq=?;"
        rows = await cls.execute(command, group_id, my_qq)
        me = rows[0] if rows else None
        if me:
            command = f"UPDATE {cls.__tablename__} SET wife_qq=?, count_draw=count_draw+1 WHERE group_id=? AND my_qq=?;"
            await cls.execute(command, wife_qq, group_id, my_qq)
        else:
            command = f"INSERT INTO {cls.__tablename__} (group_id, my_qq, wife_qq, count_draw) VALUES (?, ?, ?, ?);"
            await cls.execute(command, group_id, my_qq, wife_qq, 1)

    @classmethod
    async def wife_view(cls, group_id:int, my_qq:int):
        command = f"SELECT wife_qq FROM {cls.__tablename__} WHERE group_id=? AND my_qq=?;"
        rows = await cls.execute(command, group_id, my_qq)
        wife_qq = rows[0][0] if rows else 0
        return wife_qq

    @classmethod
    async def get_all_users(cls, group_id: int):
        if group_id is None:
            command = f"SELECT my_qq, count_draw FROM {cls.__tablename__};"
        else:
            command = f"SELECT my_qq, count_draw FROM {cls.__tablename__} WHERE group_id=?;"
        rows = await cls.execute(command, group_id)
        return list(rows)