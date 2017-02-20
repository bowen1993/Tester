from __future__ import absolute_import, unicode_literals
from .celery import app

@app.task
def excute_task(task_obj):
    task_obj.run()