from django.contrib import admin
from rserver.api.models import Project, Document, Page, Image, Transcription
from rserver.api.models import Workflow, WorkflowStep, Task, TaskStatus, Queue
from rserver.api.models import UserProfile

class ProjectAdmin(admin.ModelAdmin):
    pass

admin.site.register(Project, ProjectAdmin)

class DocumentAdmin(admin.ModelAdmin):
    pass

admin.site.register(Document, DocumentAdmin)

class PageAdmin(admin.ModelAdmin):
    """docstring for PageAdmin"""
    pass

admin.site.register(Page, PageAdmin)

class ImageAdmin(admin.ModelAdmin):
    pass

admin.site.register(Image, ImageAdmin)

class TranscriptionAdmin(admin.ModelAdmin):
    """docstring for TranscriptionAdmin"""
    pass

admin.site.register(Transcription, TranscriptionAdmin)

class WorkflowAdmin(admin.ModelAdmin):
    """docstring for WorkflowAdmin"""
    pass

admin.site.register(Workflow, WorkflowAdmin)

class WorkflowStepAdmin(admin.ModelAdmin):
    pass
    
admin.site.register(WorkflowStep, WorkflowStepAdmin)

class TaskAdmin(admin.ModelAdmin):
    pass

admin.site.register(Task, TaskAdmin)

class TaskStatusAdmin(admin.ModelAdmin):
    pass

admin.site.register(TaskStatus, TaskStatusAdmin)

class QueueAdmin(admin.ModelAdmin):
    pass

admin.site.register(Queue, QueueAdmin)

class UserProfileAdmin(admin.ModelAdmin):
    pass

admin.site.register(UserProfile, UserProfileAdmin)
