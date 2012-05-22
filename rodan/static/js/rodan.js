$(document).ready(function () {
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
});
