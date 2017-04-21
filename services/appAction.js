let models = require('../models');
var uuid = require('node-uuid');
let App = models.App;
let AppDao = models.AppDao;
let User = models.User;
let UserDao = models.UserDao;
let scopeAction = require('./scopeAction');
let userAction = require("./userAction")

var appVerify = function(client_id, redirect_uri, scopes){
    var scope_list = scopes.split(/\+/);
    var app_obj = AppDao.findOne({
        client_id:client_id,
        redirect_uri: redirect_uri
    });
    if( app_obj && scope_compare(scopes, app_obj) ){
        return true;
    }
    else{
        return false;
    }
}

var app_register = function(app_info, username){
    var user_obj = userAction.get_user_obj(username);
    if( !user_obj || !app_info_validate(app_info) ){
        return null;
    }
    var client_id = uuid.v4();
    var scope_objs = scopeAction.sarray2oarray(app_info.scopes);

    if( !scope_objs ){
        return null;
    }

    var new_app = new App({
        name : app_info.name,
        author : user_obj,
        scopes: scope_objs,
        is_stand_alone: app_info.is_stand_alone,
        launch_uri: app_info.is_stand_alone ? app_info.launch_uri : null,
        redirect_uri: app_info.redirect_uri,
        is_patient_required : app_info.is_patient_required,
        client_id:client_id
    });
    AppDao.create(new_app);
    return client_id;

}

var app_info_validate = function(app_info){
    var is_valid = true;
    if( !app_info || 
    !app_info.name || 
    app_info.name.length == 0 || 
    !app_info.redirect_uri ){
        is_valid = false;
    }
    if( !app_info.is_stand_alone && 
    (!app_info.launch_uri || pp_info.launch_uri.length == 0) ){
        is_valid = false;
    }
    return is_valid;
}

var scope_compare = function(scopes, app_obj){
    var app_scopes = scopeAction.oarray2sarray(app_obj.scopes);
    if( scopes.length != app_scopes.length ){
        return false;
    }
    for( var i = 0; i < scopes.length; i++ ){
        if ( scopes[i] != app_scopes[i] ){
            return false;
        }
    }
    return true;
}

module.exports = {
    appVerify
}