angular.module('rodanTestApp', [])
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
                getAllPages(ROOT + '/resourcetypes/')
                    .then(function (results) {
                        $rootScope.resourcetypes_hash = {};
                        _.each(results, function (rt) {
                            $rootScope.resourcetypes_hash[rt.url] = rt;
                        });
                    }, function (err) {
                        console.log(err);
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
        $scope.deleteProject = function (p) {
            $http.delete(p.url);
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
            console.log(error);
        };
        $scope.newToGreyscaleWorkflow = function () {
            $http.post(ROOT + '/workflows/', {'project': $scope.project, 'name': $scope.name_greyscale}).success(function (wf) {
                var job_greyscale = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.plugins.image_conversion.to_greyscale'});
                $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job_type': 0, 'job': job_greyscale.url}).success(function (wfjob) {
                    $q.all([
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfjob.url, 'input_port_type': job_greyscale.input_port_types[0].url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wfjob.url, 'output_port_type': job_greyscale.output_port_types[0].url}),
                        $http.post(ROOT + '/resourcecollections/', {'workflow': wf.url, 'resources': $scope.resources_greyscale})
                    ]).then(function (things) {
                        var ip = things[0].data;
                        var op = things[1].data;
                        var rc = things[2].data;
                        $http.post(ROOT + '/resourceassignments/', {'input_port': ip.url, 'resource_collection': rc.url})
                            .success(function (ra) {
                                console.log('to_greyscale workflow created!');
                            }).error(errhandler);
                    }, errhandler);
                }).error(errhandler);
            }).error(errhandler);
        };
        $scope.newToOnebitWorkflow = function () {
            $http.post(ROOT + '/workflows/', {'project': $scope.project, 'name': $scope.name_onebit}).success(function (wf) {
                var job_onebit = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.plugins.image_conversion.to_onebit'});
                $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job_type': 0, 'job': job_onebit.url}).success(function (wfjob) {
                    $q.all([
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfjob.url, 'input_port_type': job_onebit.input_port_types[0].url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wfjob.url, 'output_port_type': job_onebit.output_port_types[0].url}),
                        $http.post(ROOT + '/resourcecollections/', {'workflow': wf.url, 'resources': $scope.resources_onebit})
                    ]).then(function (things) {
                        var ip = things[0].data;
                        var op = things[1].data;
                        var rc = things[2].data;
                        $http.post(ROOT + '/resourceassignments/', {'input_port': ip.url, 'resource_collection': rc.url})
                            .success(function (ra) {
                                console.log('to_onebit workflow created!');
                            }).error(errhandler);
                    }, errhandler);
                }).error(errhandler);
            }).error(errhandler);
        };
        $scope.newRotateCropWorkflow = function () {
            $http.post(ROOT + '/workflows/', {'project': $scope.project, 'name': $scope.name_rotatecrop}).success(function (wf) {
                var jr = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.toolkits.rodan_plugins.plugins.rdn_rotate.rdn_rotate'});
                var jc = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.toolkits.rodan_plugins.plugins.rdn_crop.rdn_crop'});

                $q.all([
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': jr.url}),
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': jc.url}),
                    $http.post(ROOT + '/resourcecollections/', {'workflow': wf.url, 'resources': $scope.resources_rotatecrop})
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
                        }, errhandler);
                    }, errhandler);
                }, errhandler);
            });
        };
        $scope.newDespeckleWorkflow = function () {
            $http.post(ROOT + '/workflows/', {'project': $scope.project, 'name': $scope.name_despeckle}).success(function (wf) {
                var j = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.toolkits.rodan_plugins.plugins.rdn_despeckle.rdn_despeckle_interactive'});

                $q.all([
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': j.url}),
                    $http.post(ROOT + '/resourcecollections/', {'workflow': wf.url, 'resources': $scope.resources_despeckle})
                ]).then(function (things) {
                    var wfj = things[0].data;
                    var rc = things[1].data;

                    $q.all([
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfj.url, 'input_port_type': j.input_port_types[0].url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wfj.url, 'output_port_type': j.output_port_types[0].url})
                    ]).then(function (things) {
                        var ip = things[0].data;
                        var op = things[1].data;

                        $q.all([
                            $http.post(ROOT + '/resourceassignments/', {'input_port': ip.url, 'resource_collection': rc.url})
                        ]).then(function (things) {
                            console.log('despeckle workflow created!');
                        }, errhandler);
                    }, errhandler);
                }, errhandler);
            });
        };
        $scope.newPolyMaskWorkflow = function () {
            $http.post(ROOT + '/workflows/', {'project': $scope.project, 'name': $scope.name_polymask}).success(function (wf) {
                var j = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.border_removal.poly_mask'});

                $q.all([
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': j.url}),
                    $http.post(ROOT + '/resourcecollections/', {'workflow': wf.url, 'resources': $scope.resources_polymask})
                ]).then(function (things) {
                    var wfj = things[0].data;
                    var rc = things[1].data;

                    $q.all([
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfj.url, 'input_port_type': j.input_port_types[0].url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wfj.url, 'output_port_type': j.output_port_types[0].url})
                    ]).then(function (things) {
                        var ip = things[0].data;
                        var op = things[1].data;

                        $q.all([
                            $http.post(ROOT + '/resourceassignments/', {'input_port': ip.url, 'resource_collection': rc.url})
                        ]).then(function (things) {
                            console.log('polymask workflow created!');
                        }, errhandler);
                    }, errhandler);
                }, errhandler);
            });
        };
        $scope.newSegmentationWorkflow = function () {
            $http.post(ROOT + '/workflows/', {'project': $scope.project, 'name': $scope.name_segmentation}).success(function (wf) {
                var j = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.segmentation.segmentation'});

                $q.all([
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': j.url}),
                    $http.post(ROOT + '/resourcecollections/', {'workflow': wf.url, 'resources': $scope.resources_segmentation})
                ]).then(function (things) {
                    var wfj = things[0].data;
                    var rc = things[1].data;

                    $q.all([
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfj.url, 'input_port_type': j.input_port_types[0].url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wfj.url, 'output_port_type': j.output_port_types[0].url})
                    ]).then(function (things) {
                        var ip = things[0].data;
                        var op = things[1].data;

                        $q.all([
                            $http.post(ROOT + '/resourceassignments/', {'input_port': ip.url, 'resource_collection': rc.url})
                        ]).then(function (things) {
                            console.log('segmentation workflow created!');
                        }, errhandler);
                    }, errhandler);
                }, errhandler);
            });
        };
        $scope.newPixelSegmentWorkflow = function () {
            $http.post(ROOT + '/workflows/', {'project': $scope.project, 'name': $scope.name_pixelsegment}).success(function (wf) {
                var j = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.lyric_extraction.pixel_segment'});

                $q.all([
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': j.url}),
                    $http.post(ROOT + '/resourcecollections/', {'workflow': wf.url, 'resources': $scope.resources_pixelsegment})
                ]).then(function (things) {
                    var wfj = things[0].data;
                    var rc = things[1].data;

                    $q.all([
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfj.url, 'input_port_type': j.input_port_types[0].url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wfj.url, 'output_port_type': j.output_port_types[0].url})
                    ]).then(function (things) {
                        var ip = things[0].data;
                        var op = things[1].data;

                        $q.all([
                            $http.post(ROOT + '/resourceassignments/', {'input_port': ip.url, 'resource_collection': rc.url})
                        ]).then(function (things) {
                            console.log('pixel_segment workflow created!');
                        }, errhandler);
                    }, errhandler);
                }, errhandler);
            });
        };
        $scope.newCompleteWorkflow = function () {
            $http.post(ROOT + '/workflows/', {'project': $scope.project, 'name': $scope.name_complete}).success(function (wf) {
                var j_1 = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.custom.border_removal'});
                var j_2 = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.plugins.image_conversion.to_greyscale'});
                var j_3 = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.plugins.threshold.threshold'});
                var j_4 = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.toolkits.rodan_plugins.plugins.rdn_despeckle.rdn_despeckle_interactive'});
                var j_5 = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.segmentation.segmentation'});
                //var j_6 = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.lyric_extraction.pixel_segment'});

                $q.all([
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': j_1.url}),
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': j_2.url}),
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': j_3.url, 'job_settings': {'threshold': 128, 'storage format': "dense"}}),
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': j_4.url}),
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': j_5.url}),
                    //$http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': j_6.url}),
                    $http.post(ROOT + '/resourcecollections/', {'workflow': wf.url, 'resources': $scope.resources_complete})
                ]).then(function (things) {
                    var wfj_1 = things[0].data;
                    var wfj_2 = things[1].data;
                    var wfj_3 = things[2].data;
                    var wfj_4 = things[3].data;
                    var wfj_5 = things[4].data;
                    //var wfj_6 = things[5].data;
                    var rc = things[5].data;

                    $q.all([
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfj_1.url, 'input_port_type': j_1.input_port_types[0].url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wfj_1.url, 'output_port_type': j_1.output_port_types[0].url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfj_2.url, 'input_port_type': j_2.input_port_types[0].url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wfj_2.url, 'output_port_type': j_2.output_port_types[0].url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfj_3.url, 'input_port_type': j_3.input_port_types[0].url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wfj_3.url, 'output_port_type': j_3.output_port_types[0].url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfj_4.url, 'input_port_type': j_4.input_port_types[0].url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wfj_4.url, 'output_port_type': j_4.output_port_types[0].url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfj_5.url, 'input_port_type': j_5.input_port_types[0].url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wfj_5.url, 'output_port_type': j_5.output_port_types[0].url}),
                        //$http.post(ROOT + '/inputports/', {'workflow_job': wfj_6.url, 'input_port_type': j_6.input_port_types[0].url}),
                        //$http.post(ROOT + '/outputports/', {'workflow_job': wfj_6.url, 'output_port_type': j_6.output_port_types[0].url})
                    ]).then(function (things) {
                        var ip_1 = things[0].data;
                        var op_1 = things[1].data;
                        var ip_2 = things[2].data;
                        var op_2 = things[3].data;
                        var ip_3 = things[4].data;
                        var op_3 = things[5].data;
                        var ip_4 = things[6].data;
                        var op_4 = things[7].data;
                        var ip_5 = things[8].data;
                        var op_5 = things[9].data;
                        //var ip_6 = things[10].data;
                        //var op_6 = things[11].data;

                        $q.all([
                            $http.post(ROOT + '/resourceassignments/', {'input_port': ip_1.url, 'resource_collection': rc.url}),
                            $http.post(ROOT + '/connections/', {'output_port': op_1.url, 'input_port': ip_2.url}),
                            $http.post(ROOT + '/connections/', {'output_port': op_2.url, 'input_port': ip_3.url}),
                            $http.post(ROOT + '/connections/', {'output_port': op_3.url, 'input_port': ip_4.url}),
                            $http.post(ROOT + '/connections/', {'output_port': op_4.url, 'input_port': ip_5.url})
                            //$http.post(ROOT + '/connections/', {'output_port': op_5.url, 'input_port': ip_6.url})
                        ]).then(function (things) {
                            console.log('complete workflow created!');
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
        $scope.runWorkflow = function (w, test_run) {
            $http.post(ROOT + '/workflowruns/', {'workflow': w.url, 'test_run': !!test_run})
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
            getAllPages(ROOT + '/runjobs/?ordering=-created') // RunJobs are created in a reverse order.
                .then(function (results) {
                    $rootScope.runjobs = [];
                    angular.forEach(results, function (rj) {
                        $rootScope.runjobs[rj.workflow_run] = $rootScope.runjobs[rj.workflow_run] || [];
                        $rootScope.runjobs[rj.workflow_run].push(rj);
                    });
                }, function (err) {
                    console.log(err);
                });
        }, UPDATE_FREQ);
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
        $scope.packageResults = function (wfrun, packaging_mode, expiry_time) {
            var obj = {
                'workflow_run': wfrun.url,
                'packaging_mode': packaging_mode
            };
            if (expiry_time) {
                var d = Date.now() + expiry_time;
                var d_obj = new Date(d);
                obj['expiry_time'] = d_obj.toJSON();
            }
            $http.post(ROOT + '/resultspackages/', obj)
                .error(function (error) {
                    console.log(error);
                });
        };
    })
    .controller('resultspackageCtrl', function ($scope, $http, ROOT, intervalNow, getAllPages, UPDATE_FREQ, $rootScope) {
        intervalNow(function () {
            getAllPages(ROOT + '/resultspackages/')
                .then(function (results) {
                    $rootScope.resultspackages = results;
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
