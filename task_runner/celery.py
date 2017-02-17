from __future__ import absolute_import, unicode_literals
from celery import Celery

app = Celery('task_runner',
             broker='amqp://',
             backend='amqp://',
             include=['task_runner.tasks'])


if __name__ == '__main__':
    app.start()