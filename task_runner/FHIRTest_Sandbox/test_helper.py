from .FHIR_Operation import basic_fhir_operations, fhir_test_cases
from .HTTP_Operation import basic_http_operation

def set_reference(resource_obj, server_url, access_token=None, id_dict={}):
    '''
    resource reference id correction
    '''
    if not isinstance(resource_obj, dict):
        return resource_obj
    for key in resource_obj:
        item = resource_obj[key]
        if isinstance(item, unicode) or isinstance(item, str):
            if key.lower() == 'reference':
                #reference type, change reference id, if not found in id dict, retrive from server, if server has none, create new
                reference_type = item[:item.find('/')]
                if reference_type in id_dict:
                    resource_obj[key] = '%s/%s' % (reference_type, id_dict[reference_type][0])
                else:
                    #retrive from server
                    id_list = basic_fhir_operations.get_resources_ids(server_url, reference_type, access_token)
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
        print response['repository']
        #get variant id
        try:
            variantId = response['repository'][0]['variantId']
        except:
            pass
        print variantId
        if variantId and len(variantId) != 0:
            repo_url = '%svariants/%s' % (ga4gh_url, variantId)
            status_code, response_json = basic_http_operation.send_get(repo_url, {})
            return status_code > 400, response_json
    else:
        return False, response_json

    
