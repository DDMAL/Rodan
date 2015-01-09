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
            '1': 'Running',
            '4': 'Finished',
            '-1': 'Failed',
            '9': 'Cancelled',
            '8': 'Expired'
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
                var jrm = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.toolkits.rodan_plugins.plugins.rdn_rotate.rdn_rotate_manual'});
                var jra = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.toolkits.rodan_plugins.plugins.rdn_rotate.rdn_rotate_apply_rotate'});

                var jcm = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.toolkits.rodan_plugins.plugins.rdn_crop.rdn_crop_manual'});
                var jca = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.toolkits.rodan_plugins.plugins.rdn_crop.rdn_crop_apply_crop'});

                $q.all([
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': jrm.url}),
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': jra.url}),
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': jcm.url}),
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': jca.url}),
                    $http.post(ROOT + '/resourcecollections/', {'workflow': wf.url, 'resources': $scope.resources_rotatecrop})
                ]).then(function (things) {
                    var wfjrm = things[0].data;
                    var wfjra = things[1].data;
                    var wfjcm = things[2].data;
                    var wfjca = things[3].data;
                    var rc = things[4].data;

                    var jra_ipt_image = _.find(jra.input_port_types, function (ipt) { return ipt.name == 'image'});
                    var jra_ipt_angle = _.find(jra.input_port_types, function (ipt) { return ipt.name == 'angle'});
                    var jca_ipt_image = _.find(jca.input_port_types, function (ipt) { return ipt.name == 'image'})
                    var jca_ipt_parameters = _.find(jca.input_port_types, function (ipt) { return ipt.name == 'parameters'});
                    $q.all([
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfjrm.url, 'input_port_type': jrm.input_port_types[0].url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wfjrm.url, 'output_port_type': jrm.output_port_types[0].url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfjra.url, 'input_port_type': jra_ipt_image.url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfjra.url, 'input_port_type': jra_ipt_angle.url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wfjra.url, 'output_port_type': jra.output_port_types[0].url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfjcm.url, 'input_port_type': jcm.input_port_types[0].url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wfjcm.url, 'output_port_type': jcm.output_port_types[0].url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfjca.url, 'input_port_type': jca_ipt_image.url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfjca.url, 'input_port_type': jca_ipt_parameters.url}),
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
                            $http.post(ROOT + '/resourceassignments/', {'input_port': iprm.url, 'resource_collection': rc.url}),
                            $http.post(ROOT + '/resourceassignments/', {'input_port': ipra_img.url, 'resource_collection': rc.url}),
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
        $scope.newDespeckleWorkflow = function () {
            $http.post(ROOT + '/workflows/', {'project': $scope.project, 'name': $scope.name_despeckle}).success(function (wf) {
                var jm = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.toolkits.rodan_plugins.plugins.rdn_despeckle.rdn_despeckle_manual'});
                var ja = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.toolkits.rodan_plugins.plugins.rdn_despeckle.rdn_despeckle_apply_despeckle'});

                $q.all([
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': jm.url}),
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': ja.url}),
                    $http.post(ROOT + '/resourcecollections/', {'workflow': wf.url, 'resources': $scope.resources_despeckle})
                ]).then(function (things) {
                    var wfjm = things[0].data;
                    var wfja = things[1].data;
                    var rc = things[2].data;

                    var ja_ipt_image = _.find(ja.input_port_types, function (ipt) { return ipt.name == 'image'});
                    var ja_ipt_parameters = _.find(ja.input_port_types, function (ipt) { return ipt.name == 'parameters'});
                    $q.all([
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfjm.url, 'input_port_type': jm.input_port_types[0].url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wfjm.url, 'output_port_type': jm.output_port_types[0].url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfja.url, 'input_port_type': ja_ipt_image.url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfja.url, 'input_port_type': ja_ipt_parameters.url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wfja.url, 'output_port_type': ja.output_port_types[0].url})
                    ]).then(function (things) {
                        var ipm = things[0].data;
                        var opm = things[1].data;
                        var ipa_img = things[2].data;
                        var ipa_par = things[3].data;
                        var opa = things[4].data;

                        $q.all([
                            $http.post(ROOT + '/resourceassignments/', {'input_port': ipm.url, 'resource_collection': rc.url}),
                            $http.post(ROOT + '/resourceassignments/', {'input_port': ipa_img.url, 'resource_collection': rc.url}),
                            $http.post(ROOT + '/connections/', {'output_port': opm.url, 'input_port': ipa_par.url})
                        ]).then(function (things) {
                            console.log('despeckle workflow created!');
                        }, errhandler);
                    }, errhandler);
                }, errhandler);
            });
        };
        $scope.newPolyMaskWorkflow = function () {
            $http.post(ROOT + '/workflows/', {'project': $scope.project, 'name': $scope.name_polymask}).success(function (wf) {
                var jm = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.interactive_tasks.border_removal.poly_mask.manual'});
                var ja = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.interactive_tasks.border_removal.poly_mask.apply'});

                $q.all([
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': jm.url}),
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': ja.url}),
                    $http.post(ROOT + '/resourcecollections/', {'workflow': wf.url, 'resources': $scope.resources_polymask})
                ]).then(function (things) {
                    var wfjm = things[0].data;
                    var wfja = things[1].data;
                    var rc = things[2].data;

                    var ja_ipt_image = _.find(ja.input_port_types, function (ipt) { return ipt.name == 'image'});
                    var ja_ipt_polygon = _.find(ja.input_port_types, function (ipt) { return ipt.name == 'polygon'});
                    $q.all([
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfjm.url, 'input_port_type': jm.input_port_types[0].url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wfjm.url, 'output_port_type': jm.output_port_types[0].url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfja.url, 'input_port_type': ja_ipt_image.url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfja.url, 'input_port_type': ja_ipt_polygon.url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wfja.url, 'output_port_type': ja.output_port_types[0].url})
                    ]).then(function (things) {
                        var ipm = things[0].data;
                        var opm = things[1].data;
                        var ipa_img = things[2].data;
                        var ipa_par = things[3].data;
                        var opa = things[4].data;

                        $q.all([
                            $http.post(ROOT + '/resourceassignments/', {'input_port': ipm.url, 'resource_collection': rc.url}),
                            $http.post(ROOT + '/resourceassignments/', {'input_port': ipa_img.url, 'resource_collection': rc.url}),
                            $http.post(ROOT + '/connections/', {'output_port': opm.url, 'input_port': ipa_par.url})
                        ]).then(function (things) {
                            console.log('polymask workflow created!');
                        }, errhandler);
                    }, errhandler);
                }, errhandler);
            });
        };
        $scope.newSegmentationWorkflow = function () {
            $http.post(ROOT + '/workflows/', {'project': $scope.project, 'name': $scope.name_segmentation}).success(function (wf) {
                var jc = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.interactive_tasks.segmentation.computer_assistance'});
                var jm = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.interactive_tasks.segmentation.manual_correction'});
                var ja = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.interactive_tasks.segmentation.apply_segmentation'});

                $q.all([
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': jc.url}),
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': jm.url}),
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': ja.url}),
                    $http.post(ROOT + '/resourcecollections/', {'workflow': wf.url, 'resources': $scope.resources_segmentation})
                ]).then(function (things) {
                    var wfjc = things[0].data;
                    var wfjm = things[1].data;
                    var wfja = things[2].data;
                    var rc = things[3].data;

                    var jm_ipt_image = _.find(jm.input_port_types, function (ipt) { return ipt.name == 'image'});
                    var jm_ipt_polygon = _.find(jm.input_port_types, function (ipt) { return ipt.name == 'polygon'});
                    var ja_ipt_image = _.find(ja.input_port_types, function (ipt) { return ipt.name == 'image'});
                    var ja_ipt_polygon = _.find(ja.input_port_types, function (ipt) { return ipt.name == 'polygon'});
                    $q.all([
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfjc.url, 'input_port_type': jc.input_port_types[0].url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wfjc.url, 'output_port_type': jc.output_port_types[0].url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfjm.url, 'input_port_type': jm_ipt_image.url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfjm.url, 'input_port_type': jm_ipt_polygon.url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wfjm.url, 'output_port_type': jm.output_port_types[0].url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfja.url, 'input_port_type': ja_ipt_image.url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfja.url, 'input_port_type': ja_ipt_polygon.url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wfja.url, 'output_port_type': ja.output_port_types[0].url})
                    ]).then(function (things) {
                        var ipc = things[0].data;
                        var opc = things[1].data;
                        var ipm_img = things[2].data;
                        var ipm_pol = things[3].data;
                        var opm = things[4].data;
                        var ipa_img = things[5].data;
                        var ipa_pol = things[6].data;
                        var opa = things[7].data;

                        $q.all([
                            $http.post(ROOT + '/resourceassignments/', {'input_port': ipc.url, 'resource_collection': rc.url}),
                            $http.post(ROOT + '/resourceassignments/', {'input_port': ipm_img.url, 'resource_collection': rc.url}),
                            $http.post(ROOT + '/resourceassignments/', {'input_port': ipa_img.url, 'resource_collection': rc.url}),
                            $http.post(ROOT + '/connections/', {'output_port': opc.url, 'input_port': ipm_pol.url}),
                            $http.post(ROOT + '/connections/', {'output_port': opm.url, 'input_port': ipa_pol.url})
                        ]).then(function (things) {
                            console.log('segmentation workflow created!');
                        }, errhandler);
                    }, errhandler);
                }, errhandler);
            });
        };
        $scope.newPixelSegmentWorkflow = function () {
            $http.post(ROOT + '/workflows/', {'project': $scope.project, 'name': $scope.name_pixelsegment}).success(function (wf) {
                var jm = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.interactive_tasks.lyric_extraction.pixel_segment.manual'});
                var ja = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.interactive_tasks.lyric_extraction.pixel_segment.apply'});

                $q.all([
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': jm.url}),
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': ja.url}),
                    $http.post(ROOT + '/resourcecollections/', {'workflow': wf.url, 'resources': $scope.resources_pixelsegment})
                ]).then(function (things) {
                    var wfjm = things[0].data;
                    var wfja = things[1].data;
                    var rc = things[2].data;

                    var ja_ipt_image = _.find(ja.input_port_types, function (ipt) { return ipt.name == 'image'});
                    var ja_ipt_geometries = _.find(ja.input_port_types, function (ipt) { return ipt.name == 'geometries'});
                    $q.all([
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfjm.url, 'input_port_type': jm.input_port_types[0].url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wfjm.url, 'output_port_type': jm.output_port_types[0].url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfja.url, 'input_port_type': ja_ipt_image.url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfja.url, 'input_port_type': ja_ipt_geometries.url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wfja.url, 'output_port_type': ja.output_port_types[0].url})
                    ]).then(function (things) {
                        var ipm = things[0].data;
                        var opm = things[1].data;
                        var ipa_img = things[2].data;
                        var ipa_geo = things[3].data;
                        var opa = things[4].data;

                        $q.all([
                            $http.post(ROOT + '/resourceassignments/', {'input_port': ipm.url, 'resource_collection': rc.url}),
                            $http.post(ROOT + '/resourceassignments/', {'input_port': ipa_img.url, 'resource_collection': rc.url}),
                            $http.post(ROOT + '/connections/', {'output_port': opm.url, 'input_port': ipa_geo.url})
                        ]).then(function (things) {
                            console.log('pixel_segment workflow created!');
                        }, errhandler);
                    }, errhandler);
                }, errhandler);
            });
        };
        $scope.newCompleteWorkflow = function () {
            $http.post(ROOT + '/workflows/', {'project': $scope.project, 'name': $scope.name_complete}).success(function (wf) {
                var j_1 = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.auto_task.auto_border_removal'});
                var j_2 = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.plugins.image_conversion.to_greyscale'});
                var j_3 = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.plugins.threshold.threshold'});
                var j_4m = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.toolkits.rodan_plugins.plugins.rdn_despeckle.rdn_despeckle_manual'});
                var j_4a = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.toolkits.rodan_plugins.plugins.rdn_despeckle.rdn_despeckle_apply_despeckle'});
                var j_5c = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.interactive_tasks.segmentation.computer_assistance'});
                var j_5m = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.interactive_tasks.segmentation.manual_correction'});
                var j_5a = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.interactive_tasks.segmentation.apply_segmentation'});
//                var j_6m = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.interactive_tasks.lyric_extraction.pixel_segment.manual'});
//                var j_6a = _.find($rootScope.jobs, function (j) { return j.job_name == 'gamera.interactive_tasks.lyric_extraction.pixel_segment.apply'});

                $q.all([
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': j_1.url}),
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': j_2.url}),
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': j_3.url, 'job_settings': [{'name':'threshold', 'default': 0, 'type': 'int'}, {'name': 'storage format', 'default': 0, 'type': 'int'}]}),
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': j_4m.url}),
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': j_4a.url}),
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': j_5c.url}),
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': j_5m.url}),
                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': j_5a.url}),
//                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': j_6m.url}),
//                    $http.post(ROOT + '/workflowjobs/', {'workflow': wf.url, 'job': j_6a.url}),
                    $http.post(ROOT + '/resourcecollections/', {'workflow': wf.url, 'resources': $scope.resources_complete})
                ]).then(function (things) {
                    var wfj_1 = things[0].data;
                    var wfj_2 = things[1].data;
                    var wfj_3 = things[2].data;
                    var wfj_4m = things[3].data;
                    var wfj_4a = things[4].data;
                    var wfj_5c = things[5].data;
                    var wfj_5m = things[6].data;
                    var wfj_5a = things[7].data;
                    //var wfj_6m = things[8].data;
                    //var wfj_6a = things[9].data;
                    var rc = things[8].data;

                    var j_4a_ipt_image = _.find(j_4a.input_port_types, function (ipt) { return ipt.name == 'image'});
                    var j_4a_ipt_parameters = _.find(j_4a.input_port_types, function (ipt) { return ipt.name == 'parameters'});
                    var j_5m_ipt_image = _.find(j_5m.input_port_types, function (ipt) { return ipt.name == 'image'});
                    var j_5m_ipt_polygon = _.find(j_5m.input_port_types, function (ipt) { return ipt.name == 'polygon'});
                    var j_5a_ipt_image = _.find(j_5a.input_port_types, function (ipt) { return ipt.name == 'image'});
                    var j_5a_ipt_polygon = _.find(j_5a.input_port_types, function (ipt) { return ipt.name == 'polygon'});

                    $q.all([
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfj_1.url, 'input_port_type': j_1.input_port_types[0].url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wfj_1.url, 'output_port_type': j_1.output_port_types[0].url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfj_2.url, 'input_port_type': j_2.input_port_types[0].url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wfj_2.url, 'output_port_type': j_2.output_port_types[0].url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfj_3.url, 'input_port_type': j_3.input_port_types[0].url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wfj_3.url, 'output_port_type': j_3.output_port_types[0].url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfj_4m.url, 'input_port_type': j_4m.input_port_types[0].url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wfj_4m.url, 'output_port_type': j_4m.output_port_types[0].url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfj_4a.url, 'input_port_type': j_4a_ipt_image.url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfj_4a.url, 'input_port_type': j_4a_ipt_parameters.url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wfj_4a.url, 'output_port_type': j_4a.output_port_types[0].url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfj_5c.url, 'input_port_type': j_5c.input_port_types[0].url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wfj_5c.url, 'output_port_type': j_5c.output_port_types[0].url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfj_5m.url, 'input_port_type': j_5m_ipt_image.url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfj_5m.url, 'input_port_type': j_5m_ipt_polygon.url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wfj_5m.url, 'output_port_type': j_5m.output_port_types[0].url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfj_5a.url, 'input_port_type': j_5a_ipt_image.url}),
                        $http.post(ROOT + '/inputports/', {'workflow_job': wfj_5a.url, 'input_port_type': j_5a_ipt_polygon.url}),
                        $http.post(ROOT + '/outputports/', {'workflow_job': wfj_5a.url, 'output_port_type': j_5a.output_port_types[0].url}),
                    ]).then(function (things) {
                        var ip_1 = things[0].data;
                        var op_1 = things[1].data;
                        var ip_2 = things[2].data;
                        var op_2 = things[3].data;
                        var ip_3 = things[4].data;
                        var op_3 = things[5].data;
                        var ip_4m = things[6].data;
                        var op_4m = things[7].data;
                        var ip_4a_image = things[8].data;
                        var ip_4a_parameters = things[9].data;
                        var op_4a = things[10].data;
                        var ip_5c = things[11].data;
                        var op_5c = things[12].data;
                        var ip_5m_image = things[13].data;
                        var ip_5m_parameters = things[14].data;
                        var op_5m = things[15].data;
                        var ip_5a_image = things[16].data;
                        var ip_5a_parameters = things[17].data;
                        var op_5a = things[18].data;

                        $q.all([
                            $http.post(ROOT + '/resourceassignments/', {'input_port': ip_1.url, 'resource_collection': rc.url}),
                            $http.post(ROOT + '/connections/', {'output_port': op_1.url, 'input_port': ip_2.url}),
                            $http.post(ROOT + '/connections/', {'output_port': op_2.url, 'input_port': ip_3.url}),
                            $http.post(ROOT + '/connections/', {'output_port': op_3.url, 'input_port': ip_4m.url}),
                            $http.post(ROOT + '/connections/', {'output_port': op_3.url, 'input_port': ip_4a_image.url}),
                            $http.post(ROOT + '/connections/', {'output_port': op_4m.url, 'input_port': ip_4a_parameters.url}),
                            $http.post(ROOT + '/connections/', {'output_port': op_4a.url, 'input_port': ip_5c.url}),
                            $http.post(ROOT + '/connections/', {'output_port': op_4a.url, 'input_port': ip_5m_image.url}),
                            $http.post(ROOT + '/connections/', {'output_port': op_4a.url, 'input_port': ip_5a_image.url}),
                            $http.post(ROOT + '/connections/', {'output_port': op_5c.url, 'input_port': ip_5m_parameters.url}),
                            $http.post(ROOT + '/connections/', {'output_port': op_5m.url, 'input_port': ip_5a_parameters.url})
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
        $scope.cancelWorkflowRun = function (wfrun) {
            $http.patch(wfrun.url, {'status': 9})
                .error(function (error) {
                    console.log(error);
                });
        };
        $scope.packageResults = function (wfrun, expiry_time) {
            var obj = {
                'workflow_run': wfrun.url
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
