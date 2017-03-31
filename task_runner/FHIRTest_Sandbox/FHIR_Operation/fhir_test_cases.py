from .FHIR_Generator import Generator
from .genomics_test_generator.fhir_genomics_test_gene import *
import os
version = "3.0.0"

spec_basepath = os.path.join(os.getcwd(), 'task_runner/resources/spec/')
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

#temp version

# def get_right_cases(resource_type):
#     basepath = os.path.join(os.getcwd(), 'task_runner/resources/resource_file')
#     filepath_list = []
#     for parentDir, dirnames, filenames in os.walk(basepath):
#         for filename in filenames:
#             if filename.endswith('json') and resource_type.lower() in filename.lower():
#                 resource_name = filename[:filename.find('_')] if '_' in filename else filename[:filename.find('.')]
#                 fullFilename = (parentDir if parentDir.endswith('/') else parentDir + '/') + filename
#                 if resource_name.lower() == resource_type.lower(): filepath_list.append(fullFilename)
#     #get json objs
#     cases = []
#     for fullFilename in filepath_list:
#         f = open(fullFilename, 'r')
#         cases.append(json.loads(f.read()))
#         f.close()
#     return cases

# def create_all_test_case4type(resource_spec_filename,resource_type):
#     #load spec
#     csv_reader = csv.reader(open(resource_spec_filename, 'r'))
#     detail_dict = trans_csv_to_dict(csv_reader)
#     del csv_reader
#     #generate all cases
#     test_cases = create_element_test_cases(detail_dict)
#     right_cases, wrong_cases = create_orthogonal_test_cases(test_cases)
#     #wrap test cases
#     all_cases = {}
#     all_cases['right'] = get_right_cases(resource_type)
#     all_cases['wrong'] = []
#     # for case in right_cases:
#     #     case['resourceType'] = resource_type
#     #     all_cases['right'].append(case)
#     # get right cases from files instead
#     for case in wrong_cases:
#         case['case']['resourceType'] = resource_type
#         all_cases['wrong'].append(case['case'])
#     #return all cases
#     return all_cases

# def get_resource_correct_cases(resource_type):
#     all_cases = create_all_test_case4type('%s%s.csv' % (spec_basepath, resource_type), resource_type)
#     return all_cases['right']

# def get_resource_wrong_cases(resource_type):
#     all_cases = create_all_test_case4type('%s%s.csv' % (spec_basepath, resource_type), resource_type)
#     return all_cases['wrong']