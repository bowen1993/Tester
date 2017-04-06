var express = require('express');
var router = express.Router();
var send_resource = require('../services/send_resource');

var listener_url = "http://localhost:5000/validate"

router.post('/', function(req, res, next){
    
    var req_data = req.body;
    return send_resource.doPost(listener_url, req_data, res);
});

module.exports = router;