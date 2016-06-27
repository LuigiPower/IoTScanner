(function(){
    "use strict";

    var app = angular.module('session-module');

    app.controller("SessionController", ['$scope', 'session-service', 'python-service', function($scope, session, python) {

        $scope.isBackstackAvailable = function()
        {
            return session.screenStack.length > 0;
        }

        $scope.title = "I'm a title!";

        $scope.getTitle = function()
        {
            return $scope.title;
        };

        $scope.dataFromPython = python.data;

        $scope.getCurrentScreen = function() {
            return session.screen;
        };

        $scope.goBack = function() {
            session.goBack();
        };

        $scope.isStartScreen = function()
        {
            return session.screen === session.SESSION_START;
        };

        $scope.isMainMenu = function()
        {
            return session.screen === session.MAIN_MENU;
        };

        $scope.isImportFile = function()
        {
            return session.screen === session.IMPORT_FILE;
        };

        $scope.isClockTest = function()
        {
            return session.screen === session.CLOCK_TEST;
        };

        $scope.isAudioRec = function()
        {
            return session.screen === session.AUDIO_REC;
        };
    }]);

})();
