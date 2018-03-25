from werkzeug.local import LocalStack, LocalProxy
from wxpy import Bot

from .settings import WECHAT_CACHE_PATH, WECHAT_PUID_PATH, QR_PATH
from .func import crt_paths

import logging
logger = logging.getLogger(__name__)


def get_bot():
    # logger.info(WECHAT_CACHE_PATH)
    # logger.info(WECHAT_PUID_PATH)
    # logger.info(QR_PATH)
    crt_paths(WECHAT_CACHE_PATH, WECHAT_PUID_PATH, QR_PATH)
    bot = Bot(cache_path=WECHAT_CACHE_PATH, console_qr=None, qr_path=QR_PATH)
    bot.enable_puid(WECHAT_PUID_PATH)
    # bot.messages.max_history = 0
    logger.info(bot.self.puid)
    return bot

# current_bot = get_bot()


def _find_bot():
    # from .func import get_bot
    top = _wx_ctx_stack.top
    if top is None:
        top = get_bot()
        _wx_ctx_stack.push(top)
    return top


_wx_ctx_stack = LocalStack()
current_bot = LocalProxy(_find_bot)
