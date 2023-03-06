import asyncio
import base64
from io import BytesIO
import os
from re import A
from tokenize import group
from unicodedata import name
from utils.data_utils import init_rank
from utils.message_builder import image , at
from nonebot import on_command
from nonebot.typing import T_State
from utils.image_utils import text2image
import httpx
from PIL import Image

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
from nonebot.params import CommandArg, Arg, ArgStr
from models.group_member_info import GroupInfoUser
from utils.utils import is_number
from utils.utils import scheduler
from utils.utils import get_message_img
from utils.http_utils import AsyncHttpx
from._model import fake_wife
from._model import My_wife
import json

path_ = os.path.dirname(__file__)
path_ = path_.replace('\\', '/')
res = str(path_) + "/fake_wife/"

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
    拟造老婆:
        拟造老婆 name 图片
        一人一次加入抽老婆行列
        不被发现就是匿名【doge】
    删除拟造老婆:
        删除拟造老婆
    群拟造老婆列表:
        群拟造老婆列表 
        
""".strip()
__plugin_des__ = "抽群老婆"
__plugin_cmd__ = ["抽群老婆", "我的群老婆", "呼叫老婆",'海王榜','拟造老婆',"删除拟造老婆","群拟造老婆列表"]
__plugin_type__ = ("群内小游戏",)
__plugin_version__ = 1.0
__plugin_author__ = "冰蓝色光点"
__plugin_settings__ = {
    "level": 5,
    "default_status": True,
    "limit_superuser": False,
    "cmd": ["抽群老婆", "我的群老婆", "呼叫老婆", '海王榜','拟造老婆',"删除拟造老婆","群拟造老婆列表"],
}

make_wife = on_command("拟造老婆",permission=GROUP, priority=5, block=True)
draw_wife = on_command("抽群老婆",permission=GROUP, priority=5, block=True)
my_wife = on_command("我的群老婆",permission=GROUP, priority=5, block=True)
at_wife = on_command("呼叫老婆",permission=GROUP, priority=5, block=True)
see_king = on_command("海王榜",permission=GROUP, priority=5, block=True)
famous_women = on_command('名媛榜',permission=GROUP, priority=5, block=True)
delfakewife = on_command("删除拟造老婆",permission=GROUP, priority=5, block=True)
fakewifelist = on_command("群拟造老婆列表",permission=GROUP, priority=5, block=True)
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
    wife_list = list(await GroupInfoUser.get_group_member_id_list(group))
    fake_wife_list = await get_all_fakewife(group)
    wife_list.extend(fake_wife_list)
    user_wife = int(random.choice(wife_list))
    while user_wife == uid:
        user_wife = int(random.choice(wife_list))
    record_count_in_json(group, user_wife)
    
    
    if isfakewife(user_wife):
        list_ = await get_fake_wife_info(group, user_wife)
        wife_name = list_[0]
        msg_tuple = (f'你的群老婆是\n{wife_name}', image(b64=pic2b64(list_[1])), "好好相处哦")
        await My_wife.wife_revise(group, uid, user_wife)
        await draw_wife.finish(Message(msg_tuple), at_sender=True) 
    else:
        wife_name = await GroupInfoUser.get_user_nickname(user_wife, group)
        url = f"http://q1.qlogo.cn/g?b=qq&nk={user_wife}&s=640"
        await My_wife.wife_revise(group, uid, user_wife)
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
        user_wife = await My_wife.wife_view(group, uid)
        if user_wife == 0:
            await my_wife.finish("你还没有抽群老婆哦", at_sender=True) 
        else:
            if isfakewife(user_wife):
                try:
                    list_ = await get_fake_wife_info(group, user_wife)
                    wife_name = list_[0]
                    msg_tuple = (f'你当前的群老婆是{wife_name}', image(b64=pic2b64(list_[1])), "好好相处哦")   
                except:
                    await my_wife.finish("你的老婆是拟造老婆，现已被创造者删除，请更换",at_sender=True)             
                await my_wife.finish(Message(msg_tuple), at_sender=True)
            else:
                wife_name = await GroupInfoUser.get_user_nickname(user_wife, group)
                url = f"http://q1.qlogo.cn/g?b=qq&nk={user_wife}&s=640"
                msg_tuple = (f'你当前的群老婆是\n{wife_name}', image(url))
                await my_wife.finish(Message(msg_tuple), at_sender=True)                
                
                
                

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
            if isfakewife(user_wife):
                try: 
                    list_ = await get_fake_wife_info(group, user_wife)
                    name = list_[0]
                    msg = "@" + f"{name}"
                except:
                    await at_wife.finish("你的老婆是拟造老婆，现已被创造者删除，请更换",at_sender=True)
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
    all_user_id = [user.my_qq for user in all_users]
    all_user_data = [int(user.count_draw) for user in all_users]
    rank_image = await init_rank("海王排行榜", all_user_id, all_user_data, event.group_id, num)
    if rank_image:
        await see_king.finish(image(b64=rank_image.pic2bs4()))

@famous_women.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    num = arg.extract_plain_text().strip()
    if is_number(num) and 51 > int(num) > 10:
        num = int(num)
    else:
        num = 10
    data = get_group_data_in_json(event.group_id)
    
    all_user_id = list(data.keys())
    all_user_data = [data[uid] for uid in all_user_id]
    rank_image = await init_rank("名媛排行榜", all_user_id, all_user_data, event.group_id, num)
    if rank_image:
        await famous_women.finish(image(b64=rank_image.pic2bs4()))

@make_wife.handle()
async def _(bot: Bot,
            event: GroupMessageEvent,
            state: T_State,
            arg: Message = CommandArg(),
            ):
    args = arg.extract_plain_text().strip()
    img_list = get_message_img(event.json())
    if len(args) > 0:
        state["name"] = args
    if img_list:
        state["img_list"] = arg
        
@make_wife.got("name",  prompt="请输入名字")
@make_wife.got("img_list", prompt="请发送图片")
async def _(
    bot: Bot,
    event: MessageEvent,
    state: T_State,
    name: str = ArgStr("name"),
    img_list: Message = Arg("img_list"),
):  
    uid = event.user_id * 10000
    group = event.group_id
    if not get_message_img(img_list):
        await make_wife.reject_arg("img_list", "图呢图呢图呢图呢！GKD！")
    img_list = get_message_img(img_list)
    img_url = img_list[0]
    pil = await get_pic_pil(img_url)
    pil.save(res + f'{group}_{uid}.png')
    await asyncio.sleep(2)
    path = res + f"{group}_{uid}.png"
    pil = Image.open(path)
    await fake_wife.make_wife(group, uid, name)
    msg_tuple = (f'成功拟造群老婆\n{name}', image(b64=pic2b64(pil)))
    await make_wife.finish(Message(msg_tuple), at_sender=True)    

@delfakewife.handle()
async def _(bot: Bot,
            event: GroupMessageEvent,
            state: T_State,
            args: Message = CommandArg(),
            ):
    uid = event.user_id * 10000
    group = event.group_id   
    await fake_wife.del_wife(group, uid)
    path = res + f"{group}_{uid}.png"
    os.remove(path)
    await delfakewife.finish("成功删除你的拟造老婆", at_sender=True)

@fakewifelist.handle()
async def _(bot: Bot,
            event: GroupMessageEvent,
            state: T_State,
            args: Message = CommandArg(),
            ):
    group = event.group_id
    query = await fake_wife.get_all(group)
    list = [user.name for user in query]
    text = ''
    count = 0
    for i in list:
        count += 1
        text += i
        text += '  '
        if count % 10 == 0:
            text += '\n'
    await fakewifelist.finish(image(b64=(await text2image(text, color="#f9f6f2", padding=10)).pic2bs4()))



async def get_all_fakewife(group):
    query = await fake_wife.get_all(group)
    list = [user.uid for user in query]
    return list

async def get_pic_pil(url):
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=20)
    resp.raise_for_status()
    pic = resp.content
    pil_return = Image.open(BytesIO(pic))
    return pil_return

def isfakewife(uid):
    if uid % 10000 == 0:
        return True
    else:
        return False

async def get_fake_wife_info(group, uid):
    list = []
    try:
        list.append(await fake_wife.get_name(group, uid))
        path = res + f"{group}_{uid}.png"
        pic = Image.open(path)
        list.append(pic)
        return list
    except:
        return False
             

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

def record_count_in_json(group, uid):
    group = str(group)
    uid = str(uid)
    with open(str(path_) + '/data.json', 'r') as f:
        data = json.load(f)
    if data.get(group):
        if data[group].get(uid):
            data[group][uid] += 1
        else:
            data[group][uid] = 1
    else:
        data[group] = {}
        data[group][uid] = 1
    
    with open(str(path_) + '/data.json', 'w') as f:
        json.dump(data, f)

def get_group_data_in_json(group):
    with open(str(path_) + '/data.json', 'r') as f:
        data = json.load(f) 
    return data[str(group)]
    
    
@scheduler.scheduled_job(
    "cron",
    hour=23,
    minute=50,
)
async def _():
    global group_user_wife
    group_user_wife = {}
    








