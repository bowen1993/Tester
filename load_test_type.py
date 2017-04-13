from pymongo import MongoClient
import json

client = MongoClient("mongodb://localhost")
db = client.fhirtest

data_file = open('test_type.json', 'r')
json_data = json.loads(data_file.read())

print "Loading test types"
test_types = json_data['test_types']
resources = json_data['resources']
versions = json_data['versions']
servers = json_data['servers']

test_type_coll = db.tasktypes
resources_coll = db.resources
version_coll = db.fhirversions
server_coll = db.fhirservers

#insert versions
if version_coll.count() <= 0:
    print 'Loading versions'
    for version in versions:
        version_coll.insert_one(version)

#insert resources
if resources_coll.count() <= 0:
    print 'Loading resources'
    for resource in resources:
        version_number = resource['version']
        version_obj = version_coll.find_one({"number":version_number})
        del resource['version']
        resource['version'] = version_obj['_id']
        resources_coll.insert_one(resource)

#insert test types
if test_type_coll.count() <= 0:
    print 'Loading test types'
    for test_type in test_types:
        resource_type = test_type['resource_type']
        test_type_resources = resources_coll.find({"type_code":test_type['resource_type']})
        resource_list = []
        for r in test_type_resources:
            resource_list.append(r['_id'])
        test_type['object']['related_resources'] = resource_list
        test_type_coll.insert_one(test_type['object'])

#insert servers
if server_coll.count() <= 0:
    print 'Loading servers'
    for server in servers:
        server_coll.insert_one(server)