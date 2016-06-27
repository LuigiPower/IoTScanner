(function(){
    "use strict";

    var app = angular.module("iot-module");

    app.directive("iotNode", function() {
        return {
            controller: "IotNodeController",
            templateUrl: "/static/angular-templates/iot-node-template.html",
            restrict: "E",
            scope: {
                nodeData: "=node"
            }
        };
    });
})();
