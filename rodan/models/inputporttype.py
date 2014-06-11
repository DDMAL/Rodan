from django.db import models
from uuidfield import UUIDField


class InputPortType(models.Model):
    class Meta:
        app_label = 'rodan'

    """
        ISN'T TRUE ENTIRELY ANYMORE. WILL REWRITE LATER. HERE NOW JUST FOR MY REFERENCE
        These are the possible InputPortType definitions associated with a Job. 
        Each Job may have 0 or more InputPortTypes defined. An InputPortType consists of:

            * name (string): a name unique to the other InputPortTypes in the Job
            * resource_type (enum): the type of Resource the Job expects; this coincides with Resource.type
            * minimum (non-negative integer): the minimum number of input_ports of this InputPortType a 
              WorkflowJob must use in order to meet the execution requirements
            * maximum (non-negative integer): the maximum number of input_ports of this InputPortType a 
              WorkflowJob may use in order to meet the execution requirements

        InputPortTypes define what kind of data (i.e. Resources) this particular Job expects to work with.
        Note that the parameters above imply that some inputs may not be needed, or that a particular input
        must be included more than once.
    """

    uuid = UUIDField(primary_key=True, auto=True)
    job = models.ForeignKey('rodan.Job', null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    resource_type = models.IntegerField()
    minimum = models.IntegerField()
    maximum = models.IntegerField()
