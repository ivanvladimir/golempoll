var experimentApp = angular.module('experimentApp', ['ngTable','experimentFilters','ngCookies']);

experimentApp.controller('ExperimentUserListCtrl', function ($scope,$http,$filter,$attrs,ngTableParams) {
    $http.get('/api/user/'+$attrs.userid).success(function(data) {
    $scope.exps = data.experiments;

    $scope.tableParams = new ngTableParams({
        page: 1,            // show first page
        count: 10,          // count per page
        sorting: {
            name: 'asc'     // initial sorting
        }
    }, {
        total: $scope.exps.length, // length of data
        getData: function($defer, params) {
            $scope.exps = params.sorting() ?
                                $filter('orderBy')($scope.exps, params.orderBy()) :
                                data;
            $defer.resolve($scopes.exp.slice((params.page() - 1) * params.count(), params.page() * params.count()));
        }
    }); 
	});
});

experimentApp.controller('UserExperimentListCtrl', function ($scope,$http,$filter,$attrs,ngTableParams) {
    $http.get('/api/experiment/'+$attrs.expid).success(function(data) {
    $scope.users = data.users;
	var d = new Date();
	$scope.current_year = d.getFullYear();


    $scope.tableParams = new ngTableParams({
        page: 1,            // show first page
        count: 10,          // count per page
        sorting: {
            name: 'asc'     // initial sorting
        }
    }, {
        total: $scope.exps.length, // length of data
        getData: function($defer, params) {
            $scope.exps = params.sorting() ?
                                $filter('orderBy')($scope.exps, params.orderBy()) :
                                data;
            $defer.resolve($scopes.exp.slice((params.page() - 1) * params.count(), params.page() * params.count()));
        }
    }); 
	});
});



experimentApp.controller('ExperimentListCtrl', function ($scope,$http,$filter,ngTableParams) {
  $http.get('/api/experiment').success(function(data) {
    $scope.exps = data.objects;

    $scope.tableParams = new ngTableParams({
        page: 1,            // show first page
        count: 10,          // count per page
        sorting: {
            name: 'asc'     // initial sorting
        }
    }, {
        total: $scope.exps.length, // length of data
        getData: function($defer, params) {
            $scope.exps = params.sorting() ?
                                $filter('orderBy')($scope.exps, params.orderBy()) :
                                data;
            $defer.resolve($scopes.exp.slice((params.page() - 1) * params.count(), params.page() * params.count()));
        }
    }); 
	});
});

experimentApp.controller('UserListCtrl', function ($scope,$http,$filter,ngTableParams) {
  $http.get('/api/user').success(function(data) {
	var d = new Date();
    $scope.users = data.objects;
	$scope.current_year = d.getFullYear();

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


experimentApp.controller('GolemPollController', function ($scope, $http, $window, $cookies) {
     $http.get('/api/definition/'+$cookies.running_exp).success(function(data) {
		$scope.poll = data;
		var questions=[];
		var options=[];
        var option=0;
		for (var tmp_ in data.media.files) {
			questions.push(option);
			option+=1;
		};
		option=0;
		for (var tmp_ in data.media.keys) {
			options.push(option);
			option+=1;
		};
		$scope.questions=shuffle(questions);
		$scope.options=shuffle(options);
		$scope.current=0;
		$scope.mainImage=$scope.poll.media.files[$scope.questions[$scope.current]];
		$scope.start_time=new Date();
		$scope.answers=[];

	},
	function (error) {
	}
	);
 
	$scope.next = function(chosen) {
		if($scope.poll.media.control=="random"){
			var ans=$scope.poll.options.keys[chosen];
		}else{
			var ans=chosen;
			$scope.option="";
		}
		var opt=$scope.poll.media.keys[$scope.questions[$scope.current]];
		var delta_time=new Date()-$scope.start_time;
		var info={'emotion': opt, 'answer': ans, 'delta': delta_time};
		$scope.answers.push(info);
		$scope.current+=1;
		if($scope.current>=$scope.poll.media.files.length){
			if($cookies.running_user!=undefined){
			 	$http.put('/api/definition/'+$cookies.running_exp+'/'+$cookies.running_user,{answers:$scope.answers});
			 	$window.location='/finish';
			 }else{
			 	$window.location='/dashboard/result/'+angular.toJson($scope.answers);
			}
		}else{
			$scope.options=shuffle($scope.options);
			$scope.mainImage=$scope.poll.media.files[$scope.questions[$scope.current]];
			$scope.start_time=new Date();
		}
	};
 
});

function shuffle(o){ //v1.0
    for(var j, x, i = o.length; i; j = Math.floor(Math.random() * i), x = o[--i], o[i] = o[j], o[j] = x);
    return o;
};
