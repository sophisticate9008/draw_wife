
from utils.message_builder import image , at
from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import (
        GroupMessageEvent,
        MessageEvent,
        GROUP,
        Bot,
        Message,
        MessageSegment
)
import random
import time
from nonebot.params import CommandArg
from models.group_member_info import GroupInfoUser
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
        
""".strip()
__plugin_des__ = "抽群老婆"
__plugin_cmd__ = ["抽群老婆", "我的群老婆", "呼叫老婆"]
__plugin_type__ = ("群内小游戏",)
__plugin_version__ = 1.0
__plugin_author__ = "冰蓝色光点"
__plugin_settings__ = {
    "level": 5,
    "default_status": True,
    "limit_superuser": False,
    "cmd": ["抽群老婆", "我的群老婆", "呼叫老婆"],
}


draw_wife = on_command("抽群老婆",permission=GROUP, priority=5, block=True)
my_wife = on_command("我的群老婆",permission=GROUP, priority=5, block=True)
at_wife = on_command("呼叫老婆",permission=GROUP, priority=5, block=True)
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
        if time_pass < 180:
            time_rest = 180 - time_pass
            draw_refuse = [f'才过去了{time_pass}s时间,你就要换老婆了,真是始乱终弃呢',
                           f'不行不行，你的身体会受不了的，歇{time_rest}s再来吧',
                           f'合不合适起码相处三分钟再说吧'
                           ]    
            
            await draw_wife.finish(random.choice(draw_refuse), at_sender=True)
    except KeyError:
        pass
    group_user_wife[group][uid]['time'] = time.time()    
    wife_list = await GroupInfoUser.get_group_member_id_list(group)
    user_wife = int(random.choice(wife_list))
    while user_wife == uid:
        user_wife = int(random.choice(wife_list))
    group_user_wife[group][uid]['wife'] = {}
    group_user_wife[group][uid]['wife']['qq'] = user_wife
    wife_name = (await GroupInfoUser.get_member_info(user_wife, group)).user_name
    group_user_wife[group][uid]['wife']['name'] = wife_name
    url = f"http://q1.qlogo.cn/g?b=qq&nk={user_wife}&s=640"
    group_user_wife[group][uid]['wife']['icon'] = url
    msg_tuple = (f'你的群老婆是{wife_name}', image(url), "好好相处哦")
    await draw_wife.finish(Message(msg_tuple), at_sender=True)

@my_wife.handle()
async def _(bot: Bot,
            event: GroupMessageEvent,
            state: T_State,
            args: Message = CommandArg(),
            ):
        global group_user_wife
        uid = event.user_id
        group = event.group_id
        try:
            if not group_user_wife[group][uid]:
                await my_wife.finish('你还没有抽群老婆哦', at_sender=True)
            else:
                wife_name = group_user_wife[group][uid]['wife']['name']
                wife_avatar = group_user_wife[group][uid]['wife']['icon'] 
                msg_tuple = (f'你当前的群老婆是{wife_name}', image(wife_avatar))
                await my_wife.send(Message(msg_tuple), at_sender=True)
        except KeyError:
            await my_wife.finish("你还没有抽群老婆哦", at_sender=True)

@at_wife.handle()
async def _(bot: Bot,
            event: GroupMessageEvent,
            state: T_State,
            args: Message = CommandArg(),
            ):
        global group_user_wife
        uid = event.user_id
        group = event.group_id
        try:
            if not group_user_wife[group][uid]:
                await my_wife.finish('你还没有抽群老婆哦', at_sender=True)
            else:
                wife_qq = group_user_wife[group][uid]['wife']['qq']
                msg = at(wife_qq)
                await at_wife.send(msg)
        except KeyError:
            await my_wife.finish('你还没有抽群老婆哦', at_sender=True)  
            
        








