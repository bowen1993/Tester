# -*- coding: utf-8 -*-

import pymongo
import json
from pymongo import MongoClient
import configparser
import os




class DataBaseOperation():
    __config__ = configparser.ConfigParser()
    __config__.read( os.path.join(os.getcwd(), 'task_runner/FHIRTest_Sandbox/FHIR_Operation/conf.py') )
    __db_host__ = __config__.get('mongodb','db_host')
    __db_database__ = __config__.get('mongodb','db_database')
    # __db_user__ = __config__.get('mongodb','db_user')
    # __db_pwd__ = __config__.get('mongodb','db_pwd')
    __db_port__ = __config__.get('mongodb','db_port')
    __db_collection__ = __config__.get('mongodb','db_collection')

    global null
    null = None

    # 建立连接
    def __connection__(self):
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
        #self.__client__.disconnect()
        pass

    # 我将Postgresql来的数据导入到 Mongodb中
    def InsertfromPostgreSql(self):
        db = self.__connection__()
        collection = db[self.__db_collection__]
        ps = PostgreSqlDataOperation.DataBaseOperation()
        list = ps.selectAllcases()
        print len(list)
        for i in list:
            newdict = {}
            newdict['version'] = i[1]
            newdict['resourcename'] = i[2]
            newdict['testcase'] = eval(i[3])
            newdict['correct'] = i[4]
            collection.insert(newdict)
        self.__close__()

    # 判断我这个 版本 和 resource 在数据库中是否存在
    def selectVersionnResource(self,version,resourceName):
        db = self.__connection__()
        collection = db[self.__db_collection__]
        ss = collection.find_one({'version': version, 'resourcename': resourceName})
        self.__close__()
        if ss:
            return True
        return False

    # 存在的话返回 list
    def selectrows(self,parameters):
        db = self.__connection__()
        collection = db[self.__db_collection__]

        ss = collection.find({'version':parameters[0],'resourcename':parameters[1],'correct':parameters[2]})
        # del ss["_id"]
        self.__close__()
        if ss:
            list = [json.dumps(x['testcase']) for x in ss]
            return list
        return None

    def InsertOperation(self):
        pass

    # 计算总共有多少行数据
    def selectCount(self):
        try:
            db = self.__connection__()
            collection = db[self.__db_collection__]

            scount = collection.count()
            self.__close__()
            return scount
        except Exception,e:
            print e


# db = DataBaseOperation()
# print db.selectCount()
# parameters = []
# parameters.append('1.9.0')
# parameters.append('Specimen')
# parameters.append(1)
# db.selectrows(parameters)
