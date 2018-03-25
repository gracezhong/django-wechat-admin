# Standard library import
from datetime import datetime, timedelta
import json
import os
import logging
# from functools import wraps
# from functools import partial

# Django library import
# from django.core.exceptions import ObjectDoesNotExist

# 3rd party library import
# from wxpy import Bot
from wxpy.exceptions import ResponseError
from wxpy.api.chats.user import User as WechatUser
from wxpy.api.chats.group import Group as WechatGroup
from wxpy.api.chats.mp import MP as WechatMP
from wxpy.api.chats.member import Member as WechatMember
from itchat.signals import scan_qr_code, confirm_login, logged_out
from django_sse.redisqueue import send_event

# project import
from .settings import AVATAR_TMPL, WECHAT_AVATAR_PATH, WECHAT_CACHE_PATH, WECHAT_PUID_PATH, QR_PATH
from .models import User, Group, MP
from .redis import Notification


logger = logging.getLogger(__name__)


def _get_fields(cls, exc_fields=None):
    return [i.name for i in cls._meta.get_fields() if not exc_fields or i.name not in exc_fields]

# USER_FIELDS = [i.name for i in User._meta.get_fields()]
# GROUP_FIELDS = [i.name for i in Group._meta.get_fields() if i.name != 'owner']
# MP_FIELDS = [i.name for i in MP._meta.get_fields()]
BOT_TO_DB_OBJ_MAP = {
    # WechatUser: {'Model': User, 'Fields': _get_fields(User)},
    # WechatMember: {'Model': User, 'Fields': _get_fields(User)},
    WechatGroup: {'Model': Group, 'Fields': _get_fields(Group, ['owner'])},
    WechatMP: {'Model': MP, 'Fields': _get_fields(MP)},
    # Wechat User, Friend, Member obj will saved to User table
    'Others': {'Model': User, 'Fields': _get_fields(User)},
}



# def get_bot():
#     # logger.info(WECHAT_CACHE_PATH)
#     # logger.info(WECHAT_PUID_PATH)
#     # logger.info(QR_PATH)
#     crt_paths(WECHAT_CACHE_PATH, WECHAT_PUID_PATH, QR_PATH)
#     bot = Bot(cache_path=WECHAT_CACHE_PATH, console_qr=None, qr_path=QR_PATH)
#     bot.enable_puid(WECHAT_PUID_PATH)
#     # bot.messages.max_history = 0
#     logger.info(bot.self.puid)
#     return bot


def publish(uuid, **kwargs):
    data = {'uuid': uuid, 'extra': kwargs.pop('extra', None), 'type': kwargs.pop('type', None)}
    data.update(kwargs)
    send_event(event_name='login', data=json.dumps(data), channel='wechat')


scan_qr_code.connect(publish)
confirm_login.connect(publish)
logged_out.connect(publish)


def clean_msg_notify(receiver_id):
    Notification.clean_by_receiver_id(receiver_id)


def new_msg_notify(receiver_id, clean=False):
    if clean:
        clean_msg_notify(receiver_id)
    event_name = 'notification'
    data = {'count': Notification.count_by_receiver_id(receiver_id)}
    # send_event(event_name=event_name, data=json.dumps(data), channel=receiver_id)
    send_event(event_name=event_name, data=json.dumps(data), channel='wechat')


def get_valid_params(query_params):
    return {k: v for k, v in query_params.items() if k not in ['page', 'page_size'] and v}


def filter_queryset(queryset, query_params):
    query_paras = get_valid_params(query_params)
    if query_paras:
        try:
            # if FE send parameter which not found in DB, return original queryset, and log the error
            queryset = queryset.filter(**query_paras)
        except Exception as e:
            logger.error(e)

    return queryset


# def new_msg_dec(view_func, receiver_id, clean=False):
#     def wrapped_view(*args, **kwargs):
#         return view_func(*args, **kwargs)
#     new_msg_notify(receiver_id, clean)
#     return wraps(view_func)(wrapped_view)


