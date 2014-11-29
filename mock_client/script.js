angular.module('rodanMockApp', [])
    .constant('ROOT', 'http://localhost:8000')
    .constant('UPDATE_FREQ', 2000)
    .run(function ($http, $window, ROOT, $rootScope, getAllPages) {
        delete $window.sessionStorage.token;
        $http.post(ROOT + '/auth/token/', {'username': 'admin', 'password': 'admin'})
            .success(function (data) {
                var token = data['token'];
                $window.sessionStorage.token = token;
                console.log("Token:", token);

                getAllPages(ROOT + '/jobs/')
                    .then(function (results) {
                        $rootScope.jobs = results;
                    }, function (err) {
                        console.log(err);
                    });
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
    .factory('getAllPages', function ($http, $q) {
        return function (url) {
            var results = [];
            var deferred = $q.defer();
            function getPage (url) {
                $http.get(url)
                    .success(function (data) {
                        results = results.concat(data.results);
                        if (data.next) {
                            getPage(data.next);
                        } else {
                            deferred.resolve(results);
                        }
                    }).error(function (err) {
                        deferred.reject(err);
                    });
            };
            getPage(url);
            return deferred.promise;
        };
    })
    .factory('intervalNow', function ($interval) {
        return function (fn, args) {
            $interval.apply(null, arguments);
            fn();
        };
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

    .controller('projectsCtrl', function ($scope, $http, ROOT, intervalNow, $rootScope, getAllPages, UPDATE_FREQ) {
        intervalNow(function () {
            getAllPages(ROOT + '/projects/')
                .then(function (results) {
                    $rootScope.projects = results;
                }, function (err) {
                    console.log(err);
                });
        }, UPDATE_FREQ);
        $scope.newProject = function () {
            $http.post(ROOT + '/projects/', {'name': $scope.name})
                .success(function () {
                    $scope.name = null;
                });
        };
    })

    .controller('resourcesCtrl', function ($scope, $http, ROOT, intervalNow, $rootScope, getAllPages, UPDATE_FREQ) {
        intervalNow(function () {
            getAllPages(ROOT + '/resources/')
                .then(function (results) {
                    $rootScope.resources = results;
                }, function (err) {
                    console.log(err);
                });
        }, UPDATE_FREQ);
        $scope.newResource = function () {
            var fd = new FormData();
            fd.append('project', $scope.project);
            fd.append('files', $scope.file);
            $http.post(ROOT + '/resources/', fd, {
                transformRequest: angular.identity,
                headers: {'Content-Type': undefined}
            });
        };
        $scope.deleteResource = function (r) {
            $http.delete(r.url)
                .error(function (error) {
                    console.log(error);
                });
        };
    })

    .controller('workflowsCtrl', function ($scope, $http, ROOT, intervalNow, $rootScope, $q, getAllPages, UPDATE_FREQ) {
        intervalNow(function () {
            getAllPages(ROOT + '/workflows/')
                .then(function (results) {
                    $rootScope.workflows = results;
                }, function (err) {
                    console.log(err);
                });
        }, UPDATE_FREQ);

        function errhandler (error, status, headers, config) {
            console.log(error, config.url);
        };
        $scope.newToGreyscaleWorkflow = function () {
            $http.post(ROOT + '/workflows/', {'project': $scope.project, 'name': $scope.name_greyscale}).success(function (wf) {
                var job_greyscale = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.plugins.image_conversion.to_greyscale'});
                $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job_type': 0, 'job': job_greyscale.url}).success(function (wfjob) {
                    $q.all([
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfjob.url, 'input_port_type': job_greyscale.input_port_types[0].url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wfjob.url, 'output_port_type': job_greyscale.output_port_types[0].url})
                    ]).then(function (things) {
                        var ip = things[0].data;
                        var op = things[1].data;
                        $http.post(ROOT + '/resourceassignments/', {'input_port': ip.url, 'resources': $scope.resources_greyscale})
                            .success(function (ra) {
                                console.log('to_greyscale workflow created!');
                            }).error(errhandler);
                    }, errhandler);
                }).error(errhandler);
            }).error(errhandler);
        };
        $scope.newRotateCropWorkflow = function () {
            $http.post(ROOT + '/workflows/', {'project': $scope.project, 'name': $scope.name_rotatecrop}).success(function (wf) {
                var jrm = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.toolkits.rodan_plugins.plugins.rdn_rotate.rdn_rotate_manual'});
                var jra = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.toolkits.rodan_plugins.plugins.rdn_rotate.rdn_rotate_apply_rotate'});

                var jcm = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.toolkits.rodan_plugins.plugins.rdn_crop.rdn_crop_manual'});
                var jca = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.toolkits.rodan_plugins.plugins.rdn_crop.rdn_crop_apply_crop'});

                $q.all([
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job_type': 0, 'job': jrm.url}),
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job_type': 0, 'job': jra.url}),
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job_type': 0, 'job': jcm.url}),
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job_type': 0, 'job': jca.url})
                ]).then(function (things) {
                    var wfjrm = things[0].data;
                    var wfjra = things[1].data;
                    var wfjcm = things[2].data;
                    var wfjca = things[3].data;

                    $q.all([
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfjrm.url, 'input_port_type': jrm.input_port_types[0].url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wfjrm.url, 'output_port_type': jrm.output_port_types[0].url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfjra.url, 'input_port_type': jra.input_port_types[0].url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfjra.url, 'input_port_type': jra.input_port_types[1].url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wfjra.url, 'output_port_type': jra.output_port_types[0].url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfjcm.url, 'input_port_type': jcm.input_port_types[0].url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wfjcm.url, 'output_port_type': jcm.output_port_types[0].url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfjca.url, 'input_port_type': jca.input_port_types[0].url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfjca.url, 'input_port_type': jca.input_port_types[1].url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wfjca.url, 'output_port_type': jca.output_port_types[0].url})
                    ]).then(function (things) {
                        var iprm = things[0].data;
                        var oprm = things[1].data;
                        var ipra_img = things[2].data;
                        var ipra_arg = things[3].data;
                        var opra = things[4].data;
                        var ipcm = things[5].data;
                        var opcm = things[6].data;
                        var ipca_img = things[7].data;
                        var ipca_arg = things[8].data;
                        var opca = things[9].data;

                        $q.all([
                            $http.post(ROOT + '/resourceassignments/', {'input_port': iprm.url, 'resources': $scope.resources_rotatecrop}),
                            $http.post(ROOT + '/resourceassignments/', {'input_port': ipra_img.url, 'resources': $scope.resources_rotatecrop}),
                            $http.post(ROOT + '/connections/', {'output_port': oprm.url, 'input_port': ipra_arg.url}),
                            $http.post(ROOT + '/connections/', {'output_port': opra.url, 'input_port': ipcm.url}),
                            $http.post(ROOT + '/connections/', {'output_port': opra.url, 'input_port': ipca_img.url}),
                            $http.post(ROOT + '/connections/', {'output_port': opcm.url, 'input_port': ipca_arg.url})
                        ]).then(function (things) {
                            console.log('rotate-crop workflow created!');
                        }, errhandler);
                    }, errhandler);
                }, errhandler);
            });
        };

        $scope.validateWorkflow = function (w) {
            $http.patch(w.url, {'valid': true})
                .error(function (error) {
                    console.log(error);
                });
        };
        $scope.deleteWorkflow = function (w) {
            $http.delete(w.url)
                .error(function (error) {
                    console.log(error);
                });
        };
        $scope.runWorkflow = function (w) {
            $http.post(ROOT + '/workflowruns/', {'workflow': w.url})
                .error(function (error) {
                    console.log(error);
                });
        };
    })

    .controller('workflowrunsCtrl', function ($scope, $http, ROOT, $rootScope, intervalNow, getAllPages, UPDATE_FREQ) {
        intervalNow(function () {
            getAllPages(ROOT + '/workflowruns/')
                .then(function (results) {
                    $rootScope.workflowruns = results;
                }, function (err) {
                    console.log(err);
                });
        }, UPDATE_FREQ);
        intervalNow(function () {
            getAllPages(ROOT + '/runjobs/')
                .then(function (results) {
                    $rootScope.runjobs = [];
                    angular.forEach(results, function (rj) {
                        $rootScope.runjobs[rj.workflow_run] = $rootScope.runjobs[rj.workflow_run] || [];
                        var job = _.find($rootScope.jobs, function (j) { return j.url == rj.job});
                        rj.job_name = job.job_name;
                        $rootScope.runjobs[rj.workflow_run].push(rj);
                    });
                }, function (err) {
                    console.log(err);
                });
        }, UPDATE_FREQ);

        $scope.status = {
            '0': 'Not running',
            '1': 'Running',
            '4': 'Has finished',
            '-1': 'Failed',
            '9': 'Cancelled'
        };
    })
