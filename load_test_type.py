from pymongo import MongoClient
import json

client = MongoClient("mongodb://localhost")
db = client.fhirtest

data_file = open('test_type.json', 'r')
json_data = json.loads(data_file.read())

print "Loading test types"
test_types = json_data['test_types']
resources = json_data['resources']
test_type_coll = db.tasktypes
resources_coll = db.resources
for resource in resources:
    resources_coll.insert_one(resource)
for test_type in test_types:
    resource_type = test_type['resource_type']
    test_type_resources = resources_coll.find({"type_code":test_type['resource_type']})
    resource_list = []
    for r in test_type_resources:
        resource_list.append(r['_id'])
    test_type['object']['related_resources'] = resource_list
    test_type_coll.insert_one(test_type['object'])