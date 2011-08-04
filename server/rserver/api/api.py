from tastypie import resources
from rserver.api.models import Project, Document, Page, Image, Transcription
from rserver.api.models import Workflow, Task, Queue

class ProjectResource(resources.ModelResource):
    class Meta:
        queryset = Project.objects.all()
        resource_name = 'project'

class DocumentResource(resources.ModelResource):
    class Meta:
        queryset = Document.objects.all()
        resource_name = 'document'

class PageResource(resources.ModelResource):
    class Meta:
        queryset = Page.objects.all()
        resource_name = 'page'

class ImageResource(resources.ModelResource):
    class Meta:
        queryset = Image.objects.all()
        resource_name = 'image'

class TranscriptionResource(resources.ModelResource):
    class Meta:
        queryset = Transcription.objects.all()
        resource_name = 'transcription'

class WorkflowResource(resources.ModelResource):
    class Meta:
        queryset = Workflow.objects.all()
        resource_name = 'workflow'
        
class WorkflowStepResource(resources.ModelResource):
    class Meta:
        queryset = WorkflowStep.objects.all()
        resource_name = 'workflow_step'

class TaskResource(resources.ModelResource):
    class Meta:
        queryset = Task.objects.all()
        resource_name = 'task'
        
class TaskStatusResource(resources.ModelResource):
    class Meta:
        queryset = TaskStatus.objects.all()
        resource_name = 'task_step'

class QueueResource(resources.ModelResource):
    class Meta:
        queryset = Queue.objects.all()
        resource_name = 'queue'