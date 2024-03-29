import asyncio
import base64
from io import BytesIO
import os
from re import A
from utils.data_utils import init_rank
from utils.message_builder import image , at
from nonebot import on_command
from nonebot.typing import T_State
from PIL import Image

from nonebot.adapters.onebot.v11 import (
        GroupMessageEvent,
        GROUP,
        Bot,
        Message,
)
import random
import time
from nonebot.params import CommandArg
from models.group_member_info import GroupInfoUser
from utils.utils import is_number
from utils.utils import scheduler
from._model import My_wife


#初始化
asyncio.run(My_wife.__init__())

__zx_plugin_name__ = "群老婆"
__plugin_usage__ = """
usage:
    抽群老婆:
        有三分钟cd
        指令:
        抽群老婆
    我的群老婆:
        指令:
        我的群老婆
    呼叫老婆:
        指令:
        呼叫老婆
    海王榜:
        生成抽取老婆次数的排行榜，后加数字增加显示人数，默认10，最多50
        指令:
        海王榜 num
        
""".strip()
__plugin_des__ = "抽群老婆"
__plugin_cmd__ = ["抽群老婆", "我的群老婆", "呼叫老婆",'海王榜']
__plugin_type__ = ("群内小游戏",)
__plugin_version__ = 1.0
__plugin_author__ = "冰蓝色光点"
__plugin_settings__ = {
    "level": 5,
    "default_status": True,
    "limit_superuser": False,
    "cmd": ["抽群老婆", "我的群老婆", "呼叫老婆", '海王榜'],
}

draw_wife = on_command("抽群老婆",permission=GROUP, priority=5, block=True)
my_wife = on_command("我的群老婆",permission=GROUP, priority=5, block=True)
at_wife = on_command("呼叫老婆",permission=GROUP, priority=5, block=True)
see_king = on_command("海王榜",permission=GROUP, priority=5, block=True)
group_user_wife = {}

@draw_wife.handle()

async def _(bot: Bot,
            event: GroupMessageEvent,
            state: T_State,
            args: Message = CommandArg(),
            ):
    uid = event.user_id
    group = event.group_id
    global group_user_wife
    try:
        if group_user_wife[group]:
           pass 
    except KeyError:
        group_user_wife[group] = {}
    try:
        if group_user_wife[group][uid]:
            pass
    except KeyError:
        group_user_wife[group][uid] = {}
    try:
        time_pass = int (time.time() - group_user_wife[group][uid]['time'])
        if time_pass < 30:
            time_rest = 30 - time_pass
            draw_refuse = [f'才过去了{time_pass}s时间,你就要换老婆了,真是始乱终弃呢',
                           f'不行不行，你的身体会受不了的，歇{time_rest}s再来吧',
                           f'合不合适起码相处三分钟再说吧'
                           ]    
            
            await draw_wife.finish(random.choice(draw_refuse), at_sender=True)
    except KeyError:
        pass
    group_user_wife[group][uid]['time'] = time.time()    
    wife_list = list(await GroupInfoUser.get_group_member_id_list(group))
    user_wife = int(random.choice(wife_list))
    while user_wife == uid:
        user_wife = int(random.choice(wife_list))
        
    wife_name = await get_name(user_wife, group)
    url = f"http://q1.qlogo.cn/g?b=qq&nk={user_wife}&s=640"
    await My_wife.wife_revise(group, uid, user_wife)
    msg_tuple = (f'你的群老婆是{wife_name}({user_wife})', image(url), "好好相处哦")
    await draw_wife.finish(Message(msg_tuple), at_sender=True)
  
async def get_name(user_id: str, group_id: str) -> str: 
     if user := await GroupInfoUser.get_or_none(user_id=user_id, group_id=group_id): 
         return user.user_name
     else: 
         return "该群员不在列表中，请更新群成员信息"

@my_wife.handle()
async def _(bot: Bot,
            event: GroupMessageEvent,
            state: T_State,
            args: Message = CommandArg(),
            ):
        global group_user_wife
        uid = event.user_id
        group = event.group_id
        user_wife = await My_wife.wife_view(group, uid)
        if user_wife == 0:
            await my_wife.finish("你还没有抽群老婆哦", at_sender=True) 
        else:
                wife_name = await get_name(user_wife, group)
                url = f"http://q1.qlogo.cn/g?b=qq&nk={user_wife}&s=5"
                msg_tuple = (f'你当前的群老婆是\n{wife_name}({user_wife})', image(url))
                await my_wife.finish(Message(msg_tuple), at_sender=True)
                
async def get_name(user_id: str, group_id: str) -> str: 
     if user := await GroupInfoUser.get_or_none(user_id=user_id, group_id=group_id): 
         return user.user_name
     else: 
         return "该群员不在列表中，请更新群成员信息"
                
          
                

@at_wife.handle()
async def _(bot: Bot,
            event: GroupMessageEvent,
            state: T_State,
            args: Message = CommandArg(),
            ):
        global group_user_wife
        uid = event.user_id
        group = event.group_id
        user_wife = await My_wife.wife_view(group, uid)
        if user_wife == 0:
            await at_wife.finish("你还没有抽群老婆哦", at_sender=True) 
        else:
            msg = at(user_wife)
            await at_wife.finish(msg)
            
                
@see_king.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    num = arg.extract_plain_text().strip()
    if is_number(num) and 51 > int(num) > 10:
        num = int(num)
    else:
        num = 10
    all_users = await My_wife.get_all_users(event.group_id)
    all_user_id = [user[0] for user in all_users]
    all_user_data = [int(user[1]) for user in all_users]
    rank_image = await init_rank("海王排行榜", all_user_id, all_user_data, event.group_id, num)
    if rank_image:
        await see_king.finish(image(b64=rank_image.pic2bs4()))



def pic2b64(pic: Image) -> str:
    """
    说明:
        PIL图片转base64
    参数:
        :param pic: 通过PIL打开的图片文件
    """
    buf = BytesIO()
    pic.save(buf, format="PNG")
    base64_str = base64.b64encode(buf.getvalue()).decode()
    return "base64://" + base64_str

@scheduler.scheduled_job(
    "cron",
    hour=23,
    minute=50,
)
async def _():
    global group_user_wife
    group_user_wife = {}