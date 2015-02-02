angular.module('rodanTestApp', ['ngRoute', 'ngCookies'])
    .constant('ROOT', '')
    .constant('UPDATE_FREQ', 2000)
    .factory('authInterceptor', function ($window) {
        return {
            'request': function (config) {
                config.headers = config.headers || {};
                if ($window.sessionStorage.getItem('token')) {
                    config.headers.Authorization = "Token " + $window.sessionStorage.getItem('token');
                }
                return config;
            }
        }
    })
    .factory('errlogInterceptor', function ($window, $q) {
        return {
            'responseError': function (rejection) {
                $window['console'].error(rejection);
                /*
                var method = rejection.config.method;
                var url = rejection.config.url;
                var status = rejection.status;
                var data = rejection.data;
                data = (data.toString().length < 150) ? data : '';
                $window['console'].error("Error " + status + " in " + method + ' ' + url + '      ' + data);*/
                return $q.reject(rejection);
            }
        }
    })
    .factory('getAllPages', function ($http, $q) {
        return function (url, config) {
            var results = [];
            var deferred = $q.defer();
            function getPage (url) {
                $http.get(url, config)
                    .success(function (data) {
                        results = results.concat(data.results);
                        if (data.next) {
                            if (config && config.params) {
                                delete config['params'];  // params are contained in the next URL
                            }
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
        $httpProvider.interceptors.push('errlogInterceptor');
    })

    .directive('fileModel', ['$parse', function ($parse) {
        return {
            restrict: 'A',
            link: function(scope, element, attrs) {
                var model = $parse(attrs.fileModel);
                var modelSetter = model.assign;
                element.bind('change', function(){
                    scope.$apply(function(){
                        modelSetter(scope, element[0].files);
                    });
                });
                scope.$watch(attrs.fileModel, function (new_val) {
                    var new_val = new_val || [];
                    if (new_val.length == 0) {
                        // clear the form
                        element[0].form.reset();
                    }
                });
            }
        };
    }]) // http://uncorkedstudios.com/blog/multipartformdata-file-upload-with-angularjs

//////////////////////////////////////////////
    .config(['$routeProvider', '$locationProvider', function ($routeProvider, $locationProvider) {
        $routeProvider
            .when('/login/', {
                templateUrl: '/templates/login.html'
                ,controller: 'ctrl_login'
            })
            .when('/projects/', {
                templateUrl: '/templates/projects.html'
                ,controller: 'ctrl_projects'
            })
            .when('/project/:projectId/', {
                templateUrl: '/templates/project.html'
                ,controller: 'ctrl_project'
            })
            .otherwise({
                redirectTo: '/login/'
            });
        $locationProvider.html5Mode(false);
    }])
    .run(function (getAllPages, ROOT, $rootScope) {
        /* initialization */
        $rootScope.$on('$routeChangeSuccess', function () {
            getAllPages(ROOT + '/jobs/')
                .then(function (results) {
                    $rootScope.jobs = results;
                });
            getAllPages(ROOT + '/resourcetypes/')
                .then(function (results) {
                    $rootScope.resource_types = results;
                    $rootScope.resourcetypes_hash = {};
                    _.each(results, function (rt) {
                        $rootScope.resourcetypes_hash[rt.url] = rt;
                    });
                });
        });
        $rootScope.status = {
            '0': 'Scheduled',
            '1': 'Processing',
            '4': 'Finished',
            '-1': 'Failed',
            '9': 'Cancelled',
            '8': 'Expired',
            '2': 'Waiting for input',
            '11': 'Retrying'
        };
    })
    .controller('ctrl_navbar', function ($scope, $location, $window) {
        $scope.allProjects = function () {
            $location.path('/projects/');
        }
        $scope.logout = function () {
            $window.sessionStorage.removeItem('token');
            $location.path('/login/');
        };
    })
//////////////////
    .controller('ctrl_login', function ($scope, $http, $location, $window, ROOT, $cookies) {
        $scope.submit = function () {
            $window.sessionStorage.removeItem('token');
            $http.post(ROOT + '/auth/token/', $scope.inputs, {headers: {'X-CSRFToken': $cookies.csrftoken}})
                .success(function (data) {
                    var token = data['token'];
                    $window.sessionStorage.setItem('token', token);
                    $location.path('/projects/');
                });
        };
    })
    .controller('ctrl_projects', function ($scope, $http, $location, ROOT, $rootScope, getAllPages) {

        var loadProjects = function () {
            getAllPages(ROOT + '/projects/')
                .then(function (results) {
                    $scope.projects = results;
                });
        };
        loadProjects();

        $scope.newProject = function () {
            $http.post(ROOT + '/projects/', {'name': $scope.newproj_name})
                .success(function () {
                    $scope.name = null;
                    loadProjects();
                });
        };

        $scope.launch = function (proj) {
            $location.path('/project/' + proj.uuid + '/');
        };
    })

    .controller('ctrl_project', function ($scope, $http, $location, ROOT, $rootScope, getAllPages, $routeParams, intervalNow, UPDATE_FREQ, $q, $window) {
        $scope.select_all_resources = false;
        $scope.$watch('select_all_resources', function (newVal, oldVal) {
            if (newVal != oldVal) {
                _.each($scope.resources, function (r) {
                    if (!r.origin) { // only selected uploaded resources
                        $scope.resource_selected[r.url] = newVal;
                    }
                });
            }
        });

        $scope.ui_showtypethumb = false;
        $scope.ui_hidegenerated = true;
        $scope.resource_selected = {};

        $http.get(ROOT + '/project/' + $routeParams.projectId + '/')
            .success(function (data) {
                $scope.project = data;
            });

        $scope.resource_uuid_name_map = {};
        intervalNow(function () {
            getAllPages(ROOT + '/resources/', {params: {'project': $routeParams.projectId, 'ordering': 'name'}})
                .then(function (results) {
                    $scope.resources = results;
                    $scope.generated_resources = {};
                    $scope.resource_hash = {};  // url to object

                    _.each(results, function (r) {
                        if (r.origin) {
                            $scope.generated_resources[r.origin] = r;
                        }

                        $scope.resource_hash[r.url] = r;

                        $scope.resource_uuid_name_map[r.uuid] = r.name;
                    });
                });
        }, UPDATE_FREQ);

        $scope.uploadResources = function () {
            var fd = new FormData();
            fd.append('project', $scope.project.url);
            _.each($scope.files, function (f) {
                fd.append('files', f);
            });

            console.log($scope.upload_type);
            if ($scope.upload_type) {
                fd.append('type', $scope.upload_type);
            }

            $http.post(ROOT + '/resources/', fd, {
                transformRequest: angular.identity,
                headers: {'Content-Type': undefined}
            }).success(function () {
                $scope.files = [];
                $scope.upload_type = null;
            });
        };
        $scope.deleteResource = function (r) {
            $http.delete(r.url)
                .success(function () {
                    delete $scope.resource_selected[r.url];
                });
        };
        $scope.updateResourceName = function (r) {
            var new_name = $window.prompt('New resource name: ', r.name);
            if (new_name) {
                $http.patch(r.url, {'name': new_name});
            }
        };

        ////// CREATE WORKFLOWS

        $scope.createWorkflow_rotatecrop = function () {
            var resources = [];
            _.each($scope.resource_selected, function (value, key) {
                if (value) {
                    resources.push(key);
                };
            });

            $http.post(ROOT + '/workflows/', {'project': $scope.project.url, 'name': $scope.new_workflow_name}).success(function (wf) {
                var jr = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.toolkits.rodan_plugins.plugins.rdn_rotate.rdn_rotate'});
                var jc = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.toolkits.rodan_plugins.plugins.rdn_crop.rdn_crop'});

                $q.all([
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': jr.url}),
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': jc.url}),
                    $http.post(ROOT + '/resourcecollections/', {'workflow': wf.url, 'resources': resources})
                ]).then(function (things) {
                    var wfjr = things[0].data;
                    var wfjc = things[1].data;
                    var rc = things[2].data;

                    $q.all([
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfjr.url, 'input_port_type': jr.input_port_types[0].url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wfjr.url, 'output_port_type': jr.output_port_types[0].url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfjc.url, 'input_port_type': jc.input_port_types[0].url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wfjc.url, 'output_port_type': jc.output_port_types[0].url}),
                    ]).then(function (things) {
                        var ipr = things[0].data;
                        var opr = things[1].data;
                        var ipc = things[2].data;
                        var opc = things[3].data;

                        $q.all([
                            $http.post(ROOT + '/resourceassignments/', {'input_port': ipr.url, 'resource_collection': rc.url}),
                            $http.post(ROOT + '/connections/', {'output_port': opr.url, 'input_port': ipc.url})
                        ]).then(function (things) {
                            console.log('rotate-crop workflow created!');
                        });
                    });
                });
            }).error(function (errors) {
                $scope.new_workflow_error = errors;
            });
        };

        $scope.createWorkflow_complete = function () {
            var resources = [];
            var gamera_classifier_url;
            _.each($scope.resource_selected, function (selected, url) {
                if (selected) {
                    var r = $scope.resource_hash[url];
                    var m = $scope.resourcetypes_hash[r.resource_type].mimetype;
                    if (m.indexOf('image/') == 0) { // start with image/
                        resources.push(url);
                    } else if (m == 'application/gamera+xml') {
                        gamera_classifier_url = url;
                    }
                };
            });
            $http.post(ROOT + '/workflows/', {'project': $scope.project.url, 'name': $scope.new_workflow_name}).success(function (wf) {
                var j_gs = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.plugins.image_conversion.to_greyscale'});
                var j_bi = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.custom.simple_binarise_interactive'});
                var j_pm = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.border_removal.poly_mask'});
                var j_dsp = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.toolkits.rodan_plugins.plugins.rdn_despeckle.rdn_despeckle_interactive'});
                var j_seg = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.segmentation.segmentation'});
                var j_slr = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.toolkits.staffline_removal.plugins.staff_removal.staff_removal'});
                var j_cls = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.custom.classification'});
                var j_pf = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.custom.pitch_finding'});

                $q.all([
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': j_gs.url}),
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': j_bi.url}),
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': j_pm.url}),
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': j_dsp.url}),
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': j_seg.url, 'job_settings': {'num_lines': 4, 'scanlines': 20, 'blackness': 0.8, 'tolerance': -1}}),
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': j_slr.url}),
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': j_cls.url}),
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': j_pf.url}),
                    $http.post(ROOT + '/resourcecollections/', {'workflow': wf.url, 'resources': resources})
                ]).then(function (things) {
                    var wf_gs = things[0].data;
                    var wf_bi = things[1].data;
                    var wf_pm = things[2].data;
                    var wf_dsp = things[3].data;
                    var wf_seg = things[4].data;
                    var wf_slr = things[5].data;
                    var wf_cls = things[6].data;
                    var wf_pf = things[7].data;
                    var rc = things[8].data;

                    var j_cls_ipt_image = _.find(j_cls.input_port_types, function (ipt) { return ipt.name == 'Staffless Image'});
                    var j_cls_ipt_clsfier = _.find(j_cls.input_port_types, function (ipt) { return ipt.name == 'Classifier'});
                    var j_pf_ipt_image = _.find(j_pf.input_port_types, function (ipt) { return ipt.name == 'Segmented Image'});
                    var j_pf_ipt_clsf = _.find(j_pf.input_port_types, function (ipt) { return ipt.name == 'Classifier Result'});
                    $q.all([
                        $http.post(ROOT + '/inputports/', {'workflow_job': wf_gs.url, 'input_port_type': j_gs.input_port_types[0].url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wf_gs.url, 'output_port_type': j_gs.output_port_types[0].url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wf_bi.url, 'input_port_type': j_bi.input_port_types[0].url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wf_bi.url, 'output_port_type': j_bi.output_port_types[0].url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wf_pm.url, 'input_port_type': j_pm.input_port_types[0].url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wf_pm.url, 'output_port_type': j_pm.output_port_types[0].url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wf_dsp.url, 'input_port_type': j_dsp.input_port_types[0].url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wf_dsp.url, 'output_port_type': j_dsp.output_port_types[0].url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wf_seg.url, 'input_port_type': j_seg.input_port_types[0].url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wf_seg.url, 'output_port_type': j_seg.output_port_types[0].url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wf_slr.url, 'input_port_type': j_slr.input_port_types[0].url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wf_slr.url, 'output_port_type': j_slr.output_port_types[0].url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wf_cls.url, 'input_port_type': j_cls_ipt_image.url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wf_cls.url, 'input_port_type': j_cls_ipt_clsfier.url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wf_cls.url, 'output_port_type': j_cls.output_port_types[0].url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wf_pf.url, 'input_port_type': j_pf_ipt_image.url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wf_pf.url, 'input_port_type': j_pf_ipt_clsf.url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wf_pf.url, 'output_port_type': j_pf.output_port_types[0].url})
                    ]).then(function (things) {
                        var ip_gs = things[0].data;
                        var op_gs = things[1].data;
                        var ip_bi = things[2].data;
                        var op_bi = things[3].data;
                        var ip_pm = things[4].data;
                        var op_pm = things[5].data;
                        var ip_dsp = things[6].data;
                        var op_dsp = things[7].data;
                        var ip_seg = things[8].data;
                        var op_seg = things[9].data;
                        var ip_slr = things[10].data;
                        var op_slr = things[11].data;
                        var ip_cls_image = things[12].data;
                        var ip_cls_clsfier = things[13].data;
                        var op_cls = things[14].data;
                        var ip_pf_image = things[15].data;
                        var ip_pf_clsf = things[16].data;
                        var op_pf = things[17].data;
                        $q.all([
                            $http.post(ROOT + '/resourceassignments/', {'input_port': ip_gs.url, 'resource_collection': rc.url}),
                            $http.post(ROOT + '/connections/', {'output_port': op_gs.url, 'input_port': ip_bi.url}),
                            $http.post(ROOT + '/connections/', {'output_port': op_bi.url, 'input_port': ip_pm.url}),
                            $http.post(ROOT + '/connections/', {'output_port': op_pm.url, 'input_port': ip_dsp.url}),
                            $http.post(ROOT + '/connections/', {'output_port': op_dsp.url, 'input_port': ip_seg.url}),
                            $http.post(ROOT + '/connections/', {'output_port': op_seg.url, 'input_port': ip_slr.url}),
                            $http.post(ROOT + '/connections/', {'output_port': op_slr.url, 'input_port': ip_cls_image.url}),
                            $http.post(ROOT + '/resourceassignments/', {'input_port': ip_cls_clsfier.url, 'resource': gamera_classifier_url}),
                            $http.post(ROOT + '/connections/', {'output_port': op_cls.url, 'input_port': ip_pf_clsf.url}),
                            $http.post(ROOT + '/connections/', {'output_port': op_seg.url, 'input_port': ip_pf_image.url})
                        ]).then(function (things) {
                            console.log('created!');
                        });
                    });
                });
            }).error(function (errors) {
                $scope.new_workflow_error = errors;
            });
        };


        ////// CREATE WORKFLOWS END
        intervalNow(function () {
            getAllPages(ROOT + '/workflows/', {params: {'project': $routeParams.projectId}})
                .then(function (results) {
                    $scope.workflows = results;
                });
        }, UPDATE_FREQ);
        $scope.workflow_validationerror = {};
        $scope.validateWorkflow = function (w) {
            $http.patch(w.url, {'valid': true})
                .success(function () {
                    delete $scope.workflow_validationerror[w.url];
                })
                .error(function (error) {
                    $scope.workflow_validationerror[w.url] = error.detail
                });
        };
        $scope.deleteWorkflow = function (w) {
            $http.delete(w.url)
                .error(function (error) {
                    console.log(error);
                });
        };
        $scope.runWorkflow = function (w, test_run) {
            $http.post(ROOT + '/workflowruns/', {'workflow': w.url, 'test_run': !!test_run})
                .error(function (error) {
                    console.log(error);
                });
        };

        intervalNow(function () {
            getAllPages(ROOT + '/workflowruns/', {params: {'project': $routeParams.projectId, 'ordering': '-created'}})
                .then(function (results) {
                    $scope.workflowruns = results;
                });
        }, UPDATE_FREQ);
        intervalNow(function () {
            getAllPages(ROOT + '/runjobs/', {params: {'project': $routeParams.projectId, 'ordering': '-created'}}) // RunJobs are created in a reverse order.
                .then(function (results) {
                    $scope.runjobs = [];
                    angular.forEach(results, function (rj) {
                        $scope.runjobs[rj.workflow_run] = $scope.runjobs[rj.workflow_run] || [];
                        $scope.runjobs[rj.workflow_run].push(rj);
                    });
                });
        }, UPDATE_FREQ);

        $scope.ui_showresults = false;

        $scope.retryWorkflowRun = function (wfrun) {
            $http.patch(wfrun.url, {'status': 11})
                .error(function (error) {
                    console.log(error);
                });
        };
        $scope.cancelWorkflowRun = function (wfrun) {
            $http.patch(wfrun.url, {'status': 9})
                .error(function (error) {
                    console.log(error);
                });
        };

        $scope.packageResults = function (wfrun, mode) {
            var obj = {
                'workflow_run': wfrun.url,
                'packaging_mode': mode
            };
            $http.post(ROOT + '/resultspackages/', obj);
        };

        intervalNow(function () {
            getAllPages(ROOT + '/resultspackages/', {params: {'project': $routeParams.projectId, 'ordering': '-created'}})
                .then(function (results) {
                    $scope.resultspackages = results;
                }, function (err) {
                    console.log(err);
                });
        }, UPDATE_FREQ);
        $scope.cancelResultsPackage = function (rp) {
            $http.patch(rp.url, {'status': 9})
                .error(function (error) {
                    console.log(error);
                });
        };
        $scope.deleteResultsPackage = function (rp) {
            $http.delete(rp.url)
                .error(function (error) {
                    console.log(error);
                });
        };
    })
