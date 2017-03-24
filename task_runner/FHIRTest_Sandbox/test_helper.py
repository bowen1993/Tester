from .FHIR_Operation import basic_fhir_operations, fhir_test_cases

def test_write_resource(resource_type, operations):
    '''
    test a certain resource type with a certain operation (write or read)
    '''
    #get test cases
    correct_cases = fhir_test_cases.get_resource_correct_cases(resource_type)
    wrong_cases = fhir_test_cases.get_resource_wrong_cases(resource_type)
    #testing with correct cases
    