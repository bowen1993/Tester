from .models import *

def get_task_object(task_id):
    try:
        task_obj = Task.objects(id=task_id)
        return task_obj[0]
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

# CURD for Case
def create_a_case(case_info):
    new_case = Case(**case_info)
    try:
        new_case.save()
        return new_case
    except:
        return None

def get_case(case_id):
    try:
        caes_obj = Case.objects(id=case_id)
        return caes_obj[0]
    except:
        return None

def find_case(find_query):
    try:
        found_cases = Case.objects(**find_query)
        return found_cases
    except:
        return None

def update_a_case(case_id, update_info):
    try:
        Case.objects(id=case_id).update_one(**update_info)
        return True
    except:
        return False

#CURD for Step
def create_a_step(step_info):
    new_step = Step(**step_info)
    try:
        new_step.save()
        return new_step
    except:
        return None

def get_step(step_id):
    try:
        step_obj = Step.objects(id=step_id).first()
        return step_obj
    except:
        return None

def find_step(find_query):
    try:
        found_steps = Step.objects.(**find_query)
        return found_steps
    except:
        return None

def update_a_step(step_id, update_info):
    try:
        Step.objects(id=step_id).update_one(**update_info)
        return True
    except:
        return False

