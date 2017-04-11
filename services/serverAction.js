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
            for( var scope in server_info.scopes ){
                var new_server_scope = new ServerAuthScope({
                    name: server_info.auth_info.scopes[scope]
                });
                ServerAuthScopeDao.create(new_server_scope)
                ServerAuthInfoDao.update({
                    id:new_server_auth.id
                },{
                    $push:{
                        scopes:new_server_scope.id
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

var update_server = function(server_id, server_info, server_info){
    // check and update auth info first
    if( server_info.is_auth_required ){
        //update or create auth info
        if( server_info.auth_info.id ){
            // update server auth info
            ///update scope first
            if( server_info.auth_info.scopes.length > 0 ){
                server_info.auth_info.scopes.map(scope_info => {
                    
                });
            }
            ServerAuthInfoDao.update({
                id:server_info.auth_info.id
            },server_info.auth_info)
        }else{
            // create new auth info
        }
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
    ping_server
}