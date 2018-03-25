# Standard library import
from datetime import datetime, timedelta
import json
import os
import logging

# Django library import

# 3rd party library import
from wxpy.exceptions import ResponseError
from wxpy.api.chats.group import Group as WechatGroup
from wxpy.api.chats.mp import MP as WechatMP
from itchat.signals import scan_qr_code, confirm_login, logged_out
from django_sse.redisqueue import send_event

# project import
from .settings import AVATAR_TMPL, WECHAT_AVATAR_PATH
from .models import User, Group, MP
from .redis import Notification


logger = logging.getLogger(__name__)


def _get_fields(cls, exc_fields=None):
    return [i.name for i in cls._meta.get_fields() if not exc_fields or i.name not in exc_fields]

BOT_TO_DB_OBJ_MAP = {
    WechatGroup: {'Model': Group, 'Fields': _get_fields(Group, ['owner'])},
    WechatMP: {'Model': MP, 'Fields': _get_fields(MP)},
    # Wechat User, Friend, Member obj will saved to User table
    'Others': {'Model': User, 'Fields': _get_fields(User)},
}


def publish(uuid, **kwargs):
    data = {'uuid': uuid, 'extra': kwargs.pop('extra', None), 'type': kwargs.pop('type', None)}
    data.update(kwargs)
    send_event(event_name='login', data=json.dumps(data), channel='wechat')


scan_qr_code.connect(publish)
confirm_login.connect(publish)
logged_out.connect(publish)


def clean_msg_notify(receiver_id):
    """
    Delete new message notification key in redis for logged-in user after logout

    :param receiver_id: user PUID retrieved from wxpy.bot
    """
    Notification.clean_by_receiver_id(receiver_id)


def new_msg_notify(receiver_id, clean=False):
    """
    Publish new message notification to redis for the user, then FE listener could get new message count

    :param receiver_id: user PUID retrieved from wxpy.bot
    :param clean: indicate whether to delete the corresponding key in redis
    """
    if clean:
        clean_msg_notify(receiver_id)
    event_name = 'notification'
    data = {'count': Notification.count_by_receiver_id(receiver_id)}
    send_event(event_name=event_name, data=json.dumps(data), channel='wechat')


def get_valid_params(query_params):
    """Get valid query parameters from FE request"""
    return {k: v for k, v in query_params.items() if k not in ['page', 'page_size'] and v}


def filter_queryset(queryset, query_params):
    """Filter queryset result according to FE pass query parameters"""
    query_paras = get_valid_params(query_params)
    if query_paras:
        try:
            # if FE send parameter which not found in DB, return original queryset, and log the error
            queryset = queryset.filter(**query_paras)
        except Exception as e:
            logger.error(e)

    return queryset


def crt_paths(*dir_list):
    for dir in dir_list:
        crt_path(dir)


def crt_path(path):
    base_path = os.path.dirname(path)
    if not os.path.exists(base_path):
        os.makedirs(base_path)


def gen_avatar_path(_user, force=False):
    """
    Get avatar from User instance's get_avatar method, save the avatar in avatar_path(retrieve from settings)

    :param _user: wxpy User instance
    :param force: whether force to update the avatar
    :return:
        avatar_url: '/static/img/avatars/{}.jpg' where {} to be filled with user puid
        avatar_path: avatar saved path, retrieve from wechat.settings.py
        need_update: True/False
    """
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


def remove_old_objs(new_obj, values):
    """
    After new model instance is created/updated, check whether same values with different PUID exists in database,
    if yes, delete the old model instances

    :param new_obj: new model instance created/updated for model User/Group/MP
    :param values: dict which used to save new_obj
    """
    try:
        values.pop('puid')
        old_objs = new_obj.__class__.objects.filter(**values).exclude(puid=new_obj.puid)
        logger.info(old_objs)
        for obj in old_objs:
            obj.delete()
            logger.info("Old obj {} is deleted".format(obj))
    except Exception as e:
        logger.error(e)


def crt_or_upd_obj(wc_obj):
    """
    Create or update model instance according to wxpy instance

    :param wc_obj: wxpy instance: User, Friend, Group, Member, MP
    :return: model instance created in database for the wxpy instance
    """

    try:
        if wc_obj.__class__ in BOT_TO_DB_OBJ_MAP:
            DB_MAP = BOT_TO_DB_OBJ_MAP[wc_obj.__class__]
        else:
            DB_MAP = BOT_TO_DB_OBJ_MAP['Others']

        MODEL_FIELDS = DB_MAP['Fields']
        values = {field: getattr(wc_obj, field) for field in MODEL_FIELDS if hasattr(wc_obj, field)}
        # logger.info('Before filter: {}'.format(values))
        values = {k: v for k, v in values.items() if v}
        # logger.info('After filter: {}'.format(values))
        kwargs = {'puid': wc_obj.puid}

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
    """
    Adapter for wxpy Bot/Group and model User/Group instance,
    accept different methods to retrieve friends, groups, mps, members
    """
    def __init__(self, obj, search_method, upd_method=None, update=False):
        """
        :param obj: wxpy Bot/Group or model User/Group instance
        :param search_method:
            for wxpy Bot/Group instance: bot.friends, bot.groups, bot.mps, group.members
            for model User/Group instance: user.friends, user.groups, user.mps, group.members
        :param upd_method:
            Model User instance method: user.del_friends, user.add_friend, user.del_groups, user.add_group,
                user.del_mps, user.add_mp
            Model Group instance method: group.del_members, group.add_member
        :param update: reserved for Bot instance to indicate whether to force updating wechat contacts
        """
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

    def get_deleted_puids(self):
        return self._old_puids.difference(self._new_puids)

    def get_db_delete_objs(self):
        return self._get_db_objs(self.get_deleted_puids())

    def _get_db_objs(self, puids):
        if self.db_adapter.search_method.__name__ == 'groups':
            objs = Group.objects.filter(puid__in=puids)
        elif self.db_adapter.search_method.__name__ == 'mps':
            objs = MP.objects.filter(puid__in=puids)
        else:
            # if method name in ('friends', 'members'), get objects from User model
            objs = User.objects.filter(puid__in=puids)

        return objs
