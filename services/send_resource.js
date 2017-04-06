var requestify = require('requestify');

var doPost = function(url, data, res){
    var headers = {
        'Content-Type':'application/json'
    }
    requestify.post(url, data, {headers:headers, timeout:30000}).then(function(response){
      res.send(response.getBody());
    }).fail(function(response){
      res.status(response.getCode())
      res.send(response.getBody());
    });
}

module.exports = {
    doPost:doPost
}