from rodan.models.inputporttype import InputPortType
from rodan.models.outputporttype import OutputPortType
from rodan.models.inputport import InputPort
from rodan.models.outputport import OutputPort
from rodan.models.input import Input
from rodan.models.output import Output
from rodan.models.project import Project
from rodan.models.job import Job
from rodan.models.workflowjob import WorkflowJob
from rodan.models.workflow import Workflow
from rodan.models.workflowrun import WorkflowRun
from rodan.models.runjob import RunJob
from rodan.models.resultspackage import ResultsPackage
from rodan.models.resource import Resource
from rodan.models.resourcetype import ResourceType
from rodan.models.connection import Connection

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
import json

@receiver(post_save)
def notify_socket_subscribers(sender, instance, created, **kwargs):
    from ws4redis.publisher import RedisPublisher
    from ws4redis.redis_store import RedisMessage

    publisher = RedisPublisher(facility='rodan', broadcast=True)

    data = {"Status": "", "Name": instance.__class__.__name__, "UUID": ""} 
    if created:
	data["Status"] = "Created"
	data["UUID"] = "{0}".format(instance.uuid)
	message = RedisMessage(json.dumps(data))
        #message = RedisMessage("Status: Created, Name: {0}, UUID: {1}".format(instance.__class__.__name__, instance.uuid))
    else:
	data["Status"] = "Updated"
	data["UUID"] = "{0}".format(instance.uuid)
	message = RedisMessage(json.dumps(data))
        #message = RedisMessage("Status: Updated, Name: {0}, UUID: {1}".format(instance.__class__.__name__, instance.uuid))
    print('publishing a message')

    publisher.publish_message(message)
