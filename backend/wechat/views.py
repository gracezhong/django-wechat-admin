# Standard library import
import os
import glob
import logging
import json
import copy

# Django library import

# Django-rest library import
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, generics

# 3rd party library import
from django_sse.redisqueue import RedisQueueView, send_event

# project import
from dj_wechat_admin.celery import app
from .serializers import UserSerializer, MPSerializer, GroupSerializer, MessageSerializer
from .pagination import WechatPagination
from .globals import current_bot, _wx_ctx_stack
from .func import get_logged_in_user, get_user_info, new_msg_notify, \
    get_valid_params, filter_queryset, clean_msg_notify
from .models import Message
from .settings import WECHAT_PKL_PATH
from .redis import r, RETRIEVE_DATA_TASK_KEY, LISTENER_TASK_KEY


logger = logging.getLogger(__name__)


@api_view(['POST'])
def login(request):
    user = get_logged_in_user(current_bot)
    # user = get_user_info(current_bot)
    logger.info(current_bot.registered)
    logger.info(current_bot.listening_thread)
    logger.info(user)
    try:
        from wechat.tasks import retrieve_data
        rs = retrieve_data.delay(update=True)
        logger.info("任务id为: {}".format(rs.id))
        # r.set(RETRIEVE_DATA_TASK_KEY, rs.id)
    except Exception as e:
        logger.error(e)

    if user:
        serializer = UserSerializer(instance=user)
        data = {'type': 'logged_in', 'user': copy.deepcopy(serializer.data)}
        # data = {'type': 'logged_in', 'user': user}
        # send_event(event_name='login', data=json.dumps(data), channel=current_bot.self.puid)
        send_event(event_name='login', data=json.dumps(data), channel='wechat')
        task_id = app.send_task('wechat.tasks.bot_msg_listener')
        r.set(LISTENER_TASK_KEY, task_id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return Response(data, status=status.HTTP_201_CREATED)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def logout(request):
    try:
        _wx_ctx_stack.pop()
        if current_bot:
            logger.info(current_bot.self.puid)
            clean_msg_notify(current_bot.self.puid)

        for f in glob.glob('{}/*.pkl'.format(WECHAT_PKL_PATH)):
            try:
                os.remove(f)
                logger.info('pkl file: {} is removed after logout'.format(f))
            except FileNotFoundError:
                pass

        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(e)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class UserList(generics.ListCreateAPIView):
    serializer_class = UserSerializer
    pagination_class = WechatPagination
    # todo study further about below knowledge
    # lookup_field maps to key name in URL,
    # e.g. URL 'user/<int:pk>', kwargs = {'pk': 36}
    # lookup_field = 'pk'

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        logger.info(_wx_ctx_stack)
        logger.info(current_bot.self.puid)
        logger.info(current_bot.registered)
        logger.info(current_bot.listening_thread)
        user = get_logged_in_user(current_bot)

        if user:
            queryset = user.friends()
            logger.info(queryset)
            queryset = filter_queryset(queryset, self.request.query_params)
            return queryset.order_by('date_updated')


# ItChat不支持删除好友
class UserUpdate(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    lookup_field = 'puid'

    def get_queryset(self):
        user = get_logged_in_user(current_bot)
        if user:
            queryset = user.friends()
            return queryset

    def patch(self, request, *args, **kwargs):
        try:
            # use bot to update friend info, if successful, update DB accordingly
            logger.info(request.data)
            friend = current_bot.friends().search(puid=self.request.data['puid'])[0]
            friend.set_remark_name(self.request.data['remark_name'])
            return self.partial_update(request, *args, **kwargs)
        except Exception as e:
            logger.error(e)
            raise


class MPList(generics.ListCreateAPIView):
    serializer_class = MPSerializer
    pagination_class = WechatPagination

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `nick_name` query parameter in the URL.
        """
        logger.info(current_bot.self.puid)
        user = get_logged_in_user(current_bot)
        # queryset = MP.objects.filter(puid__in=get_mp_list(current_bot.self.puid))

        if user:
            queryset = user.mps()
            logger.info(queryset)
            queryset = filter_queryset(queryset, self.request.query_params)
            return queryset.order_by('date_updated')


class GroupList(generics.ListCreateAPIView):
    serializer_class = GroupSerializer
    pagination_class = WechatPagination

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `nick_name` query parameter in the URL.
        """
        logger.info(current_bot.self.puid)
        user = get_logged_in_user(current_bot)

        if user:
            queryset = user.groups()
            logger.info(queryset)
            queryset = filter_queryset(queryset, self.request.query_params)
            return queryset.order_by('date_updated')


class MessageList(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    pagination_class = WechatPagination

    # @method_decorator(new_msg_dec(receiver_id=current_bot.self.puid, clean=True))
    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `content` query parameter in the URL.
        """
        logger.info(current_bot.self.puid)
        # user = get_logged_in_user(current_bot)
        queryset = Message.objects.all()
        query_paras = get_valid_params(self.request.query_params)
        logger.info(query_paras)

        # if 'sender_id' in query_para_dict:
        #     sender_id = query_para_dict['sender_id']
        #     query_para_dict['sender_id'] = User.objects.get(puid=sender_id)

        if 'receiver_id' in query_paras:
            receiver_id = query_paras['receiver_id']
            new_msg_notify(receiver_id, clean=True)

        # if 'group_id' in query_para_dict:
        #     group_id = query_para_dict['group_id']
        #     query_para_dict['receiver_id'] = Group.objects.get(puid=group_id)

        # if need to filter like content__contains, pass ?content__contains=search value from FE
        queryset = filter_queryset(queryset, self.request.query_params)
        return queryset.order_by('-receive_time')

    def post(self, request, *args, **kwargs):
        logger.info(request.data)

        if request.data['group_id']:
            bot_receiver = current_bot.groups().search(puid=request.data['receiver_id'])[0]
        else:
            bot_receiver = current_bot.friends().search(puid=request.data['receiver_id'])[0]

        if bot_receiver:
            sent_msg = bot_receiver.send(request.data['content'])
            # request.data['type'] = MSG_TYPE_TO_ID_MAP.get(request.data['type'].upper(), 0)
            request.data['receive_time'] = sent_msg.receive_time
            logger.info(request.data)
            return self.create(request, *args, **kwargs)


class SSE(RedisQueueView):
    def get_redis_channel(self):
        # logger.info(self.args)
        # logger.info(self.kwargs)
        return self.kwargs['channel'] or self.redis_channel
