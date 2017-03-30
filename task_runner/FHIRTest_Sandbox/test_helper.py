from .FHIR_Operation import basic_fhir_operations, fhir_test_cases
from .HTTP_Operation import basic_http_operation
import os
import json

base_resource_list = ['Patient','Device','Encounter','ImagingStudy','Media', 'Observation', 'Practitioner', 'Provenance','Specimen', 'DiagnosticRequest', 'Organization']

def create_pre_resources(url, access_token=None):
    #walk through all resource files
    print url
    basic_resource_path = os.path.join(os.getcwd(), 'task_runner/resources/json/')
    if not basic_resource_path.endswith('/'):
        basic_resource_path += '/'
    create_result = {}
    if url and len(url) != 0:
        filepath_dict = {}
        id_dict = {}
        print 'getting resource file'
        for parentDir, dirnames, filenames in os.walk(basic_resource_path):
            for filename in filenames:
                if filename.endswith('json'):
                    resource_name = filename[:filename.find('_')] if '_' in filename else filename[:filename.find('.')]
                    fullFilename = (parentDir if parentDir.endswith('/') else parentDir + '/') + filename
                    if resource_name in filepath_dict:
                        filepath_dict[resource_name].append(fullFilename)
                    else:
                        filepath_dict[resource_name] = [fullFilename]
        print 'file getted'
        for resource_name in base_resource_list:
            isSuccessful, ids = basic_fhir_operations.get_resources_ids(url, resource_name, access_token)
            print resource_name
            print ids
            if len(ids) > 0:
                id_dict[resource_name] = ids
                print '%s exists, passing' % resource_name
                continue
            for fullFilename in filepath_dict[resource_name]:
                resource_file = open(fullFilename, 'r')
                resource_obj = json.loads(resource_file.read())
                isSuccessful, response = basic_fhir_operations.create_fhir_resource(url, resource_name, resource_obj)
                create_result[resource_name] = response
                isSuccessful, ids = basic_fhir_operations.get_resources_ids(url, resource_name, access_token)
                if ids:
                    id_dict[resource_name] = ids
    return create_result, id_dict

def set_reference(resource_obj, server_url, access_token=None, id_dict={}):
    '''
    resource reference id correction
    '''
    print resource_obj, server_url
    if not isinstance(resource_obj, dict):
        return resource_obj
    for key in resource_obj:
        item = resource_obj[key]
        if isinstance(item, unicode) or isinstance(item, str):
            if key.lower() == 'reference':
                #reference type, change reference id, if not found in id dict, retrive from server, if server has none, create new
                reference_type = item[:item.find('/')]
                print reference_type
                if reference_type in id_dict:
                    resource_obj[key] = '%s/%s' % (reference_type, id_dict[reference_type][0])
                else:
                    #retrive from server
                    isSuccess, id_list = basic_fhir_operations.get_resources_ids(server_url, reference_type, access_token)
                    print id_list
                    if len(id_list) > 0:
                        resource_obj[key] = '%s/%s' % (reference_type, id_list[0])
                        id_dict[reference_type] = id_list
            else:
                continue
        if isinstance(item, list):
            for element in item:
                element = set_reference(element, server_url, access_token, id_dict)
        if isinstance(item, dict):
            item = set_reference(item, server_url, access_token, id_dict)
    return resource_obj

def read_repo(resource_type, resource_id, url, ga4gh_url, access_token):
    print resource_id
    print 'reading repo'
    isSuccessful, response_json = basic_fhir_operations.read_one_resource(url, resource_type, resource_id, access_token)
    if isSuccessful:
        isReadSuccess = True
        variantId = None
        print 'response'
        print response_json['repository']
        #get variant id
        try:
            variantId = response_json['repository'][0]['variantId']
        except:
            pass
        print variantId
        if variantId and len(variantId) != 0:
            repo_url = '%s/variants/%s' % (ga4gh_url, variantId)
            status_code, response_json = basic_http_operation.send_get(repo_url, {})
            return status_code > 400, response_json
    else:
        return False, response_json

    
#helper methods
def get_resource_id_list(url, resource_name, access_token=None):
    entry_obj = send_fetch_resource_request(url, resource_name, access_token)
    if entry_obj:
        return fetch_resource_id_list(entry_obj)
    else:
        return None

def fetch_resource_id_list(entry_obj):
    id_list = map(lambda x: x['resource']['id'], entry_obj)
    return id_list

def remove_none(resource_obj):
    if isinstance(resource_obj, dict):
        for key in resource_obj.keys() :
            if resource_obj[key] is None:
                del resource_obj[key]
            elif isinstance(resource_obj[key], dict):
                resource_obj[key] = remove_none(resource_obj[key])
            elif isinstance(resource_obj[key], list):
                for i in xrange(len(resource_obj[key])):
                    resource_obj[key][i] = remove_none(resource_obj[key][i])
    return resource_obj

def _set_reference(resource_obj,id_dict):
    if not isinstance(resource_obj, dict):
        return resource_obj
    for key in resource_obj:
        item = resource_obj[key]
        if isinstance(item, unicode) or isinstance(item, str):
            if key.lower() == 'reference':
                reference_type = item[:item.find('/')]
                if reference_type in id_dict:
                    resource_obj[key] = '%s/%s' % (reference_type, id_dict[reference_type][0])
            else:
                continue
        if isinstance(item, list):
            for element in item:
                element = _set_reference(element, id_dict)
        if isinstance(item, dict):
            item = _set_reference(item, id_dict)
    return resource_obj
