from mongoengine import *
import datetime
from config import status_code

connect('fhirtest')

class User(Document):
    username = StringField(unique=True, required=True)
    password = StringField(required=True)
    user_level = IntField(required=True, default=0)
    meta = {
        'collection': 'users'
    }

class FHIRServer(Document):
    name = StringField(required=True, max_length=256)
    url = URLField(required=True)
    access_token = StringField(required=False)
    meta = {
        'collection': 'fhirservers'
    }

class Resource(Document):
    name = StringField(required=True, max_length=256)
    meta = {
        'collection': 'resources'
    }

class Level(Document):
    name = StringField(required=True)
    meta = {
        'collection': 'levels'
    }

class Case(Document):
    code_status = StringField(required=True, max_length=64, choices=status_code.keys())
    name = StringField(required=True)
    description = StringField()
    http_request = StringField()
    http_response = StringField()
    http_response_status = IntField()
    resource = StringField()
    @property
    def status(self):
        return status_code[self.code_status]
    meta = {
        'collection': 'cases'
    }

class Step(Document):
    name = StringField(required=True)
    code_status = StringField(required=True, max_length=64, choices=status_code.keys())
    description = StringField()
    additional_filepath = StringField()
    cases = ListField(ReferenceField(Case))
    @property
    def status(self):
        return status_code[self.code_status]
    meta = {
        'collection': 'steps'
    }

class TaskType(Document):
    name = StringField(required=True)
    task_class = StringField(required=True)
    meta = {
        'collection': 'tasktypes'
    }

class Task(Document):
    target_server = ReferenceField(FHIRServer, required=False)
    task_parameters = StringField()
    language = StringField(required=False, max_length=16)
    task_type = ReferenceField(TaskType, required=True)
    code_status = StringField(required=True, max_length=64, choices=status_code.keys())
    code = StringField(required=False)
    create_time = DateTimeField(default=datetime.datetime.now)
    user = ReferenceField(User, required=False)
    steps = ListField(ReferenceField(Step))
    is_processed = BooleanField(default=False)
    @property
    def status(self):
        return status_code[self.code_status]
    meta = {
        'collection': 'tasks'
    }

class Result(Document):
    task = ReferenceField(Task, required=True)
    code_status = StringField(required=True, max_length=64, choices=status_code.keys())
    level = ListField(ReferenceField(Level))
    @property
    def status(self):
        return status_code[self.code_status]
    meta = {
        'collection': 'results'
    }