(function(){
    "use strict";

    var app = angular.module("iot-module");

    app.directive("modeWrapper", function() {
        return {
            controller: "IotModeWrapperController",
            templateUrl: "/static/angular-templates/mode-wrapper-template.html",
            restrict: "E",
            scope: {
                modeData: "=mode"
            }
        };
    });

    app.directive("gpioMode", function() {
        return {
            controller: "IotModeController",
            templateUrl: "/static/angular-templates/gpio-mode-template.html",
            restrict: "E",
            scope: {
                parameters: "=parameters"
            }
        };
    });

    app.directive("compositeMode", function() {
        return {
            controller: "IotModeController",
            templateUrl: "/static/angular-templates/composite-mode-template.html",
            restrict: "E",
            scope: {
                parameters: "=parameters"
            }
        };
    });

    app.directive("emptyMode", function() {
        return {
            controller: "IotModeController",
            templateUrl: "/static/angular-templates/empty-mode-template.html",
            restrict: "E",
            scope: {
                parameters: "=parameters"
            }
        };
    });

    app.directive("unknownMode", function() {
        return {
            controller: "IotNodeController",
            templateUrl: "/static/angular-templates/unknown-mode-template.html",
            restrict: "E",
            scope: {
                parameters: "=parameters"
            }
        };
    });
})();
