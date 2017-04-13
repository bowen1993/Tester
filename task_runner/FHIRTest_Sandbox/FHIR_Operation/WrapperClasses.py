# -*- coding: utf-8 -*-
import sys
import configparser
import random
from .MongoDBOperation import *

# 通过Analyzer类来包装 有关 Analyzer的 数据库操作
class AnalyzerClass():
    __config__ = configparser.ConfigParser()
    __config__.read( os.path.join(os.getcwd(), 'task_runner/FHIRTest_Sandbox/FHIR_Operation/conf.py' ) )

    def ReturnClassByDataBaseName(self,DataBaseName,parametes,condition):
        if DataBaseName == 'MongoDB':
            if condition == 'select':
                return self.__GetValuesFromMongoDB__(parametes)
            elif condition == 'insert':
                return self.__InsertToMongoDB__(parametes)
        elif DataBaseName == 'PostgreSql':
            return self.__GetValueFromPostgreSql__(parametes)

    #　获取AnalyzerJson 的值
    def __GetValuesFromMongoDB__(self,parameters):
        try:
            mm = DataBaseOperation()
            mm_collection = self.__config__.get('Mongodb','db_collection4Analyzer')
            mm_findway = self.__config__.get('MongodbFindway','FindWay_Analyzer')
            mm_findway = mm_findway.replace('&1', "'" + parameters[0] + "'").replace('&2', "'" + parameters[1] + "'")
            mm_findway = eval(mm_findway)
            analyzer =  mm.SelectForlist(mm_collection,mm_findway)
            if analyzer:
                return analyzer[0]['AnalyzerJson'].encode('utf-8')
            return None
        except Exception,e:
            print 'GetAnalyzerValue Wrong:',e
            return None

    # 插入AnalyzerJson 的值
    def __InsertToMongoDB__(self, paramters):
        try:
            mm = DataBaseOperation()
            checklist = []
            if isinstance(paramters,dict):
                checklist.append(paramters['version'])
                checklist.append(paramters['resourceName'])
            else:
                checklist.append(paramters[0])
                checklist.append(paramters[1])
            if self.__GetValuesFromMongoDB__(checklist) is None:
                return mm.InsertToAnalyzer(paramters)
        except Exception,e:
            print 'Analyzer Insert Wrong:',e
            return False

    # 通过Postgresql 获取Analyzer的值
    # def __GetValueFromPostgreSql__(self,parameters):
    #     try:
    #         ps = PostgreSqlDataOperation.DataBaseOperation()
    #         ps_selectsql = self.__config__.get('PostgreSqlFindWay','FindWay_Analyzer')
    #         ps_selectsql = ps_selectsql.encode('utf-8').replace('&&1', "'" + parameters[0] + "'")
    #         ps_selectsql = ps_selectsql.replace('&&2', "'" + parameters[1] + "'")
    #         return ps.SelectForList(ps_selectsql)
    #     except Exception,e:
    #         print 'GetAnalyzerValue Wrong:',e
    #         return None

