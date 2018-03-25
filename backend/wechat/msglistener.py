# Standard library import
import os
import logging

# 3rd party library import
# Others
from wxpy import Friend as _Friend, Group as _Group, MP as _MP
from wxpy.api import consts

# project import
from .globals import get_bot
from .models import Message, User, Group
from .redis import Notification
from .func import new_msg_notify
from .settings import MSG_TYPE_TO_ID_MAP, PICTURE, RECORDING, \
    ATTACHMENT, VIDEO, MSG_UPLOAD_PATH

logger = logging.getLogger('message')

bot = get_bot()
monitor_chats = [_Friend, _Group]
all_types = [k.capitalize() for k in dir(consts)
             if k.isupper() and k not in ('SYSTEM', 'FEMALE', 'MALE')]


# @bot.register(chats=monitor_chats, except_self=False)
@bot.register(msg_types=all_types, except_self=False)
def new_messages(msg):
    logger.info(msg.text)
    logger.info(msg.type)
    logger.info(msg.url)
    # wxpy还不支持未命名的群聊消息
    # 先忽略腾讯新闻之类发的信息
    if msg.receiver.name is None or msg.sender is None:
        return

    try:
        msg_type = MSG_TYPE_TO_ID_MAP.get(msg.type.upper(), 0)
        logger.info('msg_type= {}'.format(msg_type))
        group_id = ''

        if isinstance(msg.sender, _Group):
            sender_id = msg.member.puid
            group_id = msg.chat.puid
            logger.info('Group {} msg: sender id={}, nick_name={}, display_name={},'
                        .format(msg.sender.nick_name, sender_id, msg.member.nick_name, msg.member.display_name))
        elif isinstance(msg.sender, _MP):
            sender_id = msg.sender.puid
            msg_type = MSG_TYPE_TO_ID_MAP.get('MP')
            logger.info('msg_type= {}'.format(msg_type))
            logger.info('MP msg: sender id={}, nick_name={}'
                        .format(sender_id, msg.sender.nick_name))
        else:
            sender_id = msg.sender.puid
            logger.info('Other msg: sender id={}, nick_name={}, remark_name={}'
                        .format(sender_id, msg.sender.nick_name, msg.sender.remark_name))

        receiver_id = msg.receiver.puid
        logger.info('group_id: {}'.format(group_id))
        logger.info('receiver_id: {}'.format(receiver_id))
        sender = User.objects.get(puid=sender_id)
        logger.info('sender {}'.format(sender))
        receiver = User.objects.get(puid=receiver_id)
        logger.info('receiver {}'.format(receiver))

        new_msg = Message.objects.create(sender=sender, receiver=receiver, content=msg.text, url=msg.url,
                                         type=msg_type, receive_time=msg.receive_time)
        logger.info(new_msg)

        if Group.objects.filter(puid=group_id):
            group = Group.objects.filter(puid=group_id)[0]
            new_msg.group = group
            new_msg.save()

        if msg.type in (PICTURE, RECORDING, ATTACHMENT, VIDEO):
            _, ext = os.path.splitext(msg.file_name)
            logger.info(msg.file_name)
            logger.info(ext)
            msg.get_file(os.path.join(MSG_UPLOAD_PATH, '{}{}'.format(new_msg.id, ext)))
            new_msg.file_ext = ext
            new_msg.save()

        if receiver_id == bot.self.puid:
            Notification.add(receiver_id, new_msg.id)
            new_msg_notify(receiver_id)
    except Exception as e:
        logger.error(e)
