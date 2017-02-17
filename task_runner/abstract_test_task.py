from abc import ABCMeta, abstractmethod

class abstract_test_task:
    __metaclass__ = ABCMeta

    def __init__(self, task_id, runner_obj):
        self.task_id = task_id
        self.runner_obj = runner_obj
        
    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def task_status(self):
        pass

    
