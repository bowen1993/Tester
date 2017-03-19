from .models import *

def get_task_object(task_id):
    try:
        task_obj = Task.objects.get(id=task_id)
        return task_obj
    except:
        return None

def get_unprocessed_task():
    try:
        unprocessed_tasks = Task.objects(is_processed=False)
        return unprocessed_tasks
    except:
        return None

def insert_task():
    new_task = Task(task_parameters="")
    new_task.save()
