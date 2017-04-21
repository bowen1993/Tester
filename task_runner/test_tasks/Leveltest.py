from ..abstract_test_task import abstract_test_task
from ..DBActions import *
from ..FHIRTest_Sandbox.FHIR_Operation import basic_fhir_operations, fhir_test_cases
from ..FHIRTest_Sandbox import test_helper
import json
import os

genetic_profile_extensions = [
    {
      "url": "http://hl7.org/fhir/StructureDefinition/observation-geneticsDNASequenceVariantName",
      "valueCodeableConcept": {
        "text": "NG_007726.3:g.146252T>G"
      }
    },
    {
      "url": "http://hl7.org/fhir/StructureDefinition/observation-geneticsGene",
      "valueCodeableConcept": {
        "coding": [
          {
            "system": "http://www.genenames.org",
            "code": "3236",
            "display": "EGFR"
          }
        ]
      }
    },
    {
      "url": "http://hl7.org/fhir/StructureDefinition/observation-geneticsDNARegionName",
      "valueString": "Exon 21"
    },
    {
      "url": "http://hl7.org/fhir/StructureDefinition/observation-geneticsGenomicSourceClass",
      "valueCodeableConcept": {
        "coding": [
          {
            "system": "http://loinc.org",
            "code": "LA6684-0",
            "display": "somatic"
          }
        ]
      }
    }
]
gene_repository = [{"url": "http://1kgenomes.ga4gh.org/references/", "name": "ga4gh", "variantId": "A1A2"}]


ga4gh_url = "http://1kgenomes.ga4gh.org"

