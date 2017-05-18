from ..HTTP_Operation import basic_http_operation
import requests
import re
import json
# from ..config import jwt_secreat
import jwt

def get_code(client_id, auth_url, redirect_uri, scope):
    '''
    get code from server
    '''
    p={
        "response_type":"code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope":scope,
        "state":"98wrghuwuogerg97"
    }
    r=requests.get(auth_url, params = p)
    m = '.*code=(.*)&state=.*'
    print r
    n = re.match(m,r.url)
    code=n.group(1)
    return code

def get_access_token(code, client_id, auth_url, redirect_uri):
    '''
    exchange access token with code
    '''
    header = {'Content-type': 'application/json'}
    p={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id
    }
    r=requests.post(auth_url, data = json.dumps(p),headers=header)
    # get access token
    access_token = r.json()['access_token']
    return access_token

def basicOAuth(auth_info):
    '''
    run OAuth 2.0 to gain access token
    '''
    auth_url = auth_info['auth_url']

    scope_str = ''
    for scope in auth_info['scopes']:
        scope_str += scope['name'] + "+"
    scope_str = scope_str[:-1]
    print scope_str
    auth_code = get_code(auth_info['client_id'], '%s/authorize'%auth_url, auth_info['redirect_uri'], scope_str)
    access_token = get_access_token(auth_code, auth_info['client_id'], '%s/token'%auth_url, auth_info['redirect_uri'])
    return access_token

def read_fhir_resource(server_url, resource_type, access_token=None):
    '''
    read fhir resource
    '''
    resource_url = '%s/%s?_format=json' % (server_url, resource_type)
    headers = {}
    if access_token:
        headers['Authorization'] = "Bearer %s" % access_token
    status_code, response_json = basic_http_operation.send_get(resource_url, headers)
    request_detail = {
        'url': resource_url,
        'method': 'GET',
        'data': {}
    }
    isSuccessful = status_code < 400
    return isSuccessful, response_json, request_detail

def read_one_resource(server_url, resource_type, resource_id, access_token=None):
    '''
    read one resource with id
    '''
    resource_url = "%s/%s/%s?_format=json" % (server_url, resource_type, resource_id)
    headers = {}
    if access_token:
        headers['Authorization'] = "Bearer %s" % access_token
    status_code, response_json = basic_http_operation.send_get(resource_url, headers)
    isSuccessful = status_code < 400
    return isSuccessful, response_json

def get_resources_ids(server_url, resource_type, access_token=None):
    '''
    get id list of a certain resource type
    '''
    resource_url = '%s/%s?_format=json' % (server_url, resource_type)
    headers = {}
    if access_token:
        headers['Authorization'] = "Bearer %s" % access_token
    status_code, response_json = basic_http_operation.send_get(resource_url, headers)
    isSuccessful = status_code < 400
    result = []
    if isSuccessful:
        result = extrace_id_list(response_json)
    return isSuccessful, result


def extrace_id_list(resource_bundle):
    '''
    extract id from a resource bundle
    '''
    id_list = []
    if 'total' in resource_bundle and resource_bundle['total'] > 0 and 'entry' in resource_bundle:
        entry_object = resource_bundle['entry']
        id_list = extract_id(entry_object)
    return id_list
    

def extract_id(entry_obj):
    id_list = map(lambda x: x['resource']['id'], entry_obj)
    return id_list

def create_fhir_resource(server_url, resource_type, resource, access_token=None):
    '''
    create fhir resources
    '''
    resource_url = '%s/%s?_format=json' % (server_url, resource_type)
    headers = {
        'Content-Type':'application/json'
    }
    if access_token:
        headers['Authorization'] = "Bearer %s" % access_token
    status_code, response_body = basic_http_operation.send_post(resource_url, headers, resource)
    request_detail = {
        'url': resource_url,
        'method': 'POST',
        'data': resource
    }
    isSuccessful = status_code < 400
    return isSuccessful, response_body, request_detail


def update_fhir_resource(server_url, updated_resource, resource_id, access_token=None):
    '''
    update a fhir resource
    '''
    pass

def delete_fhir_resource(server_url, resource_id, access_token=None):
    '''
    delete a fhir resource
    '''
    pass