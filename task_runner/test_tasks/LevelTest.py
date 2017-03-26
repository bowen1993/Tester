from ..abstract_test_task import abstract_test_task
from ..DBActions import *
from ..FHIRTest_Sandbox.FHIR_Operation import basic_fhir_operations, fhir_test_cases
from ..FHIRTest_Sandbox import test_helper

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
gene_repository = [{"url": "https://www.googleapis.com/genomics/v1beta2", "name": "ga4gh", "variantId": "A1A2"}]


ga4gh_url = "http://1kgenomes.ga4gh.org"

class Leveltest(abstract_test_task):
    def __init__(self, task_id, runner_obj, levels=[], server_info=None):
        self.levels = levels
        self.server_info = server_info
        self.token = None
        self.success_levels = []
    
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
        #create step
        step_obj = create_a_step({
            "nane": "Level 0",
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
            
    
    def __test_1(self):
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
    
    def __test_2(self):
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
    
    def __test_3(self):
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
    
    def __test_4(self):
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
            sequence_resource_list = fhir_test_cases.get_resource_correct_cases("Sequence")
            isSuccessful = False
            if len(sequence_resource) > 0:
                sequence_resource = sequence_resource_list[0]
                sequence_resource = test_helper.set_reference(sequence_resource, self.server_info['url'], self.token)
                sequence_resource['repository'] = gene_repository
                isSuccessful, response_json = basic_fhir_operations.create_fhir_resource(self.server_info["url"], "Sequence", sequence_resource, self.token)
                if isSuccessful:
                    resource_id = None
                    #get resource id
                    if response['resourceType'] == 'OperationOutcome':
                        try:
                            issue_desc = response['issue'][0]
                            if issue_desc['severity'] == 'information':
                                resource_id = issue_desc['diagnostics'].split('/')[1]
                        except:
                            pass
                    elif response['resourceType'] == 'Sequence':
                        try:
                            resource_id = response['id']
                        except:
                            pass
                    if resource_id and len(resource_id) != 0:
                        isRepoSuccessful, response_json = test_helper.read_repo("Sequence", resource_id, self.server_info['url'], ga4gh_url, self.token)
                        isSuccessful = isSuccessful & isRepoSuccessful
                    else:
                        isSuccessful = False
            case_obj = create_a_case({
                "code_status": 'S' if isSuccessful else 'F',
                "name": "Sequence",
                "description": 'Repository %s be read' % ('can' if isSuccessful else 'cannot'),
                "http_response": response_json
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
        case_obj = create_a_case({
            "code_status": "S" if isSuccessful else "F",
            "name": resource_type,
            "description": "%s can be readed",
            "http_response": response_json
        })
        if case_obj:
            push_case2step(step_id, case_obj)
        return (not case_obj is None) and isSuccessful

    def __excute_resource_write(self, resource_type, step_id, extensions=None):
        '''
        write a resource to server
        '''
        #get test cases
        correct_cases = fhir_test_cases.get_resource_correct_cases(resource_type)
        wrong_cases = fhir_test_cases.get_resource_wrong_cases(resource_type)
        # test with correct cases
        # TODO: test with correct/wrong cases into methods
        isCorrectPassed = True
        for case in correct_cases:
            case = test_helper.set_reference(case, self.server_info['url'], self.token)
            if extensions:
                case['extension'] = extensions
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
            case = test_helper.set_reference(case, self.server_info['url'], self.token)
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
    