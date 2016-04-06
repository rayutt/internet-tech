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
    service.Logout = Logout;
    return service;

    function getAll(endpoint) {
        return $http.get(host+endpoint).then(completed, errorMsg('Error getting all '+endpoint));
    }

    function getById(endpoint, id) {
        return $http.get(host+ endpoint+'/'+ id).then(completed, errorMsg('Error getting '+endpoint+' by id'));
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
   
    function Logout(provider) {
        return $http.post(host+provider+'/logout').then(completed, errorMsg('Error logging out'));
    }

 });


   // configure the routes
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

            // route for the create request page
            .when('/createrequest', {
                templateUrl : 'template/createrequest.html',
                controller  : 'createRequestController'
            })

              // route for the edit request page
            .when('/editrequest/:id', {
                templateUrl : 'template/editrequest.html',
                controller  : 'editRequestController'
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

             .when('/createproposal', {
                templateUrl : 'template/createproposal.html',
                controller  : 'createProposalsController'
            })

             // route for the all dates page
            .when('/dates', {
                templateUrl : 'template/dates.html',
                controller  : 'datesController'
            })

             // route for the all dates page
            .when('/creatdates', {
                templateUrl : 'template/createdate.html',
                controller  : 'createDatesController'
            })

              // route for the dates by id page
            .when('/dates/:id', {
                templateUrl : 'template/datesid.html',
                controller  : 'datesControllerId'
            })
       
            // route for the main menu
            .when('/mainmenu', {
                templateUrl : 'template/mainmenu.html',
                controller  : 'mainMenuController'
            })
            // route for the edit user
            .when('/edit/:id', {
                templateUrl : 'template/edit.html',
                controller  : 'editController'
            })

             // route for the edit date
            .when('/editdate/:id', {
                templateUrl : 'template/editdate.html',
                controller  : 'editDateController'
            })

              // route for the register user
            .when('/register', {
                templateUrl : 'template/register.html',
                controller  : 'registerController'
            })

            // route for the edit date
            .when('/logout', {
                templateUrl : 'template/logout.html',
                controller  : 'logoutController'
            })

             // route for the edit date
            .when('/gmail', {
                templateUrl : 'template/gmail.html',
                controller  : 'gmailController'
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
                    $window.location.href = '#/mainmenu';
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
                if(response && response.success != false){
                    //console.log(response.users);
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
                if(response && response.success != false){
                    $scope.user = response;
                    console.log(response);
                }
                else {
                    //prints api error
                    console.log('Error connecting to api');

                }
            }, function (error) {
            //print error message if cant connect to api
            console.log(error)
        });;   
    });

    app.controller('requestsController', function($scope, apiRepository) {
        apiRepository.getAll('requests').then(function (response) {
            //prints api response
                if(response && response.success != false){
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

         // create the user and inject Angular's $scope
    app.controller('registerController', function($scope, apiRepository) {
        
        $scope.submit = function() {
        console.log($scope.user);
        apiRepository.create('users',$scope.user).then(function (response) {
            //prints api response
                if(response && response.success != false){
                    
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
     // create the controller and inject Angular's $scope
    app.controller('createRequestController', function($scope, apiRepository) {
        
        $scope.submit = function() {
        console.log($scope.request);
        apiRepository.create('requests',$scope.request).then(function (response) {
            //prints api response
                if(response && response.success != false){
                    //moment("Thu, 17 Mar 2016 01:06:01 GMT", "ddd, DD MMM YYYY HH:mm:ss").format("YYYY-MM-DD HH:mm:ss");
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

     // create the controller and inject Angular's $scope
    app.controller('editRequestController', function($scope, apiRepository, $routeParams) {
        
        apiRepository.getById('requests',$routeParams.id).then(function (response) {
                    
                    //prints api response
                        if(response && response.success != false){
                            $scope.request = response;
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


    $scope.Delete = function() {
        console.log('delete');
        apiRepository.Delete('requests',$routeParams.id).then(function (response) {
            console.log('delete');
                if(response && response.success != false){
                    
                }
                else {
                    //prints api login error
                    
                }
            }, function (error) {
            //print error message if cant connect to api
            console.log(error)
        });;
    };

     $scope.submit = function() {
        console.log('before requeswt')
        console.log($scope.request);
        //$scope.request.meal_time=moment($scope.request.meal_time, "ddd, DD MMM YYYY HH:mm:ss").format("YYYY-MM-DD HH:mm:ss");
        apiRepository.update('requests',$scope.request).then(function (response) {
            //prints api response
                if(response && response.success != false){
                    alert('success');
                }
                else {
                    //prints api login error
                    alert('fail');
                }
            }, function (error) {
            //print error message if cant connect to api
            console.log(error)
        });;
    };

    });
    
    app.controller('requestsControllerId', function($scope, apiRepository, $routeParams) {
        apiRepository.getById('requests',$scope.user).then(function (response) {
            
            //prints api response
                if(response && response.success != false){
                    $scope.requests = response;
                    //console.log(response);
                }
                else {
                    //prints api error
                    console.log('Error connect to api');

                }
            }, function (error) {
            //print error message if cant connect to api
            console.log(error)
        });;

         $scope.createProposal = function() {
                console.log('proposals');
                var proposal ={
                                "user_proposed_to":$scope.requests.user_id,
                                "request_id":$scope.requests.id
                            }
                
                apiRepository.create('proposals', proposal).then(function (response) {
                    console.log('proposals');
                        if(response && response.success != false){
                            alert('success proposal created');
                        }
                        else {
                            //prints api login error
                            alert('fail');
                        }
                    }, function (error) {
                    //print error message if cant connect to api
                    console.log(error)
                });;
            };

    });

    app.controller('proposalsController', function($scope, apiRepository) {
        apiRepository.getAll('proposals').then(function (response) {
            //prints api response
                if(response && response.success != false){
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
                if(response && response.success != false){
                    $scope.proposals = response;
                    $scope.getRequest();
                    console.log(response);
                }
                else {
                    //prints api error
                    console.log('Error connecting to api');

                }
            }, function (error) {
            //print error message if cant connect to api
            console.log(error)
        });;

             $scope.getRequest = function() {
                console.log('request');
            
                apiRepository.getById('requests', $scope.proposals.request_id).then(function (response) {
                    console.log('request');
                        if(response && response.success != false){
                            $scope.requests = response;
                            console.log(response);
                        }
                        else {
                            //prints api login error
                            alert('fail');
                        }
                    }, function (error) {
                    //print error message if cant connect to api
                    console.log(error)
                });;
            };

    $scope.Delete = function() {
        console.log('delete');
        apiRepository.Delete('proposals',$routeParams.id).then(function (response) {
            console.log('delete');
                if(response && response.success != false){
                    alert('success proposal deleted');
                }
                else {
                    //prints api login error
                    alert('fail');
                }
            }, function (error) {
            //print error message if cant connect to api
            console.log(error)
        });;
    };

    $scope.accept = function() {
                console.log('dates');
                var MealDate ={
                                "user_1":$scope.proposals.user_proposed_to,
                                "request_id":$scope.requests.id,
                                "meal_time": $scope.requests.meal_time
                            }
                
                apiRepository.create('dates', MealDate).then(function (response) {
                    console.log('proposals');
                        if(response){
                            alert('success meal date created');
                        }
                        else {
                            //prints api login error
                            alert('fail');
                        }
                    }, function (error) {
                    //print error message if cant connect to api
                    console.log(error)
                });;
            };

    });


    app.controller('datesController', function($scope, apiRepository) {
        apiRepository.getAll('dates').then(function (response) {
            //prints api response
                if(response && response.success != false){
                    console.log(response);
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
     
    app.controller('datesControllerId', function($scope, apiRepository, $routeParams) {
        apiRepository.getById('dates', $routeParams.id).then(function (response) {
            
            //prints api response
                if(response && response.success != false){
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

        $scope.Delete = function() {
        console.log('delete');
        apiRepository.Delete('dates',$routeParams.id).then(function (response) {
            console.log('delete');
                if(response && response.success != false){
                    alert('success date deleted');
                }
                else {
                    //prints api login error
                    alert('fail');
                }
            }, function (error) {
            //print error message if cant connect to api
            console.log(error)
        });;
    };

    });

    

    app.controller('editDateController', function($scope, apiRepository, $routeParams) {
        
        apiRepository.getById('dates', $routeParams.id).then(function (response) {
            
            //prints api response
                if(response && response.success != false){
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

    app.controller('editController', function($scope, apiRepository, $routeParams) {
         apiRepository.getById('users', $routeParams.id).then(function (response) {
                    
                    //prints api response
                        if(response && response.success != false){
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

   $scope.submit = function() {
        console.log($scope.user);
        apiRepository.update('users',$scope.user).then(function (response) {
            //prints api response
                if(response && response.success != false){
                    console.log(response);
                }
                else {
                    console.log('error');
                    document.getElementById("msg").innerHTML = 'error';
                    
                }
            }, function (error) {
            //print error message if cant connect to api
            console.log(error);
        });;
    };

    $scope.Delete = function() {
        console.log('delete');
        apiRepository.Delete('users',$scope.user.id).then(function (response) {
            console.log('delete');
                if(response && response.success != false){
                    
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
    
    app.controller('logoutController', function($scope, apiRepository, $window) {
         apiRepository.Logout('app').then(function (response) {
            
                if(response && response.success != false){
                    console.log('logged out');
                    $window.sessionStorage.accessToken = null;
                }
                else {
                    //prints api login error
                    
                }
            }, function (error) {
            //print error message if cant connect to api
            console.log(error)
        });;
    });

    app.controller('gmailController', function($scope, apiRepository) {
        
    });

    app.controller('mainMenuController', function($scope, apiRepository) {
        
    });

    app.factory('tokenInterceptor', function ($location, $q, $window, $rootScope) {
 return {
 request: function (config) {
  config.headers['Authorization'] = $window.sessionStorage.accessToken;
  return config;
 },
 'requestError': function(rejection) {
  console.log(rejection)
  if (canRecover(rejection)) {
   return responseOrNewPromise
  }
  return $q.reject(rejection);
 },
 'response': function(response) {
  if(response && response.data.error){
   if(response.data.redirect){
    $location.path(response.data.redirect);
   }
   console.log(response.data.error)
   $rootScope.errorMsg = response.data.error;
  }
  return response;
 },
 'responseError': function(rejection) {
  console.log(rejection)
  if (canRecover(rejection)) {
   return responseOrNewPromise
  }
  return $q.reject(rejection);
 }
 };
});



  

