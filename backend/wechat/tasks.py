# Standard library import
import os
import glob

# 3rd party library import
from celery import shared_task
from celery.utils.log import get_task_logger
from itchat.signals import logged_out
from wxpy.signals import stopped

# project import
from dj_wechat_admin.celery import app
from .globals import get_bot
from .func import ChatAdapter, CompareClass, get_logged_in_user, crt_or_upd_obj
from .redis import r, LISTENER_TASK_KEY


def restart_listener(sender, **kwarg):
    logger.info(sender)
    task_id = r.get(LISTENER_TASK_KEY)
    if task_id:
        logger.info(str(task_id, 'utf-8'))
        app.control.revoke(str(task_id, 'utf-8'), terminate=True)
    # task_id = app.send_task('wechat.tasks.bot_msg_listener')
    # r.set(LISTENER_TASK_KEY, task_id)

logger = get_task_logger('celery_tasks')
bot = get_bot()

logged_out.connect(restart_listener)
stopped.connect(restart_listener)


@shared_task
def retrieve_data(update=False):
    user = get_logged_in_user(bot)
    logger.info(bot.self.puid)
    _retrieve_data(user, update)


@shared_task
def bot_msg_listener():
    # 不用全局的bot，因为在import listener的过程中会
    # 注册各种函数（处理自动加群、接受消息、踢人以及各种插件功能
    task_id = r.get(LISTENER_TASK_KEY)
    if task_id:
        from wechat.msglistener import bot as _bot
        logger.info('Global bot PUID:{}'.format(bot.self.puid))
        logger.info('Global bot instance:{}'.format(bot))
        logger.info('Global bot registered info:{}'.format(bot.registered))
        logger.info('Global bot listening thread:{}'.format(bot.listening_thread))

        logger.info('Msg listener bot PUID:{}'.format(_bot.self.puid))
        logger.info('Msg listener bot instance:{}'.format(_bot))
        logger.info('Msg listener bot registered info:{}'.format(_bot.registered))
        logger.info('Msg listener bot listening thread:{}'.format(_bot.listening_thread))
        _bot.join()


def _retrieve_data(user, update=False):
    _update_friend(user, update)
    _update_group(user, update)
    _update_mp(user, update)


def _update_friend(user, update):
    bot_adapter = ChatAdapter(obj=bot, search_method=bot.friends, update=update)
    db_adapter = ChatAdapter(obj=user, search_method=user.friends)
    _update_chatobj(bot_adapter, db_adapter, user.del_friends, user.add_friend)


def _update_mp(user, update):
    bot_adapter = ChatAdapter(obj=bot, search_method=bot.mps, update=update)
    db_adapter = ChatAdapter(obj=user, search_method=user.mps)
    _update_chatobj(bot_adapter, db_adapter, user.del_mps, user.add_mp)


def _update_group(user, update):
    bot_adapter = ChatAdapter(obj=bot, search_method=bot.groups, update=update)
    db_adapter = ChatAdapter(obj=user, search_method=user.groups)
    _update_chatobj(bot_adapter, db_adapter, user.del_groups, user.add_group)


def _update_chatobj(bot_adapter, db_adapter, del_method, add_method):
    """
    Retrieve new contact list from bot_adapter and existing contact list from db_adapter,
    delete contacts which exist in DB but not in bot, then create/update new contacts in DB
    according to latest contact list retrieved from bot_adapter

    :param bot_adapter: ChatAdapter instance initialized with wxpy Bot/Group instance
    :param db_adapter: ChatAdapter instance initialized with model User/Group instance
    :param del_method:
        model User method: user.del_friends, user.del_groups, user.del_mps
        model Group method: group.del_members
    :param add_method:
        model User method: user.add_friend, user.add_group, user.add_mp
        model Group method: group.add_member
    """
    try:
        com_cls = CompareClass(bot_adapter, db_adapter)
        deleted_objs = com_cls.get_db_delete_objs()
        db_adapter.upd_method = del_method
        db_adapter.do_update(deleted_objs)

        i = 1
        # if add_method.__name__ == 'add_group':
        #     break_num = 1
        # else:
        #     break_num = 5

        # logger.info("只保存{}个新记录".format(break_num))
        db_adapter.upd_method = add_method
        # logger.info(db_adapter.upd_method.__name__)

        for bot_obj in bot_adapter.get_objs():
            # if add_method.__name__ != 'add_member' and i > break_num:
            #     break

            logger.info("保存{}的信息".format(bot_obj))
            db_obj = crt_or_upd_obj(bot_obj)

            if add_method.__name__ == 'add_group':
                # if it's to add group, after group is created in DB,
                # create group owner in User, and update to group.owner
                owner = crt_or_upd_obj(bot_obj.owner)
                db_obj.owner = owner
                db_obj.save()

            if db_obj:
                i += 1
                db_adapter.do_update(db_obj)

                # if it's add_group function, the new_obj is Group, need to add members under the group
                if add_method.__name__ == 'add_group':
                    bot_adapter2 = ChatAdapter(obj=bot_obj, search_method=bot_obj.members)
                    db_adapter2 = ChatAdapter(obj=db_obj, search_method=db_obj.members)
                    _update_chatobj(bot_adapter2, db_adapter2, db_obj.del_members, db_obj.add_member)
    except Exception as e:
        logger.error(e)