def crt_paths(*dir_list):
    for dir in dir_list:
        crt_path(dir)


def crt_path(path):
    base_path = os.path.dirname(path)
    if not os.path.exists(base_path):
        os.makedirs(base_path)


def gen_avatar_path(_user, force=False):
    puid = _user.puid
    need_update = True
    avatar_url = AVATAR_TMPL.format(puid)
    avatar_path = os.path.join(WECHAT_AVATAR_PATH, '{}.jpg'.format(puid))
    crt_paths(avatar_path)

    if os.path.exists(avatar_path):
        mtime = datetime.fromtimestamp(os.stat(avatar_path).st_mtime)
        if datetime.now() - mtime < timedelta(days=1) and not force:
            need_update = False

    if need_update:
        try:
            _user.get_avatar(avatar_path)
        except ResponseError:
            logger.info('No member: {}'.format(_user.puid))

    return avatar_url, avatar_path, need_update


def get_user_info(bot):
    # return crt_or_upd_obj(bot.self)
    # user_ = bot.self
    # puid = bot.self.puid
    url, path, need_update = gen_avatar_path(bot.self, force=True)
    try:
        bot.core.get_head_img(picDir=path)
    except FileNotFoundError:
        os.mkdir(os.path.dirname(path))
        bot.core.get_head_img(picDir=path)
    user = {
        'puid': bot.self.puid,
        'avatar': url,
        'nick_name': bot.self.nick_name
    }
    return user


def get_logged_in_user(bot):
    return crt_or_upd_obj(bot.self)

# def get_logged_in_user(bot):
    # try:
    #     return User.objects.get(puid=bot.self.puid)
    # except ObjectDoesNotExist:
    #     pass


def remove_old_objs(new_obj, values):
    try:
        values.pop('puid')
        # logger.info(new_obj)
        # logger.info(values)
        old_objs = new_obj.__class__.objects.filter(**values).exclude(puid=new_obj.puid)
        logger.info(old_objs)
        for obj in old_objs:
            # logger.info(obj)
            obj.delete()
            logger.info("Old obj {} is deleted".format(obj))
    except Exception as e:
        logger.error(e)


def crt_or_upd_obj(wc_obj):
    # MODEL_FIELDS = None
    # logger.info(wc_obj)

    try:
        # wxpy Friend, Member, MP inherits wxpy User, so need to check MP first
        # if isinstance(wc_obj, WechatGroup):
        #     MODEL_FIELDS = GROUP_FIELDS
        # elif isinstance(wc_obj, WechatMP):
        #     MODEL_FIELDS = MP_FIELDS
        # elif isinstance(wc_obj, WechatUser):
        #     MODEL_FIELDS = USER_FIELDS
        if wc_obj.__class__ in BOT_TO_DB_OBJ_MAP:
            DB_MAP = BOT_TO_DB_OBJ_MAP[wc_obj.__class__]
        else:
            DB_MAP = BOT_TO_DB_OBJ_MAP['Others']

        MODEL_FIELDS = DB_MAP['Fields']

        if MODEL_FIELDS:
            values = {field: getattr(wc_obj, field) for field in MODEL_FIELDS if hasattr(wc_obj, field)}
            # logger.info('Before filter: {}'.format(values))
            values = {k: v for k, v in values.items() if v}
            # logger.info('After filter: {}'.format(values))
            kwargs = {'puid': wc_obj.puid}

            # wxpy Friend, Member, MP inherits wxpy User, so need to check MP first
            # if isinstance(wc_obj, WechatGroup):
            #     obj, created = Group.objects.update_or_create(defaults=values, **kwargs)
            # elif isinstance(wc_obj, WechatMP):
            #     obj, created = MP.objects.update_or_create(defaults=values, **kwargs)
            # elif isinstance(wc_obj, WechatUser):
            #     obj, created = User.objects.update_or_create(defaults=values, **kwargs)
            obj, created = DB_MAP['Model'].objects.update_or_create(defaults=values, **kwargs)

            # remove old objs with same values in DB(only PUID is updated)
            remove_old_objs(obj, values)

            if created:
                logger.info("{} {}: {} created in DB.".format(obj.__class__.__name__, obj.puid, obj.nick_name))
            else:
                logger.info("{} {}: {} updated in DB.".format(obj.__class__.__name__, obj.puid, obj.nick_name))

            if obj.__class__.__name__ in ['User', 'Group']:
                url, *_ = gen_avatar_path(wc_obj)
                obj.avatar = url
                obj.save()

            return obj
    except Exception as e:
        logger.error('Error: {}'.format(e))