# 通过Analyzer类来包装 有关 Analyzer的 数据库操作
class CodeTypeClass():
    __config__ = configparser.ConfigParser()
    __config__.read( os.path.join(os.getcwd(), 'task_runner/FHIRTest_Sandbox/FHIR_Operation/conf.py' ) )

    def ReturnClassByDataBaseName(self,DataBaseName,parametes,conditions):
        if DataBaseName == 'MongoDB':
            if conditions == 'findPrimitiveValues':
                return self.__GetValuesFromMongoDB__(parametes,'FindWay_PrimitiveData')
            elif conditions == 'findComplexValues':
                return self.__GetValuesFromMongoDB__(parametes,'FindWay_ComplexData')
            elif conditions == 'findComplexCount':
                return self.__GetCountFromMongoDB__(parametes,'FindWay_ComplexData')
            elif conditions == 'InsertDataType_Complex':
                return self.__InsertToMongoDB__(parametes,conditions)
            elif conditions == 'InsertDataType_Primitive':
                return self.__InsertToMongoDB__(parametes, conditions)
        elif DataBaseName == 'PostgreSql':
            return self.__GetValueFromPostgreSql__(parametes)

    # 插入DataType数据
    def __InsertToMongoDB__(self,parametes,condition):
        typecondition = condition.split('_')[-1]
        mm = DataBaseOperation()
        try:
            if typecondition == 'Complex':
                parameters = []
                parameters.append(parametes['Version'])
                parameters.append(parametes['TypeName'])
                if not self.ReturnClassByDataBaseName('MongoDB',parameters,'findComplexCount'):
                    return mm.InsertToDataType(parametes)
                return False
            else:
                parameters = []
                parameters.append(parametes['Version'])
                parameters.append(parametes['DataType'])
                if not self.ReturnClassByDataBaseName('MongoDB', parameters, 'findPrimitiveValues'):
                    return mm.InsertToDataType(parametes)
                return False
        except Exception,e:
            print 'InsertDataType Wrong:',e
            return False

    # 找寻是否存在数据
    def __GetCountFromMongoDB__(self,parameters,conditionsfind):
        try:
            mm = DataBaseOperation()
            mm_collection = self.__config__.get('Mongodb', 'db_collection4DataType').encode('utf-8')
            mm_findway = self.__config__.get('MongodbFindway', conditionsfind)
            mm_findway = mm_findway.replace('&1', "'" + parameters[0] + "'").replace('&2', "'" + parameters[1] + "'")
            mm_findway = eval(mm_findway)
            return mm.SelectForCount(mm_collection, mm_findway)
        except Exception,e:
            print conditionsfind,' Wrong:',e
            return None

    # 返回List
    def __GetValuesFromMongoDB__(self,parameters,conditionsfind):
        try:
            mm = DataBaseOperation()
            mm_collection = self.__config__.get('Mongodb','db_collection4DataType').encode('utf-8')
            mm_findway = self.__config__.get('MongodbFindway',conditionsfind)
            mm_findway = mm_findway.replace('&1', "'" + parameters[0] + "'").replace('&2', "'" + parameters[1] + "'")
            mm_findway = eval(mm_findway)
            pp = mm.SelectForlist(mm_collection,mm_findway)
            if pp:
                return pp[0]['Value']
            else:
                return None
        except Exception,e:
            print conditionsfind, ' Wrong:', e
            return None


    # 这个还没改过 要做的时候再改
    # def __GetValueFromPostgreSql__(self,parameters):
    #     ps = PostgreSqlDataOperation.DataBaseOperation()
    #     ps_selectsql = self.__config__.get('PostgreSqlFindWay','FindWay_Analyzer')
    #     ps_selectsql = ps_selectsql.encode('utf-8').replace('&&1', "'" + parameters[0] + "'")
    #     ps_selectsql = ps_selectsql.replace('&&2', "'" + parameters[1] + "'")
    #     return ps.SelectForList(ps_selectsql)

