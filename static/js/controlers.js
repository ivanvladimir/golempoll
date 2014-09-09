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
		data[id].age=n-data[id].birthday;
		if (typeof data[id].experiments != 'undefined'){
			data[id].experiment=data[id].experiments[0]
		}
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


experimentApp.controller('GolemPollController', function ($scope, $cookies, golemPollService) {
	$scope.poll = {};
	golemPollService.getData('poll', $cookies.running_exp).then(function (data) {
		$scope.poll = data;
		var questions=[];
		var options=[];
        var option=0;
		for (var tmp_ in data.media.files) {
			questions.push(option);
			option+=1;
		};
        option=0;
		for (var tmp_ in data.options.labels) {
			options.push(option);
			option+=1;
		};
		$scope.questions=shuffle(questions);
		$scope.options=shuffle(options);
		$scope.current=0;
		$scope.mainImage=$scope.poll.media.files[$scope.questions[$scope.current]];

	},
	function (error) {
	}
	);
 
	$scope.save = function () {
		if ($scope.poll.option) {
			golemPollService.postData($routeParams.id, {option: $scope.poll.option}).then(function (data) {
			},
			function (error) {
			});
		} else {
		}
	};

	$scope.next = function(chosen) {
		var ans=$scope.poll.options.keys[chosen];
		var opt=$scope.poll.media.keys[$scope.questions[$scope.current]];
		golemPollService.postData($cookies.running_exp, {emotion: opt, answer: ans}).then(function (data) {
			},
			function (error) {
			});

		$scope.current+=1;
		$scope.mainImage=$scope.poll.media.files[$scope.questions[$scope.current]];
		$scope.options=shuffle($scope.options);
	};
 
});

function shuffle(o){ //v1.0
    for(var j, x, i = o.length; i; j = Math.floor(Math.random() * i), x = o[--i], o[i] = o[j], o[j] = x);
    return o;
};
