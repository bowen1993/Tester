from .runner import Runner
from db_watcher import DBWatcher
import os
if __name__ == '__main__':
    print 'Hello World'
    runner = Runner()
    watcher = DBWatcher(runner_obj=runner)
    watcher.watching()
    # w = DBWatcher()
    # w.watching()