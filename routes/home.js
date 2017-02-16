var express = require('express');
var router = express.Router();
var serverAction = require('../services/serverAction');
var matrixAction = require('../services/matrixAction');
var viewAction = require('../services/viewAction');

var add_new_server = serverAction.add_new_server;
var all_servers = serverAction.all_servers;
var delete_server = serverAction.delete_server;
var rmatrix = matrixAction.rmatrixAction;
var ttime = matrixAction.ttimeAction;
var cmatrix = matrixAction.cmatrixAction;
var submit_task = viewAction.submit_task;
var get_resources = viewAction.get_resources;
var get_user_task_history = viewAction.get_user_task_history;
var search_task = viewAction.search_task;

router.get('/', function(req, res, next) {
	res.send('respond with a resource');
});

router.post('/addServer', function(req, res, next){
    var name = req.body.name;
    var url = req.body.url;
    var access_token = null;
    console.log(name)
    if( req.body.token ){
        access_token = req.body.token;
    }
    add_new_server(name, url, access_token);
    res.json({isSuccessful:true});
});

router.get('/servers', function(req, res, next){
    var servers = all_servers();
    res.json({
        isSuccessful:true,
        servers:servers
    });
})

router.post('/deleteServer', function(req, res, next) {
    var server_id = req.body.id;
    var isSuccessful = delete_server(server_id);
    res.json({
        isSuccessful:isSuccessful,
        error: !isSuccessful ? 'Server cannot be deleted' : null
    });
})
/**/
router.get('/submit_task', function(req, res, next){
	// get code, language, type
	var result = submit_task(req.body);
	res.json(result);
});

router.get('/get_resources', function(req, res, next){
    var result = get_resources(req.body);
    res.json(result);
});

router.get('/get_user_task_history', function(req, res, next){
    var result = get_user_task_history(req.body);
    res.json(result);
});

router.get('/search_task', function(req, res, next){
    var result = search_task(req.body);
    res.json(result);
});

router.get('/rmatrix', function(req, res, next){
	// get_resource_matrix
	// rmatrix 
	// set JSON type
	var rmat = rmatrix(req.body.rmatrix);
	console.log('rmatrix: ', rmat);
	res.json({
		links:rmat.links,
        resources:rmat.resources,
        servers:rmat.servers	
	});
});

router.post('/ttime', function(req, res, next){
	// all test time
	var ttimes = ttime(req.body.times);
	console.log('times: ', ttimes);
	res.json({
        isSuccessful:ttimes.isSuccessful,
        times:ttimes.times
    });
});

router.post('/cmatrix', function(req, res, next){
	// certain matrix
	var cmat = cmatrix(req.body.matrix);
	console.log('cmatrix: ', cmat);
	res.json({
        isSuccessful:cmat.isSuccessful,
        matrix:{
            links:cmat.matrix.links,
            resources:cmat.matrix.resources,
            servers:cmat.matrix.servers
        }
	});
});

module.exports = router;
