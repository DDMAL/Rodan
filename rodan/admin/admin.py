from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from rodan.models.project import Project
from rodan.models.page import Page
from rodan.models.workflow import Workflow
from rodan.models.workflowjob import WorkflowJob
from rodan.models.workflowrun import WorkflowRun
from rodan.models.runjob import RunJob
from rodan.models.job import Job
from rodan.models.result import Result
from rodan.models.classifier import Classifier

# from rodan.models.rodanuser import RodanUser


# class WorkflowJobInline(admin.StackedInline):
#     model = WorkflowJob
#     extra = 5


# class WorkflowAdmin(admin.ModelAdmin):
#     inlines = [WorkflowJobInline]


class JobAdmin(admin.ModelAdmin):
    list_display = ('job_name', 'enabled', 'category')


class ProjectAdmin(GuardedModelAdmin):
    readonly_fields = ('uuid',)


class PageAdmin(admin.ModelAdmin):
    list_display = ('page_image', 'page_order', 'created', 'updated')


class WorkflowJobAdmin(admin.ModelAdmin):
    list_display = ('job_name', 'sequence', 'created', 'updated')
    list_filter = ('workflow__name',)


class RunJobAdmin(admin.ModelAdmin):
    list_display = ('job_name', 'page_name', 'created', 'updated')


class WorkflowRunAdmin(admin.ModelAdmin):
    list_display = ('workflow', 'run', 'created')


class ClassifierAdmin(admin.ModelAdmin):
    list_display = ('name',)


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
admin.site.register(Page, PageAdmin)
admin.site.register(Workflow)
admin.site.register(Job, JobAdmin)
admin.site.register(WorkflowJob, WorkflowJobAdmin)
admin.site.register(Result)
admin.site.register(Classifier, ClassifierAdmin)