# 通过TestCase类来进行数据库插入操作
class TestCaseClass():
    __config__ = configparser.ConfigParser()
    __config__.read( os.path.join(os.getcwd(), 'task_runner/FHIRTest_Sandbox/FHIR_Operation/conf.py' ) )

    def ReturnClassByDataBaseName(self,DataBaseName,parametes,OperationType):
        if DataBaseName == 'MongoDB':
            if OperationType == 'insert':
                return self.__InsertToMongoDB__(parametes)
            elif OperationType == 'selectForCount':
                return self.__SelectCountFromMongoDB__(parametes)
            elif OperationType == 'selectForList':
                return self.__SelectListFromMongoDB__(parametes)
        elif DataBaseName == 'PostgreSql':
            return self.__InsertToPostgreSql__(parametes)

    def  __InsertToMongoDB__(self,parameters):
        try:
            mm = DataBaseOperation()
            return mm.InsertToTestCase(parameters)
        except Exception,e:
            print 'GetAnalyzerValue Wrong:',e
            return False
        return False

    def __SelectListFromMongoDB__(self,parameters):
        try:
            mm = DataBaseOperation()
            mm_collection = self.__config__.get('Mongodb', 'db_collection4testcase')
            if len(parameters) == 4:
                mm_findway = self.__config__.get('MongodbFindway', 'FindeWay_GeneratorListForRightCase')
                mm_findway = mm_findway.replace('&1', "'" + parameters[0] + "'").replace('&2', "'" + parameters[1] + "'").replace('&3', "'" + parameters[2] + "'").replace('&4',"'" + parameters[3] + "'")
            else:
                mm_findway = self.__config__.get('MongodbFindway', 'FindWay_GeneratorListForWrongCase')
                mm_findway = mm_findway.replace('&1', "'" + parameters[0] + "'").replace('&2',"'" + parameters[1] + "'").replace('&3',"'" + parameters[2] + "'")
            mm_findway = eval(mm_findway)
            countlist = mm.SelectForlist(mm_collection, mm_findway)

            # 返回样例List中 随机返回一个
            if countlist:
                # randomset = random.randint(0, len(countlist) - 1)
                return countlist
            else:
                return None
        except Exception, e:
            print 'SelectTestList Wrong:', e
            return None

    def __SelectCountFromMongoDB__(self,parameters):
        try:
            mm = DataBaseOperation()
            mm_collection = self.__config__.get('Mongodb', 'db_collection4testcase').encode('utf-8')
            mm_findway = self.__config__.get('MongodbFindway', 'FindWay_GeneratorCount')
            mm_findway = mm_findway.replace('&1', "'" + parameters[0] + "'").replace('&2', "'" + parameters[1] + "'")
            mm_findway = eval(mm_findway)
            return mm.SelectForCount(mm_collection, mm_findway)
        except Exception,e:
            print 'SelectTestCount Wrong:',e
            return None

    def __InsertToPostgreSql__(self,parameters):
        pass

# 插入 version 和它对应的网址，这个网址是后来用来爬网页数据的
class VersionClass():
    __config__ = configparser.ConfigParser()
    __config__.read( os.path.join(os.getcwd(), 'task_runner/FHIRTest_Sandbox/FHIR_Operation/conf.py' ) )

    def ReturnClassByDataBaseName(self, DataBaseName, parametes, OperationType):
        if DataBaseName == 'MongoDB':
            if OperationType == 'insert':
                return self.__InsertToMongoDB__(parametes)
            elif OperationType == 'select':
                return self.__SelectListFromMongoDB__(parametes)
        elif DataBaseName == 'PostgreSql':
            return self.__InsertToPostgreSql__(parametes)

    def __InsertToMongoDB__(self, parameters):
        try:
            mm = DataBaseOperation()
            version = parameters[0]
            if not self.__SelectListFromMongoDB__(version):
                return mm.InsertToVersion(parameters)
            return False
        except Exception, e:
            print 'GetAnalyzerValue Wrong:', e
            return False
        return False

    def __SelectListFromMongoDB__(self, parameters):
        try:
            mm = DataBaseOperation()
            mm_collection = self.__config__.get('Mongodb', 'db_collection4Version')
            mm_findway = self.__config__.get('MongodbFindway', 'FindWay_Version')
            mm_findway = mm_findway.replace('&1', "'" + parameters[0] + "'")
            mm_findway = eval(mm_findway)
            countlist = mm.SelectForlist(mm_collection, mm_findway)
            if countlist:
                return True
            else:
                return False
        except Exception, e:
            print 'SelectTestList Wrong:', e
            return None

# parametes = []
# parametes.append('3.0.0')
# parametes.append('DiagnosticReport')
# aa = AnalyzerClass()
# pp = aa.ReturnClassByDataBaseName('MongoDB',parametes)
