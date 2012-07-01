$(document).ready(function () {
    if ($('#main-line-graph').length) {
        var graph = new Highcharts.Chart({
            chart: {
                backgroundColor: null,
                height: 300,
                renderTo: 'main-line-graph',
                type: 'spline'
            },
            credits: {
                enabled: false
            },
            title: {
                text: ''
            },
            xAxis: {
                categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            },
            yAxis: {
                title: {
                    text: 'Pages processed per day'
                },
                labels: {
                    formatter: function() {
                        return this.value;
                    }
                }
            },
            tooltip: {
                crosshairs: true,
                shared: true
            },
            plotOptions: {
                spline: {
                    marker: {
                        radius: 4,
                        lineColor: '#666666',
                        lineWidth: 1
                    }
                }
            },
            series: [{
                name: 'Binarisation',
                marker: {
                    symbol: 'square'
                },
                data: [7.0, 6.9, 9.5, 14.5, 18.2, 21.5, 25.2, {
                    y: 26.5,
                    marker: {
                        //symbol: 'url(http://www.highcharts.com/demo/gfx/sun.png)'
                    }
                }, 23.3, 18.3, 13.9, 9.6]
            }, {
                name: 'Segmentation',
                marker: {
                    symbol: 'diamond'
                },
                data: [{
                    y: 3.9,
                    marker: {
                        //symbol: 'url(http://www.highcharts.com/demo/gfx/snow.png)'
                    }
                }, 4.2, 5.7, 8.5, 11.9, 15.2, 17.0, 16.6, 14.2, 10.3, 6.6, 4.8]
            }]
        });
    }

    if ($('#main-pie-chart').length) {
        var chart = new Highcharts.Chart({
            chart: {
                renderTo: 'main-pie-chart',
                backgroundColor: null,
                plotBorderWidth: null,
                height: 200,
                plotShadow: false
            },
            credits: {
                enabled: false
            },
            title: {
                text: ''
            },
            tooltip: {
                formatter: function() {
                    return '<b>'+ this.point.name +'</b>: '+ this.percentage +' %';
                }
            },
            plotOptions: {
                pie: {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    dataLabels: {
                        enabled: false,
                        color: '#000000',
                        connectorColor: '#000000',
                        formatter: function() {
                            return '<b>'+ this.point.name +'</b>: '+ this.percentage +' %';
                        }
                    }
                }
            },
            series: [{
                type: 'pie',
                name: 'Browser share',
                data: [
                    ['Firefox',   45.0],
                    ['IE',       26.8],
                    {
                        name: 'Chrome',
                        y: 12.8,
                        sliced: true,
                        selected: true
                    },
                    ['Safari',    8.5],
                    ['Opera',     6.2],
                    ['Others',   0.7]
                ]
            }]
        });
    }

/*
    (function ($) {
        Project = Backbone.Model.extend({
            name: null,
            desc: null
        });

        Projects = Backbone.Collection.extend({
            initialize: function (models, options) {
                this.bind("add", options.view.addProjectLi);
            }
        });

        CreateView = Backbone.View.extend({
            el: $('body'),
            initialize: function () {
                this.projects = new Projects(Project, { view: ProjectView });
            },
            events: {
                'click #create-project-button': 'showForm',
                'submit #create-form': 'createProject',
            },
            showForm: function () {
                console.log("creating");
                $('#create-form').show();
            },
            createProject: function () {
                var projectName = $('#create-form-name').val();
                var projectDesc = $('#create-form-desc').val();
                var newProject = new Project({
                    name: projectName,
                    desc: projectDesc,
                });
                this.projects.add(newProject);
                // Reset is a DOM function not a jQuery one
                $('#create-form').hide()[0].reset();
            },
            addProjectLi: function (model) {
                console.log("calling it");
                $('#project-list').append('<li title="' + model.get('desc') + '">' + model.get('name') + '</li>');
            }
        });

        ProjectView = Backbone.View.extend({
            el: $('body'),
            initialize: function () {
                console.log("setting up project view");
            },
            events: {
                'click #project-list li': 'showProject'
            },
            showProject: function () {
                console.log("this project");
            }
        });

        var createView = new CreateView;
        var projectView = new ProjectView;
    })(jQuery);
*/
    var workers = $('#workers').children();
    var queueSizes = _.map(workers, function (worker) { return parseInt($(worker).attr('data-queue'), 10); });

    // The fake worker queue stuff
    var updateWorkers = function (queueSizes) {
        // Max queue size at least 10
        var maxQueueSize = Math.max(_.max(queueSizes), 10);
        var i, worker, queueSize, colour;
        for (i = 0; i < workers.length; i++) {
            worker = $(workers[i]).find('div');
            queueSize = Math.max(queueSizes[i], 0);
            worker.removeClass();
            if (queueSize === 0) {
                colour = 'green';
            } else if (queueSize < 3) {
                colour = 'yellow';
            } else if (queueSize < 7) {
                colour = 'orange';
            } else {
                colour = 'red';
            }
            worker.addClass(colour);
            worker.find('span').text(queueSize);

            worker.animate({
                height: queueSize / maxQueueSize * 90 + 40 + 'px'
            });
        }
    };

    setTimeout(function () {
        updateWorkers(queueSizes);
    }, 100);

    setInterval(function() {
        var fakeSizes = [];

        for (var i = 0; i < queueSizes.length; i++) {
            fakeSizes.push(queueSizes[i] + Math.round(Math.random() * 3) - 2);
        }

        updateWorkers(fakeSizes);
    }, 4000);


    // The search box
    $('#search').submit(function () {
        var query = $('#search-query').val().toLowerCase();
        var numResults = 0;
        // Hide all the projects that don't have the search term in their name/desc
        $('#project-list').find('a').each(function () {
            var projectName = $(this).text().toLowerCase();
            var projectDesc = $(this).attr('title').toLowerCase();
            if (projectName.indexOf(query) + projectDesc.indexOf(query) === -2) {
                // Not present in either the name or the description; hide
                $(this).hide();
            } else {
                $(this).show();
                numResults++;
            }
        });

        var resultsText = numResults + ' result' + ((numResults === 1) ? '' : 's');
        $('#results-tab').show().addClass('active').text(resultsText);
        $('#title-tab').removeClass('active');
        return false;
    });

    $('#title-tab').click(function () {
        if (!$('#results-tab').is(':hidden')) {
            $('#results-tab').removeClass('active').hide();
            $(this).addClass('active');
            // Show all the project lis
            $('#project-list').find('a').each(function () {
                console.log("lol");
                $(this).show();
            });
        }
    });

    $('#job-lists').delegate('.edit-parameters', 'click', function (event) {
        var jobSlug = $(this).parent().attr('data-id');
        $('#job-to-edit').val(jobSlug);
        $('#job-form').submit();
    });

    $('#job-form').submit(function () {
        var jobsList = [];
        $('#workflow-jobs').children().each(function () {
            jobsList.push($(this).attr('data-id'));
        });

        $('#ordered-jobs').val(jobsList.join(' '));
    });

    $('#workflow-jobs').delegate('.remove-job', 'click', function (event) {
        var jobNode = $(this).parent();
        // The input type is the same as the previous job's output type
        var jobID = jobNode.attr('data-id');

        $('#job-to-remove').val(1);
        $('#form').submit();
    });

    $('#available-jobs').delegate('.add-job', 'click', function (event) {
        var jobNode = $(this).parent().parent();
        var jobID = jobNode.attr('data-id');

        $('#job-to-add').val(jobID);
        $('#form').submit();
    });

    // If the flash message exists, make it disappear after some time
    // and also refresh the page
    if ($('.flash-message').length) {
        setTimeout(function () {
            $('.flash-message').fadeOut('slow');
            setTimeout(function () {
                window.location.search = '';
            }, 1000);
        }, 2000);
    }

    // Handle selecting pages (the add pages view)
    $('.select-pages').click(function () {
        // Odd and even seem to be switched but it's just because it's 0-indexed
        var filter = $(this).attr('data-filter');
        $('.image-buttons img').filter(filter).each(function () {
            $(this).addClass('selected');
            $(this).next().prop('checked', true);
        });

        $('.image-buttons img').not(filter).each(function () {
            $(this).removeClass('selected');
            $(this).next().prop('checked', false);
        });
    });

    var submitForm = $('#upload-images').length;
    // If the .image-buttons class exists, handle clicking the images
    if ($('.image-buttons').length) {
        $('.image-buttons').delegate('img', 'click', function (event) {
            // Check the radio button immediately following the image
            var radioButton = $(this).next();
            if (radioButton.attr('checked')) {
                radioButton.prop('checked', false);
            } else {
                radioButton.prop('checked', true);
            }

            if (submitForm) {
                $('#form').submit();
            } else {
                $(this).toggleClass('selected');
            }
        });
    }

    // "Automatic" file upload lol
    $('input[type=file]').change(function () {
        $('#form').trigger('submit');
    });
});
