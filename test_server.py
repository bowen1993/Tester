import json
import requests
test_data_file = open('./test.json', 'r')
test_data = json.loads(test_data_file.read())

header = {}
url = "http://localhost:3000/home/submit_task"
response = requests.post(url, data=test_data, headers=header)
print response.status_code
print response.json()

