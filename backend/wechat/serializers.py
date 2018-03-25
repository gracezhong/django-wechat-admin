import logging
from wechat.models import User, MP, Group, Message
from rest_framework import serializers

logger = logging.getLogger(__name__)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('puid', 'nick_name', 'avatar', 'remark_name', 'sex', 'province', 'city', 'signature')


class MPSerializer(serializers.ModelSerializer):
    class Meta:
        model = MP
        fields = ('puid', 'nick_name', 'province', 'city', 'signature')


class GroupSerializer(serializers.ModelSerializer):
    owner = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Group
        fields = ('puid', 'owner', 'avatar', 'nick_name')


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(many=False, read_only=True)
    group = GroupSerializer(many=False, read_only=True)
    receiver = UserSerializer(many=False, read_only=True)
    # sender_id = serializers.SlugRelatedField(many=False, slug_field='puid', queryset=User.objects.all())
    # receiver_id = serializers.SlugRelatedField(many=False, slug_field='puid', queryset=User.objects.all())
    # group_id = serializers.SlugRelatedField(many=False, slug_field='puid', allow_null=True,
    #                                         queryset=Group.objects.all())

    class Meta:
        model = Message
        fields = ('id', 'sender', 'group', 'receiver', 'type',
                  'sender_id', 'receiver_id', 'group_id', 'content', 'receive_time',
                  'type', 'url', 'file_ext')

    def create(self, validated_data):
        logger.info(self.initial_data)
        logger.info(validated_data)
        logger.info(self.data)
        # todo SlugRelatedField usage
        # define 'sender_id' as SlugRelatedField
        # sender_id will be user instance
        # validated_data = {
        #     'type': 1, 'sender_id': <User c4f89447: 草凡>,
        #     'receiver_id': <User c4f89447: 草凡>, 'group_id': None,
        #     'content': 'test again',
        #     'receive_time': datetime.datetime(2018, 3, 19, 21, 50, 14, 779520, tzinfo=<DstTzInfo 'America/Chicago' CDT-1 day, 19:00:00 DST>)}
        # self.data = {
        #     'type': 1, 'sender_id': 'c4f89447', 'receiver_id': 'c4f89447',
        #     'group_id': None, 'content': 'test again', 'receive_time': '2018-03-19T21:50:14.779520-05:00'}

        # use validated_data can't save to DB successfully, use self.data can be saved to DB successfully
        # but if use SlugRelatedField, when FE pass a string in 'sender_id', it can't get puid attribute to initialize the user instance
        # then there will be error during rendering message list page, check further about this point

        # if not define sender_id as SlugRelatedField, even if FE pass sender_id,
        # validated_data won't have this field, only could retrieve from self.initial_data
        validated_data['sender_id'] = self.initial_data['sender_id']
        validated_data['receiver_id'] = self.initial_data['receiver_id']
        # if 'receiver_id' in self.initial_data['receiver_id']:
        #     validated_data['receiver_id'] = self.initial_data['receiver_id']
        #
        # if 'grp_receiver_id' in self.initial_data['grp_receiver_id']:
        #     validated_data['grp_receiver_id'] = self.initial_data['grp_receiver_id']

        if 'group_id' in self.initial_data:
            validated_data['group_id'] = self.initial_data['group_id']
        # message = Message.objects.create(**self.data)
        message = Message.objects.create(**validated_data)
        return message
