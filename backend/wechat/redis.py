import redis

r = redis.StrictRedis(host='localhost', port=6379, db=0)

NOTIFICATION_KEY = 'notification:{receiver_id}'
LISTENER_TASK_KEY = 'listener:task_id'
RETRIEVE_DATA_TASK_KEY = 'retrieve_data:task_id'


class Notification:
    @staticmethod
    def add(rid, msg_id):
        r.sadd(NOTIFICATION_KEY.format(receiver_id=rid), msg_id)

    @staticmethod
    def count_by_receiver_id(rid):
        return r.scard(NOTIFICATION_KEY.format(receiver_id=rid))

    @staticmethod
    def clean_by_receiver_id(rid):
        r.delete(NOTIFICATION_KEY.format(receiver_id=rid))
