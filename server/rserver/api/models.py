from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Project(models.Model):
    """(Project description)"""
    project_name = models.CharField(max_length=255)
    documents = models.ManyToManyField("Document")
    assigned_users = models.ManyToManyField(User)
    
    class Admin:
        list_display = ('',)
        search_fields = ('',)

    def __unicode__(self):
        return u"Project"

class Document(models.Model):
    """(Document description)"""
    document_name = models.CharField(max_length=255)
    pages = models.ManyToManyField("Page")
    
    class Admin:
        list_display = ('',)
        search_fields = ('',)

    def __unicode__(self):
        return u"Document"

class Page(models.Model):
    """(Page description)"""
    images = models.ManyToManyField("Image")
    
    class Admin:
        list_display = ('',)
        search_fields = ('',)

    def __unicode__(self):
        return u"Page"

class Image(models.Model):
    """(Image description)"""
    img_file = models.ImageField(upload_to="/tmp")
    
    class Admin:
        list_display = ('',)
        search_fields = ('',)

    def __unicode__(self):
        return u"Image"

class Transcription(models.Model):
    """(Transcription description)"""
    
    
    class Admin:
        list_display = ('',)
        search_fields = ('',)

    def __unicode__(self):
        return u"Transcription"

class Workflow(models.Model):
    """(Workflow description)"""
    workflow_step = models.ForeignKey("WorkflowStep")
    
    class Admin:
        list_display = ('',)
        search_fields = ('',)

    def __unicode__(self):
        return u"Workflow"

class WorkflowStep(models.Model):
    description = models.CharField(max_length=255)
    
    def __unicode__(self):
        return u'Workflow Step'

class Task(models.Model):
    """(Task description)"""
    task_description = models.CharField(max_length=255)
    queue = models.ForeignKey("Queue")
    status = models.ForeignKey("TaskStatus")
    
    class Admin:
        list_display = ('',)
        search_fields = ('',)

    def __unicode__(self):
        return u"Task"
        
class TaskStatus(models.Model):
    status_description = models.CharField(max_length=255)
    
    def __unicode__(self):
        return u'Task Status'

class Queue(models.Model):
    """(Queue description)"""
    queue_user = models.ForeignKey(User)
    
    
    class Admin:
        list_display = ('',)
        search_fields = ('',)

    def __unicode__(self):
        return u"Queue"
