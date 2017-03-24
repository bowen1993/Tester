from __future__ import absolute_import, unicode_literals
from celery import Celery


app = Celery('task_runner',
             broker='redis://localhost:6379',
             include=['task_runner.tasks']
             )

app.config_from_object('task_runner.celeryconf')
if __name__ == '__main__':
    app.start()