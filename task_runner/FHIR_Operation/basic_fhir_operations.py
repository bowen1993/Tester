from ..HTTP_Operation import basic_http_operation
from ..config import jwt_secreat
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
    r=requests.get(get_url, params = p)
    m = '.*code=(.*)&state=.*'
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
    r=requests.post(post_url, data = json.dumps(p),headers=header)
    # get access token
    access_token = r.json()['access_token']
    return access_token

def basicOAuth(auth_info, auth_url):
    '''
    run OAuth 2.0 to gain access token
    '''
    auth_code = get_code(auth_info['client_id'], '%s/authorize'%auth_url, auth_info['redirect_uri'], auth_info['scope'])
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
    isSuccessful = status_code < 400
    return isSuccessful, response_json
    

def create_fhir_resource(server_url, resource, access_token=None):
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
    isSuccessful = status_code < 400
    return isSuccessful, response_body


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