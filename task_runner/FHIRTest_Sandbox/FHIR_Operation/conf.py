[db]
db_database = fhir_solution
db_user = ant
db_pwd = ant1994
db_host = 127.0.0.1
db_port = 5432

[SelectOperation]
SelectTestCase = select testcase from fhir_testcase where version = &&1 and resourcename = &&2 and correct = &&3
SelectAllCase = select * from fhir_testcase
SelectCorrectCaseName = select DISTINCT(resourcename) from fhir_testcase where correct =1

[mongodb]
db_database = fhirtest
db_collection = TestData
db_user = 
db_pwd = 
db_host = 127.0.0.1
db_port = 27017