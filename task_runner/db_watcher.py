from .models import Task

# TODO: finish DB Watcher, nofify runner obj when new task comes

class DBWatcher:
    def __init__(self, runner_obj, interval = 1):
        self.runner_obj = runner_obj
        self.interval = interval
        
    def watching(self):
