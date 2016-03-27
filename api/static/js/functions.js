var app = angular.module('main', []);

app.controller('myController', function($scope, apiRepository) {
    
$scope.lol = function() {
    console.log('works');
        //apiRepository.getAll('users').success(function(users) {console.log(users)});
        console.log(apiRepository.getAll('users'));
        };

});


app.factory('apiRepository', function($http) {
  var service = {};
    var host = 'http://localhost:5000/api/v1/';
    service.getAll = getAll;
    service.getById = getById;
    service.create = create;
    service.update = update;
    service.Delete = Delete;

    return service;

    function getAll(endpoint) {
        return $http.get(host+endpoint).then(completed, errorMsg('Error getting all '+endpoint));
    }

    function getById(id) {
        return $http.get(host+ endpoint+'/'+ id).then(completed, errorMsg('Error getting '+endpoint+'by id'));
    }

    function create(endpoint,obj) {
        return $http.post(host+ endpoint, obj).then(completed, errorMsg('Error creating  ' +endpoint));
    }

    function update(endpoint, obj) {
        return $http.put(host+ endpoint+'/' + obj.id, obj).then(completed, errorMsg('Error updating  '+endpoint));
    }

    function Delete(endpoint, id) {
        return $http.delete(host+ endpoint +'/'+ id).then(completed, errorMsg('Error deleting ' +endpoint));
    }


    function completed(res) {
        return res.data;
    }

    function errorMsg(error) {
        return function () {
            return { success: false, message: error };
        };
    }
});

