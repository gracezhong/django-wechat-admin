# import logging
# import sys
#
# from .serializers import UserSerializer, MPSerializer, GroupSerializer, MessageSerializer
# from .pagination import WechatPagination
# from .globals import current_bot, _wx_ctx_stack
# from .func import get_logged_in_user, new_msg_notify
# from .settings import WECHAT_PKL_PATH
# from .redis import Notification
#
# __title__ = 'Django-wechat-admin'
# __version__ = '0.1.0.0'
# __author__ = 'Grace Zhong'
# # __license__ = 'MIT'
# __copyright__ = '2018, Grace Zhong'
#
# version_details = 'Django-wechat-admin {ver} from {path} (python {pv.major}.{pv.minor}.{pv.micro})'.format(
#     ver=__version__, path=__path__[0], pv=sys.version_info)