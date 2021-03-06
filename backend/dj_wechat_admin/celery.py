import os
from celery import Celery
from celery.signals import worker_ready
from wechat.redis import r, LISTENER_TASK_KEY

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dj_wechat_admin.settings')

app = Celery('dj_wechat_admin')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


@worker_ready.connect
def at_start(sender, **kwargs):
    with sender.app.connection() as conn:  # noqa
        task_id = sender.app.send_task('wechat.tasks.bot_msg_listener')
        r.set(LISTENER_TASK_KEY, task_id)
