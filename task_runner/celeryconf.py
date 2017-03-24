from kombu.serialization import registry
registry.enable('pickle')
registry.enable('application/x-python-serialize')
CELERY_ACCEPT_CONTENT = ['application/json','application/x-python-serialize']