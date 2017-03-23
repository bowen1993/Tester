from .FHIR_Generator import Generator

version = "1.9.0"

def get_resource_correct_cases(resource_type):
    '''
    get correct resource objects for a certain resource type
    '''
    generator = Generator()
    generator.load_definition(version, resource_type)
    return generator.correct_cases()

def get_resource_wrong_cases(resource_type):
    '''
    get wrong resource objects for a certain resource type
    '''
    generator = Generator()
    generator.load_definition(version, resource_type)
    return generator.wrong_cases()