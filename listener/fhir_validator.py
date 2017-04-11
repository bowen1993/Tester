#!/usr/bin/env python
from BaseHTTPServer import HTTPServer
from BaseHTTPServer import BaseHTTPRequestHandler
import cgi,json

PORT = 6000

import re
import os
import json
import requests

versions_url = {
    1 : "http://hl7.org/fhir/2017Jan/%s.profile.json",
    2 : "http://hl7.org/fhir/STU3/%s.profile.json"
}


DATE_RE = re.compile(r'-?([1-9][0-9]{3}|0[0-9]{3})(-(0[1-9]|1[0-2])(-(0[1-9]|[12][0-9]|3[01]))?)?')
DATETIME_RE = re.compile(r'-?([1-9][0-9]{3}|0[0-9]{3})(-(0[1-9]|1[0-2])(-(0[1-9]|[12][0-9]|3[01])(T(([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\.[0-9]+)?|(24:00:00(\.0+)?))(Z|(\+|-)((0[0-9]|1[0-3]):[0-5][0-9]|14:00))?)?)?)?')
ID_RE = re.compile(r'[a-z0-9\-\.]{1,36}')
INSTANT_RE = re.compile(r'[1-9][0-9]{3}-.+T[^.]+(Z|[+-].+)')
OID_RE = re.compile(r'urn:oid:\d+\.\d+\.\d+\.\d+')
UUID_RE = re.compile(r'urn:uuid:[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}')
URI_RE = re.compile(r'''(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?]))''')

def validate_by_regex(regex):
    return lambda data: regex.match(str(data)) is not None


def validate_by_instance(datatype):
    return lambda data: isinstance(data, datatype)

FHIR_PRIMITIVE_VALIDATORS = {
    'base64Binary': validate_by_instance(unicode),
    'boolean': validate_by_instance(bool),
    'date': validate_by_regex(DATE_RE),
    'dateTime': validate_by_regex(DATETIME_RE),
    'decimal': validate_by_instance(float),
    'id': validate_by_regex(ID_RE),
    'instant': validate_by_regex(INSTANT_RE),
    'integer': validate_by_instance(int),
    'positiveInt': validate_by_instance(int),
    'oid': validate_by_regex(OID_RE),
    'string': validate_by_instance(unicode),
    'uri': validate_by_regex(URI_RE),
    'uuid': validate_by_regex(UUID_RE),
    'code': validate_by_instance(unicode)
}

FHIR_PRIMITIVE_INIT = {
    'boolean': lambda bl: bl == 'true',
    'decimal': float,
    'integer': int
}

def validate_reference(element, reference_types):
    #get reference in element
    if 'reference' not in  element:
        return False
    
    ref_type = element["reference"][:element["reference"].find('/')]
    return ref_type in reference_types
        

