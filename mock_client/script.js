angular.module('rodanMockApp', [])
    .constant('ROOT', 'http://localhost:8000')
    .run(function ($http, $window, ROOT) {
        delete $window.sessionStorage.token;
        $http.post(ROOT + '/auth/token/', {'username': 'admin', 'password': 'admin'})
            .success(function (data) {
                var token = data['token'];
                $window.sessionStorage.token = token;
                console.log("Token:", token);
            });
    })
    .factory('authInterceptor', function ($window) {
        return {
            'request': function (config) {
                config.headers = config.headers || {};
                if ($window.sessionStorage.token) {
                    config.headers.Authorization = "Token " + $window.sessionStorage.token;
                }
                return config;
            }
        }
    })
    .config(function ($httpProvider) {
        $httpProvider.interceptors.push('authInterceptor');
    })

    .directive('fileModel', ['$parse', function ($parse) {
        return {
            restrict: 'A',
            link: function(scope, element, attrs) {
                var model = $parse(attrs.fileModel);
                var modelSetter = model.assign;

                element.bind('change', function(){
                    scope.$apply(function(){
                        modelSetter(scope, element[0].files[0]);
                    });
                });
            }
        };
    }]) // http://uncorkedstudios.com/blog/multipartformdata-file-upload-with-angularjs

    .controller('projectsCtrl', function ($scope, $http, ROOT, $interval, $rootScope) {
        $interval(function () {
            $http.get(ROOT + '/projects/')
                .success(function (data) {
                    $rootScope.projects = data.results;
                });
        }, 2000);
        $scope.newProject = function () {
            $http.post(ROOT + '/projects/', {'name': $scope.name})
                .success(function () {
                    $scope.name = null;
                });
        };
    })

    .controller('resourcesCtrl', function ($scope, $http, ROOT, $interval, $rootScope) {
        $interval(function () {
            $http.get(ROOT + '/resources/')
                .success(function (data) {
                    $rootScope.resources = data.results;
                });
        }, 2000);
        $scope.newResource = function () {
            var fd = new FormData();
            fd.append('project', $scope.project);
            fd.append('files', $scope.file);
            $http.post(ROOT + '/resources/', fd, {
                transformRequest: angular.identity,
                headers: {'Content-Type': undefined}
            });
        };
    })

    .controller('workflowsCtrl', function ($scope, $http, ROOT, $interval, $rootScope) {
        $interval(function () {
            $http.get(ROOT + '/workflows/')
                .success(function (data) {
                    $rootScope.workflows = data.results;
                });
        }, 2000);
        $scope.newWorkflow = function () {
            $http.post(ROOT + '/workflows/', $scope.fd)
                .success(function () {
                    $scope.fd = {};
                });
        };
    })
