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

expFilters.filter('cookie_project', function() {
	  return function(input) {
		      return input ? input : "Sin experimento";
	  };
});

expFilters.filter('active_experiment', function() {
	  return function(input) {
		      return input ? input : "- - -";
	  };
});
