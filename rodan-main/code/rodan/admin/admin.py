from django.contrib import admin
from django.contrib.auth import forms
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from guardian.admin import GuardedModelAdmin

from rodan.models.project import Project
from rodan.models.user import User
from rodan.models.workflow import Workflow
from rodan.models.workflowjob import WorkflowJob
from rodan.models.workflowrun import WorkflowRun
from rodan.models.runjob import RunJob
from rodan.models.job import Job
from rodan.models.resultspackage import ResultsPackage
from rodan.models.resource import Resource
from rodan.models.resourcelist import ResourceList


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

class UserChangeForm(forms.UserChangeForm):
    class Meta(forms.UserChangeForm.Meta):
        model = User

class UserCreationForm(forms.UserCreationForm):
    class Meta(forms.UserCreationForm.Meta):
        model = User

class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active')

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )

    search_fields = ('username', 'email')
    ordering = ('username', 'email')

admin.site.register(Project, ProjectAdmin)
admin.site.register(WorkflowRun, WorkflowRunAdmin)
admin.site.register(RunJob, RunJobAdmin)
admin.site.register(Workflow)
admin.site.register(Job, JobAdmin)
admin.site.register(WorkflowJob, WorkflowJobAdmin)
admin.site.register(ResultsPackage, ResultsPackageAdmin)
admin.site.register(Resource)
admin.site.register(ResourceList, ResourceListAdmin)
admin.site.register(User, UserAdmin)