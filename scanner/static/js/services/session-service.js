(function(){
    "use strict";

    var app = angular.module('session-module', ['utility-module']);

    app.service('session-service', [ 'utility-service', function(utility) {
        var context = this;

        this.SESSION_START = "SESSION_START";
        this.MAIN_MENU = "MAIN_MENU";
        this.IMPORT_FILE = "IMPORT_FILE";
        this.CLOCK_TEST = "CLOCK_TEST";
        this.AUDIO_REC = "AUDIO_REC";

        this.screenStack = [ this.SESSION_START ];
        this.listenerList = [];

        this.screen = this.SESSION_START;

        this.patientFiscalCode = "";
        this.isSessionValid = false;

        this.startSession = function(fiscalCode)
        {
            context.patientFiscalCode = fiscalCode;
            context.isSessionValid = true;
        };

        this.checkIfSessionIsValid = function()
        {
            return context.isSessionValid;
        }

        this.goTo = function(screen)
        {
            context.screenStack.push("" + context.screen);
            context.screen = screen;
        };

        this.goBack = function()
        {
            context.screen = context.screenStack.pop();

            for(var i = 0; i < context.listenerList.length; i++)
            {
                var listener = context.listenerList[i];

                if(listener.onBack)
                {
                    listener.onBack();
                }

                if(listener.oneTime)
                {
                    context.listenerList.splice(i, 1);
                }
            }
        };

        this.addListener = function(listener)
        {
            context.listenerList.push(listener);
        }

    }]);

})();
