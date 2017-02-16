let config = require('../config');
let models = require('../models');
let Resource = models.Resource;
let ResourceDao = models.ResourceDao;
let FHIRServer = models.FHIRServer;
let FHIRServerDao = models.FHIRServerDao;
let Task = models.Task;
let TaskDao = models.TaskDao;

var test_type = config.task;

var get_token = function(username){
    return window.btoa(username);
}

var extract_username = function(token){
    return window.btoa(token);
}

var test_task = function(){
    // find in home/task_runner
}

var perform_test = function(language, code, url, test_type){
    var server_id = arguments[4] ? arguments[4] : undefined; 
    var resource_list = arguments[5] ? arguments[5] : []; 
    var access_token = arguments[6] ? arguments[6] : undefined; 
    var username = arguments[7] ? arguments[7] : undefined;
    // new_test_task = test_task(resources=resource_list,language=language,code=code,test_type=test_type,url=url,server_id=server_id,access_token=access_token, username=username)
    // run_test_task.delay(new_test_task)
    // return new_test_task.get_id()
    return undefined;
}


var submit_task = function(req_json){
    var code = req_json['code'];
    var language = req_json['language'];
    var test_type = req_json['type'];
    var resource_list = [];
    if (test_type == 3 || test_type == 0) {
        var resource_state = req_json['resources'];
        for (var item in resource_state){
            if (item['checked']) {
                resource_list.push(item['name'])
            }
        }
    }
    if (req_json['chosen_server'] != undefined){
        try{
            intID = parseInt(req_json['chosen_server']);
            let server_list = FHIRServerDao.find({
                // _id = intID
            });
            var url = server_obj.server_url;
            var access_token = server_obj.access_token;
        }
        catch(err){
            var result = {
                'isSuccessful':false,
                'error':"Invalid server"
            }
            return result;
        }
    } else {
        var access_token = req_json['access_token']
        var url = req_json['url']
    }
    var token = undefined;
    try{
        token = req_json['token'];
    }
    catch(err){}
    
    var username = undefined;
    if (token){
        username = extract_username(token);
    }

    var task_id = undefined;
    if (req_json["chosen_server"] != undefined ){
        task_id = perform_test(language=language,code=code,url=url,test_type=test_type,server_id=req_json['chosen_server'], resource_list=resource_list, access_token=access_token, username=username)
    }
    else{
        task_id = perform_test(language=language,code=code,url=url,test_type=test_type,server_id=undefined, resource_list=resource_list, access_token=access_token, username=username)
    }
    var result = {
        'isSuccessful':true,
        'task_id':task_id
    }
    return result;
}

var get_resources = function(req){
    // var res_type = req.GET.get('type', 0);
    var res_type = undefined;
    if (res_type == "String"){
        try{
            res_type = parseInt(res_type);
        }
        catch(err){
            res_type = 0;
        }
    }
    var result = {
        'isSuccessful':false,
        'names':[]
    }
    try{
        var resources = ResourceDao.find({});
        resources.forEach(resource_obj => {
            result['names'].push({'name':resource_obj.name,'checked':true});
        });
        result['isSuccessful'] = true;
    }
    catch(err){}
    return result;
}

var get_user_task_history = function(req_json){
    try{
        var token = req_json['token'];
    }
    catch(err){
        return {'isSuccessful': false };               
    }
    var result = {
        'isSuccessful': false
    }
    if (token){
        try{
            var username = extract_username(token);
            var task_obj_list = TaskDao.find({
                // _id = username
            });
            var task_list = [];
            task_obj_list.forEach(task_obj => {
                var task_id = task_obj.task_id;
                var task_time = task_obj.create_time;
                task_list.push({
                    'task_id':task_id,
                    'time':task_time.toUTCString()
                })
            });
            result['tasks'] = task_list;
            result['isSuccessful'] = true;
        }
        catch(err){}
    }
    return result;
}

var search_task = function(req_json){
    var keyword = req_json['keyword'];
    var result = {
        'isSuccessful': true
    }
    result['tasks'] = search_basedon_id(keyword);
    return result;
}

module.exports = {
    submit_task,
    get_resources,
    get_user_task_history,
    search_task
}