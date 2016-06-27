(function(angular) {
    "use strict";

    var app = angular.module('ajax-module', []);

    app.service('ajax-service', ['$http', 'utility-service', function($http, utility){
    	var context = this;

    	this.defaultHeader = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'};
    	this.GET = "GET";
        this.POST = "POST";

        this.ME = "127.0.0.1:5000";

        /**
         * execute a request
         * headers - headers of request
         * url - target url
         * method - method of request
         * params - parameters of request
         * success - callback function
         */
        this.request = function(url, method, params, success, failure){
            var conf_obj = {
                headers: context.defaultHeader,
                url: url,
                method: method,
                params: params//,
                //data: $.param(params) //TODO se i post o context.GET non funzionano qui e' l'errore (params e' per GET, data e' per context.POST)
            };

            //console.log(conf_obj);

            $http(conf_obj).then(success, failure);
        };

        this.sendAction = function(nodeid, action, success) {
            context.request("/node/" + nodeid + "/" + action, context.GET, {}, success, function(){});
        };

    }]);
})(window.angular);