class Leveltest(abstract_test_task):
    def __init__(self, task_id, runner_obj, version, resources=[], server_info=None):
        super(Leveltest, self).__init__(task_id, runner_obj)
        self.resources = resources
        self.server_info = server_info
        self.token = None
        self.success_levels = []
        self.version = version
        self.id_dict = {}
    
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
            self.token = basic_fhir_operations.basicOAuth(self.server_info["auth_info"])
        for level in self.resources:
            test_method_name = "test_%s" % level
            getattr(self, test_method_name)()
        print 'finish'
        update_a_task(self.task_id, {
            "code_status": 'S' if len(self.success_levels) == len(self.resources) else 'F'
        })
        task_obj = get_task(self.task_id)
        if task_obj:
            #create results and with levels
            result_obj = create_a_result({
                "code_status": 'S' if len(self.success_levels) == len(self.resources) else 'F'
            })
            # add levels
            if result_obj:
                for level_name in self.success_levels:
                    level_obj = get_resource_wit_name(level_name, 1)
                    if level_obj:
                        push_level2result(result_obj.id, level_obj)
            push_result2task(self.task_id, result_obj)
        self.runner_obj.notify_completed(self.task_id)

    def task_status(self):
        # TODO: finish return task status
        return 'PROC'
    
    def test_0(self):
        '''
        level 0 test code
        '''
        #create step
        step_obj = create_a_step({
            "name": "Level 0",
            "code_status": "PROC",
            "description": "Level 0 Test Performing"
        })
        
        if step_obj:
            push_step2task(self.task_id, step_obj)
            isStepSuccess = self.__excute_resource_write("Observation", step_obj.id)
            update_a_step(step_obj.id, {
                "code_status": 'S' if isStepSuccess else 'F',
                "description": "Level 0 test %s" % ("successfully" if isStepSuccess else "failed")
            })
            if isStepSuccess:
                self.success_levels.append("0")
            
    
    def test_1(self):
        '''
        level 1 test code
        '''
        step_obj = create_a_step({
            "name": "Level 1",
            "code_status": "PROC",
            "description": "Level 1 Test Performing"
        })

        if step_obj:
            push_step2task(self.task_id, step_obj)
            isStepSuccess = self.__excute_resource_write("Observation", step_obj.id, genetic_profile_extensions)
            update_a_step(step_obj.id, {
                "code_status": "S" if isStepSuccess else 'F',
                "description": "Level 1 test %s" % ("successfully" if isStepSuccess else "failed")
            })
            if isStepSuccess:
                self.success_levels.append("1")
    
    def test_2(self):
        '''
        level 2 test code
        '''
        step_obj = create_a_step({
            "name": "Level 2",
            "code_status": "PROC",
            "description": "Level 2 Test Performing"
        })

        if step_obj:
            push_step2task(self.task_id, step_obj)
            isStepSuccess = self.__excute_resource_write("Observation", step_obj.id, genetic_profile_extensions)
            update_a_step(step_obj.id, {
                "code_status": "S" if isStepSuccess else 'F',
                "description": "Level 2 test %s" % ("successfully" if isStepSuccess else "failed")
            })
            if isStepSuccess:
                self.success_levels.append("2")
    
    def test_3(self):
        '''
        level 3 test code
        '''
        step_obj = create_a_step({
            "name": "Level 3",
            "code_status": "PROC",
            "description": "Level 3 Test Performing"
        })

        if step_obj:
            push_step2task(self.task_id, step_obj)
            isStepSuccess = self.__excute_resource_write("Sequence", step_obj.id)
            update_a_step(step_obj.id, {
                "code_status": 'S' if isStepSuccess else 'F',
                "description": "Level 3 test %s" % ("successfully" if isStepSuccess else "failed")
            })
            if isStepSuccess:
                self.success_levels.append("3")
    
    def test_4(self):
        '''
        level 4 test code
        '''
        step_obj = create_a_step({
            "name": "Level 4",
            "code_status": "PROC",
            "description": "Level 4 Test Performing"
        })

        if step_obj:
            push_step2task(self.task_id, step_obj)
            #get sequence resource
            sequence_resource_list = fhir_test_cases.get_resource_correct_cases(self.version, "Sequence")
            isSuccessful = False
            if sequence_resource_list and len(sequence_resource_list) > 0:
                sequence_resource = sequence_resource_list[0]
                sequence_resource = test_helper.set_reference(sequence_resource, self.server_info['url'], self.version, self.token, self.id_dict)
                sequence_resource['repository'] = gene_repository
                isSuccessful, response_json = basic_fhir_operations.create_fhir_resource(self.server_info["url"], "Sequence", sequence_resource, self.token)
                if isSuccessful:
                    resource_id = None
                    #get resource id
                    if response_json['resourceType'] == 'OperationOutcome':
                        try:
                            issue_desc = response_json['issue'][0]
                            if issue_desc['severity'] == 'information':
                                resource_id = issue_desc['diagnostics'].split('/')[1]
                        except:
                            pass
                    elif response_json['resourceType'] == 'Sequence':
                        try:
                            resource_id = response['id']
                        except:
                            pass
                    if resource_id and len(resource_id) != 0:
                        isRepoSuccessful, response_json = test_helper.read_repo("Sequence", resource_id, self.server_info['url'], ga4gh_url, self.token)
                        isSuccessful = isSuccessful & isRepoSuccessful
                    else:
                        isSuccessful = False
            json_str = ''
            try:
                json_str = json.dumps(response_json)
            except:
                pass
            case_obj = create_a_case({
                "code_status": 'S' if isSuccessful else 'F',
                "name": "Sequence",
                "description": 'Repository %s be read' % ('can' if isSuccessful else 'cannot'),
                "http_response": json_str
            })
            if case_obj:
                push_case2step(step_obj.id, case_obj)
            if isSuccessful:
                self.success_levels.append("4")

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
            "name": resource_type,
            "description": "%s can be readed" % resource_type,
            "http_response": json_str
        })
        if case_obj:
            push_case2step(step_id, case_obj)
        return (not case_obj is None) and isSuccessful

    def __excute_resource_write(self, resource_type, step_id, extensions=None):
        '''
        write a resource to server
        '''
        #get test cases
        correct_cases = fhir_test_cases.get_resource_correct_cases(self.version, resource_type)
        wrong_cases = fhir_test_cases.get_resource_wrong_cases(self.version, resource_type)
        #res, id_dict = test_helper.create_pre_resources(self.server_info['url'], self.token)
        # test with correct cases
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
                        "name": resource_type,
                        "description": "%s in correct format can not be processed" % resource_type,
                        "http_response":json_str,
                        "resource": json.dumps(case)
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
                        "name": resource_type,
                        "description": "%s in wrong format can not be processed" % resource_type,
                        "http_response": json_str,
                        "resource":json.dumps(case)
                    })
                    if case_obj:
                        push_case2step(step_id, case_obj)
        if isWrongPassed:
            case_obj = create_a_case({
                "code_status": "S",
                "name": resource_type,
                "description": "%s in wrong format can be processed properly" % resource_type
            })
            if case_obj:
                push_case2step(step_id, case_obj)
        return isCorrectPassed