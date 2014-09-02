var expFilters=angular.module('experimentFilters', []);

expFilters.filter('checkmark', function() {
	  return function(input) {
		      return input ? '\u2713' : '\u2718';
	  };
});

expFilters.filter('switch', function() {
	  return function(input) {
		      return input ? "off" : "on";
	  };
});
