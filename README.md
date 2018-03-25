# django-wechat-admin

# Preview

![效果图](https://github.com/gracezhong/django-wechat-admin/blob/master/backend/screenshots/friend.png)
![效果图](https://github.com/gracezhong/django-wechat-admin/blob/master/backend/screenshots/group.png)
![效果图](https://github.com/gracezhong/django-wechat-admin/blob/master/backend/screenshots/message.png)

## 前言
该系统是参考[wechat-admin](https://github.com/dongweiming/wechat-admin)搭建的django-wechat-admin。
主要的技术栈：Django, Django REST, celery, Redis, sse。

## 目前已实现的功能
* 扫码登录后拉取微信好友、群、群成员、公众号信息 
* 显示好友／群聊／公众号列表，可过滤
* 发送微信信息
* 永久保存消息，可以通过消息列表页面查看和过滤。接收消息进程停止自动重启
* 新消息推送提醒


## 使用的技术和库

### 前端

* Vue
* Axios
* Element-ui
* Vue-cli

### 后端

* Django
* Django REST
* Celery
* [django-sse](https://github.com/niwinz/django-sse)
* Redis
* [ItChat](https://github.com/dongweiming/ItChat)
* [Wxpy](https://github.com/dongweiming/wxpy)
* MySQL


## 感谢
* [django-sse](https://github.com/niwinz/django-sse)
* [vue-admin](https://github.com/taylorchen709/vue-admin)
* [wxpy](https://github.com/youfou/wxpy)
* [ItChat](https://github.com/littlecodersh/ItChat)
