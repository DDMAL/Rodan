from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from rodan.models.project import Project

from rodan.models.workflow import Workflow
from rodan.models.workflowjob import WorkflowJob
from rodan.models.workflowrun import WorkflowRun
from rodan.models.runjob import RunJob
from rodan.models.job import Job
from rodan.models.resultspackage import ResultsPackage
from rodan.models.resource import Resource
from rodan.models.resourcelist import ResourceList

# from rodan.models.rodanuser import RodanUser


# class WorkflowJobInline(admin.StackedInline):
#     model = WorkflowJob
#     extra = 5


# class WorkflowAdmin(admin.ModelAdmin):
#     inlines = [WorkflowJobInline]


class JobAdmin(admin.ModelAdmin):
    list_display = ('name', 'enabled', 'category')


class ProjectAdmin(GuardedModelAdmin):
    list_display = ('name', 'uuid', 'creator', 'created', 'updated')
    readonly_fields = ('uuid',)


class WorkflowJobAdmin(admin.ModelAdmin):
    list_display = ('job_name', 'created', 'updated')
    list_filter = ('workflow__name',)


class RunJobAdmin(admin.ModelAdmin):
    list_display = ('job', 'created', 'updated')


class WorkflowRunAdmin(admin.ModelAdmin):
    list_display = ('workflow', 'created')


class ResultsPackageAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'workflow_run', 'created')


class ResourceAdmin(admin.ModelAdmin):
    list_display = ('resource_image', 'created', 'updated')


class ResourceListAdmin(admin.ModelAdmin):
    list_display = ('created', 'updated')


# class UserProfileInline(admin.StackedInline):
#     model = RodanUser
#     can_delete = False
#     verbose_name_plural = 'profile'


# class RodanUserAdmin(UserAdmin):
#     inlines = (UserProfileInline, )

# admin.site.unregister(User)
# admin.site.register(User, RodanUserAdmin)

# admin.site.register(RodanUser)
admin.site.register(Project, ProjectAdmin)
admin.site.register(WorkflowRun, WorkflowRunAdmin)
admin.site.register(RunJob, RunJobAdmin)
admin.site.register(Workflow)
admin.site.register(Job, JobAdmin)
admin.site.register(WorkflowJob, WorkflowJobAdmin)
admin.site.register(ResultsPackage, ResultsPackageAdmin)
admin.site.register(Resource)
admin.site.register(ResourceList, ResourceListAdmin)
