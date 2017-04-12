var express = require('express');
var router = express.Router();
var serverAction = require('../services/serverAction')
var taskAction = require('../services/taskAction');
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

router.post('/addServer', function(req, res, next){
    console.log(req.body);
    isSuccessful = add_new_server(req.body);
    res.json({isSuccessful:isSuccessful});
});

router.get('/servers', function(req, res, next){
    var servers = all_servers();
    res.json({
        isSuccessful:true,
        servers:servers
    });
});

router.get('/serverInfo', function(req, res, next){
    var server_id = req.query.server_id;
    var server_info = serverAction.get_server_info(server_id);
    console.log(server_info);
    var result = {
        isSuccessful: server_info != null,
        server_info: server_info
    }
    res.json(result);
});

router.post('/ping', function(req, res, next){
    var url = req.body.url;
    serverAction.ping_server(url, res);
});

router.post('/deleteServer', function(req, res, next) {
    var server_id = req.body.id;
    var isSuccessful = delete_server(server_id);
    res.json({
        isSuccessful:isSuccessful,
        error: !isSuccessful ? 'Server cannot be deleted' : null
    });
})
/**/
// router.get('/submit_task', function(req, res, next){
// 	// get code, language, type
// 	var result = submit_task(req.body);
// 	res.json(result);
// });

router.post('/submit_task', function(req, res, next){
    var raw_task_info = req.body;
    console.log(raw_task_info);
    var processed_task_info = taskAction.pre_process_task_info(raw_task_info);
    console.log(processed_task_info);
    var created_task_id = taskAction.create_new_task(processed_task_info);
    console.log(created_task_id);
    var result = {
        task_id:created_task_id,
        isSuccessful: false
    }
    if( created_task_id ){
        result.isSuccessful = true;
    }
    res.json(result);
});

router.get('/task_types', function(req, res, next){
    var task_types = taskAction.get_task_types()
    result = {
        isSuccessful:true,
        task_types:task_types
    }
    res.json(result);
});

router.get('/get_resources', function(req, res, next){
    var result = {
        isSuccessful:true,
        names:[]
    }
    var resources = get_resources(req.query.type);
    result.names = resources;
    res.json(result);
});

// router.get('/get_user_task_history', function(req, res, next){
//     try{
//         var user_token = req.query.token;

//     }catch( err ){
//         return res.json({
//             isSuccessful:false,
//             error: "Invalid User",
//             tasks:[]
//         });
//     }
//     var result = get_user_task_history(user_token);
//     res.json({
//         isSuccessful:true,
//         tasks:result
//     });
// });

// router.get('/search_task', function(req, res, next){
//     var result = {
//         isSuccessful:true,
//         tasks:[]
//     }
//     res.json(result);
// });

// router.get('/rmatrix', function(req, res, next){
// 	// get_resource_matrix
// 	// rmatrix 
// 	// set JSON type
// 	var rmat = rmatrix(req.query.rmatrix);
// 	console.log('rmatrix: ', rmat);
// 	res.json({
// 		links:rmat.links,
//         resources:rmat.resources,
//         servers:rmat.servers	
// 	});
// });

function getRandomArbitrary(min, max) {
  return Math.floor(Math.random() * (max - min)) + min;
}

router.get('/rmatrix', function(req, res, next){
    //get default random matrix
    // random task type
    var task_types = taskAction.get_task_types();
    var random_task_type = task_types[getRandomArbitrary(0, task_types.length)].id;
    var matrix_data = matrixAction.form_matrix(random_task_type, null);
    res.json(matrix_data);
})

router.post('/ttime', function(req, res, next){
	// all test time
    var times = taskAction.get_task_times(req.body.task_type);
    res.json({
        isSuccessful:true,
        times:times
    });
	// var ttimes = ttime(req.body);
	// console.log('times: ', ttimes);
	// res.json({
    //     isSuccessful:ttimes.isSuccessful,
    //     times:ttimes.times
    // });
});

// router.post('/cmatrix', function(req, res, next){
// 	// certain matrix
// 	var cmat = cmatrix(req.body.matrix);
// 	console.log('cmatrix: ', cmat);
// 	res.json({
//         isSuccessful:cmat.isSuccessful,
//         matrix:{
//             links:cmat.matrix.links,
//             resources:cmat.matrix.resources,
//             servers:cmat.matrix.servers
//         }
// 	});
// });

router.post('/cmatrix', function(req, res, next){
    console.log(req.body)
    var task_type_id = req.body.task_type;
    var task_time = null;
    if( req.body.hasOwnProperty('time') ){
        task_time = req.body.time;
    }
    var matrix_data = matrixAction.form_matrix(task_type_id, task_time);
    res.json({
        isSuccessful:true,
        matrix:matrix_data
    });
});

module.exports = router;
