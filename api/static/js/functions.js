var app = angular.module('main', ['ngRoute']);


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

    function getById(endpoint, id) {
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

    function authenticateUser(provider, userObj) {
        return $http.post(host+provider+'/login', userObj).then(completed, errorMsg('Invalid credentials provided'));
    }
   

 });
   // configure our routes
    app.config(function($locationProvider, $routeProvider, $httpProvider) {
        
        $httpProvider.interceptors.push('tokenInterceptor');

        //$locationProvider.html5Mode(true);
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
            .when('/usersid/:id', {
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
       
            // route for the main menu
            .when('/mainmenu', {
                templateUrl : 'template/mainmenu.html',
                controller  : 'mainMenuController'
            })
            // route for the edit
            .when('/edit', {
                templateUrl : 'template/edit.html',
                controller  : 'editController'
            })

    });


  
    // create the controller and inject Angular's $scope
    app.controller('loginController', function($scope, apiRepository, $window) {
        //if user is logged in drecect to main menu
        $scope.submit = function() {
        
        // testing code
        //console.log(apiRepository.authenticateUser('app',$scope.vm));

        apiRepository.authenticateUser('app',$scope.vm).then(function (response) {
            //prints api response
                if(response && response.token){
                    //stores the token
                    $window.sessionStorage.accessToken = response.token;
                    //redirects to a main menu after successful login
                    $window.location.href = '#/mainMenu';
                }
                else {
                    //prints api login error

                }
            }, function (error) {
            //print error message if cant connect to api
            console.log(error)
        });;
        
      };
    });

    app.controller('userController', function($scope, apiRepository) {
        
        apiRepository.getAll('users').then(function (response) {
            //prints api response
                if(response){
                    console.log(response.users);
                    $scope.users = response.users;
                }
                else {
                    //prints api error

                }
            }, function (error) {
            //print error message if cant connect to api
            console.log(error)
        });;
        
        console.log($scope);
    });

    app.controller('userControllerId', function($scope, apiRepository, $routeParams) {

        apiRepository.getById('users',$routeParams.id).then(function (response) {
            
            //prints api response
                if(response){
                    $scope.user = response;
                    console.log(response);
                }
                else {
                    //prints api error
                    console.log('Error connect to api');

                }
            }, function (error) {
            //print error message if cant connect to api
            console.log(error)
        });;   

    });

    app.controller('requestsController', function($scope, apiRepository) {
        apiRepository.getAll('requests').then(function (response) {
            //prints api response
                if(response){
                    $scope.requests = response.requests;
                }
                else {
                    //prints api error

                }
            }, function (error) {
            //print error message if cant connect to api
            console.log(error)
        });;
        
    });
    
    app.controller('requestsControllerId', function($scope, apiRepository, $routeParams) {
        apiRepository.getById('requests',$routeParams.id).then(function (response) {
            
            //prints api response
                if(response){
                    $scope.requests = response;
                    console.log(response);
                }
                else {
                    //prints api error
                    console.log('Error connect to api');

                }
            }, function (error) {
            //print error message if cant connect to api
            console.log(error)
        });;
    });

    app.controller('proposalsController', function($scope, apiRepository) {
        apiRepository.getAll('proposals').then(function (response) {
            //prints api response
                if(response){
                    $scope.proposals = response.proposals;  
                }
                else {
                    //prints api error

                }
            }, function (error) {
            //print error message if cant connect to api
            console.log(error)
        });;
        
    });

    app.controller('proposalsControllerId', function($scope, apiRepository, $routeParams) {
        apiRepository.getById('proposals',$routeParams.id).then(function (response) {
            
            //prints api response
                if(response){
                    $scope.proposals = response;
                    console.log(response);
                }
                else {
                    //prints api error
                    console.log('Error connect to api');

                }
            }, function (error) {
            //print error message if cant connect to api
            console.log(error)
        });;
    });


    app.controller('datesController', function($scope, apiRepository) {
        apiRepository.getAll('dates').then(function (response) {
            //prints api response
                if(response){
                    $scope.dates = response.dates;
                }
                else {
                    //prints api error

                }
            }, function (error) {
            //print error message if cant connect to api
            console.log(error)
        });;
        
    });
     
    app.controller('datesIdController', function($scope, apiRepository, $routeParams) {
        apiRepository.getById('users',$routeParams.id).then(function (response) {
            
            //prints api response
                if(response){
                    $scope.dates = response;
                    console.log(response);
                }
                else {
                    //prints api error
                    console.log('Error connect to api');
                }
            }, function (error) {
            //print error message if cant connect to api
            console.log(error)
        });;
    });

    app.controller('editController', function($scope, apiRepository) {
        
    });


    app.controller('mainMenuController', function($scope, apiRepository) {
        
    });
    //stores the token in an intercept fucntion
    app.factory('tokenInterceptor', function ($window) {
        return {
         request: function (config) {
         config.headers['Authorization'] = $window.sessionStorage.accessToken;

            return config;
    }
  };
});

