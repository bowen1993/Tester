# -*- coding: utf-8 -*-

import sys
import os
from pymongo import MongoClient
import configparser


class DataBaseOperation():
    __config__ = configparser.ConfigParser()
    __config__.read( os.path.join(os.getcwd(), 'task_runner/FHIRTest_Sandbox/FHIR_Operation/conf.py' ) )
    __db_host__ = __config__.get('Mongodb','db_host')
    __db_database__ = __config__.get('Mongodb','db_database')
    __db_port__ = __config__.get('Mongodb','db_port')

    # 打开连接
    def __connections__(self):
        # client = MongoClient(self.__db_host__,int(self.__db_port__))
        # print self.__db_user__,self.__db_pwd__
        # client['FHIR'].authenticate(self.__db_user__,self.__db_pwd__)
        # db = client.database
        # print db
        # print db.collection
        try:
            self.__client__ = MongoClient(self.__db_host__,int(self.__db_port__))
            return self.__client__[self.__db_database__]
        except Exception,e:
            print e

    # 关闭连接
    def __close__(self):
        self.__client__.close()

    # 插入数据到 DataType里面
    def InsertToDataType(self,parameters):
        Flag = False
        db = self.__connections__()
        try:
            dbcollection = self.__config__.get('Mongodb','db_collection4DataType')
            collection = db[dbcollection]

            if isinstance(parameters,dict):
                jsondict = parameters
            else:
                jsondict = {}
                jsondict['Version'] = parameters[0]
                jsondict['DataType'] = parameters[1]
                jsondict['TypeName'] = parameters[2]
                jsondict['Value'] = parameters[3]

            collection.insert(jsondict)
            Flag = True
        except Exception,e:
            print 'InsertDataType Wrong:',e
        finally:
            self.__close__()
        return Flag

    # 插入数据到 Analyzer 里面
    def InsertToAnalyzer(self,parameters):
        Flag = False
        db = self.__connections__()
        try:
            dbcollection = self.__config__.get('Mongodb', 'db_collection4Analyzer')
            collection = db[dbcollection]

            if isinstance(parameters, dict):
                jsondict = parameters
            else:
                jsondict = {}
                jsondict['version'] = parameters[0]
                jsondict['resourceName'] = parameters[1]
                jsondict['AnalyzerJson'] = parameters[2]

            collection.insert(jsondict)
            Flag = True
        except Exception, e:
            print 'InsertDataType Wrong:', e
        finally:
            self.__close__()
        return Flag

    # 插入数据到 TestCase 里面
    def InsertToTestCase(self,parameters):
        Flag = False
        db = self.__connections__()
        try:
            dbcollections = self.__config__.get('Mongodb','db_collection4testcase')
            collection = db[dbcollections]

            jsondict = {}
            jsondict['version'] = parameters[0]
            jsondict['resourcename'] = parameters[1]
            jsondict['testcase'] = parameters[2]
            jsondict['correct'] = parameters[3]
            if len(parameters) == 5:
                jsondict['constraint'] = parameters[4]

            collection.insert(jsondict)
            Flag = True
        except Exception,e:
            print 'InserToTestCase Wrong:',e
        finally:
            self.__close__()
        return Flag

    # 插入数据到 Version 里面
    def InsertToVersion(self,parameters):
        Flag = False
        db = self.__connections__()
        try:
            dbcollections = self.__config__.get('Mongodb', 'db_collection4Version')
            collection = db[dbcollections]

            jsondict = {}
            jsondict['version'] = parameters[0]
            jsondict['versionhtml'] = parameters[1]

            collection.insert(jsondict)
            Flag = True
        except Exception, e:
            print 'InserToTestCase Wrong:', e
        finally:
            self.__close__()
        return Flag

    # 查询 某个collection 里面的数据，附带上查询条件 findway
    def SelectForlist(self,dbcollection,findway):
        db = self.__connections__()
        collection = db[dbcollection]
        listtable = []
        try:
            # print findway
            returnlist = collection.find(findway)
            for x in returnlist:
                del x["_id"]
                listtable.append(x)
        except Exception,e:
            print e
        self.__close__()

        if len(listtable)>0:
            return listtable
        else:
            return None

    # 返回某个 collection 查询的数量
    def SelectForCount(self,dbcollection,findway):
        listcount = 0
        db = self.__connections__()
        collection = db[dbcollection]
        try:
            listcount = collection.count(findway)
        except Exception,e:
            print e
        self.__close__()

        return listcount




