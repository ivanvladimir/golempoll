var experimentApp = angular.module('experimentApp', ['ngTable']);

experimentApp.controller('ExperimentListCtrl', function ($scope,$filter,$http,ngTableParams) {
  $http.get('/dashboard/experiments.json').success(function(data) {
    $scope.exps = data;
  });

  var data=$scope.exps;

  $scope.tableParams = new ngTableParams({
        page: 1,            // show first page
        count: 10,          // count per page
        sorting: {
            name: 'asc'     // initial sorting
        }
    }, {
        total: data.length, // length of data
        getData: function($defer, params) {
            // use build-in angular filter
            var orderedData = params.sorting() ?
                                $filter('orderBy')(data, params.orderBy()) :
                                data;
            $defer.resolve(orderedData.slice((params.page() - 1) * params.count(), params.page() * params.count()));
        }
    }); 


});
