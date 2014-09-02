var experimentApp = angular.module('experimentApp', ['ngTable','experimentFilters']);

experimentApp.controller('ExperimentListCtrl', function ($scope,$http,$filter,ngTableParams) {
  $http.get('/dashboard/experiments.json').success(function(data) {
	var data_ = [];
	for (var expid in data) {
		data[expid].date_creation_=(new Date(data[expid].date_creation*1000)).toDateString();
		data[expid].date_modification_=(new Date(data[expid].date_modification*1000)).toDateString();
		data[expid].expid=expid;
		data_.push(data[expid]);
	};
    $scope.exps = data_;

    $scope.tableParams = new ngTableParams({
        page: 1,            // show first page
        count: 10,          // count per page
        sorting: {
            name: 'asc'     // initial sorting
        }
    }, {
        total: $scope.exps.length, // length of data
        getData: function($defer, params) {
            // use build-in angular filter
            var orderedData = params.sorting() ?
                                $filter('orderBy')($scope.exps, params.orderBy()) :
                                data;
            $defer.resolve(orderedData.slice((params.page() - 1) * params.count(), params.page() * params.count()));
        }
    }); 
});


});
