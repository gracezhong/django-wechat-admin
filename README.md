# django-wechat-admin

## 前言
该系统是参考[wechat-admin](https://github.com/dongweiming/wechat-admin)搭建的django-wechat-admin。
本人的目的是利用此项目学习后端技术：Django, Django REST, celery, Redis, sse，因此并没有实现很多微信机器人wxpy支持的功能。有兴趣继续添加wxpy功能的可自行增加。

## 已实现的功能
* 支持显示好友／群聊／公众号列表，可过滤
* 支持发送微信信息，仅支持文本信息
* 永久保存消息，可以通过消息列表页面查看和过滤。接收消息进程停止自动重启
* 支持新消息提醒


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
