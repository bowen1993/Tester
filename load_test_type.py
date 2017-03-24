from pymongo import MongoClient
import json

client = MongoClient("mongodb://localhost")
db = client.fhirtest

data_file = open('test_type.json', 'r')
json_data = json.loads(data_file.read())

print "Loading test types"
test_types = json_data['test_types']
test_type_coll = db.tasktypes
for test_type in test_types:
    test_type_coll.insert_one(test_type)