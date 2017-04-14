from ..abstract_test_task import abstract_test_task
from ..DBActions import *
from ..FHIRTest_Sandbox.FHIR_Operation import basic_fhir_operations, fhir_test_cases
from ..FHIRTest_Sandbox import test_helper
import os
import json

class FHIRResourceTest(abstract_test_task):
    def __init__(self, task_id, runner_obj, version, resources=[], server_info=None):
        super(FHIRResourceTest, self).__init__(task_id, runner_obj)
        self.resources = resources
        self.server_info = server_info
        self.token = None
        self.version = version
        self.id_dict = {}

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
        print 'finish'
        update_a_task(self.task_id, {
            "code_status": 'S' if isAllSuccess else 'F'
        })
        task_obj = get_task(self.task_id)
        if task_obj:
            print 'create result'
            result_obj = create_a_result({
                "code_status": 'S' if isAllSuccess else 'F'
            })
            push_result2task(self.task_id, result_obj)
        self.runner_obj.notify_completed(self.task_id)
    
    def task_status(self):
        return 'PROC'

    def __excute_resource_read(self, resource_type, step_id):
        '''
        read a resource with server
        '''
        isSuccessful, response_json = basic_fhir_operations.read_fhir_resource(self.server_info["url"], resource_type, self.token)
        print isSuccessful
        json_str = ''
        try:
            json_str = json.dumps(response_json)
        except:
            pass
        case_obj = create_a_case({
            "code_status": "S" if isSuccessful else "F",
            "name": "%s.Read" % resource_type,
            "description": "%s can be readed" % resource_type,
            "http_response": json_str
        })
        if case_obj:
            push_case2step(step_id, case_obj)
        return (not case_obj is None) and isSuccessful
    
    def __excute_resource_write(self, resource_type, step_id):
        '''
        write a resource to server
        '''
        #get test cases
        correct_cases = fhir_test_cases.get_resource_correct_cases(self.version, resource_type)
        wrong_cases = fhir_test_cases.get_resource_wrong_cases(self.version, resource_type)
        #res, self.id_dict = test_helper.create_pre_resources(self.server_info['url'], self.token)
        # test with correct cases
        # TODO: test with correct/wrong cases into methods
        isCorrectPassed = True
        if correct_cases:
            for case in correct_cases:
                case = test_helper.set_reference(case, self.server_info['url'], self.version, self.token, self.id_dict)
                isSuccessful, response_json = basic_fhir_operations.create_fhir_resource(self.server_info["url"],resource_type, case, self.token)
                if not isSuccessful:
                    isCorrectPassed = False
                    json_str = ''
                    try:
                        json_str = json.dumps(response_json)
                    except:
                        pass
                    case_obj = create_a_case({
                        "code_status": "F",
                        "name": "%s.Write" % resource_type,
                        "description": "%s in correct format can not be processed" % resource_type,
                        "http_response":json_str,
                        "resource": json.dumps(case)
                    })
                    if case_obj:
                        push_case2step(step_id, case_obj)
        if isCorrectPassed:
            case_obj = create_a_case({
                "code_status": "S",
                "name": "%s.Write" % resource_type,
                "description": "%s in correct format can be processed properly" % resource_type
            })
            if case_obj:
                push_case2step(step_id, case_obj)
        isWrongPassed = True
        if wrong_cases:
            for case in wrong_cases:
                case = test_helper.set_reference(case, self.server_info['url'], self.version, self.token, self.id_dict)
                isSuccessful, response_json = basic_fhir_operations.create_fhir_resource(self.server_info["url"],resource_type, case, self.token)
                if isSuccessful:
                    isWrongPassed = False
                    json_str = ''
                    try:
                        json_str = json.dumps(response_json)
                    except:
                        pass
                    case_obj = create_a_case({
                        "code_status": "W",
                        "name": "%s.Write" % resource_type,
                        "description": "%s in wrong format can not be processed" % resource_type,
                        "http_response": json_str,
                        "resource":json.dumps(case)
                    })
                    if case_obj:
                        push_case2step(step_id, case_obj)
        if isWrongPassed:
            case_obj = create_a_case({
                "code_status": "S",
                "name": "%s.Write" % resource_type,
                "description": "%s in wrong format can be processed properly" % resource_type
            })
            if case_obj:
                push_case2step(step_id, case_obj)
        return isCorrectPassed





