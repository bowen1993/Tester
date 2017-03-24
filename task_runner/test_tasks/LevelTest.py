from ..abstract_test_task import abstract_test_task
from ..DBActions import *
from ..FHIRTest_Sandbox.FHIR_Operation import basic_fhir_operations, fhir_test_cases

class Leveltest(abstract_test_task):
    def __init__(self, task_id, runner_obj, levels=[], server_info=None):
        self.levels = levels
        self.server_info = server_info
        self.token = None
    
    def run(self):
        '''
        excute level test
        '''
        #server & auth
        if self.server_info == None:
            update_a_task(task_id,{
                "code_status": 'F'
            })
            self.runner_obj.notify_completed(self.task_id)
            return
        if self.server_info["is_auth_required"]:
            self.token = basic_fhir_operations.basicOAuth(self.server_info["auth_info"], self.server_info["auth_url"])
        # TODO: finish level test
        for level in self.levels:
            test_method_name = "__test_%s" % level

    def task_status(self):
        # TODO: finish return task status
        return 'PROC'
    
    def __test_0(self):
        '''
        level 0 test code
        '''
        correct_cases = fhir_test_cases.get_resource_correct_cases('Observation')
