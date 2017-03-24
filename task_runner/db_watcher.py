from .models import Task
import DBActions
from time import sleep
# TODO: finish DB Watcher, nofify runner obj when new task comes

class DBWatcher:
    def __init__(self, runner_obj=None, interval = 0.2):
        self.runner_obj = runner_obj
        self.interval = interval
        
    def watching(self):
        '''
        watching database, when new task come, add to runner pool
        '''
        while True:
            new_tasks = DBActions.get_unprocessed_task()
            # print new_tasks
            if new_tasks and new_tasks.count() > 0:
                # new task find
                for new_task in new_tasks:
                    print "New Task %s found" % new_task.id
                    new_task.is_processed = True
                    new_task.save()
                    # add task to runner
                    self.runner_obj.append_new_task(new_task.id)
            sleep(self.interval)
        

