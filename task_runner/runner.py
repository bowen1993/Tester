from .test_tasks import *
from .tasks import *

class Runner:
    def __init__(self, pool_size=-1):
        self.pendding_tasks = []
        self.processing_tasks = []
        self.pool_size = pool_size

    def __is_pool_full(self):
        return !self.pool_size != -1 and len(self.processing_tasks) - self.pool_size <= 0

    def __excute_next_task(self):
        if len(self.pendding_tasks) > 0:
            next_task_id = self.pendding_tasks.pop(0)
            next_task_obj = self.__create_new_task_obj(next_task_id)
            self.processing_tasks.append({
                'task_id':next_task_id,
                'task_obj': next_task_obj
            })

    def __create_new_task_obj(self, task_id):
        pass

    def append_new_task(self, task_id):
        self.pendding_tasks.append(task_id)
        if !self.__is_pool_full():
            self.__excute_next_task()

