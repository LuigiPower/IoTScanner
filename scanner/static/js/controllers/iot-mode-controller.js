(function(){
   "use strict";

   var app = angular.module('iot-module');

   app.controller("IotModeWrapperController", ['$scope', 'utility-service', function($scope, utility) {

      console.log($scope.modeData);

      $scope.modes = utility;

      $scope.isUnknown = function()
      {
         var name = $scope.getModeName();
         if((name !== $scope.modes.gpio
               && name !== $scope.modes.composite
               && name !== $scope.modes.empty)
               || name === $scope.modes.unknown)
            return true;
         else return false;
      }

      $scope.getModeName = function()
      {
         return $scope.modeData.name;
      };

      $scope.getParameters = function()
      {
         var parameters = $scope.modeData.params;
         parameters.nodeId = $scope.modeData.nodeId;
         return parameters;
      };

   }]);

   app.controller("IotModeController", ['$scope', 'utility-service', 'ajax-service', function($scope, utility, ajax) {

      console.log($scope.parameters);

      $scope.sendAction = function(action) {
         ajax.sendAction($scope.parameters.nodeId, action, function(data){
            console.log("SUCCESS!")
         });
      };

   }]);

})();
