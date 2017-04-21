var jwt = require("jsonwebtoken");
var bodyParser = require("body-parser");
var router = require("express").Router();
var config = require('../configs');
var server_config = config.servers
var appAction = require("../services/appAction");

String.prototype.endsWith = function(suffix) {
    return this.indexOf(suffix, this.length - suffix.length) !== -1;
};
Object.assign = require('object-assign');

router.get("/authorize", function(req, res, next){
    //verify basic app info
    if( req.query.redirect_uri == null || 
        req.query.client_id == null ||
        req.query.scope == null ||
        appAction.appVerify(req.query.client_id, req.query.redirect_uri, req.query.scope) ){
            res.send("Bad Client Info", 400);
            return;
    }
    if( req.query.state == null ){
        res.send("state missing", 400);
        return;
    }
    // generate code with jwt
    var incomingJwt = req.query.launch && req.query.launch.replace(/=/g, "");
    var code = {
        context: incomingJwt && jwt.decode(incomingJwt) || {},
        client_id: req.query.client_id,
        scope: req.query.scope
    };
    var state = req.query.state;
    var signedCode = jwt.sign(code, server_config.jwtSecret, { expiresIn: "5m" });
    res.redirect(req.query.redirect_uri + ("?code=" + signedCode + "&state=" + state));
});

router.post("/token", function(req, res, next){
    if( req.body.grant_type == null ||
        req.body.client_id == null ){
        
        return res.status(400).send("Bad Info")
    }

    var grantType = req.body.grant_type;
    var codeRaw;

    if (grantType === 'authorization_code') {
        if( req.body.code == null ){
            return res.status(400).send("code missed");
        }
        codeRaw = req.body.code;
    } else if (grantType === 'refresh_token') {
        if( req.body.code == null ){
            return res.status(400).send("refresh_token missed");
        }
        codeRaw = req.body.refresh_token;
    }else{
        return res.status(400).send("Invalid Grant Type")
    }
    
    try {
        var code = jwt.verify(codeRaw, server_config.jwtSecret);
    } catch (e) {
        console.log(e);
        return res.status(401).send("Invalid code");
    }

    code.context['refresh_token'] = jwt.sign(code, server_config.jwtSecret);

    var token = Object.assign({}, code.context, {
        token_type: "bearer",
        expires_in: 3600,
        scope: code.scope,
        client_id: req.body.client_id
    });

    res.json(token);
});