let models = require('../models');
let serverAction = require('./serverAction');
let userAction = require('./userAction');
let Task = models.Task;
let TaskDao = models.TaskDao;
let TaskType = models.TaskType;
let TaskTypeDao = models.TaskTypeDao;


var task_keywords = ['target_server', 'task_type', 'code_status', 'username']

var validate_task_info = function(task_info){
    // validate task info
    return true;
}

var pre_process_task_info = function(task_info){
    // extract parameters from raw task info
    console.log(task_info);
    var parameters = {};
    for( key in task_info ){
        if( task_info.hasOwnProperty(key) ){
            // check key task info or task parameters
            if( task_keywords.indexOf(key) < 0 ){
                console.log(key)
                parameters[key] = task_info[key];
                console.log(task_info[key])
                delete task_info[key];
            }
        }
    }
    task_info['parameters'] = parameters;
    console.log(parameters)
    return task_info;
}

var create_new_task = function(task_info){
    var server_obj = serverAction.get_server_obj(task_info.target_server);
    var user_obj = userAction.get_user_obj(task_info.username);
    var task_type_obj = get_task_type_obj(task_info.task_type);

    if( !task_type_obj ){
        console.log("Invalid task type");
        return null;
    }
    var new_task = new Task({
        task_type:task_type_obj,
        task_parameters: JSON.stringify(task_info.parameters),
        code_status: 'WTNG',
        create_time: Date.now(),
        is_processed: false
    });
    if( user_obj ){
        new_task.user = user_obj;
    }
    if( server_obj ){
        new_task.target_server = server_obj;
    }
    if( task_info.hasOwnProperty('code') ){
        new_task.code = task_info.code;
    }
    if( task_info.hasOwnProperty('language') ){
        new_task.language = task_info.language;
    }
    try{
        TaskDao.create(new_task);
    }
    catch(err){
        console.log(err);
        return null;
    }
    return new_task.id;
}

var get_task_obj = function(task_id){
    var task_obj = null;
    try{
        task_obj = Task.objects.findOne({id:task_id});
    }catch(err){
        console.log(err);
    }
    return task_obj;
}

var get_task_info = function(task_id){
    var task_obj = get_task_obj(task_id);
    var task_info = null;
    if( task_obj ){
        task_info = task_obj.toObject({
            recursive: true
        });
    }
    return task_info;
}

var get_task_type_obj = function(task_type_id){
    console.log(task_type_id);
    task_type_obj = null;
    try{
        task_type_obj = TaskTypeDao.findOne({id:task_type_id});
    }catch(err){
        console.log(err);
    }
    return task_type_obj;
}

module.exports = {
    create_new_task,
    get_task_info,
    pre_process_task_info
}