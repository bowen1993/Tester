from ..abstract_test_task import abstract_test_task
from ..DBActions import *
from ..FHIRTest_Sandbox.FHIR_Operation import basic_fhir_operations, fhir_test_cases

class FHIRResourceTest(abstract_test_task):
    def __init__(self, task_id, runner_obj, resources=[], server_info=None):
        super(FHIRResourceTest, self).__init__(task_id, runner_obj)
        self.resources = resources
        self.server_info = server_info
        self.token = None

    def run(self):
        '''
        excute resource test
        '''
        # check server auth
        if self.server_info == None:
            update_a_task(task_id, {
                "code_status": 'F'
            })
            self.runner_obj.notify_completed(self.task_id)
            return
        
        if self.server_info["is_auth_required"]:
            self.token = basic_fhir_operations.basicOAuth(self.server_info["auth_info"], self.server_info["auth_url"])
        
        isAllSuccess = True
        for resource in self.resources:
            print "Testing %s" % resource["type"]
            step_obj = create_a_step({
                "name": resource["type"],
                "code_status": "PROC",
                "description": "Testing %s" % resource["type"]
            })
            #add step to current task
            if step_obj:
                push_step2task(self.task_id, step_obj)
            # test resource
            isStepSuccess = True
            if 'R' in resource['operation']:
                isStepSuccess = isStepSuccess and self.__excute_resource_read(resource["type"], step_obj.id)
            if 'W' in resource['operation']:
                isStepSuccess = isStepSuccess and self.__excute_resource_write(resource["type"], step_obj.id)
            
            update_a_step(step_obj.id, {
                "code_status": "S" if isStepSuccess else "F",
                "description": "%s test %s" % (resource["type"], ("successfully" if isStepSuccess else "failed"))
            })
            isAllSuccess = isAllSuccess and isStepSuccess
        update_a_task(self.task_id, {
            "code_status": 'S' if isAllSuccess else 'F'
        })
        self.runner_obj.notify_completed(self.task_id)
    
    def task_status(self):
        return 'PROC'

    def __excute_resource_read(self, resource_type, step_id):
        '''
        read a resource with server
        '''
        isSuccessful, response_json = basic_fhir_operations.read_fhir_resource(self.server_info["url"], resource_type, self.token)
        case_obj = create_a_case({
            "code_status": "S" if isSuccessful else "F",
            "name": resource_type,
            "description": "%s can be readed",
            "http_response": response_json
        })
        if case_obj:
            push_case2step(step_id, case_obj)
        return (case_obj is None) and isSuccessful
    
    def __excute_resource_write(self, resource_type, step_id):
        '''
        write a resource to server
        '''
        #get test cases
        correct_cases = fhir_test_cases.get_resource_correct_cases(resource_type)
        wrong_cases = fhir_test_cases.get_resource_wrong_cases(resource_type)
        # test with correct cases
        isCorrectPassed = True
        for case in correct_cases:
            isSuccessful, response_json = basic_fhir_operations.create_fhir_resource(self.server_info["url"],resource_type, case, self.token)
            if not isSuccessful:
                isCorrectPassed = False
                case_obj = create_a_case({
                    "code_status": "F",
                    "name": resource_type,
                    "description": "%s in correct format can not be processed" % resource_type,
                    "http_response":response_json,
                    "resource": case
                })
                if case_obj:
                    push_case2step(step_id, case_obj)
        if isCorrectPassed:
            case_obj = create_a_case({
                "code_status": "S",
                "name": resource_type,
                "description": "%s in correct format can be processed properly" % resource_type
            })
            if case_obj:
                push_case2step(step_id, case_obj)
            else:
                isCorrectPassed = False
        isWrongPassed = True
        for case in wrong_cases:
            isSuccessful, response_json = basic_fhir_operations.create_fhir_resource(self.server_info["url"],resource_type, case, self.token)
            if isSuccessful:
                isWrongPassed = False
                case_obj = create_a_case({
                    "code_status": "F",
                    "name": resource_type,
                    "description": "%s in wrong format can not be processed" % resource_type,
                    "http_response": response_json,
                    "resource":case
                })
                if case_obj:
                    push_case2step(step_id, case_obj)
        if isWrongPassed:
            case_obj = create_a_case({
                "code_status": "S",
                "name": resource_type,
                "description": "%s in correct format can be processed properly" % resource_type
            })
            if case_obj:
                push_case2step(step_id, case_obj)
                isWrongPassed = False
        return isCorrectPassed and isWrongPassed





