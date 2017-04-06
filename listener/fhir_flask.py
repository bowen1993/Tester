# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import fhir_validator

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/validate', methods=['POST','GET'])
@cross_origin()
def validater():
	# print "\n\nget it: ",request.json, "\n\n"
	print request.json
	request_json = request.json
	print request_json['resource']
	data = request_json['resource']

	datatype = data['resourceType']
	version = request_json['version']
	result = fhir_validator.parse(datatype, data, version)
	res = jsonify({"is_validate": result})
	return res

if __name__ == '__main__':
	app.run(debug=True)