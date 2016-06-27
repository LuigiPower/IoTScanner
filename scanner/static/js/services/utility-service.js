(function(){
   "use strict";

   var app = angular.module("utility-module", []);

   app.service("utility-service", [ "$mdToast", function($mdToast) {
      var context = this;

      this.gpio = "gpio_mode";
      this.composite = "composite_mode";
      this.empty = "empty_mode";
      this.unknown = "unknown_mode";

      this.loadFile = function(mimetype, e, callback) {
         var file = e.target.files[0];
         if(!file)
         {
            return;
         }

         var reader = new FileReader();
         reader.onload = callback;

         if(mimetype == "audio/wav")
         {
            reader.readAsDataURL(file);
         }
         else
         {
            reader.readAsText(file);
         }
      };

      this.showToast = function(message)
      {
         console.log("SHOWING TOAST...");
         $mdToast.show($mdToast.simple()
               .content("sticapperi")
               .textContent(message)
               .position('bottom right')
               .hideDelay(3000));
      };
   }]);

})();