class FHIRElement(object):

    def __init__(self, spec):
        self.path = spec['path']
        self.elem_types = []
        if 'type' in spec['definition']:
            if isinstance(spec['definition']['type'], list):
                self.elem_types = [_type
                                for _type in spec['definition']['type']]
            else:
                self.elem_types = [spec['definition']['type']]
        self.min_occurs = spec['definition']['min']
        self.max_occurs = spec['definition']['max']
        if 'reference_type' in spec['definition']:
            self.reference_types = spec['definition']['reference_type']

    def _push_ancestors(self, jsondict, path_elems, elem_ancestors):
        cur_key = path_elems[0]
        if cur_key not in jsondict:
            return
        val = jsondict[cur_key]
        if isinstance(val, dict):
            elem_ancestors.append((val, path_elems[1:]))
        else:
            elem_ancestors.extend(
                [(ancestor, path_elems[1:]) for ancestor in val])
    
    def get_element_path(self):
        return self.path

    def validate(self, data):
        path_elems = self.path.split('.')
        if len(path_elems) == 1:
            return True
        elem_name = path_elems[-1]
        path_elems = path_elems[1:-1]
        elem_parents = []
        elem_ancestors = []

        if len(path_elems) == 0:
            elem_parents = [data]
        else:
            self._push_ancestors(data, path_elems, elem_ancestors)

        while len(elem_ancestors) > 0:
            ancestor, ancestor_path = elem_ancestors.pop()
            if len(ancestor_path) == 0:
                elem_parents.append(ancestor)
            else:
                self._push_ancestors(ancestor, path_elems, elem_ancestors)

        for parent in elem_parents:
            if not isinstance(parent, dict):
                print 'error: ',
                print parent
                return False

            elem = parent.get(elem_name)

            if elem is None:
                if self.min_occurs > 0:
                    print 'required missing'
                    return False
                continue

            if isinstance(elem, list):
                if self.max_occurs != "*":
                    print 'too many'
                    return False

                elems = elem
                for i, elem in enumerate(elems):
                    if not self.validate_elem(elem):
                        return False

            elif not self.validate_elem(elem):

                return False

            elif self.max_occurs == '*':
                # in this case, the elem itself is correct, with a cardinality
                # or '*' but stored as a single item
                parent[elem_name] = [elem]

        return True

    def validate_elem(self, elem):
        is_elem_validate = False
        for elem_type in self.elem_types:
            if elem_type in FHIR_PRIMITIVE_VALIDATORS:
                validate_func = FHIR_PRIMITIVE_VALIDATORS[elem_type]
                if not validate_func(elem):
                    print 'error element',
                    print elem
                else:
                    is_elem_validate = True
            
            elif elem_type == "Reference":
                if not validate_reference(elem, self.reference_types):
                    print 'reference error' 
                else:
                    is_elem_validate = True

            elif elem_type.lower() == 'resource' and 'resourceType' in elem:
                elem_type = elem['resourceType']
                valid = parse(elem_type, elem)
                if valid:
                    is_elem_validate = True
            
            else:
                # type of the element is a complex type
                valid = parse(elem_type, elem)
                if valid:
                    is_elem_validate = True

        return is_elem_validate

def get_resource_spec(resourceType, version):
    url = versions_url[version] % resourceType.lower()
    r = requests.get(url)
    if r.status_code < 400:
        spec_json = r.json()
        spec_obj = {
            'elements':[]
        }
        for ele in spec_json['snapshot']['element']:
            new_ele = {
                'path': ele['path'],
                'definition':{
                    'max':ele['max'],
                    'min': ele['min']
                }
            }
            if 'type' in ele:
                ele_type = []
                refs = []
                for et in ele['type']:
                    if 'code' not in et:
                        continue
                    ele_type.append(et['code'])
                    if "Reference" == et['code'] and 'targetProfile' in et:
                        refs.append( et['targetProfile'][et['targetProfile'].rindex('/')+1:])
                new_ele['definition']['type'] = list(set(ele_type))
                new_ele['definition']['reference_type'] = list(set(refs))
            spec_obj['elements'].append(new_ele)
        return spec_obj
    else:
        return None

def get_resource_extensions(data):
    extension_list = []
    if 'extension' in data:
        for ext in data['extension']:
            ext_url = ext['url']
            if '/' in ext_url:
                ext_name = ext_url[ext_url.rfind('/')+1:]
                extension_list.append(ext_name)
    return extension_list

def parse(datatype, data, version=1):
    #get datatype spec
    spec = None
    spec = get_resource_spec(datatype, version)
    if spec is None:
        print 'spec none'
        return False
    else:
        elements = [FHIRElement(element_spec)
                    for element_spec in spec['elements']]
        for element in elements:
            if not element.validate(data):
                print element.get_element_path()
                return False    
    return True

def run_validate(datatype, data, version=1):
    if 'text' in data:
        del data['text']
    is_validate = parse(datatype, data, version)
    extension_list = []
    if is_validate:
        extension_list = get_resource_extensions(data)
    return is_validate, extension_list