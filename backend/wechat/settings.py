from wxpy.api.consts import *

import os

import logging
logger = logging.getLogger(__name__)

WECHAT_BASE_PATH = os.path.dirname(os.path.abspath(__file__))
WECHAT_PKL_PATH = os.path.join(WECHAT_BASE_PATH, 'static/pkl')
WECHAT_CACHE_PATH = os.path.join(WECHAT_PKL_PATH, 'wechat.pkl')
WECHAT_PUID_PATH = os.path.join(WECHAT_PKL_PATH, 'wechat_puid.pkl')
WECHAT_IMG_PATH = os.path.join(WECHAT_BASE_PATH, 'static/img')
WECHAT_AVATAR_PATH = os.path.join(WECHAT_BASE_PATH, 'static/img/avatars')
MSG_UPLOAD_PATH = os.path.join(WECHAT_BASE_PATH, 'static/msg_uploads')
QR_PATH = os.path.join(WECHAT_IMG_PATH, 'qr_code.png')
AVATAR_TMPL = '/static/img/avatars/{}.jpg'

GENDER_CHOICES = ((MALE, 'MALE'), (FEMALE, 'FEMALE'))

MSG_TYPE_TO_ID_MAP = {
    'Default': 0,
    TEXT: 1,
    MAP: 2,
    CARD: 3,
    NOTE: 4,
    SHARING: 5,
    PICTURE: 6,
    RECORDING: 7,
    ATTACHMENT: 8,
    VIDEO: 9,
    FRIENDS: 10,
    SYSTEM: 11,
    'MP': 12
}

MSG_TYPE_TO_ID_MAP = {k.upper(): v for k, v in MSG_TYPE_TO_ID_MAP.items()}

MSG_ID_TO_TYPE_MAP = {v: k for k, v in MSG_TYPE_TO_ID_MAP.items()}

MESSAGE_TYPE_CHOICES = tuple((v, k) for k, v in MSG_TYPE_TO_ID_MAP.items())