class ChatAdapter(object):
    def __init__(self, obj, search_method, upd_method=None, update=False):
        # obj : bot, user, group object
        # method :
        #   bot methods: bot.friends(), bot.groups(), bot.mps(), bot.group()[0].members,
        #   model methods: user.friends(), user.groups(), user.mps(), group.members()
        # update : indicate whether bot refresh the contacts
        self.obj = obj
        self.search_method = search_method
        self.upd_method = upd_method
        self.update = update

    def __str__(self):
        return 'ChatAdapter object for {}.'.format(self.obj.__class__)

    __repr__ = __str__

    def __getattr__(self, item):
        return getattr(self.obj, item)

    def get_objs(self):
        try:
            if self.update:
                return self.search_method(self.update)
            else:
                return self.search_method()
        except TypeError:
            # if obj is bot Group, group.members will return a list, it's not callable and will raise TypeError
            return self.search_method

    def get_puids(self):
        return set([u.puid for u in self.get_objs() if u.puid])

    def do_update(self, objs):
        # model operation
        #   user.del_friends(deleted_objs)
        #   user.add_friend(new_obj)
        #   user.del_friends(deleted_friends)
        #   user.add_friend(new_user)
        #   user.del_mps(deleted_mps)
        #   user.add_mp(new_mp)
        #   user.del_groups(deleted_groups)
        #   user.add_group(group)
        #   group.del_members(deleted_members)
        #   group.add_member(new_user)
        # bot operation
        #   xxxx
        try:
            self.upd_method(objs)
        except Exception as e:
            logger.error('Error in calling {} for {}'.format(self.upd_method, self.obj.__class__))
            logger.error('Details: {}'.format(e))


class CompareClass(object):
    def __init__(self, bot_adapter, db_adapter):
        self.bot_adapter = bot_adapter
        self.db_adapter = db_adapter
        self._new_puids = self.get_new_puids()
        self._old_puids = self.get_old_puids()

    def get_new_puids(self):
        return self.bot_adapter.get_puids()

    def get_old_puids(self):
        return self.db_adapter.get_puids()

    def get_add_puids(self):
        return self._new_puids.difference(self._old_puids)

    def get_same_puids(self):
        return self._new_puids.intersection(self._old_puids)

    def get_deleted_puids(self):
        return self._old_puids.difference(self._new_puids)

    def get_db_same_objs(self):
        return self._get_db_objs(self.get_same_puids())

    def get_db_delete_objs(self):
        return self._get_db_objs(self.get_deleted_puids())

    def _get_db_objs(self, puids):
        # logger.info(self.db_adapter.search_method.__name__)
        if self.db_adapter.search_method.__name__ == 'groups':
            objs = Group.objects.filter(puid__in=puids)
        elif self.db_adapter.search_method.__name__ == 'mps':
            objs = MP.objects.filter(puid__in=puids)
        else:
            # if method name in ('friends', 'members'), get objects from User model
            objs = User.objects.filter(puid__in=puids)

        return objs

    def _get_bot_objs(self, puids):
        # logger.info(self.bot_adapter.search_method.__name__)
        if puids:
            pass
            # search in the results
            # return self.bot_adapter.get_objs().search
        else:
            return self.bot_adapter.get_objs()
