from django.db import models
from uuidfield import UUIDField


class OutputPortType(models.Model):
    class Meta:
        app_label = 'rodan'

    """
        FROM THE WIKI FOR MY REFERENCE WHILE I WRITE THIS THING
        These are the possible OutputPortType definitions associated with a Job.
        Each Job MUST have 1 or more OutputPortTypes defined. An OutputPortType consists of:

            * name (string): a name unique to the other OutputPortTypes in the Job
            * resource_type (enum): the type of Resource the Job expects; this coincides with Resource.type
        
        OutputPortTypes define what kind of data (i.e. Resources) this particular job will output.
    """

    uuid = UUIDField(primary_key=True, auto=True)
    job = models.ForeignKey('rodan.Job', related_name='outputporttype', null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    resource_type = models.IntegerField()
