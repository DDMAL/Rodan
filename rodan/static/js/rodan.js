$(document).ready(function () {

    var graph = new Highcharts.Chart({

            chart: {
                height: 300,

                renderTo: 'main-line-graph',

                type: 'spline'

            },
            credits: {
                enabled: false,
            },

            title: {

                text: ''

            },

            xAxis: {

                categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',

                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

            },

            yAxis: {

                title: {

                    text: 'Pages processed per day'

                },

                labels: {

                    formatter: function() {

                        return this.value

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

    var chart = new Highcharts.Chart({

            chart: {

                renderTo: 'main-pie-chart',

                plotBackgroundColor: null,

                plotBorderWidth: null,
                height: 200,

                plotShadow: false

            },
            credits: {
                enabled: false,
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
});
