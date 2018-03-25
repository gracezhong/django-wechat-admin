import os
import logging

from django.db import models

from .settings import WECHAT_AVATAR_PATH, GENDER_CHOICES, \
    MESSAGE_TYPE_CHOICES, MSG_UPLOAD_PATH

logger = logging.getLogger(__name__)


class User(models.Model):
    puid = models.CharField('用户PUID', max_length=20, primary_key=True)
    nick_name = models.CharField('昵称', max_length=60, db_index=True)
    remark_name = models.CharField('备注名称', max_length=60, default='')
    sex = models.SmallIntegerField('性别', choices=GENDER_CHOICES, null=True)
    province = models.CharField('省份', max_length=20, default='')
    city = models.CharField('城市', max_length=20, default='')
    signature = models.CharField('个性签名', max_length=512, default='')
    avatar = models.CharField('头像', max_length=1024, default='')
    date_created = models.DateTimeField('创建时间', auto_now_add=True)
    date_updated = models.DateTimeField('更新时间', auto_now=True)

    def __str__(self):
        return '<User {}: {}>'.format(self.puid, self.nick_name)

    __repr__ = __str__

    def delete(self, *args, **kwargs):
        # delete the user's avatar file
        f = os.path.join(WECHAT_AVATAR_PATH, '{}.jpg'.format(self.puid))
        try:
            os.remove(f)
            logger.info('Avatar {} is removed.'.format(f))
        except FileNotFoundError:
            logger.error('Fail to remove avatar {}.'.format(f))

        # delete the user's friends, groups, mps
        self.del_friends(self.friends())
        self.del_groups(self.groups())
        self.del_mps(self.mps())

        super().delete(*args, **kwargs)

    def friends(self):
        flist = [u.friend.puid for u in Friendship.objects.filter(user__puid=self.puid)]
        return User.objects.filter(puid__in=flist)

    def is_friend(self, user):
        return Friendship.objects.filter(user__puid=user.puid, friend__puid=self.puid).count() > 0

    def add_friend(self, user):
        if not user.is_friend(self):
            Friendship.objects.create(user=self, friend=user)
            logger.info('Friend {} is added to user {}.'.format(user, self))

    def del_friend(self, user):
        if user.is_friend(self):
            Friendship.objects.get(user__puid=self.puid, friend__puid=user.puid).delete()
            logger.info('Friend {} is deleted for user {}.'.format(user, self))

    def del_friends(self, users):
        for user in users:
            self.del_friend(user)

    def groups(self):
        glist = [u.group.puid for u in GroupRelation.objects.filter(member__puid=self.puid)]
        return Group.objects.filter(puid__in=glist)

    def is_in_group(self, group):
        return GroupRelation.objects.filter(group__puid=group.puid, member__puid=self.puid).count() > 0

    def add_group(self, group):
        if not self.is_in_group(group):
            GroupRelation.objects.create(group=group, member=self)
            logger.info('Group {} is added to user {}.'.format(group, self))

    def del_group(self, group):
        if self.is_in_group(group):
            Group.objects.get(puid=group.puid).delete()
            logger.info('Group {} is deleted for user {}.'.format(group, self))

    def del_groups(self, groups):
        for group in groups:
            self.del_group(group)

    def mps(self):
        mlist = [u.mp.puid for u in MPRelation.objects.filter(user__puid=self.puid)]
        return MP.objects.filter(puid__in=mlist)

    def has_mp(self, mp):
        return MPRelation.objects.filter(mp__puid=mp.puid, user__puid=self.puid).count() > 0

    def add_mp(self, mp):
        if not self.has_mp(mp):
            MPRelation.objects.create(mp=mp, user=self)
            logger.info('MP {} is added to user {}.'.format(mp, self))

    def del_mp(self, mp):
        if self.has_mp(mp):
            MP.objects.get(puid=mp.puid).delete()
            logger.info('MP {} is deleted for user {}.'.format(mp, self))

    def del_mps(self, mps):
        for mp in mps:
            self.del_mp(mp)


