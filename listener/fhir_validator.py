#!/usr/bin/env python
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
DECIMAL_RE = re.compile(r'^\d*\.?\d*$')

lower_first = lambda s: s[:1].lower() + s[1:] if s else ''
remove_type_path = lambda s: s[s.find('.')+1:] if '.' in s else s

def validate_by_regex(regex):
    return lambda data: regex.match(str(data)) is not None


def validate_by_instance(datatype):
    return lambda data: isinstance(data, datatype)

FHIR_PRIMITIVE_VALIDATORS = {
    'base64Binary': validate_by_instance(unicode),
    'boolean': validate_by_instance(bool),
    'date': validate_by_regex(DATE_RE),
    'dateTime': validate_by_regex(DATETIME_RE),
    'decimal': validate_by_regex(DECIMAL_RE),
    'id': validate_by_regex(ID_RE),
    'instant': validate_by_regex(INSTANT_RE),
    'integer': validate_by_instance(int),
    'positiveInt': validate_by_instance(int),
    'unsignedInt': validate_by_instance(int),
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

FHIR_PRIMITIVE_TYPES = ['base64Binary', 'boolean', 'date', 'dateTime', \
    'decimal', 'id', 'instant', 'integer', 'positiveInt', 'oid', \
    'string', 'uri', 'uuid', 'code', 'BackboneElement']

def validate_reference(element, reference_types):
    #get reference in element
    if 'reference' not in  element:
        return False
    
    ref_type = element["reference"][:element["reference"].find('/')]
    return ref_type in reference_types
        

class FHIRElement(object):

    def __init__(self, spec):
        self.path = spec['path']
        self.errors = []
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
        if len(self.elem_types) == 0:
            return True, self.errors
        path_elems = self.path.split('.')
        is_validate = True
        if len(path_elems) == 1:
            is_validate = True
            return True, self.errors
        element_name = path_elems[-1]
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
                print 'error: '
                print parent
                self.errors.append({
                    "error": "Not a valid resource",
                    "path": self.get_element_path()
                })
                return False, self.errors
            ele_names = []
            if '[x]' in element_name:
                for ele_type in self.elem_types:
                    elem_type_name = element_name.replace('[x]', ele_type)
                    ele_names.append((elem_type_name, ele_type))
            else:
                ele_names = [(element_name,self.elem_types[0])]
            if len(ele_names) > 1:
                elem = []
                for elname in ele_names:
                    if elname[0] in parent:
                        elem.append((parent.get(elname[0]), elname[1]))
            else:
                elem = (parent.get(ele_names[0][0]), ele_names[0][1])
            if len(elem) == 0 or elem[0] is None:
                if self.min_occurs > 0:
                    self.errors.append({
                        "error": "Required Element %s Missing" % element_name,
                        "path": self.get_element_path()
                    })
                    print 'required missing'
                    is_validate = False
                continue
            if isinstance(elem, list):
                if self.max_occurs != "*" and len(elem) > 1:
                    self.errors.append({
                        "error": "Element should not be more than one",
                        "path": self.get_element_path()
                    })
                    print 'too many',
                    print self.get_element_path(),
                    print elem
                    
                    is_validate = False

                elems = elem
                for i, elem in enumerate(elems):
                    if not self.validate_elem(elem[0], elem[1]):
                        is_validate = False
            elif isinstance(elem[0], list):
                if self.max_occurs != "*":
                    self.errors.append({
                        "error": "Element should not be more than one",
                        "path": self.get_element_path()
                    })
                    print 'too many',
                    print self.get_element_path(),
                    print elem
                    is_validate = False
                elems = elem[0]
                for i, ele in enumerate(elems):
                    if not self.validate_elem(ele, elem[1]):
                        is_validate = False
                
            elif not self.validate_elem(elem[0], elem[1]):

                is_validate = False

            elif self.max_occurs == '*':
                # in this case, the elem itself is correct, with a cardinality
                # or '*' but stored as a single item
                parent[element_name] = [elem[0]]

            for elname in ele_names:
                if elname[0] in parent:
                    if isinstance(parent[elname[0]], dict) or isinstance(parent[elname[0]], list):
                        if len(parent[elname[0]]) == 0:
                            del parent[elname[0]]
                    else:
                        del parent[elname[0]]
        return is_validate, self.errors

    def validate_elem(self, elem, elem_type):
        is_elem_validate = False
        if elem_type in FHIR_PRIMITIVE_VALIDATORS:
            print 'primitive type'
            validate_func = FHIR_PRIMITIVE_VALIDATORS[elem_type]
            if validate_func(elem):
                is_elem_validate = True
        
        elif elem_type == "Reference":
            print 'reference'
            if not validate_reference(elem, self.reference_types):
                self.errors.append({
                    "error": "Reference in Error",
                    "path": self.get_element_path()
                })
                print 'reference error'
            else:
                is_elem_validate = True

        elif elem_type.lower() == 'resource' and 'resourceType' in elem:
            print 'resource type'
            elem_type = elem['resourceType']
            valid, errors = parse(elem_type, elem, self.get_element_path())
            self.errors.extend(errors)
            if valid:
                is_elem_validate = True
        
        else:
            print 'complex'
            # type of the element is a complex type
            valid, errors = parse(elem_type, elem, self.get_element_path())
            self.errors.extend(errors)
            if valid:
                is_elem_validate = True
        if not is_elem_validate:
            print 'error element'
            self.errors.append({
                "error": "Element not in correct data type",
                "path": self.get_element_path()
            })
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

def get_element_types(element_obj):
    ele_type = []
    if 'type' in element_obj:
        for et in element_obj['type']:
            if 'code' not in et:
                continue
            ele_type.append(et['code'])
    return ele_type

def get_path_spec(resourceType, parent, version):
    url = versions_url[version] % resourceType.lower()
    r = requests.get(url)
    spec_obj = []
    if r.status_code < 400:
        spec_json = r.json()
        for ele in spec_json['snapshot']['element']:
            inner_path = remove_type_path(ele['path'])
            final_path = '%s.%s' % (parent, inner_path)
            print final_path
            spec_obj.append(final_path)
            types = get_element_types(ele)
            for ele_type in types:
                if ele_type not in FHIR_PRIMITIVE_TYPES:
                    print 'type: %s' % ele_type
                    spec_obj.extend(get_path_spec(ele_type, final_path, version))
    return spec_obj

def get_resource_extensions(data):
    extension_list = []
    if 'extension' in data:
        for ext in data['extension']:
            ext_url = ext['url']
            if '/' in ext_url:
                ext_name = ext_url[ext_url.rfind('/')+1:]
                extension_list.append(ext_name)
    return extension_list

def parse(datatype, data, parent_path, version=1):
    #get datatype spec
    spec = None
    if 'text' in data:
        del data['text']
    errors = []
    is_valid_element = True
    spec = get_resource_spec(datatype, version)
    if spec is None:
        print 'spec none'
        return False, errors
    else:
        elements = [FHIRElement(element_spec)
                    for element_spec in spec['elements']]
        for element in elements:
            is_valid, e = element.validate(data)
            errors.extend(e)
            if not is_valid:
                is_valid_element = False
    return is_valid_element, errors

def get_resources(data):
    entries = []
    if 'entry' in data:
        entries = data['entry']
    return list({x['resource']['resourceType'] for x in entries})

def run_validate(datatype, data, version=1):
    if 'text' in data:
        del data['text']
    is_validate, errors = parse(datatype, data, "%s." % datatype, version)
    print is_validate, errors
    resources = []
    if is_validate and "resourceType" in data and data['resourceType'] == 'Bundle':
        resources = get_resources(data)
    if "resourceType" in data:
        del data['resourceType']
    print data
    extension_list = []
    if is_validate:
        extension_list = get_resource_extensions(data)
    return is_validate, extension_list, errors, resources