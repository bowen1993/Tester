let models = require('../models');
let Server = models.FHIRServer;
let ServerDao = models.FHIRServerDao;
let ServerAuthInfo = models.ServerAuthInfo;
let ServerAuthInfoDao = models.ServerAuthInfoDao;
let ServerAuthScope = models.ServerAuthScope;
let ServerAuthScopeDao = models.ServerAuthScopeDao;


var add_new_server = function(server_info){
    var new_server = new Server({
        name: server_info.nane,
        url: server_info.url,
        is_deleted: false,
        is_deletable: true,
        is_auth_required: server_info.is_auth_required
    })
    ServerDao.create(new_server);
    if( server_info.is_auth_required ){
        // create server auth
        var new_server_auth = new ServerAuthInfo({
            client_id: server_info.client_id,
            redirect_uri: server_info.redirect_uri,
            auth_url:server_info.auth_url,
            token_url:server_info.token_url
        });
        try{
            ServerAuthInfoDao.create(new_server_auth);
            for( var scope in server_info.scopes ){
                var new_server_scope = new ServerAuthScope({
                    name: server_info.scopes[scope]
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

var all_servers = function(){
    var servers = ServerDao.find({
        is_deleted:false
    });
    var format_servers = Server.toObjectArray(servers,{recursive: true});
    return format_servers;
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

module.exports = {
    add_new_server,
    all_servers,
    delete_server,
    get_server_obj
}