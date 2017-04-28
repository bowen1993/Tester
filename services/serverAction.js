let models = require('../models');
let Server = models.FHIRServer;
let ServerDao = models.FHIRServerDao;
let ServerAuthInfo = models.ServerAuthInfo;
let ServerAuthInfoDao = models.ServerAuthInfoDao;
let ServerAuthScope = models.ServerAuthScope;
let ServerAuthScopeDao = models.ServerAuthScopeDao;
let requestify = require('requestify');


var add_new_server = function(server_info){
    var new_server = new Server({
        name: server_info.name,
        url: server_info.url,
        is_deleted: false,
        is_deletable: true,
        is_auth_required: server_info.is_auth_required
    })
    ServerDao.create(new_server);
    if( server_info.is_auth_required ){
        // create server auth
        var new_server_auth = new ServerAuthInfo({
            client_id: server_info.auth_info.client_id,
            redirect_uri: server_info.auth_info.redirect_uri,
            auth_url:server_info.auth_info.auth_url,
            token_url:server_info.auth_info.token_url
        });
        try{
            ServerAuthInfoDao.create(new_server_auth);
            for( var scope in server_info.auth_info.scopes ){
                console.log(server_info.auth_info.scopes[scope]);
                var new_server_scope = new ServerAuthScope({
                    name: server_info.auth_info.scopes[scope].name
                });
                ServerAuthScopeDao.create(new_server_scope)
                ServerAuthInfoDao.update({
                    id:new_server_auth.id
                },{
                    $push:{
                        scopes:new_server_scope
                    }
                });
            }
            ServerDao.update({
                id:new_server.id
            },{
                $push:{
                    auth_info:new_server_auth
                }
            });
        } catch( err ){
            console.log(err);
            return false;
        }
    }
    return true;
}

var update_server = function(server_id, server_info){
    // check and update auth info first
    var is_successful = false;
    var server_obj = get_server_obj(server_id);
    if( server_obj ){
        // update basic infos
        ServerDao.update({
            id:server_id
        },{
            name:server_info.name,
            url:server_info.url,
            is_auth_required:server_info.is_auth_required,
        });
        // update auth info
        if( server_info.is_auth_required ){
            var auth_obj = null;
            // create auth object if not exists
            if( server_obj.auth_info == null ){
                //create new auth
                console.log("creating new auth")
                auth_obj = new ServerAuthInfo({
                    client_id: server_info.auth_info.client_id,
                    redirect_uri: server_info.auth_info.redirect_uri,
                    auth_url:server_info.auth_info.auth_url,
                    token_url:server_info.auth_info.token_url
                });
                try{
                    ServerAuthInfoDao.create(auth_obj);
                    ServerDao.update({
                        id:server_id
                    },{
                        $push:{
                            auth_info:auth_obj
                        }
                    });
                }catch( err ){
                    console.log(err);
                    return false;
                }
            } else {
                console.log("updating auth");
                auth_obj = server_obj.auth_info
                try{
                    ServerAuthInfoDao.update(
                        {id:auth_obj.id},{
                            client_id: server_info.auth_info.client_id,
                            redirect_uri: server_info.auth_info.redirect_uri,
                            auth_url:server_info.auth_info.auth_url,
                            token_url:server_info.auth_info.token_url
                    });
                } catch( err ){
                    console.log(err);
                    return false;
                }  
            }
            console.log("basic auth updated");
            try{
                ServerAuthInfoDao.update({
                    id:auth_obj.id
                },{
                    $unset:{
                        scopes:[]
                    }
                });
            }catch( err ){
                console.log(err);
                return false;
            }
            console.log("scope removed");
            //update scopes
            if( server_info.auth_info.scopes && server_info.auth_info.scopes.length > 0 ){
                server_info.auth_info.scopes.map(scope_info => {
                            var new_server_scope = new ServerAuthScope({
                                name: scope_info.name
                            });
                            ServerAuthScopeDao.create(new_server_scope);
                            ServerAuthInfoDao.update({
                                id:auth_obj.id
                            },{
                                $push:{
                                    scopes:new_server_scope
                                }
                            });
                        });
            }
        }else{
            if( server_obj.auth_info != null ){
                ServerDao.update({
                    id:server_id
                },{
                    $unset:{
                        auth_info:{}
                    }
                })
            }
        }
        return true
    }else{
        return false
    }
}

var all_servers = function(){
    var servers = ServerDao.find({
        is_deleted:false
    });
    var format_servers = Server.toObjectArray(servers,{recursive: true});
    return format_servers;
}

var ping_server = function(url, res){
    requestify.get(url).then( response => {
        res.json({
            is_reachable: true
        });
    }).fail( error => {
        res.json({
            is_reachable: false
        });
    });
}

var delete_server = function(server_id){
    var server = ServerDao.findOne({
        id:server_id
    });
    var isSuccessful = false;
    if( server && server.is_deletable){
        server.is_deleted = true;
        ServerDao.update(server)
        isSuccessful = true
    }
    return isSuccessful;
}

var get_server_obj = function(server_id){
    try{
        var server = ServerDao.findOne({
            id:server_id
        });
        return server;
    }catch(err){
        console.log(err);
        return null;
    }
}

var get_server_info = function(server_id){
    var server_obj = get_server_obj(server_id);
    console.log(server_obj);
    if( server_obj ){
        return server_obj.toObject({
            recursive: true
        });
    }else{
        return null;
    }
}

module.exports = {
    add_new_server,
    all_servers,
    delete_server,
    get_server_obj,
    get_server_info,
    update_server,
    ping_server
}