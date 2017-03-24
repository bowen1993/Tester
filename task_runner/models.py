from mongoengine import *
import datetime
from .config import status_code

connect('fhirtest')

class User(Document):
    username = StringField(unique=True, required=True)
    password = StringField(required=True)
    user_level = IntField(required=True, default=0)
    meta = {
        'collection': 'users',
        'strict': False
    }

class ServerAuthScope(Document):
    name = StringField()
    meta = {
        'collection': 'serverauthscopes',
        'strict': False
    }

class ServerAuthInfo(Document):
    client_id = StringField(required=True, max_length=256)
    redirect_uri = StringField(required=True)
    scopes = ListField(ReferenceField(ServerAuthScope))
    auth_url = StringField(required=True)
    token_url = StringField(required=True)
    meta = {
        'collection': 'serverauthinfos',
        'strict': False
    }

class FHIRServer(Document):
    name = StringField(required=True, max_length=256)
    url = URLField(required=True)
    access_token = StringField(required=False)
    user = ReferenceField(User)
    is_open = BooleanField()
    is_deleted = BooleanField()
    is_deletable = BooleanField()
    is_auth_required = BooleanField()
    auth_info = ReferenceField(ServerAuthInfo)
    meta = {
        'collection': 'fhirservers',
        'strict': False
    }

class Resource(Document):
    name = StringField(required=True, max_length=256)
    meta = {
        'collection': 'resources',
        'strict': False
    }

class Level(Document):
    name = StringField(required=True)
    meta = {
        'collection': 'levels',
        'strict': False
    }

class Case(Document):
    code_status = StringField(required=True, max_length=64, choices=status_code.keys())
    name = StringField(required=True)
    description = StringField()
    http_request = StringField()
    http_response = StringField()
    http_response_status = IntField()
    resource = StringField()
    meta = {
        'collection': 'cases',
        'strict': False
    }

class Step(Document):
    name = StringField(required=True)
    code_status = StringField(required=True, max_length=64, choices=status_code.keys())
    description = StringField()
    additional_filepath = StringField()
    cases = ListField(ReferenceField(Case))
    meta = {
        'collection': 'steps',
        'strict': False
    }

class TaskType(Document):
    name = StringField(required=True)
    task_class = StringField(required=True)
    meta = {
        'collection': 'tasktypes',
        'strict': False
    }

class Task(Document):
    target_server = ReferenceField(FHIRServer, required=False)
    task_parameters = StringField()
    task_type = ReferenceField(TaskType)
    code_status = StringField(max_length=64, choices=status_code.keys())
    create_time = DateTimeField(default=datetime.datetime.now)
    user = ReferenceField(User, required=False)
    steps = ListField(ReferenceField(Step))
    is_processed = BooleanField(default=False)
    meta = {
        'collection': 'tasks',
        'strict': False
    }

class Result(Document):
    task = ReferenceField(Task, required=True)
    code_status = StringField(required=True, max_length=64, choices=status_code.keys())
    level = ListField(ReferenceField(Level))
    meta = {
        'collection': 'results',
        'strict': False
    }