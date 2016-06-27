(function(){
   "use strict";

   var app = angular.module('iot-module', ['utility-module', 'ajax-module']);

   app.controller("IotNodeController", ['$scope', 'utility-service', function($scope, utility) {

      console.log($scope.nodeData);

      $scope.getNodeName = function()
      {
         return $scope.nodeData.name;
      };

      $scope.getNodeIP = function()
      {
         return $scope.nodeData.ip;
      };

      $scope.getMode = function()
      {
         var modeData = $scope.nodeData.mode;
         modeData.nodeId = $scope.nodeData.name;
         return modeData;
      };

   }]);

})();
