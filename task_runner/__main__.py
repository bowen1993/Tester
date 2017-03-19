from .runner import Runner
from db_watcher import DBWatcher
if __name__ == '__main__':
    print 'Hello World'
    w = DBWatcher()
    w.watching()