class Group(models.Model):
    puid = models.CharField('群PUID', max_length=20, primary_key=True)
    owner = models.ForeignKey('User', on_delete=models.CASCADE, blank=True, null=True,
                              related_name='owner', related_query_name='owner')
    nick_name = models.CharField('昵称', max_length=60, db_index=True)
    avatar = models.CharField('头像', max_length=1024, default='')
    date_created = models.DateTimeField('创建时间', auto_now_add=True)
    date_updated = models.DateTimeField('更新时间', auto_now=True)

    def __str__(self):
        return '<Group {}: {}>'.format(self.puid, self.nick_name)

    __repr__ = __str__

    def delete(self, *args, **kwargs):
        # delete the user's avatar file
        f = os.path.join(WECHAT_AVATAR_PATH, '{}.jpg'.format(self.puid))
        try:
            os.remove(f)
            logger.info('Avatar {} is removed.'.format(f))
        except FileNotFoundError:
            logger.error('Fail to remove avatar {}.'.format(f))

        super().delete(*args, **kwargs)

    def members(self):
        mlist = [u.member.puid for u in GroupRelation.objects.filter(group__puid=self.puid)]
        return User.objects.filter(puid__in=mlist)

    def has_member(self, user):
        return GroupRelation.objects.filter(group__puid=self.puid, member__puid=user.puid).count() > 0

    def add_member(self, user):
        if not self.has_member(user):
            GroupRelation.objects.create(group=self, member=user)

    def del_member(self, user):
        if self.has_member(user):
            GroupRelation.objects.get(group__puid=self.puid, member__puid=user.puid).delete()

    def del_members(self, users):
        for user in users:
            self.del_member(user)


class MP(models.Model):
    puid = models.CharField('公众号PUID', max_length=20, primary_key=True)
    nick_name = models.CharField('昵称', max_length=60, db_index=True)
    province = models.CharField('省份', max_length=20, default='')
    city = models.CharField('城市', max_length=20, default='')
    signature = models.CharField('个性签名', max_length=512, default='')
    date_created = models.DateTimeField('创建时间', auto_now_add=True)
    date_updated = models.DateTimeField('更新时间', auto_now=True)

    def __str__(self):
        return '<MP {}: {}>'.format(self.puid, self.nick_name)

    __repr__ = __str__


class Friendship(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE,
                             related_name='user', related_query_name='user', db_index=True)
    friend = models.ForeignKey('User', on_delete=models.CASCADE,
                               related_name='friend', related_query_name='friend', db_index=True)
    date_created = models.DateTimeField('创建时间', auto_now_add=True)
    date_updated = models.DateTimeField('更新时间', auto_now=True)


class GroupRelation(models.Model):
    group = models.ForeignKey('Group', on_delete=models.CASCADE, db_index=True)
    member = models.ForeignKey('User', on_delete=models.CASCADE, db_index=True)
    date_created = models.DateTimeField('创建时间', auto_now_add=True)
    date_updated = models.DateTimeField('更新时间', auto_now=True)


class MPRelation(models.Model):
    mp = models.ForeignKey('MP', on_delete=models.CASCADE,
                           related_name='mp', related_query_name='mp', db_index=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE,
                             related_name='mpuser', related_query_name='mpuser', db_index=True)
    date_created = models.DateTimeField('创建时间', auto_now_add=True)
    date_updated = models.DateTimeField('更新时间', auto_now=True)


class Message(models.Model):
    group = models.ForeignKey('Group', on_delete=models.CASCADE, blank=True, null=True,
                              related_name='group', related_query_name='group')
    sender = models.ForeignKey('User', on_delete=models.CASCADE,
                               related_name='sender', related_query_name='sender')
    receiver = models.ForeignKey('User', on_delete=models.CASCADE,
                                 related_name='receiver', related_query_name='receiver')
    content = models.CharField('消息内容', max_length=1024, blank=True, null=True)
    type = models.SmallIntegerField('消息类型', choices=MESSAGE_TYPE_CHOICES)
    url = models.CharField(max_length=512, default='')
    file_ext = models.CharField(max_length=20, default='')
    receive_time = models.DateTimeField('接收时间')

    def __str__(self):
        return '<Message {1} type {0}: {2}>'.format(self.type, self.id, self.content)

    __repr__ = __str__

    def delete(self, *args, **kwargs):
        # delete the message's uploaded file
        f = os.path.join(MSG_UPLOAD_PATH, '{}{}'.format(self.id, self.file_ext))
        try:
            os.remove(f)
            logger.info('Msg uploaded file {} is removed.'.format(f))
        except FileNotFoundError:
            logger.error('Fail to remove msg uploaded file {}.'.format(f))

        super().delete(*args, **kwargs)
