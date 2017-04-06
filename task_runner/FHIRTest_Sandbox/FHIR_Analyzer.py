# -*- coding: utf-8 -*-
# import sys
# sys.path.append('..')
import urllib2
import json
# from UnitOperation import MongodbOperation

class Analyzer():
    """docstring for Analyser"""
    global null
    null = None

    __loadready__ = False
    __resourceType__ = None
    __Analyze_Result__ = {}
    __ResourceVersion__ = None
    __ResourceName__ = None

    # 根据类型来判断是什么类型的内容
    def load_spec(self,spec_url):
        if 'http' and 'json' in spec_url:
            try:
                req = urllib2.urlopen(spec_url)
                js = json.loads(req.read())
                self.__resourceType__ = 'URL'
                if self.__analyzeJson__(js):
                    return True
            except Exception,e:
                print e
        elif isinstance(spec_url,str):
            try:
                js = json.loads(spec_url)
                self.__resourceType__ = 'JsonString'
                if self.__analyzeJson__(js):
                    return True
            except Exception,e:
                print e
        elif isinstance(spec_url,dict):
            self.__resourceType__ = 'JsonObject'
            if self.__analyzeJson__(spec_url):
                return True
        return False

    # 返回传进参数是什么类型
    def resource_type(self):
        return self.__resourceType__

    # 获取传进来内容的 version 和 resourceName
    def GetVersionandResourceName(self):
        return self.__ResourceVersion__,self.__ResourceName__

    # 返回正确的analyze_result
    def analyze_result(self):
        return json.dumps(self.__Analyze_Result__)
        # return self.__Analyze_Result__

    # 解析Json格式并返回是否解析成功
    def __analyzeJson__(self,Jsondict):
        # 解析发来的json里面有没有 ID 即是 后面的resource_name
        try:
            dictData = {}
            if not Jsondict['id']:
                self.__Analyze_Result__ = dictData
            else:
                # 获取到 整个ResourceName 以方便后续对Element进行遍历
                obj_name = Jsondict['id'].encode('utf-8')
                self.__ResourceVersion__ = Jsondict['fhirVersion'].encode('utf-8')
                self.__ResourceName__ = Jsondict['id'].encode('utf-8')
                for ElementDict in Jsondict['snapshot']['element']:
                    new_obj = {}
                    Node = self.__GetNode__(ElementDict,obj_name)
                    new_obj["parent"] = self.__GetParent__(ElementDict,obj_name)
                    new_obj["range"] = self.__GetRange__(ElementDict)
                    new_obj["type"] = self.__GetType__(ElementDict)
                    new_obj["reference_type"] = self.__GetReferenceType__(ElementDict)
                    new_obj["constraint"] = self.__GetConstraint__(ElementDict)
                    # new_obj["options"] = self.__GetOptions__(ElementDict)
                    new_obj['valueSetReference'] = self.__GetvalueSetReference__(ElementDict)
                    dictData[Node] = new_obj
                self.__Analyze_Result__ = dictData
                return True
        except Exception,e:
            print 'Analyzer Json Wrong:',e
        return False

    # 获取该节点是什么
    def __GetNode__(self,ElementDict,obj_name):
        node = None
        try:
            if not ElementDict.has_key('id'):
                node = filter(lambda en: en in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.(',ElementDict['path'].encode('utf-8')).split(obj_name + '.')[-1]
            else:
                node = filter(lambda en: en in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.(',ElementDict['id'].encode('utf-8')).split(obj_name + '.')[-1]
        except Exception,e:
            print 'GET Node Wrong:',e
        return node

    # 获取他的Type
    def __GetType__(self,ElementDict):
        NodeType = None
        try:
            NodeType = []
            if ElementDict.has_key('type'):
                if isinstance(ElementDict['type'],dict):
                    NodeType.append(ElementDict['code']['value'].encode('utf-8'))
                else:
                    for codelist in ElementDict['type']:
                        if codelist['code'] not in NodeType:
                            NodeType.append(codelist['code'].encode('utf-8'))
            else:
                NodeType = ['rootElement']
        except Exception,e:
            print 'GET Type Wrong:',e
        return NodeType

    # 获取它的ReferenceType
    def __GetReferenceType__(self,ElementDict):
        try:
            if ElementDict.has_key('type'):
                reference_typelist = []
                for tt in ElementDict['type']:
                    if 'Reference' in tt['code']:
                        if tt.has_key('profile'):
                            aim = 'profile'
                        else:
                            aim = 'targetProfile'
                        # 这里可能还存在着一些问题 比如会不会出现 DICT 的问题
                        if not isinstance(tt[aim],list):
                            reference_typelist.append(tt[aim].encode('utf-8').split('/')[-1])
                        else:
                            for typeData in tt[aim]:
                                if type(typeData) is dict:
                                    reference_typelist.append(typeData['value'].encode('utf-8').split('/')[-1])
                                else:
                                    reference_typelist.append(typeData.encode('utf-8').split('/')[-1])
                if len(reference_typelist) > 0:
                    return reference_typelist
                else:
                    return None
        except Exception,e:
            print 'GET ReferenceType Wrong:',e

    # 获取它的 min 和 max 大小
    def __GetRange__(self,ElementDict):
        rangement = None
        try:
            if type(ElementDict['min']) is dict:
                if ElementDict['min']['value'] == '0' and ElementDict['max']['value'] == '1':
                    rangement = 0
                elif ElementDict['min']['value'] == '0' and ElementDict['max']['value'] == '*':
                    rangement =  2
                elif ElementDict['min']['value'] == '1' and ElementDict['max']['value'] == '1':
                    rangement = 1
                elif ElementDict['min']['value'] == '1' and ElementDict['max']['value'] == '*':
                    rangement = 3
            else:
                if ElementDict['min'] == 0 and ElementDict['max'] == '1':
                    rangement = 0
                elif ElementDict['min'] == 0 and ElementDict['max'] == '*':
                    rangement = 2
                elif ElementDict['min'] == 1 and ElementDict['max'] == '1':
                    rangement = 1
                elif ElementDict['min'] == 1 and ElementDict['max'] == '*':
                    rangement = 3
        except Exception,e:
            print 'GET Range Wrong:',e
        return rangement

    # 通过valueSetReference 获取到可以爬虫的网址
    def __GetvalueSetReference__(self,ElementDict):
        ValueSetReference = None
        try:
            if ElementDict.has_key('binding'):
                if ElementDict['binding'].has_key('valueSetReference'):
                    if isinstance(ElementDict['binding']['valueSetReference'],dict):
                        ValueSetReference = ElementDict['binding']['valueSetReference']['reference']
        except Exception,e:
            print 'GET ValueSetRefenrece Wrong',e
        return ValueSetReference

    # 获取它的codeValues
    def __GetOptions__(self,ElementDict):
        codelist = None
        try:
            if '|' in ElementDict['short']:
                codelist = ElementDict['short'].encode('utf-8').replace(' ','').replace('+','').split('|')
        except Exception,e:
            print 'GET Options Wrong:',e
        return codelist

    # 获取他的约束条件
    def __GetConstraint__(self,ElementDict):
        constraintList = []
        if ElementDict.has_key('constraint'):
            try:

                if type(ElementDict['constraint']) is dict:
                    newConstraintData = {}
                    if ElementDict['constraint'].has_key('expression'):
                        newConstraintData['expression'] = ElementDict['expression']['value'].encode('utf-8')
                    newConstraintData['xpath'] = ElementDict['xpath']['value'].encode('utf-8')
                    constraintList.append(newConstraintData)
                else:
                    for constraintData in ElementDict['constraint']:
                        newConstraintData = {}
                        if constraintData.has_key('expression'):
                            if type(constraintData['expression']) is dict:
                                newConstraintData['expression'] = constraintData['expression']['value'].encode('utf-8')
                                newConstraintData['xpath'] = constraintData['xpath']['value'].encode('utf-8')
                            else:
                                newConstraintData['expression'] = constraintData['expression'].encode('utf-8')
                                newConstraintData['xpath'] = constraintData['xpath'].encode('utf-8')
                        constraintList.append(newConstraintData)
            except Exception,e:
                print 'GET Constraint Wrong:',e
        else:
            return None
        return constraintList

    # 获取该节点的父节点
    def __GetParent__(self,ElementDict,obj_name):
        parent = None
        try:
            if not ElementDict.has_key('id'):
                if ElementDict['path'] == obj_name:
                    parent = None
                else:
                    parent = ElementDict['path'].encode('utf-8').split('.')[-2]
            else:
                if ElementDict['id'] == obj_name:
                    parent = None
                else:
                    parent = ElementDict['id'].encode('utf-8').split('.')[-2]
        except Exception,e:
            print 'GET Parent Wrong:',e
        return parent
