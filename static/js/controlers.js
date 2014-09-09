var experimentApp = angular.module('experimentApp', ['ngTable','experimentFilters','ngCookies']);

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
            $scope.exps = params.sorting() ?
                                $filter('orderBy')($scope.exps, params.orderBy()) :
                                data;
            $defer.resolve($scopes.exp.slice((params.page() - 1) * params.count(), params.page() * params.count()));
        }
    }); 
	});
});

experimentApp.controller('UserListCtrl', function ($scope,$http,$filter,ngTableParams) {
  $http.get('/dashboard/users.json').success(function(data) {
	var data_=[]
	var d = new Date();
	var n = d.getFullYear(); 
	for (var id in data) {
		data[id].userid=id;
		data[id].age=n-data[id].birthday
		data_.push(data[id]);
	};
    $scope.users = data_;

    $scope.tableParams = new ngTableParams({
        page: 1,            // show first page
        count: 10,          // count per page
        sorting: {
            name: 'asc'     // initial sorting
        }
    }, {
        total: $scope.users.length, // length of data
        getData: function($defer, params) {
            // use build-in angular filter
            $scope.users = params.sorting() ?
                                $filter('orderBy')($scope.users, params.orderBy()) :
                                data;
            $defer.resolve($scope.users.slice((params.page() - 1) * params.count(), params.page() * params.count()));
        }
    }); 
	});
});

experimentApp.controller('CookieController', ['$scope','$cookies', function($scope,$cookies) {
		 $scope.project = $cookies.project;
		 $scope.project_name = $cookies.project_name;
	}]);



