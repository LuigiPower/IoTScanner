(function(){
	"use strict";

	var app = angular.module('iotscanner', [
		'ngMaterial', 'session-module', 'utility-module',
                'python-module', 'iot-module'
	]);

	app.config(function($mdThemingProvider){
		$mdThemingProvider.theme('default')
			.primaryPalette('indigo', {
				'default':'400'
				//'hue-1': '100', // use shade 100 for the <code>md-hue-1</code> class
                //'hue-2': '600' // use shade 600 for the <code>md-hue-2</code> class
			});
	});
})();
