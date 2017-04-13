[PostgreSqldb]
db_database = fhir_tester
db_user = ant
db_pwd = ant1994
db_host = 127.0.0.1
db_port = 5432

[Mongodb]
db_collection4testcase = TestData
db_collection4DataType = DataType
db_collection4Analyzer = FHIR_Analyzer
db_collection4Version = Version
db_database = fhirtest
db_user = AntFHIR
db_pwd = a123456
db_host = 127.0.0.1
db_port = 27017

[MongodbFindway]
FindWay_Analyzer = {'version': &1, 'resourceName': &2}
FindWay_PrimitiveData = {'Version': &1, 'DataType': &2}
FindWay_ComplexData = {'Version': &1, 'TypeName': &2}
FindWay_GeneratorListForWrongCase = {'version': &1, 'resourcename': &2, 'correct': &3}
FindeWay_GeneratorListForRightCase = {'version': &1, 'resourcename': &2, 'correct': &3, 'constraint': &4}
FindWay_GeneratorCount = {'version': &1, 'resourcename': &2}
FindWay_DataTypeExist = {'Version': &1, 'DataType': &2}
FindWay_Version = { 'version': &1}

[PostgreSqlFindWay]
FindWay_Analyzer = select AnalyzerJson from FHIR_Analyzer where version = &&1 and resourceName = &&2

[PostgreSqlInsertOperation]
fhir_InsertToDatatype = insert into fhir_DataType(version, datatype, datatypeName) values



