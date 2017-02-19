let CryptoJS = require('crypto-js');
let config = require('../config');
let models = require('../models');
let Resource = models.Resource;
let ResourceDao = models.ResourceDao;
let Level = models.Level;
let LevelDao = models.LevelDao;
let FHIRServer = models.FHIRServer;
let FHIRServerDao = models.FHIRServerDao;
let Task = models.Task;
let TaskDao = models.TaskDao;
let userAction = require('./userAction');
var test_type = config.task;


// generate string with length and consist by '0-9 A-Z'
var random_string_generate = function(length){
	var chars = ['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z'];
	var res = "";
	var id = -1;
    for(var i = 0; i < length ; i ++) {
    	id = Math.ceil(Math.random()*35);
    	res += chars[id];
    }
    return res;
}

// return "yyyy-MM-dd HH:MM:SS.mis”
var getNowDate = function() {
    var date = new Date();
    var seperator1 = "-";
    var seperator2 = ":";
    var year = date.getFullYear();
    var month = date.getMonth() + 1;
    var day = date.getDate();
    var hour = date.getHours();
    var minute = date.getMinutes();
    var second = date.getSeconds();
    var millis = date.getMilliseconds();
    if (month >= 1 && month <= 9) {
        month = "0" + month;
    }
    if (day >= 0 && day <= 9) {
        day = "0" + day;
    }
    var currentdate = year + "-" + month + "-" + day + "T" + hour + ":" + minute + ":" + second + "." + millis + "000";
    return currentdate;
}

// SHA1 code length = 10
var form_taskname = function(salt){
    salt += random_string_generate(3)
    timestamp = getNowDate()
    return CryptoJS.SHA1(timestamp+salt).substr(0,10);
}

/*
var test_task_class = {
	createNew: function(){
		var obj = {}

		obj.init = function(){
			var resources = arguments[0] ? arguments[0] : [];
			var language = arguments[1] ? arguments[1] : "";
			var code = arguments[2] ? arguments[2] : "";
			var test_type = arguments[3] ? arguments[3] : 0;
			var url = arguments[4] ? arguments[4] : "";
			var server_id = arguments[5] ? arguments[5] : undefined;
			var access_token = arguments[6] ? arguments[6] : undefined;
			var username = arguments[7] ? arguments[7] : undefined;

			this.test_type = test_type;
	        this.language = language;
	        this.username = username;
	        this.resources = resources;
	        this.code = code;
	        this.url = url;
	        this.server_id=server_id;
	        this.task_name = form_taskname(language);
	        this.result = '';
	        this.access_token = access_token;
	        this.status='created';
	        this.level = undefined;
	        this.baseid_dict = {};
	        this.is_finished = false;

	        // create database object ??
	        with transaction.atomic(){
	            new_task = task(task_id=self.task_name,language=self.language,task_type=self.test_type, status=self.status,code=self.code, user_id=self.username, target_server_id=server_id)
	            try{
	                new_task.save()
	            }
	            catch(err){
	                self.form_error_report("Database object creation failed, process killed")
	                self.save_result()
	        	}
	        }
	        //
		};

		obj.isProcessable = function(){
			if(this.test_type == 1){
				return true
			}
			return false;
		};

		obj.get_id = function(){  return this.task_name;  };
		
		return obj;
	}
};

var perform_test = function(language, code, url, test_type){
    var server_id = arguments[4] ? arguments[4] : undefined; 
    var resource_list = arguments[5] ? arguments[5] : []; 
    var access_token = arguments[6] ? arguments[6] : undefined; 
    var username = arguments[7] ? arguments[7] : undefined;
    var new_test_task = test_task_class.createNew();
    new_test_task.init(resources=resource_list,language=language,code=code,test_type=test_type,url=url,server_id=server_id,access_token=access_token, username=username);
    // run_test_task.delay(new_test_task) ???
    return new_test_task.get_id()
}
*/

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
            var intID = parseInt(req_json['chosen_server']);
            let server_list = FHIRServerDao.findOne({
                id:intID
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
	var task_obj = TaskDao.findOne({
		language: language,
		code: code,
		// url:url,
		test_type: test_type,
		// server_id:req_json['chosen_server'], 
		// resource_list:resource_list, 
		// access_token:access_token, 
		user: username
	})
	task_id = task.obj.id;
/*
    if (req_json["chosen_server"] != undefined ){
        
        task_id = perform_test(language=language,code=code,url=url,test_type=test_type,server_id=req_json['chosen_server'], resource_list=resource_list, access_token=access_token, username=username)
    }
    else{

        task_id = perform_test(language=language,code=code,url=url,test_type=test_type,server_id=undefined, resource_list=resource_list, access_token=access_token, username=username)
    }
*/
    var result = {
        'isSuccessful':true,
        'task_id':task_id
    }
    return result;
}

var get_resources = function(resource_type){
    var result = [];
    var resources = null;
    if( resource_type == 0 || resource_type === '0' ){
        resources = ResourceDao.find({});
    }else{
        resources = LevelDao.find({});
    }
    if( resources ){
        resources.forEach(resource_obj => {
            result.push({
                name:resource_obj.name,
                checked:true
            });
        });
    }
    return result;
}

var get_user_task_history = function(user_token){
    var results = [];
    var username = userAction.get_token_username(user_token);
    var user_obj = userAction.get_user_obj(username);   
    if( user_obj ){
        var task_list = TaskDao.find({
            user:user_obj
        });
        task_list.forEach( task_obj =>{
            results.push({
                task_id: task_obj.id,
                time: task_obj.create_time.toUTCString()
            })
        });
    }
    return results;
}

// var search_task = function(req_json){
//     var keyword = req_json['keyword'];
//     var result = {
//         'isSuccessful': true
//     }
//     result['tasks'] = search_basedon_id(keyword);
//     return result;
// }

module.exports = {
    submit_task,
    get_resources,
    get_user_task_history
    // search_task
}