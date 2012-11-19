from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from rodan.models.project import Project
from rodan.models.page import Page
from rodan.models.workflow import Workflow
from rodan.models.jobitem import JobItem
from rodan.models.job import Job
from rodan.models.parameter import Parameter
from rodan.models.result import Result
from rodan.models.rodanuser import RodanUser


class JobItemInline(admin.StackedInline):
    model = JobItem
    extra = 5


class WorkflowAdmin(admin.ModelAdmin):
    inlines = [JobItemInline]


class UserProfileInline(admin.StackedInline):
    model = RodanUser
    can_delete = False
    verbose_name_plural = 'profile'


class RodanUserAdmin(UserAdmin):
    inlines = (UserProfileInline, )

admin.site.unregister(User)
admin.site.register(User, RodanUserAdmin)

admin.site.register(RodanUser)
admin.site.register(Project)
admin.site.register(Page)
admin.site.register(Workflow, WorkflowAdmin)
admin.site.register(Job)
admin.site.register(JobItem)
admin.site.register(Parameter)
admin.site.register(Result)
