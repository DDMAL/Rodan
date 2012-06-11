from django.contrib import admin
from rodan.models.projects import Project, Page, Workflow, JobItem

class JobItemInline(admin.StackedInline):
    model = JobItem
    extra = 5

class WorkflowAdmin(admin.ModelAdmin):
    inlines = [JobItemInline]

admin.site.register(Project)
admin.site.register(Page)
admin.site.register(Workflow, WorkflowAdmin)
