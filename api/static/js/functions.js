var app = angular.module('main', ['ngRoute']);

app.controller('myController', function($scope, apiRepository) {
    
$scope.lol = function() {
    console.log('works');
        //apiRepository.getAll('users').success(function(users) {console.log(users)});
        console.log(apiRepository.getAll('users'));
        };


$scope.submit = function() {
    console.log($scope)
    if ($scope.text) {
        $scope.list.push(this.text);
          scope.text = '';
        }
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
    service.authenticateUser = authenticateUser;

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

    function authenticateUser(provider, email, password) {
        return $http.post(host+provider+'/login', {'email' : email, 'password': password}).then(completed, errorMsg('Invalid credentials provided'));
    }
   

 });
   // configure our routes
    app.config(function($locationProvider, $routeProvider) {
        $locationProvider.html5Mode(true);
        $routeProvider

            // route for the login page
            .when('/', {
                templateUrl : 'template/login.html',
                controller  : 'loginController'
            })

            // route for the all users page
            .when('/users', {
                templateUrl : 'template/users.html',
                controller  : 'userController'
            })

            // route for the user by id page
            .when('/users/:id', {
                templateUrl : 'template/usersid.html',
                controller  : 'userControllerId'
            })

            // route for the all requests page
            .when('/requests', {
                templateUrl : 'template/requests.html',
                controller  : 'requestsController'
            })

            // route for the request by id page
            .when('/requests/:id', {
                templateUrl : 'template/requestsid.html',
                controller  : 'requestsControllerId'
            })

             // route for the all proposals page
            .when('/proposals', {
                templateUrl : 'template/proposals.html',
                controller  : 'proposalsController'
            })

              // route for the proposals page
            .when('/proposals/:id', {
                templateUrl : 'template/proposalsid.html',
                controller  : 'proposalsControllerId'
            })

             // route for the all dates page
            .when('/dates', {
                templateUrl : 'template/dates.html',
                controller  : 'datesController'
            })

              // route for the dates by id page
            .when('/dates:id', {
                templateUrl : 'template/datesid.html',
                controller  : 'datesControllerId'
            })
       
       
    });

    // create the controller and inject Angular's $scope
    app.controller('loginController', function($scope) {
        //if user is logged in drecect to main menu

    });

    app.controller('userController', function($scope) {
        $scope=apiRepository.getAll('users');
    });

     app.controller('userControllerId', function($scope) {
        
    });

    app.controller('requestsController', function($scope) {
        
    });
    
    app.controller('requestsControllerId', function($scope) {
        
    });

    app.controller('proposalsController', function($scope) {
        
    });

    app.controller('proposalsControllerId', function($scope) {
        
    });


    app.controller('datesController', function($scope) {
        
    });
     
    app.controller('datesIdController', function($scope) {
        
    });