import requests
import json, sys, re

def get_code(get_url, redirect_uri):
  p={
        "response_type":"code",
        "client_id": "771b919d-6ac6-4a6b-b683-a7b3d763463d",
        "redirect_uri": redirect_uri,
        "scope":"user/*.*",
        "state":"98wrghuwuogerg97"
    }
  r=requests.get(get_url, params = p)
  # print "\nresponse:  ",r.url
  m = '.*code=(.*)&state=.*'
  n = re.match(m,r.url)
  code=n.group(1)
  return code

def get_access_token(code, post_url, redirect_uri):
  header = {'Content-type': 'application/json'}
  p={
      "grant_type": "authorization_code",
      "code": code,
      "redirect_uri": redirect_uri,
      "client_id": "771b919d-6ac6-4a6b-b683-a7b3d763463d"
    }
  r=requests.post(post_url, data = json.dumps(p),headers=header)
  # get access token
  access_token = r.json()['access_token']
  return access_token

def send_json(send_json_url, access_token):
  header = {'Content-Type':'application/json','Authorization':'Bearer %s'% access_token}

  try:
    file_name = open(sys.argv[1])
  except Exception as e:
    print "\n**  ERROR: open file failed !!  **\n"
  try:
    dict_file = json.load(file_name)
  except Exception as e:
    print "\n**  ERROR: load json file failed !!  **\n"

  json_file = json.dumps(dict_file)
  print json_file
  resource_type =  dict_file["resourceType"]
  r = requests.post(send_json_url+resource_type,data=json_file,headers=header)

  print r.text

  if r.status_code < 400:
    print "\n**  send succeed!!  **\n"
  else:
    print "\n**  send failed!!  **\n** status_code: %i**\n" % r.status_code
  return r.status_code

def main():
  redirect_uri = "jsonsender.org"
  get_code_url = "http://localhost:3000/api/oauth/authorize?"
  get_access_token_url = "http://localhost:3000/api/oauth/token"
  send_json_url = "http://localhost:3000/api/fhir/"

  code = get_code(get_code_url, redirect_uri)
  access_token = get_access_token(code, get_access_token_url, redirect_uri)
  status_code = send_json(send_json_url, access_token)

if __name__ == '__main__':
  main()
