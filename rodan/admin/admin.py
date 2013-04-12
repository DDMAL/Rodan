from django.contrib import admin

from rodan.models.project import Project
from rodan.models.page import Page
from rodan.models.workflow import Workflow
from rodan.models.workflowjob import WorkflowJob
from rodan.models.workflowrun import WorkflowRun
from rodan.models.runjob import RunJob
from rodan.models.job import Job
from rodan.models.result import Result
# from rodan.models.rodanuser import RodanUser


# class WorkflowJobInline(admin.StackedInline):
#     model = WorkflowJob
#     extra = 5


# class WorkflowAdmin(admin.ModelAdmin):
#     inlines = [WorkflowJobInline]


class JobAdmin(admin.ModelAdmin):
    list_display = ('job_name', 'enabled', 'category')


class ProjectAdmin(admin.ModelAdmin):
    readonly_fields = ('uuid',)


class PageAdmin(admin.ModelAdmin):
    list_display = ('page_image', 'page_order', 'created', 'updated')

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
admin.site.register(WorkflowRun)
admin.site.register(RunJob)
admin.site.register(Page, PageAdmin)
admin.site.register(Workflow)
admin.site.register(Job, JobAdmin)
admin.site.register(WorkflowJob)
admin.site.register(Result)
